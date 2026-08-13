# Valley View Trails — offline GPS trail map

A single-page web app that shows your live GPS position on the Valley View
Walking Trails map. Works offline once loaded (GPS needs no cell signal), and
installs to the home screen on iPhone and iPad.

## Using it

Open the hosted link, enter the passcode, allow location, and tap ◎ to follow
your position. The passcode is remembered on that device afterwards.
On iOS: Share → **Add to Home Screen** to get an app icon and full-screen mode.

- One finger drags, two fingers pinch to zoom
- ◎ toggles follow-me; panning by hand turns it off
- The ring around the dot is the GPS accuracy radius, drawn to map scale
- The **N** badge points to true north (the map sits 6.25° off north)

Location requires an `https://` page — opening `index.html` straight off disk
will not get a fix, because browsers withhold GPS from `file://` pages.

## How the georeferencing works

The map is trail overlays painted onto to-scale Google Earth imagery, so
latitude/longitude maps to map pixels through a plain similarity transform
(uniform scale, rotation, translation). It was fitted by least squares to three
landmarks read off Google Earth:

| Landmark | Coordinates | Residual |
|---|---|---|
| Pond, north tip | 42°19'53.71"N 75°22'01.84"W | 2.3 m |
| Grey roof, top-right corner | 42°19'57.70"N 75°21'59.33"W | 1.7 m |
| White building by the pines | 42°19'41.24"N 75°22'02.16"W | 0.6 m |

Result: **2.3425 px/m**, rotated **6.25°** off north. All three residuals sit
inside typical phone GPS error (3–5 m, worse under tree cover), so the fit is
not the limiting factor on accuracy — the phone is.

The scale was cross-checked against a Google Earth export whose scale bar
measured exactly 800 px per 1000 ft.

## The map is encrypted

`map.enc` is the map image under **AES-256-GCM**, with the key derived from a
passcode by PBKDF2-SHA256 (310,000 iterations, random 16-byte salt). The site is
public, so the published file is deliberately meaningless without the passcode —
it carries no JPEG signature and measures 7.997 bits/byte of entropy, which is
indistinguishable from random noise. Decryption happens in the browser via
WebCrypto; the passcode is never transmitted.

GCM is authenticated, so a corrupted or altered file is rejected rather than
rendered as a broken image.

**The passcode cannot be recovered.** It is not stored anywhere — not in this
repo, not on the server. If it is lost, re-encrypt from the local `map.jpg`
with `encrypt-map.html` and republish.

To change the passcode or the map: re-run `encrypt-map.html` (kept outside this
repo, in `Desktop\MAPS\`), pick `map.jpg`, and replace `map.enc`.

## Files

- `index.html` — the whole app; georeference constants are inlined at the top of the script
- `map.enc` — encrypted 1600×2071 map render (0.43 m/px on the ground)
- `sw.js`, `manifest.json` — offline caching and home-screen install
- `icon-*.png`, `apple-touch-icon.png` — app icon; original artwork, a plan-view
  trail network with the app's own locator dot. Regenerate with `make-icon.py`
  in `Desktop\MAPS\`. `icon-maskable.png` is inset so Android's circle crop
  cannot clip the dot.

`map.jpg`, the plaintext source, is gitignored and stays local — publishing it
would defeat the encryption.

Caching is network-first for the app shell and cache-first for `map.enc`, so a
published update actually reaches a phone that already installed the app, while
the large map still loads instantly offline.

To re-georeference after changing the map image, refit the transform against
landmarks and replace the `G = {...}` constants in `index.html`.

## Also in this repo

`camera/` is a second, unrelated app on the same GPS idea: it reads your
location, pulls the local dew point, and says with a traffic light whether the
camera and lenses should go outside. See `camera/README.md`.

`macro/` is a third: effective aperture, depth of field, rail step and flash
power for manual macro work with the Laowa set on an R5. No GPS, no network —
pure optics. See `macro/README.md`.

## Credits

Trail routes and map design by Rob. Satellite imagery © Google / Airbus.
