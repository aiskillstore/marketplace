# Capability: Invest

Multi-chain DeFi product discovery and investment execution. The CLI handles precision conversion, multi-step orchestration, and validation internally.

For CLI parameter details, see `references/invest-cli-reference.md`.

> Address resolution (Step 0) and address-chain compatibility rules live in the top-level `SKILL.md` — apply them before every command here.

## Command Index

| # | Command | Description |
|---|---------|-------------|
| 1 | `defi support-chains` | Get supported chains for DeFi |
| 2 | `defi support-platforms` | Get supported platforms for DeFi |
| 3 | `defi list` | List top DeFi products by APY |
| 4 | `defi search --token <tokens> [--platform <names>] [--chain <chain>] [--product-group <group>]` | Search DeFi products |
| 5 | `defi detail --investment-id <id>` | Get full product details |
| 6 | `defi invest --investment-id <id> --address <addr> --token <symbol_or_addr> --amount <minimal_units> [--chain <chain>] [--slippage <pct>] [--tick-lower <n>] [--tick-upper <n>] [--token-id <nft>]` | One-step deposit (CLI handles prepare + precision + calldata) |
| 7 | `defi withdraw --investment-id <id> --address <addr> --chain <chain> [--ratio <0-1>] [--amount <minimal_units>] [--token-id <nft>] [--platform-id <pid>] [--slippage <pct>]` | One-step withdrawal (CLI handles position lookup + calldata) |
| 8 | `defi collect --address <addr> --chain <chain> --reward-type <type> [--investment-id <id>] [--platform-id <pid>] [--token-id <nft>] [--principal-index <idx>]` | One-step reward claim (CLI handles reward check + calldata) |
| 9 | `defi rate-chart --investment-id <id> [--time-range <range>]` | Historical APY chart data |
| 10 | `defi tvl-chart --investment-id <id> [--time-range <range>]` | Historical TVL chart data |
| 11 | `defi depth-price-chart --investment-id <id> [--chart-type <type>] [--time-range <range>]` | V3 Pool depth or price history chart |

> `defi positions` / `defi position-detail` (viewing) are documented in the **Portfolio** capability (`references/portfolio.md`) — but you will call them here as mandatory pre-steps before withdraw/collect.

## Investment Types

| productGroup | Description |
|-------------|-------------|
| `SINGLE_EARN` | Single-token yield (savings, staking, vaults) |
| `DEX_POOL` | Liquidity pools (Uniswap V2/V3, PancakeSwap, etc.) |
| `LENDING` | Lending / borrowing (Aave, Compound, etc.) |

## Operation Flow

### Deposit (invest)

```
1. defi search --token USDC --chain ethereum       → pick investmentId
2. defi detail --investment-id <id>                 → confirm APY/TVL, get underlyingToken[].tokenAddress
3. token search --query <tokenAddress> --chains <chain>  → get decimal (e.g. 6) for amount conversion
4. Ask user for amount → convert: userAmount × 10^decimal (e.g. 100 USDC → 100000000)
5. Check wallet balance (okx-agentic-wallet) → if insufficient, warn user and stop
6. defi invest --investment-id <id> --address <addr> --token USDC --amount 100000000
   → CLI returns calldata (APPROVE + DEPOSIT steps)
7. User signs and broadcasts each step in order
```

> **Token decimal**: Get `tokenAddress` from `defi detail` → `underlyingToken[].tokenAddress`, then use `token search --query <tokenAddress>` to get `decimal`. Same approach as DEX swap.
>
> **CRITICAL — Balance check is REQUIRED before calling `defi invest`.** You MUST call `okx-agentic-wallet` to verify the user has sufficient balance of the deposit token BEFORE generating calldata. If balance is insufficient, STOP and warn the user. Do NOT proceed to `defi invest` without confirming balance. Skipping this step wastes gas and results in failed on-chain transactions.

### Withdraw

> **CRITICAL — position-detail is MANDATORY before withdraw.** You MUST call `defi position-detail` immediately before every `defi withdraw`, even if you already have position data from a previous call. Do NOT reuse stale position-detail results.

```
1. defi positions --address <addr> --chains ethereum
2. defi position-detail --address <addr> --chain ethereum --platform-id <pid>
   → MUST be called fresh — get investmentId, tokenPrecision, coinAmount (current balance)
3. Full exit:
   defi withdraw --investment-id <id> --address <addr> --chain ethereum --ratio 1 --platform-id <pid>
   Partial exit (convert coinAmount to minimal units: amount × 10^tokenPrecision):
   defi withdraw --investment-id <id> --address <addr> --chain ethereum --amount <minimal_units> --platform-id <pid>
4. User signs and broadcasts
```

