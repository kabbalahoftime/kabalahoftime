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
nobody. Currently **v393**; the next is v394.

**2. Run `check.mjs` before anything reaches `main`.**

```sh
node check.mjs          # ~4 minutes, binds 127.0.0.1:8731
```

Ending in `all checks passed`. Its own header explains what each section is
for and which bug put it there — read that rather than guessing.

**The suite runs in UTC, and that hid a bug for a long time.** Section 16
exists for it: the reading cycle was walked in `7 * 864e5` jumps from a local
midnight, so the first daylight-saving fall-back after Simchat Torah moved
every remaining Shabbat onto the Friday, and a reader in New York was shown
**the next week's parasha** for a third of every year. 326 of 938 readings
wrong in New York, 384 in London, 372 in Jerusalem — and none in UTC or São
Paulo, which is why 501 readings checked against Hebcal said nothing was
wrong. `getDafYomi` floored the same kind of difference and ran a day behind
for half the year.

So: **never add a day to a Date in milliseconds and then read a calendar day
off it.** Use `setDate()`, which moves whole calendar days whatever the offset
does, and anchor at noon so no shift can cross midnight. `Math.round` of a
day-difference tolerates the hour; `Math.floor` does not. Section 16 asserts
that the answer does not depend on where the reader is standing — UTC is the
baseline the rest of the suite has matched to Hebcal, and four zones chosen
for their differing transitions must agree with it, reading for reading. It
needs no network. Playwright lives at `/opt/pw-browsers/chromium`; override with
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

**Publish without asking.** Once `check.mjs` ends in `all checks passed`,
merge and push. Do not wait to be told; the author has said so standing.
The suite passing is the gate, not a second opinion.

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

**Never invent or adjust a fact in Books 1 and 2 to make a sentence work**, and
never fill a gap in them by inference. Where two books disagree about a fact, or
a change would contradict one, say so and ask. Lands carry other names, and one
land may answer to more than one at once — and **no character anywhere carries a
real name**.

The Epilogue of Book 2 quotes a child's own handwritten book, which did name
three people, and those are **redacted to initials**: *a baby named D. His
parents were S. and A.* The quotation is otherwise word for word, and the
sentence after it still stands — *the child began in his own words and wrote
all of them* — because the child did write them; the redaction is the book's,
not hers.

This file used to say to leave that quotation exactly as it stood. The author
changed it. Should another name ever be needed there, redact it the same way
and rebuild the PDF: 14 pages.

LibreOffice is broken in this environment; read `.docx` XML directly.

## Panes and cards

Each card has a face and four panes. `_paneKind` files a detail block:
`.maalah.yom[data-wane]` → Mi'utim, `.maalah` → Ma'alot, `[data-rebbe]` →
Menorah, `[data-shelf]` or text opening with ✡ → Stars. `_paneTakeFace` moves
`.malchut-ksa-row` / `.malchut-section` off the face into a pane, filing by
`_paneKind([row])` — not by a fixed destination. `_paneTrim` hides a pane
button whose body is empty.

### Tzedakah

The day asks for four things — **meditation, prayer, study and action** —
and they are four movements, not one journey. The meditation comes down,
Keter to Malchut; the מעלות climb back, Malchut to Keter; the מיעוטים come
down again; and **the deed rises, Malchut to Keter**, because Malchut is the
world a deed happens in and nothing descends into it to act. So the ten
funds are read from the bottom up: `fundOrderUp()` reverses the reading
only — the ordinals index `TZEDAKAH` itself and `kotFundSteps` is written
in them, so reversing those would silently move what a reader had chosen.

The Menorah pane is the action. `TZEDAKAH` in `index.html` holds one fund per
Sefirah (Chesed, Yesod and Malchut hold more than one), and `_paneTzedakah`
puts it **under the master's name and above his Torah**: the menorah and the
name head the pane as they always have, and beneath them come the deed, the
learning and the niggun, in that order. **Written by hand, never generated**
— the same rule the Branches leaves are kept under.

It is placed against the heading rather than against the pane, because on
Keter the heading is not a child of the pane: label, text and meta are one
box and the block belongs inside it. The lookup for an existing block is
likewise unscoped (`body.querySelector('.tzedakah-block')`) — scoped to the
pane's own children it found nothing on Keter and built a second block on
every pass.

Done again on every render, because the filing empties and refills the pane
and its nodes land after whatever is there. A block already in place is left
alone.

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

Three things lean on the order, so check them after any change:

- The master's own book is named by CSS, not by a pass:
  `.tzedakah-block + *:not(.ps-niggun):not([data-rebbe])::before` draws a
  TORAH flag on whatever follows the funds. A `::before` rather than a span
  because that element is rewritten by render on the nine cards and by a
  fetch on Keter, and a span inside it would be wiped within the second.


- `renderRebbeNiggunim` walks forward from each `[data-rebbe]` heading to the
  next bearer, and puts the melody there. It used to stop at
  `.tzedakah-block` as well, which was right while the block stood at the
  foot of the pane; with the block between the name and the Torah that stop
  would put the niggun above both, so it is gone.
- Every Menorah pane is now non-empty, so `_paneTrim` never hides that button.

Keter's panes are static markup rather than built by `buildCardPanes`, so
`_paneTzedakah` is called for `.keter-panes` by name.

### A reader's own

Two of the four kinds can take additions, and two cannot. The difference is
in the storage, and it is not an accident:

```
maalotMask()  … & 32767   15 bits — the fifteen Songs of Ascents
yomMask()     … & 32767   15 bits
prayersMask() … & 1023    10 bits — the ten Sefirot
medMask()     … & 1023    10 bits
funds         … no mask           nothing is marked
```

The thirty and the ten faces are **closed structures**, not lists: there is
no sixteenth מעלה, and a face is computed by `_faceOf()` from what the card
already holds rather than chosen. So "your own" exists where it can:

