# DEX Swap — CLI Reference

Syntax, parameters, and key return fields for `onchainos swap` subcommands. Verify with `onchainos swap <subcommand> --help` when unsure.

## `swap chains`

Supported chains for the DEX aggregator (no params). Returns per chain: `chainIndex`, `chainName`, `dexTokenApproveAddress` (router address for approvals).

## `swap liquidity --chain <chain>`

Available liquidity sources on a chain. Returns `id`, `name` (e.g. `Uniswap V3`), `logo`.

## `swap quote`

Read-only price estimate. **No `--slippage`.**

```bash
onchainos swap quote --from <addr> --to <addr> --readable-amount <amt> --chain <chain> [--swap-mode <exactIn|exactOut>]
```

`--readable-amount` (human units, CLI converts) or `--amount` (raw minimal units) — one of. Key return: `toTokenAmount`, `fromTokenAmount`, `estimateGasFee`, `tradeFee` (USD), `priceImpactPercent`, `dexRouterList[]` (`dexName`, `percentage`), and per-side `fromToken` / `toToken` with `isHoneyPot`, `taxRate`, `decimal`, `tokenUnitPrice`.

## `swap execute`

One-shot: quote → approve (if needed) → sign → broadcast. Honeypot and price impact >10% are blocked internally.

```bash
onchainos swap execute --from <addr> --to <addr> --readable-amount <amt> --chain <chain> --wallet <addr> \
  [--slippage <pct>] [--gas-level <slow|average|fast>] [--swap-mode <exactIn|exactOut>] \
  [--mev-protection] [--tips <sol>] [--max-auto-slippage <pct>] [--force]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--from` / `--to` | Yes | — | Source / destination token address. |
| `--readable-amount` / `--amount` | One of | — | Human units (converted) / raw minimal units. |
| `--chain` | Yes | — | Chain name or ID. |
| `--wallet` | Yes | — | User's wallet address. |
| `--slippage` | No | autoSlippage | Percent (e.g. `"1"`). Omit for autoSlippage. |
| `--gas-level` | No | `average` | `slow` / `average` / `fast`. |
| `--mev-protection` | No | — | EVM (Ethereum / BSC / Base). |
| `--tips` | No | — | Jito tips in SOL (Solana only). Mutually exclusive with `computeUnitPrice`. |
| `--max-auto-slippage` | No | — | Caps autoSlippage upper bound; only when `--slippage` omitted. |
| `--force` | No | — | Bypass risk warning 81362 — only after explicit user confirmation (see [swap-troubleshooting.md](swap-troubleshooting.md)). |

Returns `approveTxHash?`, `swapTxHash`, `fromAmount`, `toAmount`, `priceImpact`, `gasUsed`, `nextSteps`.

## `swap swap` (calldata only)

Returns unsigned tx data; does NOT sign or broadcast.

```bash
onchainos swap swap --from <addr> --to <addr> --readable-amount <amt> --chain <chain> --wallet <addr> \
  [--slippage <pct>] [--swap-mode <exactIn|exactOut>] [--tips <sol>] [--max-auto-slippage <pct>]
```

Returns `routerResult` (same shape as `quote`) and `tx` (`to`, `data`, `gas`, `gasPrice`, `value`, `minReceiveAmount`). Present the pair summary + tx fields; for an EVM non-native token, run `swap approve` first and present its calldata separately. Solana: `--tips` embeds Jito calldata. EVM: `--mev-protection` is not supported here — recommend a MEV-protected RPC.

## `swap approve`

ERC-20 approval calldata (advanced/manual use).

```bash
onchainos swap approve --token <addr> --amount <minimal_units> --chain <chain>
```

Returns `data` (approval calldata — send the tx to the **token contract**, not `dexContractAddress`), `dexContractAddress` (spender, already encoded in `data`), `gasLimit`, `gasPrice`.

## `swap check-approvals`

Check an ERC-20 allowance for a token / spender.

```bash
onchainos swap check-approvals --chain <chain> --address <owner> --token <addr> [--spender <addr>]
```

`--spender` defaults to the OKX DEX router.
