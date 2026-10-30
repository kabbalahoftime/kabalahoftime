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
nobody. Currently **v301**; the next is v302.

**2. Run `check.mjs` before anything reaches `main`.**

```sh
node check.mjs          # ~4 minutes, binds 127.0.0.1:8731
```

55 checks over 17 sections, ending in `all checks passed`. Its own header
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
python3 tools/make_book_pdf.py docs/<name>.md <name>.pdf
```

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

`book7_gathering_of_songs.pdf` and `perek_shirah_booklet.pdf` have no
manuscript here.

`a-year-inside-the-day.pdf` is the **old** companion text and is not linked
from the app: it carries fabrications the rewrite removed. It has a manuscript
now (`docs/a-year-inside-the-day.md`) but no setter — `make_book_pdf.py` opens
a page at every `##`, which would give 364 of them. Setting it again is open
work.

## The daily companion

`companion-days.json` is what the app fetches: **one KoT Book for one week,
each day**, filed the way Binah files them. Day 1 is Book 1's reading for week
1, day 2 is Book 2's for week 1, day 8 is Book 1's for week 2, day 225 is Book
1's for week 33. Seven books × fifty-two weeks = 364, and 364 posts on the
blog, one to each day, which is where each entry links.

**Nothing in it is written.** Every entry is already in `index.html` — the
weekly table `getWeeklyData` reads holds all seven books' readings for all
fifty-two weeks. There are seven templates, one to a book, and 364 fillings of
them. That, not a citation beside a sentence, is what stops an entry claiming
something the app does not hold.

```sh
# 1. ask the page what it knows (needs a server on some port)
node tools/dump_week_data.mjs http://127.0.0.1:8731/index.html docs/week-data.json
# 2. build the entries
python3 -I tools/build_companion_days.py docs/week-data.json index.html companion-days.json
# 3. the sweep, which should flag nothing at all
python3 -I tools/check_companion.py index.html companion-days.json
```

**Rebuild it whenever the weekly table changes**, or the companion starts
saying last month's readings. Both steps are checkable by diff: re-run step 1
and diff `docs/week-data.json`, re-run step 2 and diff `companion-days.json`.
Either diff coming back non-empty means something upstream moved.

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

## Scratch work

Prototypes and experiments belong in the session scratchpad, not the repo.
Several explorations have been built, shown and deliberately left out.
