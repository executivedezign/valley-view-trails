#!/usr/bin/env python3
"""autotone — analyze JPEG photos and write per-image corrections.

For each JPEG, autotone measures exposure, contrast, color cast, and
saturation, then embeds Lightroom develop settings (Camera Raw /
Process 2012) as XMP metadata inside the JPEG, so Lightroom 5+ applies
the corrections at import (or via Metadata > Read Metadata from File).

Only the metadata block of the JPEG is touched; image pixels are never
recompressed. Usage:

    python autotone.py PHOTOS_DIR             # embed XMP in place
    python autotone.py PHOTOS_DIR --report    # analyze only, change nothing
    python autotone.py PHOTOS_DIR --backup    # keep untouched .orig copies
"""

from __future__ import annotations

import argparse
import os
import re
import struct
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, fields

import numpy as np
from PIL import Image

JPEG_EXTENSIONS = {".jpg", ".jpeg", ".jpe", ".jfif"}
XMP_HEADER = b"http://ns.adobe.com/xap/1.0/\x00"
CRS_NS = "http://ns.adobe.com/camera-raw-settings/1.0/"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
X_NS = "adobe:ns:meta/"
ANALYSIS_MAX_DIM = 1024  # downsample long edge to this before measuring


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

@dataclass
class Settings:
    """Corrections in Lightroom slider units (Process 2012)."""

    exposure: float = 0.0      # stops, crs:Exposure2012
    contrast: int = 0          # crs:Contrast2012
    highlights: int = 0        # crs:Highlights2012
    shadows: int = 0           # crs:Shadows2012
    whites: int = 0            # crs:Whites2012
    blacks: int = 0            # crs:Blacks2012
    temperature: int = 0       # crs:IncrementalTemperature (JPEG-relative)
    tint: int = 0              # crs:IncrementalTint
    vibrance: int = 0          # crs:Vibrance

    def is_noop(self) -> bool:
        return all(getattr(self, f.name) == 0 for f in fields(self))


def load_for_analysis(path: str) -> np.ndarray:
    """Return the image as float32 RGB in [0, 1], downsampled for speed."""
    with Image.open(path) as im:
        im = im.convert("RGB")
        scale = ANALYSIS_MAX_DIM / max(im.size)
        if scale < 1.0:
            im = im.resize(
                (max(1, round(im.width * scale)), max(1, round(im.height * scale))),
                Image.BILINEAR,
            )
        return np.asarray(im, dtype=np.float32) / 255.0