- **Funds** — `kotFundsOwn`, merged by `fundsFor(sef)`. See above.
- **Companions** — `kotStarsOwn` as `[{sef, label, url}]`, `url` optional.
  `_paneStarsOwn` draws them at the foot of that Sefirah's **Stars** pane
  with their own `.star-mark[data-own]`, so the ordinary click handler and
  `starsSet()` mark them for free. The id is `starsOwnId()`, not
  `starIdFor()`, so it cannot collide with one of the day's and survives the
  pane being rebuilt. Added from the **path chooser's** foot, under a
  heading that says they are not among the thirty.

  **They must stay out of the ring.** The eleven stars are twenty-two halves
  and the day has exactly twenty-two companions, so `applyStarState` files a
  `[data-own]` mark into `litOwn` rather than `lit`. Without that they are
  either clamped away by `Math.min` or they fill a half belonging to the
  day's own. How many are gathered is said in the Study column's title.
- **Prayers** — `kotPrayersOwn` as `[{sef, label, url}]`, `url` optional.
  These *do* join the heart: it has never counted to ten but to
  `prayerSteps().length`, which is already five or seven for most readers,
  so an eleventh undertaken thing belongs in the count rather than beside
  it. That is the difference from the ring, whose eleven are a geometry.
  Marked in a key of their own (`kotPrayersOwn:<date>`, derived from
  `_prayerKey` so the two cannot fall on different days) rather than in
  `prayersMask`, which is ten bits and holds the ten. They live in the
  window the heart opens, not on the cards — the ten tags sit in a label
  column with no room for an eleventh. Added from the prayer chooser's foot.

The two forms toggle **by index**, not by id: an id built from a reader's
own words would have to survive being quoted into an `onclick` attribute.

### The travelling bar

**Four** doors beside the lit step, in the day's own order: `.kt-med` (the
hour's face), `.kt-pray` (its prayer), `.kt-study` (the step) and `.kt-act`
(its menorah). Each is a chip — outlined while undone, filled in its own
colour when done: blue, red, gold, gold. The step and the menorah share
gold because gold is the step's colour everywhere here; the shapes tell
them apart. The action's "done" is **the bearer being gathered**, because
the fund itself is never marked; the door goes to the pane where both
stand. The step's "done" is `_hourStepIdx(currentOffset) === -1`, the same
test the ladder skips the step on.

**All four go up together or none does.** Each used to answer for itself,
so an hour whose fund was set aside showed two chips and an hour outside a
prayer's window showed one — a ragged row reads as something having gone
missing rather than as a set. `_travelMarks` gathers what each can say in
`ups` and applies one verdict to all four at the end.

The study chip draws a **bare rim**, not the counter's moon: that one
carries `maalot-moon-rim` and `maalot-moon-fill`, and a second copy would
put duplicate ids in the document — the same trap the flame is kept out of,
where a cloned `med-clip` made the bar's flame fill from the counter.

`_travelMarks()` must be called from wherever a mark is taken. The faces
and the prayers already did it; `applyStarState` did not, because until the
third door the bar carried nothing that depended on star state — so the
chip lit only on the next render. It calls it now.

### The meditation face falls through to the heading

**`_faceOf` cannot fail.** It walks a chain — the card's `FACE_RULE`, then the
first non-position `<strong>`, then the first block, then the sub-text — and
**ends at the card's `.sefirah-cycle-name`, which is a heading and never a
face**. So when a card's face stops being findable, nothing throws and
nothing fails. The ladder quietly starts naming the section instead of the
day, and it reads plausibly enough that nobody looks.

It happened twice in one sitting and **shipped twice**. Chesed's day-Name was
the only bold thing on that card that was not a number, so `_strongFace`
found it by accident. The rewritten face bolds a number on every line:

| version | what the Ladder named |
| --- | --- |
| v374 | `יבמ` — the day's Name ✓ |
| v375 | `וְיִשְׁמְרֶךָ` — the gold blessing word |
| v376–v377 | `Shem Ayin-Bet — 72-Day Cycle` — the card's own heading |

So **a card whose face a reader meditates on must name it outright**, not
leave `_faceOf` to find it. Chesed has `#chesed-day-face` and Gevurah has
`#gevurah-day-face`, each with a one-line `FACE_RULE`, and both survive the
face being reshuffled under them. On Gevurah the span sits on the **Face**
line, and on the three break-days — which have no face — on the **Season**
line, so the standing rule that a break-day names its Chaya is kept by the
meditation too.

`check.mjs` has a **`faces`** section for this: all ten cards must name a
face, and none of it may equal that card's own heading. Landing on the
heading is the signature of the whole class and costs one render to ask.
Proved by reverting the fix and watching it fire:

```
FAIL the meditation face — Chesed: the face is the cycle heading,
     "Shem Ayin-Bet — 72-Day Cycle"
```

Every other check passed through both broken versions, because **every other
check reads the card and this one reads the ladder**.

### The meditation flames

`injectMedMarks` puts each card's flame **inside** its first
`.sefirah-main-text`. So anything that rewrites that element throws the
flame away, and only the next render puts it back.

Yesod is the one card whose face is written by a second function with a
caller of its own — `displayParasha`, which `render()` calls and which is
*also* called at DOMContentLoaded. When that second call lands after the
marks have gone in, Yesod is left the only card without a flame for the
rest of the visit. Reproduced on the live build: one `displayParasha()`
and Yesod alone loses it.

`displayParasha` asks for the marks again at both its exits now. Anything
else added that rewrites a card's main text must do the same;
`injectMedMarks` only fills a host that has no mark, so asking is cheap.

### The dial's name, and its unit

The dial is **מַעֲלוֹת הַזְּמַן** and its fifty-two half-hours are
**steps**. One of the four panes on every card is also **מעלות**, and the
thirty readings are steps in prose 48 times over. **Both overlaps are
settled rather than open, and neither is to be renamed again.**

Four candidates were tried in one sitting and each was worse than the step
it replaced:

- **stretch** — what the unit was. Not a climbing word, which was the
  objection to it.
- **מדרגות / rung** — already the word for R. Pinchas ben Yair's ten, for
  the Ramchal's ladder, for `pathAddRung` and the path chooser's own offer
  of "another rung", and for the micro-step's `Rung N:` detail row. It did
  not resolve the collision; it moved it onto a word carrying three things
  already.
- **week** — what the fifty-two actually are, and the one candidate with
  nothing in its way. Declined.
- a title without מעלות at all — declined; the dial keeps its name.

