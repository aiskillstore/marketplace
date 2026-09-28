---
name: turbo-pipelines
description: "Turbo pipeline YAML reference and architecture guide. Covers: YAML field syntax (start_at, from, version, primary_key), source/transform/sink configuration, validation errors, resource sizing (xs–xxl), architecture decisions (dataset vs kafka, streaming vs job, fan-out vs fan-in, sink selection, pipeline splitting). Triggers on: 'what does field X do', 'what fields does a postgres sink need', 'what resource size', 'should I use kafka or dataset', 'how to structure my pipeline'. For writing transforms, use /turbo-transforms. For end-to-end building, use /turbo-builder."
---

# Turbo Pipeline Configuration & Architecture

YAML configuration reference and architecture guide for Turbo pipelines. For interactive pipeline building, use `/turbo-builder`. For troubleshooting, use `/turbo-doctor`. For transform implementation, use `/turbo-transforms`.

> **CRITICAL:** Always validate YAML with `goldsky turbo validate <file.yaml>` before showing complete pipeline YAML to the user or deploying.

---

## Quick Start

```yaml
name: my-first-pipeline
resource_size: s
sources:
  transfers:
    type: dataset
    dataset_name: base.erc20_transfers
    version: 1.2.0
    start_at: latest
transforms: {}
sinks:
  output:
    type: blackhole
    from: transfers
```

```bash
goldsky turbo validate pipeline.yaml   # Validate first
goldsky turbo apply pipeline.yaml -i   # Deploy + inspect
```

## Prerequisites

- **Goldsky CLI** — `curl https://goldsky.com | sh`
- **Turbo extension** (separate binary) — `curl https://install-turbo.goldsky.com | sh`
- **Logged in** — `goldsky login`
- Secrets created for sinks if using PostgreSQL, ClickHouse, Kafka, etc. (see `/secrets`)

---

## Architecture Decisions

### Source Type Selection

| Scenario                          | Source Type | Why                                          |
| --------------------------------- | ----------- | -------------------------------------------- |
| Decode contract events from logs  | `dataset`   | Need `raw_logs` + `_gs_log_decode()`         |
| Track token transfers             | `dataset`   | `erc20_transfers` has structured data        |
| Historical backfill + live        | `dataset`   | `start_at: earliest` processes history       |
| Live token balances               | `kafka`     | `latest_balances_v2` is a streaming topic    |
| Real-time state snapshots         | `kafka`     | Kafka delivers latest state continuously     |
| Only need new data going forward  | Either      | Dataset with `start_at: latest` or Kafka     |

> **Note:** Kafka sources are used in production but are not documented in official Goldsky docs. Contact Goldsky support for topic names.

### Data Flow Patterns

| Pattern              | When to Use                                          | Template                           |
| -------------------- | ---------------------------------------------------- | ---------------------------------- |
| **Linear**           | Single source, single destination, simple processing | `templates/linear-pipeline.yaml`   |
| **Fan-out**          | One source → multiple sinks (different views/subsets)| `templates/fan-out-pipeline.yaml`  |
| **Fan-in**           | Multiple event types → UNION ALL → one table         | `templates/fan-in-pipeline.yaml`   |
| **Multi-chain**      | Same logic across chains (separate pipelines)        | `templates/multi-chain-templated.yaml` |

For detailed pattern diagrams, YAML examples, and multi-chain deployment guidance, read `references/architecture-patterns.md`.

### Resource Sizing

| Size  | Workers | CPU   | Memory  | When to Use                                                      |
| ----- | ------- | ----- | ------- | ---------------------------------------------------------------- |
| `xs`  | —       | 0.4   | 0.5 Gi  | Small datasets, light testing                                    |
| `s`   | 1       | 0.8   | 1.0 Gi  | Simple filters, single source/sink, low volume (default)         |
| `m`   | 4       | 1.6   | 2.0 Gi  | Multiple sinks, Kafka streaming, moderate transform complexity   |
| `l`   | 10      | 3.2   | 4.0 Gi  | Multi-event decoding + UNION ALL, high-volume backfill           |
| `xl`  | 20      | 6.4   | 8.0 Gi  | Large chain backfills, complex JOINs                             |
| `xxl` | 40      | 12.8  | 16.0 Gi | Highest throughput; up to 6.3M rows/min                          |

Start small and scale up — defensive sizing avoids wasted resources.

