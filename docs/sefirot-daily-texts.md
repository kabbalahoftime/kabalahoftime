# Sefirot Daily-Text Cycles — Design Notes

A working record of the daily/weekly study-text overlays being designed for the
sefirah cards, so a long design session isn't lost. Each sefirah's **defining
cycle** (the counted מעלה rung) stays as-is; these are *texts* layered onto the
card — the study reading that changes each day, the way Chesed carries the Mishna
and Gevurah the Tanach.

**Design principle observed throughout:** the fit for each work emerged with
minimal forcing. Where a clean number had to be reached, the counter was almost
always an *introduction* (Netzach) or a *cover page* (Chochmah) — never
rearranging the source. When a structure clicks shut without forcing, that's the
sign it's real.

**Guardrails when building any of these:**
- Don't disturb the 15 מעלה + 15 מיעוט counted steps (the new blocks use plain
  ✧ labels, no `maalah` tags).
- Overlays are **364-day cycles that reset with the year** — except **Yesod**
  (parasha-native, follows the real Torah reading) and **Netzach** (369, with a
  5-day "doubling" at the seam that re-syncs each year rather than drifting).
- Verify all counts against Sefaria before wiring (most enumeration is still
  pending — see each section). Sefaria/HebrewBooks/Wikisource were unreachable
  from the build environment during design, so figures the author supplied are
  marked as such.

Status legend: **LIVE** = built and deployed · **DESIGNED** = worked out, not yet
built.

---

## Chochmah — Torah Ohr / Likutei Torah  **(LIVE)**

Defining cycle: Alef-Bet, 22-day (מעלה ד׳). Overlay: the Alter Rebbe's Torah,
**one folio a day**, 364-day cycle, on the card face + detail.

Layout (one folio/day; 3 discourses/day for Shir HaShirim), with **two paired
cover days** seating the four cover pages:

| Days | Section | Content |
|---|---|---|
| 1 | Cover¹ | Torah Ohr cover (req 16069 pg 1) + LT Vayikra cover (req 16093 pg 12) |
| 2–100 | Torah Ohr | 99 folios (main text ends Page 200 — a few lines — so 99 folios) |
| 101–150 | LT Vayikra | 50 folios |
| 151 | Cover² | LT Bamidbar cover (pg 138) + LT Devarim cover (pg 332) |
| 152–247 | LT Bamidbar | 96 folios |
| 248–347 | LT Devarim | 100 folios |
| 348–364 | Shir HaShirim | 51 folios, 3/day = 17 days |

**HebrewBooks:** Torah Ohr = req **16069**; all Likutei Torah = req **16093**.

**Page anchors** (folio 1a pgnum → last main folio a-side pgnum; folio→page is
linear except Vayikra):
- Torah Ohr: 9 → 205 (fMax 99) · Bamidbar: 140 → 330 (96) · Devarim: 334 → 530
  (100) · Shir HaShirim: 534 → 632 (51) · **Vayikra: 14 → 128 (50)** — non-linear
  (inserted Hosafot), interpolated within a page.

**Leap year** — the 28-day Adar I microcosm reads the **Hosafot** (the addenda as
the added month), ½ + 4 + 23½ = 28 folios:
- Day 1: LT Vayikra Hosafa, folio 8b (pgnum 29)
- Days 2–5: LT Vayikra 4-folio Hosafa, folio 50b→ (pgnum 130, 132, 134, 136)
- Days 6–28: Torah Ohr 23½-folio Hosafa, Page 203–248 (pgnum 211–255)

---

## Binah — Likutei Tefilot  **(LIVE)**

Defining cycle: Sefirot 7×7×7 Omer, 49-day (מעלה ה׳). Overlay: **Likutei Tefilot**
(Reb Noson), 364-day cycle, per-prayer Sefaria links on the Binah face.

- Day 1: Introduction
- Days 2–305: Part 1 — 152 prayers × 2 days (first/second half) → `Likutei_Tefilot,_Volume_I.N`
- Days 306–364: Part 2 — 59 prayers × 1 day → `Likutei_Tefilot,_Volume_II.N`
- 1 + 304 + 59 = 364.

---

## Netzach — Sichos HaRan + Likutei Etzot  **(DESIGNED)**

Defining cycle: 41-day, "receiving the Torah" (מעלה ט׳). Netzach's number is
**369** (with a 5-day doubling at the year seam — no drift). Two Rebbe Nachman
works, the narrative + the distilled counsel, sum to it:

| Work | Count |
|---|---|
| Sichos HaRan — Hakdamah + §1–308 | **309** |
| Likutei Etzot — Introduction + 59 topics | **60** |
| **Total** | **369** |

**Likutei Etzot 59** = 65 listed topics (44 + 21) with the holiday cluster
combined. The 13 holiday entries (Moadei Hashem + its 12) → **7**, per the
author's pairing:
1. Moadei Hashem & Shabbat
2. Rosh Chodesh & Three Festivals
3. Nisan/Passover & Omer/Shavuot
4. Three Weeks & Elul
5. **Rosh Hashana** (alone)
6. Yom Kippur & Sukkot
7. Chanukah & Purim

