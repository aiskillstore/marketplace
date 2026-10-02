---
name: database-guardrails
description: "Plans database-backed changes with an ask-first safety gate, minimal schema growth, programmatic versioned migrations, and evidence-based indexes. Use for database modeling, schema changes, migrations, data repair, or database performance work; do not access or change a database by default."
---

# Database guardrails

Treat database work as a gated design conversation. A request to add persistence
or change a model is not permission to connect to, inspect, or mutate a live
database.

## Hard stop before database access

Unless the user explicitly authorizes the exact target, operation, and scope:

- Do not open a database connection, issue a query, inspect a live database,
  run a migration, seed data, reset or dump a database, or run tests that write
  to a real database.
- Do not infer permission from a general request such as “add a database” or
  “fix the data.” Keep the work at repository code, schema files, migration
  history, documentation, or synthetic/disposable fixtures.
- If the environment, owner, data sensitivity, or allowed side effects are
  unclear, stop and ask. Say explicitly that no database action has been taken.

## Converse before designing the schema

Before proposing tables or columns, make the behavior concrete and ask about:

1. The one user-visible or service-level use case being supported first.
2. The target database and environment, who owns it, and whether this is a
   fresh install, an upgrade, or a repair.
3. Existing schema and migration ownership, data-retention requirements, and
   compatibility with current callers.
4. Identity, nullability, units and precision, time zones, authorization,
   concurrency, transaction boundaries, and recovery expectations.
5. Whether any backfill, data rewrite, destructive change, or downtime is
   actually authorized.

Explain why the current schema or persistence boundary is insufficient before
proposing a change. Then show the smallest design: only the necessary tables,
columns, types, defaults, relationships, and constraints. Start with one
bounded workflow and increase the model only when a concrete requirement or
measured failure justifies it.

Use constraints to protect real invariants: primary keys, foreign keys,
uniqueness, nullability, checks, and valid state transitions. Do not add
speculative audit/event tables, soft-delete flags, tenants, generic entity-value
models, JSON escape hatches, or lookup tables merely because they might be
useful later.

## Index only for a reason

Every index must have a named query, join, uniqueness rule, ordering/filter
path, or measured performance problem behind it. Record the reason and expected
selectivity. Do not index every column, every foreign key automatically, or
duplicate an existing prefix/covering index. Re-check write cost, storage,
cardinality, and the query plan before keeping an index that is not required by
a constraint or demonstrated access path.

## Make changes programmatically and incrementally

- If the project has a migration system, use its programmatic, versioned,
  reviewed migration mechanism and the repository's normal command to run it.
- If the project does not support that mechanism, write a scoped migration
  program/file and its dry-run, recovery, and execution instructions into the
  project first. Do not improvise SQL in a terminal or GUI and do not execute
  an unreviewed artifact from chat.
- Keep migrations separate from application startup. Never silently create,
  reset, seed, or repair schema on boot, and never edit an already-applied
  migration; add a new migration instead.
- Preserve existing data and relationships. Plan transaction boundaries,
  locking, retries, idempotency, backfills, precision, and rollback before an
  authorized run. Prefer additive, reversible steps and expand later in a
  separate change.

## Verify and report

Before an authorized run, verify the exact target, backup/recovery path, and
the disposable fresh-install and upgrade tests. Afterward, report the commit,
artifact, target, changed tables/columns/constraints/indexes, checks run, and
rollback path. Keep the response structured as: known facts, minimal proposal,
open questions, migration artifact, approval needed, and database actions taken.
