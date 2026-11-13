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
nobody. Currently **v364**; the next is v365.

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

Two sentences have to stay honest with this — the welcome box and the Help
Guide's **Where to start**. Both have twice said the ladder "names all four
and goes straight to each", and twice been made false by a change here.

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

### Three cards nest the same way

Binah's face reads **where the day stands in the smallest cycle, then that
cycle, then the large one**, and the tag under it repeats the large cycle
with the absolute day. Chesed and Gevurah hold the same shape and were not
using it: both led with the absolute day and left the nesting unsaid.

```
Binah     Day 6    · Week 2 · Cycle 2     >>  Cycle 2  · Day 13 of 49
Chesed    Watch 14 · Word 3 · Cycle 1     >>  Cycle 1  · Day 62 of 72
Gevurah   Letter 16 · Face 3 · Season 1   >>  Season 1 · Day 62 of 91
```

**Chesed nests without a remainder**: the mishmarot wrap at 24, each word
of Birkat Kohanim holds exactly those 24 days, and `BIRKAT_KOHANIM_CYCLES`
gives three words to a cycle — so 24 × 3 = 72 exactly. `bkIdx` is the word
in the cycle (0–2) and `bkMishmarNum` the watch in the word (1–24).

**Gevurah's** face is 22 letters and a season is four of them, so
`inQuarter` inside `quarter` inside `season`. The **break-days keep the
plain day**: the heart and the two kidneys have neither letter nor face,
which is what they are.

Gevurah's line carried the season's name and its half — *(Fall) · Shov* —
and both came off: they are said in full in the detail, under **Season**
and under **Motion**, where Motion also gives the Hebrew and what the word
means. Three numbers and nothing else, as Binah's line is. Taking them off
also stopped the line wrapping, which put the tag at 81px — Binah's own.

The absolute day left both faces and lives only in the tag, as Binah's
does. And "Mishmar N of 24" on Chesed's face lost its number — Watch and
Mishmar are one thing under two names and it was being said twice; the
detail below still states the count in full.

### Where the day falls, in a tag

Every Sefirah card has a `*-tags` row under its face, and **only Binah used
it** — `Cycle 2 · Day 13 of 49`. Chesed, Gevurah and Chochmah all set it to
`''`, so on those cards the question a reader asks second, *where does
today stand in this count*, could only be answered by opening the detail.

Chesed and Gevurah carry it now, in Binah's own shape and with its
`tag highlight` class — but **drawn inside `*-main`, under the day's own
name, not in the `*-tags` row at the foot**. The row sits after the face
and the sub-text, which on Binah is two lines and on these two is six, so
the one line that answers *where am I* was the last thing a reader
reached. Both `*-tags` rows are left empty and the pill is built into the
face with `<div class="sefirah-tags">` round it, which is all that row
ever was — flex, a 5px gap and a 7px top margin — so it draws identically
wherever it stands.

```
Binah     Cycle 2  · Day 13 of 49
Chesed    Cycle 1  · Day 62 of 72     Microcosm · Day N of 28
Gevurah   Season 1 · Day 62 of 91     Microcosm · Day N of 28
```

A **silent day** on Chesed says so instead of counting: it has no number in
the seventy-two, which is what makes it silent. Gevurah's three break-days
**keep** their number — the heart and the two kidneys are days of the
ninety-one like any other, and it is the letters that stop on them, not the
count.

Chochmah still sets its tag row empty, and was left alone.

### Why this face, in this season

Gevurah's card named the day *"The Eagle's Face of the Ox"* and left the
reader to work out where the Ox came from. The rule was written down
twice — in the comment over `seasonFaceOf` and in the **advanced** depth
of the card's ⓘ — and in neither place a reader meets the words.

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
