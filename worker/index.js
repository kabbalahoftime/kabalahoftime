// Kabbalahoftime Daily Digest — Cloudflare Worker
// Deploy:  wrangler deploy
// Secrets: wrangler secret put ANTHROPIC_API_KEY

const ALLOWED_ORIGINS = [
  'https://www.kabbalahoftime.com',
  'https://kabbalahoftime.com',
];

const SEFARIA_CALENDAR = 'https://www.sefaria.org/api/calendars';
const SEFARIA_TEXTS    = 'https://www.sefaria.org/api/v3/texts';
const CLAUDE_API       = 'https://api.anthropic.com/v1/messages';
const CLAUDE_MODEL     = 'claude-haiku-4-5-20251001';

// Which Sefaria calendar items to include (matched against title.en)
const WANTED_TITLES = [
  'Daf Yomi',
  'Daily Rambam',
  'Daily Tanya',
  'Parashat Hashavua',
];

// ── helpers ──────────────────────────────────────────────────────────────────

function getCorsHeaders(origin) {
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin':  allowed,
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age':       '86400',
  };
}

function stripHtml(str) {
  return (str || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

function flattenText(node) {
  if (typeof node === 'string') return stripHtml(node);
  if (Array.isArray(node))     return node.map(flattenText).filter(Boolean).join(' ');
  return '';
}

async function fetchSefariaCalendar(date) {
  const url = `${SEFARIA_CALENDAR}?date=${date}&diaspora=1&timezone=America%2FNew_York`;
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`Sefaria calendar: ${resp.status}`);
  return resp.json();
}

async function fetchSefariaText(ref, maxChars = 4000) {
  try {
    const encoded = encodeURIComponent(ref);
    const url     = `${SEFARIA_TEXTS}/${encoded}?version=english&context=0&pad=0`;
    const resp    = await fetch(url);
    if (!resp.ok) return null;
    const data    = await resp.json();
    const version = (data.versions || []).find(v => v.language === 'en');
    if (!version) return null;
    const text = flattenText(version.text);
    return text.length > maxChars ? text.slice(0, maxChars) + '…' : text;
  } catch {
    return null;
  }
}

async function summariseWithClaude(items, apiKey) {
  const numbered = items
    .map((item, i) => `${i + 1}. ${item.title}\n${item.text || '(Text not available)'}`)
    .join('\n\n---\n\n');

  const prompt = `You are writing a daily Torah study digest for a Jewish learning site.
For each numbered text below, write a 2–3 sentence summary in plain, respectful English that captures the main teaching or content.

Return ONLY a valid JSON array in this exact format — no extra text:
[{"title": "<exact title as given>", "summary": "<2-3 sentence summary>"}]

Today's texts:

${numbered}`;

  const resp = await fetch(CLAUDE_API, {
    method: 'POST',
    headers: {
      'Content-Type':      'application/json',
      'x-api-key':         apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model:      CLAUDE_MODEL,
      max_tokens: 2048,
      messages:   [{ role: 'user', content: prompt }],
    }),
  });

  if (!resp.ok) throw new Error(`Claude API: ${resp.status}`);
  const data    = await resp.json();
  const content = data.content?.[0]?.text || '';
  const match   = content.match(/\[[\s\S]*\]/);
  if (!match) throw new Error('Could not parse Claude response as JSON');
  return JSON.parse(match[0]);
}

// ── main handler ─────────────────────────────────────────────────────────────

export default {
  async fetch(request, env) {
    const url     = new URL(request.url);
    const origin  = request.headers.get('Origin') || '';
    const cors    = getCorsHeaders(origin);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== 'GET') {
      return new Response('Method not allowed', { status: 405, headers: cors });
    }
    if (url.pathname !== '/digest') {
      return new Response('Not found', { status: 404, headers: cors });
    }

    try {
      const date     = url.searchParams.get('date')     || new Date().toISOString().slice(0, 10);
      const lmLesson = url.searchParams.get('lmLesson') || null;
      const hayomYom = url.searchParams.get('hayomYom') || null;

      // 1. Sefaria calendar → select wanted items
      const calData  = await fetchSefariaCalendar(date);
      const calItems = (calData.calendar_items || []).filter(item =>
        WANTED_TITLES.some(t => (item.title?.en || '').includes(t))
      );

      // 2. Fetch texts in parallel
      const items = await Promise.all(calItems.map(async item => ({
        title: `${item.title?.en}: ${item.displayValue?.en}`,
        url:   item.sefaria_link || `https://www.sefaria.org/${item.url}`,
        text:  await fetchSefariaText(item.ref),
      })));

      // 3. Add Likutei Moharan if lesson number provided
      if (lmLesson) {
        const lmText = await fetchSefariaText(`Likutei_Moharan.${lmLesson}`);
        items.push({
          title: `Daily Likutei Moharan: Lesson ${lmLesson}`,
          url:   `https://www.sefaria.org/Likutei_Moharan.${lmLesson}`,
          text:  lmText,
        });
      }

      // 4. Prepend Hayom Yom (text already known client-side, no fetch needed)
      if (hayomYom) {
        items.unshift({
          title: 'Hayom Yom',
          url:   `https://www.chabad.org/library/article_cdo/aid/3304/jewish/Hayom-Yom.htm`,
          text:  decodeURIComponent(hayomYom),
        });
      }

      // 5. Summarise all with one Claude call
      const summaries = await summariseWithClaude(items, env.ANTHROPIC_API_KEY);

      // 6. Merge summaries with URLs (align by index)
      const result = summaries.map((s, i) => ({
        title:   s.title,
        summary: s.summary,
        url:     items[i]?.url || null,
      }));

      return new Response(JSON.stringify({ date, items: result }), {
        headers: { ...cors, 'Content-Type': 'application/json' },
      });

    } catch (err) {
      console.error(err);
      return new Response(JSON.stringify({ error: err.message }), {
        status:  500,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }
  },
};