> **Partial exit --amount**: position-detail returns `coinAmount` in human-readable (e.g. "2.3792") and `tokenPrecision` (e.g. 6). Convert to minimal units: `floor(2.3792 × 10^6) = 2379200` → `--amount 2379200`.

### Claim Rewards

> **CRITICAL — position-detail is MANDATORY before collect.** You MUST call `defi position-detail` immediately before every `defi collect`, even if you already have position data from a previous call in the conversation. Position data (rewards, investmentId, platformId, tokenId) changes after each on-chain operation (withdraw, previous collect, etc.), so stale data leads to wrong parameters or failed transactions. Do NOT skip this step. Do NOT reuse position-detail results from earlier in the conversation.

```
1. defi positions --address <addr> --chains ethereum
2. defi position-detail --address <addr> --chain ethereum --platform-id <pid>
   → MUST be called fresh — do NOT reuse prior results
3. defi collect --address <addr> --chain ethereum --reward-type REWARD_INVESTMENT --investment-id <id> --platform-id <pid>
   → CLI returns calldata (or skips if no rewards)
4. User signs and broadcasts
```

### V3 Pool Deposit

```
1. defi search --token USDT --platform PancakeSwap --chain bsc --product-group DEX_POOL
2. defi detail --investment-id <id>
3. (Optional) defi depth-price-chart --investment-id <id>
   → show liquidity depth distribution to help user pick tick range
4. Ask user for amount and tick range
5. Check wallet balance (okx-agentic-wallet) → if insufficient, warn user and stop
6. defi invest --investment-id <id> --address <addr> --token USDT --amount 100000000 --range 5
   → CLI handles calculate-entry internally, returns calldata
7. User signs and broadcasts
```

### View Chart Data

Use chart commands to analyze product trends before investing or to monitor existing positions.

**APY History** — check yield trend before depositing:
```
defi rate-chart --investment-id <id> --time-range MONTH
```
- Time ranges: `WEEK` (default), `MONTH`, `SEASON` (3 months), `YEAR`. `DAY` is V3 Pool only.
- Returns: `timestamp`, `rate` (APY), `bonusRate` (extra rewards), `limitValue` (1=peak, -1=trough).

**TVL History** — evaluate pool size stability:
```
defi tvl-chart --investment-id <id> --time-range SEASON
```
- Time ranges: same as rate-chart.
- Returns: `chartVos[]` with `timestamp`, `tvl` (USD), `limitValue`.

**V3 Depth Chart** — see liquidity concentration to pick optimal tick range:
```
defi depth-price-chart --investment-id <id>
```
- Returns: `tick`, `liquidity`, `liquidityNet`, `token0Price`, `token1Price` per tick.
- No `--time-range` parameter — DEPTH mode always returns current snapshot.
- Use this before V3 Pool deposit to identify where liquidity is concentrated and choose `tickLower`/`tickUpper` accordingly.

**V3 Price History** — see historical relative price between token0 and token1:
```
defi depth-price-chart --investment-id <id> --chart-type PRICE --time-range WEEK
```
- Chart types: `DEPTH` (default), `PRICE`.
- `--time-range` only applies to PRICE mode: `DAY` (default), `WEEK`.
- Returns: `token0Price`, `token1Price`, `timestamp` per data point.

### Sign & Broadcast Calldata

After `invest`/`withdraw`/`collect` returns `dataList`, execute each step via one of two paths:

**Path A (user-provided wallet)**: user signs externally → broadcast via gateway
```bash
# For each dataList step:
# 1. User signs the tx externally using dataList[N].to, dataList[N].serializedData, dataList[N].value
# 2. Broadcast:
onchainos gateway broadcast --signed-tx <signed_hex> --address <addr> --chain <chain>
# 3. Poll until confirmed:
onchainos gateway orders --address <addr> --chain <chain> --order-id <orderId>
# → wait for txStatus=2, then proceed to next step
```

**Path B (Agentic Wallet)**: sign & broadcast via `wallet contract-call`

EVM chains (Ethereum, BSC, Polygon, Arbitrum, Base, etc.):
```bash
onchainos wallet contract-call \
  --to <dataList[N].to> \
  --chain <chainIndex> \
  --input-data <dataList[N].serializedData> \
  --value <value_in_UI_units> \
  --biz-type defi
```

EVM (XLayer):
```bash
onchainos wallet contract-call \
  --to <dataList[N].to> \
  --chain 196 \
  --input-data <dataList[N].serializedData> \
  --value <value_in_UI_units> \
  --biz-type defi
```

Solana:
```bash
onchainos wallet contract-call \
  --to <dataList[N].to> \
  --chain 501 \
  --unsigned-tx <dataList[N].serializedData> \
  --biz-type defi
```

