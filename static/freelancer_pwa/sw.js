const CACHE_NAME = 'eventix-freelancer-pwa-v1';
const STATIC_ASSETS = [
  new URL('./styles.css', self.location).toString(),
  new URL('./app.js', self.location).toString(),
  new URL('./manifest.webmanifest', self.location).toString(),
  new URL('../icons/icon-192x192.png', self.location).toString(),
  new URL('../icons/icon-512x512.png', self.location).toString(),
  new URL('../icons/icon-maskable-192x192.png', self.location).toString(),
  new URL('../icons/icon-maskable-512x512.png', self.location).toString(),
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS)).catch((err) => {
      console.warn('[Eventix PWA] Falha ao pré-carregar assets', err);
    }),
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;

      return fetch(request)
        .then((response) => {
          if (!response || response.status !== 200 || response.type === 'opaque') {
            return response;
          }
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          return response;
        })
        .catch((error) => {
          console.warn('[Eventix PWA] Falha ao buscar recurso', request.url, error);
          throw error;
        });
    }),
  );
});

