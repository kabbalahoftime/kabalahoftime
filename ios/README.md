# Kabbalah of Time — iOS

The app is the site in a WKWebView, plus the things a browser tab cannot do.
This directory holds only what Xcode needs; `index.html` stays at the
repository root and is referenced from there, so there is never a second copy
to keep in step.

## Building

The `.xcodeproj` is generated rather than committed — it never conflicts in
git and never drifts from what is actually in the tree.

```sh
brew install xcodegen
cd ios
xcodegen generate
open KabbalahOfTime.xcodeproj
```

Then set your Team under Signing & Capabilities and run. Bundle identifier is
`com.kabbalahoftime.KabbalahOfTime`; change `bundleIdPrefix` in `project.yml`
if you want another.

**Nothing here has been compiled.** It was written on Linux, where there is no
Xcode, so treat the first build as the first test.

## How it loads

It loads **the live site**, not the bundled copy. Two reasons:

1. The app changes several times a day. Loading remotely means a merge to main
   is on the phone at once, instead of waiting on App Store review.
2. The ma'alot, the miutim and the ten prayers live in `localStorage`, which is
   per-origin. Serving the bundled file would be a different origin and so a
   different, empty store — you would lose the day's marks every time the app
   fell back.

Offline is covered by the site's own service worker, which is already
network-first for HTML and cache-first for the fonts and icons. The bundled
copy is the cold-start fallback only: a first ever launch with no network,
before the service worker has installed. After that the service worker
answers and the bundled copy is never used.

Links to Sefaria, HebrewBooks, Chabad.org and the recordings open in
`SFSafariViewController`, so a tap doesn't navigate the app away from the
day's page.

## Still to build

The shell alone is a repackaged website, which App Review rejects under
guideline 4.2. Two things earn it past, and both are worth having:

- **Prayer notifications.** The ten prayers already have their Sefirah hours
  in `SEFIRAH_TIMES`. A local notification when each hour opens is what the
  flashing tag does now, except it reaches you with the app closed.
- **A widget.** The ma'alot moon and its count, the KoT day, the Sefirah of
  the hour. The widget cannot run a web view, so the app should compute a week
  ahead on each launch and write it to a shared App Group container for the
  widget to read — rather than porting `gregToHebrew` and `calibrateOffset` to
  Swift, where the two implementations would eventually disagree.
