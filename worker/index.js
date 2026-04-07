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

// Sefaria calendar items to auto-fetch (Tanya + Rambam chapters are computed here,
// not client-side, so we pull them directly from the calendar API)
const CALENDAR_TITLES = ['Daily Tanya', 'Daily Rambam'];

// ── helpers ──────────────────────────────────────────────────────────────────

function getCorsHeaders(origin) {
  const ok = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin':  ok,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
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

async function fetchSefariaText(ref, maxChars = 3000) {
  try {
    const url  = `${SEFARIA_TEXTS}/${encodeURIComponent(ref)}?version=english&context=0&pad=0`;
    const resp = await fetch(url);
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

async function fetchCalendarItems(date) {
  try {
    const url  = `${SEFARIA_CALENDAR}?date=${date}&diaspora=1&timezone=America%2FNew_York`;
    const resp = await fetch(url);
    if (!resp.ok) return [];
    const data = await resp.json();
    return (data.calendar_items || []).filter(item =>
      CALENDAR_TITLES.some(t => (item.title?.en || '').includes(t))
    );
  } catch {
    return [];
  }
}

async function summariseWithClaude(items, apiKey) {
  const numbered = items
    .map((item, i) => `${i + 1}. ${item.title}\n${item.text || '(Text unavailable — no summary possible)'}`)
    .join('\n\n---\n\n');

  const prompt = `You are writing a daily Torah study digest for a Jewish learning site.
For each numbered entry below, write a 2–3 sentence summary in plain, respectful English that captures the main teaching or content. If the text is unavailable, write a brief description of what this study cycle covers based on the title alone.

Return ONLY a valid JSON array — no extra text, no markdown fences:
[{"title": "<exact title as given>", "summary": "<your summary>"}]

Today's entries:

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
    const origin = request.headers.get('Origin') || '';
    const cors   = getCorsHeaders(origin);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405, headers: cors });
    }
    if (new URL(request.url).pathname !== '/digest') {
      return new Response('Not found', { status: 404, headers: cors });
    }

    try {
      const body = await request.json();
      const date  = body.date || new Date().toISOString().slice(0, 10);

      // Items sent from the client.  Each has:
      //   { title, url, text? }          — text already known (no fetch needed)
      //   { title, url, sefariaRef? }    — fetch text from Sefaria
      const clientItems = body.items || [];

      // Auto-add Tanya + Rambam from Sefaria calendar
      const calItems = await fetchCalendarItems(date);
      const calMapped = calItems.map(item => ({
        title:      `${item.title?.en}: ${item.displayValue?.en}`,
        url:        item.sefaria_link || `https://www.sefaria.org/${item.url}`,
        sefariaRef: item.ref,
      }));

      const allItems = [...clientItems, ...calMapped];

      // Fetch Sefaria text for any item that has a sefariaRef but no text
      const itemsWithText = await Promise.all(allItems.map(async item => {
        if (item.text)        return item;
        if (item.sefariaRef)  return { ...item, text: await fetchSefariaText(item.sefariaRef) };
        return item;
      }));

      // Summarise everything in one Claude call
      const summaries = await summariseWithClaude(itemsWithText, env.ANTHROPIC_API_KEY);

      // Merge summaries with URLs
      const result = summaries.map((s, i) => ({
        title:   s.title,
        summary: s.summary,
        url:     itemsWithText[i]?.url || null,
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
