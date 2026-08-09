---
name: neon-postgres
description: >-
  Guides and best practices for working with Lakebase Postgres, the database
  behind Neon. Covers setup, connection methods and drivers, pooled vs direct
  connections, branching, schema migrations, autoscaling, scale-to-zero, instant
  restore, read replicas, connection pooling, IP allow lists, and logical
  replication.
  Use when users ask about "Lakebase Postgres", "Neon setup", "connect to Neon",
  "Neon project", "DATABASE_URL", "serverless Postgres", "Neon CLI", "neon", "Neon MCP",
  "Neon Auth", "@neondatabase/serverless", "@neondatabase/neon-js",
  "scale to zero", "Neon autoscaling", "Neon read replica",
  "Neon connection pooling", or "schema migrations".
metadata:
  parent: neon
---

**FIRST**: Use the parent `neon` skill for a Neon overview, getting started with Neon, Neon development best practices, and more.

If the `neon` skill is not installed, fetch it from https://neon.com/docs/ai/skills/neon/SKILL.md or install it with:

```bash
npx skills add neondatabase/agent-skills --skill neon
```

# Lakebase Postgres

Lakebase Postgres is the database at the core of Neon. It runs on the lakebase architecture — OLTP built directly on cloud object storage — which decouples storage from compute to offer autoscaling, branching, instant restore, and scale-to-zero. It's fully compatible with Postgres and works with any language, framework, or ORM that supports Postgres.

It is the same database whether you reach it through Neon or through Databricks; this skill covers the Neon access path.

## Setup Flow

### 1. Select the organization and project

Use the CLI (default) or MCP server to list organizations and projects. Let the user select an existing project or create a new one. Check the `.neon` file for an existing linked project or branch.

### 2. Get the connection string

Use the CLI (default), `neon env pull`, or the MCP server to get the connection string. Store it in `.env` as `DATABASE_URL`. Read the file first before modifying it, to avoid overwriting existing values.

#### When to use pooled vs direct connections

| Use case                                 | Connection type  |
| ---------------------------------------- | ---------------- |
| Web applications, serverless functions   | Pooled (-pooler) |
| Schema migrations                        | Direct           |
| pg_dump / pg_restore                     | Direct           |
| Logical replication                      | Direct           |
| Long-running analytics with temp tables  | Direct           |
| Admin tasks needing SET or session state | Direct           |
| LISTEN / NOTIFY                          | Direct           |

### 3. Pick the connection method and driver

Always pair Neon with an ORM such as **Drizzle** for easy schema management and migrations. Refer to the connection methods guide to pick the correct driver based on how the runtime treats your code: https://neon.com/docs/connect/choose-connection.md.

Recommendations:

