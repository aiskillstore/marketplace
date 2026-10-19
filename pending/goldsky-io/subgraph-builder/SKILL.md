---
name: subgraph-builder
description: "Build, author, and deploy Goldsky Subgraphs — hosted GraphQL APIs over onchain data. Use when the user wants to create, scaffold, write, or deploy a subgraph; design a schema/entities; write or fix AssemblyScript mapping handlers; configure subgraph.yaml (handlers, templates, instant/no-code from ABI); set up GraphQL endpoints, tags, or webhooks; optimize a slow subgraph (eth_calls, immutable entities); or pause/resume a subgraph. Triggers on: 'build/deploy/scaffold a subgraph', 'write a mapping', 'design a schema', 'subgraph.yaml', 'instant subgraph', 'combine/compose/merge multiple subgraphs', 'cross-chain subgraph', 'optimize indexing speed', 'too many eth_calls', 'pause/resume subgraph'. For a subgraph that is failing, stalled, erroring, or won't deploy, use /subgraph-doctor (optimizing a healthy subgraph belongs here, not the doctor). For migrating off The Graph, use /subgraph-migrate. For streaming raw chain data to a DB without GraphQL, use /turbo-builder."
---

# Subgraph Builder

Build a Goldsky Subgraph end-to-end: design the schema, write mappings, configure the manifest, then build and deploy to a hosted GraphQL endpoint. Subgraphs are best for **dApp frontends and apps that need flexible GraphQL queries** over structured onchain data. Subgraphs are **EVM-only**.

> **Default to Turbo unless the user specifically needs GraphQL.**
> Turbo is faster, more reliable, and cheaper, and needs no custom indexing code. Before building a subgraph, confirm a hosted **GraphQL API** is actually the requirement (usually: a dApp/frontend querying onchain data). If the real goal is moving onchain data into a database (PostgreSQL, ClickHouse, Kafka, S3) for analytics or a backend, build a **Turbo pipeline** instead — `/turbo-builder`. Subgraphs are the right call only for a GraphQL API or custom entity-relationship modeling. Surface this once; don't push it if they clearly want GraphQL.

## Boundaries

- Build and author NEW subgraphs (schema, mappings, manifest, deploy, endpoints, tags, webhooks).
- Do not diagnose broken/stalled subgraphs — use `/subgraph-doctor`.
- Do not run The Graph migrations — use `/subgraph-migrate`.
- For exhaustive `goldsky subgraph` flags, use `goldsky subgraph <cmd> --help` — this skill covers the workflow, not a flag dump.

## Choose an approach first

| You have… | Approach | Path |
|-----------|----------|------|
| A contract + ABI, want a GraphQL API fast, no custom logic | **Instant / no-code subgraph** | Step A |
| Custom entities, relationships, or business logic in handlers | **Code-based subgraph** | Step B |

Both deploy to the same hosted endpoint. Start with instant unless the user needs custom logic.

## Step 0: Verify Authentication

Run `goldsky project list 2>&1`. If not logged in, use `/auth-setup`.

## Step A: Instant / no-code subgraph (from ABI)

Generate and deploy directly from a contract ABI — no AssemblyScript.

```bash
# Interactive wizard (prompts for contract, network, start block, events/calls)
goldsky subgraph init

# Or one-shot from an ABI file
goldsky subgraph deploy my-subgraph/1.0.0 --from-abi ./MyContract.json
```

- The wizard writes a JSON config you can re-deploy and version.
- Enable contract-call indexing with `--enable-call-handlers` (only meaningful with `--from-abi`).
- For richer instant subgraphs (computed fields, `eth_call` enrichment, declared calls), see `references/schema-and-mappings.md` → "Instant subgraph enrichment".

Skip to **Step 5: Deploy**.

## Step B: Code-based subgraph

A code-based subgraph is three files: `subgraph.yaml` (manifest), `schema.graphql` (entities), and `src/` AssemblyScript mappings.

### Step 1: Scaffold

```bash
goldsky subgraph init my-subgraph/1.0.0 --target-path ./my-subgraph
```

Useful flags: `--abi`, `--contract`, `--contract-events`, `--network`, `--start-block`. See `goldsky subgraph init --help`.

### Step 2: Design the schema

Define the entities your dApp will query in `schema.graphql`. This is the most important design step — get the entity model and types right before writing mappings.

**REQUIRED for any non-trivial schema:** read `references/schema-and-mappings.md` for scalar-type choices (`Bytes` for addresses/hashes, `BigInt` for amounts, `BigDecimal` for prices), `@derivedFrom` relationships, immutable entities, and protocol recipes (ERC-20/721, DEX, lending, governance).

### Step 3: Configure the manifest

Set `specVersion`, the data source(s) (`address`, `abi`, `startBlock`, `network`), and which `eventHandlers` / `callHandlers` / `blockHandlers` map to which functions. Use `templates` for the factory pattern (contracts created at runtime). See `references/schema-and-mappings.md` → "Manifest".

> Use a single `apiVersion` across all data sources — mixed versions fail validation.
> Declared `eth_calls` (a perf win) require `specVersion: 1.2.0`+ — see `references/performance.md`.