The lesson is that every climbing word in this app is spoken for, so a
fifth synonym is not available. What carries the distinction instead is
**prose, in both depths of the dial's ⓘ**: both are steps and both climb,
but these are the steps of the clock, fifty-two half-hours, and those are
the steps of the learning, of which there are thirty. Said outright rather
than left to be noticed.

A **"Dial" line at the head of Today's Ladder** was built three times and
rejected three times. The four lines under it are already in the journey's
order; what the block does not do is name where to begin. Leave it so.

### Today's Ladder is one line

The block asks **one thing**. It shows the next of the hour's four still
undone, in the order the day's work goes — **the face, the prayer, the
step, the deed** — all of them the Sefirah's whose hour it is. Mark one and
the next comes up. Four lines at once was a menu, and a menu is not an
instruction.

`_ladderDone()` answers all four with **the same tests the travelling bar's
chips fill from**, so a line and its chip can never disagree. The deed's
"done" is the bearer gathered, because a fund is never marked.

**Catching up comes last.** The hour's own step is third, where the order
puts it (`_hourStepIdx`); anything outstanding from earlier is offered
again *after* the deed. That is the Baal Shem Tov's rule for the Psalms of
Elul, already written into `_pathNow`: today's portion first, the backlog
after, never before. An hour holding none of the thirty skips the step
rather than borrowing somebody else's to stand in third place.

**`_ladderNext` and `_ladderShow` are two questions, not one.** The first
is what is being *asked for* — null when nothing is, which is what lights
nothing and hides the bar. The second is what to *draw*, and when nothing
is asked it keeps the last line up in its done state so the block is never
empty. Collapsed into one, the line reading *"Done · the month complete"*
was lit as though it were still being asked for.

**No verb.** The lines carried one for a while — `Dwell on`, `Say`, `Read`,
`Give`, in a `.t-do` span after the chip. The pill already names the kind,
so the verb said it twice, and the bar inherited it because
`_travelTextFrom` strips the chip and the arrow but not that span. Gone:
the CSS, `_ladderVerb`, `_ladderVerbFor` and the call.

**The wrapper hides, never the row.** Rows go away by `.ladder-off`
(`display:none !important`), not by their own `style.display` — each
builder writes that to say whether the row holds anything at all, and
`_travelMarks` reads exactly that to decide whether to draw the row's chip.
Those chips are the only way to reach the other three now.

`applyLadderNext` also runs on the **30-second beat**, because which of the
four is asked for turns with the hour.

**Three** places have to stay honest with this, not two: the welcome box, the
Help Guide's **Where to start**, and the ladder's own **ⓘ** (`CYCLE_INFO.ladder`).
The first two have twice said the ladder "names all four and goes straight to
each", and twice been made false by a change here.

The ⓘ was the one nobody listed, so nobody checked it, and it rotted longest.
Its beginner and main depths still described **four lines** with a gold rule
down the lit one, and said that line carried **a verb** — a design removed
twice over, the fourth row when the block became one line, and the verbs in
this file's own "No verb" note above. It is rewritten around the four
movements and their directions. **Check all three after any change here.**

**Three said where the block sits, and none does now.** The welcome box and
the Help Guide both placed it "under the date", and the comment over
`#today-block` said the date was "in the bar directly above" — all three went
false the moment the companion moved up between the two. The locators are
gone rather than corrected: a sentence that says what the block *does* cannot
be falsified by moving it, and these have now rotted three times between
them. Do not put a position back into any of them.

### The companion comes first

`#companion` sits between the date bar and `#today-block`, above everything
else on the page. It is for the reader who has just arrived and does not know
what a Sefirah is, and the ladder asks that reader to do one of four things
before anything has explained why. It is shut by default and about 117px
tall, so a reader who already knows scrolls past one line and a two-line
peek. It stood below the ladder and below the welcome box until then.

### One gap down the column

Every card in the stack above the Sefirot is **16px** from the one before it:
the week artwork, the date bar, the companion, the Ladder, the welcome box
and the crown. They had drifted to 16, 24, 14, 12 and 24, which on a phone
read as the companion sitting closer to the Ladder than to anything else.

```
.week-card        margin: 16px auto
.date-bar         margin-bottom: 16px
.companion        margin: 16px 0 0
#today-block      margin: 16px 0 0
#kot-welcome      margin: 16px 0 0   (inline)
.keter-title-row  margin: 16px 0 0
```

**These are collapsing margins, so one stray value wins the whole gap.** The
date bar's old 24 beat the companion's 14 and made the first gap wider than
the second — the drift was invisible until two of the five sat next to each
other. Change one and change them all.

`.keter-card` keeps `margin-top: 0` on purpose: its own comment says the
heading and the dial are **one card, not two stacked**, so the crown's
heading carries the top of one outline and the card below carries the bottom.

### The acrostic psalms are not one verse a letter

Chochmah's 22-day cycles name a verse for the letter of the day, and two of
them were mapped **arithmetically** — `d => 34:${d+1}` and `25:${d}`. Both
psalms are missing the **ו** verse, so from day 6 onward every day sat
against the wrong letter, and the extra **פ** verse each closes with
(25:22, 34:23) landed on ת. Seventeen of twenty-two wrong in each.

Psalm 25 also has no **ק**: 25:18 and 25:19 both open with ר.

Both are hand-mapped now and checked verse by verse against `ACROSTIC_HE`,
which this file already holds — so the check costs no network call. A
letter the psalm does not have is `null`, and the card draws nothing:
`if (_raw)` guards it, the same way cycle 17 carries its ten empty days.

**A first-letter check gives false positives**, so do not "fix" the others
on one. The first verse of Psalms 25 and 37 takes its letter from the
second word (אליך, אל), Psalm 37's ת is the second letter of וּתְשׁוּעַת,
and Psalms 9–10 are a broken acrostic in the Masoretic text whose list here
is deliberate. Cycles 1 and 4 were examined and left alone.

### By the hour, or in order

