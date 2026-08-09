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

// Fetch:
//   • HTML / navigations → NETWORK-FIRST, so the latest page always shows
//     when online (cache is only a fallback for offline). This is the fix
//     for the old cache-first behaviour that pinned the app to a stale copy.
//   • Everything else (manifest, icons) → cache-first, they rarely change.
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const isHTML = req.mode === 'navigate' ||
    (req.headers.get('accept') || '').includes('text/html');

  if (isHTML) {
    event.respondWith(
      fetch(req)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          return response;
        })
        .catch(() => caches.match(req).then((r) => r || caches.match('/index.html')))
    );
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
