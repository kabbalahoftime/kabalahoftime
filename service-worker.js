// Service Worker for Kabbalah of Time PWA
// Bumped so the activate handler below drops everything held under the old
// name and the shell is fetched again. A cache that has gone stale in a way
// the network-first rule cannot correct is the one failure this app has that
// leaves every card reading "Loading…" with nothing to say why.
const CACHE_NAME = 'kabbalah-of-time-v6';
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

// How long the network gets to answer a page request before the cached copy
// is served instead. Long enough that a merely slow connection still delivers
// the newest page; short enough that a bad one is not something you sit and
// watch. The request is not abandoned — it keeps running, and refreshes the
// cache whenever it lands.
const HTML_NETWORK_TIMEOUT = 3000;

// Fetch:
//   • HTML / navigations → NETWORK-FIRST WITH A CLOCK, so the latest page
//     shows when the network answers, and the cached one shows when it does
//     not. A failed request rejects and falls back on its own; a request that
//     merely hangs never rejects at all, and on weak wifi that left every card
//     reading "Loading…" indefinitely with a perfectly good copy in the cache.
//     Hence the timer: a fallback that waits on failure needs its own clock.
//   • Everything else (manifest, icons) → cache-first, they rarely change.
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const isHTML = req.mode === 'navigate' ||
    (req.headers.get('accept') || '').includes('text/html');

  if (isHTML) {
    event.respondWith((async () => {
      const network = fetch(req).then((response) => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
        return response;
      });
      // Keep the worker alive for the update even once the cached copy has
      // been handed over, so the next load has the newer page.
      event.waitUntil(network.catch(() => {}));

      const cached = (await caches.match(req)) || (await caches.match('/index.html'));
      if (!cached) return network;      // nothing to fall back to — let it fail as it would

      const timeout = new Promise((resolve) => setTimeout(resolve, HTML_NETWORK_TIMEOUT));
      const winner = await Promise.race([network.catch(() => null), timeout]);
      return winner || cached;
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
