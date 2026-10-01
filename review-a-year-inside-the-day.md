# Review — *A Year Inside the Day*

155 pages, 364 daily entries, 52 weeks in seven movements plus the three Mochin.
Read in full; every factual and arithmetical claim checked against `index.html`.

The document's own standing invitation — *"Correct my Kabbalah wherever I
overstep"* — is what this answers.

---

## A. Three places where it contradicts the app

### A1. Week 20 "The Calendar Walk" (days 134–140) and day 158 "Bolted to the Calendar"

These say the letter-cycles land on fixed Hebrew dates: *"Rosh Hashanah's cycle
always carries Alef; the Three Weeks always carry the final Nun; Elul always
carries the returner's Tzadik."* Day 221 does the same (*"cycle 14 of the Alef
Beit year (17 Tammuz–9 Av, the letter Nun Sofit)"*).

The app does not work that way. `get22DayInfo(d)` is called with the day of the
**Kabbalah of Time year** and folds at 364:

```js
d = ((d - 1) % 364) + 1;
const cycle = (d % 22 == 0) ? parseInt(d/22) : 1 + parseInt(d/22);
```

and the Keter/Da'at ⓘ says of that year: *"It is deliberately not a lunar-solar
year, and so it walks against the Hebrew calendar rather than with it"* — plus a
28-day intercalation in a leap year, during which the cycles hold where they
stood. So the letter on any given Hebrew date moves year to year.

What is worth keeping: the **chain is internally perfect** as 22-day sets counted
backwards from 6 Tishrei — Nun Sofit 17 Tammuz–9 Av, Peh Sofit 10 Av–1 Elul,
Tzadik Sofit 2–23 Elul, the twelve-day seal 24 Elul–6 Tishrei (which does contain
25 Elul, the first day of Creation). That is almost certainly the original blog's
anchoring, and the set order matches the app's (set 16 = Tzadik Sofit). So the
week is right about the *order* and the *affinities*; it is only the claim of
fixity that fails.

Two ways out, either fine:
- reframe the week as the anchoring the original blog used, and the shape it
  reveals — explicitly not the app's running count; or
- drop "always" and keep the letter–season pairings as readings.

The app already has the exact sentence for this, used three times in the cores:
*"This is a reading of the number and not an anchor on it."* Borrow it.

Two smaller errors inside the same week, which survive either fix:
- **Day 136** puts Tu b'Shvat in Kaf/Lamed. On that chain Kaf/Lamed closes 11
  Shevat; Tu b'Shvat (15 Shevat) falls in Mem/Nun.
- **Day 136** says "Mem/Nun and Samech/Ayin close winter in Adar." Mem/Nun runs
  12 Shevat–4 Adar — mostly Shevat.

### A2. Day 277 misquotes Lesson 23

The day's whole conceit is that the teaching performs itself: Rebbe Nachman's
yahrzeit, and *"Lesson 23: 'life, true life, holiness, which continues even after
a person passes away.'"*

The date is right — the app puts Lesson 23 on the 4th day of Sukkot, which is 18
Tishrei, the yahrzeit. The content is not. The app's summary:

> for the 4th day of Sukkot. About the 'voice' of the Shofar and the 'voice' of
> the Hoshanot, calling out to the inner point of every Jew to awaken from
> spiritual slumber.

Keep the coincidence — it is real and lovely — but the day needs to be rebuilt on
what Lesson 23 actually says, or moved to a lesson that does say it.

### A3. Day 178 generalises the Gevurah core's dated organs to all four seasons

Week 26 states "Right kidney: the 3rd of Iyar. Left kidney: the 20th of Sivan.
Heart: the 26th of Iyar" as properties of *"the ninety-one days."*

In the app the four 91-day seasons are counted from the KoT day; each has a heart
on **its own** day 46, and Winter's is Tu b'Shvat. The dated heart and kidneys
belong only to the one stretch, 11 Nissan → 12 Tammuz. Week 35 then states them
again, correctly, as the core's.

