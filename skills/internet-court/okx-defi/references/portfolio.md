# Capability: Portfolio

Read-only viewing of DeFi positions and holdings across protocols and chains.

> Address resolution (Step 0) and address-chain compatibility rules live in the top-level `SKILL.md` — apply them before every command here.

## Quickstart

```bash
# Get DeFi holdings overview across chains
onchainos defi positions \
  --address 0xYourWallet \
  --chains ethereum,bsc,solana

# Get detailed holdings for a specific protocol (analysisPlatformId from positions output)
onchainos defi position-detail \
  --address 0xYourWallet \
  --chain ethereum \
  --platform-id 67890
```

## Command Index

| # | Command | Description |
|---|---------|-------------|
| 1 | `onchainos defi support-chains` | Get supported chains for DeFi |
| 2 | `onchainos defi support-platforms` | Get supported platforms for DeFi |
| 3 | `onchainos defi positions --address <addr> --chains <chains>` | Get user DeFi holdings overview |
| 4 | `onchainos defi position-detail --address <addr> --chain <chain> --platform-id <id>` | Get detailed holdings for a protocol |

## Chain Support

| Chain | Name / Aliases | chainIndex |
|-------|----------------|-----------|
| Ethereum | `ethereum`, `eth` | `1` |
| BSC | `bsc`, `bnb` | `56` |
| Polygon | `polygon`, `matic` | `137` |
| Arbitrum | `arbitrum`, `arb` | `42161` |
| Base | `base` | `8453` |
| X Layer | `xlayer`, `okb` | `196` |
| Avalanche | `avalanche`, `avax` | `43114` |
| Optimism | `optimism`, `op` | `10` |
| Fantom | `fantom`, `ftm` | `250` |
| Sui | `sui` | `784` |
| Tron | `tron`, `trx` | `195` |
| TON | `ton` | `607` |
| Linea | `linea` | `59144` |
| Scroll | `scroll` | `534352` |
| zkSync | `zksync` | `324` |
| Solana | `solana`, `sol` | `501` |

## Operation Flow

### Step 1: Identify Intent

| User says | Action |
|-----------|--------|
| View positions / portfolio / holdings | `onchainos defi positions` |
| View detail for a protocol | `onchainos defi position-detail` |
| Redeem / claim after viewing | Switch to the **Invest** capability (`references/invest.md`) |

### Step 2: Collect Parameters

- **Missing wallet address** → resolve via `SKILL.md` Step 0 (wallet status → wallet addresses), or ask user if not logged in
- **Missing chains** → ask user which chains to query, or suggest common ones (ethereum, bsc, solana)
- **Missing platform-id** → run `defi positions` first to get `analysisPlatformId`

### Step 3: Display Results

#### Displaying Positions Results

When displaying `defi positions` output, you MUST use **exactly** these columns in this order — no substitutions, no omissions:

| # | Platform | analysisPlatformId | Chains | Positions | Value(USD) |
|---|---------|--------------------|----|--------|-----------|
| 1 | Aave V3 | 12345 | ETH,BSC | 2 | $120.00 |

Rules:
- **`analysisPlatformId` is MANDATORY in every row** — users must copy this value to run `position-detail`
- **Never omit, hide, or replace `analysisPlatformId`** with any other field
- **Never group platforms** — show every platform as its own row regardless of value size
- Raw JSON path: `walletIdPlatformList[*].platformList[*]` — each element is one platform row
  - `platformName` → Platform
  - `analysisPlatformId` → analysisPlatformId
  - `networkBalanceList[*].network` → Chains (join with comma)
  - `investmentCount` → Positions
  - `currencyAmount` → Value(USD)

#### Displaying Position Detail Results

**Output shape**: `{ "ok": true, "data": [ { "walletIdPlatformDetailList": [...] }, ... ] }` — `data` is an **array**. Never call `.get()` on `data` directly; iterate over it as a list.

When displaying `defi position-detail` output, render all tokens in a **single flat table** with these exact columns:

| Type | Asset | Amount | Value(USD) | investmentId | aggregateProductId | Token Contract | Rewards |
|------|------|------|-----------|--------------|--------------------|-----------|------|
| Supply | USDT | 1.002285 | $1.0025 | 127 | 71931 | 0x970223...7 | 0.000080 AVAX |
| Pending | sAVAX | 0.00000091 | $0.000012 | – | – | – | Platform reward |

Rules:
- Each token row is one row; merge in `investmentId` and `aggregateProductId` from its parent investment entry
- **`investmentId` is MANDATORY in every row** — users need it for `redeem`/`claim` (via the **Invest** capability)
- `aggregateProductId` — show if present, otherwise `–`
- Token Contract: show the **full contract address** without truncation; show `–` if native/empty
- Rewards: show pending reward amount + symbol if present, `–` if none; for platform rewards show `Platform reward`
- Type: map investType → Supply/Borrow/Stake/Farm/Pool etc; pending rewards row uses `Pending`
- **Health rate**: show separately below the table with warning if `healthRate < 1.5`

#### V3 Pool Positions — Extra Fields

For V3 Pool positions (`positionList` present), show an additional section per position:

| tokenId | Status | Range | tickLower | tickUpper |
|---------|--------|-------|-----------|-----------|
| 93828 | ACTIVE | 0.892 – 0.992 USDC/DAI | -33500 | -30450 |

- `tokenId`: from `positionList[].tokenId`
- `positionStatus`: `ACTIVE` or `INACTIVE`
- `range`: from `positionList[].range`
- `tickLower` / `tickUpper`: from `positionList[].rangeInfo.tickLower` / `rangeInfo.tickUpper`
- These fields are critical for V3 operations (add liquidity, withdraw, collect V3 fees)

## investType Reference

| investType | Description |
|------------|-------------|
| 1 | Save (savings/yield) |
| 2 | Pool (liquidity pool) |
| 3 | Farm (yield farming) |
| 4 | Vaults |
| 5 | Stake |
| 6 | Borrow |
| 7 | Staking |
| 8 | Locked |
| 9 | Deposit |
| 10 | Vesting |

## Post-execution Suggestions

| Just completed | Suggest |
|----------------|---------|
| `defi positions` | 1. View detail → `defi position-detail`  2. Redeem → Invest capability  3. Claim rewards → Invest capability |
| `defi position-detail` | 1. Redeem position → Invest capability with `investmentId` from table  2. Claim rewards → Invest capability  3. Add more → Invest capability |
| `defi position-detail` (V3 Pool) | 1. View depth chart → `defi depth-price-chart --investment-id <id>` (Invest capability)  2. View price history → `defi depth-price-chart --investment-id <id> --chart-type PRICE` |

## Troubleshooting

> Errors and edge cases: read `references/portfolio-troubleshooting.md`.

## Portfolio-specific Notes

- `defi positions` uses `--chains` (plural, comma-separated, e.g. `--chains ethereum,bsc`) — do NOT use `--chain`
- `defi position-detail` uses `--chain` (singular) — do NOT use `--chains`
- `position-detail` requires `analysisPlatformId` from `positions` output as `--platform-id`
- The CLI resolves chain names automatically (`ethereum` → `1`, `bsc` → `56`, `solana` → `501`)
