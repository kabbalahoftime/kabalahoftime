# Kabbalah of Time

A single-file PWA. `index.html` is ~2.9 MB and holds the markup, the styles and
every script inline; there is no build step and no bundler. Edit it in place.

Published by GitHub Pages from `main` to **www.reflectionsofitall.com** (`CNAME`).

## Writing

**Use simple and direct language wherever it is possible.** This holds for the
app's own text, the ⓘ notes, the Help Guide, commit messages and anything said
to the reader. A complex idea still has to arrive in words a bright child could
follow. Prefer the short word, the short sentence, the plain statement. When a
sentence runs past about thirty words, it is usually two sentences.

The ⓘ notes come in three depths — `beginner`, `main` (the intermediate
default) and `advanced`. `infoProse(entry)` falls back to `main` when a depth
is missing.

## Two rules that will bite

**1. Bump the cache on every change that ships.** `service-worker.js` holds
`CACHE_NAME = 'kabbalah-of-time-vNNN'`. Returning visitors keep the old copy
until that string changes, so a correct fix that forgets the bump reaches
nobody. Currently **v335**; the next is v336.

**2. Run `check.mjs` before anything reaches `main`.**

```sh
node check.mjs          # ~4 minutes, binds 127.0.0.1:8731
```

56 checks over 17 sections, ending in `all checks passed`. Its own header
explains what each section is for and which bug put it there — read that rather
than guessing. Playwright lives at `/opt/pw-browsers/chromium`; override with
`CHROMIUM=/path/to/chromium`.

Run it in the background and **wait by polling the log for `all checks
passed`**, never by polling the process table:

```sh
node check.mjs > /tmp/check.log 2>&1       # run_in_background: true
# then, in a later call:
grep -cE 'fail|✗|Error' /tmp/check.log
grep -v '^$' /tmp/check.log | tail -1
```

`pgrep -f "node check.mjs"` matches **its own wrapper shell**, so a loop that
waits on it waits forever. That has cost two sessions already. Equally, never
put `&` inside a command that is already backgrounded — it orphans the run,
which then squats on 8731 and the next run dies with `EADDRINUSE`. Clear it
with `kill <pid>`, by pid.

Never `pkill -f "http.server <port>"` — the pattern matches the calling shell
and kills it. Use a fresh port instead.

## Branches

Develop on the feature branch. `main` is live, so merging to it publishes.

```sh
git fetch origin main
git checkout main
git merge --ff-only <branch>
git merge-base --is-ancestor origin/main HEAD   # confirm nothing is skipped
git push origin main
```

Local `main` is often far behind `origin/main`; fetch before trusting it.
Pages takes a minute or two, and an open app keeps the old service worker
until its next load — so the old text showing straight after a push is the
cache, not a failed push.

## The books

Manuscripts in `docs/*.md`, typeset to PDFs at the repo root by the shared
setter. Edit the manuscript, never the PDF.

```sh
python3.13 tools/make_book_pdf.py docs/<name>.md <name>.pdf
```

**`python3` on PATH is 3.11 and pip installs into 3.13**, so the setter only
runs under `python3.13`. A fresh container has neither the packages nor the
faces; `tools/setup_book_fonts.py` does both in one step and is safe to re-run.

It handles verse, `[links](url)`, Hebrew (flush right, Frank Ruhl Libre built
at run time from `fonts/`), bidi, and footnotes. Its docstring covers the
heading grammar (`## kicker | title | subtitle`, `### title | subtitle`).

**After every rebuild, check the page count against the published one.** A
reflow that adds a page usually means something upstream broke.

| manuscript | PDF | pages |
| --- | --- | --- |
| `docs/from-the-new-moon-to-the-next.md` | `from-the-new-moon-to-the-next.pdf` | 31 |
| `docs/from-the-sunrise-to-the-next.md` | `from-the-sunrise-to-the-next.pdf` | 14 |
| `docs/ascents.md` | `ascents.pdf` | 52 |
| `docs/reflections.md` | `reflections.pdf` | 119 |
| `docs/alef-bet.md` | `alef-bet.pdf` | 41 |
| `docs/daily-companion.md` | `daily-companion.pdf` | 461 |

`perek_shirah_booklet.pdf` has no manuscript here.

`branches-sciences.pdf` and `branches-arts.pdf` are the two volumes of
**Branches** — the sciences and the arts — and each is the source its own
JSON is built from. Both rows on the shelf say they were written with AI.

**Book 7 does have a manuscript**, and this file used to say it did not.
`book7_content.txt` at the repo root, set by `make_book7_pdf.py` beside it —
not `docs/` and not `tools/`, and it takes no arguments:

