# Daily summaries — work in progress

Nothing here is wired into the app yet. These are the first two pieces of the
per-day summary work, kept so they can be checked and continued.

## reference-map.csv

Every day of one KoT year against every lens the Weekly Journal draws — 39
columns, 364 rows in a common year, 392 in a leap one. Each cell is the exact
portion that cycle lands on that day, taken from the app's own per-day
functions rather than re-derived, so a cell and the card it describes cannot
part company.

Regenerate with `node tools/reference-map.mjs` (serve index.html on :8399
first). It reads `_yrBuild()` and `YR_LENSES`, which is what the Journal reads.

Two columns come back empty past **23 May 2027**: `ח׳ · Daf Yomi` and
`Talmud (Chazarah)`. Both call `getDafYomi`, whose table `DAF_YOMI_CYCLE14`
covers the 14th cycle only — 5 Jan 2020 to 23 May 2027, ending with Niddah.
In the current year 255 of 392 days have a daf and 137 do not. The 15th cycle
begins the next day and the table needs extending.

## tanach.json

A pilot: the first five days of מעלה ט׳, the Tanach cycle. The whole cycle is
742 chapters over 364 days — all of Nevi'im and Ketuvim exactly once, with
day 250 taking Psalms 119-134 together, the fifteen Songs of Ascent. Checked:
742 references, 742 distinct, none repeated, none missed, and no reference
outside its book's real chapter count.

The summaries were written from the text itself — the Sefaria export's merged
English, read chapter by chapter — not from memory. The `disclaimer` field is
carried in the file so whatever renders it cannot render it without.

Sizes, measured rather than guessed: these average 685 characters, 826 bytes
an entry with the JSON around them. The whole Tanach cycle would be ~294 KB;
all thirty cycles at ten thousand entries, ~7.9 MB. index.html is 1.8 MB
today, so this cannot live inside it — it wants loading per cycle, for the
day, which is a decision to take before the writing goes much further.
