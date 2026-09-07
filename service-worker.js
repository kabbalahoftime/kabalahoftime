// Service Worker for Kabbalah of Time PWA
// Bumped so the activate handler below drops everything held under the old
// name and the shell is fetched again. A cache that has gone stale in a way
// the network-first rule cannot correct is the one failure this app has that
// leaves every card reading "Loading…" with nothing to say why.
const CACHE_NAME = 'kabbalah-of-time-v7';
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

// Install — pre-cache the shell, then take over immediately
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
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
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const isHTML = req.mode === 'navigate' ||
    (req.headers.get('accept') || '').includes('text/html');

  if (isHTML) {
    event.respondWith((async () => {
      const network = fetch(req).then((response) => {
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
