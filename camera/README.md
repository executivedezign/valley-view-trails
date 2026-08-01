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
| Rain, both sealed | 45 % in 3 hr | 75 %, or raining now |
| Rain, one of the two sealed | 25 % | 55 %, or raining now |
| Rain, neither sealed | 15 % | 40 %, or raining now |
| Wind | gusts ≥ 20 mph — no lens changes outdoors | gusts ≥ 35 mph |
| Heat | ≥ 95 °F in open sun — video thermal limits | — |
| Cold | ≤ 25 °F — battery life halves | — |

Body and lens are picked separately, and the rain row follows the weakest of the
two — a sealed body behind a bare lens is still a bare lens, so the four
combinations collapse to the three tiers above.

Only condensation causes permanent damage; the rest are inconvenience or risk to
the shot. Weather sealing does nothing against condensation, so that row ignores
the sealing setting entirely.

## Coming back inside

Going out is usually the safe direction. The damage happens on the way home,
when cold gear meets warm indoor air and moisture condenses *inside* the lens
barrel where no cloth reaches — which is where fungus and permanent haze start.

The app assumes the gear ends the outing at ambient temperature and compares
that against the dew point *inside your house*, computed by Magnus-Tetens from
the indoor temperature and humidity you set. If the gear will come home below
that, it tells you to seal it in a bag **while still outside** and gives an
equalisation time of roughly one hour per 20 °F of difference, floored at 20
minutes and capped at 3 hours.

Indoor humidity is asked rather than assumed because guessing it is worth about
25 °F of error. The same 70 °F house:

| Indoor RH | Dew point | Gear colder than this fogs on the way in |
|---|---|---|
| 20 % — tight house, deep winter | 27 °F | |
| 30 % | 37 °F | |
| 40 % | 45 °F | |
| 50 % | 50 °F | |
| 60 % — humidifier, or summer without AC | 55 °F | |
| 70 % — basement | 60 °F | |

A fixed 45 °F assumption is wrong in both directions: it nags for nothing in a
dry winter house, and it misses the real risk in a humid one, which is the
direction that costs a lens. Presets cover dry winter / average / humid or no
AC / basement, and the field below takes an exact hygrometer reading.

Above 60 % the settings panel also raises lens fungus, which grows on coatings
and between elements in sustained humidity and effectively stops below about
50 %. That is a storage problem rather than an outing problem, so it is a note
rather than part of the verdict.

## Storage presets

The picker sets a starting temperature, and the field below it can be typed over
to set the number exactly.

- **In the house** — the indoor temperature set below it
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
