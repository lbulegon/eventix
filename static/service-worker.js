// Service Worker para Eventix PWA
// Versão do cache - atualize quando fizer mudanças significativas
const CACHE_NAME = 'eventix-v1';
const RUNTIME_CACHE = 'eventix-runtime-v1';

// Arquivos essenciais para cache (cache-first)
const STATIC_CACHE_URLS = [
  '/',
  '/static/manifest.json',
  '/static/css/style.css',
  '/static/logo_eventix.png',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/static/icons/icon-maskable-192x192.png',
  '/static/icons/icon-maskable-512x512.png',
  '/static/icons/apple-touch-icon-180x180.png',
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Instalando...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Cacheando arquivos estáticos');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .then(() => self.skipWaiting()) // Força ativação imediata
  );
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Ativando...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // Remove caches antigos
          if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
            console.log('[Service Worker] Removendo cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim()) // Toma controle de todas as páginas
  );
});

// Estratégia: Cache First para assets estáticos
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignora requisições não-GET
  if (request.method !== 'GET') {
    return;
  }

  // Ignora requisições de API (sempre busca na rede)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() => {
        // Retorna resposta offline se disponível
        return new Response(
          JSON.stringify({ error: 'Offline - API não disponível' }),
          {
            headers: { 'Content-Type': 'application/json' },
            status: 503,
          }
        );
      })
    );
    return;
  }

  // Cache First para assets estáticos
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        
        return fetch(request).then((response) => {
          // Cacheia a resposta
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(RUNTIME_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        });
      })
    );
    return;
  }

  // Network First para páginas HTML
  event.respondWith(
    fetch(request)
      .then((response) => {
        // Cacheia páginas visitadas
        if (response.status === 200 && request.destination === 'document') {
          const responseClone = response.clone();
          caches.open(RUNTIME_CACHE).then((cache) => {
            cache.put(request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // Fallback: tenta buscar do cache
        return caches.match(request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          
          // Fallback: página offline genérica
          if (request.destination === 'document') {
            return caches.match('/').then((indexResponse) => {
              return indexResponse || new Response('Offline', {
                headers: { 'Content-Type': 'text/html' },
              });
            });
          }
          
          return new Response('Recurso não disponível offline', {
            status: 503,
          });
        });
      })
  );
});

// Mensagens do Service Worker
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