Two modes, in `kotLadderMode`, chosen by two pills at the foot of the
ladder, **drawn with the app's own `.year-toggle-pill` / `.year-pill-btn`**
rather than anything of their own. Written fresh they were given 17px of
padding to reach the 44px tap target, which made them 46px slabs — exactly
what the note three hundred lines above the toggle's CSS warns against,
where growing a control "turned the Diaspora/Israel pill into a slab". The
control keeps its drawn height of 24px and the `::after` overlay does the
reaching. `white-space: nowrap` is the one rule of their own: "by the hour"
is three words where "Diaspora" is one, and at the largest text size it
wrapped and doubled the pill's height. **By the hour** (the default) asks for this hour's own four. **In
order** releases the clock and walks the four movements end to end, in
their own directions:

```
meditations   Keter → Malchut    1…10          medStepHas / medHas
the prayer    its own hour       the hour's    prayersMask
מעלות          Malchut → Keter    idx 0…14      pathSteps / _stepMarked
מיעוטים        Keter → Malchut    idx 15…29     (one pass: pathSteps is sorted)
מעשה          Malchut → Keter    fundOrderUp   bearer gathered, never the fund
```

**The prayer is never released from the clock, in either mode.** A prayer
has its hour in a way a face and a reading do not. But in order it sits
**after the meditations**, not ahead of them: the descent from Keter to
Malchut is one movement, and a prayer in the middle would break it in
half. So the meditations are never interrupted, and the prayer is the next
thing asked for once they are done — before the climb, and still waiting
while it is unsaid.

`_ladderFreePick()` returns the first undone thing in that order, and
`_ladderFaceSef()` / `_ladderActSef()` say which Sefirah each row is about
— the hour's by the hour, the movement's in order. **They must stay
separate:** the meditations come down while the deeds climb, so in order
the face row and the action row are rarely the same Sefirah and cannot be
made to share one.

Four things read those two: `applyTodayFace`, `applyTodayAction`, their
`todayFaceGo` / `todayActionGo` doors, and `_travelMarks`, so the bar's
chips answer for the same Sefirot the rows do. The study row passes
`{off:0, idx}` to `_todayLine`, which writes `dataset.idx`, so `todayGo`
follows without being told.

The study chip's "done" differs by mode: this hour's steps all marked
(`_hourStepIdx`) by the hour, none of the thirty left at all in order.

### Two cards nest, and two are read one count to a line

Binah's face reads **where the day stands in the smallest cycle, then that
cycle, then the large one**, and the tag under it repeats the large cycle
with the absolute day. Netzach holds the same shape and was not using it: it
led with the absolute day and left the nesting unsaid.

```
Binah     Day 6    · Week 2  · Cycle 2    >>  Cycle 2  · Day 13 of 49
Netzach   Day 7    · Level 3 · Cycle 2    >>  Cycle 2  · Day 27 of 41
```

**Chesed and Gevurah were made to nest and both have come back out of it.**
Each now reads **one count to a line, a number and its own name**, which is
the section below and the one after it. Chesed had `Mishmar 14 · Word 3 ·
Cycle 1` over a tag saying `Cycle 1 · Name 62 of 72`; Gevurah had `Letter 16
· Face 3 · Season 1` over `Eagle's Face of the Ox שׁוֹר · ט`.

**Neither carries a tag any more**, because on both the face now says the
count the tag was repeating.

**Netzach was the fourth and nobody had noticed.** Three rows stand under
its face — **Day**, **Level/World**, **Cycle** — and the face named only two
of them, so the middle count had no number anywhere on the card.

The first attempt printed `Day 23 · Level 3 · Cycle 2` — the absolute day
beside the level, which says the large count twice and the small one never.
The face takes the day **inside the level**, as Binah takes the day inside
the week, and the absolute day goes to the tag where the other three keep
theirs. Ten days to a level, four levels to the forty: the level is
`Math.ceil(day / 10)` and the day in it `((day - 1) % 10) + 1`.

**Day 41 keeps the plain day**, as Gevurah's break-days do. It is Yechidah
in Adam Kadmon, which stands *above* all four rather than being a fifth, so
it has no level to name — and `Math.ceil(41 / 10)` would otherwise index a
fifth that is not there. The guard is in both places for that reason.

**The trap that cost a round here.** Three statements below the face stood
`cards[5].querySelector('.sefirah-tags').innerHTML = ''`, meant for the foot
row. Once the face contains a `.sefirah-tags` of its own, `querySelector`
returns **that** one — so it emptied the tag just written and left
`<div class="sefirah-tags"></div>` behind. Both branches now say
`.sefirah-content-col > .sefirah-tags`, which the child combinator keeps off
anything nested in the face. **Any card that grows a tag inside `*-main`
needs its foot-row selector checked the same way.**

Checked across 44 consecutive days and a cycle roll: the level agrees with
the Level/World row on every one, the tag counts to 41, the foot row stays
empty, and the forty-first prints no level.

#### Chesed holds two meditations, not one nest

The numbers do divide evenly — the mishmarot wrap at 24, each word of Birkat
Kohanim holds exactly those 24 days, and `BIRKAT_KOHANIM_CYCLES` gives three
words to a cycle, so 24 × 3 = 72 exactly. `bkIdx` is the word in the cycle
(0–2) and `bkMishmarNum` the mishmar in the word (1–24). But dividing evenly
is not the same as nesting, and the author named it before I saw it:

> It feels like two separate meditations. Each of the 72 names within one of
> the 5 books. And each of 24 Watches within each of the 15 words of Birkat
> Kohanim.

5 × 72 and 15 × 24 are **two factorings of the same 360 days**, not one count
with four levels. Four numbers on one line read as the latter, which is what
made the line hard. The face is **five lines, each a number and its own
name**:

```
Name 70 (יבמ)
Cycle 1 (בְּרֵאשִׁית)
Mishmar 22 (גָּמוּל)
Blessing Word 3 (וְיִשְׁמְרֶךָ)
1 Av (משה רבינו)
```

**Every line is built the same way** — a number, then in parentheses the
Hebrew thing that number points at. The parenthesis is the same gesture five
times, which is what makes the block read as one list rather than five facts.

**The Cycle's name is its lobe.** `_lobe` is `CHESED_LOBES[cycle - 1]`, the
app's own mapping, already drawn in the detail's *Lobe of the Lung* row. The
Cycle was the one count on this face with a number and no name.

