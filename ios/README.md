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

## The bridge

No dates are computed in Swift. The Hebrew calendar, the cycles and the
Sefirah hours all live in the page, and a second implementation would drift
from the first. Instead the page posts a snapshot — `kotSnapshot()` in
`index.html` — and the app stores and displays it.

The snapshot carries the Hebrew and civil dates, the ma'alot and prayer
counts, the Sefirah of the hour, the seven Sefirah windows with their start
and end times, and the ten prayers with the hour each falls in. It is posted
on load, whenever a ma'alah or prayer is marked, and once a minute. In a
browser `window.webkit` is undefined and none of it runs.

Both targets share `Snapshot.swift` and the App Group
`group.com.kabbalahoftime.shared`, so there is one model and one store.

## Prayer notifications

A local notification when each prayer's Sefirah hour opens — the flashing tag
on the card, reaching you with the app closed. All ten are scheduled: the three
Mochin take the half hour either side of Chatzot, where Ma'alot HaZman places
them, so Hitbodedut, Tikkun Rachel and Tikkun Leah have hours of their own.

Triggers repeat daily and are rewritten every time the app runs, so sha'ot
zmaniyot — which drift a few minutes a day — stay close without the app having
to be opened at any particular moment.

## The widget

Small and medium: the Hebrew date, the Sefirah of the hour, and the two
counts — ma'alot out of fifteen, prayers out of ten. The timeline turns over
at each Sefirah window boundary, so the hour stays current on its own.

A snapshot from a previous day shows the counts as zero rather than carrying
yesterday's over, since both reset with the Jewish day.
