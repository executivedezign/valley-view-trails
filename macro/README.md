# Macro Exposure — EOS R5 with the Laowa macro set

A single-page web app for manual macro work: effective aperture, depth of field,
rail step and flash power. Needs no network at all — every number is computed on
the phone — so it works anywhere, unlike the weather app next door.

Lives at `/macro/`, with its own page, manifest, service worker and icon.

## Why this exists rather than an exposure triangle app

At macro magnifications the marked f-stop is close to fiction. Light reaching
the sensor follows the **effective aperture**:

```
N_eff = N · (1 + m/P)          light lost = 2·log₂(1 + m/P)
```

and everything downstream — exposure, diffraction, depth of field, flash power —
follows from that number rather than the one on the barrel. Wide open, across
this kit:

| Lens | m | Marked | Effective | Lost |
|---|---|---|---|---|
| 15mm f/4 Shift | 1:1 | f/4 | f/8 | 2.0 stops |
| 24mm f/14 Probe | 2:1 | f/14 | f/42 | 3.2 stops |
| 25mm Ultra | 2.5x | f/2.8 | f/9.8 | 3.6 stops |
| 25mm Ultra | 5x | f/2.8 | f/16.8 | 5.2 stops |
| 100mm APO | 2:1 | f/2.8 | f/7.3 | 2.7 stops |
| 180mm APO | 1.5x | f/4.5 | f/11.2 | 2.6 stops |
| Aurogon, NA 0.5 | 20x | — | f/21 | — |
| Aurogon, NA 0.5 | 50x | — | f/51 | — |

The probe at f/14 is four stops darker than the barrel says, which is why open
shade needs ISO 3200 on it.

### Pupil magnification

Laowa documents the 100mm APO at 1.7 stops of loss at 1:1 and 2.7 at 2x — lower
than a symmetric lens would give, because it isn't one. Those two figures pin
P = 1.29, which then reproduces both to within a twentieth of a stop and
predicts the intermediate magnifications. Every other lens is treated as
symmetric (P = 1), the standard assumption absent published figures.

The Aurogon is specified by numerical aperture instead, so it uses the working
f-number, `(1 + m) / 2NA` — the same quantity by another road. Its eight NA
detents are spaced logarithmically from 0.5 to 0.15, the way aperture scales
always are.

## What the light loss does and does not mean

The R5 meters off the sensor, so with a fully manual lens **the loss is already
reflected in what the meter shows**. It is not a correction to dial in. It bites
on three things instead: manual flash power, ISO headroom, and diffraction.

## Diffraction

Airy disk diameter is `2.44·λ·N_eff` at 550 nm, against the R5's 4.39 µm pixel
pitch. Reported in three bands rather than as one threshold, because diffraction
is not a cliff:

- below ~f/6.5 effective — not diffraction limited
- f/6.5 to ~f/22 — softening at 100%, invisible in a print
- past ~f/22 — visible in print too

Every row of the table above is at or past the first threshold wide open. On
this kit the question is never whether you are diffracted, only which
compromise to take.

## Depth of field and stacking

```
DoF = 2 · N_eff · c / m²
```

Two circles of confusion are offered: 0.030 mm, the traditional print standard,
and 0.009 mm, roughly two pixels on a 45 MP sensor and the honest figure if you
inspect at 100%.

The payoff is the rail step: step = DoF less the overlap, default 30%. Slices
that merely touch leave banding where the sharp zones meet. Frame count follows
from the subject depth.

At 5x and f/2.8 that is a 40 µm slice; on the Aurogon at 20x it is 3 µm, which
is below what a manual rail resolves — the app says so.

## Flash

Five of the six lenses have no electronic contacts, so the camera has no
aperture to work from and TTL cannot compute a correct exposure. Manual power is
the only reliable path, and guide numbers are quoted in metres and stop meaning
much at a 20 mm working distance.

So the app works from a baseline instead: save a frame that came out right, and
it reports the power correction whenever magnification, aperture or ISO change.

```
Δstops = 2·log₂(N_eff_now / N_eff_base) − log₂(ISO_now / ISO_base)
```

Shutter speed is deliberately absent from that. Below sync the entire flash
lands in the frame regardless of shutter, which controls ambient only. Sync on
the R5 is 1/200 mechanical and 1/250 with electronic first curtain, and the
fully electronic shutter will not fire flash at all — the app refuses to hand
you a setting past that.

## Files

- `index.html` — the whole app; lens data at the top, physics in the section marked as such
- `make-icon.py` — draws the icon set; re-run after changing the artwork
- `sw.js`, `manifest.json`, `icon-*.png` — install and offline shell

Lens specifications come from the owner's Laowa/R5 settings reference: aperture
ranges, magnification ranges, working distances and handling notes.
