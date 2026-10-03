# Daily Grace

*A little reminder of God, every day.*

Daily Grace is a private, offline Android app that shows one Bible verse and one peaceful
wallpaper each day, with a short reflection and prayer. It is built for direct APK sharing
within a small Christian community, not for the Play Store.

**Verse first, artwork second.** The verse is always real text drawn by the app over the
artwork, never baked into an image, so it is always correctly spelled, crisp and readable.

## What's in V1

| Screen | What it does |
| --- | --- |
| Today | Full-screen artwork with today's verse, gentle motion, reflection and prayer, Save / Set Wallpaper / Share |
| Wallpapers | Every wallpaper, filterable by category |
| Detail | Any wallpaper or past day, with the same actions |
| Set Wallpaper | Live preview on a frame shaped like *your* phone, lock/home simulation, verse on/off, Home / Lock / Both |
| Favorites | Saved verses in a grid |
| History | Every day since first use (at least two weeks), newest first |
| Prayer | Today's prayer, morning and evening prayers, prayers from Scripture |
| Settings | Daily reminder and time, wallpaper verse default, gentle motion, about |

- Works fully offline. No account, no server, no analytics, no ads.
- Permissions: `SET_WALLPAPER`, `POST_NOTIFICATIONS` (only asked when the reminder is turned on)
  and `RECEIVE_BOOT_COMPLETED` (to keep the reminder after a restart). Nothing else.
- Scripture: **King James Version (KJV)**, public domain, used consistently. "LORD" is set in
  small capitals as in printed KJV Bibles. Every verse was checked against a public-domain KJV text.

## Tech stack

Kotlin, Jetpack Compose (Material 3), Navigation Compose, SharedPreferences, AlarmManager.
No image library, database or network layer: content ships in `assets/` and is read with `org.json`.
minSdk 26 (Android 8), targetSdk 35.

## Project structure

```text
app/src/main/
  assets/
    content/verses.json     verses, reflections, prayers, layout per wallpaper
    content/prayers.json    the Prayer tab
    wallpapers/             1440 x 3200 master artwork (20:9)
    wallpapers/thumbs/      432 x 960 thumbnails for grids
  res/font/                 Cormorant Garamond (Scripture), Inter (UI)
  java/com/dailygrace/app/
    data/      content model, parser, daily schedule, preferences
    image/     safe-zone crop maths, verse typography rules, image loading
    render/    draws artwork + verse into a bitmap (wallpaper, share image, preview)
    actions/   set wallpaper, share
    notify/    daily reminder
    ui/        theme, components, screens, navigation
tools/artwork/              generator for the placeholder artwork
```

## Adding wallpapers 030, 031, ... (no code changes)

1. Put the artwork at `app/src/main/assets/wallpapers/wallpaper_030.jpg` (1440 x 3200) and a
   432 x 960 copy in `wallpapers/thumbs/` with the same name.
2. Add an entry to `entries` in `assets/content/verses.json`:

```json
{
  "id": "030",
  "dateIndex": 30,
  "image": "wallpaper_030.jpg",
  "verse": "The LORD is my shepherd; I shall not want.",
  "reference": "Psalm 23:1",
  "theme": "Peace",
  "categories": ["Psalm 23", "Peace"],
  "reflection": "…",
  "prayer": "…",
  "layout": "bottom"
}
```

`layout` is `top`, `center` or `bottom`: put the verse where the artwork is calm. Optional
`focusY` (0 to 1) says where the important subject sits vertically. A new category name in
`categories` appears in the Wallpapers filter automatically. Entries with a missing image or
an empty verse are skipped rather than crashing the app.

The day-to-wallpaper mapping cycles through entries in `dateIndex` order starting on
3 October 2026 (`DailySchedule.ANCHOR`), so adding entries lengthens the cycle.

## Artwork rules

All wallpapers are composed for 20:9 at 1440 x 3200 with a safe-zone approach:

- **Critical safe zone**: the central 72% of width and height holds the verse, faces, the
  cross, people and other important objects.
- **Flexible zone**: sky, clouds, land and water fill the outer areas and may be cropped a little.
- **No text in the artwork.** The app renders Scripture itself.
- Leave calm negative space where the entry's `layout` puts the verse.

The current images are **placeholder artwork** painted procedurally by
`tools/artwork/generate.py` (Python 3 with Pillow and NumPy). Replace them with final
illustrations at any time; keep the file names or update `verses.json`.

## How wallpapers fit every phone

`WallpaperFit` picks the largest crop of the art with the phone's exact aspect ratio (so zoom
is the minimum possible), centres it on the artwork's focus and keeps the safe zone intact. The
wallpaper is then rendered at the phone's physical resolution, with the verse laid out for that
size, and applied with `WallpaperManager`. Unit tests cover the Galaxy S22 Ultra (both
resolutions), 6.5", 6.7" and 6.9" phones at 19.5:9 and 20:9, and older 18:9 and 16:9 screens.
On every one of them the full safe zone is kept.

## Building

The GitHub Actions workflow builds both APKs on every push:

- **Actions tab → latest run → Artifacts**: `daily-grace-debug-apk` and `daily-grace-release-apk`.
- **Tag a version** (`git tag v0.1.0 && git push --tags`) to publish both APKs on the
  Releases page, where they can be downloaded straight to a phone.

Locally, with Android Studio or the Android SDK installed:

```bash
./gradlew assembleDebug      # app/build/outputs/apk/debug/DailyGrace-debug.apk
./gradlew assembleRelease    # app/build/outputs/apk/release/DailyGrace-release.apk
./gradlew testDebugUnitTest
```

### Release signing

Every release you share must be signed with the **same key**, or phones will refuse to
update. Keep the keystore safe and private.

- Locally: create `keystore.properties` in the project root (it is git-ignored):

  ```properties
  storeFile=signing/daily-grace-release.jks
  storePassword=…
  keyAlias=dailygrace
  keyPassword=…
  ```

- On GitHub: add repository secrets `DG_KEYSTORE_BASE64` (the keystore file, base64-encoded),
  `DG_KEYSTORE_PASSWORD`, `DG_KEY_ALIAS` and `DG_KEY_PASSWORD`.

The debug build installs alongside the release build (`com.dailygrace.app.debug`).

## Installing on a phone

Send the APK to the phone, open it, and allow "Install unknown apps" for the app you opened it
from (Files, WhatsApp, Chrome…) when Android asks.

## Credits

- Scripture: King James Version, public domain.
- Fonts: Cormorant Garamond and Inter, SIL Open Font License 1.1.
