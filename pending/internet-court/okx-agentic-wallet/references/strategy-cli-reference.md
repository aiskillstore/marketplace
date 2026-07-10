# Limit-Order Strategy — CLI Reference

4 subcommands: `create-limit`, `cancel`, `list`, `resume`. All emit the JSON envelope `{ok:true,data:{...}}` on stdout (no `--format` flag — strategy CLI is agent-facing; the agent renders any user-visible table from JSON). Behavior/flow is in [strategy.md](strategy.md).

## `strategy create-limit`

```bash
onchainos strategy create-limit --chain-id <id|alias> --from-token <address> --to-token <address> \
  --amount <decimal-string> --direction <buy|sell> --trigger-price <usd> \
  [--current-price <usd>] [--slippage <percent>] [--mev-protection <on|off|default>] [--expires-in <secs>]
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
| `--expires-in` | N | TTL in seconds. Default `604800` (7 days). |

Output: `{orderId, status:<int>, statusLabel, estimatedWaitTime:<int|null>, eventCursor:<string|null>}`. Solana returns `estimatedWaitTime=0`; other chains follow the async wait pattern.

## `strategy cancel`

Pass exactly one flag:
```bash
onchainos strategy cancel --order-id <id>
onchainos strategy cancel --order-ids id1,id2,...
onchainos strategy cancel --all
```
Output `{updateNum:N, estimatedWaitTime:null|n}`. `updateNum` is the count BE accepted, not the count that reached terminal state — re-query with `list` after the wait.

## `strategy list`

```bash
onchainos strategy list [--order-id <id>] [--status active,suspended,...] [--chain-id 1,501] \
  [--token <address>] [--limit <int>] [--cursor <string>] [--strategy-mode 7]
