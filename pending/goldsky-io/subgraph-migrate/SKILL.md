---
name: subgraph-migrate
description: "Migrate a subgraph from The Graph to Goldsky as a drop-in replacement — no code changes required. Use this skill when the user wants to move, switch, port, or migrate a subgraph off The Graph (hosted service, Subgraph Studio, or the decentralized network) onto Goldsky, or when a subgraph endpoint they relied on (e.g. The Graph hosted service) was sunset. Triggers on: 'migrate from The Graph', 'move my subgraph to Goldsky', 'switch off The Graph', 'redeploy a TheGraph subgraph', 'my subgraph endpoint is gone', 'from-url', 'from-ipfs-hash', 'drop-in replacement for The Graph'. For diagnosing a subgraph that fails after migrating, use /subgraph-doctor. For building/authoring or general deploy/tag/endpoint reference, use /subgraph-builder."
---

# Migrate a Subgraph from The Graph

Migrating an existing subgraph from The Graph to Goldsky is a **drop-in replacement** — you don't change your subgraph code. You point Goldsky at your published subgraph (by URL or IPFS hash) or redeploy from source, then swap the endpoint your app queries.

> **Worth a quick check first: do they still need a subgraph?**
> Migration is a natural moment to reconsider. If the dApp needs a hosted **GraphQL API**, migrating the subgraph is the right move — continue below. But if the real goal is getting this data into a database for analytics or a backend, a **Turbo pipeline** is faster, more reliable, and cheaper (`/turbo-builder`) — they may not need a subgraph at all. Surface this once; if they clearly want GraphQL, proceed with the migration.

## Boundaries

- This skill is for migrating **from The Graph** (hosted service, Subgraph Studio, or decentralized network).
- For diagnosing a subgraph that fails to deploy or sync after migrating, use `/subgraph-doctor`.
- For deploy/tag/endpoint/webhook reference, use `/subgraph-builder`.
- For migrating from Alchemy, follow the dedicated Alchemy migration docs (not covered here).

## Two hard rules

> **1. Never invent the source URL or IPFS hash.** Always have the user provide their actual deployment URL or IPFS hash. Do not construct or guess `api.thegraph.com/...` or gateway URLs — fabricated source URLs are a top failure mode and waste deploy attempts. If you don't have a verified source, ask for it (see Step 2).

> **2. Never quote pricing.** Do not tell the user migration is "free" or "cheap" or estimate a price. Subgraph pricing depends on usage and plan, and a wrong guess erodes trust (one customer was told "cheap" then quoted $10k+). For any cost question, route them to a Goldsky quote: support@goldsky.com or their account/sales contact.

## Step 1: Choose a migration path

| You have… | Use | Notes |
|-----------|-----|-------|
| A public GraphQL endpoint for the deployed subgraph | `--from-url <url>` | Simplest. Works for publicly deployed subgraphs. |
| The subgraph's IPFS hash (deployment ID) | `--from-ipfs-hash <hash>` | Use when you have the hash but not a queryable URL. |
| The original source code locally | `--path .` (build first) | Use if the published version is unavailable or you want to change code. |

Recommend `--from-url` when the user has a working endpoint; otherwise `--from-ipfs-hash`.

## Step 2: Get the real source identifier

Before deploying, get the user's actual source — do not guess it.

- **From-URL:** Ask the user to paste the GraphQL endpoint they currently query on The Graph.
- **From-IPFS-hash:** The IPFS hash is the deployment ID (`Qm...`). The user can find it on The Graph's explorer/Studio, or by querying their existing endpoint:
  ```graphql
  { _meta { deployment } }
  ```
  `deployment` is the IPFS hash.

If the user can't produce either, fall back to deploying from source (`--path`) and point them to `/subgraph-builder` for `init`/build.

## Step 3: Install the CLI and log in

CLI setup is the most common migration sticking point — confirm it before deploying.

```bash
# Install (macOS/Linux)
curl https://goldsky.com | sh
# Install (Windows, or if the curl installer fails)
npm i -g @goldskycom/cli

goldsky login
```

Verify with `goldsky project list`. If login fails, use `/auth-setup`.

## Step 4: Deploy to Goldsky

Pick the line matching the path from Step 1. Choose your own `name/version` for the Goldsky deployment:

```bash
# From a public GraphQL endpoint
goldsky subgraph deploy my-subgraph/1.0.0 --from-url <your-thegraph-endpoint>

# From an IPFS hash (deployment ID)
goldsky subgraph deploy my-subgraph/1.0.0 --from-ipfs-hash <Qm...>

# From source (build first per /subgraph-builder)
goldsky subgraph deploy my-subgraph/1.0.0 --path ./build
```

> If a subgraph with the same IPFS hash was already indexed on Goldsky, it can sync **instantly** to 100% — that's expected, not an error. You still get your own endpoint with your own rate limits.

> Deployments with a lot of metadata can hit IPFS timeouts (`524`). Retry — usually a later attempt succeeds. If it keeps failing, escalate to support to port it manually.

## Step 5: Verify it's syncing

```bash
goldsky subgraph list my-subgraph/1.0.0
```

Then run the `_meta` query against the new Goldsky endpoint to confirm the indexed head is advancing:

```graphql
{ _meta { hasIndexingErrors block { number } } }
```

- A fresh migration that wasn't pre-indexed syncs from the start block — this can take a while. That's normal.
- **Stuck at a low %** (e.g. 0.05%) is usually a mapping/handler error or a wrong network, **not** a slow sync. Hand off to `/subgraph-doctor`.
- `hasIndexingErrors: true` → `/subgraph-doctor`.

## Step 6: Migrate tags and swap your endpoint

Goldsky tags pin a stable alias (like `prod`) to a version so your frontend URL never changes on redeploy:

```bash
goldsky subgraph tag create my-subgraph/1.0.0 --tag prod
# Tagged endpoint:
# https://api.goldsky.com/api/public/<project-id>/subgraphs/my-subgraph/prod/gn
```

Once synced, point your app at the Goldsky endpoint (use the tagged URL so future redeploys don't break the frontend). See `/subgraph-builder` for endpoints, private endpoints/API keys, and webhooks.

## Common migration gotchas

These show up because a subgraph authored for The Graph hits Goldsky's spec validation on first deploy. If any occur, hand the exact error to `/subgraph-doctor`:

- `subgraph must use a single apiVersion across its data sources` — unify `apiVersion`.
- `Interface '<X>' not defined`, or timeseries/aggregation spec errors — fix the schema.
- `no network <slug> found` — the chain slug differs on Goldsky; use the correct supported-network slug.
- `A deployment with this name & version already exists` — bump the version.
- CLI deploy keeps failing on a valid subgraph — the no-code/dashboard deploy path is a fallback; escalate if both fail.

## Related

- **`/subgraph-builder`** — Build, author, and deploy subgraphs; endpoints, tags, webhooks reference
- **`/subgraph-doctor`** — Diagnose a subgraph that fails to deploy or sync after migrating
- **`/auth-setup`** — CLI installation and login
- **Goldsky docs:** [docs.goldsky.com/subgraphs/migrate-from-the-graph](https://docs.goldsky.com/subgraphs/migrate-from-the-graph)