def analyze(rgb: np.ndarray, strength: float = 1.0) -> Settings:
    """Measure the image and propose corrections.

    All the gain constants below are deliberately damped: the goal is a
    correction a human would call "most of the way there", never a wild
    swing the user has to undo.
    """
    s = Settings()
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b

    p005, p25, p75, p995 = np.percentile(lum, [0.5, 25.0, 75.0, 99.5])

    # Exposure: aim the linearized median at a mid-gray of ~0.14
    # (about 0.42 in gamma-encoded terms).
    median_linear = float(np.median(lum)) ** 2.2
    ev = 0.6 * np.log2(0.14 / max(median_linear, 1e-4))
    ev = float(np.clip(ev * strength, -2.5, 2.5))
    if abs(ev) >= 0.10:
        s.exposure = round(ev, 2)

    # Highlights/Shadows recover clipped or crushed regions.
    hi_clip = float(np.mean(lum > 0.98))
    lo_clip = float(np.mean(lum < 0.02))
    if hi_clip > 0.004:
        s.highlights = -int(np.clip(round(1600 * hi_clip * strength), 0, 70))
    if lo_clip > 0.004:
        s.shadows = int(np.clip(round(1400 * lo_clip * strength), 0, 70))

    # Whites/Blacks stretch a flat histogram toward the endpoints.
    if p995 < 0.93:
        s.whites = int(np.clip(round((0.93 - p995) * 140 * strength), 0, 35))
    if p005 > 0.05:
        s.blacks = -int(np.clip(round((p005 - 0.05) * 160 * strength), 0, 35))

    # Contrast from the interquartile spread of luminance.
    spread = p75 - p25
    contrast = round((0.36 - spread) * 110 * strength)
    if abs(contrast) >= 4:
        s.contrast = int(np.clip(contrast, -25, 25))

    # White balance: gray-world over midtones, ignoring near-clipped pixels.
    midtones = (lum > 0.15) & (lum < 0.85) & (rgb.max(axis=-1) < 0.97)
    if np.count_nonzero(midtones) < 500:
        midtones = np.ones(lum.shape, dtype=bool)
    rm = float(np.mean(r[midtones]))
    gm = float(np.mean(g[midtones]))
    bm = float(np.mean(b[midtones]))
    neutral = (rm + gm + bm) / 3.0
    if neutral > 1e-4:
        cast_rb = (rm - bm) / neutral        # > 0: warm cast
        cast_green = (gm - (rm + bm) / 2.0) / neutral  # > 0: green cast
        if abs(cast_rb) > 0.015:
            # Correct opposite to the cast; positive slider = warmer.
            s.temperature = -int(np.clip(round(cast_rb * 180 * strength), -45, 45))
        if abs(cast_green) > 0.015:
            # Positive slider = magenta, which corrects a green cast.
            s.tint = int(np.clip(round(cast_green * 180 * strength), -45, 45))

    # Vibrance for washed-out color.
    maxc = rgb.max(axis=-1)
    minc = rgb.min(axis=-1)
    sat = np.where(maxc > 1e-4, (maxc - minc) / np.maximum(maxc, 1e-4), 0.0)
    mean_sat = float(np.mean(sat[midtones]))
    if mean_sat < 0.25:
        s.vibrance = int(np.clip(round((0.28 - mean_sat) * 90 * strength), 0, 25))

    return s


# ---------------------------------------------------------------------------
# Lightroom output: XMP embedded in the JPEG
# ---------------------------------------------------------------------------

def _fmt_signed(v: int) -> str:
    return f"+{v}" if v > 0 else str(v)


def crs_attributes(s: Settings) -> dict:
    """Camera Raw settings as XMP attribute {qualified-name: value}."""
    wb_custom = s.temperature != 0 or s.tint != 0
    attrs = {
        f"{{{CRS_NS}}}Version": "8.7",
        f"{{{CRS_NS}}}ProcessVersion": "6.7",
        f"{{{CRS_NS}}}WhiteBalance": "Custom" if wb_custom else "As Shot",
        f"{{{CRS_NS}}}IncrementalTemperature": _fmt_signed(s.temperature),
        f"{{{CRS_NS}}}IncrementalTint": _fmt_signed(s.tint),
        f"{{{CRS_NS}}}Exposure2012": f"{s.exposure:+.2f}" if s.exposure else "0.00",
        f"{{{CRS_NS}}}Contrast2012": _fmt_signed(s.contrast),
        f"{{{CRS_NS}}}Highlights2012": _fmt_signed(s.highlights),
        f"{{{CRS_NS}}}Shadows2012": _fmt_signed(s.shadows),
        f"{{{CRS_NS}}}Whites2012": _fmt_signed(s.whites),
        f"{{{CRS_NS}}}Blacks2012": _fmt_signed(s.blacks),
        f"{{{CRS_NS}}}Vibrance": _fmt_signed(s.vibrance),
        f"{{{CRS_NS}}}Saturation": "0",
        f"{{{CRS_NS}}}ToneCurveName2012": "Linear",
        f"{{{CRS_NS}}}HasSettings": "True",
        # Explicitly False so Lightroom applies (not ignores) the settings.
        f"{{{CRS_NS}}}AlreadyApplied": "False",
    }
    return attrs