**The fifth line is the soul of the cycle**, and it carries a number of its
own — the day of Av — rather than repeating the cycle's. `NINE_DAYS_SOULS`
was already in `index.html` with the whole idea in its comment: the Nine Days
are the year's **5-cycle/4-gap shape in miniature**, five odd days marked and
four even days between them, carrying Rebbe Nachman's five holy souls. Read
the other way round, **cycle N answers to the (2N-1)th of Av**:

```
Cycle 1   1 Av   משה רבינו        Cycle 4   7 Av   הבעל שם טוב
Cycle 2   3 Av   רשב״י            Cycle 5   9 Av   רבי נחמן
Cycle 3   5 Av   האר״י
```

`_cycleSoul` **derives** this from that one table rather than listing the
five again, so the face and the Nine Days cannot name different souls for one
cycle. The Hebrew lives in `NINE_DAYS_SOULS` beside the English for the same
reason, unvocalized because that is how the app writes these five everywhere
else. Note `_cycleSoul` must be declared **with `ayinBetInfo`**, not beside
the table — the table is three hundred lines above the `const` that holds the
cycle number, and reading it there is a temporal-dead-zone throw.

**Putting the soul in the Cycle's own parenthesis was built and measured
instead, and lost on the measurement.** `Cycle 4 (בְּמִדְבַּר · הבעל שם טוב)`
wraps at 390px, so four cycles drew at 108px and the fourth at 136 — one
ragged card in five. A line of its own is **136px for all five and wraps on
none**.

**Two intermediate shapes came before it, and the history is the argument:**

```
Mishmar 21 · Word 3 · Cycle 1        the nest forced on it, over a tag
ראה                                   saying Cycle 1 · Name 69 of 72

Name 69 (ראה) · Cycle 1              two lines — but said Mishmar twice,
Mishmar 21 · Blessing Word 3          once here and again in the row under
Mishmar: יָכִין — Yachin              it
Birkat Kohanim: <three words>
```

Giving every count its name killed both sub-rows. Then the four would not
sit two to a line: at 390px the blessing word wrapped to a line by itself,
`(וְיִשְׁמְרֶךָ)` orphaned in brackets. **One count to a line, 108px, and
nothing wraps.** The author chose it from a render of both.

**Neither the transliteration nor the blessing's other two words are on the
face.** No line carries a transliteration, and the detail states
`Mishmar N of 24: יָכִין — Yachin` in full with its link, and the cycle's
three words with today's in gold under *one word each 24 days*.

**The tag is at the foot, not on the face.** It stood inside the face for a
while, under the day's name; with the face one count to a line its
`Cycle 1 · Name 62 of 72` read as the first line over again, so it came off
altogether — and then back, in `#chesed-tags`, where Binah keeps its own.
See *Where the day falls, in a tag*.

Each Hebrew word goes inside its **own `<bdi>`**: after a Latin label and an
opening bracket it is no longer a run of its own and has to be told which way
it reads.

**The seventy-two are Names, not days.** The tag and the detail both said
*Day N of 72*, so the day's own Name sat bare with its number named nowhere.
Both say **Name N** now. `nameNum` and `dayInCycle` are the same field,
returned twice under two names, so there is only ever one number to label.

**Two readers in `check.mjs` read this face, and both break when it moves.**
`flat()` is `innerText`, so the `<br>`s arrive as single spaces and the four
lines read as one run.

- the **calendar probe**, `/Name (\d+) \((\S+)\) Cycle \d+/`, assembled
  name-first to match the calendar cell. Matched to the current wording
  rather than widened to accept the old — this probe caught the Day→Name
  rename, and a probe that accepts every past spelling catches no future one.
  It fails loudly.
- the **leap sweep's `name:`**, for check (d) *the 72 Names hold across each
  microcosm*. This one **failed silently**, and did for a long time: its
  pattern was still `/Day (\d+) · Cycle (\d+) of 5/`, wording the face had
  dropped at some earlier rewrite, and its only reader skips a row whose
  name is null — so the check printed **ok while comparing nothing at all**.

The quiet failure mode is the lesson, not the pattern. Two things now stand
against it. The Name and the Cycle are matched **separately** rather than as
one run, so a line inserted between them cannot unmatch both. And the check
**fails outright when a whole 1401-day sweep yields no name**:

```
FAIL the Chesed face reader has gone stale — no day in 1401 yielded a
     Name, so the check below compares nothing
```

That guard was proved by breaking the pattern on purpose and running the
suite: it fires, and the `ok` line no longer prints. The `mishmar:` field
beside it reads the *microcosm* branch, which still says `Mishmar N of 24:`,
and was never affected.

Swept 401 days: 369 ordinary days all five lines well-formed, all **15**
cycle-and-word pairs seen (5 × 3), all five souls on their own cycles, no tag
anywhere inside the face, and the height a constant **136px with nothing
wrapping** on any of them.

**Gevurah's** face is 22 letters and a season is four of them, so
`inQuarter` inside `quarter` inside `season`. The **break-days keep the
plain day**: the heart and the two kidneys have neither letter nor face,
which is what they are.

Gevurah's line carried the season's name and its half — *(Fall) · Shov* —
and both came off: they are said in full in the detail, under **Season**
and under **Motion**, where Motion also gives the Hebrew and what the word
means. Three numbers and nothing else, as Binah's line is. Taking them off
also stopped the line wrapping, which put the tag at 81px — Binah's own.

The absolute day left Gevurah's face and lives only in its tag, as Binah's
does. And "Mishmar N of 24" on Chesed's face lost its *of 24* — Mishmar is
one thing and the count was being said twice; the detail below still states
it in full.

**One word for it, and the word is Mishmar.** The face line said *Watch*
and everything else on the card said *Mishmar* — the microcosm branch, the
row under the face, the detail, and the link to I Divrei HaYamim 24, which
is where the twenty-four come from. The face was the only English in the
reckoning. Do not reintroduce *Watch*.

### The faces must be measured at every text size

A sweep at the default size says nothing about the other two. Six faces were
rebuilt one count to a line, swept over hundreds of days, and shipped — and
the author's next screenshot showed Yesod at the **large** setting with
`Moshe)` alone on a line, the closing bracket orphaned from the one it
opened. The overflow section of `check.mjs` has walked all three sizes for
years, for exactly this reason; the sweeps written by hand did not.

