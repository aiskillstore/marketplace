---
name: caching
description: "Diagnoses stale data and defines HTTP/CDN caching, freshness, and invalidation policies. Use for cache headers, ETags, hashed assets, or cache-layer investigations. Service-worker lifecycle and TanStack APIs are separate workflows."
---

# Caching

Caching is the highest-leverage performance lever and the easiest to get subtly wrong. Every caching decision reduces to one question:

> **Does the URL change when the content changes?**

- **Yes** (fingerprinted/hashed assets) → cache forever, immutable.
- **No** (HTML docs, API responses) → short freshness + revalidation.

## The layers (which may satisfy a request)

`App/query cache → controlling Service Worker → browser HTTP cache → CDN → Origin`

This is a conceptual model, not a guaranteed network path: a service worker can answer from Cache Storage or call fetch, which may use the HTTP cache. A hit can avoid downstream work entirely. Set policy deliberately at each layer.

## HTTP `Cache-Control` — the essentials

- `max-age=<s>` — browser freshness window.
- `s-maxage=<s>` — freshness for **shared** caches (CDN); overrides `max-age` there. Lets you cache briefly in the browser but longer at the CDN.
- `public` vs `private` — `private` = browser only (per-user data); `public` = shared caches may store it.
- `no-cache` — store but **revalidate before use** (not "don't cache"). `no-store` — never store (truly sensitive/dynamic).
- `immutable` — never revalidate during the freshness window; perfect for hashed assets.
- `stale-while-revalidate=<s>` — serve stale instantly while refetching in the background (best of both for HTML/API).
- `must-revalidate` — once stale, must check origin before reuse.

```http
# Fingerprinted asset (app.9f3c2.js) — cache aggressively
Cache-Control: public, max-age=31536000, immutable

# Public, non-personalized HTML / API response allowing stale reuse
Cache-Control: public, max-age=0, s-maxage=60, stale-while-revalidate=600
```

## Validation (revalidation without re-downloading)

- `ETag` + `If-None-Match`, or `Last-Modified` + `If-Modified-Since` → origin returns **304 Not Modified** (no body) when unchanged. Cheap freshness checks for HTML/API.

## The golden pattern

- **Static assets**: hash the filename at build time → `max-age=31536000, immutable`. New deploy = new URL = automatic cache bust.
- **HTML entry document**: short/zero `max-age` + `s-maxage` + `stale-while-revalidate`, or revalidate via ETag — so users get new asset references promptly.
- **API responses**: `private` for user data; short `max-age`/`s-maxage` + `stale-while-revalidate` for shared/list data; `no-store` for sensitive.

## Invalidation (the hard part)

- Prefer **URL versioning** (content hashes) so you never have to purge.
- For unhashed resources, use CDN **purge/tag-based invalidation** on deploy/update.
- Don't let a service worker pin stale HTML forever — version your SW caches and clean old ones on `activate`.

## Application / data caches

- TanStack Query, SWR, Apollo, RTK Query are in-memory caches keyed by query keys: tune `staleTime`/TTL, invalidate after mutations (see `tanstack`).
- Server-side: memoize/single-flight expensive aggregates; add Redis/edge KV with explicit TTL + invalidation for hot reads.
- Always make a cached write path **idempotent** so retries don't double-apply.

## Service worker caches (precise control)

- `cache-first` for hashed static assets, `network-first` for HTML/navigations, and SWR only for data that may safely be stale. Cache Storage does not enforce HTTP freshness or `no-store`: implement exclusions, expiry, and account/logout cleanup explicitly (see `service-worker`).

## Debug checklist

- Inspect response `Cache-Control`, `ETag`, `Age`, and CDN `x-cache: HIT/MISS`.
- Stale content? Check every layer (browser, SW, CDN) — purge the right one.
- "Update never shows" usually = HTML itself was cached too long, or SW serving stale HTML.

## Reference

- MDN: [Cache-Control](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control), [Cache API](https://developer.mozilla.org/en-US/docs/Web/API/Cache), HTTP caching.
- web.dev: "HTTP caching", "Love your cache".
- Jono Alderson "A complete guide to HTTP caching"; your CDN's caching/purge docs.