def build_xmp_packet(s: Settings, existing_packet: bytes | None) -> bytes:
    """Return a full <?xpacket?> block carrying our crs settings.

    If the JPEG already has an XMP packet, all other metadata in it is
    preserved; only crs:* entries are replaced with ours.
    """
    ET.register_namespace("x", X_NS)
    ET.register_namespace("rdf", RDF_NS)
    ET.register_namespace("crs", CRS_NS)

    root = None
    if existing_packet:
        text = existing_packet.decode("utf-8", errors="replace")
        # Keep the original namespace prefixes readable on re-serialization.
        for prefix, uri in re.findall(r'xmlns:([A-Za-z0-9_.-]+)="([^"]+)"', text):
            if prefix not in ("x", "rdf", "crs", "xml", "xmlns"):
                try:
                    ET.register_namespace(prefix, uri)
                except ValueError:
                    pass
        body = re.sub(r"<\?xpacket[^?]*\?>", "", text).strip()
        root = ET.fromstring(body)  # raises ParseError on malformed XMP

    if root is None:
        root = ET.Element(f"{{{X_NS}}}xmpmeta")
        ET.SubElement(root, f"{{{RDF_NS}}}RDF")

    rdf = root.find(f"{{{RDF_NS}}}RDF")
    if rdf is None:
        rdf = ET.SubElement(root, f"{{{RDF_NS}}}RDF")

    # Strip any pre-existing Camera Raw entries (attributes or elements).
    for desc in rdf.findall(f"{{{RDF_NS}}}Description"):
        for key in [k for k in desc.attrib if k.startswith(f"{{{CRS_NS}}}")]:
            del desc.attrib[key]
        for child in [c for c in list(desc) if c.tag.startswith(f"{{{CRS_NS}}}")]:
            desc.remove(child)

    desc = ET.SubElement(rdf, f"{{{RDF_NS}}}Description", {f"{{{RDF_NS}}}about": ""})
    desc.attrib.update(crs_attributes(s))

    xml_bytes = ET.tostring(root, encoding="utf-8")
    packet = (
        b'<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        + xml_bytes
        + b"\n"
        + b" " * 512  # writer padding, per the XMP spec
        + b'<?xpacket end="w"?>'
    )
    return packet


