# NHW Field Log — what to record at each session

A single-page web app for logging macro outings in the field, built to
`NHW_Field_Log_Spec_v2` (28 Oct 2026). It records everything a future book
needs that the camera does not, at three levels linked by IDs and camera file
numbers: the **session** (once per outing), each **subject** found, and each
**shot** (frame, burst or stack). Installs to the home screen like the trail map.

Lives at `/fieldlog/` alongside the other apps and shares nothing with them —
its own page, manifest, service worker and storage.

## Using it

Open the hosted link in Safari, then Share → **Add to Home Screen**. Open it
from the icon from then on: that is what keeps the data, and lets iOS protect
it from clean-up.

1. **Start a session.** GPS is taken at once; place, access and gear carry over
   from the last session. Photograph the big clock with the camera and note that
   frame's number (or type the difference in seconds if you can read it).
2. **+ New subject** for each find: phone ID photo, name, kind, size, what it is
   on, and so on. The form only shows what applies — tree partners and ID
   features for fungi, behaviour for animals.
3. **+ New shot** for each frame, burst or stack. Picking a lens fills its
   profile and limits magnification and aperture to that lens. **Next shot**
   copies everything from the shot before and offers the next file number.
4. **End session**, then **Export**: one zip per session, shared to Files,
   Mail or AirDrop.

Each record shows how many needed fields are still blank. Nothing blocks you
from moving on — fill gaps later, at home if need be.

### Typing or voice

Every text box takes typing, or the 🎤 on the iPhone keyboard for dictation
(works with no signal on recent iPhones). Session notes, subject notes and
"why these settings" also have **● Record voice memo**, which keeps the audio
itself; it is exported next to the spreadsheet. iOS may ask for microphone
permission the first time.

## Offline first

Everything is stored on the phone (IndexedDB) and the app shell is cached by
the service worker, so the whole log works with no signal. Weather is the one
online lookup: it is fetched from Open-Meteo for the **hour the session
started**, whenever the phone next has signal, and only fills fields you left
blank — what you typed always wins. It also supplies rain over the previous
24 hours and 3 days.

**Removing the app from the home screen deletes its data.** Export each
session when you get home.

## Location privacy

The exact GPS position of the session and of each subject is kept on the phone
for the weather lookup and your own reference. It is **never exported** — not in
the spreadsheet, not in file names. The book only gets the public place
description. Land access is exported, labelled as private.

## Lens profiles

Built in from `NHW_Lens_Profiles.xlsx` (copy in this folder). Choosing a lens
fills mount, contacts, focal length, working distance, IS reminder, light note,
default support and the book's "How it was made" line, and:

- shows magnification quick picks from the profile (plus an "other" box);
- shows f-stops limited to the lens's range, or the eight NA detents
  (0.50 → 0.15, log-spaced as in the Macro Exposure app) for the Aurogon;
- hides aperture for the 100mm, which the camera records;
- offers in-camera focus bracketing only for a lens whose profile allows it
  (none in the current kit);
- remembers your last magnification, aperture, light and support per lens.

To change the kit, edit the spreadsheet (Lenses, Lights, Supports, Camera tabs)
and import it under **Lens profiles, storage and help**. Columns are found by
header name, so their order does not matter. Lights whose name contains
"diffuser" or "reflector" are offered as modifiers rather than light sources.

## Export

`NHW-YYYYMMDD-N.zip` holds:

- `NHW-YYYYMMDD-N.xlsx` — tabs **Session** (field / value), **Subjects** and
  **Shots** (one row each), with lens-profile columns on every shot;
- `photos/<subject ID>_1.jpg` … — the phone ID photos;
- `voice/<record ID>_<field>_1.m4a` … — the voice memos.

IDs: session `NHW-20261028-1`, subject `NHW-20261028-1-S01`, shot
`NHW-20261028-1-S01-03`. With the camera file numbers on every shot, entries
can be matched to the `MACRO__` raw files after renaming. Fields the form hid
(stack settings on a single frame, say) export blank rather than stale.

The xlsx writer and reader are in the page itself (no library), so export and
import both work offline.

## Not in this version

- Reading the raw files: working out the clock offset from the clock frame, and
  filling shutter speed and ISO from the CR3s (spec sections 1 and 5).
- The desk-side fields of spec section 6: final ID and who confirmed it,
  processing done, art title.

## Files

- `index.html` — the whole app, including the built-in lens profiles
- `NHW_Lens_Profiles.xlsx` — the editable kit list the app imports
- `sw.js`, `manifest.json` — offline caching and home-screen install
- `icon-*.png`, `favicon-32.png` — a ruled field-notebook page with a mushroom;
  regenerate with `make-icon.py`
