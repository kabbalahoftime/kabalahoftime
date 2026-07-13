// Service Worker for Kabbalah of Time PWA
const CACHE_NAME = 'kabbalah-of-time-v4';
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json'
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
