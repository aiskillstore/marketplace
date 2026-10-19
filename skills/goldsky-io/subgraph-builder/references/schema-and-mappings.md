# Schema, Manifest, and Mappings

Authoring reference for code-based Goldsky subgraphs. Goldsky runs standard `graph-node`, so the schema (`schema.graphql`), manifest (`subgraph.yaml`), and AssemblyScript mapping APIs (`@graphprotocol/graph-ts`) are the standard subgraph toolchain — only the deploy command differs (`goldsky subgraph deploy`, not `graph deploy --studio`).

## Schema design (`schema.graphql`)

Entities are GraphQL types annotated with `@entity`. Each needs an `id` field.

> **Current graph-cli requires an explicit `immutable` argument on every `@entity`.** A bare `type X @entity { … }` fails `graph codegen`/`graph build` with *"@entity directive requires `immutable` argument."* Always write `@entity(immutable: false)` for entities that update and `@entity(immutable: true)` for write-once event logs (see Immutable entities below). All examples here follow this.

### Scalar type choices

| Use for | Type | Notes |
|---------|------|-------|
| Addresses, tx hashes, byte IDs | `Bytes` | Half the storage of a hex `String`, faster comparisons. Prefer over `String` for any hex value. |
| Token amounts, balances, timestamps, block numbers | `BigInt` | 256-bit integers. |
| Prices, ratios, derived decimals | `BigDecimal` | Arbitrary precision; slower than `BigInt` — only when you need fractions. |
| Flags | `Boolean` | |
| Enumerations | `enum` | Define once, reference in fields. |
| Auto-incrementing timeseries id | `Int8` | Required for timeseries entities (see performance.md). |

> **Bytes sort by hex value, not numerically.** If you need to sort/paginate entities in sequence, add an explicit `BigInt` index field rather than relying on a `Bytes` id.

### IDs

Build stable, collision-free IDs:
- Per-event row: `event.transaction.hash.concatI32(event.logIndex.toI32())`.
- Composite key: concatenate the parts (`account.concat(token)`), keeping `Bytes`.
- Singletons (e.g. a protocol-wide stats entity): a constant string id like `"global"`.

Avoid reusing an id across different entity types — overlapping ids cause "Conflicting key for entity" errors.

### Relationships

- **One-to-many:** store the reference on the *child* and derive on the *parent* with `@derivedFrom`:
  ```graphql
  type Pool @entity(immutable: false) {
    id: Bytes!
    swaps: [Swap!]! @derivedFrom(field: "pool")
  }
  type Swap @entity(immutable: true) {
    id: Bytes!
    pool: Pool!
  }
  ```
  Never store a growing array directly on the parent — large arrays are catastrophically slow (see performance.md). `@derivedFrom` is virtual (no storage, fast).
- **Many-to-many:** model a join entity (e.g. `PoolMembership { pool, account }`).

### Immutable entities

Mark entities that are written once and never updated as immutable:
```graphql
type Transfer @entity(immutable: true) { id: Bytes! ... }
```
graph-node skips block-range/version tracking for immutable entities, so they index and query faster. Use for append-only event records (transfers, swaps, mints). Do **not** use for anything that updates after creation (balances, pool reserves, positions).

## Manifest (`subgraph.yaml`)

Core structure:
```yaml
specVersion: 1.2.0          # 1.2.0+ required for declared eth_calls
schema:
  file: ./schema.graphql
dataSources:
  - kind: ethereum
    name: MyContract
    network: mainnet         # use the correct Goldsky chain slug
    source:
      address: "0x..."
      abi: MyContract
      startBlock: 12985438
    mapping:
      kind: ethereum/events
      apiVersion: 0.0.9       # keep ONE apiVersion across all dataSources
      language: wasm/assemblyscript
      entities: [Pool, Swap]
      abis:
        - name: MyContract
          file: ./abis/MyContract.json
      eventHandlers:
        # Uniswap V2-style Swap — matches the DEX recipe's handleSwap below
        - event: Swap(indexed address,uint256,uint256,uint256,uint256,indexed address)
          handler: handleSwap
      file: ./src/mapping.ts
```