- Drizzle as ORM (see https://neon.com/docs/guides/drizzle.md)
- On Vercel, use `node-postgres` (`npm install pg`) with Vercel Fluid compute and `import { attachDatabasePool } from "@vercel/functions";`
- On Cloudflare, use `node-postgres` with Cloudflare Hyperdrive
- On Neon Functions, use `node-postgres`, as the functions are long-running and reuse the pool across requests.
- Use the `@neondatabase/serverless` driver for serverless and edge environments (for example, when using Netlify) — HTTP transport for one-shot queries, WebSocket for transaction support. Link: https://neon.com/docs/serverless/serverless-driver.md

### 4. Set up the schema

Manage schemas and migrations as code. Avoid running ad hoc schema migrations against your database, since they're hard to manage.

If you're using an ORM, follow your ORM's best practices to manage schemas and migrations. For example, if using Drizzle, only use Drizzle for schema and migration management unless instructed otherwise.

## Branching

Use this when the user is planning isolated environments, schema migration testing, preview deployments, or branch lifecycle automation.

Key points:

- Branches are instant, copy-on-write clones (no full data copy).
- Each branch has its own compute endpoint.
- Use the neon CLI or MCP server to create, inspect, and compare branches.

Link: https://neon.com/docs/introduction/branching.md

For detailed branch creation workflows (normal vs schema-only branches, reset-from-parent, CLI/MCP selection), use the `neon-postgres-branches` skill. If it isn't installed, fetch it from https://neon.com/docs/ai/skills/neon-postgres-branches/SKILL.md or install it with:

```bash
npx skills add neondatabase/agent-skills --skill neon-postgres-branches
```

## Migrations

Test a migration on a branch of production, against production-like data, before applying it to production.

Use a **direct (non-pooled)** connection string when you run the migration, not a pooled one. `neon connection-string` returns the direct string by default; make sure the hostname does not include the `-pooler` suffix.

## Autoscaling

Use this when the user needs compute to scale automatically with workload and wants guidance on CU sizing and runtime behavior.

Link: https://neon.com/docs/introduction/autoscaling.md

## Scale to Zero

Use this when optimizing idle costs and discussing suspend/resume behavior, including cold-start trade-offs.

Key points:

- Idle computes suspend automatically after a default of 5 minutes; the timeout is configurable, and suspension can only be disabled on the Launch and Scale plans.
- First query after suspend typically has a cold-start penalty (around hundreds of ms)
- Storage remains active while compute is suspended.

Link: https://neon.com/docs/introduction/scale-to-zero.md

## Instant Restore

Use this when the user needs point-in-time recovery or wants to restore data state without traditional backup restore workflows.

Key points:

- History windows for instant restore depend on plan limits.
- Users can create branches from historical points-in-time.
- Time Travel queries can be used for historical inspection workflows.

Link: https://neon.com/docs/introduction/branch-restore.md

## Read Replicas

Use this for read-heavy workloads where the user needs dedicated read-only compute without duplicating storage.

Key points:

- Replicas are read-only compute endpoints sharing the same storage.
- Creation is fast and scaling is independent from primary compute.
- Typical use cases: analytics, reporting, and read-heavy APIs.

Link: https://neon.com/docs/introduction/read-replicas.md

## Connection Pooling

Use this when the user is in serverless or high-concurrency environments and needs safe, scalable Postgres connection management.

Key points:

- Neon pooling uses PgBouncer.
- Add `-pooler` to endpoint hostnames to use pooled connections.
- Pooling is especially important in serverless runtimes with bursty concurrency.

Link: https://neon.com/docs/connect/connection-pooling.md

## IP Allow Lists

Use this when the user needs to restrict database access by trusted networks, IPs, or CIDR ranges.

Link: https://neon.com/docs/introduction/ip-allow.md

## Logical Replication

Use this when integrating CDC pipelines, external Postgres sync, or replication-based data movement.

Key points:

- Neon supports native logical replication workflows.
- Useful for replicating to/from external Postgres systems.

Link: https://neon.com/docs/guides/logical-replication-guide.md

## Gotchas

### Pooled vs direct connections: use the direct URL for migrations, dumps, and replication

Neon gives you two connection strings for the same database: a **pooled** one (hostname with the `-pooler` suffix) and a **direct/unpooled** one (no `-pooler` suffix). `neon env pull` writes them as `DATABASE_URL` and `DATABASE_URL_UNPOOLED`. The pooled connection routes through PgBouncer in transaction mode, which doesn't support session-level operations. Choose the right one:

- **Pooled (`DATABASE_URL`)** — your application's normal query traffic, especially serverless and connection-per-request workloads.
- **Direct (`DATABASE_URL_UNPOOLED`)** — schema migrations (Prisma Migrate, Drizzle Kit, Alembic, and others), `pg_dump` / `pg_restore`, logical replication, `LISTEN`/`NOTIFY`, and anything relying on `SET` or other session state.

Running migrations, dumps, or replication over the pooled connection can fail, and never in a way that names pooling: `prepared statement "s0" already exists` from Prisma Migrate, a `SET search_path` that doesn't persist past its own transaction so the next query reports `relation "mytable" does not exist`, or a write intermittently hitting a read-only transaction (`SQLSTATE 25006`) that a pooled backend inherited from an earlier client. Migration tools generally take both strings at once — Prisma's `directUrl` alongside `url` — so point that at the direct one rather than swapping `DATABASE_URL` and losing pooling for the application. See https://neon.com/docs/connect/connection-pooling.md.
