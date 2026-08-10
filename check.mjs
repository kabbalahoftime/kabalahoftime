#!/usr/bin/env node
// Checks for index.html — the ones that have actually caught bugs here.
//
//   node check.mjs
//
// Needs Playwright. If it isn't installed, the browser checks are skipped and
// only the parse check runs, which still catches the most common breakage.
//   npm i -D playwright && npx playwright install chromium
//
// Set CHROMIUM=/path/to/chromium to use a browser you already have.
//
// What it looks for, and why each one is here:
//   1. parse      — every inline <script> parses. A stray brace in a 16,000
//                   line file gives a blank page and no other warning.
//   2. sweep      — no exception on any day across several years. The Hebrew
//                   calendar work (leap years, folded weeks, the 392-day year)
//                   is where the arithmetic goes wrong, and it goes wrong on
//                   dates nobody is looking at.
//   3. holes      — no "undefined" or "NaN" reaching the page. This is how the
//                   Binah card was found reading "undefined she'beundefined"
//                   for every date before the anchor.
//   4. ids        — no duplicated element id. Mirroring a card's face into the
//                   Now card once cloned 23 ids and quietly broke both.
//   5. perek      — each of the 52 weekly creatures resolves to a song, and no
//                   song sits in the table that no week ever reaches. The verses
//                   are keyed by the weekly table's own creature names, and a
//                   renamed creature would otherwise fall silent unnoticed.
//   6. alef-bet   — the 22-day cycle stays inside its 17 sets on every day of
//                   several years, on the card and in the calendar. 16 × 22 + 12
//                   = 364; a set above 17 means the year failed to roll over.
//                   Every other folded cycle is held to its bound the same way
//                   — the 13 Attributes to 28, the 41-day to 9, the 72 Names to
//                   5 — since all three of the faults found so far were one
//                   fault: a year-long count handed the count from the epoch.
//                   Each of the 27 letters also has its one sentence, keyed by
//                   the name the card shows — a rename loses it silently.
//   7. seo        — canonical, description and JSON-LD on every page, and a
//                   sitemap on the right namespace naming only pages that
//                   exist. All of it is served to crawlers and never to a
//                   reader, so nothing else would ever notice it rot.
//   8. targets    — no control under 44px that isn't a link inside a sentence.
//   9. overflow   — the page never scrolls sideways, at any phone width,
//                   with the cards shut and with every one of them open, and
//                   no detail value is squeezed too narrow to hold a word.
//  10. hebrew     — every Hebrew glyph is drawn by one face. Asked of the
//                   browser, not the stylesheet: a family with no Hebrew in it
//                   falls through silently to whatever the device happens to
//                   own, which differs on every device.
//  11. tracking   — no Hebrew-only text is letterspaced.
//  12. calendar   — each of the ten monthly calendars is compared against the
//                   card whose cycle it draws. They are two readings of one
//                   count, and if they part company the reader cannot tell
//                   which is wrong. This has caught two real faults already.
//
// Exits non-zero if any check fails, so it can gate a commit.

import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 8731);
const FILE = 'index.html';

// A date the app is exercised on. Fixed rather than "today" so a run in
// December tests the same thing a run in June did.
const FIXED_NOW = process.env.CHECK_DATE || '2026-08-07T09:00:00';
const SWEEP_FORWARD = Number(process.env.SWEEP_FORWARD || 1500);
const SWEEP_BACK    = Number(process.env.SWEEP_BACK    || 1500);
const WIDTHS = [320, 390, 430];
// The one face every Hebrew letter in the app should be drawn with.
const HEBREW_FACE = process.env.HEBREW_FACE || 'Frank Ruhl Libre';

let failures = 0;
const pass = m => console.log('  \x1b[32mok\x1b[0m   ' + m);
const fail = m => { failures++; console.log('  \x1b[31mFAIL\x1b[0m ' + m); };
const note = m => console.log('  \x1b[2m--\x1b[0m   ' + m);

// ── 1. parse ────────────────────────────────────────────────────────────────
// Every inline script must be JavaScript that parses — except the JSON-LD,
// which is data wearing a script tag. That one is JSON.parsed by checkSeo
// instead; running new Function() over it fails on the first colon.
function checkParse() {
  console.log('\nparse');
  const src = fs.readFileSync(path.join(ROOT, FILE), 'utf8');
  const re = /<script(?![^>]*src=)(?![^>]*ld\+json)[^>]*>([\s\S]*?)<\/script>/g;
  let m, n = 0, bad = 0;
  while ((m = re.exec(src))) {
    n++;
    try { new Function(m[1]); }
    catch (e) { bad++; fail(`script block ${n}: ${e.message}`); }
  }
  if (!bad) pass(`${n} inline script blocks parse`);
  return src;
}

