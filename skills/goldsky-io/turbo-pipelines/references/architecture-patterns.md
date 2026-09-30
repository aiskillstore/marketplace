# Architecture Patterns Reference

Detailed architecture patterns for Turbo pipelines. For quick decision tables, see the main SKILL.md.

## Table of Contents

1. [Data Flow Patterns](#data-flow-patterns)
2. [Templated Multi-Chain Deployment](#templated-multi-chain-deployment)
3. [Dynamic Table Architecture](#dynamic-table-architecture)
4. [PostgreSQL Aggregate Sink Pattern](#postgresql-aggregate-sink-pattern)

---

## Data Flow Patterns

### Linear Pipeline

The simplest pattern. One source → one or more chained transforms → one sink.

```
source → transform_a → transform_b → sink
```

**Use when:** Single data source, single destination, straightforward processing (decode, filter, reshape).

**Template:** `templates/linear-pipeline.yaml`
**Resource size:** `s` or `m`

### Fan-Out (One Source → Multiple Sinks)

One source feeds multiple transforms, each writing to a different sink.

```
              ┌→ transform_a → sink_1 (clickhouse)
source ──────┤
              └→ transform_b → sink_2 (webhook)
```

**Use when:** Different views or subsets of the same data going to different destinations.

**Template:** `templates/fan-out-pipeline.yaml`
**Resource size:** `m`

Example: filter ERC-20 balances to ClickHouse, all token types to a webhook:

```yaml
transforms:
  fungible_balances:
    type: sql
    primary_key: id
    sql: |
      SELECT ... FROM latest_balances balance
      WHERE balance.token_type = 'ERC_20' OR balance.token_type IS NULL

  all_tokens:
    type: sql
    primary_key: id
    sql: |
      SELECT ... FROM latest_balances balance
      WHERE balance.token_type IN ('ERC_20', 'ERC_721', 'ERC_1155')

sinks:
  warehouse:
    type: clickhouse
    from: fungible_balances
    # ...
  webhook:
    type: webhook
    from: all_tokens
    # ...
```

### Fan-In (Multiple Events → One Output)

Multiple event types decoded from the same source, normalized to a common schema, combined with UNION ALL into a single sink.

```
              ┌→ event_type_a ──┐
source → decode ┤                 ├→ UNION ALL → sink
              └→ event_type_b ──┘
```

**Use when:** Unified activity feed combining trades, deposits, withdrawals, transfers into one table.

**Template:** `templates/fan-in-pipeline.yaml`
**Resource size:** `l` (complex processing with many transforms)

### Multi-Chain Fan-In

Multiple sources from different chains combined into a single output.

```
source_chain_a ──┐
source_chain_b ──┼→ UNION ALL → sink
source_chain_c ──┘
```

**Use when:** Cross-chain analytics or unified view across chains.

```yaml
sources:
  eth_transfers:
    type: dataset
    dataset_name: ethereum.erc20_transfers
    version: 1.0.0
    start_at: latest
  base_transfers:
    type: dataset
    dataset_name: base.erc20_transfers
    version: 1.2.0
    start_at: latest

transforms:
  combined:
    type: sql
    primary_key: id
    sql: |
      SELECT *, 'ethereum' AS chain FROM eth_transfers
      UNION ALL
      SELECT *, 'base' AS chain FROM base_transfers
```

**Resource size:** `m` or `l` depending on chain count

---

## Templated Multi-Chain Deployment

When you need the **same pipeline logic** across multiple chains, create separate pipeline files per chain rather than one multi-source pipeline:

- Independent lifecycle (deploy/delete per chain)
- Independent checkpointing (one chain failing doesn't block others)
- Clearer monitoring per chain

**Pattern:** Copy the pipeline YAML and swap chain-specific values:

| Field              | Chain A (base)                    | Chain B (arbitrum)                    |
| ------------------ | --------------------------------- | ------------------------------------- |
| `name`             | `base-balance-streaming`          | `arbitrum-balance-streaming`          |
| `topic`            | `base.raw.latest_balances_v2`     | `arbitrum.raw.latest_balances_v2`     |
| Source key         | `base_latest_balances_v2`         | `arbitrum_latest_balances_v2`         |
| Transform SQL      | `'base' AS chain`                 | `'arbitrum' AS chain`                 |
| Sink table         | `base_token_balances`             | `arbitrum_token_balances`             |

**Template:** `templates/multi-chain-templated.yaml`

**When to use templated vs multi-source:**

| Approach                | Pros                                          | Cons                                |
| ----------------------- | --------------------------------------------- | ----------------------------------- |
| Templated (per-chain)   | Independent lifecycle, clear monitoring        | More files to manage                |
| Multi-source (one file) | Single deployment, cross-chain UNION possible  | Coupled lifecycle, harder to debug  |

---

## Dynamic Table Architecture

Dynamic tables enable runtime-updatable lookup data within a pipeline — the Turbo answer to "no joins in streaming SQL."

### Pattern: Dynamic Allowlist/Blocklist

```
                    ┌──────────────────────┐
                    │  External Updates     │
                    │  (Postgres / REST)    │
                    └──────────┬───────────┘
                               ▼
source ──→ sql transform ──→ [dynamic_table_check()] ──→ sink
```

The SQL transform filters records against the dynamic table. Table contents can be updated externally without pipeline restart.

### Pattern: Lookup Enrichment

```
source ──→ decode ──→ filter ──→ sql (with dynamic_table_check) ──→ sink
                                        ▲
                              [token_metadata table]
                              (postgres-backed)
```

Store metadata (token symbols, decimals, protocol names) in a PostgreSQL table. Reference it in transforms for enrichment.

### Backend Decisions

| Backend     | `backend_type` | When to Use                                                       |
| ----------- | -------------- | ----------------------------------------------------------------- |
| PostgreSQL  | `Postgres`     | Data managed by external systems, shared across pipeline restarts |
| In-memory   | `InMemory`     | Auto-populated from pipeline data, ephemeral, fastest lookups     |

### Sizing Considerations

- Dynamic tables add memory overhead proportional to table size
- For large lookup tables (>100K rows), use `Postgres` backend
- For small, frequently-changing lists (<10K rows), `InMemory` is faster
- Dynamic table queries are async — they add slight latency per record

For full dynamic table configuration syntax and examples, see `/turbo-transforms`.

---

## PostgreSQL Aggregate Sink Pattern

The `postgres_aggregate` sink handles real-time running aggregations (balances, counters, totals) using a two-table pattern: a landing table receives raw events, and a database trigger maintains aggregated values.

```yaml
sinks:
  token_balances:
    type: postgres_aggregate
    from: transfers
    schema: public
    landing_table: transfer_events
    agg_table: account_balances
    primary_key: id
    secret_name: MY_POSTGRES
    group_by:
      account:
        type: text
      token_address:
        type: text
    aggregate:
      balance:
        from: amount
        fn: sum
      transfer_count:
        from: id
        fn: count
```

**Supported aggregation functions:** `sum`, `count`, `avg`, `min`, `max`

**When to use:** Real-time running totals, balances, counters — where you need incremental aggregation rather than full recomputation on each event.
