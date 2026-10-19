# Subgraph Operations Reference

Conceptual reference for what the CLI help doesn't explain. For exhaustive flags, use `goldsky subgraph <cmd> --help`.

## When to use Subgraphs vs. Turbo vs. Mirror

| Use case | Best tool |
|----------|-----------|
| Frontend / dApp needs a GraphQL API | **Subgraphs** |
| Custom entity relationships / business logic in handlers | **Subgraphs** |
| Stream raw blockchain data to a database | **Turbo** (`/turbo-builder`) |
| Real-time analytics in ClickHouse/Kafka | **Turbo** |
| Sync subgraph entities into your own database | **Mirror + subgraph source** (`/mirror`) |
| Non-EVM chains (Solana, Sui, …) | **Turbo / Mirror** (subgraphs are EVM-only) |

**Default to Turbo.** Reach for Subgraphs only when the user specifically needs a hosted GraphQL API (typically a dApp frontend) or custom entity-relationship modeling — Turbo is faster, more reliable, and cheaper for everything else. Reach for Mirror only when you need a subgraph entity source, which is the one thing Turbo can't do.

## GraphQL endpoints

Every deployed subgraph gets a public endpoint:
```
https://api.goldsky.com/api/public/<project-id>/subgraphs/<name>/<version>/gn
```
Get it (and tag URLs) with `goldsky subgraph list <name/version>`.

### Public vs. private

Endpoints are public by default. Toggle visibility:
```bash
goldsky subgraph update my-subgraph/1.0.0 --public-endpoint disabled
goldsky subgraph update my-subgraph/1.0.0 --private-endpoint enabled
```
Private endpoints require an API key. Create one at **app.goldsky.com → Settings → API Keys** and send:
```
Authorization: Bearer <your-api-key>
```
API keys are stored hashed — copy on creation; a lost key must be regenerated. As a best practice, proxy queries from your backend so the endpoint URL isn't exposed in frontend code.

### Rate limits

Default is ~50 requests / 10 seconds. Higher limits are plan/sales-gated — route requests for increases to support; don't promise a specific number.

## Tags

Tags pin a human-readable alias (like `prod`) to a specific version, so your frontend URL never changes when you redeploy:
```bash
goldsky subgraph tag create my-subgraph/1.0.0 --tag prod
# Tagged endpoint:
# https://api.goldsky.com/api/public/<project-id>/subgraphs/my-subgraph/prod/gn

goldsky subgraph tag delete my-subgraph/1.0.0 --tag prod
```
Re-create the same tag on a new version to hot-swap with zero frontend changes. You can also tag at deploy: `--tag prod` (comma-separate multiple).

## Webhooks

Push entity changes (INSERT/UPDATE/DELETE) to an HTTP endpoint:
```bash
goldsky subgraph webhook create my-subgraph/1.0.0 \
  --name my-webhook --url https://example.com/hook --entity Transfer --secret my-secret
goldsky subgraph webhook list
goldsky subgraph webhook list-entities my-subgraph/1.0.0
goldsky subgraph webhook delete my-webhook
```
> For guaranteed delivery into a database, prefer syncing the subgraph via Mirror (`/mirror`) over webhooks — it's more reliable than push.

## Lifecycle

```bash
goldsky subgraph list                       # all subgraphs
goldsky subgraph list my-subgraph/1.0.0      # one subgraph
goldsky subgraph list --summary
goldsky subgraph pause my-subgraph/1.0.0     # stop indexing
goldsky subgraph start my-subgraph/1.0.0     # resume (command is `start`, not `resume`)
goldsky subgraph update my-subgraph/1.0.0 --description "Production deployment"
goldsky subgraph delete my-subgraph/1.0.0    # add --force to skip confirm
```

> Each version is billed separately (worker + entity storage). Delete versions you no longer query.

## Logs

```bash
goldsky subgraph log my-subgraph/1.0.0 --since 1h --filter error
goldsky subgraph log my-subgraph/1.0.0 --format json
```
For diagnosing failures from these logs, use `/subgraph-doctor`.

## Combining or composing multiple subgraphs

> **Goldsky does not offer native subgraph composition.** If the user asks to "compose subgraphs," combine/merge/aggregate multiple subgraphs into one API, or build a subgraph on top of other subgraphs (The Graph's `kind: subgraph` composition), there is no equivalent native feature on Goldsky — don't point them at `kind: subgraph` / `specVersion 1.3.0`. The way to combine subgraph data on Goldsky is to route it through a pipeline (Mirror or Turbo). Detect this intent and steer accordingly.

A subgraph indexes **one chain** and produces **one GraphQL API**, so combining always means deploying each subgraph separately, then merging downstream. Confirm what the user actually needs before building anything:

1. **Just separate APIs (simplest — start here).** Deploy each subgraph; the frontend/app queries each endpoint directly. No pipeline, no database. Often all they need.
2. **Unified queries in one database, data derivable from raw chain data → prefer Turbo.** Build a **Turbo pipeline** per chain/contract into one table (e.g. with a chain column) and query across it. No subgraph needed; faster and more reliable — the default for combined analytics. Use `/turbo-builder`.
3. **Unified queries that must reuse the subgraphs' entity logic → Mirror.** The **only** case that requires Mirror, because Turbo can't source from subgraphs:
   - **Same-schema subgraphs** (the same protocol across chains, or multiple deployments of one schema) → one Mirror `subgraph_entity` source listing all of them, merged into a single table. Mirror requires the subgraphs share a GraphQL schema. See `docs.goldsky.com/subgraphs/guides/create-a-cross-chain-subgraph`.
   - **Different-schema subgraphs** (e.g. a DEX subgraph + a lending subgraph) → sync each into the same database as separate tables via Mirror, then join across them in SQL. There is no single "merged source" for differing schemas.

See `/mirror` for the pipeline setup. Don't delete/redeploy subgraphs or stand up a database until the user has picked an option.

**Cross-chain** (same contract/schema on multiple chains) is just the same-schema case above: one subgraph per chain, then two endpoints (option 1), or a Turbo (option 2) or Mirror (option 3) merge.
