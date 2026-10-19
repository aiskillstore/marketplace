# Subgraph Performance

Tuning knobs for faster indexing and queries on Goldsky-hosted subgraphs. Most are standard `graph-node` features; Goldsky-specific behavior is called out.

## Goldsky-confirmed facts

- **Permanent RPC call cache.** Goldsky permanently caches subgraph RPC calls, so re-syncs of the same or similar subgraph are much faster (cached `eth_call`/log results are reused). You generally don't need to engineer around RPC cost on a resync.
- **Grafting fully supported** (start a new version from an existing one's data — see schema-and-mappings.md). Note the optimization tradeoff below.
- **Indexer resources are not the bottleneck.** Goldsky indexers are not resource-starved, and "ask for more indexing resources" is not a lever (it only ever applied to dedicated indexing, which is being deprecated). Slow indexing is almost always **subgraph design** (heavy per-event work, `eth_calls`, large stored arrays — the knobs below) or **upstream RPC performance**. Fix the design or the RPC path; don't expect more resources to help.
- **Every version is billed separately** (worker fee + entity storage). Delete old versions you no longer query — this is the cheapest, highest-impact "optimization."

## Immutable entities + Bytes IDs

Mark write-once entities `@entity(immutable: true)` and use `Bytes` ids. graph-node skips validity-range/version tracking for immutable entities, so they index faster and query faster. `Bytes` ids use about half the storage of equivalent hex strings and compare faster. Use for append-only records (transfers, swaps, mints); never for entities that update.

## `@derivedFrom` instead of stored arrays

Storing a growing array on a parent entity degrades badly as it grows — every update rewrites the whole array, and very large arrays (tens of thousands of elements) time out. Model the relationship on the child and derive on the parent:

```graphql
type Pool @entity(immutable: false) { id: Bytes!  swaps: [Swap!]! @derivedFrom(field: "pool") }
type Swap @entity(immutable: true) { id: Bytes!  pool: Pool! }
```

`@derivedFrom` is virtual (no storage, resolved at query time) and stays fast regardless of cardinality.

## eth_calls: avoid, declare, or cache

`eth_call`s during indexing are expensive (each is a synchronous RPC round-trip). In order of preference:

1. **Avoid** — if the data is in the event payload, read it from `event.params` instead of calling.
2. **Declared eth_calls** — declare calls in the manifest so graph-node runs them in parallel and caches them. **Requires `specVersion: 1.2.0` or higher.** Declared calls only work when the call is computable from event params alone (no dependency on a mapping handler's intermediate state). For instant subgraphs, set `declared: true` on the enrichment call (ignored on call handlers).
3. **Cache contract metadata** — fetch immutable values (a token's `decimals`/`symbol`) once on first sight and store them on an entity; never re-call per event. Combine with `try_` for revert safety (see schema-and-mappings.md).

## Timeseries and aggregations

For high-volume metrics (daily volume, hourly counts), use timeseries + aggregation entities so the database computes aggregates instead of your mapping doing it per event:

```graphql
type Swap @entity(timeseries: true) {
  id: Int8!
  timestamp: Timestamp!
  amountUSD: BigDecimal!
}
type VolumeStats @aggregation(intervals: ["hour", "day"], source: "Swap") {
  id: Int8!
  timestamp: Timestamp!
  totalUSD: BigDecimal! @aggregate(fn: "sum", arg: "amountUSD")
}
```

Aggregation functions include `sum`, `count`, `min`, `max`, `first`, `last`. This offloads work to the DB and avoids load-modify-save churn on a running total. Timeseries entities require an `Int8` id and a `Timestamp` field. Confirm your `specVersion`/`apiVersion` supports timeseries before relying on it (it's a newer graph-node feature); validate with a small deploy first.

## Pruning

Limit historical state graph-node retains to shrink storage and speed up queries:

```yaml
indexerHints:
  prune: auto      # or a block count, or `never`
```

`auto` keeps the minimum history needed. Trade-off: **you cannot graft at a pruned block**, and historical time-travel queries below the pruned range won't work. Use `never` if you need full history or plan to graft from old blocks.

## Grafting and optimization: the tradeoff

A user who wants their subgraph to "go faster without re-indexing from scratch" usually has grafting in mind. Be clear about what grafting does and doesn't do:

- **Grafting doesn't make indexing faster by itself.** It copies an existing version's already-indexed data up to a graft block so you skip re-processing *those* blocks; the *remaining* blocks only go faster if the new code does less work.
- **The biggest speedups break graft compatibility.** Making entities immutable, changing entity storage, or restructuring the schema all change the schema, and **you can't graft across a schema change.** So you can optimize hard *or* graft-to-skip-resync — not both.
- **Graft-safe changes** are manifest-level and mapping-internal only: declaring `eth_calls`, trimming work inside handlers, removing an unused handler. These keep the schema identical, so a graft is valid — but they often don't touch a design-bound bottleneck (e.g. per-swap USD pricing).

If the only changes that would meaningfully help require schema/storage changes, the realistic option is to rebuild leaner and resync from scratch (below). There is no "add more resources" shortcut — the slowness is the design.

## Optimizing a migrated or over-modeled subgraph

A subgraph deployed via `--from-ipfs-hash`/`--from-url` (migrated from The Graph) carries the **entire upstream codebase's complexity** — not a thin instant-subgraph config. If the user can't see the source ("I just did the instant deploy"), **don't assume it's simple**: introspect the live GraphQL schema (or fetch the manifest by IPFS hash) to see what it actually models. A full DEX subgraph (USD pricing, day/hour aggregates, ticks, positions, per-swap `eth_calls`) is slow by design, and the bottleneck is usually that per-event work — not something a few graft-safe tweaks will fix.

**Lean-rebuild recipe** (common fix for an over-modeled migrated subgraph when the user accepts a resync): author a code-based subgraph against the same contract that keeps only what's queried and drops the expensive machinery —
- **Keep:** live state entities (mutable) + raw event logs as `@entity(immutable: true)` with `Bytes` ids and `@derivedFrom` collections.
- **Drop:** USD/price derivation (Bundle/`derivedETH`/`amountUSD`), token metadata you don't query, day/hour aggregates, ticks/positions, and **all `eth_call`s**.
- **Deploy under a NEW name** (`<name>-lean`) and leave the original running — the lean schema is **not a drop-in**; any dApp query using the dropped fields breaks. Cut over only after the lean version syncs and the frontend is updated.

This routinely turns a multi-day sync into hours because each block does far less work. See the protocol recipes in schema-and-mappings.md for the lean entity shapes.

## Quick checklist

- [ ] Immutable + `Bytes` ids for append-only event entities
- [ ] `@derivedFrom` for every one-to-many (no stored arrays)
- [ ] No per-event `eth_call`s — declared (`specVersion 1.2.0`+) or cached
- [ ] Timeseries/aggregations for rolling metrics
- [ ] Pruning configured if you don't need deep history
- [ ] Old versions deleted (billing)
