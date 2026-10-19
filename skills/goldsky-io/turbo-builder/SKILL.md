---
name: turbo-builder
description: "Build and deploy new Goldsky Turbo pipelines: requirements, dataset selection, YAML, validation, and deployment. Use for 'build a pipeline', 'index X on Y chain', or moving chain/contract data into Postgres, MySQL, ClickHouse, Kafka, Pub/Sub, S3, SQS, or webhooks. Also use for data goals such as Polymarket fills/positions/PnL, prediction markets, stablecoin or circulating supply, proof of reserves, sanctions/AML transfer monitoring, deposit detection, CCTP burns/mints, cross-chain settlement, payment reconciliation, wallet history streamed into the user's own database, token holder registries, tokenized equities/RWA, and wash-trading detection. A REST lookup of one wallet's balances or transfers is /feeds, not a pipeline, and so is a read of Polymarket activity, positions or balances. Debug existing pipelines with /turbo-doctor; look up syntax with /turbo-pipelines."
---

# Pipeline Builder

## Boundaries

- Build NEW pipelines. Do not diagnose broken pipelines — that belongs to `/turbo-doctor`.
- Do not serve as a YAML reference. If the user only needs to look up a field or syntax, use the `/turbo-pipelines` skill instead.
- For dataset lookups, use `/datasets`.
- A REST lookup of one wallet's balances or transfers is `/feeds`. Build a pipeline only when the rows need to land in the user's own database or webhook.

Walk the user through building a complete pipeline from scratch, step by step. Generate a valid YAML configuration, validate it, and deploy it.

## Builder Workflow

### Step 1: Verify Authentication

Run `goldsky project list 2>&1` to check login status.

- **If logged in:** Note the current project and continue.
- **If not logged in:** Use the `/auth-setup` skill for guidance.

### Step 2: Understand the Goal

Ask the user what they want to index. Good questions:

- What blockchain/chain? (Ethereum, Base, Polygon, Solana, etc.)
- What data? (transfers, swaps, events from a specific contract, all transactions, etc.)
- Where should the data go? (PostgreSQL, ClickHouse, Kafka, S3, etc.)
- Do they need transforms? (filtering, aggregation, enrichment)
- One-time backfill or continuous streaming?

If the user already described their goal, extract answers from their description.

### Step 3: Choose the Dataset

Use the `/datasets` skill to find the right dataset.

Key points:
- Common datasets: `<chain>.raw_logs`, `<chain>.raw_transactions`, `<chain>.erc20_transfers`, `<chain>.raw_traces`
- For decoded contract events on EVM chains: source from `<chain>.raw_logs` with a filter on `address` ONLY, then add a SQL transform that calls `_gs_log_decode(_gs_fetch_abi(<explorer-url>, <source>), topics, data) AS decoded`, then filter downstream by `WHERE decoded.event_signature = '<EventName>(<types>)'`. Never put topic0 hashes in the source filter — see `/turbo-transforms` for the full pattern. There is no consumable `<chain>.decoded_logs` dataset; decoding always happens in a transform.
- For pre-decoded common token events: `<chain>.erc20_transfers`, `<chain>.erc721_transfers`, `<chain>.erc1155_transfers` are available and don't need decoding transforms.
- For Solana: use `solana.transactions`, `solana.token_transfers`, etc.

Present the dataset choice to the user for confirmation.

### Step 4: Configure the Source

Build the source section of the YAML:

```yaml
sources:
  my_source:
    type: dataset
    dataset_name: <chain>.<dataset>
    version: 1.0.0
    start_at: latest  # REQUIRED — see below. `latest` or `earliest` (Solana uses `start_block` instead)
```

**A start position is required, not optional.** Never emit a dataset source without an explicit `start_at` — that is the field on EVM, NEAR, Bitcoin, and Stellar. Omitting it does not mean "start now": the backend starts from the earliest available data, so the pipeline silently backfills the entire chain history. That is how a pipeline ends up running for days, writing millions of rows, and filling its sink before it ever reaches live data. Solana is the exception — it uses the numeric `start_block`, and omitting that starts at the latest slot, so state which you did rather than leaving the user to guess.

If the user has not stated a start position, ask before writing YAML — offer exactly three options:

1. **From now** (`start_at: latest`) — no backfill, live data only.
2. **From a specific point in history** — `start_at: earliest` plus a `block_number` predicate in the source `filter` (pre-applied at the source, so the excluded range never reaches the sink). On Solana use the numeric `start_block` instead, and on Stellar a ledger sequence number is also accepted (`start_at: 60000000`). A block number is **not** a valid `start_at` value on the other chains: EVM, NEAR, and Bitcoin take `earliest` or `latest` and nothing else.
3. **Full history** (`start_at: earliest`) — state plainly that this replays the entire chain history: days of backfill and millions of rows before live data arrives, and the sink must have room for all of it.

Also ask about:
- **End block:** Solana job-mode backfills only — `end_block` is silently ignored on EVM dataset sources, so bound an EVM range with a `block_number` predicate in `filter`. Omit for streaming.
- **Source-level filter:** Optional filter to reduce data at the source (e.g., specific contract address)

### Step 5: Configure Transforms (if needed)

If the user needs transforms, use the `/turbo-transforms` skill to help:

- **SQL transforms** — filter, aggregate, join, or reshape data using DataFusion SQL
- **TypeScript transforms** — custom logic, external API calls, complex processing
- **Dynamic tables** — join with a PostgreSQL table or in-memory allowlist

Build the transforms section:

```yaml
transforms:
  my_transform:
    type: sql
    primary_key: id
    sql: |
      SELECT * FROM my_source
      WHERE <conditions>
```