// ── seo — the things that are wrong only where nobody looks ────────────────
// A canonical pointing at the wrong host, a sitemap listing a page that was
// renamed, a JSON-LD block with a trailing comma: all silent, all served to
// crawlers rather than to people, so nothing in the app ever complains.
const SITE = 'https://www.reflectionsofitall.com';
function checkSeo() {
  console.log('\nseo');
  const read = f => fs.readFileSync(path.join(ROOT, f), 'utf8');
  const pages = [['index.html', SITE + '/'],
                 ['kot-structure.html', SITE + '/kot-structure.html'],
                 ['maalot.html', SITE + '/maalot.html']];
  let bad = 0;
  for (const [file, want] of pages) {
    const src = read(file);
    const can = (src.match(/<link rel="canonical" href="([^"]+)"/) || [])[1];
    if (can !== want) { bad++; fail(`${file}: canonical is ${can || 'missing'}, expected ${want}`); }
    const desc = (src.match(/<meta name="description" content="([^"]*)"/) || [])[1];
    if (!desc || desc.length < 40) { bad++; fail(`${file}: description ${desc ? 'is too thin' : 'is missing'}`); }
    for (const m of src.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
      try { JSON.parse(m[1]); } catch (e) { bad++; fail(`${file}: ld+json does not parse — ${e.message}`); }
    }
  }
  if (!bad) pass(`${pages.length} pages: canonical, description and any JSON-LD all sound`);

  // the sitemap must be well-formed, on the right namespace, and every page it
  // names must actually be here
  const sm = read('sitemap.xml');
  let smBad = 0;
  if (!sm.includes('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')) {
    smBad++; fail('sitemap.xml: wrong or missing namespace (it is sitemaps.org, plural)');
  }
  const locs = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1]);
  if (!locs.length) { smBad++; fail('sitemap.xml names no pages'); }
  for (const loc of locs) {
    if (!loc.startsWith(SITE + '/')) { smBad++; fail(`sitemap.xml: ${loc} is not on ${SITE}`); continue; }
    const rel = loc.slice(SITE.length + 1) || 'index.html';
    if (!fs.existsSync(path.join(ROOT, rel))) { smBad++; fail(`sitemap.xml names ${rel}, which is not here`); }
  }
  if (!fs.existsSync(path.join(ROOT, 'robots.txt'))) { smBad++; fail('robots.txt is missing'); }
  else if (!read('robots.txt').includes(SITE + '/sitemap.xml')) {
    smBad++; fail('robots.txt does not point at the sitemap');
  }
  if (!smBad) pass(`sitemap names ${locs.length} pages, all present, and robots points at it`);
  return bad + smBad;
}

// ── a static server, so no python or global install is needed ───────────────
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
                '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
                '.woff2': 'font/woff2', '.svg': 'image/svg+xml', '.txt': 'text/plain' };

function serve() {
  return new Promise(resolve => {
    const server = http.createServer((req, res) => {
      const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '') || FILE;
      const file = path.join(ROOT, rel);
      if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
        res.writeHead(404); res.end('not found'); return;
      }
      res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
      fs.createReadStream(file).pipe(res);
    });
    server.listen(PORT, '127.0.0.1', () => resolve(server));
  });
}

// Playwright ships as CommonJS, and a bare directory is not something an ESM
// import can resolve — so it is loaded through require, which also lets a
// globally installed copy be found by absolute path.
function loadPlaywright() {
  const require = createRequire(import.meta.url);
  const tries = ['playwright', process.env.PLAYWRIGHT_PATH,
                 '/opt/node22/lib/node_modules/playwright',
                 '/usr/lib/node_modules/playwright',
                 '/usr/local/lib/node_modules/playwright'].filter(Boolean);
  for (const spec of tries) {
    try { return require(spec).chromium; } catch (e) { /* try the next */ }
  }
  return null;
}

