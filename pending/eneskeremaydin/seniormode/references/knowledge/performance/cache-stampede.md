---
id: "cache-stampede"
title: "Cache stampede and prewarming"
category: "performance"
summary: "Protect an expensive origin when a popular cache entry is missing or expires."
aliases: ["cache warming","request coalescing","flash sale","önbellek yığılması","cache stampede","önbellek boşaldığında bütün istekler veri tabanına gidiyor","önbellek aynı anda doluyor","indirimden önce önbelleği ısıt","önbellek boşalınca yoğun veritabanı trafiği"]
decisions: [{"when":"A predictable event and safe public data","use":"Prewarm versioned content before the surge and set expiry according to staleness policy.","tradeoff":"Operational timing matters and the final update may require a second warmup."},{"when":"Misses recur unpredictably and stale data has defined bounds","use":"Coalesce refreshes, jitter expiries and serve bounded stale content where acceptable.","tradeoff":"Adds coordination and stale data must remain visibly within its contract."}]
checks: ["Send a burst at expiration and assert origin requests stay under the intended bound.","Simulate a failed refresh and verify timeouts, fallback behavior and maximum staleness."]
sources: [{"title":"AWS Builders’ Library on caching","url":"https://aws.amazon.com/builders-library/caching-challenges-and-strategies/"},{"title":"NGINX proxy cache directives","url":"https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache_lock"}]
related: ["cache-invalidation","bounded-concurrency"]
---

<!-- Generated record title. -->
# Cache stampede and prewarming

## Scenario

A university publishes a schedule at a known hour. The first requests would otherwise recompute the same large schedule from the database.

## Failure modes

Identical misses multiply origin queries. Warming too early can publish stale data. Request coalescing is per process unless the coordination boundary covers other instances.

## Explain it simply

Prepare the popular result before the rush and have simultaneous requests share one refresh.

## Implementation guidance

Use the versioned cache key as the single-flight scope. Set a bounded wait for followers and keep ownership and freshness limits explicit across processes. Controlled fallback can serve stale data within the agreed budget after a refresh fails. Observe simultaneous expiry with a delayed or stuck refresher, and verify how a former owner completing after lease expiry is handled.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A predictable event and safe public data** Prewarm versioned content before the surge and set expiry according to staleness policy. Operational timing matters and the final update may require a second warmup.
- **Misses recur unpredictably and stale data has defined bounds** Coalesce refreshes, jitter expiries and serve bounded stale content where acceptable. Adds coordination and stale data must remain visibly within its contract.

## Verification

- Send a burst at expiration and assert origin requests stay under the intended bound.
- Simulate a failed refresh and verify timeouts, fallback behavior and maximum staleness.

## Sources

- [AWS Builders’ Library on caching](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/)
- [NGINX proxy cache directives](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache_lock)

## Related decisions

- [Cache invalidation and freshness budgets](../data/cache-invalidation.md)
- [Bounded concurrency and backpressure](../concurrency/bounded-concurrency.md)

<!-- End generated record details. -->