Fix week 26 to say the body is in the count — ratzo 45, the heart on 46, shov 45,
kidneys at 23 and 69 — and hold the dates back for week 35. The reveal is better
drama there anyway.

---

## B. Arithmetic

### B1. The 41 days from Rosh Chodesh Elul to Yom Kippur — and this one is in the app too

Days 222, 256 and 272 all say: *"Rosh Chodesh Elul to Yom Kippur — 41 days: the
original 40 that Moses stood on Sinai, plus the day of receiving."*

Elul always has 29 days and Av always 30, so:
- 1 Elul → 10 Tishrei inclusive = **39** days
- 30 Av (the first day of Rosh Chodesh Elul) → 10 Tishrei = **40** days

Never 41. And the logic double-counts: Yom Kippur *is* the fortieth — the day
Moshe came down with the second tablets — not a forty-first beyond it.

The app says it too, in `netzach.main`:

> forty-one days is also the count from the first of Elul to Yom Kippur — the
> original forty days on Sinai, plus the day of receiving

and again in `netzach.advanced`. **This wants fixing in `index.html` as well as
in the book.**

Nothing else moves. The Netzach structure stands on its own: nine rounds of forty
climbing the four soul-levels, each sealed by a forty-first day of Yechidah,
9 × 41 = 369. Only the Elul anchor is off by one. Suggested wording:

> Forty days is the count from Rosh Chodesh Elul to Yom Kippur — Moshe's forty on
> Sinai, the tenth of Tishrei the day of receiving. The cycle seals each forty
> with a forty-first of Yechidah.

### B2. Sixteen rounds or seventeen

- Day 99: *"Sixteen full rounds a year, plus a twelve-day seal: 16 × 22 + 12 = 364."*
- Day 104 and day 159: *"The letter-cycle turns seventeen times a year… Seventeen
  rounds of good, every year, without fail."*
- Day 146 and day 255: back to sixteen.

Both framings are in the app — `chochmah.beginner` says *"Seventeen rounds a
year"*, the code comment says *"sixteen full sets of twenty-two days and then a
short one: set 17 is the vowels"* — so the book inherited the looseness rather
than inventing it. But at 150 words a day, four pages apart, it reads as a
contradiction, and "seventeen rounds of good, without fail" overstates it: the
alphabet is completed sixteen times.

One sentence reconciles it, and keeps the טוב:

> Seventeen sets a year — sixteen that complete the alphabet, and a seventeenth of
> twelve days, the vowels. Seventeen is טוב, good.

### B3. "Fortnight" for thirteen days

Day 224 and the week-32 teaser: *"the thirteen: the year's mercy, in a
fortnight."* Day 258's shelf repeats it. A fortnight is fourteen days. (Same slip
I caught in the app's Tiferet text before it shipped.)

### B4. Day 65 — the Song of the Sea does not come after the forty-two journeys

> The Song of the Sea is sung at the end of forty-two journeys — the wilderness
> stations, from Egypt to the Jordan. Forty-two stops, then the song. … The sea
> parted on day one; the song came after forty-two journeys.

The Song is sung **at** the sea (Shemot 15), at the start of the wilderness; the
forty-two journeys of Bamidbar 33 end at the Jordan forty years later. The app's
Sunday book pairs sea-song verses with the forty-two stations as parallel weekly
tracks, not as a sequence.

The teaching — *"redemption isn't a moment, it's a route"* — survives intact if
"the song came after" becomes "the book sets the song beside the forty-two
stations, one to a week."

### B5. Day 133 — not the same verse

> the last line of Avot: "Everything that God created in His world, He created
> only for His glory" (6:11) — the exact verse the grass sings.

Avot 6:11 is a mishnah. The grass sings Psalms 104:31, *"May the glory of God
endure forever; may God rejoice in His works."* Different texts, the same word:
**kavod**. "The ethics end on the word the song began with" keeps the whole
effect and is true.

### B6. Day 61 — six doubled parashot