```
Modes: `--order-id <id>` → single-order detail (`openOrderDetail`); omit → page query (`getOpenOrder`, active wallet addresses auto-supplied; `--limit` max 100 default 100; `--cursor` from the previous response's `nextCursor`). `--status` and `--chain-id` accept comma-separated lists; `--token` accepts a single address only (multi-token → call once per token and merge).

## `strategy resume`

```bash
onchainos strategy resume                     # auto-discover all SUSPENDED + canResume=true
onchainos strategy resume --order-ids id1,id2  # explicit
```

## strategyType enum + derivation

Derived inside the CLI from `(--direction, --trigger-price, current price)`; equality folds into the aggressive side (CHASE_HIGH / STOP_LOSS). The Display label is the only user-facing string.

| int | Enum | Direction | trigger vs current | Display label | Semantics |
|---|---|---|---|---|---|
| 2 | BUY_DIP | buy | trigger < current | Buy Dip | Buy when price falls to trigger |
| 5 | CHASE_HIGH | buy | trigger ≥ current | Buy Above | Buy when price rises above trigger |
| 3 | TAKE_PROFIT | sell | trigger > current | Take Profit | Sell when price rises to trigger |
| 4 | STOP_LOSS | sell | trigger ≤ current | Stop Loss | Sell when price falls to trigger |

To fetch the current price: `onchainos market price --chain <chain> --address <token>`, read `data[0].price` (buy → to-token's price; sell → from-token's price).

## status enum

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

## Error code → agent action

Match by integer code, not msg string.

| Code | Name | Action |
|---|---|---|
| 100 | REQUEST_PARAM_ERROR | Surface the BE message; ask the user to fix the flag. |
| 10019 | INSUFFICIENT_NATIVE_GAS_BALANCE | Native gas below required minimum (msg includes `minAmount`). Prompt to top up (deposit / transfer / swap a stablecoin to native via `swap execute`). Do NOT auto-retry. |
| 10026 | JWT_TOKEN_VERIFY_FAILED | Suggest `wallet login`, then retry. |
| 10106 | CHAIN_NOT_SUPPORT_ERROR | Chain unsupported; suggest a supported alternative. |
| 60002 | NO_ORDER_FOUND | Target id wrong or already terminal — suggest `list`. |
| 60003 | LIMIT_ORDER_NO_AUTHORITY | Trader Mode not activated yet; next CLI call triggers SD-A automatically — retry once. |
| 60006 | LIMIT_ORDER_OUT_LIMIT_FAIL | Pending order count at the per-account max (100); ask the user to cancel some and retry. |
| 60009 | LIMIT_ORDER_ILLIQUIDITY_ERROR | No liquidity at the trigger; suggest a different pair or wider trigger. |
| 60014 | LIMIT_ORDER_EXPIRED_CANNOT_OPERATE | Order already expired. |
| 60015 | LIMIT_ORDER_PENDING_CANNOT_OPERATE | Mid-lifecycle; wait for terminal state. |
| 60017 | LIMIT_ORDER_SUCCESS_CANNOT_OPERATE | Already completed. |
| 60018 | ...UPGRADE_REQUIRED | Transparent — CLI handles via SD-A retry; if it leaks, just retry the same command. |
| 60030 | QUOTA_EXCEEDED | Account-level quota reached. |
| 100005 | WALLET_ADDRESS_BLACKLISTED | Address flagged; ask the user to contact support — do not retry. |
| 100007 | TEE_SIGN_FAILURE | Transient — retry once. |
| 100008 | TEE_SERVICE_UNAVAILABLE | Temporarily unavailable; retry later. |
| 100010 | ORDER_AMOUNT_TOO_SMALL | Below the $1 USD minimum; increase `--amount` and retry. |
| 100012 | LIMIT_ORDER_INSUFFICIENT_BALANCE | Insufficient balance; suggest `wallet balance`. |

## Execution event codes (`executionHistoryList[].code`)

Emitted by the TEE swap-trade engine on an active order. Read the **latest** entry first. Per recognised code the CLI injects `name` (internal, do NOT surface), `message` (surface verbatim, translate), `terminal` (`true` → stop polling and surface; `false` → safe to wait). Unrecognised codes: surface the raw BE `msg` (else `"event code <N>"`).

Reading patterns: latest entry wins; same code recurring every ~10s without a `txHash` = soft retry loop (surface the latest message + repeat count, ask wait/cancel/adjust); `terminal=true` → stop and surface; `terminal=false` repeating 3+ times → treat as user-actionable; code `0` with `txHash` → success (surface `txHash` + explorer link).

Action hints by hot code: `0` success (txHash + explorer) · `3013` top up from-token or smaller amount · `3014` fund the native fee token · `3015` widen `--slippage` · `3016` non-transient (different pair / smaller amount / wider trigger / different chain) · `3017` engine retries (recurring 3+ → treat like 3016) · `3019` terminal, destination token blocklisted · `3020` terminal, wallet flagged · `3023` recreate with longer `--expires-in`. Codes outside this list: follow the CLI's `terminal` field.

## `getOpenOrder` request body (reference only — agent never builds it)

Page-query mode POSTs `getOpenOrder`; the agent only sets mapped flags. Fields: `accountId` (auto, JWT auth), `walletAddressList` (auto, EVM+SOL), `chainIdList` (← `--chain-id`), `orderStatusList` (← `--status`; default 5 non-terminal), `orderTypeList` (unused), `idList` (use `--order-id` detail mode instead), `tokenAddress` (← `--token`, single only), `limit` (← `--limit`, BE default 100 max 100), `cursor` (← `--cursor`, Base64; omit on first page).

## Current limitations

Symbol→address resolution: out of scope (pass addresses). Custom preset (fee tiers, dexId filter): default preset only (MEV via `--mev-protection`). Events stream: `eventCursor` surfaced verbatim, no consumer yet. `cancel --all` channel filter: BE default pass-through. Multi-account batch: out of scope (active account only). `get_account_status`: intentionally not implemented — SA activation/expiry is handled transparently inside the 60018 flow.