```sh
python3.13 make_book7_pdf.py        # book7_content.txt -> book7_gathering_of_songs.pdf
```

The songs are set in **stanzas of four**, and a blank line in the source is a
stanza break. So a source with a blank line after every line gives one stanza
per line, which the setter renders faithfully at stanza spacing: the week
comes out double-spaced and ungrouped. Week 8 shipped that way, along with
its opposite — fourteen lines run into a single block where the blank lines
were missing. The setter now warns on both, naming the week; it does not fail
the build, because several weeks legitimately carry a five- or six-line
stanza and most end on a single line. 100 pages.

**A changed PDF needs a cache bump to reach anyone.** PDFs fall to the last
branch of the service worker's fetch handler, which is cache-first with no
revalidation — a reader who has opened a book keeps that copy until
`CACHE_NAME` changes and `activate` purges the old cache.

The sciences volume was `branches-roots.pdf` while the book was called
*Branches / Roots*. It is retitled simply *Branches*, so the filename that
matched the old title has gone with it and the two volumes are named alike.

`a-year-inside-the-day.pdf` is the **old** companion text and is not linked
from the app: it carries fabrications the rewrite removed. It has a manuscript
now (`docs/a-year-inside-the-day.md`) and still no setter of its own.

`docs/daily-companion.md` is the one manuscript here that is **generated, not
written** — `tools/build_companion_book.py` makes it from `companion-days.json`,
which is itself built from `docs/companion-summaries.md`. Edit the summaries;
never this file and never the PDF. The chain is

```sh
# after any change to docs/companion-summaries.md
python3 -I tools/build_companion_days.py ...          # as in the section below
python3 -I tools/build_companion_book.py companion-days.json docs/daily-companion.md
python3.13 tools/make_book_pdf.py docs/daily-companion.md daily-companion.pdf
```

A page at every `##` is what kept the companion off paper: 364 entries would
have been 364 mostly-white pages. It is set by **week** instead — `##` takes
the week and `###` the day — so 52 openings carry seven readings each.

## Branches

Two volumes on one tree, shown in a shut section below the Kohelet artwork
with a switch at the top. The Arts volume's own Tree page is why it is one
section and not two: *there is one tree, not two — each branch bears two
fruits.* Ten stations, each bearing a science and an art.

| volume | PDF | JSON | shape |
| --- | --- | --- | --- |
| The Sciences | `branches-sciences.pdf` | `branches-sciences.json` | 10 × 5 sections |
| The Arts | `branches-arts.pdf` | `branches-arts.json` | 10 × 4 sections |

Every chapter has an opening, then a Torah-root section named differently
every time, `First doors`, `How X works`, `The present edge` — and, in the
sciences only, a closing `The ... at work`.

Both are **built from their PDF, not written here**, so the books stay the
source:

```sh
python3.13 -I tools/build_branches.py branches-sciences.pdf branches-sciences.json
python3.13 -I tools/build_branches.py branches-arts.pdf  branches-arts.json
```

The builder reads the page's **layout**, not its text, and asserts what it
finds: ten chapters, and **every chapter carrying the same number of
sections**. That regularity is the check — a count fixed at fifty was right
for the sciences and wrong for the arts, where "the shape holds even" is
right for both and still catches a section dropped from one chapter. Font
sizes carry the structure (53.3 book title, 36 chapter, 18 heading, 16
subtitle, 14.7 body, 12.7 station and kicker) and paragraphs come from the
vertical gap: 23-24 points inside a paragraph, 36-37 between, nothing in
between. Line length will not do it — a last line can run the full column,
and in the sciences volume one does.

Which volume a PDF is comes from its **title-page kicker**, "THE SEFIROT AND
THE ARTS", not from its title: one book is called *Branches* and the other
*Branches / Roots*, so the title will not tell them apart.

Each volume is **fetched when it is first asked for**, never on load, and
neither is pre-cached — the same reasoning written against `companion.json`
in `service-worker.js`. A reader who only opens the arts never pays for the
sciences. The service worker's JSON rule holds what was fetched for offline.

The reader's choice of volume is remembered in `kotBranchVolume`.

The cards use `.branch-card`, not `.sefirah-card`: that class is what
`buildCardPanes` files into the four panes, and these have sections of their
own.

### Leaves

`branches-links.json` holds links gathered by hand, shown as a **Leaves** fold
at the foot of a card that has any. A station with none gets no fold.

**It is written, never generated.** The two volumes are rebuilt from their
PDFs — three times in two days so far — so a link added to one of those would
be thrown away without a word. This file is the only place a link belongs, and
the builder never looks at it.