**`resource_size` sizes the pipeline, not the sink — they are independent.** An `l`/`xl` pipeline pointed at an undersized destination produces the "deployed but writing nothing" shape: it validates, deploys, reports `Running`, and then fails every write. A Neon free tier (512 MB) will not hold a multi-month backfill of a high-volume chain — it errors `could not extend file because project size limit (512 MB) has been exceeded` and checkpoints time out. Check the destination's storage ceiling against the backfill scope (the start position plus any end bound) before deploying, not after.

### Sink Selection

| Destination          | Sink Type            | Best For                                       |
| -------------------- | -------------------- | ---------------------------------------------- |
| Application DB       | `postgres`           | Row-level lookups, joins, application serving  |
| Real-time aggregates | `postgres_aggregate` | Balances, counters, running totals via triggers|
| MySQL-compatible DB  | `mysql`              | Existing MySQL stacks, upserts on primary key  |
| Analytics queries    | `clickhouse`         | Large-scale aggregations, time-series data     |
| Event processing     | `kafka`              | Downstream consumers, event-driven systems     |
| AWS messaging        | `sqs_sink`           | Decoupled AWS consumers (standard queues only) |
| GCP messaging        | `pubsub`             | Google Cloud Pub/Sub topics (Turbo-only)       |
| Serverless streaming | `s2_sink`            | S2.dev streams, alternative to Kafka           |
| Notifications        | `webhook`            | Lambda functions, API callbacks, alerts        |
| Data lake            | `s3_sink`            | Long-term archival, batch processing           |
| Testing              | `blackhole`          | Validate pipeline without writing data         |