Handler kinds:
- `eventHandlers` — react to emitted events (most common). The `event:` signature must match the ABI exactly, including `indexed`.
- `callHandlers` — react to contract function calls (needs trace support; enable with `--enable-call-handlers` for instant subgraphs).
- `blockHandlers` — run per block (or filtered). Expensive; use sparingly.

### Templates (factory pattern)

For contracts created at runtime (e.g. a DEX factory deploying pools), declare a `templates:` data source and instantiate it from a handler:
```ts
import { Pool as PoolTemplate } from "../generated/templates"
// in handlePoolCreated:
PoolTemplate.create(event.params.pool)
// with context:
let ctx = new DataSourceContext()
ctx.setBytes("token0", event.params.token0)
PoolTemplate.createWithContext(event.params.pool, ctx)
```
Read context inside the template's handlers via `dataSource.context()`.

### Grafting

Goldsky fully supports grafting (start a new version from an existing version's data at a block):
```yaml
features: [grafting]
graft:
  base: <base-deployment-id>
  block: 12345678
```
You cannot graft at a pruned block (see performance.md). Use `--graft-from <name>/<version>` / `--remove-graft` on deploy.

## AssemblyScript mapping idioms (`src/`)

After editing the schema/manifest, regenerate types with codegen so `../generated/schema` and contract bindings exist. (Missing-type or unknown-field compile errors usually mean codegen wasn't re-run.)

### Get-or-create

```ts
function getOrCreatePool(id: Bytes): Pool {
  let pool = Pool.load(id)
  if (pool == null) {
    pool = new Pool(id)
    pool.totalVolume = BigInt.zero()   // initialize EVERY non-nullable field
  }
  return pool
}
```
Always initialize all non-nullable fields on create, and always `.save()` before the handler returns.

### Revert-safe contract calls

A contract call that reverts will abort the handler with a fatal `unexpected null`. Use `try_`:
```ts
let contract = ERC20.bind(tokenAddress)
let decimalsResult = contract.try_decimals()
let decimals = decimalsResult.reverted ? 18 : decimalsResult.value   // sensible default, never skip the save
```
> This is the single most common cause of crashing subgraphs: a non-ERC-20 contract whose `decimals()`/`symbol()` reverts, an early-return that skips `.save()`, then a later `.load()` panics on the missing entity. Default the value, persist the entity, skip only the downstream pricing.

### Safe math

```ts
function safeDiv(a: BigDecimal, b: BigDecimal): BigDecimal {
  return b.equals(BigDecimal.zero()) ? BigDecimal.zero() : a.div(b)
}
// decimal conversion: amount / 10^decimals
let scaled = amount.toBigDecimal().div(
  BigInt.fromI32(10).pow(decimals as u8).toBigDecimal()
)
```

## Instant subgraph enrichment

Instant (no-code) subgraphs configure indexing via JSON instead of AssemblyScript. You can still enrich entities with `eth_call` results and computed expressions. The expression runtime context exposes `event` (or `call`), the parent `entity` (already saved before enrichment), and `calls` (results of previously executed eth_calls). Mark a call `required` to force ordering. **Declared calls** (`declared: true`) run in parallel for a big perf boost but only work for calls with no mapping-handler dependency (computable from event params alone), and are ignored on call handlers. See performance.md and `docs.goldsky.com/subgraphs/guides/create-a-low-code-subgraph`.

## Protocol recipes

Complete, copy-adaptable schema + mapping for the three most common contract types. All follow the rules above: `Bytes` ids, immutable entities for append-only event logs, `@derivedFrom` for the "list of X under Y" queries dApps need, and revert-safe `try_` calls. After editing the schema/manifest, re-run codegen before building. These are standard graph-node patterns and deploy unchanged on Goldsky.

### ERC-20 token tracker

Tracks token metadata, per-holder balances, and an immutable transfer log.

```graphql
type Token @entity(immutable: false) {
  id: Bytes!                  # token address
  symbol: String!
  name: String!
  decimals: Int!
  totalSupply: BigInt!
  holderCount: BigInt!
  balances: [Balance!]! @derivedFrom(field: "token")
  transfers: [Transfer!]! @derivedFrom(field: "token")
}

type Balance @entity(immutable: false) {
  id: Bytes!                  # token ++ holder
  token: Token!
  holder: Bytes!
  amount: BigInt!
}

type Transfer @entity(immutable: true) {
  id: Bytes!                  # txHash ++ logIndex
  token: Token!
  from: Bytes!
  to: Bytes!
  amount: BigInt!
  blockNumber: BigInt!
  timestamp: BigInt!
}
```

```ts
import { BigInt, Bytes, Address } from "@graphprotocol/graph-ts"
import { Transfer as TransferEvent, ERC20 } from "../generated/MyToken/ERC20"
import { Token, Balance, Transfer } from "../generated/schema"

const ZERO_ADDRESS = Address.zero()

function getOrCreateToken(address: Bytes): Token {
  let token = Token.load(address)
  if (token == null) {
    token = new Token(address)
    let c = ERC20.bind(Address.fromBytes(address))
    let sym = c.try_symbol();     token.symbol = sym.reverted ? "???" : sym.value
    let nm = c.try_name();        token.name = nm.reverted ? "Unknown" : nm.value
    let dec = c.try_decimals();   token.decimals = dec.reverted ? 18 : dec.value
    let sup = c.try_totalSupply(); token.totalSupply = sup.reverted ? BigInt.zero() : sup.value
    token.holderCount = BigInt.zero()
    token.save()
  }
  return token
}

function applyDelta(tokenAddr: Bytes, holder: Bytes, delta: BigInt): void {
  let id = tokenAddr.concat(holder)
  let bal = Balance.load(id)
  if (bal == null) {
    bal = new Balance(id)
    bal.token = tokenAddr
    bal.holder = holder
    bal.amount = BigInt.zero()
    let token = getOrCreateToken(tokenAddr)
    token.holderCount = token.holderCount.plus(BigInt.fromI32(1))
    token.save()
  }
  bal.amount = bal.amount.plus(delta)
  bal.save()
}

export function handleTransfer(event: TransferEvent): void {
  let token = getOrCreateToken(event.address)

  let t = new Transfer(event.transaction.hash.concatI32(event.logIndex.toI32()))
  t.token = token.id
  t.from = event.params.from
  t.to = event.params.to
  t.amount = event.params.value
  t.blockNumber = event.block.number
  t.timestamp = event.block.timestamp
  t.save()

  if (event.params.from != ZERO_ADDRESS) applyDelta(event.address, event.params.from, event.params.value.neg())
  if (event.params.to != ZERO_ADDRESS) applyDelta(event.address, event.params.to, event.params.value)
}
```

### DEX / AMM (Uniswap-style, factory + pool template)

Factory deploys pools at runtime → use a **template** (see "Templates" above). Swaps are an immutable log derived on the pool.

```graphql
type Pool @entity(immutable: false) {
  id: Bytes!                  # pool address
  token0: Bytes!
  token1: Bytes!
  reserve0: BigInt!
  reserve1: BigInt!
  txCount: BigInt!
  swaps: [Swap!]! @derivedFrom(field: "pool")
}

type Swap @entity(immutable: true) {
  id: Bytes!
  pool: Pool!
  sender: Bytes!
  amount0In: BigInt!
  amount1In: BigInt!
  amount0Out: BigInt!
  amount1Out: BigInt!
  timestamp: BigInt!
}
```

```ts
// factory handler — instantiate the pool template (no per-event eth_call needed:
// token0/token1 come from the PairCreated event payload)
import { Pool as PoolTemplate } from "../generated/templates"
import { Pool, Swap } from "../generated/schema"

export function handlePairCreated(event: PairCreatedEvent): void {
  let pool = new Pool(event.params.pair)
  pool.token0 = event.params.token0
  pool.token1 = event.params.token1
  pool.reserve0 = BigInt.zero()
  pool.reserve1 = BigInt.zero()
  pool.txCount = BigInt.zero()
  pool.save()
  PoolTemplate.create(event.params.pair)   // start indexing the new pool
}

// pool template handlers
export function handleSwap(event: SwapEvent): void {
  let pool = Pool.load(event.address)
  if (pool == null) return            // pool must exist; created by the factory above
  let s = new Swap(event.transaction.hash.concatI32(event.logIndex.toI32()))
  s.pool = pool.id
  s.sender = event.params.sender
  s.amount0In = event.params.amount0In
  s.amount1In = event.params.amount1In
  s.amount0Out = event.params.amount0Out
  s.amount1Out = event.params.amount1Out
  s.timestamp = event.block.timestamp
  s.save()
  pool.txCount = pool.txCount.plus(BigInt.fromI32(1))
  pool.save()
}

export function handleSync(event: SyncEvent): void {
  let pool = Pool.load(event.address)
  if (pool == null) return
  pool.reserve0 = event.params.reserve0
  pool.reserve1 = event.params.reserve1
  pool.save()
}
```

> For per-swap token metadata or pricing, prefer **declared eth_calls** in the manifest over inline `try_` calls in the handler — see performance.md.

### ERC-721 NFT collection

Tracks collection, per-token ownership, and an immutable transfer log. ERC-1155 is the same shape with `(id ++ tokenId ++ holder)` balances instead of a single `owner`.

```graphql
type Collection @entity(immutable: false) {
  id: Bytes!                  # contract address
  name: String!
  symbol: String!
  tokens: [Nft!]! @derivedFrom(field: "collection")
}

type Nft @entity(immutable: false) {
  id: Bytes!                  # collection ++ tokenId
  collection: Collection!
  tokenId: BigInt!
  owner: Bytes!
  tokenURI: String
}

type NftTransfer @entity(immutable: true) {
  id: Bytes!
  nft: Nft!
  from: Bytes!
  to: Bytes!
  timestamp: BigInt!
}
```

```ts
import { Bytes, ByteArray } from "@graphprotocol/graph-ts"
import { Transfer as TransferEvent, ERC721 } from "../generated/MyNft/ERC721"
import { Collection, Nft, NftTransfer } from "../generated/schema"

export function handleTransfer(event: TransferEvent): void {
  let collection = Collection.load(event.address)
  if (collection == null) {
    collection = new Collection(event.address)
    let c = ERC721.bind(event.address)
    let nm = c.try_name();   collection.name = nm.reverted ? "Unknown" : nm.value
    let sym = c.try_symbol(); collection.symbol = sym.reverted ? "???" : sym.value
    collection.save()
  }

  let nftId = event.address.concat(Bytes.fromByteArray(ByteArray.fromBigInt(event.params.tokenId)))
  let nft = Nft.load(nftId)
  if (nft == null) {
    nft = new Nft(nftId)
    nft.collection = event.address
    nft.tokenId = event.params.tokenId
    let c = ERC721.bind(event.address)
    let uri = c.try_tokenURI(event.params.tokenId)
    nft.tokenURI = uri.reverted ? null : uri.value
  }
  nft.owner = event.params.to       // persist BEFORE returning — never skip .save() on a null path
  nft.save()

  let xfer = new NftTransfer(event.transaction.hash.concatI32(event.logIndex.toI32()))
  xfer.nft = nft.id
  xfer.from = event.params.from
  xfer.to = event.params.to
  xfer.timestamp = event.block.timestamp
  xfer.save()
}
```

### Lending / governance (sketches)

- **Lending:** `Market`, `Account`, `Position(market ++ user)`; immutable `Borrow` / `Repay` / `Liquidation` event logs `@derivedFrom` on `Market`.
- **Governance:** `Proposal` (with a `ProposalState` enum), `Vote(immutable)` `@derivedFrom` on `Proposal`, `Delegate`; vote weights as `BigInt`.

Both follow the same rules: immutable event logs, `@derivedFrom` collections, `Bytes` ids.
