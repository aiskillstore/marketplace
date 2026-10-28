# Limit-Order Strategy

## Module Description

Price-triggered limit orders on the Agentic Wallet (`create-limit`, `cancel`, `list`, `resume`). Orders are stored on the TEE and execute automatically when the trigger fires. Distinct from swap (market orders, immediate execution). Requires an authenticated session. SA activation (Trader Mode upgrade) is done transparently by the CLI on `UPGRADE_REQUIRED` — never ask the user to activate it.

Symbol→address resolution is out of scope — pass `--from-token` / `--to-token` as contract addresses directly. If a venue is named (Uniswap, PancakeSwap, Raydium, …) → re-route to `okx-dapp-discovery`; this is OKX-aggregated limit orders only.

## Flow

### Boundary vs Swap

| User intent | Where |
|---|---|
| "Swap X for Y now" / "Buy 0.5 ETH with USDC" | swap (market order) |
| "Buy ETH if it dips to $2000" / "Sell when ETH hits $5000" / "Take profit at X" / "Stop loss at Y" | this domain |
| "Cancel my pending order" / "What limit orders do I have?" | this domain |

## Chain Name Support

### Supported Chains (6 only)

Ethereum (`1`), BSC (`56`), X Layer (`196`), Solana (`501`), Base (`8453`), Arbitrum (`42161`). When the user names a chain, resolve to chainIndex and check this list. If not supported (Polygon, Optimism, Avalanche, Linea, Sui, Tron, …), respond directly and do NOT call the CLI or open Step 1:
> Strategy orders are only supported on Ethereum / BSC / X Layer / Solana / Base / Arbitrum right now. `<requested chain>` is not supported — pick one of these to continue.

## Security

### create-limit — Two-Step Confirmation (agent MUST follow)

`create-limit` is a write op. Present a confirmation summary and only call the CLI after explicit confirmation. Strategy type is derived inside the CLI from `(--direction, --trigger-price, current price)` — the agent never passes or computes it.

**Step 0 — From-token price for the Value estimate (before Step 1).** For the Step 1 "Value" line, get the from-token USD price: stablecoin (USDT/USDC/USDG/USDe/DAI/FDUSD/…) → assume `from_price ≈ 1.0` (no HTTP); else `onchainos market price --chain <chain> --address <from_token>`, read `data[0].price`. Carry `from_price` forward for Step 1. **Do NOT run a $1-minimum gate here** — the CLI now enforces the $1 USD minimum itself (a local pre-check plus backend `100010` normalization) and returns a structured `belowMinimum` response at exit 0; you render that in Step 2, never compute the threshold client-side.

**Step 1 — Order summary** (5 categories, none may be dropped; prose organised freely):