For full sink field specifications, see [Sinks](https://docs.goldsky.com/turbo-pipelines/sinks/overview) in the docs (one page per sink type).

### Streaming vs Job Mode

| Scenario                             | Mode        | Why                                            |
| ------------------------------------ | ----------- | ---------------------------------------------- |
| Real-time dashboard                  | Streaming   | Continuous updates needed                      |
| Backfill 6 months of history         | Job         | One-time, stops when done                      |
| Real-time + catch-up on deploy       | Streaming   | `start_at: earliest` does backfill then streams|
| Export data to S3 once               | Job         | No need for continuous processing              |
| Webhook notifications on events      | Streaming   | Needs to react as events happen                |
| Load test with historical data       | Job         | Process and inspect, then discard              |

**Job mode rules:** Runs to completion, auto-deletes ~1hr after finishing. Must delete before redeploying. Cannot pause/resume/restart.

### Pipeline Splitting

**Default to one pipeline with multiple sinks** when the user wants the same source data sent to multiple destinations. A single Turbo pipeline supports multiple sinks natively — each sink has a `from:` field pointing at a source or transform by name, and sinks run independently (one failing does not block the others, and each can have its own `batch_size` / `batch_flush_interval`).

**Do NOT split into separate pipelines just because there are multiple destinations.** Generating one pipeline per sink duplicates the source ingestion, wastes resources, and decouples deployments that should be atomic.

**Split into multiple pipelines only when:** sources are fundamentally different (different chains with independent lifecycles), the destinations need different resource sizes, or the user explicitly asks for separate pipelines.

See `references/architecture-patterns.md` for fan-out (one source → multiple sinks) and fan-in (UNION ALL) YAML examples, and `templates/multi-sink-pipeline.yaml` / `templates/fan-out-pipeline.yaml` / `templates/fan-in-pipeline.yaml` for ready-to-adapt configs.

---

## Configuration Reference

### Pipeline Structure

```yaml
name: my-pipeline          # Required: unique identifier (lowercase, hyphens)
resource_size: s            # Required: xs/s/m/l/xl/xxl
job: true                   # Optional: one-time batch (default: false = streaming)

sources:
  source_name:
    type: dataset           # or: kafka
    # ... source config

transforms:                 # Optional
  transform_name:
    type: sql               # or: script, handler, dynamic_table
    # ... transform config

sinks:
  sink_name:
    type: postgres           # or: clickhouse, kafka, webhook, s3_sink, etc.
    # ... sink config
```

### Source Configuration

#### Dataset Source

```yaml
sources:
  my_source:
    type: dataset
    dataset_name: <chain>.<dataset_type>
    version: <version>
    start_at: latest | earliest    # EVM, NEAR, Bitcoin, Stellar
    # start_block: <slot_number>   # Solana only — omit to start at the latest slot
    # end_block: <block_number>    # Solana only: bounded backfill (ignored on EVM)
    # filter: >-                   # Optional: SQL WHERE for source-level pre-filtering
    #   address = '0x...' AND block_number >= 10000000
```

| Field          | Required | Description                                              |
| -------------- | -------- | -------------------------------------------------------- |
| `type`         | Yes      | `dataset` for blockchain data                            |
| `dataset_name` | Yes      | Format: `<chain>.<dataset_type>`                         |
| `version`      | Yes      | Dataset version (e.g., `1.2.0`)                          |
| `start_at`     | EVM-family | `latest` or `earliest`; on Stellar also a ledger sequence number. Used by EVM, NEAR, Bitcoin, Stellar. Omitted = `earliest` = full chain history |
| `start_block`  | No       | Solana only: starting slot. Omitted = latest slot, i.e. no backfill      |
| `end_block`    | No       | Solana only: stop at this slot. Silently ignored on EVM                  |
| `filter`       | No       | SQL WHERE clause — pre-filters at ingestion (efficient)  |

Use `filter` for contract addresses and block ranges (coarse pre-filtering). Use transform `WHERE` for fine-grained filtering.

Set the start position explicitly on every dataset source, and say which one you chose. On the `start_at` chains (EVM, NEAR, Bitcoin, Stellar) omitting it does not mean "start now": the backend starts from the earliest available data, so the pipeline backfills the full chain history — days of replay and millions of rows before it reaches live data, and the sink has to hold all of it. A block number is not a valid `start_at` value; bound an EVM range with a `block_number` predicate in `filter` (pre-applied at the source), plus `job: true` for a one-shot backfill — `end_block` is silently ignored on EVM. Solana is the opposite default: it uses the numeric `start_block`, and omitting that starts at the latest slot, so a Solana backfill is always something you asked for — bound it with `end_block` or `block_ranges`.

For chain prefixes and dataset types, see `/datasets`.

#### Kafka Source

```yaml
sources:
  my_source:
    type: kafka
    topic: base.raw.latest_balances_v2
```

No `start_at` or `version` fields. Optional: `filter`, `include_metadata`, `starting_offsets`.

### Transform Configuration

| Type            | Use Case                                       |
| --------------- | ---------------------------------------------- |
| `sql`           | Filtering, projections, SQL functions          |
| `script`        | Custom TypeScript/WASM logic                   |
| `handler`       | Call external HTTP APIs to enrich              |
| `dynamic_table` | Lookup tables backed by a database             |
| `throttle`      | Cap throughput to a fixed records-per-second   |

#### SQL Transform

```yaml
transforms:
  filtered:
    type: sql
    primary_key: id
    sql: |
      SELECT id, sender, recipient, amount
      FROM source_name
      WHERE amount > 1000
```

| Field         | Required | Description                            |
| ------------- | -------- | -------------------------------------- |
| `type`        | Yes      | `sql`                                  |
| `primary_key` | Yes      | Column for uniqueness/ordering         |
| `sql`         | Yes      | SQL query (reference sources by name)  |
| `from`        | No       | Override default source (for chaining) |

#### Transform Chaining

Chain transforms using `from`:

```yaml
transforms:
  step1:
    type: sql
    primary_key: id
    sql: SELECT * FROM source WHERE amount > 100
  step2:
    type: sql
    primary_key: id
    from: step1
    sql: SELECT *, 'processed' as status FROM step1
```

For TypeScript, handler, and dynamic table transforms, see `/turbo-transforms`.

#### Throttle Transform

Caps the throughput of a stream by buffering records into batches and emitting each batch on a fixed minimum interval. Throttle does **not** modify data — every input record passes through unchanged. Use it to stay under rate limits of downstream sinks or external APIs, smooth bursty sources, or pace records into HTTP handlers.

```yaml
transforms:
  throttled:
    type: throttle
    from: my_source
    max_batch_size: 100
    min_batch_interval: 10s
```

| Field                | Required | Description                                                  |
| -------------------- | -------- | ------------------------------------------------------------ |
| `type`               | Yes      | `throttle`                                                   |
| `from`               | Yes      | Source or transform to read from                             |
| `max_batch_size`     | No       | Max records per batch                                        |
| `min_batch_interval` | No       | Minimum time between batches (e.g. `10s`, `500ms`, `1m`)     |

Effective max throughput ≈ `max_batch_size / min_batch_interval` records per second. Throttle limits the **maximum** rate, not the minimum — if upstream is slow, batches will be smaller and arrive less frequently.

**Place throttle close to the bottleneck** (just before the rate-limited sink or handler) so upstream transforms still process at full speed.

### Sink Configuration

Quick examples for common sinks. For full field specs of all sink types, see [Sinks](https://docs.goldsky.com/turbo-pipelines/sinks/overview) in the docs (one page per sink type).

#### PostgreSQL

```yaml
sinks:
  output:
    type: postgres
    from: my_transform
    schema: public
    table: my_table
    secret_name: MY_POSTGRES_SECRET
    primary_key: id
```

#### ClickHouse

```yaml
sinks:
  output:
    type: clickhouse
    from: my_transform
    table: my_table
    secret_name: MY_CLICKHOUSE_SECRET
    primary_key: id
```

#### Pub/Sub (Turbo-only)

```yaml
sinks:
  output:
    type: pubsub
    from: my_transform
    topic: my-topic
    secret_name: MY_PUBSUB_SECRET
```

The secret holds a GCP project id and service-account JSON. Topic must already exist in GCP.

#### Blackhole (Testing)

```yaml
sinks:
  output:
    type: blackhole
    from: my_transform
```

---

## Checkpoint Behavior

- **Preserved by default** when updating a pipeline
- **Tied to source names** — renaming a source resets its checkpoint
- **Tied to pipeline names** — renaming the pipeline resets all checkpoints

To reset checkpoints: rename the source or pipeline. Warning: this reprocesses all historical data.

---

## Starter Templates

| Template                       | Description                       | Use Case                     |
| ------------------------------ | --------------------------------- | ---------------------------- |
| `minimal-erc20-blackhole.yaml` | Simplest pipeline, no credentials | Quick testing                |
| `filtered-transfers-sql.yaml`  | Filter by contract address        | USDC, specific tokens        |
| `postgres-output.yaml`         | Write to PostgreSQL               | Production data storage      |
| `pubsub-output.yaml`           | Write to Google Cloud Pub/Sub     | GCP-based event consumers    |
| `multi-chain-pipeline.yaml`    | Combine multiple chains           | Cross-chain analytics        |
| `solana-transfers.yaml`        | Solana SPL tokens                 | Non-EVM chains               |
| `multi-sink-pipeline.yaml`     | Multiple outputs                  | Archive + alerts + streaming |
| `linear-pipeline.yaml`         | Simple decode → filter → sink     | Basic linear flow            |
| `fan-out-pipeline.yaml`        | One source → multiple sinks       | Multi-destination            |
| `fan-in-pipeline.yaml`         | Multiple events → UNION ALL       | Activity feeds               |
| `multi-chain-templated.yaml`   | Per-chain pipeline pattern        | Independent chain deploys    |

**Template location:** `templates/` (relative to this skill's directory)

---

## CLI Quick Reference

| Action                  | Command                                                |
| ----------------------- | ------------------------------------------------------ |
| Install Goldsky CLI     | `curl https://goldsky.com \| sh`                       |
| Install Turbo extension | `curl https://install-turbo.goldsky.com \| sh`         |
| **Validate (REQUIRED)** | `goldsky turbo validate pipeline.yaml`                 |
| Deploy/Update           | `goldsky turbo apply pipeline.yaml`                    |
| Deploy + Inspect        | `goldsky turbo apply pipeline.yaml -i`                 |
| List pipelines          | `goldsky turbo list`                                   |
| List datasets           | `goldsky dataset list --output json`                   |
| List secrets            | `goldsky secret list`                                  |

For lifecycle commands (pause/resume/restart/delete) and monitoring (inspect/logs), see `/turbo-operations`.

---

## Troubleshooting

See `references/troubleshooting.md` for CLI hanging, validation errors, and runtime errors.

---

## Related

- **`/turbo-builder`** — Interactive wizard to build pipelines step-by-step
- **`/turbo-doctor`** — Diagnose and fix pipeline issues
- **`/turbo-operations`** — Lifecycle commands and monitoring reference
- **`/turbo-transforms`** — SQL, TypeScript, and dynamic table transform reference
- **`/datasets`** — Dataset names and chain prefixes
- **`/secrets`** — Sink credential management
