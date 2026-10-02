---
name: service-worker
description: "Implements service-worker lifecycle, offline routing, cache ownership, update flows, and PWA behavior. Use for a worker or offline/PWA task; HTTP/CDN header policy alone belongs to caching."
---

# Service Worker & PWA

A service worker is a network proxy that runs in its own thread, independent of pages. It enables offline, fine-grained caching, push, and background sync — but it's powerful and easy to footgun (stale content, "won't update"). Treat versioning and updates as first-class.

## Lifecycle (internalize this)

`register → install → activate → (controls pages) → update`

- **install**: precache the app shell. Call `self.skipWaiting()` to activate immediately (only if you handle updates gracefully).
- **activate**: clean up old caches. Call `self.clients.claim()` to control existing pages.
- A new SW **waits** until all old tabs close unless you `skipWaiting()`. This is why "my change didn't show up".
- Scope = the SW's directory and below. Serve it from the root to control the whole origin.

```js
navigator.serviceWorker.register('/sw.js'); // page side

// sw.js
const CACHE_PREFIX = 'my-app-shell-'; // unique to this app on the origin
const VERSION = `${CACHE_PREFIX}v3`;
const SHELL_ASSETS = ['/offline.html']; // include every offline fallback
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL_ASSETS)));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k.startsWith(CACHE_PREFIX) && k !== VERSION)
        .map((k) => caches.delete(k))),
    ),
  );
});
```

## Caching strategies — match to content type

| Strategy | Use for | Behavior |
|---|---|---|
| **Cache-first** | hashed static assets, fonts | serve cache, fall back to network |
| **Network-first** | HTML/navigations, fresh-critical API | try network, fall back to cache offline |
| **Stale-while-revalidate** | API JSON, avatars, mixed content | serve cache instantly, refresh in background |
| **Network-only / Cache-only** | non-GET, analytics / pure offline assets | bypass or only-cache |

- **Never serve stale HTML forever** — use network-first or SWR for documents so users discover updates.
- Only cache `GET`. Don't cache responses to mutations.
- Version and namespace cache names; delete only this app's old versions on `activate`. Cache Storage is shared across the origin, not isolated by service-worker scope.
- The Cache API does not enforce HTTP freshness or `Cache-Control: no-store`. Explicitly exclude private/authenticated responses unless offline storage is designed for that data, partition by account when needed, and clear it on logout. Check response status before caching.

```js
self.addEventListener('fetch', (e) => {
  const { request } = e;
  if (request.method !== 'GET') return;
  if (request.mode === 'navigate') {
    e.respondWith(fetch(request).catch(async () => {
      const cache = await caches.open(VERSION);
      return (await cache.match('/offline.html')) ??
        new Response('Offline. Please reconnect and try again.', {
          status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' },
        });
    }));
  }
});
```

## Background sync & updates

- **Background Sync** (`sync` event): queue eligible failed writes in IndexedDB with idempotency keys, bounded retries, and an explicit failure state. Feature-detect support and provide a foreground retry path. Periodic Background Sync has limited support.
- Tell users when a new SW is ready ("Refresh to update") rather than silently swapping, to avoid mid-session breakage.

## Installable PWA

- Ship a **web app manifest** (`name`, `icons` incl. maskable, `start_url`, `display: standalone`, `theme_color`).
- Install criteria vary by browser; serve over HTTPS with a suitable manifest. A service worker enables offline behavior but is not a universal install prerequisite. `beforeinstallprompt` is not cross-browser: feature-detect it and provide platform-specific instructions where absent.

## Use Workbox unless you have a reason not to

- Hand-written SWs get complex fast. **Workbox** gives battle-tested routing, strategies, precaching with revision manifests, and cleanup. Prefer it for non-trivial apps.

## Footgun checklist

- [ ] Cache names versioned and app-scoped; other apps' caches preserved.
- [ ] HTML is network-first / SWR, not cache-first.
- [ ] Only `GET` cached; mutations always hit network.
- [ ] Update flow handled (skipWaiting + user prompt) so changes ship.
- [ ] Tested offline and on a slow network in DevTools → Application → Service Workers.

## Reference

- MDN: [Cache API](https://developer.mozilla.org/en-US/docs/Web/API/Cache), [PWA installability](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable), Service Worker API, Background Sync.
- web.dev "Learn PWA"; Chrome for Developers: Workbox + "Caching strategies overview".
