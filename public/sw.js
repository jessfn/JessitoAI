// Service worker de Blu: red primero (siempre la versión más nueva) y copia local para uso sin internet.
const CACHE = 'blu-cache';
const CDN = ['cdnjs.cloudflare.com'];
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('message', e => { if (e.data === 'skip') self.skipWaiting(); });
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.pathname.startsWith('/api/')) return;
  if (u.origin !== location.origin && !CDN.includes(u.hostname)) return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    if (u.origin !== location.origin) {                       // librerías de CDN: copia primero
      const hit = await cache.match(r); if (hit) return hit;
      const net = await fetch(r); if (net.ok) cache.put(r, net.clone()); return net;
    }
    try {
      const net = await fetch(r, { cache: 'no-store' });
      if (net.ok) cache.put(r, net.clone());
      return net;
    } catch (err) {
      const hit = await cache.match(r, { ignoreSearch: true }); if (hit) return hit;
      throw err;
    }
  })());
});
