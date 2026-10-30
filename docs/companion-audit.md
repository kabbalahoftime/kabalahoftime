# The daily companion — what the sweep found

The companion's 364 entries were AI-generated. In October 2026 a reader
followed day 8's instruction, found no such thing on the screen, and asked.
Everything below came out of answering that.

The companion was taken offline the same day. Its entries, code and styles are
untouched; the fetch in `index.html` is commented out, with the reasons at the
switch. Restoring four lines brings it back.

Re-run this sweep before it returns:

    python3 tools/check_companion.py index.html companion.json

364 entries · 294,297 characters · checked against every string `index.html`
can render.

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