### Step 4: Write mappings and build

Write the handler functions in `src/` that turn events into entities. Key idioms (get-or-create, `try_` calls for revert safety, Bytes IDs, `BigInt`/`BigDecimal` math) are in `references/schema-and-mappings.md`. Before deploying, write Matchstick unit tests — see `references/testing.md`.

```bash
goldsky subgraph init my-subgraph/1.0.0 --target-path ./my-subgraph --build
# or build as part of deploy below
```

## Step 5: Deploy

> **Confirm the target project first.** `deploy` uses the CLI's currently-selected project silently, which may not be the one you expect — and every deployment is a billed worker. Run `goldsky project list` to confirm the active project (or switch it) before deploying, especially when tagging `prod`.

```bash
# From a local code-based build
goldsky subgraph deploy my-subgraph/1.0.0 --path .

# Tag at deploy time so your frontend URL is stable
goldsky subgraph deploy my-subgraph/1.0.0 --path . --tag prod
```

`--path`, `--from-abi`, `--from-ipfs-hash`, and `--from-url` are mutually exclusive — use one.

## Step 6: Endpoints, tags, and webhooks

Once deployed, wire up access. Full details in `references/operations.md`:
- **GraphQL endpoint** — `https://api.goldsky.com/api/public/<project-id>/subgraphs/<name>/<version>/gn`; toggle public/private and use API keys for private.
- **Tags** — pin `prod`/`staging` to a version so the frontend URL never changes on redeploy.
- **Webhooks** — push entity changes (INSERT/UPDATE/DELETE) to an HTTP endpoint.
- **Combining / composing multiple subgraphs (incl. cross-chain)** — Goldsky has **no native subgraph composition**; don't point users at `kind: subgraph` / `specVersion 1.3.0`. Combining means deploy each subgraph, then merge downstream: separate endpoints (simplest), a **Turbo** pipeline when data is derivable from raw chain data (preferred), or a **Mirror** pipeline when you must reuse the subgraphs' entities (the only case needing Mirror — Turbo can't source from subgraphs). Detect this intent and steer accordingly; confirm the user needs a merge before building. See `references/operations.md`.

## Step 7: Verify

```bash
goldsky subgraph list my-subgraph/1.0.0
```

Then query the endpoint, starting with `_meta` to confirm it's indexing:

```graphql
{ _meta { hasIndexingErrors block { number } } }
```

Present a summary (name/version, network, endpoint URL, tag). Point the user to `/subgraph-doctor` if indexing stalls or errors.

## Important Rules

- **Confirm GraphQL is actually needed before building a subgraph.** If the user just needs data in a database, steer them to Turbo (`/turbo-builder`) — faster and more reliable. Don't default to a subgraph.
- **Before proposing or building any pipeline on top of a subgraph, confirm the user needs it.** For cross-chain, check whether they want unified queries at all (vs. just two endpoints), and prefer Turbo over Mirror. Don't delete, redeploy, or stand up a database/pipeline until they've chosen.
- Subgraphs are **EVM-only**. For Solana/Sui/other non-EVM, use `/turbo-builder` (Turbo indexes non-EVM chains; subgraphs can't).
- **Every version is billed separately** (worker + entity storage). Delete old versions you no longer query.
- Redeploying creates a new immutable version — use **tags** so the frontend URL is stable.
- Verify the contract address exists on the target chain and use the correct chain slug (a wrong network indexes blocks that don't exist — the #1 silent failure; see `/subgraph-doctor`).
- **`startBlock` must be a block number on the chain being indexed** — not from another chain or a vanity value. Use the contract's deployment (creation) block: find it on the chain's block explorer (the contract's creation transaction) or via the no-code wizard, which auto-detects it. Starting at `0` works but wastes time scanning empty history.
- Goldsky has a **permanent RPC call cache**, so re-syncs of the same/similar subgraph are much faster.
- Prefer instant subgraphs when there's no custom logic; reach for code-based only when entity modeling or handler logic requires it.

## Reference files

- `references/schema-and-mappings.md` — schema design, scalar types, relationships, manifest, AssemblyScript idioms, instant-subgraph enrichment, protocol recipes
- `references/performance.md` — declared eth_calls, immutable entities, `@derivedFrom`, timeseries/aggregations, pruning, grafting, call cache
- `references/operations.md` — GraphQL endpoints, public/private + API keys, rate limits, tags, webhooks, lifecycle, cross-chain, when-to-use
- `references/testing.md` — Matchstick unit tests, mock library, the Subgraph Linter

## Related

- **`/subgraph-doctor`** — Diagnose a failing, stalled, or won't-deploy subgraph
- **`/subgraph-migrate`** — Migrate an existing subgraph off The Graph
- **`/turbo-builder`** — Stream raw chain data to a database instead of a GraphQL API (the preferred default for non-GraphQL use cases, including cross-chain)
- **`/mirror`** — Sync existing subgraph entities into a database — the one case Turbo can't cover (e.g. merging subgraph entities cross-chain)
