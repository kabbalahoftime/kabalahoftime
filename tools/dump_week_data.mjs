// Dump what the app knows about all fifty-two weeks, by asking the app.
//
//   node tools/dump_week_data.mjs http://127.0.0.1:8731/index.html out.json
//
// The companion's 364 entries are one KoT Book for one week each — day 1 is
// Book 1's entry for week 1, day 2 is Book 2's for week 1, day 8 is Book 1's
// for week 2, which is how Binah files them. Every one of those entries is
// already in index.html, in the weekly table getWeeklyData reads. So the
// entries are transcribed rather than written, and this is the transcription
// step: the page is loaded and asked, because the table is built by the
// page's own code and a regex over 2.9MB of it would be guessing.
//
// Nothing here interprets anything. It copies 52 weeks x (7 books of fields,
// a creature, a teaching, a trait, a pairing, a month, a parasha, 7 post
// URLs) into one JSON file, and the builder makes sentences of it.
// Playwright is CommonJS and may be installed globally rather than here, so
// it is loaded the way check.mjs loads it — by require, across the places it
// turns up in.
import { createRequire } from 'node:module';
const _require = createRequire(import.meta.url);
const chromium = (() => {
  for (const spec of ['playwright', process.env.PLAYWRIGHT_PATH,
                      '/opt/node-tools/node_modules/playwright',
                      '/opt/node22/lib/node_modules/playwright',
                      '/usr/lib/node_modules/playwright',
                      '/usr/local/lib/node_modules/playwright'].filter(Boolean)) {
    try { return _require(spec).chromium; } catch (e) { /* try the next */ }
  }
  console.error('playwright not found; set PLAYWRIGHT_PATH');
  process.exit(2);
})();

const [url, out] = process.argv.slice(2);
if (!url || !out) {
  console.error('usage: node tools/dump_week_data.mjs <url> <out.json>');
  process.exit(2);
}

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium',
  args: ['--no-sandbox'],
});
const page = await browser.newPage();
await page.goto(url, { waitUntil: 'load' });
await page.waitForFunction(() => typeof getWeeklyData === 'function', { timeout: 30000 });
await page.waitForTimeout(1500);

const data = await page.evaluate(() => {
  const urlsFor = (n) => {
    try { return eval(`BOOK${n}_WEEK_URLS`); } catch (e) { return []; }
  };
  const bookUrls = [1, 2, 3, 4, 5, 6].map(urlsFor);
  const weeks = [];
  for (let w = 1; w <= 52; w++) {
    const wk = getWeeklyData(w);
    const face = (typeof kotwWeekData === 'function') ? kotwWeekData(w) : null;
    // Weeks 50-52 are the Mochin and stand outside the 7x7, so combo gives
    // nothing for them. That is the table's own answer, not a gap to fill.
    let pair = null;
    try { pair = (typeof kotwCombo === 'function') ? kotwCombo(w) : null; } catch (e) {}
    weeks.push({
      week: w,
      month: wk.month || '',
      parasha: wk.parasha || '',
      pairing: pair ? { he: pair.he, en: pair.en } : null,
      face: face ? { animal: face.a, avot: face.r, trait: face.t } : null,
      fields: {
        b1: { theme: wk.b1_theme, animal: wk.b1_animal, avot: wk.b1_avot },
        b2: { quality: wk.b2_quality, prophet: wk.b2_prophet, haazinu: wk.b2_haazinu,
              haftorah: wk.b2_haftorah, city: wk.b2_city },
        b3: { ruth: wk.b3_ruth, haftara: wk.b3_haftara, sotah: wk.b3_sotah,
              journeys: wk.b3_journeys },
        b4: { proverbs: wk.b4_proverbs, hannah: wk.b4_hannah, avot6: wk.b4_avot6,
              yahrzeit: wk.b4_yahrzeit },
        b5: { shir: wk.b5_shir, souls: wk.b5_souls, jeremiah: wk.b5_jeremiah,
              talmud: wk.b5_talmud },
        b6: { psalms: wk.b6_psalms, tikkun: wk.b6_tikkun, psalm89: wk.b6_psalm89 },
        b7: { mesilas: wk.b7_mesilas, theme: wk.b7_theme },
      },
      // The seven posts for the week, one to each book. Books 1-6 come from
      // their own table; book 7 carries its own address in the week's row.
      postUrls: [
        bookUrls[0][w - 1] || null, bookUrls[1][w - 1] || null,
        bookUrls[2][w - 1] || null, bookUrls[3][w - 1] || null,
        bookUrls[4][w - 1] || null, bookUrls[5][w - 1] || null,
        wk.b7_url || null,
      ],
    });
  }
  return {
    books: (typeof KOT_BOOKS !== 'undefined')
      ? KOT_BOOKS.map((b) => ({ book: b.book, what: b.what, emoji: b.emoji })) : [],
    weeks,
  };
});

await browser.close();

const missing = data.weeks.flatMap((w) =>
  w.postUrls.map((u, i) => (u ? null : `week ${w.week} book ${i + 1}`)).filter(Boolean));
const { writeFileSync } = await import('node:fs');
writeFileSync(out, JSON.stringify(data, null, 1), 'utf8');

console.log(`${data.weeks.length} weeks, ${data.books.length} books -> ${out}`);
console.log(`  post urls: ${data.weeks.length * 7 - missing.length} of ${data.weeks.length * 7}`);
if (missing.length) console.log(`  without a post: ${missing.join(', ')}`);
const noPair = data.weeks.filter((w) => !w.pairing).map((w) => w.week);
console.log(`  weeks with no Sefirah pairing: ${noPair.join(', ') || 'none'}`);