Keyed by volume and by **Sefirah, not by the name of the discipline**. The
names move: Malchut was Law before the rework and is Political Science now,
and a list keyed to the old name would have come away attached to nothing.

```sh
python3 -I tools/check_branch_links.py branches-links.json \
    branches-sciences.json branches-arts.json
```

Run it after any rebuild of a volume. It confirms every volume and station
named still exists, that each link has a label and an http(s) address, and
that nothing is listed twice under one station. It does not go to the network:
a checker that needs the internet fails on a train.

**Strip the tracking parameter.** A YouTube share link arrives as
`?si=...`, which identifies the sharer; store the bare address.

## The daily companion

`companion-days.json` is what the app fetches: **one KoT Book for one week,
each day**, filed the way Binah files them. Day 1 is Book 1's reading for week
1, day 2 is Book 2's for week 1, day 8 is Book 1's for week 2, day 225 is Book
1's for week 33. Seven books × fifty-two weeks = 364, and 364 posts on the
blog, one to each day, which is where each entry links.

An entry comes from one of two places and says which it is.

**A summary**, written in `docs/companion-summaries.md` against the week's
post for that book — what the writing teaches, not just what the readings
are. **Edit the manuscript, never the JSON.** These are the entries the
companion is for.

**Book 7's entries are short on purpose.** It is the gathering — the other
six books' verses rearranged, with no commentary of its own — so there is no
teaching to summarise. Its entries say what the braid makes and stop, in two
paragraphs and forty to eighty words. They were 340 words of quotations
chained with slashes, a median sentence of 175 words against the other books'
25 to 39, and the builder's floor of three paragraphs is relaxed for Book 7
alone because of it. The floor that remains catches an entry that failed to
get written: two paragraphs and thirty words.

**Otherwise a transcription** of the weekly table through seven templates,
one to a book. Nothing in those is composed, so nothing in them can be
invented, and the companion is never short of an entry while the summaries
are being written.

```sh
# 1. ask the page what it knows (needs a server on some port)
node tools/dump_week_data.mjs http://127.0.0.1:8731/index.html docs/week-data.json
# 2. build the entries — summary where one exists, table where not
python3 -I tools/build_companion_days.py docs/week-data.json index.html \
    companion-days.json docs/companion-summaries.md docs/companion-posts.json
# 3. every summary against its own post
python3 -I tools/check_companion_summaries.py docs/companion-posts.json companion-days.json
# 4. the app-claims sweep, which should flag nothing at all
python3 -I tools/check_companion.py index.html companion-days.json
```

### Writing a summary

Read the post. Write from it and from nothing else. Step 3 scores the
**proper nouns and numbers** in each entry against its own post, and any that
the post does not have is a fault — that is the "Isaiah 60:22" shape, a
citation the source never carried.

It has caught, so far, only my own habits rather than inventions: a verse
range merged out of two separate citations, a chapter-and-verse nobody wrote,
*Frankfurt* for *the Frankforter*, and a dozen transliterations the blog
spells its own way. **Match the post's spelling rather than aliasing the
check** unless the two really are one name; the alias list says which.

Two scopes are deliberately wider than one post. **Book 7** is the gathering —
the other six books' verses braided into one song, naming none of them — so
it answers to the week's seven posts. And a **Book 6** psalms post is often
bare psalm text with no commentary, so an entry for it must keep to the words
that are there; it cannot call the week Sukkot if its post never does.

**Rebuild it whenever the weekly table changes**, or the companion starts
saying last month's readings. Both steps are checkable by diff: re-run step 1
and diff `docs/week-data.json`, re-run step 2 and diff `companion-days.json`.
Either diff coming back non-empty means something upstream moved.

### Check the weekly table against the writing

```sh
python3 -I tools/check_week_table.py docs/week-data.json docs/companion-posts.json
```

Every week's reading has a post that names it, so the table can be checked
rather than trusted. **Run this after any change to the weekly table.** It
found four faults in one day, none of them visible from a single week:

- the prophets a week late from 24 to 50 (Yoel listed twice, as Yoel and Joel)
- the qualities a week late from 26 (Emunat Chachamim twice; two of the
  forty-eight sharing one cell at week 42)
- Chuldah missing from the prophets
- 31 of the 52 Levitical cities wrong — Jerusalem missing, the seven nations
  in weeks 40–42, daf of Nazir in 43–45, nothing at all in 46–52

A reader going a day at a time sees "the card says Nahum, the post says
Chabakuk" and patches that week. The cause — a duplicate nine weeks earlier —
only shows with all fifty-two side by side.

It reports repeats as notices rather than failures (Gath-Rimmon is twice in
Joshua 21), and it leaves out fields a post does not name: Book 4's Solomon
column holds a verse, not a reference, so there is nothing to match on.

