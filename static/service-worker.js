// Service Worker for Skin Diary PWA

importScripts('https://storage.googleapis.com/workbox-cdn/releases/5.1.2/workbox-sw.js');

const CACHE_NAME = 'skindiary-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/custom.css',
  '/static/css/pwa.css',
  '/static/js/app.js',
  '/static/manifest.json',
  '/static/icons/icon-72x72.png',
  '/static/icons/icon-96x96.png',
  '/static/icons/icon-128x128.png',
  '/static/icons/icon-144x144.png',
  '/static/icons/icon-152x152.png',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-384x384.png',
  '/static/icons/icon-512x512.png',
  '/static/offline.html',
  'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js'
];

// Offline fallback page
const offlineFallbackPage = "/static/offline.html";

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

// Install event - cache assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  const currentCaches = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return cacheNames.filter(cacheName => !currentCaches.includes(cacheName));
    }).then(cachesToDelete => {
      return Promise.all(cachesToDelete.map(cacheToDelete => {
        return caches.delete(cacheToDelete);
      }));
    }).then(() => self.clients.claim())
  );
});

if (workbox.navigationPreload.isSupported()) {
  workbox.navigationPreload.enable();
}

// Network-first strategy with fallback to cache for normal navigation and API requests
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin) && 
      !event.request.url.includes('cdn.')) {
    return;
  }
  
  // Skip Google OAuth requests - OAuth needs to always go to network
  if (event.request.url.includes('google_login') || 
      event.request.url.includes('accounts.google.com')) {
    return;
  }

  // For HTML pages use network-first approach
  if (event.request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const preloadResp = await event.preloadResponse;

        if (preloadResp) {
          return preloadResp;
        }

        const networkResp = await fetch(event.request);
        return networkResp;
      } catch (error) {
        const cache = await caches.open(CACHE_NAME);
        const cachedResp = await cache.match(offlineFallbackPage);
        return cachedResp;
      }
    })());
    return;
  }

  // For other requests (CSS, JS, images), use cache-first approach
  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        if (cachedResponse) {
          return cachedResponse;
        }
        
        return fetch(event.request)
          .then(response => {
            // If we got a valid response, clone it and store in cache
            if (response && response.status === 200) {
              const responseToCache = response.clone();
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseToCache);
                });
            }
            return response;
          })
          .catch(error => {
            console.error('Fetch failed:', error);
            // Special handling for image requests
            if (event.request.url.match(/\.(jpg|jpeg|png|gif|svg)$/)) {
              return new Response('Image not available offline', { 
                status: 503, 
                statusText: 'Service Unavailable' 
              });
            }
            return new Response('Network error happened', {
              status: 503,
              statusText: 'Service Unavailable',
              headers: new Headers({
                'Content-Type': 'text/plain'
              })
            });
          });
      })
  );
});

// Handle push notifications (if we add them later)
self.addEventListener('push', event => {
  const title = 'Skin Diary';
  const options = {
    body: event.data.text() || 'New update from Skin Diary',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png'
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});