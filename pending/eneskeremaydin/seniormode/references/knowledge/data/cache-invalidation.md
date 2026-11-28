---
id: "cache-invalidation"
title: "Cache invalidation and freshness budgets"
category: "data"
summary: "Define when derived cached data is safe to serve and how mutations become visible."
aliases: ["cache invalidation","cache aside","ttl","stale reads","write through","önbellek geçersiz kılma","veri değişince önbelleği yenile","eski veriyi önbellekten okuma"]
decisions: [{"when":"Data is low-risk and bounded staleness suffices","use":"Use cache-aside with an explicit TTL and a scoped key.","tradeoff":"TTL-based cleanup leaves an intentional stale window."},{"when":"A write must be immediately visible to its author","use":"Read the source for that path or use versioned cache keys after commit.","tradeoff":"Stronger freshness costs more source reads and lifecycle complexity."}]
checks: ["Simulate overlapping read, write and refresh with a delayed reader.","Verify staleness bounds, fallback on cache failure and tenant separation."]
sources: [{"title":"AWS Builders’ Library on caching","url":"https://aws.amazon.com/builders-library/caching-challenges-and-strategies/"},{"title":"RFC 9111 HTTP caching","url":"https://www.rfc-editor.org/rfc/rfc9111"}]
related: ["read-your-writes"]
---

<!-- Generated record title. -->
# Cache invalidation and freshness budgets

## Scenario

A directory caches display names for five minutes. A user can rename their own profile and expects the settings screen to show the saved version now.

## Failure modes

Evicting before a database commit can refill old data. Delayed writers can repopulate after eviction. Shared cache keys can leak personalized data.

## Explain it simply

Decide how old cached information may be and make important updates visible through a reliable path.

## Implementation guidance

Order the primary database commit before notifying cache consumers. For a rename, use a primary read or a version-aware key on the edit confirmation path, and let the directory list follow its documented TTL. Include tenant, identity or representation dimensions where the data varies. A delayed refresh with an old version must not supersede a newer value. Exercise the interleaving where an earlier read completes after the rename commits.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Data is low-risk and bounded staleness suffices** Use cache-aside with an explicit TTL and a scoped key. TTL-based cleanup leaves an intentional stale window.
- **A write must be immediately visible to its author** Read the source for that path or use versioned cache keys after commit. Stronger freshness costs more source reads and lifecycle complexity.

## Verification

- Simulate overlapping read, write and refresh with a delayed reader.
- Verify staleness bounds, fallback on cache failure and tenant separation.

## Sources

- [AWS Builders’ Library on caching](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/)
- [RFC 9111 HTTP caching](https://www.rfc-editor.org/rfc/rfc9111)

## Related decisions

- [Replica lag and read-your-writes](read-your-writes.md)

<!-- End generated record details. -->
