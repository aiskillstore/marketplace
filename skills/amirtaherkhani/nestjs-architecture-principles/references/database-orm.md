# Database and ORM Rules

Treat persistence as an owned system boundary. An ORM reduces mapping work; it does not decide data ownership, integrity, transaction scope, or production migration safety.

## Start with the real persistence model

Before changing it, inspect the installed ORM and driver versions, schema and migration history, constraints and indexes, repository/query usage, transaction helpers, connection-pool settings, replica count, and database tests. Identify which feature owns each table or collection and which use case owns each write.

## Ownership and mapping

- A capability owns its writes and invariants. Other features call its application API or consume a deliberately designed read model.
- Do not expose mutable ORM entities as public HTTP, message, or cross-module contracts.
- Map between transport, domain, and persistence shapes only where those boundaries are real; do not create ceremonial copies with no policy difference.
- Keep ORM query builders, decorators, and driver errors in the persistence adapter when the application needs infrastructure independence.
- A repository is optional. Introduce one for a meaningful application boundary, not because every table needs an interface.
- Prefer capability-shaped operations such as `findPayableOrders()` over a generic repository that leaks unrestricted query behavior.

## Migrations

1. Commit and review every production schema change.
2. Generate a migration only as a starting point; inspect the emitted SQL and data effects.
3. Avoid automatic schema synchronization in production.
4. Define who runs migrations and how concurrent replicas are prevented from racing.
5. Use expand-and-contract changes when old and new application versions may overlap.
6. Back up and rehearse recovery for destructive or high-volume changes.
7. Make rollback honest: some data transformations require a forward repair or restore rather than a reversible `down` migration.

Test migrations from a production-like previous schema, not only against a freshly created empty database.

## Transactions and consistency

- Align a transaction with one business invariant or use case, not an entire request by habit.
- Keep transactions short and avoid remote HTTP, broker, email, or file calls while locks are held.
- Pass the transaction-scoped client explicitly so nested operations cannot accidentally use a different connection.
- Choose isolation and retry behavior from observed anomalies and driver semantics.
- Enforce uniqueness, foreign keys, and other critical invariants in the database as well as application code.
- Use an outbox or another atomic publication mechanism when a durable event must correspond to a committed state change.
- Make retried writes and consumers idempotent; a transaction alone does not prevent duplicate external effects.

## Query and pool performance

Diagnose with traces, query logs, plans, lock metrics, and production-like data.

- Detect N+1 behavior by counting and tracing queries. Fix it with an appropriate join, projection, prefetch, or batch loader rather than loading every relation.
- Select only required fields and bound every collection. Use cursor/keyset pagination when deep offsets become the measured problem.
- Add indexes for real predicates, joins, ordering, and data distribution; account for write and storage cost.
- Keep pool wait time visible. Size each instance's pool against the database limit multiplied by the maximum replica count.
- Eliminate leaked clients and unnecessarily long transactions before increasing the pool.
- Cache only after the query is correct and a measured repeated cost justifies staleness and invalidation complexity.

Measured latency optimization belongs to the Features, Scaling, and Performance skill; this reference owns persistence boundaries and integrity.

## Test the boundary

| Risk | Minimum useful test |
| --- | --- |
| Domain/application policy | Unit test with an owned fake or stub |
| ORM mapping and query shape | Integration test against the supported database engine |
| Constraints and transaction behavior | Integration/concurrency test with realistic conflicts |
| Migration | Upgrade test from the previous schema plus representative data |
| Public read/write contract | Transport or contract test through the owning feature |
| Pool/capacity limit | Load test with production-like replica and data assumptions |

Do not use a mock ORM as proof that SQL, indexes, constraints, isolation, or migrations work.

See the official [TypeORM migrations](https://typeorm.io/docs/advanced-topics/migrations/), [TypeORM transactions](https://typeorm.io/docs/advanced-topics/transactions/), [Prisma Migrate](https://www.prisma.io/docs/orm/prisma-migrate), and [Prisma transaction](https://www.prisma.io/docs/orm/prisma-client/queries/transactions) documentation. Verify APIs against the ORM version installed in the target repository.
