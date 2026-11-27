# Data and storage

- [Cache invalidation and freshness budgets](../knowledge/data/cache-invalidation.md) · Define when derived cached data is safe to serve and how mutations become visible.
- [Composite indexes for access patterns](../knowledge/data/composite-indexes.md) · Design database indexes around actual filters, sorting, selectivity and write costs.
- [End-to-end data retention and deletion](../knowledge/data/data-retention.md) · Define where an entity's data lives and how authorized deletion propagates to derived copies.
- [Exact money values and rounding boundaries](../knowledge/data/decimal-money.md) · Store monetary values without binary floating-point drift or ambiguous rounding.
- [SQLite or a database server](../knowledge/data/embedded-database-choice.md) · Choose local embedded storage or a server according to writer coordination and deployment requirements.
- [Search index freshness and recoverability](../knowledge/data/index-freshness.md) · Manage search as a derived view with measurable lag and a repeatable rebuild path.
- [Inverted index for text search](../knowledge/data/inverted-index.md) · Build text retrieval around term postings, query semantics and the freshness of the index.
- [LRU cache eviction and admission](../knowledge/data/lru-cache.md) · Choose an eviction policy by comparing access locality, memory cost and workload skew.
- [Object retention and deletion lifecycle](../knowledge/data/object-storage-lifecycle.md) · Express how object versions are retained, restored and ultimately removed.
- [Replica lag and read-your-writes](../knowledge/data/read-your-writes.md) · Choose a read routing strategy that makes a user's own successful writes visible when required.
- [Transaction isolation for cross-row invariants](../knowledge/data/transaction-isolation.md) · Pick isolation or explicit locking based on the anomaly that would break a business invariant.
- [Expand-and-contract schema changes](../knowledge/data/zero-downtime-migrations.md) · Evolve persistent schemas while applications and backfills continue to work.
