# Cross-Chain Bridge — CLI Reference

Return-field schemas, field semantics, and worked examples for the 7 `cross-chain` subcommands (`bridges`, `tokens`, `quote`, `approve`, `swap`, `execute`, `status`). **Flags are not listed here** — run `onchainos cross-chain <subcommand> --help` for the exact, current flag list.

## `bridges` — return fields

One entry per bridge protocol. Empty response (both chain flags set) = no bridge connects that pair.

| Field | Description |
|---|---|
| `bridgeId` | Bridge protocol ID (openApiCode). Use in `quote` / `approve` / `swap` / `execute --bridge-id`. |
| `bridgeName` | Human-readable name (e.g. `STARGATE V2 BUS MODE`, `ACROSS V3`). |
| `requireOtherNativeFee` | Whether an extra native-token fee applies on top of `crossChainFee`. |
| `supportedChains` | chainIndex values this bridge supports. |

Display 4 columns: `# | Bridge | Supported Chains | Native Fee` (collapse `requireOtherNativeFee` to Yes/No). Do not show `logo` or raw ID fields.

## `tokens` — return fields

One entry per bridgeable from-token: `chainIndex`, `tokenContractAddress` (canonical identifier; lowercase for EVM, native may be `""` or `0xeee…`), `tokenName`, `tokenSymbol` (may be a chain-specific alias like `ARB_ETH`), `decimals`.

## `quote` — return shape

`data` is an array with one quote object; `routerList` is a multi-bridge list.

```json
{
  "fromChainIndex": "42161", "toChainIndex": "10",
  "fromTokenAmount": "1000000",
  "fromToken": { "decimals": 6, "tokenContractAddress": "0xaf88...", "tokenSymbol": "USDC" },
  "toToken": { "decimals": 6, "tokenContractAddress": "0x0b2c...", "tokenSymbol": "USDC" },
  "routerList": [
    { "bridgeId": 636, "bridgeName": "ACROSS V3", "toTokenAmount": "999533", "minimumReceived": "999533",
      "estimateGasFee": "", "estimateTime": "43", "priceImpactPercentage": "", "needApprove": true,
      "needCancelApprove": false, "crossChainFee": "466", "crossChainFeeTokenAddress": "0xaf88...", "otherNativeFee": "0" }
  ]
}
```

- `needApprove` — reliable only when `--check-approve` was set.
- `needCancelApprove` — true for USDT-pattern tokens (revoke before re-approve); backend may not emit it yet (default false).
- `crossChainFee` / `otherNativeFee` — raw units of `crossChainFeeTokenAddress` / native (0 for most bridges).
- `estimateTime` — seconds (string). `priceImpactPercentage` / `estimateGasFee` — may be empty in pre-prod (treat impact as 0%).
- Empty `routerList` → no direct route → backend returns a `fallback` object → [bridge-troubleshooting.md](bridge-troubleshooting.md).

## `approve` — return shape

```json
{ "chainIndex": "42161", "tokenContractAddress": "0xaf88...", "approveAddress": "0xe35e98...", "needApprove": true,
  "tx": { "from": "0xaef7...", "to": "0xaf88...", "data": "0x095ea7b3...", "value": "0", "gasLimit": "55000", "gasPrice": "50527197", "maxPriorityFeePerGas": "23524497" } }
```

`approveAddress` = bridge router receiving the allowance (already encoded in `tx.data`). `tx.to` = token contract; `tx.value` always `"0"`. `needApprove` meaningful only with `--check-allowance`; when allowance is already sufficient, `tx: null` / `needApprove: false`. **`MAX` not supported** — pass a numeric amount (`"0"` to revoke).

## `swap` — return shape

Same `router` info as `quote` plus a ready-to-sign `tx`. Calldata only — does NOT broadcast. `--bridge-id` must match the one used in `approve` (spender alignment). Do NOT `gateway broadcast` this calldata (bypasses the agentic-wallet TEE signing) — use `execute` for the full signed flow.

## `execute` — return (action=execute)

The only success return on the one-shot path (after any in-flight approval + USDT-pattern revoke confirmed on-chain). Uniquely identified by the presence of `nextSteps`.

| Field | Description |
|---|---|
| `action` | `"execute"`. |
| `fromTxHash` | Source chain tx hash — use to query status. |
| `swapOrderId` / `approveTxHash` / `approveOrderId` | Present when non-empty / when an approval ran. |
| `bridgeId` / `bridgeName` / `fromChainIndex` | Bridge + source chain. |
| `minimumReceived` / `toTokenAmount` / `crossChainFee` / `estimateTime` | Echoed from the chosen route. |
| `nextSteps.checkBridgeStatus` | `onchainos cross-chain status --tx-hash <fromTxHash> --bridge-id <bridgeId> --from-chain <fromChainIndex>` — paste verbatim. |

Other `action` values: `blocked` (balance/gas gate) and `fallback` (no route → [bridge-troubleshooting.md](bridge-troubleshooting.md)).

## `status` — return shape

```json
{ "chainIndex": "42161", "txHash": "0xabc...", "toChainIndex": "10", "toTxHash": "0xdef...",
  "toTokenAddress": "0x0b2c...", "toAmount": "999555", "bridgeId": 636, "status": "SUCCESS" }
```

`status` ∈ `SUCCESS` / `PENDING` / `NOT_FOUND`. `toChainIndex` / `toTxHash` / `toTokenAddress` / `toAmount` are empty/zero until `SUCCESS`. Echoed `bridgeId` may disagree with the one passed — trust your own `quote`/`execute` record.

## Worked examples

One-shot — "Bridge 1 USDC Arbitrum → Optimism":
```bash
onchainos cross-chain quote --from usdc --to usdc --from-chain arbitrum --to-chain optimism --readable-amount 1 --wallet 0xaef7... --check-approve
onchainos cross-chain execute --from usdc --to usdc --from-chain arbitrum --to-chain optimism --readable-amount 1 --wallet 0xaef7...
onchainos cross-chain status --tx-hash 0x... --bridge-id 636 --from-chain 42161
```

Manual calldata (external wallet signs): `quote` → `approve` (sign+broadcast `tx`) → `swap` (sign+broadcast `tx`) → `status --tx-hash <swap_hash> --bridge-id <id> --from-chain <idx>`. `--bridge-id` must match across `approve` and `swap`.

## Cross-command rules

- `bridgeId` is a stable openApiCode — derive it from `quote.routerList[].bridgeId` or `cross-chain bridges`; never hardcode.
- Bridgeable scope is runtime — decide a pair via `cross-chain bridges --from-chain <X> --to-chain <Y>`, not a static list.
