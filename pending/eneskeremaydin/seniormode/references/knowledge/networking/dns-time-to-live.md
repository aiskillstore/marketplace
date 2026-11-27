---
id: "dns-time-to-live"
title: "DNS TTL and service cutover"
category: "networking"
summary: "Plan a DNS change around resolver caches, connection reuse and reversible origin transitions."
aliases: ["dns ttl","dns migration","record propagation","negative caching","service cutover","DNS kaydı değişikliği yayılma süresi","eski IP adresi önbellekte","alan adı geçişi"]
decisions: [{"when":"A migration can be planned and both origins can operate","use":"Lower TTL well ahead, keep both endpoints compatible and compare traffic before retiring the old one.","tradeoff":"Operating two origins adds temporary cost and synchronization needs."},{"when":"Endpoint ownership and routing can be controlled without DNS churn","use":"Change traffic behind a stable load balancer and use DNS for the stable boundary.","tradeoff":"The load balancer becomes an operational dependency."}]
checks: ["Measure resolver behavior from representative locations during a dry run.","Test failback with stale records and preexisting connections."]
sources: [{"title":"RFC 1034 Domain Names","url":"https://www.rfc-editor.org/rfc/rfc1034"},{"title":"RFC 2308 DNS negative caching","url":"https://www.rfc-editor.org/rfc/rfc2308"},{"title":"RFC 8767 serving stale DNS data","url":"https://www.rfc-editor.org/rfc/rfc8767.html"}]
---

<!-- Generated record title. -->
# DNS TTL and service cutover

## Scenario

A service moves to a new endpoint. Some clients may continue reaching the old origin after the record is updated.

## Failure modes

A lower TTL cannot shorten records already cached. Negative caching and long-lived connections can delay recovery or rollback.

## Explain it simply

Keep both endpoints working during the move because some clients remember the old address for a while.

## Implementation guidance

Before a cutover, lower the relevant TTL early enough for cached records with the old TTL to expire and plan for cached negative lookups. TTL governs normal cache freshness. A resolver that implements serve-stale may return expired data when it cannot refresh its answer, and an existing connection can outlive any DNS cache entry. Keep both endpoints contract-compatible while clients migrate and monitor actual traffic reaching each. Test a resolver still holding the old answer, an upstream lookup failure and a client with a reused connection before retiring the old origin.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A migration can be planned and both origins can operate** Lower TTL well ahead, keep both endpoints compatible and compare traffic before retiring the old one. Operating two origins adds temporary cost and synchronization needs.
- **Endpoint ownership and routing can be controlled without DNS churn** Change traffic behind a stable load balancer and use DNS for the stable boundary. The load balancer becomes an operational dependency.

## Verification

- Measure resolver behavior from representative locations during a dry run.
- Test failback with stale records and preexisting connections.

## Sources

- [RFC 1034 Domain Names](https://www.rfc-editor.org/rfc/rfc1034)
- [RFC 2308 DNS negative caching](https://www.rfc-editor.org/rfc/rfc2308)
- [RFC 8767 serving stale DNS data](https://www.rfc-editor.org/rfc/rfc8767.html)

<!-- End generated record details. -->