### Step 6: Configure the Sink(s)

Ask where the data should go. Use the `/turbo-pipelines` skill for sink configuration:

| Sink | Key config |
|------|-----------|
| PostgreSQL | `secret_name`, `schema`, `table`, `primary_key` (optional, enables upsert) |
| MySQL | `secret_name`, `schema`, `table`, `primary_key` (optional, enables upsert) |
| ClickHouse | `secret_name`, `table`, `primary_key` (required, sets ordering and deduplication) |
| Kafka | `secret_name`, `topic` |
| Pub/Sub (Turbo-only) | `secret_name`, `topic` |
| SQS | `secret_name`, `queue_url` |
| S3 | `bucket`, `region`, `prefix`, `format` |
| Webhook | `url`, `format` |

**If the user names more than one destination, generate ONE pipeline with multiple sinks — do not generate a separate pipeline per destination.** Each sink has a `from:` field that references the source (or a transform) by name, and sinks run independently. Use a fan-out pattern when different sinks want different views of the same source — add an SQL transform per view, then point each sink's `from:` at the appropriate transform. See `references/architecture-patterns.md` in `/turbo-pipelines` and `templates/multi-sink-pipeline.yaml` for examples.

Only split into separate pipelines when sources are fundamentally different (e.g., different chains with independent lifecycles) or the user explicitly asks for separate pipelines.

For sinks requiring `secret_name`, check if the secret exists:

```bash
goldsky secret list
```

If it doesn't exist, help create it using the `/secrets` skill.

**No Postgres database yet?** On the Scale plan (or above), you can provision a Goldsky-hosted Postgres (Neon) database and have its credentials stored as a secret in one step:

```bash
goldsky hosted-sink create --type postgres
```

This prints the created secret's **name**, **ID**, and **type** (the connection string is never printed). Use the printed **name** as the sink `secret_name`. If the account lacks access, the command returns a Scale-plan upgrade message with the team's billing URL — fall back to bringing an external Postgres via the `/secrets` skill.

**Size the sink against the backfill before recommending it.** If the start position from Step 4 is `earliest` or the user described a multi-month or full-history range, say so explicitly before pointing them at a free-tier database — their own or a newly provisioned one. A 512 MB free tier cannot hold a multi-month backfill of a high-volume dataset, and the failure mode is silent: the pipeline validates, deploys, reports `Running`, and then errors `could not extend file because project size limit (512 MB) has been exceeded` with checkpoints timing out while writing nothing. Recommend a paid/sized database, or narrow the start position, before deploying. See the storage-exceeded row in `/turbo-operations` for the post-hoc diagnosis.

### Step 7: Choose Mode

Use the `/turbo-pipelines` skill for guidance:

- **Streaming** (default) — continuous processing, no `end_block`, runs indefinitely
- **Job mode** — one-time backfill, set `job: true` plus a bound: a `block_number` upper bound in the source `filter` on EVM (which also makes the source bounded), `end_block` on Solana

### Step 8: Generate, Validate, and Present

Assemble the complete pipeline YAML. Use a descriptive name following the convention: `<chain>-<data>-<sink>` (e.g., `base-erc20-transfers-postgres`).

1. Write the YAML file to disk (e.g., `<pipeline-name>.yaml`).
2. Run validation BEFORE showing the YAML to the user:

```bash
goldsky turbo validate <pipeline-name>.yaml
```

3. If validation fails, fix the issues and re-validate. Do NOT present the YAML until validation passes. Common fixes:
   - Missing `version` field on dataset source
   - Invalid dataset name (check chain prefix)
   - Missing `secret_name` for database sinks
   - SQL syntax errors in transforms

4. Once validation passes, present the full YAML to the user for review.

### Step 9: Deploy

After user confirms the YAML looks good:

```bash
goldsky turbo apply <pipeline-name>.yaml
```

### Step 10: Verify

After deployment:

```bash
goldsky turbo list
```

Suggest running inspect to verify data flow:

```bash
goldsky turbo inspect <pipeline-name> -p
```

To filter to a specific node: `goldsky turbo inspect <pipeline-name> -n <node-name> -p`.

Present a summary:

```
## Pipeline Deployed

**Name:** [name]
**Chain:** [chain]
**Dataset:** [dataset]
**Sink:** [sink type]
**Mode:** [streaming/job]

**Next steps:**
- Verify data flow with `goldsky turbo inspect <name> -p`
- Check logs with `goldsky turbo logs <name>`
- Use /turbo-doctor if you run into issues
```

## Important Rules

- Always validate before presenting complete YAML to the user. Never show unvalidated complete pipeline YAML.
- Always validate before deploying.
- Always show the user the complete YAML before deploying.
- For job-mode pipelines, remind the user they auto-cleanup ~1hr after completion.
- Use `blackhole` sink for testing pipelines without writing to a real destination.
- If the user wants to modify an existing pipeline, check if it's streaming (update in place) or job-mode (must delete first).
- Never emit a dataset source without an explicit start position. Never default to `start_at: earliest` — ask (from now / from a specific point in history / full history), and when the answer is full history, warn that it replays the entire chain history before live data and check the sink has room for it.
- Never recommend a free-tier database (512 MB) as the sink for a multi-month or full-history backfill.
- Always include `version: 1.0.0` on dataset sources.

## Related

- **`/turbo-pipelines`** — YAML configuration and architecture reference
- **`/turbo-doctor`** — Diagnose and fix pipeline issues
- **`/turbo-operations`** — Lifecycle commands and monitoring reference
- **`/turbo-transforms`** — SQL and TypeScript transform reference
- **`/datasets`** — Dataset names and chain prefixes
- **`/secrets`** — Sink credential management
