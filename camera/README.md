# Camera Weather — is it safe to take the gear out?

A single-page web app that takes your GPS position, pulls the local weather, and
answers one question with a traffic light: should the camera and lenses go
outside right now. Installs to the home screen like the trail map.

Lives at `/camera/` alongside the trail map, and shares nothing with it — its
own page, manifest and service worker.

## Why dew point, not humidity

Water condenses on any surface colder than the surrounding air's dew point. So
"is it humid out" is the wrong question; the right one is **is my gear colder
than the dew point where I am standing.** A 70 °F camera walking into 78 °F air
at a 72 °F dew point fogs instantly, while the same camera in 95 °F desert air
never will.

That is why the app asks where the gear has been sitting. Everything else —
rain, wind-blown dust, heat, cold — is a modifier layered on top.

## The rules

The verdict is the worst of these; the note under the light explains the worst one.

| Risk | Amber | Red |
|---|---|---|
| Condensation | gear within 4 °F of dew point | gear below dew point |
| Lightning | — | thunderstorm codes 95/96/99 |
| Rain, fully sealed | 45 % in 3 hr | 75 %, or raining now |
| Rain, sealed body + bare lens | 25 % | 55 %, or raining now |
| Rain, unsealed | 15 % | 40 %, or raining now |
| Wind | gusts ≥ 20 mph — no lens changes outdoors | gusts ≥ 35 mph |
| Heat | ≥ 95 °F in open sun — video thermal limits | — |
| Cold | ≤ 25 °F — battery life halves | — |

Only condensation causes permanent damage; the rest are inconvenience or risk to
the shot. Weather sealing does nothing against condensation, so that row ignores
the sealing setting entirely.

## Coming back inside

Going out is usually the safe direction. The damage happens on the way home,
when cold gear meets warm indoor air and moisture condenses *inside* the lens
barrel where no cloth reaches — which is where fungus and permanent haze start.

The app assumes the gear ends the outing at ambient temperature and compares
that against an estimated indoor dew point: about 45 °F in a heated house
(70 °F at 40 % RH), and outdoor dew point capped at 58 °F in cooling season. If
the gear will come home below that, it tells you to seal it in a bag **while
still outside** and gives an equalisation time of roughly one hour per 20 °F of
difference, floored at 20 minutes and capped at 3 hours.

## Storage presets

The picker sets a starting temperature, and the field below it can be typed over
to set the number exactly.

- **In the house** — fixed 70 °F
- **Garage / shed** — tracks outdoors, pulled 45 % of the way toward 58 °F
- **Car trunk** — outdoor temperature plus 26 °F in daytime sun, 9 °F under
  cloud, 2 °F after dark

The trunk estimate is the roughest of the three. If you have a thermometer in
there, type the real number.

## Hourly strip

The same rules run against each of the next 24 hours, with the gear still
leaving at its stored temperature, so the colours answer "if I went out then,
what happens" — green means go. Tap an hour for its numbers.

## Data

[Open-Meteo](https://open-meteo.com) for the forecast — no API key, CORS-enabled,
so the app stays a static file with no backend and no secrets. Place names come
from BigDataCloud's keyless reverse geocoder and fail silently to coordinates.

Coordinates go to those two APIs and nowhere else; nothing is stored off the
phone. Settings and the last reading live in `localStorage`.

**This app needs a connection** — unlike the trail map, a forecast cannot be
carried offline. The service worker caches the shell only, deliberately: a stale
forecast is worse than none. The last reading is shown while a fresh one loads,
timestamped at the bottom.

## Files

- `index.html` — the whole app; rules are in `assess()` and `homecoming()`
- `sw.js`, `manifest.json` — home-screen install and shell caching

To change a threshold, edit `SEAL_RAIN` or the numbers in `assess()`.