`contract-call` handles TEE signing and broadcasting internally — no separate broadcast step needed.

**`--value` unit conversion**: `dataList[].value` is in minimal units (wei). `contract-call --value` expects UI units. Convert: `value_UI = value / 10^nativeToken.decimal` (e.g. 18 for ETH/POL, 9 for SOL). If `value` is `""`, `"0"`, or `"0x0"`, use `"0"`.

**`--chain` mapping**: `contract-call` and `gateway broadcast` require `realChainIndex` (e.g. `1`=Ethereum, `137`=Polygon, `56`=BSC, `501`=Solana, `196`=XLayer).

**Execution rules**:
- Execute `dataList[0]` first, then `dataList[1]`, etc. Never in parallel.
- Wait for on-chain confirmation before next step (Path A: `txStatus=2`; Path B: `contract-call` returns txHash).
- If any step fails, stop all remaining steps and report which succeeded/failed.

> `invest`/`withdraw`/`collect` only return **unsigned calldata** — they do NOT broadcast. The CLI never holds private keys.

## Displaying Search / List Results

| # | Platform | Chain | investmentId | Name | APY | TVL |
|---|---------|-------|-------------|------|-----|-----|
| 1 | Aave V3 | ETH | 9502 | USDC | 1.89% | $3.52B |

- `investmentId` is **MANDATORY** in every row
- `rate` is decimal → multiply by 100 and append `%`
- `tvl` → format as human-readable USD ($3.52B, $537M)
- Display data as-is — do NOT editorialize on APY values

## rewardType Reference

| rewardType | When to use | Required params |
|------------|-------------|-----------------|
| `REWARD_PLATFORM` | Protocol-level rewards (e.g. AAVE token) | `--platform-id` |
| `REWARD_INVESTMENT` | Product mining/staking rewards | `--investment-id` + `--platform-id` |
| `V3_FEE` | V3 trading fee collection | `--investment-id` + `--token-id` |
| `REWARD_OKX_BONUS` | OKX bonus rewards | `--investment-id` + `--platform-id` |
| `REWARD_MERKLE_BONUS` | Merkle proof-based bonus | `--investment-id` + `--platform-id` |
| `UNLOCKED_PRINCIPAL` | Unlocked principal after lock | `--investment-id` + `--principal-index` |

## Key Protocol Rules

- **Aave borrow**: uses `callDataType=WITHDRAW` internally — do not expose to user
- **Aave repay**: uses `callDataType=DEPOSIT` internally — do not expose to user
- **V3 Pool exit**: pass `--token-id` + `--ratio` (e.g. `--ratio 1` for full exit)
- **Partial withdrawal (non-V3)**: pass `--amount` for the exit amount
- **Full withdrawal**: `--ratio 1`

## Post-execution Suggestions

| Just completed | Suggest |
|----------------|---------|
| `defi list` / `defi search` | View details → `defi detail`, or start deposit flow |
| `defi detail` | Check trends → `defi rate-chart` / `defi tvl-chart`, or proceed → `defi invest` |
| `defi detail` (V3 Pool) | View depth → `defi depth-price-chart`, check price history → `defi depth-price-chart --chart-type PRICE` |
| `defi invest` success | View positions → Portfolio capability (`references/portfolio.md`), or search more |
| `defi withdraw` success | Check positions → Portfolio capability, or check balance → `okx-agentic-wallet` |
| `defi collect` success | Check positions → Portfolio capability, or swap rewards → `okx-agentic-wallet` |

## Troubleshooting

> Error codes and failure handling: read `references/invest-troubleshooting.md`.

## Invest-specific Notes

- `--amount` must be in **minimal units** (integer). Convert: userAmount × 10^tokenPrecision. Example: 0.1 USDC (precision=6) → `--amount 100000`. Get tokenPrecision from `defi detail` or `defi position-detail`
- `--slippage` default is `"0.01"` (1%); suggest `"0.03"`–`"0.05"` for volatile V3 pools
- **CRITICAL — Solana transaction expiry**: Solana DeFi transactions use base58-encoded VersionedTransaction with a blockhash that expires in ~60 seconds. After receiving calldata, you MUST warn the user: "This Solana transaction must be signed and broadcast within 60 seconds or it will expire. Please sign immediately." Do NOT proceed to other conversation without delivering this warning first.
- **CRITICAL — High APY risk warning**: When displaying search/list results, if any product has APY > 50% (rate > 0.5), you MUST warn the user: "WARNING: This product shows APY above 50%, which indicates elevated risk (potential impermanent loss, smart contract risk, or unsustainable rewards). Proceed with caution." Do NOT silently display high-APY products without this warning.
- User confirmation required before every invest/withdraw/collect execution
- Address used for calldata generation MUST match the signing address