It also checks the **shape of every post address** — Blogger gives each one
`/YYYY/MM/slug.html` and no other form. Week 8's Book 7 shipped with the
`.html` missing: a 404 in the companion, in the printed companion and on the
card. Nothing caught it, because the post's text had been fetched and cached
correctly, so every check that reads text passed and the only thing wrong was
a string nothing compared against anything. The shape can be compared, and it
costs no network call.

The companion's week is `(day − 1) / 7 + 1`. That matches the week the page
prints on all 364 days and all 28 intercalated ones — checked — so an entry
can never sit above the cards claiming a different week.

### The other companion, which is off

`companion.json` is a written 364-entry text, with its manuscript at
`docs/a-year-inside-the-day.md` and `tools/companion_from_md.py` to build it.
Nothing fetches it. Its own header marks weeks 1 and 2 as placeholder until
the real opening is written — creation as the creation of time, the six
thousand years, the Torah before the world — and those are the first fourteen
days a reader meets.

Its first version was AI-generated and invented a motto for this app, a verse
and a route. `docs/companion-audit.md` is the sweep that found it, the rule the
rewrite is held to, and six standing false positives in the checker — read
those rather than re-investigating them.

Books 1 and 2 are the author's own life in allegory, and the people in them are
real. **Never invent or adjust a biographical fact to make a sentence work.**
Where two books disagree about a fact, or a change would contradict one, say so
and ask. Lands carry other names — the Land of the Donkeys is Egypt and Brazil
at once — and no character is ever given a name except in the Epilogue of Book
2, where a child's own handwritten book is quoted verbatim. Leave that quotation
exactly as it stands.

LibreOffice is broken in this environment; read `.docx` XML directly.

## Panes and cards

Each card has a face and four panes. `_paneKind` files a detail block:
`.maalah.yom[data-wane]` → Mi'utim, `.maalah` → Ma'alot, `[data-rebbe]` →
Menorah, `[data-shelf]` or text opening with ✡ → Stars. `_paneTakeFace` moves
`.malchut-ksa-row` / `.malchut-section` off the face into a pane, filing by
`_paneKind([row])` — not by a fixed destination. `_paneTrim` hides a pane
button whose body is empty.

### Tzedakah

The day asks for four things — **meditation, prayer, study and action** — and
the Menorah pane is the action. `TZEDAKAH` in `index.html` holds one fund per
Sefirah (Chesed, Yesod and Malchut hold more than one), and `_paneTzedakah`
appends it to the foot of that card's Menorah pane. **Written by hand, never
generated** — the same rule the Branches leaves are kept under.

It is appended again on every pass, because the filing empties and refills a
pane each render and a block put there once would end up above the day's
reading. `appendChild` on a node already in the pane moves it to the foot.

The ladder's fourth line and the row's fourth column both read this table.
`kotFundSteps` holds which of the ten a reader has undertaken, the same
shape as `kotPrayerSteps`; the ordinals index `Object.keys(TZEDAKAH)`, so
the table's own order is the only list of the ten. The Action line hides in
the hour of a fund that is not undertaken. **No fund is ever marked or
counted** — giving happens on somebody else's page.

What the Action column counts is the menorah: `#rebbe-count`, the ten
bearers lit as they are gathered, written by `applyStarState` beside the
`nR` it already had. Kindling a light is a deed, so that tally sits with
the action and not at the end of the moon's row, where it was while the
stand was drawn there and read as part of the learning.

A reader can add funds of their own, kept in `kotFundsOwn` as
`[{sef, label, url}]` and nowhere else. **Nothing draws a fund from
`TZEDAKAH` directly** — the pane, the window, the chooser and the ladder
all ask `fundsFor(sef)`, which merges the written ones with the reader's,
flagging the latter with a third element so they can be marked *yours*.
`fundCleanUrl` adds `https://` to a bare host and refuses anything that is
not http(s), which is the one way a stored string here could do harm.
`_paneTzedakah` keeps a `data-sig` of what it drew, so a fund added or
dropped rebuilds the block instead of leaving the old one in place.

Two things lean on it, so check them after any change:

- `renderRebbeNiggunim` walks forward from each `[data-rebbe]` heading to find
  where the niggun goes, and `.tzedakah-block` stops that walk the way a next
  bearer does. Without the stop the melody lands under the fund.
- Every Menorah pane is now non-empty, so `_paneTrim` never hides that button.

Keter's panes are static markup rather than built by `buildCardPanes`, so
`_paneTzedakah` is called for `.keter-panes` by name.

## Scratch work

Prototypes and experiments belong in the session scratchpad, not the repo.
Several explorations have been built, shown and deliberately left out.
