# Testing Subgraphs

Test mappings before deploying — a deployed bug means a costly re-sync (and a stalled subgraph). Subgraph testing uses the standard `graph-node` toolchain (Matchstick + the Subgraph Linter), independent of where you deploy.

## Matchstick unit tests

[Matchstick](https://github.com/LimeChain/matchstick) (`graph test`) runs mapping handlers against mocked events in a local WASM runtime — no chain, no deploy.

Core pattern:
```ts
import { assert, describe, test, clearStore, beforeEach } from "matchstick-as/assembly/index"
import { newMockEvent } from "matchstick-as"
import { ethereum, Address, BigInt } from "@graphprotocol/graph-ts"
import { handleTransfer } from "../src/mapping"
import { Transfer } from "../generated/MyContract/MyContract"

function createTransferEvent(from: Address, to: Address, value: BigInt): Transfer {
  let e = changetype<Transfer>(newMockEvent())
  e.parameters = []
  e.parameters.push(new ethereum.EventParam("from", ethereum.Value.fromAddress(from)))
  e.parameters.push(new ethereum.EventParam("to", ethereum.Value.fromAddress(to)))
  e.parameters.push(new ethereum.EventParam("value", ethereum.Value.fromUnsignedBigInt(value)))
  return e
}

describe("handleTransfer", () => {
  beforeEach(() => { clearStore() })

  test("creates a Transfer entity", () => {
    handleTransfer(createTransferEvent(Address.zero(), Address.zero(), BigInt.fromI32(100)))
    assert.entityCount("Transfer", 1)
    assert.fieldEquals("Transfer", "<expected-id>", "amount", "100")  // entity field is `amount` (the event param is `value`)
  })
})
```

Key APIs:
- `newMockEvent()` + `changetype<T>()` to build a typed event; push `ethereum.EventParam`s for each argument.
- `createMockedFunction(addr, "name", "name():(uint256)").withArgs([...]).returns([...])` — mock contract calls your handler makes. Add `.reverts()` to test revert-safety paths (`try_` handling).
- Assertions: `assert.entityCount`, `assert.fieldEquals`, `assert.notInStore`.
- `clearStore()` between tests (in `beforeEach`); `dataSourceMock` to simulate template context.

Always cover edge cases that crash subgraphs in production: zero-value transfers, self-transfers, a contract whose `decimals()`/`symbol()` reverts (non-ERC-20), and max `BigInt` values.

## Subgraph Linter (catch bugs before deploy)

Static analysis flags the exact mapping-code mistakes that become fatal indexing errors. The high-value checks (these map 1:1 onto what `/subgraph-doctor` diagnoses *after* a crash):

| Check | Catches |
|-------|---------|
| `unchecked-load` | `Entity.load(id)!` force-unwrap that panics when the entity is missing — use get-or-create. |
| `unexpected-null` | A handler path that can produce null (missing required field, mutating a `@derivedFrom` field). |
| `division-guard` | Division without a zero check — use `safeDiv`. |
| `entity-overwrite` | A stale `.save()` after a helper already modified the entity, clobbering fields. |
| `undeclared-eth-call` | An `eth_call` that should be declared (perf) — see performance.md. |

Run the linter in CI alongside `graph test` so these never reach a deploy.

## CI/CD

Gate deploys on tests + lint:
```bash
graph codegen && graph build   # types compile, mappings build
graph test                     # Matchstick unit tests
# subgraph linter
goldsky subgraph deploy my-subgraph/<version> --path .   # only on green
```