Measured properly, at 390px:

```
normal   every line on every card fits on one row
large    Yesod's Parasha line and Chochmah's Cycle line wrapped
larger   those two, plus all three of Binah's and one of Chesed's
```

**A wrapped line is not the fault. An orphaned bracket is.** Two lines were
shortened until they fit at `large`, and both lost the part the detail
already states:

- **Yesod** carried four things — label, letter in English, letter in Hebrew,
  tzaddik. The English name went; the detail says `Cycle 2: Vav`. What is
  left reads as Binah and Gevurah read, the name then its Hebrew, and the
  name here is the tzaddik: `Parasha 1 (Moshe — ש)`.
- **Chochmah's set line** names *two* letters, so English and Hebrew together
  made it twice the day line's length. It is Hebrew alone — `Cycle 4 (ז & ח)`
  — while the day's own letter keeps both, because that is the one being
  meditated on. The set's English is one tap below in *What the letters stand
  for*, which lists exactly the letters the face is showing.

At `larger`, Binah's three lines and Chesed's longest still wrap and are left
to. They are vocalized Hebrew words that cannot be shortened without losing
them, and the break falls after the em dash — `Day 7 (Malchut —` /
`מַלְכוּת)` — so the Hebrew and its bracket stay together and the line reads
as a continuation.

**Measuring this needs care.** `Range.getClientRects()` returns a rect per
inline *box*, not per line, so a probe built on it reported "10 rows" for a
three-word line and would have sent the fix in the wrong direction. Count
lines by dividing the rendered height by a one-line reference in the same
styles.

### Where the day falls, in a tag

Every Sefirah card has a `*-tags` row under its face, and **only Binah used
it** — `Cycle 2 · Day 13 of 49`. Chesed, Gevurah and Chochmah all set it to
`''`, so on those cards the question a reader asks second, *where does
today stand in this count*, could only be answered by opening the detail.

**Chesed and Gevurah carry it at the foot**, in `#chesed-tags` and
`#gevurah-tags`, **parallel to Binah's** — the author's own ask: *"The golden
tag in the bottom of Binah can be paralleled in the bottom of Chesed and the
bottom of Gevurah."*

```
Binah     Cycle 2  · Day 13 of 49
Chesed    Cycle 1  · Name 70 of 72     A silent day   /  Microcosm · Day N of 28
Gevurah   Season 1 · Day 70 of 91                        Microcosm · Day N of 28
Netzach   Cycle 2  · Day 27 of 41      (inside *-main)
```

**The tag has stood in three places, and this is the third.** At the foot
first; then drawn **inside `*-main`**, under the day's own name, because at
the foot it came after everything the face had to say; then **nowhere at
all**, when both faces were rebuilt one count to a line and the tag's two
numbers read as the first line over again. Back at the foot, where it is not
read against the face's own lines and the parallel with Binah is the point.

So **do not move it inside the face again**. The objection that sent it
there — that the foot is far from the face — is real, and it is outweighed by
the repetition it causes once the face names its own counts.

Netzach is the one that still draws its tag **inside `*-main`**, with
`<div class="sefirah-tags">` round it: that is all the row ever was — flex, a
5px gap and a 7px top margin — so it draws identically wherever it stands.

A **silent day** on Chesed says so instead of counting, because it has no
number in the seventy-two. Gevurah's three break-days **keep** their number —
the heart and the two kidneys are days of the ninety-one like any other, and
it is the letters that stop on them, not the count. Chochmah still sets its
tag row empty, and was left alone.

Checked over 461 days: all three cards carry a foot tag on **every** day, and
neither Chesed nor Gevurah draws one inside its face.

### The label column must not outrun the face

Gevurah was **the one card in the ten whose label column was taller than its
content** — 250px against 209 — so the margin punched a hole in the face
beside it. Two things did it, and both are fixed:

- **the songs' margins.** `#gevurah-kot-song` and `#gevurah-kot-song-8` each
  carried `margin-top:26px`, and most days show both, so the pair was 52px of
  a 250px column. They are **20px**, and **20 is the floor, not a
  preference** — see below.
- **the tag's return.** Putting it back at the foot gave the content column
  19px it did not have.

Together: **−40px of overhang became −9px** on an ordinary day.

**It does not reach zero, and two different things stop it.**

The first is the content: 18 days in 461 overhang badly whatever the margins
do — Gevurah's break-days, whose face is `Day 46 / Season 1 (Eagle — נֶשֶׁר)
/ Eicha 5` with no letter, no face and no verse text, and Chesed's four
silent days, which are one line. There the card has less to say than its own
margin.

The second is the **44px tap rule, and it cost a failed suite run.** The
margins went to 12px first, on the reasoning that `.study-pray-btn` reaches
14px below its text and the song links carry no `::after` overlay, so the
boxes would still stand 8px clear. **That reasoning was wrong.** `targets`
does not ask whether boxes overlap; it asks whether a control under 44px can
hit-test **21px above and below its own centre** and still land on itself. A
one-line song — `Perek Shirah`, 47×13 — therefore needs about 28px of clear
air above it, not 8. The 26 was load-bearing:

```
FAIL A "Perek Shirah" on Gevurah is 47x13 and reaches under 44px down
```

Walked 12, 16, 18, 20, 22, 24, 26 against the suite's own `reaches()` over a
fortnight of songs: **18 and below fail, 20 and above pass.** So Gevurah's
label column has four tappable things in it — a prayer arrow, the study
button and two song links — and each needs roughly 44px of its own. That sets
the column's height, and the last 9px is not available.

**A reach test needs the element scrolled into view.** `reaches()` returns
true for anything off-screen, as "cannot judge", so a probe that forgets
`scrollIntoView` passes everything silently — which is how 65 of 79 controls
once went untested, and how my first attempt to find the floor reported that
*every* candidate failed, 26 included.

### Gevurah reads one count to a line, with the English

```
Letter 1 (Alef — א)
Face 4 (Lion — אַרְיֵה)
Season 1 (Eagle — נֶשֶׁר)
```

Chesed's shape, and the author asked for it directly. It was two lines —
three numbers, then the day's name, `Eagle's Face of the Lion אַרְיֵה · א` —
which **wrapped at 390px and left `· א` stranded on a line of its own**.

