# Limit-Order Strategy — CLI Reference

## Commands

### `strategy create-limit`

```bash
onchainos strategy create-limit --chain-id <id|alias> --from-token <address> --to-token <address> \
  --amount <decimal-string> --direction <buy|sell> --trigger-price <usd> \
  [--current-price <usd>] [--slippage <percent>] [--mev-protection <on|off|default>] [--wait]
```

| Flag | Required | Notes |
|---|---|---|
| `--chain-id` | Y | `1` / `solana` / `bsc` / `arbitrum` / `base` / `xlayer` (6 supported chains only). |
| `--from-token` / `--to-token` | Y | Sell-side / buy-side token contract address. |
| `--amount` | Y | Amount of from-token to sell (string, no precision loss). |
| `--direction` | Y | `buy` or `sell` (case-insensitive). Strategy type is derived by the CLI — no `--type` flag. |
| `--trigger-price` | Y | USD trigger price. |
| `--current-price` | N | Current USD price of the comparison token (to-token for buy, from-token for sell). Omit → CLI fetches via `market price`. |
| `--slippage` | N | Percent, default `15`. Pass a plain number (`20%` → `20`; `0.05` = 0.05%, not 5%). |
| `--mev-protection` | N | `on` / `off` / `default` (default = BE picks). |
| `--wait` | N | bool `[UNIT: bool]`, default `false`. Wait for terminal state: fixed 3 s sleep, then re-query + merge (see Output). |

Order TTL is fixed at `604800` seconds (7 days) by the CLI and cannot be configured with a command-line flag.

Output: `{orderId, status:<int>, statusLabel, estimatedWaitTime:<int|null>, eventCursor:<string|null>}`. Solana returns `estimatedWaitTime=0`; other chains follow the async wait pattern.

**belowMinimum (exit 0, no order created):** below the $1 USD minimum — caught by the local pre-check OR by normalizing backend `100010` — the CLI returns `{belowMinimum:true, minFromAmount:<string>, fromSymbol:<string>}` instead. `minFromAmount = ceil(1.0 / from_token_price)` as an integer string; both paths emit identical shape. Return this object to the already-loaded strategy flow for rendering.

**`--wait` merge:** appends `settled:<bool>`; when settled, also `transactionInfo` / `executionHistoryList` / `fromToken` / `toToken` / `orderStatusUpdateTime`. `status` / `statusLabel` reflect the re-query.

### `strategy cancel`

Pass exactly one target selector:
```bash
onchainos strategy cancel --order-id <id> [--wait]
onchainos strategy cancel --order-ids id1,id2,... [--wait]
onchainos strategy cancel --all
```
`--wait` (bool, `[UNIT: bool]`) waits for terminal state (fixed 3 s + per-order re-query/merge). **`--all` + `--wait` is rejected** before any cancel is sent (`code: invalid_input`, `field: wait`, exit 1) — use `--order-id` / `--order-ids` with `--wait`, or omit `--wait` for bulk cancel. Output without `--wait`: `{updateNum:N, estimatedWaitTime:null|n}`; with `--wait`: `{settled:<bool>, orders:[{orderId, settled, status, statusLabel, ...}]}` (top-level `settled` = logical AND across orders). `updateNum` is the count BE accepted, not the count that reached terminal state — re-query with `list` if you did not pass `--wait`.

### `strategy list`

```bash
onchainos strategy list [--order-id <id>] [--status active,suspended,...] [--chain-id 1,501] \
  [--token <address>] [--limit <int>] [--cursor <string>] [--strategy-mode 7]
```
Modes: `--order-id <id>` → single-order detail (`openOrderDetail`); omit → page query (`getOpenOrder`, active wallet addresses auto-supplied; `--limit` max 100 default 100; `--cursor` from the previous response's `nextCursor`). `--status` and `--chain-id` accept comma-separated lists; `--token` accepts a single address only (multi-token → call once per token and merge).

### `strategy resume`

```bash
onchainos strategy resume [--wait]                      # auto-discover all SUSPENDED + canResume=true
onchainos strategy resume --order-ids id1,id2 [--wait]  # explicit
```
`--wait` (bool, `[UNIT: bool]`) waits for terminal state (fixed 3 s + per-order re-query/merge), same `{settled, orders:[...]}` shape as `cancel --wait`.

## Command Constraints

4 subcommands: `create-limit`, `cancel`, `list`, `resume`. All emit the JSON envelope `{ok:true,data:{...}}` on stdout (no `--format` flag — strategy CLI is agent-facing; the agent renders any user-visible table from JSON). Follow the already-loaded strategy flow for behavior.

### strategyType enum + derivation

Derived inside the CLI from `(--direction, --trigger-price, current price)`; equality folds into the aggressive side (CHASE_HIGH / STOP_LOSS). The Display label is the only user-facing string.

| int | Enum | Direction | trigger vs current | Display label | Semantics |
|---|---|---|---|---|---|
| 2 | BUY_DIP | buy | trigger < current | Buy Dip | Buy when price falls to trigger |
| 5 | CHASE_HIGH | buy | trigger ≥ current | Buy Above | Buy when price rises above trigger |
| 3 | TAKE_PROFIT | sell | trigger > current | Take Profit | Sell when price rises to trigger |
| 4 | STOP_LOSS | sell | trigger ≤ current | Stop Loss | Sell when price falls to trigger |

To fetch the current price: `onchainos market price --chain <chain> --address <token>`, read `data[0].price` (buy → to-token's price; sell → from-token's price).

### status enum

| int | Enum | CLI `--status` value | Display label | Terminal? |
|---|---|---|---|---|
| -7 | EXPIRED | `expired` | Expired | Yes |
| -3 | CANCELLING | `cancelling` | Cancelling | No |
| -2 | CANCELLED | `cancelled` | Cancelled | Yes |
| -1 | FAILED | `failed` | Failed | Yes |
| 0 | TRADING | `processing` / `trading` | Trading | No |
| 1 | COMPLETED | `completed` | Completed | Yes |
| 2 | CREATING | `creating` | Creating | No |
| 3 | ACTIVE | `active` | Active | No |
| 4 | SUSPENDED | `suspended` | Suspended | No |

Non-terminal set `{-3,0,2,3,4}` (the default when `--status` is omitted); terminal set `{-7,-2,-1,1}`. `SPEEDING_UP` (-4) is not a valid filter. To see terminal orders, pass `--status` explicitly (e.g. `completed`, `cancelled`, `failed`, `expired`, or the full 9 for "all including terminal").

### `getOpenOrder` request body (reference only — agent never builds it)

Page-query mode POSTs `getOpenOrder`; the agent only sets mapped flags. Fields: `accountId` (auto, JWT auth), `walletAddressList` (auto, EVM+SOL), `chainIdList` (← `--chain-id`), `orderStatusList` (← `--status`; default 5 non-terminal), `orderTypeList` (unused), `idList` (use `--order-id` detail mode instead), `tokenAddress` (← `--token`, single only), `limit` (← `--limit`, BE default 100 max 100), `cursor` (← `--cursor`, Base64; omit on first page).

### Current limitations

Symbol→address resolution: out of scope (pass addresses). Custom preset (fee tiers, dexId filter): default preset only (MEV via `--mev-protection`). Events stream: `eventCursor` surfaced verbatim, no consumer yet. `cancel --all` channel filter: BE default pass-through. Multi-account batch: out of scope (active account only). `get_account_status`: intentionally not implemented — SA activation/expiry is handled transparently inside the 60018 flow.

## Troubleshooting

- [Strategy troubleshooting](strategy-troubleshooting.md)
