# Data and storage

Name the source of truth, uniqueness constraints, references, and lifetimes. Store invariants the database can enforce as constraints or guarded operations. Separate derived indexes, caches, and reporting views from the authoritative data and define rebuilding, freshness, and failure behavior.

Choose transactions for invariants spanning related writes. Test coordination with independent connections when possible. Design indexes against predicates and stable sort order, and check the query plan at representative cardinality.

For an existing database, define backward-compatible deployment, backfill, read/write switch, and rollback behavior. A large schema change may need a phased migration. Verify old rows, mixed application versions, failed migrations, and the required invariant. Use [migration guidance](../knowledge/data/zero-downtime-migrations.md) for the applicable rollout.