// ── the browser checks ──────────────────────────────────────────────────────
async function checkInBrowser(chromium) {
  const launch = {};
  if (process.env.CHROMIUM) launch.executablePath = process.env.CHROMIUM;
  else if (fs.existsSync('/opt/pw-browsers/chromium')) launch.executablePath = '/opt/pw-browsers/chromium';
  const browser = await chromium.launch(launch);
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });

  const crashes = [];
  page.on('pageerror', e => crashes.push(e.message));

  await page.clock.setFixedTime(new Date(FIXED_NOW));
  await page.goto(`http://127.0.0.1:${PORT}/${FILE}`, { waitUntil: 'load' });
  await page.waitForTimeout(2500);

  // 2. sweep — every day for several years, forward and back
  console.log('\nsweep');
  const sweep = await page.evaluate(([fwd, back]) => {
    const out = { errors: [], holes: [], days: 0 };
    const look = () => {
      const t = document.body.innerText;
      return /\bundefined\b/.test(t) ? 'undefined' : /\bNaN\b/.test(t) ? 'NaN' : null;
    };
    const run = (dir, n) => {
      for (let i = 0; i < n; i++) {
        try {
          changeDay(dir);
          out.days++;
          const hole = look();
          if (hole && out.holes.length < 6) {
            out.holes.push({ offset: currentOffset, what: hole,
                             date: (document.body.innerText.match(/[A-Z]+ \d+, \d{4}/) || [])[0] });
          }
        } catch (e) {
          if (out.errors.length < 6) out.errors.push({ offset: currentOffset, msg: e.message });
        }
      }
      currentOffset = 0; render();
    };
    run(1, fwd);
    run(-1, back);
    return out;
  }, [SWEEP_FORWARD, SWEEP_BACK]);

  if (sweep.errors.length) sweep.errors.forEach(e => fail(`threw at offset ${e.offset}: ${e.msg}`));
  else pass(`${sweep.days.toLocaleString()} days rendered, no exception`);

  console.log('\nholes');
  if (sweep.holes.length) {
    sweep.holes.forEach(h => fail(`"${h.what}" on the page at offset ${h.offset} (${h.date || '?'})`));
  } else pass('no "undefined" or "NaN" on any day swept');

  // 4. duplicate ids
  console.log('\nids');
  const dups = await page.evaluate(() => {
    const seen = {}, out = [];
    document.querySelectorAll('[id]').forEach(e => {
      seen[e.id] = (seen[e.id] || 0) + 1;
      if (seen[e.id] === 2) out.push(e.id);
    });
    return out;
  });
  if (dups.length) fail(`duplicated id: ${dups.slice(0, 8).join(', ')}`);
  else pass('every element id is unique');

  // perek shirah — every week's creature has its song, keyed by the same name
  console.log('\nperek shirah');
  const ps = await page.evaluate(() => {
    const out = { weeks: 0, missing: [], thin: [], unused: [] };
    const used = new Set();
    for (let w = 1; w <= 52; w++) {
      const a = getWeeklyData(w).b1_animal;
      out.weeks++;
      const v = PEREK_SHIRAH_VERSES[a];
      if (!v) { out.missing.push(`week ${w}: ${a}`); continue; }
      used.add(a);
      // [chapter, source, verse, qualifier?] — a verse under 20 characters or
      // a citation with no number in it is extraction damage, not a song.
      if (!/^Ch [456]$/.test(v[0]) || !/\d/.test(v[1]) || !v[2] || v[2].length < 20)
        out.thin.push(`${a}: ${JSON.stringify(v).slice(0, 70)}`);
    }
    out.unused = Object.keys(PEREK_SHIRAH_VERSES).filter(k => !used.has(k));
    // The elements of Chapters 1-3 run one for one with the 33 tractate halves;
    // if the two lists ever slip apart the Chochmah card names the wrong element
    // for the wrong eleven days, and nothing on the page would say so.
    out.elems = { n: PEREK_SHIRAH_ELEMENTS.length, halves: TRACTATE_CYCLES.length, bad: [] };
    PEREK_SHIRAH_ELEMENTS.forEach((p, i) => {
      const t = TRACTATE_CYCLES[i];
      if (!t || t.id !== p.id) out.elems.bad.push(`slot ${i}: element ${p.id} against tractate ${t ? t.id : '—'}`);
      if (!/^Ch [123]$/.test(p.ch)) out.elems.bad.push(`${p.id}: chapter "${p.ch}" is not 1-3`);
      if (!p.el || !p.heb || !/\d/.test(p.src || '') || !p.verse || p.verse.length < 20)
        out.elems.bad.push(`${p.id}: incomplete — ${JSON.stringify(p).slice(0, 70)}`);
      if (!/^[֐-׿\s]+$/.test(p.heb || '')) out.elems.bad.push(`${p.id}: "${p.heb}" is not Hebrew`);
    });
    return out;
  });
  ps.missing.forEach(m => fail(`no Perek Shirah verse for ${m}`));
  ps.thin.forEach(m => fail(`Perek Shirah entry looks damaged — ${m}`));
  ps.unused.forEach(m => fail(`Perek Shirah verse for "${m}" is never reached by any week`));
  if (!ps.missing.length && !ps.thin.length && !ps.unused.length)
    pass(`all ${ps.weeks} weekly creatures have their song, and none is unreachable`);
  if (ps.elems.n !== ps.elems.halves)
    fail(`${ps.elems.n} Perek Shirah elements against ${ps.elems.halves} eleven-day halves`);
  ps.elems.bad.forEach(m => fail(`Perek Shirah element — ${m}`));
  if (ps.elems.n === ps.elems.halves && !ps.elems.bad.length)
    pass(`all ${ps.elems.n} eleven-day halves have their element, aligned with the tractate cycle`);

  // ── alef-bet — the 22-day cycle stays inside its 17 sets, every day of every
  // year. The count is 16 × 22 + 12 = 364, so a set number above 17 means the
  // year did not roll over: the card read the alphabet off a count that only
  // reset when the page was reloaded, and froze on the vowels for anyone who
  // read forward past a Rosh Hashanah. The last set clamps rather than throws,
  // so nothing else on the page would have shown it.
  console.log('\nalef-bet');
  const ab = await page.evaluate(() => {
    const out = { card: { days: 0, bad: [] }, cal: [], shown: { days: 0, bad: [], least: 99 } };
    for (let o = -400; o <= 800; o++) {
      currentOffset = o; render();
      const face = document.getElementById('chochmah-main').innerText;
      // Every letter the face names — the day's and the set's — must carry its
      // sentence in the pop-up the KoT Book opens; a letter named with nothing
      // behind it is the whole point of having them. Vowels are not a letter.
      const named = new Set();
      const dayLt = (face.match(/Day:\s*(.+?)\s+[֐-׿]/) || [])[1];
      const setLt = (face.match(/Cycle:\s*(.+?)\s+[֐-׿]/) || [])[1];
      if (dayLt) named.add(dayLt.trim());
      (setLt || '').split('&').forEach(x => x.trim() && named.add(x.trim()));
      named.delete('Vowels');
      if (named.size) {
        out.shown.days++;
        const box = document.createElement('div');
        box.innerHTML = _ltDetailMain;
        const lines = new Set([...box.querySelectorAll('[data-letter]')].map(e => e.dataset.letter));
        out.shown.least = Math.min(out.shown.least, lines.size);
        named.forEach(n => { if (!lines.has(n)) out.shown.bad.push(`offset ${o}: ${n} named with no sentence`); });
        lines.forEach(n => { if (!named.has(n)) out.shown.bad.push(`offset ${o}: a sentence for ${n}, which is not on the face`); });
        // and the control that opens them must be there, naming the same letters
        const ctl = document.querySelector('#chochmah-kot-book .kot-summary');
        if (!ctl) out.shown.bad.push(`offset ${o}: the letters are explained but nothing opens them`);
        else named.forEach(n => { if (!ctl.innerText.includes(n)) out.shown.bad.push(`offset ${o}: the control omits ${n}`); });
      }
      const m = face.match(/Day (\d+) · Cycle (\d+)/);
      if (!m) continue;               // the leap year's microcosm names no set
      out.card.days++;
      if (+m[2] > 17 || +m[2] < 1 || +m[1] > 22 || +m[1] < 1)
        out.card.bad.push(`offset ${o}: ${m[0]}`);
    }
    currentOffset = 0; render();
    // and the calendar's own lens, over a whole year — the card and the lens
    // are two readings of one count, and both were reading it from the epoch.
    const built = _yrBuild();
    if (built) {
      const bad = [], sets = new Set();
      for (const D of built.days) {
        const s = YR_LENSES[1].seg(D);
        if (s.mic) continue;
        const m = (s.cell2 || '').match(/set (\d+) · day (\d+) of 22/);
        if (!m) { bad.push(`${D.date.toDateString()}: the lens named no set`); continue; }
        sets.add(+m[1]);
        if (+m[1] > 17 || +m[2] > 22) bad.push(`${D.date.toDateString()}: ${m[0]}`);
      }
      out.cal.push({ hYear: built.hYear, days: built.days.length, sets: sets.size, bad });
    }
    // Every cycle that is bounded rather than rolling must stay inside its
    // bound on every day of the year. Each of these folds at 364 and each was
    // once handed the epoch count instead, which is a wrong reading and not an
    // error — the alef-bet froze on the vowels, the thirteen named itself a
    // microcosm it had left behind, and the forty-one reported cycle 30 of 10.
    out.bounds = [];
    const bound = (name, fn, max) => {
      let worst = 0, first = null;
      for (let day = 1; day <= 1200; day++) {
        const c = fn(day);
        if (c > max || c < 1) { worst = Math.max(worst, c); if (first === null) first = day; }
      }
      out.bounds.push({ name, max, worst, first });
    };
    bound('the 22-day alef-bet', d => get22DayInfo(d).cycle, 17);
    bound('the 13 Attributes',   d => get13DayInfo(d).cycle, 28);
    bound('the 41-day cycle',    d => get41DayInfo(d).cycle, 9);
    bound('the 72 Names',        d => getAyinBetInfo(d).cycle || 1, 5);
    // and each of the 27 letters has its sentence, keyed by the name the card
    // shows. A renamed letter would silently lose its meaning, since the face
    // simply omits the line when the lookup misses.
    const names = SINGLE_LETTERS_22.map(l => l.letter).concat(FINAL_LETTERS_MIC.map(l => l.letter));
    out.meanings = { n: names.length, missing: [], thin: [], unused: [] };
    names.forEach(n => {
      const m = LETTER_MEANINGS[n];
      if (!m) { out.meanings.missing.push(n); return; }
      // one sentence: some length, and no full stop before the last character
      if (m.length < 40) out.meanings.thin.push(`${n}: "${m}"`);
      if (/\.\s+\S/.test(m)) out.meanings.thin.push(`${n}: more than one sentence`);
    });
    out.meanings.unused = Object.keys(LETTER_MEANINGS).filter(k => !names.includes(k));
    return out;
  });
  ab.card.bad.slice(0, 5).forEach(m => fail(`the 22-day cycle left its 17 sets — ${m}`));
  if (!ab.card.bad.length) pass(`${ab.card.days.toLocaleString()} days on the card, every one inside sets 1–17`);
  ab.cal.forEach(c => {
    c.bad.slice(0, 5).forEach(m => fail(`the Chochmah calendar left its 17 sets — ${m}`));
    if (!c.bad.length) pass(`the Chochmah calendar for ${c.hYear} draws ${c.days} days across all ${c.sets} sets`);
  });
  ab.bounds.forEach(c => {
    if (c.first !== null)
      fail(`${c.name} runs to cycle ${c.worst} against a bound of ${c.max} — first at day ${c.first}`);
  });
  if (ab.bounds.every(c => c.first === null))
    pass(`all ${ab.bounds.length} folded cycles stay inside their bounds across 1,200 days`);
  ab.meanings.missing.forEach(m => fail(`the letter ${m} has no sentence`));
  ab.meanings.thin.forEach(m => fail(`letter meaning — ${m}`));
  ab.meanings.unused.forEach(m => fail(`a sentence for "${m}", which is no letter the card names`));
  if (!ab.meanings.missing.length && !ab.meanings.thin.length && !ab.meanings.unused.length)
    pass(`all ${ab.meanings.n} letters stand for something, one sentence each`);
  ab.shown.bad.slice(0, 5).forEach(m => fail(`the face and its sentences disagree — ${m}`));
  if (!ab.shown.bad.length)
    pass(`on ${ab.shown.days.toLocaleString()} days every letter the face names has its sentence, and no other does`);

  // 5. tap targets — a link inside a sentence is exempt, as WCAG has it
  console.log('\ntargets');
  // What matters is what the finger can reach, not what the box measures: a
  // control may keep its drawn size and carry a transparent overlay that grows
  // the hit area without moving the layout. So the page is asked what is
  // actually at a point 21px out from the centre, in each direction.
  const small = await page.evaluate(() => {
    const out = [];
    const reaches = (el, dx, dy) => {
      const r = el.getBoundingClientRect();
      const x = r.left + r.width / 2 + dx, y = r.top + r.height / 2 + dy;
      if (x < 0 || y < 0 || x > innerWidth || y > innerHeight) return true;  // off-screen, cannot judge
      const hit = document.elementFromPoint(x, y);
      return !!hit && (hit === el || el.contains(hit) || hit.contains(el));
    };
    document.querySelectorAll('button,a,input,select,[onclick]').forEach(e => {
      const r = e.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) return;
      const wideEnough = r.width  >= 44 || (reaches(e, -21, 0) && reaches(e, 21, 0));
      const tallEnough = r.height >= 44 || (reaches(e, 0, -21) && reaches(e, 0, 21));
      if (wideEnough && tallEnough) return;
      const parentText = e.parentElement ? (e.parentElement.textContent || '').trim().length : 0;
      const ownText = (e.textContent || '').trim().length;
      const inlineInProse = e.tagName === 'A' &&
        getComputedStyle(e).display.startsWith('inline') && parentText > ownText + 8;
      if (inlineInProse) return;
      out.push({ what: e.id || (e.className || '').toString().split(/\s+/)[0] || e.tagName,
                 w: Math.round(r.width), h: Math.round(r.height),
                 narrow: !wideEnough, short: !tallEnough });
    });
    return out;
  });
  // The language bar holds six buttons in a fixed strip; they are full height
  // and cannot also be full width without overflowing it.
  // Two deliberate exceptions, both from controls packed into a row where a
  // 44px reach would have to be taken from the control beside them:
  //   • the six language buttons — full height, but six of them cannot each be
  //     44px wide inside a 233px strip;
  //   • the toggle halves — 24px tall, the size WCAG requires, with the
  //     jump-to-date line about 30px below them.
  const excused = small.filter(s =>
    (/^lang-btn|^beginner-btn/.test(s.what) && !s.short) ||
    (/^year-pill-btn|^pr-|^tm-/.test(s.what) && s.h >= 24));
  const offenders = small.filter(s => !excused.includes(s));
  if (offenders.length) {
    offenders.slice(0, 10).forEach(s => fail(
      `${s.what} is ${s.w}x${s.h} and reaches under 44px ${s.narrow && s.short ? 'both ways'
        : s.narrow ? 'across' : 'down'}`));
    if (offenders.length > 10) fail(`…and ${offenders.length - 10} more`);
  } else pass(`all controls at least 44px${excused.length ? ` (${excused.length} in the language bar excused on width)` : ''}`);

  // 7. one Hebrew face — asked of the browser, not of the stylesheet
  //
  // Declaring a font is not the same as getting it. Cinzel and Cormorant
  // Garamond carry no Hebrew, so Hebrew set in them silently fell through to
  // whatever serif the device owned — Times on an iPhone, Liberation here.
  // Three faces were drawing Hebrew on one page. Chromium is asked which font
  // actually put each glyph on the screen, so the answer cannot be wishful.
  console.log('\nhebrew');
  const runs = await page.evaluate(() => {
    let i = 0;
    const nodes = [];
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walk.nextNode()) nodes.push(walk.currentNode);
    for (const node of nodes) {
      if (!/[֐-׿]/.test(node.nodeValue)) continue;
      if (!node.parentElement || /SCRIPT|STYLE/.test(node.parentElement.tagName)) continue;
      const frag = document.createDocumentFragment();
      for (const part of node.nodeValue.split(/([֐-׿]+)/)) {
        if (!part) continue;
        if (/^[֐-׿]+$/.test(part)) {
          const s = document.createElement('span');
          s.setAttribute('data-heb-check', String(i++));
          s.textContent = part;
          frag.appendChild(s);
        } else frag.appendChild(document.createTextNode(part));
      }
      node.parentNode.replaceChild(frag, node);
    }
    return i;
  });

  const cdp = await page.context().newCDPSession(page);
  await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
  const { root } = await cdp.send('DOM.getDocument', { depth: -1 });
  const { nodeIds } = await cdp.send('DOM.querySelectorAll',
    { nodeId: root.nodeId, selector: '[data-heb-check]' });

  const faces = {};
  const strays = [];
  for (const nodeId of nodeIds) {
    let fonts;
    try { ({ fonts } = await cdp.send('CSS.getPlatformFontsForNode', { nodeId })); } catch (e) { continue; }
    for (const f of (fonts || [])) {
      if (!f.glyphCount) continue;
      faces[f.familyName] = (faces[f.familyName] || 0) + f.glyphCount;
      if (f.familyName !== HEBREW_FACE && strays.length < 8) {
        const attrs = (await cdp.send('DOM.getAttributes', { nodeId })).attributes;
        const idx = attrs[attrs.indexOf('data-heb-check') + 1];
        const info = await page.evaluate(j => {
          const el = document.querySelector(`[data-heb-check="${j}"]`);
          const cs = getComputedStyle(el);
          return { text: el.textContent.slice(0, 14), declared: cs.fontFamily,
                   where: (el.closest('[id]') || {}).id || el.parentElement.tagName };
        }, idx);
        strays.push({ face: f.familyName, ...info });
      }
    }
  }
  if (strays.length) {
    strays.forEach(s => fail(`"${s.text}" in ${s.where} drawn by ${s.face}, declared ${s.declared}`));
  } else {
    pass(`all Hebrew (${runs} runs, ${faces[HEBREW_FACE] || 0} glyphs) drawn by ${HEBREW_FACE}`);
  }

  // 8. Hebrew is not letterspaced — tracking belongs to the Latin small-caps
  console.log('\ntracking');
  const tracked = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('*').forEach(el => {
      const own = [...el.childNodes].filter(c => c.nodeType === 3).map(c => c.nodeValue).join('').trim();
      if (!own || !/[֐-׿]/.test(own) || /[A-Za-z]/.test(own)) return;
      const cs = getComputedStyle(el);
      if (parseFloat(cs.letterSpacing)) {
        out.push({ where: el.id || (el.className || '').toString().split(/\s+/)[0] || el.tagName,
                   ls: cs.letterSpacing, text: own.slice(0, 16) });
      }
    });
    return out;
  });
  if (tracked.length) tracked.slice(0, 6).forEach(t =>
    fail(`Hebrew "${t.text}" in ${t.where} is letterspaced ${t.ls}`));
  else pass('no Hebrew-only text is letterspaced');

  // 9. the monthly calendars against the cards
  //
  // Each calendar draws a card's cycle. If the two ever disagree, one of them
  // is lying to the reader and there is no way to tell which from the outside.
  // So every lens is asked, on sampled days, to produce a value the card also
  // states, and the two are compared. This has already caught two real faults:
  // Gevurah measuring from the wrong year across the leap-year seam, and
  // Netzach still counting to 41 where the card had opened out to 55.
  console.log('\ncalendar');
  const agree = await page.evaluate(() => {
    const cards = [...document.querySelectorAll('.sefirah-card')].filter(c => c.id !== 'now-sefirah-featured');
    const flat = el => el ? el.innerText.replace(/\s+/g, ' ').trim() : '';
    const main = i => flat(cards[i] && cards[i].querySelector('.sefirah-main-text'));
    const m = (s, re) => (s || '').match(re);
    const pair = (x, a, b) => x ? x[a] + '|' + x[b] : '';
    // every match of a repeating pattern, order-independent
    const sig = (s, re, norm) => {
      const out = []; const r = new RegExp(re.source, 'g'); let x;
      while ((x = r.exec(s || ''))) out.push(x.slice(1).map(v => (norm && norm[v]) || v).join(':'));
      return out.sort().join(' , ');
    };
    const combo = s => { const x = m((s || '').replace(/'/g, ''), /(\w+) shebe(\w+) shebe(\w+)/); 
                         return x ? x[1] + '|' + x[2] + '|' + x[3] : ''; };

    // For each lens: what the card says, and what the calendar cell says.
    const PROBES = [
      { lens: 0, name: 'Keter',
        card: () => sig(flat(document.getElementById('keter-lm-main')),
                        /(Part I · Lesson|Tinyana · Torah) (\d+)/,
                        { 'Part I · Lesson': 'I', 'Tinyana · Torah': 'II' }),
        cell: s => sig(s.cell, /(Torah|Tinyana) (\d+)/, { Torah: 'I', Tinyana: 'II' }) },
      { lens: 1, name: 'Chochmah',
        card: () => (m(main(0), /Day: (\w+)/) || [])[1] || '',
        cell: s => (m(s.cell, /^\S+ (\w+)/) || [])[1] || '' },
      { lens: 2, name: 'Binah',
        card: () => combo(main(1)),
        cell: s => combo((s.cell || '') + ' ' + (s.cell2 || '')) },
      { lens: 3, name: 'Chesed',
        card: () => pair(m(main(2), /Day (\d+) · Cycle \d+ of 5: (\S+)/), 2, 1),
        cell: s => pair(m(s.cell, /^(\S+) · (\d+) of 72$/), 1, 2) },
      { lens: 4, name: 'Gevurah',
        card: () => pair(m(main(3), /Day (\d+) · Season \d+ \((\w+)/), 2, 1),
        cell: s => pair(m(s.cell, /^(\w+) · (\d+) of 91$/), 1, 2) },
      { lens: 5, name: 'Tiferet',
        card: () => { const x = m(main(4), /Day (\d+), (?:(\d)(?:st|nd|rd|th)|Microcosm ·) Cycle (\d+)/);
                      return x ? (x[2] || '3') + '|' + x[3] + '|' + x[1] : ''; },
        cell: s => { const x = m((s.cell || '') + ' ' + (s.cell2 || ''),
                                 /(?:(\d)(?:st|nd|rd|th)|microcosm) cycle (\d+)(?: of 2)? day (\d+) of 13/);
                     return x ? (x[1] || '3') + '|' + x[2] + '|' + x[3] : ''; } },
      { lens: 6, name: 'Netzach',
        card: () => pair(m(main(5), /Day (\d+) · Cycle (\d+)/), 2, 1) ||
                    pair(m(main(5), /Day (\d+) of 55 · Year-Cycle (\d+)/), 2, 1),
        cell: s => pair(m(s.cell, /Cycle (\d+) · day (\d+) of 41/), 1, 2) ||
                   pair(m(s.cell, /Year-Cycle (\d+) · day (\d+) of 55/), 1, 2) },
      { lens: 7, name: 'Hod',
        card: () => pair(m(main(6), /Half-Days (\d+) & (\d+)/), 1, 2),
        cell: s => pair(m(s.cell, /OC (\d+)–(\d+)/), 1, 2) },
      { lens: 8, name: 'Yesod',
        // A double parasha carries two numbers on each side — "Cycle 6 & 7" —
        // so the run has to be taken whole, not up to the first space.
        card: () => { const x = m(main(7), /Day (\d+) · Parasha (\d+(?: & \d+)*) · Cycle (\d+(?: & \d+)*)/);
                      return x ? x[1] + '|' + x[2] + '|' + x[3] : ''; },
        cell: s => { const x = m(s.cell2, /D(\d+) · P(\d+(?: & \d+)*) · C(\d+(?: & \d+)*)/);
                     return x ? x[1] + '|' + x[2] + '|' + x[3] : ''; } },
      { lens: 9, name: 'Malchut',
        // The Yad tag sits in the collapsed detail, which innerText skips —
        // textContent sees it whether the card is open or shut.
        card: () => pair(m((document.getElementById('malchut-detail') || {}).textContent,
                           /Cycle (\d+) · Day (\d+) of 28/), 1, 2),
        cell: s => pair(m(s.cell, /set (\d+) · (\d+)\/28/), 1, 2) },
    ];

    if (typeof openYearView !== 'function') return { missing: true };
    openYearView();
    const days = _yrDays.days;
    // Every lens's reading of every day, gathered before any card is drawn.
    const segs = PROBES.map(p => { yrSetLens(p.lens); return days.map(d => ({ ...d._seg })); });
    closeYearView();

    // Sample across the year, and take the last stretch whole — the year seam
    // is where the two have disagreed before.
    const idx = new Set();
    for (let i = 0; i < days.length; i += 11) idx.add(i);
    for (let i = Math.max(0, days.length - 15); i < days.length; i++) idx.add(i);

    const tally = PROBES.map(p => ({ name: p.name, compared: 0, skipped: 0 }));
    const bad = [];
    const held = currentOffset;
    [...idx].forEach(i => {
      const d = days[i];
      currentOffset = Math.round((localMidnight(d.date) - localMidnight(new Date())) / 86400000);
      render();
      PROBES.forEach((p, j) => {
        const a = p.card(), b = p.cell(segs[j][i]);
        if (!a || !b) { tally[j].skipped++; return; }
        tally[j].compared++;
        if (a !== b && bad.length < 8)
          bad.push(`${p.name} on ${d.date.toDateString()}: card "${a}" vs calendar "${b}"`);
        else if (a !== b) tally[j].mismatch = (tally[j].mismatch || 0) + 1;
      });
    });
    currentOffset = held; render();
    return { days: idx.size, tally, bad };
  });

  if (agree.missing) {
    fail('the monthly calendars are not present — openYearView is missing');
  } else {
    const dead = agree.tally.filter(t => t.compared === 0);
    if (agree.bad.length) agree.bad.forEach(x => fail(x));
    // A probe that never compared anything is a broken probe, not a pass.
    dead.forEach(t => fail(`${t.name}: nothing could be compared — the probe no longer matches`));
    if (!agree.bad.length && !dead.length) {
      const total = agree.tally.reduce((n, t) => n + t.compared, 0);
      const skipped = agree.tally.reduce((n, t) => n + t.skipped, 0);
      pass(`${total} readings across ${agree.tally.length} calendars match their cards ` +
           `(${agree.days} days sampled${skipped ? `, ${skipped} not comparable` : ''})`);
    }
  }

  // 6. sideways scroll at phone widths, shut and open
  //
  // Measuring only with the cards shut missed a real one: a long unbreakable
  // title in the Yad HaChazakah list pushed the page 7px sideways, but only
  // once Malchut was expanded. Most of the app's text lives inside a card that
  // has to be opened to be seen, so both states are measured.
  console.log('\noverflow');
  for (const w of WIDTHS) {
    await page.setViewportSize({ width: w, height: 844 });
    await page.waitForTimeout(250);
    const over = await page.evaluate(() => {
      const cards = [...document.querySelectorAll('.sefirah-card')];
      const shut = document.documentElement.scrollWidth - document.documentElement.clientWidth;
      const already = cards.filter(c => c.classList.contains('expanded'));
      cards.forEach(c => c.classList.add('expanded'));
      const open = document.documentElement.scrollWidth - document.documentElement.clientWidth;
      // A value column too narrow to hold a word is not a sideways scroll, so
      // nothing above would catch it: at 320px the label claimed 110 of the
      // row's 145 and "Torah Ohr" came down the page a letter at a time.
      const vals = [...document.querySelectorAll('.detail-row')]
        .filter(r => r.children.length === 2)
        .map(r => Math.round(r.querySelector('.detail-value').getBoundingClientRect().width));
      const narrowest = vals.length ? Math.min(...vals) : null;
      cards.forEach(c => { if (!already.includes(c)) c.classList.remove('expanded'); });
      return { shut, open, narrowest, rows: vals.length };
    });
    if (over.shut > 0) fail(`${w}px wide, cards shut: page scrolls sideways by ${over.shut}px`);
    else if (over.open > 0) fail(`${w}px wide, cards open: page scrolls sideways by ${over.open}px`);
    else pass(`${w}px wide: no sideways scroll, shut or open`);
    if (over.narrowest !== null && over.narrowest < 120)
      fail(`${w}px wide: the narrowest of ${over.rows} detail values is ${over.narrowest}px — too narrow to hold a word`);
    else if (over.narrowest !== null)
      pass(`${w}px wide: every detail value at least ${over.narrowest}px across ${over.rows} rows`);
  }

  if (crashes.length) crashes.slice(0, 5).forEach(c => fail('uncaught: ' + c));

  await browser.close();
}

// ── run ─────────────────────────────────────────────────────────────────────
console.log(`checking ${FILE}`);
checkParse();
checkSeo();

const chromium = loadPlaywright();
if (!chromium) {
  console.log('\nbrowser');
  note('Playwright not found — browser checks skipped.');
  note('npm i -D playwright && npx playwright install chromium');
} else {
  const server = await serve();
  try { await checkInBrowser(chromium); }
  finally { server.close(); }
}

console.log(failures ? `\n\x1b[31m${failures} check${failures > 1 ? 's' : ''} failed\x1b[0m\n`
                     : '\n\x1b[32mall checks passed\x1b[0m\n');
process.exit(failures ? 1 : 0);
