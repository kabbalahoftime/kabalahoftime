// Service Worker for Kabbalah of Time PWA
// Bumped so the activate handler below drops everything held under the old
// name and the shell is fetched again. A cache that has gone stale in a way
// the network-first rule cannot correct is the one failure this app has that
// leaves every card reading "Loading…" with nothing to say why.
const CACHE_NAME = 'kabbalah-of-time-v41';
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  // Fonts are bundled now rather than fetched from Google, so pre-cache them
  // — otherwise the first offline load falls back to system serifs.
  '/fonts/cinzel-latin-ext.woff2',
  '/fonts/cinzel-latin.woff2',
  '/fonts/cormorant-garamond-italic-latin-ext.woff2',
  '/fonts/cormorant-garamond-italic-latin.woff2',
  '/fonts/cormorant-garamond-latin-ext.woff2',
  '/fonts/cormorant-garamond-latin.woff2',
  '/fonts/frank-ruhl-libre-hebrew.woff2',
  '/fonts/frank-ruhl-libre-latin-ext.woff2',
  '/fonts/frank-ruhl-libre-latin.woff2'
];

// Install — pre-cache the shell, then take over immediately.
//
// Every request is made with cache: 'reload', which is the whole point of
// bumping CACHE_NAME. addAll goes through the browser's own HTTP cache, and
// GitHub Pages serves the page with a max-age of its own — so a new cache
// could be primed with the very copy the bump was meant to replace, and the
// reader would see yesterday's page for as long as that max-age ran. This
// goes to the network for the shell, always.
//
// One file at a time rather than addAll, which rejects the whole install if
// any single request fails: a font that 404s should not stop the page being
// cached. Anything missed here is fetched by the handler below.
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => Promise.all(
      urlsToCache.map((url) =>
        fetch(new Request(url, { cache: 'reload' }))
          .then((res) => (res && res.ok) ? cache.put(url, res) : null)
          .catch(() => {}))
    ))
  );
  self.skipWaiting();
});

// Fetch:
//   • HTML / navigations → CACHE-FIRST, REVALIDATING BEHIND. The cached page
//     is handed over at once and the network copy is fetched anyway, so the
//     next open has the newer one.
//
//     This was network-first with a three-second clock, which meant the cache
//     was only ever a rescue and never a shortcut: every open waited either
//     for the whole page to come down — half a megabyte compressed — or for
//     three seconds to pass. There was no path that served a warm cache
//     immediately, so the app was never quick to open, on any connection.
//
//     What it costs: a change to the page reaches the reader on their second
//     open rather than their first. That is a fair price here because the
//     page computes every card from the date at run time — a build from
//     yesterday still shows today correctly — so what waits a load is a fix
//     to the code, not the day's learning. Bump CACHE_NAME to force the
//     issue; the activate handler below drops everything under the old name.
//
//   • Everything else (manifest, icons, fonts) → cache-first, as before.
// The same request, made without consulting the browser's HTTP cache. A
// navigation Request cannot be rebuilt as-is — its mode is 'navigate', which
// a constructor will not take — so this builds a plain same-origin GET for
// the same URL. The response is stored under the original request, so the
// cache key does not change.
function fresh(req) {
  try {
    return new Request(req.url, { cache: 'reload', credentials: 'same-origin' });
  } catch (e) {
    return req;
  }
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const isHTML = req.mode === 'navigate' ||
    (req.headers.get('accept') || '').includes('text/html');

  if (isHTML) {
    event.respondWith((async () => {
      // Past the browser's own HTTP cache, for the same reason the install
      // does: GitHub Pages serves the page with a max-age, so a plain fetch
      // here can hand back the very copy this is meant to replace and write
      // it into the cache again. That is what made a change take several
      // opens to arrive instead of one — each open refreshed the cache with
      // the stale copy, and only when the max-age finally ran out did the
      // real page get through.
      const network = fetch(fresh(req)).then((response) => {
        if (response && response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
        }
        return response;
      });
      // The update runs whether or not anyone is waiting on it, so a cached
      // page that is wrong is replaced by the next open rather than standing.
      event.waitUntil(network.catch(() => {}));

      const cached = (await caches.match(req)) || (await caches.match('/index.html'));
      return cached || network;         // nothing cached yet — the first open pays
    })());
    return;
  }

  // Our own JSON is data the app is still being written into — the Zohar
  // summaries grow by a few entries at a time — so it gets the page's own
  // treatment rather than the fonts': served from cache at once, refetched
  // behind, and so one open behind rather than frozen. Cache-first with no
  // revalidation would have pinned the first copy a reader ever fetched, and
  // no bump of CACHE_NAME short of a new name would have shifted it.
  const sameOrigin = new URL(req.url).origin === self.location.origin;
  if (sameOrigin && new URL(req.url).pathname.endsWith('.json')) {
    event.respondWith((async () => {
      const network = fetch(fresh(req)).then((response) => {
        if (response && response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
        }
        return response;
      });
      event.waitUntil(network.catch(() => {}));
      const cached = await caches.match(req);
      return cached || network;
    })());
    return;
  }

  event.respondWith(
    caches.match(req).then((cached) => cached || fetch(req).then((response) => {
      if (response && response.status === 200 && response.type === 'basic') {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
      }
      return response;
    }))
  );
});

// Activate — purge old caches and claim open pages at once
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) => Promise.all(
      names.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n))
    )).then(() => self.clients.claim())
  );
});
