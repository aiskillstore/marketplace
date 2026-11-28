---
id: "sharded-counter"
title: "Sharded counters for write-heavy metrics"
category: "concurrency"
summary: "Distribute high-volume increments while being explicit about aggregate freshness and duplication."
aliases: ["sharded counter","hot counter","view count","parçalı sayaç","write contention","izlenme sayacını parçalara bölme","yoğun yazmada sayaç satırı kilitleniyor","dağıtık sayaç toplamı"]
decisions: [{"when":"Bursty writes dominate and approximate freshness is acceptable","use":"Increment partitioned counters and project their aggregate on a schedule.","tradeoff":"Reads become cheaper but the displayed total is temporarily stale."},{"when":"An exact current balance is a correctness invariant","use":"Use a transactional ledger or a serialized update with retry and exact reads.","tradeoff":"Throughput is bounded by the write coordination boundary."}]
checks: ["Stress concurrent increments and verify final aggregate equals accepted events.","Retry deliveries and change shard count without losing previously written totals."]
sources: [{"title":"Firestore distributed counters","url":"https://firebase.google.com/docs/firestore/solutions/counters"},{"title":"PostgreSQL explicit locking","url":"https://www.postgresql.org/docs/current/explicit-locking.html"}]
---

<!-- Generated record title. -->
# Sharded counters for write-heavy metrics

## Scenario

A community poll counts nonbinding page views during a festival. A single database row begins to queue writes during bursts.

## Failure modes

Reading all shards per request shifts the bottleneck to reads. Retried events can inflate totals and changing shard counts needs a compatible aggregation path.

## Explain it simply

Spread updates across several buckets and periodically add the buckets together for display.

## Implementation guidance

Pick the write shard from a stable event identity when retries can land on different workers. Deduplicate logical events if accuracy matters. A read projection trades consolidation work and staleness for faster requests. Define how readers and writers coexist while shard count changes so neither layout is counted twice. Use an exact ledger instead when the value governs a balance or entitlement that callers must read atomically.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Bursty writes dominate and approximate freshness is acceptable** Increment partitioned counters and project their aggregate on a schedule. Reads become cheaper but the displayed total is temporarily stale.
- **An exact current balance is a correctness invariant** Use a transactional ledger or a serialized update with retry and exact reads. Throughput is bounded by the write coordination boundary.

## Verification

- Stress concurrent increments and verify final aggregate equals accepted events.
- Retry deliveries and change shard count without losing previously written totals.

## Sources

- [Firestore distributed counters](https://firebase.google.com/docs/firestore/solutions/counters)
- [PostgreSQL explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html)

<!-- End generated record details. -->
