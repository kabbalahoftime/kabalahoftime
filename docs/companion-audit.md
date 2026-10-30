# The daily companion — what the sweep found

The companion's 364 entries were AI-generated. In October 2026 a reader
followed day 8's instruction, found no such thing on the screen, and asked.
Everything below came out of answering that.

The companion was taken offline the same day and rewritten.
**Everything below describes the first text.** It is kept because the failures
are the reason everything after it is built the way it is.

## What the app shows now

Not either written text. `companion-days.json`: **one KoT Book for one week,
each day**, filed the way Binah files them — day 1 is Book 1's reading for
week 1, day 2 is Book 2's for week 1, day 225 is Book 1's for week 33. Seven
books × fifty-two weeks = 364.

Every entry was already in `index.html` before the companion existed, in the
weekly table. Seven templates, one to a book, and 364 fillings of them — so
there is no sentence in it that anybody composed, which is a stronger promise
than any citation. The sweep below now flags **nothing at all**: no routes
named, no claims about the app, no quotations attributed to it, because the
entries only say what the week's readings are.

Each entry links the week's post for its book — 364 posts for 364 days, from
the app's own `BOOKn_WEEK_URLS` and `b7_url`.

## The written text, which is off

`companion.json` and its manuscript `docs/a-year-inside-the-day.md` are the
rewrite of the text described below. It holds, but the manuscript's own header
marks weeks 1 and 2 as placeholder until the real opening replaces them —
creation as the creation of time, the six thousand years, the Torah before the
world. Those are the first fourteen days a reader meets, and it does not go
out with its door unbuilt. Nothing fetches it.

Re-run this sweep before any change to it ships:

    python3 tools/check_companion.py index.html companion.json

364 entries · 294,297 characters · checked against every string `index.html`
can render.

## What the rewrite changed

The text is now a manuscript — `docs/a-year-inside-the-day.md` — and
`companion.json` is built from it by `tools/companion_from_md.py`. Edit the
manuscript; the JSON is not hand-held.

It was rewritten against one rule: **every claim checkable against
`index.html`, a named traditional source, or the books.** What that fixed:

| was | is |
|---|---|
| the invented motto, in quotation marks, twice as the app's | the same words, no marks, the book's own rule — Days 36, 38, 151, 154, 166, 175, 199 all state it the same way |
| *hakatan yihyeh le'alef* / Isaiah 60:22 / "the smallest shall become a thousand" | gone. Day 38's opening is plain, Day 154 is retitled "Living the Crown", the echoes read "The smallest counts" |
| "when the soul reached ultimate completion", quoted | unquoted, and Day 288 says whose phrase it is |
| a "Today view" and a "This Week view" | the Weekly Journal's **This Week** tab, which is what it is called |
| day 8 promising four things in a tab that draws three | three — the pairing, the trait, the creature. `openWeeklyReport` builds exactly those |

Day 151's 88 Mochin minutes stayed, because they are real. See the correction
below.

The second sweep leaves six flags, all of them the checker mis-reading a
correct sentence: days 8 and 13 (it splices "the Weekly Journal's This Week
tab" into a label), 149 and 150 (the title running into the sentence), 155
("the mechanic's view", a metaphor), and 136 (see below).

The PDF link in the companion's footer is **out**. `a-year-inside-the-day.pdf`
is the first text and carries every fabrication listed here — the motto eight
times, *hakatan*, Isaiah 60:22, "ultimate completion", and both unfollowable
routes. The link returns when the PDF is set again from the manuscript.

---

*What follows is the first text, and the record of what was wrong with it.*

## It put words in the app's mouth

This is the serious category. A fabricated motto reads exactly like a real one,
and a reader has no way to tell.

| day | what it says | what is true |
|---|---|---|
| 36 | "The order is what's asked for, not the measure" — **the app's motto**, and again as "the beginner's charter" | no such string anywhere |
| 38 | the entry is **titled** "The Order, Not the Measure", and quotes "Hakatan yihiyeh l'elef" — "the small shall become a thousand" | neither phrase is in the app |
| 154 | *hakatan yihyeh le'alef* — "the smallest shall become a thousand" (Isaiah 60:22), **"in the app's own words"**, plus the motto a third time | no "hakatan", no "smallest … thousand", no "60:22" |
| 288 | the tzadikim cycle, "when the soul reached ultimate completion" | no such string |

An invented motto, an invented verse citation, and an invented number — each
stated with complete confidence, and one of them load-bearing enough to title
an entry.

### Correction — day 151 was wrongly listed here

The first version of this audit listed day 151's **"88 Mochin minutes"** as
invented. It is not. The app says it four times, in the Mochin dialogs:
*"the eighty-eight minutes wrapped around Chatzot."*

The search was for `88`. The app spells the number out. Absence was concluded
from a search that could not have found it — which is the same mistake the
companion makes, committed by the person auditing the companion.

`Ma'alot HaZman` is real too; it uses a curly apostrophe, and a straight-quote
search missed it.

**The rule this leaves:** before writing "no such string", search the spelled
form, the digit form, and both apostrophes. A checker that reports absence is
only as good as its worst variant.


## Routes a reader cannot follow

| day | what it says | what is true |
|---|---|---|
| 7 | "open the site's **Today view**" | nothing is named that |
| 8 | "Open the site's **This Week view** and you'll see four things: an animal, a rabbi, a trait, and a pairing" | it is a **tab inside the Weekly Journal modal**, which the entry never names. That tab draws three: pairing, trait, animal. The rabbi is in the data but not rendered there |
| 8 | practice: "Open the This Week view." | same |
| 13 | "Open the This Week view and read it top to bottom" | same |
| 40 | presets — "begin with three" **as a button** | the words exist, as prose: "begin with three, and the app will offer you another rung". Not a button |

Day 8's four-item description does match a real component — the **week dial's**
detail block draws animal, rabbi, times and pairing together. So the entry
describes one place and sends the reader to another.

## What checks out

- the dial "The Year as a Single Day · 52 weeks"
- "The highest thing there is, is not waiting somewhere far off" (day 150)
- the thirty-first reading is Yehoshua 10:12, the seal of a completed path
- the daily count folding at 364
- Shovavim carried across the 52 weeks

It is not uniformly wrong, which is part of the problem.

## Things the checker flags that are fine

Left here so the next reader does not re-investigate them:

- **day 136** — "when the body benefits from the body" is a real phrase about
  Tevet, attributed to the sages, not to the app. The checker's attribution
  window is wider than it should be.
- **days 149, 150, 155** — flagged names like `'Single Day The Keter'` are the
  title running into the sentence, and day 155's "the mechanic's view" is a
  metaphor, not a screen.

## What this cannot tell you

It checked the app-facing claims only. The other ~290,000 characters are
teaching: Torah, Chassidus, practice, dates. A string check finds an invented
button. It will not find an invented teaching, a misquoted Rebbe, or a wrong
date.

Given that the text invented a motto for this app, a verse citation and a
number — and titled an entry after one of them — the teaching should be
assumed to carry the same error rate, with nothing mechanical to catch it.
That part needs a reader.
