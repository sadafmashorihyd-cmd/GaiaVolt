// GaiaVolt Service Worker — Full Offline PWA
const CACHE_NAME = 'gaiavolt-v3';
const STATIC_ASSETS = [
    '/',
    '/verify',
    '/evolution',
    '/bridges',
    '/nfts',
    '/vault',
    '/auth',
    '/manifest.json',
    '/icon-192.png',
    '/icon-512.png',
];

// Install — cache all static assets
self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS).catch(err => {
                console.log('Cache install error:', err);
            });
        })
    );
    self.skipWaiting();
});

// Activate — clean old caches
self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Fetch — cache first for static, network first for API
self.addEventListener('fetch', (e) => {
    const url = e.request.url;

    // Skip non-GET and extensions
    if (
        e.request.method !== 'GET' ||
        url.includes('chrome-extension') ||
        url.includes('supabase.co')
    ) {
        return;
    }

    // API calls — network only, show offline message if fail
    if (
        url.includes('hf.space') ||
        url.includes('127.0.0.1:8000') ||
        url.includes('/api/')
    ) {
        e.respondWith(
            fetch(e.request).catch(() => {
                return new Response(
                    JSON.stringify({
                        verdict: 'OFFLINE',
                        fraud_reason: 'You are offline. Please connect to internet to verify actions.',
                        offline: true
                    }),
                    { headers: { 'Content-Type': 'application/json' } }
                );
            })
        );
        return;
    }

    // Static assets — cache first, network fallback
    e.respondWith(
        caches.match(e.request).then(cached => {
            if (cached) return cached;

            return fetch(e.request).then(res => {
                if (res && res.status === 200) {
                    const clone = res.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
                }
                return res;
            }).catch(() => {
                // Offline fallback for pages
                if (e.request.destination === 'document') {
                    return caches.match('/');
                }
            });
        })
    );
});

// Background sync — when online again
self.addEventListener('sync', (e) => {
    if (e.tag === 'sync-verifications') {
        console.log('🌍 GaiaVolt: syncing pending verifications...');
    }
});

// Push notifications
self.addEventListener('push', (e) => {
    const data = e.data ? e.data.json() : {};
    e.waitUntil(
        self.registration.showNotification(data.title || 'GaiaVolt', {
            body: data.body || 'Your planet needs you! 🌍',
            icon: '/icon-192.png',
            badge: '/icon-192.png',
        })
    );
});