def _iter_jpeg_segments(data: bytes):
    """Yield (marker, seg_start, seg_end) for header segments up to SOS."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG (missing SOI)")
    pos = 2
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            raise ValueError(f"corrupt JPEG segment marker at offset {pos}")
        marker = data[pos + 1]
        if marker == 0xDA:  # SOS: entropy-coded data follows, stop here
            return
        if marker == 0xD9:  # EOI
            return
        if 0xD0 <= marker <= 0xD7 or marker == 0x01:  # standalone markers
            pos += 2
            continue
        length = struct.unpack(">H", data[pos + 2 : pos + 4])[0]
        yield marker, pos, pos + 2 + length
        pos += 2 + length


def embed_xmp(path: str, settings: Settings, backup: bool = False) -> None:
    """Rewrite the JPEG at *path* with our XMP develop settings embedded."""
    with open(path, "rb") as f:
        data = f.read()

    xmp_span = None
    insert_at = 2  # right after SOI, adjusted below
    for marker, start, end in _iter_jpeg_segments(data):
        payload = data[start + 4 : end]
        if marker == 0xE1 and payload.startswith(XMP_HEADER):
            xmp_span = (start, end)
            break
        if marker in (0xE0, 0xE1):  # keep JFIF/EXIF ahead of the XMP block
            insert_at = end

    existing = data[xmp_span[0] + 4 + len(XMP_HEADER) : xmp_span[1]] if xmp_span else None
    packet = build_xmp_packet(settings, existing)

    seg_payload = XMP_HEADER + packet
    if len(seg_payload) + 2 > 0xFFFF:
        raise ValueError("XMP packet too large for a single JPEG segment")
    segment = b"\xff\xe1" + struct.pack(">H", len(seg_payload) + 2) + seg_payload

    if xmp_span:
        out = data[: xmp_span[0]] + segment + data[xmp_span[1] :]
    else:
        out = data[:insert_at] + segment + data[insert_at:]

    if backup:
        orig = path + ".orig"
        if not os.path.exists(orig):
            with open(orig, "wb") as f:
                f.write(data)

    # Atomic replace so a crash can't leave a truncated photo behind.
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(out)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def collect_jpegs(paths: list[str], recursive: bool) -> list[str]:
    out: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            if recursive:
                for root, _dirs, names in os.walk(p):
                    out += [os.path.join(root, n) for n in names
                            if os.path.splitext(n)[1].lower() in JPEG_EXTENSIONS]
            else:
                out += [os.path.join(p, n) for n in sorted(os.listdir(p))
                        if os.path.splitext(n)[1].lower() in JPEG_EXTENSIONS]
        elif os.path.splitext(p)[1].lower() in JPEG_EXTENSIONS:
            out.append(p)
        else:
            print(f"skipping (not a JPEG): {p}", file=sys.stderr)
    return out


def describe(s: Settings) -> str:
    if s.is_noop():
        return "no correction needed"
    parts = []
    if s.exposure:
        parts.append(f"exposure {s.exposure:+.2f}")
    for name, label in (("contrast", "contrast"), ("highlights", "highlights"),
                        ("shadows", "shadows"), ("whites", "whites"),
                        ("blacks", "blacks"), ("temperature", "temp"),
                        ("tint", "tint"), ("vibrance", "vibrance")):
        v = getattr(s, name)
        if v:
            parts.append(f"{label} {v:+d}")
    return ", ".join(parts)


def _pause_if_own_window() -> None:
    """Keep the console open when Windows launched us in our own window.

    Double-clicking the .exe (or dropping a folder onto it) opens a console
    that would vanish the instant we exit; cmd sets PROMPT in the
    environment, Explorer does not, so its absence marks that case.
    """
    if sys.platform == "win32" and "PROMPT" not in os.environ:
        try:
            if sys.stdin and sys.stdin.isatty():
                input("\nPress Enter to close this window...")
        except EOFError:
            pass


def interactive_session() -> int:
    """Guided mode for a double-clicked .exe: ask, preview, confirm, apply."""
    print("autotone — per-image Lightroom corrections for JPEGs")
    print("(You can also drag a photo folder onto autotone.exe next time.)\n")
    try:
        folder = input("Folder of JPEGs to analyze: ").strip().strip('"')
        while not os.path.isdir(folder):
            if not folder:
                return 0
            folder = input("That folder doesn't exist — try again "
                           "(or press Enter to quit): ").strip().strip('"')
        rc = main([folder, "--report"])
        if rc != 0:
            return rc
        answer = input("\nEmbed these corrections into the photos? "
                       "Untouched .orig copies will be kept. [y/N] ").strip().lower()
        if answer in ("y", "yes"):
            return main([folder, "--backup"])
        print("No changes made.")
        return 0
    except (EOFError, KeyboardInterrupt):
        return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="autotone",
        description="Analyze JPEGs and embed per-image Lightroom corrections.")
    ap.add_argument("paths", nargs="+", help="JPEG files and/or folders")
    ap.add_argument("--report", action="store_true",
                    help="analyze and print proposed corrections; change nothing")
    ap.add_argument("--backup", action="store_true",
                    help="save an untouched copy as <name>.orig before writing")
    ap.add_argument("--strength", type=float, default=1.0, metavar="N",
                    help="correction strength multiplier, 0.0-1.5 (default 1.0)")
    ap.add_argument("--recursive", action="store_true",
                    help="descend into subfolders")
    args = ap.parse_args(argv)
    strength = min(max(args.strength, 0.0), 1.5)

    files = collect_jpegs(args.paths, args.recursive)
    if not files:
        print("no JPEG files found", file=sys.stderr)
        return 1

    failures = 0
    for path in files:
        try:
            settings = analyze(load_for_analysis(path), strength)
            print(f"{path}: {describe(settings)}")
            if args.report:
                continue
            embed_xmp(path, settings, backup=args.backup)
        except Exception as exc:  # keep going; report at the end
            failures += 1
            print(f"{path}: ERROR: {exc}", file=sys.stderr)

    if failures:
        print(f"\n{failures} file(s) failed", file=sys.stderr)
        return 1
    if not args.report:
        print(f"\nDone: corrections embedded in {len(files)} file(s). "
              "In Lightroom, import them (or select and run "
              "Metadata > Read Metadata from File).")
    return 0


if __name__ == "__main__":
    exit_code = interactive_session() if len(sys.argv) < 2 else main()
    _pause_if_own_window()
    sys.exit(exit_code)