65 − 6 = 59; + intro = 60. The two counters are **Reb Noson's two hakdamos**
(one to Sichos HaRan, one to Likutei Etzot) — the disciple's two prefaces are
exactly what complete the year to 369.

**To verify on Sefaria:** exact Likutei Etzot topic list; that both works carry a
countable introduction; Sichos HaRan = 308 sections.

---

## Tiferet — Seder Birkas HaNehenin + Rebbe Nachman's Tales  **(DESIGNED)**

Defining cycle: 13-day, 13 Attributes of Mercy (מעלה ח׳). **Structure: 26
thirteen-day cycles + a 26-day microcosm of the 26** (26×13 = 338 + 26 = 364).
Two works, one per 13-day cycle, read **once each** (no repetition):

- **First half (cycles 1–13):** Seder Birkas HaNehenin, chapters **1→13 in order**
  (13 chapters — confirmed via Chabad).
- **Second half (cycles 14–26):** Sippurei Ma'asiyot (Rebbe Nachman's Tales),
  tales **1→13 in printed order** (no rearranging).

**26 = יהוה** (the Name Tiferet embodies) · **13 = אחד / אהבה** — two thirteens
making the Name.

**Seam at Purim:** Birkas HaNehenin Ch 13 ("Blessings Over Miracles and as
Thanksgiving") hands to Tale 1 (the Lost Princess) — hoda'ah → hester.

**Resonances discovered from the printed order (not arranged):** Lost Princess
(Tale 1) ≈ Adar/Purim → Pesach (hidden→revealed); Master of Prayer (Tale 12) ≈
Av/Elul (tefilah/teshuva); Seven Beggars (Tale 13, unfinished) ≈ Elul (defect→
perfection, the year's seal); Birkas HaNehenin Ch 11 (Shehecheyanu/fruits) ≈ Tu
B'Shvat. Middle tales fall where they fall — **read off the calendar once the
canonical tale order + exact cycle dates are confirmed**.

The **26-day microcosm** reviews all 26 at the end; the **introductions** are held
for leap years.

**To verify:** Seder Birkas HaNehenin has an introduction (the 14th-ish counter,
leap only) and per-chapter seif counts (for within-cycle daily pace); Sippurei
Ma'asiyot tale order; cycle→calendar dates (anchor: day 182 = 1 Nisan; 16 Nisan =
day 197).

---

## Yesod — Ben Ish Chai (both years, every year)  **(DESIGNED)**

Defining cycle: Shovavim / Parasha (מעלה י״ב) — **parasha-native**, follows the
real weekly Torah reading. Ben Ish Chai is already parasha-shaped, so text and
container are the same shape; nothing to fit.

**Name resonance:** Ben Ish *Chai* ("son of a living man") ↔ Yesod = *chai
olamim* (Zohar: the life of the worlds), the tzaddik *yesod olam*; his responsa
*Rav Pe'alim* ("abundant in deeds") = Yesod channeling light into deed. His
weekly method — open with a **drush** (sod), descend into **halacha** — is Yesod's
function drawn small.

**Sefaria structure** (`Ben_Ish_Hai`):
- Introduction
- **Drashot** — 54 (one homily per parasha, uncombined)
- **Halachot 1st Year** — 52 (51 parshiyot + a Chanukah section after Vayeshev)
- **Halachot 2nd Year** — 47, deliberately **partial** (skips the Bamidbar
  parasha; ends at Ki Tavo — Rav Yosef Chaim never finished the 2nd cycle)

**Mapping — complete the whole work every year, distinct daily:**
- Each parasha-week reads that parasha's *full* Ben Ish Chai — **Drash + Shanah
  Alef + Shanah Bet** — with the week's total **ot** distributed **one portion per
  day** (distinct daily readings; whole work finishes once a year).
- **Gaps handle themselves:** where Shanah Bet is silent (Bamidbar parasha;
  Devarim → V'Zot HaBerachah) the week carries Drash + Shanah Alef only. The
  Chanukah section reads on Chanukah (Vayeshev–Miketz = Kislev).
- **Common/leap auto-distributes:** combined-parsha weeks (common year) take both
  parshiyos' halachot at once; leap-year separate weeks spread lighter — the same
  combined-vs-separate seam seen between Shanah Alef and Shanah Bet.

**To verify:** per-parasha ot-counts (Drash, Year 1, Year 2) from Sefaria, so each
week's total divides evenly across its days.

---

## Where each still-Sephardi/Breslov/Chabad voice lands

Chabad (Chochmah, Tiferet ½), Breslov (Binah, Netzach, Tiferet ½), Sephardi
(Yesod) — the overlays quietly span the breadth of Klal Yisrael.

## Consolidated open tasks (need Sefaria reachable)

- **Netzach:** Likutei Etzot topic enumeration; confirm the two introductions;
  Sichos HaRan = 308.
- **Tiferet:** Seder Birkas HaNehenin intro + per-chapter seif counts; Sippurei
  Ma'asiyot tale order; cycle→calendar date map.
- **Yesod:** Ben Ish Chai per-parasha ot-counts (Drash / Year 1 / Year 2).
