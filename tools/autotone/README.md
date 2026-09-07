# autotone

Analyzes JPEG photos for exposure, contrast, color cast, and saturation
problems, then embeds **per-image corrections** in each JPEG as Camera Raw
(Process 2012) develop settings. Import the photos into **Lightroom 5+** and
they arrive with the sliders already set; every correction stays
non-destructive and editable.

Only the JPEG's metadata block is modified. **Image pixels are never
recompressed or altered.**

## Getting the Windows .exe

Every change to this tool triggers the "Build autotone.exe" GitHub Actions
workflow, which builds and smoke-tests a standalone `autotone.exe` on a
Windows runner. Download it from the workflow run's **Artifacts** section
(repo → Actions → Build autotone.exe → latest run). No Python installation is
needed to run it.

To build it yourself instead, on a Windows machine with Python:

```
pip install pyinstaller -r requirements.txt
pyinstaller --onefile --name autotone autotone.py
```

## Usage

Three ways to run it:

1. **Double-click `autotone.exe`.** A window opens and walks you through it:
   it asks for your photo folder, shows the proposed correction for every
   image, and only writes anything after you confirm (keeping untouched
   `.orig` copies).
2. **Drag a photo folder onto `autotone.exe`.** Processes that folder and
   waits for a keypress before closing so you can read the results.
3. **Command line**, for options like `--strength` and `--recursive`
   (substitute `python autotone.py` if running from source):

```
autotone.exe C:\Photos\hike-2026-09           # embed corrections in place
autotone.exe C:\Photos\hike-2026-09 --report  # preview only, change nothing
autotone.exe C:\Photos --recursive --backup   # keep untouched .orig copies
autotone.exe C:\Photos\hike --strength 0.7    # gentler corrections (0.0-1.5)
```

Run with `--report` first on a new batch — it prints exactly what would be
applied to each image.

## Lightroom 5 workflow (JPEGs)

1. Run autotone on the folder **before importing** into Lightroom.
2. Import as usual. Each photo shows up with its corrections already applied
   in the Develop module — identical to having moved the sliders by hand.
3. Fine-tune anything the heuristics got wrong; it's all just slider state.

For photos **already in your catalog**: run autotone on the files on disk,
select them in Lightroom, then **Metadata > Read Metadata from File**.
(Note this replaces any develop edits you had made to those photos with
autotone's settings — use it on unedited photos.)

JPEG white balance uses Lightroom's relative sliders
(`IncrementalTemperature`/`IncrementalTint`, -100..+100), not Kelvin — that's
normal for non-raw files.

## How the analysis works

The image is downsampled and measured:

| Problem | Measurement | Correction |
|---|---|---|
| Under/overexposure | linearized median luminance vs. mid-gray target | `Exposure2012` (stops) |
| Blown highlights / crushed shadows | fraction of pixels near 255 / 0 | `Highlights2012` / `Shadows2012` |
| Flat histogram | 0.5th/99.5th luminance percentiles | `Whites2012` / `Blacks2012` |
| Low contrast | interquartile luminance spread | `Contrast2012` |
| Color cast | gray-world average over midtones (clipped pixels excluded) | temperature / tint |
| Washed-out color | mean midtone saturation | `Vibrance` |

All corrections are deliberately damped and clamped — the goal is "most of the
way there", never a wild swing. If results are consistently too strong or too
weak for your camera, adjust `--strength`, or edit the gain constants in
`analyze()` (they're commented).

## Notes and limits

- JPEGs have less recovery latitude than raw: detail already clipped in the
  file can't be brought back; the tool balances what's there.
- If a photo already contains XMP metadata (titles, keywords, GPS), it is
  preserved; only Camera Raw settings are replaced.
- If you later shoot raw: the same analysis applies, but the output should
  switch to `.xmp` sidecar files (and Kelvin white balance). The emitter is
  isolated in `build_xmp_packet()`, so that's a small extension.