| # | Category | Content |
|---|---|---|
| 1 | Chain | Human-readable name from `--chain-id`. |
| 2 | Order Type | Display label per the strategyType enum (translate). |
| 3 | From token | Symbol + Amount (raw `--amount`). |
| 4 | To token | Symbol; Trigger Price (USD-denominated); Estimated Amount; Value (est. USD). |
| 5 | Slippage | `Default 15%` (user didn't mention) or `User-specified X%`. |

Estimated Amount / Value formulas — Buy (BUY_DIP / CHASE_HIGH): `Estimated Amount = from_amount ÷ trigger_price`; `Value = from_amount × from_token_USD_price` (stablecoin ≈ from_amount). Sell (TAKE_PROFIT / STOP_LOSS): `Estimated Amount = from_amount × trigger_price`; `Value = from_amount × trigger_price` (if to is a stablecoin). These are agent estimates from `trigger_price`, NOT BE quotes — never present as actual fill amounts.

Slippage: user didn't mention → display `Default 15%` and OMIT `--slippage` (CLI default 15). User said "slippage X%" → display `User-specified X%` and pass `--slippage X`.

After the 5 categories and before the reply prompt, surface the expiry note: `If the trigger condition is not met within 7 days, this order auto-expires.` Then `Reply confirm / change / cancel.`

Structural example:
```
1. Chain: Arbitrum
2. Order Type: Buy Dip
3. From: USDC 10
4. To:
   - Symbol: ARB
   - Trigger Price: $0.10
   - Estimated Amount: 100 ARB
   - Value: $10
5. Slippage: 15% (default)

If the trigger condition is not met within 7 days, this order auto-expires.

Reply confirm / change / cancel.
```

**Step 2 — Handle the reply.** confirm/yes/submit → call `strategy create-limit`. change (e.g. "amount = 5", "trigger to 0.08") → update the field and re-render Step 1. cancel/abort → do not call the CLI; acknowledge discarded.

**belowMinimum response.** If `create-limit` returns `data.belowMinimum == true` (order below the $1 USD minimum — the CLI short-circuits at exit 0, no order created; same shape whether caught by the local pre-check or backend `100010`), surface **exactly this single line, no extra prose** (no math, no $1 mention, no echo, no apology): `Minimum order amount: <minFromAmount> <fromSymbol>` — both values read verbatim from the response; translate only the prefix per Display Labels. Wait for a larger `--amount`, then re-submit.

`--trigger-price` is a USD price — make this clear to avoid confusion with an exchange rate.

## Render Rules

### Display Labels & Output Language (single source of truth)

Canonical Display labels are the only strings the agent may surface. The CLI returns `statusLabel` directly for status; for `strategyType` look up the label from the enum table in [strategy-cli-reference.md](strategy-cli-reference.md).

| Surface | Canonical EN Display labels |
|---|---|
| `strategyType` (4) | `Buy Dip` / `Take Profit` / `Stop Loss` / `Buy Above` |
| `status` (9) | `Expired` / `Cancelling` / `Cancelled` / `Failed` / `Trading` / `Completed` / `Creating` / `Active` / `Suspended` |

Match the user's conversation language — translate the canonical English label at output time. Never: mix two languages in one label; expose the enum name (`BUY_DIP`, `COMPLETED`, …) or the CLI flag value (`buy_dip`, `completed`, …); pass through the raw `statusLabel` untranslated for a non-English user. `CHASE_HIGH` renders as **`Buy Above`** (not "Chase High"). `SPEEDING_UP` (-4) is not a valid filter or display value.

### list — Rendering (general "show my orders" with no status qualifier)

1. Run `onchainos strategy list --limit 10` (no `--status` → CLI applies the non-terminal set `[-3,0,2,3,4]` server-side). Always `--limit 10` for general queries.
2. Render `data.list` as a Markdown table with **exactly these 8 columns** (locked):

   | Order id | Order Status | Order Type | Estimated Amount | To Token addr | Value | Trigger price | Expire after |
   |---|---|---|---|---|---|---|---|

   Mapping: Order id = `orderId`; Order Status = `statusLabel` (translate); Order Type = strategyType label (translate); Estimated Amount = `toToken.tokenAmount` + ` ` + `toToken.tokenSymbol`; To Token addr = `toToken.tokenContractAddress` truncated first-6+last-4 (EVM `0x1234...cdef`; base58 first 6 + `...` + last 4; <10 chars → verbatim); Value = `toToken.tokenUsd` as `<n> USD`; Trigger price = `triggerInfo.triggerPrice` prefixed `$` (empty → `triggerInfo.triggerRate`); Expire after = `expireTime` (13-digit ms UTC) converted to the user's local timezone, `MM/DD/YYYY HH:MM:SS` 24-hour.

   Sample: `| 17262791359882688 | Active | Take Profit | 0.2 SOL | 9xQeWv...vEjz | 16 USD | $80 | 05/15/2026 17:50:49 |`

3. After the table, append one combined reminder (include the pagination line only when `nextCursor` is non-empty; translate):
   > Showing live orders by default (10 per page).
   > - Reply "next page" to load more.
   > - To filter by a specific state, ask for orders by their Display label — e.g. `Completed`, `Cancelled`, `Failed`, `Expired`.
4. "next page" → re-run `--limit 10 --cursor <nextCursor>`, same table.
5. User names a status (any of the 9 Display labels) → re-run `list --limit 10 --status <label>`, same table; drop the status-filter bullet.

To see terminal orders, pass `--status` explicitly (see the status enum in [strategy-cli-reference.md](strategy-cli-reference.md)).

### Resume

`strategy resume` (no ids) auto-discovers all `SUSPENDED` + `canResume=true` on the active wallet; `--order-ids id1,id2` for explicit. After resume, advise that orders whose trigger was already met may execute immediately — re-query with `list` to confirm.

### Async Wait Pattern

`create-limit`, `cancel`, `resume` return after the request is **accepted**, not after terminal state. Pass **`--wait`** to fold the terminal-state check into the call: the CLI sleeps a fixed 3 s (covers all supported chains — never keyed to `estimatedWaitTime`), re-queries each affected order, and merges the result — `settled` (bool; for multi-order cancel/resume it is the logical AND across orders, with a per-order `orders[]` array), `status`, `statusLabel`, plus settled-only `transactionInfo` / `executionHistoryList` / `fromToken` / `toToken` / `orderStatusUpdateTime`. If `settled == false`, surface the partial state — do not loop indefinitely. **NEVER**: combine `cancel --all` with `--wait` — the CLI rejects it (`code: invalid_input`, `field: wait`, exit 1) before any cancel is sent; use `--order-id` / `--order-ids` with `--wait`, or omit `--wait` for bulk cancel. Without `--wait`, the response is acceptance-only; re-query `strategy list --order-id <orderId>` yourself if you need terminal state. Solana settles immediately (`estimatedWaitTime=0`).

### SA Activation Transparency

On `create-limit` / `resume`, if BE returns `60018` (`UPGRADE_REQUIRED`), the CLI activates Trader Mode transparently and retries once — the user sees `Trader Mode activated.` then normal output. Never ask the user to activate it first. If activation fails, the command aborts with the activation error — suggest `onchainos wallet status`.

## Troubleshooting

### Error Handling

On **any** BE error code (`100`, `100010`, `10019`, `10026`, `60002`, `60006`, `60009`, `60018`, …) or execution-event code from a `create-limit` / `cancel` / `list` / `resume` response, load [strategy-cli-reference.md](strategy-cli-reference.md) and map the code → recommended action via its **Error code → agent action** and **Execution event codes** tables. Match by integer code, not message text.

## CLI Reference

- [strategy-cli-reference.md](strategy-cli-reference.md)
