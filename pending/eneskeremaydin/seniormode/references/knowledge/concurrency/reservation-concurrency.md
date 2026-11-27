---
id: "reservation-concurrency"
title: "Concurrent reservations and expiring holds"
category: "concurrency"
summary: "Preserve one owner for a scarce time slot while payment or confirmation is asynchronous."
aliases: ["double booking","pessimistic locking","inventory hold","çifte rezervasyon","room reservation","son odayı aynı anda ayırtma","aynı yer için iki rezervasyon","süreli yer tutma","son odayı aynı anda ayırtıyor"]
decisions: [{"when":"Inventory has a row with a predictable owner","use":"Use a short transaction with a row lock or a guarded state transition, then persist a lease expiry.","tradeoff":"Hot slots can serialize and the expiry worker must be idempotent."},{"when":"The resource is naturally identified by a unique key","use":"Use a unique constraint and an atomic claim with a bounded retry policy.","tradeoff":"Losers must receive an explicit conflict, and leased claims still need expiry."}]
checks: ["Race two independent connections and assert at most one active claim.","Deliver a confirmation after expiration and verify it cannot revive a released slot."]
sources: [{"title":"PostgreSQL explicit locking","url":"https://www.postgresql.org/docs/current/explicit-locking.html"},{"title":"PostgreSQL constraints","url":"https://www.postgresql.org/docs/current/ddl-constraints.html"}]
related: ["payment-idempotency","optimistic-concurrency"]
---

<!-- Generated record title. -->
# Concurrent reservations and expiring holds

## Scenario

Two volunteers request the last rehearsal room at the same time and can take two minutes to confirm. Only one confirmation should succeed.

## Failure modes

A read followed by an unguarded insert can double-book. Holding a database lock during payment creates contention and cleanup risk. A late payment callback may arrive after expiration.

## Explain it simply

Reserve the slot briefly for one person and release it if their confirmation never arrives.

## Implementation guidance

For a room/night inventory row, reserve it with one guarded database change or uniqueness constraint and persist the claimant and expiry. Keep asynchronous payment outside the critical section. An expiry job and confirmation callback should each require the current hold identity, so an old callback cannot confirm a newly rented slot. Compare exact-slot bookings with overlapping date ranges, as separate room/night uniqueness does not model a range booking without claiming each affected night atomically.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Inventory has a row with a predictable owner** Use a short transaction with a row lock or a guarded state transition, then persist a lease expiry. Hot slots can serialize and the expiry worker must be idempotent.
- **The resource is naturally identified by a unique key** Use a unique constraint and an atomic claim with a bounded retry policy. Losers must receive an explicit conflict, and leased claims still need expiry.

## Verification

- Race two independent connections and assert at most one active claim.
- Deliver a confirmation after expiration and verify it cannot revive a released slot.

## Sources

- [PostgreSQL explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html)
- [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)

## Related decisions

- [Idempotent payments and retry identity](payment-idempotency.md)
- [Optimistic concurrency and version checks](optimistic-concurrency.md)

<!-- End generated record details. -->
