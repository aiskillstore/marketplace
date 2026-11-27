# Software architecture

- [Batch processing versus streaming](../knowledge/architecture/batch-versus-streaming.md) · Match processing cadence to business freshness, event order and recovery needs.
- [Sharding and consistent hashing](../knowledge/architecture/consistent-hashing.md) · Assign keys to changing storage or worker sets while limiting unnecessary movement.
- [Small dependency seams for testable policies](../knowledge/architecture/dependency-injection-seam.md) · Separate deterministic decisions from time, persistence and external calls where the distinction pays for itself.
- [Timeline delivery and fan-out](../knowledge/architecture/feed-fanout.md) · Balance write amplification, read latency and fan-out lag for a personalized feed.
- [Modular monolith or independent service](../knowledge/architecture/modular-monolith.md) · Choose a deployment boundary according to ownership, failure isolation and operational constraints.
- [Module boundaries around business rules](../knowledge/architecture/module-boundaries.md) · Put stable policies in testable modules where real responsibilities and callers justify the boundary.
- [Offline synchronization and conflict resolution](../knowledge/architecture/offline-sync-conflicts.md) · Design synchronization around missing connectivity, concurrent edits and explicit conflict semantics.
- [Transactional outbox and reliable delivery](../knowledge/architecture/transactional-outbox.md) · Publish domain changes without a race between a database transaction and a separate message broker.