**With the English, which is where this differs from Chesed.** There the
parenthesis holds Hebrew alone and the transliteration lives in the detail.
Here the creatures and the letters have English names the card uses in prose,
and the author asked for both: *"I think this one should have the English,
too."*

**The letter's English comes from `SINGLE_LETTERS_22` by glyph, never by
index.** Eicha 2, 3 and 4 set פ before ע, so the day's position in the
twenty-two is not its position in the alef-bet. Checked: 461 days, all 22
letters, **none mismatched**.

**Quarter 1 is the season's own face**, so those two lines name one creature
twice — on 88 days a year. True, but two identical lines read as a fault, so
the day that is its own says `Face 1 (Eagle — נֶשֶׁר, its own)`. Not *", the
season's own"*: that wrapped the line in two, which costs more than the
repeat it explains. `f.own` is the flag `seasonFaceOf` already sets.

**A break-day keeps the plain day and the Chaya**: `Day 69` over
`Season 4 (Lion — אַרְיֵה)`. It has neither letter nor face — that is what a
break-day is — and which joint it is stays in the detail under *This day*.

**No tag on the face, and no body rows.** The tag is at the foot in
`#gevurah-tags`, parallel to Binah's — on the face its `Season 1` read
against the Season line. `_gevBody` printed Yehuda ben Teima's posture, the
angel and the element — all three are detail rows already, at greater length,
and `Chayot HaKodesh` carries Winter's gloss about the Man who bears the
fish. `_gevBody`, `_gevWho` and `_gevTagRow` are all **deleted rather than
left unused**.

#### What the possessive used to carry

Gevurah's card named the day *"The Eagle's Face of the Ox"* and left the
reader to work out where the Ox came from. The rule was written down
twice — in the comment over `seasonFaceOf` and in the **advanced** depth
of the card's ⓘ — and in neither place a reader meets the words.

**That construction is gone, and the two lines say it better:** a reader who
sees `Face 3 (Ox — שׁוֹר)` over `Season 1 (Eagle — נֶשֶׁר)` has been told
outright what the possessive made them infer. The notes below are kept
because the reasoning still governs which face a day wears; the wording they
describe is no longer on the card.

The four turn in the seasons' own order, **Eagle → Man → Ox → Lion**,
beginning at the season's own face. So the Eagle's season runs Eagle, Man,
Ox, Lion and its third quarter is the Ox; the Lion's runs Lion, Eagle,
Man, Ox. Sixteen quarters in a year, each position carrying each face once
— a Latin square, which the advanced ⓘ still explains in full.

A line was added under the face that printed the season's own four with
today's marked — *the season turns Eagle → Man → Ox → Lion* — and it was
**taken out again the next day**. Do not add it back.

What answers the question now is the face line itself: *Letter 16 · Face 3
· Season 1*. A reader who sees the day is face 3 of the Eagle's season has
what the turn would have told them, and the ⓘ still explains the rule in
full at the advanced depth. The turn line said a third time what two lines
above it were already saying.

**A break-day's face is the Chaya itself, bare: *Eagle*.** The day has no
face, and what is left when the face goes is the creature whose season it
still is.

Two wrong answers came first. It said **The Left Kidney**, which named no
creature at all — so the one day a reader happened to look at was the one
day the card never mentioned the Chaya. Then **Eagle's Left Kidney**, which
named it but put a kidney in the possessive that belongs to a face. A kidney
is not a face. Both were mine; the author rejected the second in one line.

`_gevFace` returned for the heart and the kidneys **above** its call to
`seasonFaceOf`, so those three days never reached the possessive that the
other eighty-eight wear. And `seasonFaceOf` returns null without a quarter,
which a break-day has none of — so the creature had to be read straight from
the season, the same way that function derives its own `of`. Both now come
from `CHAYOT_FACES[(season - 1) % 4]`, so they cannot name different
creatures for one day.

The letter and the face **do** stop on a joint; that is what a joint is. The
season does not. The day is still inside the Eagle's ninety-one, and the tag
beside it says *Season 1*, so dropping the Eagle was an over-correction.
Read across the seam: *Eagle's Face of the Ox*, **Eagle**, *Eagle's Face of
the Lion*.

**Which joint it is belongs in the detail**, and was there all along —
`_placeLine`'s own note states the rule it was already keeping: *the face
carries only what the day is, and where it falls is read inside*. Two rows
say it, and the pane machinery files them out of `#gevurah-detail`, so look
for them in the panes rather than there:

```
Within the 91:  Left Kidney — 22 + 1 + 22 + 1 + 22 + 1 + 22 …
This day:       Left Kidney — between faces 3 and 4
                The Heart of Fall — near Rachel Imeinu's yahrzeit
```

The leap microcosm shares `_gevFace`, so its twelve break-days were corrected
by the same change. Swept a full year: all twelve of the season break-days
and all twelve of the microcosm's carry their creature, and no ordinary day
changed.

### Hod's 728 are the letters, and nothing is left over

Each half-day carries one **combination of the twenty-seven letters** — the
twenty-two and the five finals, `ך ם ן ף ץ` — taken straight through: the
first letter with each of the twenty-seven, then the second, to the end.

`27 × 27 = 729` ordered pairs against 728 half-days, so exactly one is left
out, and it is **alef with itself**. The One is not a combination. What that
leaves is the number three times over:

```
729 − 1 = 728 = 26 × 28                      יהוה × כֹּחַ
pairs of two different letters  27 × 26 = 702 = שַׁבָּת
letters standing with themselves 27 − 1 =  26 = שֵׁם הֲוָיָה
```

The card's advanced ⓘ already asserted *728 is שבת joined to the Name* as
gematria. It is now the structure: 702 gates of two letters and 26 letters
standing alone are **the two kinds of half-day the cycle is made of**.

**What it replaced, and why.** A matrix of 72 Divine Names × 10 Sefirot = 720
half-days, with **8 "cornerstone" half-days added on** to reach 728. The ten
was the ten Sefirot, which have no particular claim on Hod; the eight were
four of **Chesed's own silent days**, borrowed; and those four days of the
year stood outside the count altogether, with a branch of their own on the
card saying so. All of that is gone — `HOD_SEFIROT` deleted rather than left
unused, the break branch deleted, and the suite's `Half-Days N & M` fallback
deleted with them rather than left to rot unmatched.

