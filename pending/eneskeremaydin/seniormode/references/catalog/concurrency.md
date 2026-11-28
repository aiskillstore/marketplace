# Concurrency and coordination

- [Atomic file replacement and recovery](../knowledge/concurrency/atomic-file-replacement.md) · Publish complete local files while accounting for concurrency, durability and platform semantics.
- [Bounded concurrency and backpressure](../knowledge/concurrency/bounded-concurrency.md) · Bound in-flight work and queue growth when producers are faster than downstream resources.
- [Event ordering and versioned consumers](../knowledge/concurrency/event-ordering.md) · Preserve the ordering boundary that matters to correctness while allowing unrelated work to proceed.
- [Leases and fencing tokens](../knowledge/concurrency/lease-fencing.md) · Protect shared state from a worker that continues after losing a lease or being replaced.
- [Concurrent text editing and position transforms](../knowledge/concurrency/operational-transformation.md) · Preserve concurrent editing intent by applying versioned positions and explicit conflict rules.
- [Optimistic concurrency and version checks](../knowledge/concurrency/optimistic-concurrency.md) · Detect conflicting edits using a version check and explicit conflict handling at the write boundary.
- [Idempotent payments and retry identity](../knowledge/concurrency/payment-idempotency.md) · Preserve one durable financial effect per payment intent despite timeouts, retries and concurrent submissions.
- [Concurrent reservations and expiring holds](../knowledge/concurrency/reservation-concurrency.md) · Preserve one owner for a scarce time slot while payment or confirmation is asynchronous.
- [Sharded counters for write-heavy metrics](../knowledge/concurrency/sharded-counter.md) · Distribute high-volume increments while being explicit about aggregate freshness and duplication.