54 − 6 = 48 works, but there are **seven** pairs that can be doubled
(Vayakhel-Pekudei, Tazria-Metzora, Acharei-Kedoshim, Behar-Bechukotai,
Chukat-Balak, Matot-Masei, Nitzavim-Vayelech), and how many actually are varies
by year. Worth checking what the app's Shabbat book does before fixing a number
in print.

### B7. Day 57 — "never read on Shabbat"

True of the weekly cycle. But in Israel Simchat Torah is 22 Tishrei, the same
weekday as Rosh Hashanah, and Rosh Hashanah can fall on Shabbat — so V'zot
HaBrachah *is* read on a Shabbat in those years. Safe phrasing: *"never read on a
Shabbat of the weekly cycle."*

### B8. Day 149 — the dial's clock times are not fixed

> The afternoon and evening — 2:01 PM to 9:35 PM, weeks 27 through 42 — are Nissan
> through Tammuz

Those are one rendering, in fixed mode (where Chatzot is 1:43 AM). With zmanim
on, or at any other latitude or date, they move. Either drop the numbers or name
the setting they come from.

### B9. Days 274 / 299 — "25 Elul to 6 Tishrei"

Right as the app's own labels: Lesson 1 is for 25 Elul, and day 364 is Tinyana 92
"for the 6th of Tishrei — the last day of Week 52." But 364 days cannot run 25
Elul → 6 Tishrei in every Hebrew year; the app's own code comment hedges, *"about
25 Elul to 11 Tishrei."* Present them as the cycle's named ends, not as an
invariant span.

---

## C. Draft seams — text still thinking out loud in front of the reader

Seven places where the drafting shows. These are the ones a beginner would trip
on hardest, because the register breaks:

| Day | Text |
|---|---|
| 53 | *"and — the culmination — Israel's song? No: the dog's? … Actually the six: …"* — the whole paragraph is a note to self |
| 41 | *"Three in the curriculum's DNA: seven daily entries, one practice, one teaser — no, that's not three."* |
| 185, 224 | *"Twelve small offerings today — no, begin with three (the rule holds)"* |
| 62 | *"(the survey found no single thesis — so the week offers the question, not a verdict)"* — the research process showing |
| 314 | *"The unexamined song isn't worth singing? No — the tradition is kinder"* |
| 316 | *"You've walked the day, sung the songs (almost — they're coming)"* — the songs were Movement II, weeks 8–14, 250 days earlier |
| 31 | *"afternoon is spring (week / 1. — the exodus"* — a broken parenthesis that has turned into a list marker |

---

## D. Cross-references that point the wrong way in time

Four places treat a much later week as already past:

- Day 76: *"(Week 42's tzadik-within: the song the inner tzadik sings.)"*
- Day 86: *"(Week 44's image, returned as practice.)"* — week 44 is 216 days later
- Day 87: *"(The remedy gathers one of each — week 43.)"*
- Week 13's header: *"(The remedy-angle **was** week 43's; this week is the song.)"*

