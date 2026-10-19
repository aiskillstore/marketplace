---
name: subgraph-doctor
description: "Diagnose and fix broken Goldsky Subgraphs. Use this skill whenever a user has a subgraph that is failing, stalled, stuck syncing, not indexing, auto-paused, returning errors, or won't deploy. Triggers on: 'subgraph stopped syncing', 'subgraph stuck at block', 'subgraph stalled', 'subgraph failed to deploy', 'indexing error', 'SubgraphSyncingFailure', 'unexpected null in handler', 'no network found', 'deployment already exists', 'subgraph not returning data', 'subgraph endpoint 404', 'reached the subgraph limit', 'rate limited'. Also use when the user names a subgraph alongside a problem. Runs CLI commands directly to check status, read logs, identify root cause, and apply fixes. For building, authoring, deploying, endpoint/tag reference, or optimizing a healthy-but-slow subgraph (e.g. too many eth_calls), use /subgraph-builder instead. For migrating from The Graph, use /subgraph-migrate instead."
---

# Subgraph Doctor

Diagnose and fix existing Goldsky Subgraph problems by running CLI commands, reading logs, identifying root causes, and executing fixes.

## Boundaries

- Diagnose and fix EXISTING subgraph problems.
- Diagnose only subgraphs that are **broken** (failing, stalled, erroring, won't deploy). A healthy but slow subgraph is an *optimization* task — use `/subgraph-builder` (e.g. reducing/declaring eth_calls).
- Do not build or scaffold new subgraphs — use `/subgraph-builder` for authoring/`init`/`deploy`.
- Do not handle The Graph migrations — use `/subgraph-migrate`.
- Do not serve as a command reference — use `/subgraph-builder` or `goldsky subgraph <cmd> --help` for CLI syntax and flag lookups.
- Do not handle Turbo or Mirror pipelines — use `/turbo-doctor` or `/mirror-doctor`.
- **Customer-facing only.** Use only `goldsky` CLI commands, the dashboard, and GraphQL queries. Never suggest `graphman`, `kubectl`, Datadog, or direct database access — those are internal Goldsky tooling. When a problem needs them, escalate to support (see Step 6).

## Mode Detection

Before running anything, check if you have the `Bash` tool:

- **Bash available (CLI mode):** Run commands directly and parse output.
- **Bash NOT available (reference mode):** Give the user one command at a time, explain what to look for, and proceed based on what they paste back.

## Diagnostic Workflow

Follow these steps in order. Each builds on the previous one.

### Step 1: Verify Authentication

Run `goldsky project list 2>&1` to confirm the user is logged in.

- **If logged in:** Note the project name and continue.
- **If not logged in:** Direct the user to `/auth-setup`. Do not proceed until auth works.

### Step 2: Identify the Subgraph

Run `goldsky subgraph list 2>&1` to list all subgraphs and their status.

If the user already named a subgraph (`name/version`), confirm it exists in the list. Otherwise show the list and ask which one to diagnose. Note its status and which **network** it indexes — a wrong network is one of the most common root causes (see Step 5).

### Step 3: Triage by Symptom

Subgraph problems fall into a few families. Pick the path that matches the symptom:

| Symptom | Likely family | Go to |
|---------|---------------|-------|
| Deploy command failed (never created) | Deploy-time error | Step 4 → "Deploy-time failures" |
| Stuck at a block / head not moving / stalled / auto-paused | Indexing stalled | Step 4 → logs + `_meta` |
| `Error` / `failed` health, indexing halted | Handler/mapping error | Step 4 → logs |
| Stuck at low % during a migration | Sync-from-scratch (slow), or handler error | Step 4 → logs + `_meta` |
| Endpoint 404 / no data / can't query | Endpoint or not-yet-synced | Step 4 → `_meta` + endpoint check |
| `reached the subgraph limit`, `database unavailable`, frozen with no log errors | Operational/quota (Goldsky-side) | Step 6 (escalate) |

### Step 4: Gather Diagnostic Data

Run these and analyze before concluding:

```bash
# Errors only — START HERE. Widen the window (e.g. --since 24h) if nothing shows.
goldsky subgraph log <name/version> --since 1h --filter error 2>&1

# Subgraph + tag + deployment status
goldsky subgraph list <name/version> 2>&1
```

> **Do not pull unfiltered logs.** Subgraphs emit a huge volume at `info`/`debug` level — running `goldsky subgraph log` without `--filter error` is slow and extremely token-hungry, and rarely adds signal over the error-filtered view. If you genuinely need non-error context, scope it tightly: a very short window (`--since 5m`) and, if possible, grep for a specific string. Lead with errors + the `_meta` query below.

Then run the **`_meta` query** against the GraphQL endpoint — this is the single most useful check for "stuck" or "no data" subgraphs. It reports the latest indexed block:

```graphql
{
  _meta {
    deployment
    hasIndexingErrors
    block { number hash timestamp }
  }
}
```

- `hasIndexingErrors: true` → a handler/mapping error halted indexing. Go to the error patterns below.
- `block.number` far behind the chain head → still syncing (or stalled). Compare against a block explorer.
- `block.number` **ahead of / not yet on** the chain → wrong network deployed (see below).

### Step 5: Match Error Patterns

#### Wrong network / contract on the wrong chain

**Symptoms:** Subgraph never produces data, or `_meta` shows a start/current block that doesn't exist yet on the target chain. Often the subgraph name hints at the intended chain.

**Cause:** The manifest's `network`/chain slug points at a different chain than intended, so the subgraph is waiting for blocks that haven't been mined.

**Fix:** Correct the `network` in `subgraph.yaml` (verify the exact chain slug against the supported-networks docs at `docs.goldsky.com/chains/supported-networks` — e.g. it's `liteforge`, not `litvm-testnet`) and redeploy a new version. Confirm the contract address actually exists on the target chain via a block explorer.

#### Deploy-time failures

The deploy command errors out and nothing gets created. Common cases:

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `no network <slug> found` | Wrong/unknown chain slug in `subgraph.yaml` | Use the correct slug from supported networks. |
| YAML parse error from `subgraph init` | Illegal characters in `--contract-name` (e.g. `:`, spaces from an explorer label) | Pass a clean name: `--contract-name PolymarketUMACTFAdapter`. |
| `subgraph must use a single apiVersion across its data sources. Found: 0.0.7, 0.0.9` | Mixed `apiVersion` across `dataSources`/`templates` | Unify `apiVersion` across the whole manifest. |
| `Interface '<X>' not defined` | Schema references an undefined interface | Define the interface in `schema.graphql`. |
| Timeseries/aggregation spec errors (`must have id field of type Int8`, `@unique` missing, `aggregations not supported in spec version 1.0.0`) | Schema uses timeseries/aggregations not valid for the spec version | Fix the `id` type to `Int8`, add `@unique`, or remove aggregations. |
| `A deployment with this name & version already exists` | Re-deploying the same `name/version` | Bump the version, or `goldsky subgraph delete <name/version>` then redeploy. |
| Windows CLI install fails | The installer runs in WSL, not native Windows | Use auth-setup `scripts/install.ps1`. It installs the pinned CLI with npm inside WSL. Do not pipe a remote installer. |

#### Handler / mapping errors (indexing halts)

**Symptoms:** `hasIndexingErrors: true`; logs show things like:
- `Mapping aborted at src/mappings/...: unexpected null in handler '<handler>' at block #<n>`
- `Subgraph error ... code: SubgraphSyncingFailure`
- `Token.load` failures / Heap (out-of-memory) errors
- WASM trap / "Handler skipped due to execution failure" (when `nonFatalErrors` is enabled)

**Cause:** A bug in the customer's AssemblyScript mappings — most often a null dereference. Classic case: an entity is never `.save()`d because the handler early-returns when a token's `decimals()`/`symbol()` reverts (non-ERC-20 contract), then a later handler `.load()`s that missing entity and panics.

**Fix:**
1. Identify the handler and block from the error.
2. Patch the mapping so it doesn't skip `.save()` on the null path (e.g. default `decimals` to a sentinel like `18`, persist the entity, skip downstream pricing).
3. Redeploy a new version and **rewind to the first affected block** so the missing entities re-initialize.
4. As a stopgap to keep the endpoint serving (incomplete) data while you fix it, `subgraphError: allow` lets queries return partial results.

> Goldsky-side caveat: a deterministic error with `nonFatalErrors` enabled may not auto-clear even after the underlying cause is resolved. If a subgraph stays errored after a correct redeploy, escalate (Step 6).

#### Stalled / auto-paused subgraph

**Symptoms:** Head stops advancing; Goldsky auto-pauses a stalled subgraph and emails you.

**Cause:** Often a handler error (above), sometimes a transient upstream RPC issue or a stale source chain.

**Fix:**
1. Check logs and `_meta` for errors first.
2. If it's a code bug, fix and redeploy. If it was transient, resume: `goldsky subgraph start <name/version>`.
3. If the source chain itself is stale (no new blocks on the explorer either), there's nothing to index — wait for the chain.

#### Upstream RPC errors

**Symptoms:** `eth_getLogs does not exist` / method-not-supported, or `Found no transaction for event` / block-number mismatches.

**Cause:** The chain's RPC provider is misbehaving or missing methods — not the subgraph. (Real case: a node stamped every log with the request's `fromBlock`, so graph-node couldn't match logs to blocks and went fatal.)

**Fix:** This is Goldsky/RPC-side. Confirm it's not a manifest issue, then escalate (Step 6) with the exact error and block number.

#### Endpoint / query problems

**Symptoms:** `404` on the GraphQL endpoint, "no data", or rate-limit errors.

- **404 / no data:** The subgraph may not be synced yet (check `_meta`), or the public endpoint is disabled. Verify the endpoint URL with `goldsky subgraph list <name/version>`. Don't assume an endpoint is live before the resource exists and has synced.
- **Public vs private:** If queries fail auth, the endpoint may be private. Toggle with `goldsky subgraph update <name/version> --public-endpoint enabled` (see `/subgraph-builder`).
- **Rate limits:** Default is ~50 requests / 10 seconds. Higher limits are sales/support-gated — escalate (Step 6); don't promise a specific new limit.

### Step 6: Present Diagnosis

```
## Diagnosis

**Subgraph:** <name/version>
**Network:** <chain>
**Symptom:** <one-line>

**Root cause:**
<what's wrong and why>

**Evidence:**
- <log line / _meta block number / error string>

**Recommended fix:**
1. <step>
2. <step>

**Prevention:**
<how to avoid it next time, if applicable>
```

**When to escalate to support@goldsky.com** (don't burn cycles guessing):
- Operational/quota issues not visible via CLI: `reached the subgraph limit` (especially if the count looks wrong), `database unavailable`, frozen head with no log errors.
- Upstream RPC bugs (`eth_getLogs does not exist`, log/block mismatches).
- A subgraph that stays errored after a verified-correct redeploy.

Give the user the exact info to send: subgraph `name/version`, project ID, the GraphQL endpoint, the error string, and the affected block number. Mention they can reference using the AI/MCP for priority handling.

### Step 7: Execute Fix

Offer to run fixes, and confirm before anything destructive:

- **Resume a paused subgraph:** `goldsky subgraph start <name/version>`
- **Pause for maintenance:** `goldsky subgraph pause <name/version>`
- **Redeploy a fixed version:** `goldsky subgraph deploy <name/new-version> --path .`
- **Redeploy with a rewind:** `goldsky subgraph deploy <name/version> --start-block <firstAffectedBlock>`
- **Delete and recreate (last resort, reindexes from scratch — warn the user):** `goldsky subgraph delete <name/version>` then redeploy.

After a fix, re-check `goldsky subgraph list <name/version>` and the `_meta` query to confirm the head is advancing again.

## Common mapping-code root causes (catch before redeploy)

When indexing halted on a handler/mapping error, the underlying cause is almost always one of these AssemblyScript mistakes. Check the mapping for them before redeploying — and recommend the **Subgraph Linter** (static analysis) plus Matchstick tests so they never reach a deploy again (see `/subgraph-builder` → `references/testing.md`):

| Root cause | Symptom it produces | Fix |
|------------|--------------------|-----|
| Unchecked `Entity.load(id)!` force-unwrap | `unexpected null in handler` panic when the entity is missing | Use get-or-create; never `!`-unwrap a `load`. |
| Early-return that skips `.save()` (often after a reverting `decimals()`/`symbol()` on a non-ERC-20) | later `.load()` panics; `Token.load`/Heap errors | Use `try_` calls, default the value, persist the entity, skip only downstream pricing. |
| Division without a zero guard | math abort / `unexpected null` | Wrap in a `safeDiv` (return 0 when denominator is 0). |
| Stale `.save()` after a helper already mutated the entity | overwritten/clobbered fields, wrong data (not always a crash) | Load once, mutate, save once; don't save a stale copy. |
| Per-event `eth_call` that reverts or is undeclared | slow indexing or `unexpected null` | Make it revert-safe (`try_`) and declare it (`specVersion 1.2.0`+). |

These are the *causes* behind the reactive symptoms in Step 5's "Handler / mapping errors". Fixing the code and rewinding to the first affected block is the durable fix.

## Important Rules

- Always gather data (logs + `_meta`) before diagnosing. Never guess.
- "The product is solid — most issues are customer-side." Check the obvious customer causes first (wrong network, mapping bug, schema/manifest error) before assuming a Goldsky-side problem.
- Never recommend `graphman`/`kubectl`/Datadog/database access to a customer. Escalate instead.
- Confirm before destructive commands (delete, reindex from scratch).
- Redeploying creates a new immutable version. Use tags so the frontend URL doesn't change (see `/subgraph-builder`).

## When Bash Is Not Available

Give one command at a time, explain what to look for, and proceed based on the user's pasted output. Always prefer running commands directly when Bash is available.

## Related

- **`/subgraph-builder`** — Build, author, and deploy subgraphs; schema/mapping/manifest authoring; endpoints, tags, webhooks
- **`/subgraph-migrate`** — Migrate a subgraph from The Graph
- **`/auth-setup`** — CLI installation and authentication
- **`/datasets`** — Chain prefixes and supported-network slugs
- **`/turbo-doctor`**, **`/mirror-doctor`** — Pipeline (not subgraph) diagnosis