`LETTERS_27` is `SINGLE_LETTERS_22.concat(FINAL_LETTERS_MIC)` — **derived, not
listed again**, so the letters and their spellings cannot drift from the
cycles that already use them. The author's own order, and the order the leap
microcosm already walks.

**`hodGate` folds at 728**, as `get13DayInfo` folds at 364, and returns the
folded number in `h` so the line printed and the pair drawn can never be two
different half-days. Without the fold the **year-seam** check walked past day
364, `LETTERS_27` handed back `undefined`, and the whole suite died on
`reading 'hebrew'`. The old matrix never showed this, because its index was a
modulo of five and could not leave its table — so a seam that had always been
walked became reachable the moment the lookup stopped folding.

**The meditation is the afternoon pair.** Hod's hour is 3:26–6:52, after
midday, so `#hod-day-face` sits on the second of the two. The id is on the
pair alone, not the line: `_blockFace` would hand the ladder the label and
the number with it.

**Thirteen days a year turn letter at midday** — a block is 27 half-days and
a day is 2, so a boundary falls mid-day whenever it falls on an odd half-day.
The foot tag says so (`Letter 5 → 6 of 27`) rather than naming one and hiding
the other. Checked: 13 in a Kabbalah of Time year, all 27 blocks seen.

**The tag's Hebrew carries `letter-spacing:normal`.** `.tag` is tracked, as
the page's Latin small-caps labels are, and no tag had held Hebrew before
this one. Tracked Hebrew is exactly what the `tracking` check forbids, and it
failed the suite on the mem sofit the first time round.

Swept a year at all three text sizes: 0 malformed, no overflow, all 728 pairs
distinct, alef-alef absent, first `אב`, 27th `בא`, last `ץץ`.

**Three depths of the ⓘ say this**, not one — `beginner`, `main` and
`advanced` all describe the combinations now. Change the construction and
change all three.


### No byline, anywhere

The app names **no person**. The two JSON-LD `author` fields are gone from
`index.html` and `kot-structure.html`; the footer credits the work rather
than the people — *Based on the book / Kabbalah of Time / kabbalahoftime.com*
— and the two in-text citations read *From "The Kabbalah of Time"*. None of
the twelve PDFs carries a name on any opening page; they never did.

**Do not put one back.** `check.mjs` used to require a Person as author and
now fails if it finds one: the assertion was inverted rather than dropped,
because a byline restored by a later edit, unnoticed, is exactly how the
name would return to the search engines.

The book keeps its credit and its own site, `kabbalahoftime.com`, still
leads to the authors. Removing the names here removed a co-author's credit
too, which was deliberate: leaving one name would have read as sole
authorship.

### The ma'amar in Hebrew is linked, not carried

Malchut's **Year-Round Connection** names the se'if and its month and links
Chabad's English. The Hebrew was nowhere on the card, and there was nothing
to put there without writing it: the twelve se'ifim are **numbered, not
titled**, and `VATAH_TITLES` holds the author's own English summaries, which
render in the monthly calendar and not in the pane.

So the pane links Sichos In English's bilingual edition — the whole ma'amar,
Hebrew facing a translation, with the summaries and the notes — at
`sie.org/media/pdf/1130/fkNX11307530.pdf`. **One link, not twelve:** the
document is the whole ma'amar and every se'if is in it.

**Linked rather than copied in**, which is the line this file already keeps:
Eicha reads the public-domain 1917 JPS here because the Steinsaltz and Chabad
translations could not be published. Extracting the twelve דיבור המתחיל from
that PDF was offered and declined.

The link is `http`, as supplied; `sie.org` is blocked from this session's
proxy so neither it nor an `https` variant could be checked from here.

### The cards are drawn as a ladder

The seven in `#sefirot-grid` carry a 4px rail on each side and a rung between
each pair. They already stood in a column with the Sefirot in their own order,
Keter at the top and Malchut at the foot, so the page was a ladder before it
was drawn as one — the meditation comes down it and the מעלות climb back up.

The rung is `::after` on `.sefirah-card:not(:last-child)`, `left:-4px;
right:-4px; bottom:-7px; height:7px`, which fills the 6px gap plus the 1px
bottom border exactly — so the rails run **unbroken** through it. Thinner and
centred in the gap, the rails would break at every junction and it would stop
reading as a ladder. **The last card has no rung**, because a ladder does not
end in one.

**Chochmah and Binah are not rungs of it.** They sit above the ◆ divider in
`#upper-sefirot-grid`, wear their accent on a top border, and have never
carried the left rail. `.upper-sefirah` switched off `border-left` alone, so
the new right rail reached them and they stood lopsided; both are off there
now. Anything added to `.sefirah-card`'s box reaches those two as well.

**One colour, named outright.** All three rules say `var(--gold)` rather than
`var(--sefirah-color, var(--gold))`, which is what the left rail asked for
before. That matters because of the next item.

### Two faults left standing, on purpose

Both are old, both were found while drawing the ladder, and the author has
said to leave them. **Do not "tidy" either without asking** — each is a
visible change to every card, not a cleanup.

- `index.html:1629` and the six rules after it declare **`–sefirah-color`
  with an EN DASH** (U+2013). A custom property must begin with two hyphens,
  so all seven have never set anything, and every `var(--sefirah-color,
  var(--gold))` in the file — the rails, the Sefirah name, two more — has
  always fallen back to gold. That fallback is what makes the ladder one
  colour. Repairing the dash would give each card its own rail and name
  colour, which is a change to look at first; it is also why the ladder's
  rules name gold directly, so a later repair cannot split the ladder into
  seven colours without anyone touching them.
- `index.html:245` is `- { margin: 0; padding: 0; box-sizing: border-box; }`
  — a hyphen where `*` was meant, so the global reset is dead. Harmless as it
  stands; applying it would reflow the whole page.

## Scratch work

Prototypes and experiments belong in the session scratchpad, not the repo.
Several explorations have been built, shown and deliberately left out.