A reader at day 86 has nowhere to look. Make them forward-looking ("week 44 will
take this up as practice") or cut them.

---

## E. Structure and headings

- Weeks 1–3 are **named** ("The First Week", "The Second Week", "The Third
  Week"); weeks 4–52 are **numbered**. The Contents inherits the split.
- Weeks 1–14 and 46–52 carry no day ranges in the Contents; weeks 15–45 do.
- Weeks 1–3 use **"Today's practice:"** and **"Tomorrow:"**; weeks 4 on use
  **"Practice:"** and **"Teaser:"**.
- Day 323's teaser and day 327 both say "forty-nine weeks" at week 47. Should be
  forty-six.

The Contents is the reader's only map of a 155-page document. Worth regularising.

---

## F. A latent inconsistency the book makes visible

Day 107: *"Heh is feminine. It stands for Malchut."*
Day 111: *"Nun stands for Malchut — kingship."*

Both are the app's own words (`'Heh': 'The feminine letter of Malchut…'`,
`'Nun': 'Malchut…'`). The app spreads them eight days apart; the book puts them
four days apart in one week, where a beginner will notice. A half-sentence
distinguishing them — Heh as Malchut receiving, Nun as Malchut reigning — turns
the collision into a teaching.

---

## G. Omissions worth considering

Three of the ten cycle-weeks are much thinner than their cards:

1. **Week 25, Chesed** drops the structure that makes the cycle: five 72-day
   readings parted by four silent days (360 + 4 = 364); the four silences as the
   apertures of Birkat Kohanim's raised hands; the five lobes of the lung against
   the five Books of Moshe; water as the Kohanim's element; Chesed breathing over
   Gevurah, five lobes fanning one heart. That is the richest material on any
   card, and Chesed's week is the thinnest of the ten.

2. **Week 28, Netzach** never mentions the forty-first day — the Yechidah day
   that makes 9 × 41 = 369 and the reason Netzach is the one cycle that runs past
   the year. Day 272 introduces it 76 days later as if it were new. It belongs in
   week 28, where "its cycle is forty days" currently stands alone and is, by the
   app's reckoning, forty-one.

3. **Week 26, Gevurah** has the season as a body but not the season's face: the
   four Chayot of the Merkavah, the four cups from red receding to white and back,
   the four houses of Levi, the thirteen niggunim four times over, and Shamil —
   the one melody without words — on the day the season turns.

---

## H. What checks out

Worth recording, because it is most of the document.

**The three cores, entirely.** 21 Nissan → 3 Tammuz = 72 days. 11 Nissan → 12
Tammuz = 91. 17 Tammuz → Tu b'Av = 28, with the first 22 the Three Weeks and six
days of filling after. 17 Tammuz → 9 Av = 22. The heart on day 46 and the
kidneys at 23 and 69, symmetric. Right kidney = the way out, left = the way back
— matching the app's `כִּלְיָה יְמָנִית` / `כִּלְיָה שְׂמָאלִית`. Eicha's four
acrostics and the fifth chapter that keeps its twenty-two verses and will not
spell them. 20 Sivan and the Va'ad Arba Aratzot. 3 Iyar between Beis Iyar and Yom
HaZikaron. 26 Iyar as Yehoshua's yahrzeit, and Yehoshua holding both the heart of
the 91 and the close of the 72. The 31st reading as Yehoshua 10:12.

**The gematria and the counts.** 91 = ilan = 26 + 65 = the 13th triangular
number. 28 = koach. 72 = chesed. 17 = tov. 15 = yud-heh. 40 = mem. 343 = 7 × 7 × 7
as "the last day of the forty-nine." 13 × 28 = 364. 56 × 13 = 728, with Eliyahu
Rabbah's 31 chapters and Eliyahu Zuta's 25. 24 Elul → 6 Tishrei = 12. 10 Av → 1
Elul = 22 and 2–23 Elul = 22, which is what makes the backward chain in A1 land
so cleanly.

**The sources.** Avot 1:2 (Shimon HaTzaddik), 3:1 (Akavia ben Mahalalel), 4:1
(Ben Zoma), 4:3 (Ben Azzai), 5:20 (Yehuda ben Teima), 5:22 (Ben Bag-Bag), 5:23
(Ben He-He), 6:6 (the forty-eight). The fifty gates of Binah with the fiftieth
withheld. Wednesday's Psalm 94. Shemot 34:28 for the forty days without bread or
water. Chullin 60a for the grass. Psalms 146:8 for the bent made straight. Lesson
1 on 25 Elul and Torah 205 on Erev Pesach, both exactly as the app has them.
Haazinu's 52 verses with the prophets, the cities of refuge and the forty-eight
qualities.

---

## One note on voice

The first three weeks do what the brief asks — plain English first, Hebrew terms
as named gifts, one practice, one teaser. From week 4 the prose compresses into a
telegraphic register: *"Practice: Tonight, climb one step… Teaser: Tomorrow —
fifteen: why this number."* Verbless fragments, colons, em-dashes carrying the
argument.

It reads well, but it reads like a different book — and the compression lands
exactly where the material gets harder. For an on-ramp the looser voice of weeks
1–3 is the one that on-ramps. Worth at least carrying it through Movement I,
which is the part a newcomer will decide on.
