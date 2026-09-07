# autotone

Analyzes JPEG photos for exposure, contrast, color cast, and saturation
problems, then writes **per-image corrections** that your editor applies for
you:

- **Lightroom 5+** — the corrections are embedded in each JPEG as Camera Raw
  (Process 2012) develop settings. Import the photos and they arrive with the
  sliders already set; every correction stays non-destructive and editable.
- **Photoshop 6 (2000)+** — optionally writes a `photo.acv` curves file next to
  each image. Open the image, open Curves, click **Load**, pick the `.acv`.

Only the JPEG's metadata block is modified. **Image pixels are never
recompressed or altered.**

## Setup

Requires Python 3.10+.

```
pip install -r requirements.txt
```

## Usage

```
python autotone.py C:\Photos\hike-2026-09           # embed corrections in place
python autotone.py C:\Photos\hike-2026-09 --report  # preview only, change nothing
python autotone.py C:\Photos --recursive --backup   # keep untouched .orig copies
python autotone.py C:\Photos\hike --acv             # also write Photoshop .acv files
python autotone.py C:\Photos\hike --strength 0.7    # gentler corrections (0.0-1.5)
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

## Photoshop 6 workflow

With `--acv`, each image gets a `same-name.acv` file approximating the same
corrections as curves (master tone curve + per-channel color balance).
In Photoshop 6: open the image, **Image > Adjust > Curves**, click **Load…**,
select the `.acv`. Works in every later Photoshop version too.

## Building a standalone .exe (Windows)

On a Windows machine with Python installed:

```
pip install pyinstaller Pillow numpy
pyinstaller --onefile --name autotone autotone.py
```

The result is `dist\autotone.exe` — a single file, no Python needed to run it.
You can then drag a folder onto a shortcut to it, or run it from the command
prompt as above.

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
