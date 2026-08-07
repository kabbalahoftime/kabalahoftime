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
//   5. targets    — no control under 44px that isn't a link inside a sentence.
//   6. overflow   — the page never scrolls sideways, at any phone width.
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

let failures = 0;
const pass = m => console.log('  \x1b[32mok\x1b[0m   ' + m);
const fail = m => { failures++; console.log('  \x1b[31mFAIL\x1b[0m ' + m); };
const note = m => console.log('  \x1b[2m--\x1b[0m   ' + m);

// ── 1. parse ────────────────────────────────────────────────────────────────
function checkParse() {
  console.log('\nparse');
  const src = fs.readFileSync(path.join(ROOT, FILE), 'utf8');
  const re = /<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/g;
  let m, n = 0, bad = 0;
  while ((m = re.exec(src))) {
    n++;
    try { new Function(m[1]); }
    catch (e) { bad++; fail(`script block ${n}: ${e.message}`); }
  }
  if (!bad) pass(`${n} inline script blocks parse`);
  return src;
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

  // 5. tap targets — a link inside a sentence is exempt, as WCAG has it
  console.log('\ntargets');
  const small = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('button,a,input,select,[onclick]').forEach(e => {
      const r = e.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) return;
      if (r.width >= 44 && r.height >= 44) return;
      const parentText = e.parentElement ? (e.parentElement.textContent || '').trim().length : 0;
      const ownText = (e.textContent || '').trim().length;
      const inlineInProse = e.tagName === 'A' &&
        getComputedStyle(e).display.startsWith('inline') && parentText > ownText + 8;
      if (inlineInProse) return;
      out.push({ what: e.id || (e.className || '').toString().split(/\s+/)[0] || e.tagName,
                 w: Math.round(r.width), h: Math.round(r.height) });
    });
    return out;
  });
  // The language bar holds six buttons in a fixed strip; they are full height
  // and cannot also be full width without overflowing it.
  const excused = small.filter(s => /^lang-btn|^beginner-btn/.test(s.what) && s.h >= 44);
  const offenders = small.filter(s => !excused.includes(s));
  if (offenders.length) {
    offenders.slice(0, 10).forEach(s => fail(`${s.what} is ${s.w}x${s.h}, under 44px`));
    if (offenders.length > 10) fail(`…and ${offenders.length - 10} more`);
  } else pass(`all controls at least 44px${excused.length ? ` (${excused.length} in the language bar excused on width)` : ''}`);

  // 6. sideways scroll at phone widths
  console.log('\noverflow');
  for (const w of WIDTHS) {
    await page.setViewportSize({ width: w, height: 844 });
    await page.waitForTimeout(250);
    const over = await page.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    if (over > 0) fail(`${w}px wide: page scrolls sideways by ${over}px`);
    else pass(`${w}px wide: no sideways scroll`);
  }

  if (crashes.length) crashes.slice(0, 5).forEach(c => fail('uncaught: ' + c));

  await browser.close();
}

// ── run ─────────────────────────────────────────────────────────────────────
console.log(`checking ${FILE}`);
checkParse();

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
