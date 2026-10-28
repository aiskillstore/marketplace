# Strategy Troubleshooting

## Error Codes

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
| 100010 | ORDER_AMOUNT_TOO_SMALL | Below the $1 USD minimum. For `create-limit` the CLI normalizes this to a `belowMinimum` response at exit 0 (see create-limit Output) — you won't see it as an error there; elsewhere, increase `--amount` and retry. |
| 100012 | LIMIT_ORDER_INSUFFICIENT_BALANCE | Insufficient balance; suggest `wallet balance`. |

## Failure Diagnostics

Emitted by the TEE swap-trade engine on an active order. Read the **latest** entry first. Per recognised code the CLI injects `name` (internal, do NOT surface), `message` (surface verbatim, translate), `terminal` (`true` → stop polling and surface; `false` → safe to wait). Unrecognised codes: surface the raw BE `msg` (else `"event code <N>"`).

Reading patterns: latest entry wins; same code recurring every ~10s without a `txHash` = soft retry loop (surface the latest message + repeat count, ask wait/cancel/adjust); `terminal=true` → stop and surface; `terminal=false` repeating 3+ times → treat as user-actionable; code `0` with `txHash` → success (surface `txHash` + explorer link).

Action hints by hot code: `0` success (txHash + explorer) · `3013` top up from-token or smaller amount · `3014` fund the native fee token · `3015` widen `--slippage` · `3016` non-transient (different pair / smaller amount / wider trigger / different chain) · `3017` engine retries (recurring 3+ → treat like 3016) · `3019` terminal, destination token blocklisted · `3020` terminal, wallet flagged · `3023` the fixed TTL expired; ask whether to create a new order. Codes outside this list: follow the CLI's `terminal` field.
