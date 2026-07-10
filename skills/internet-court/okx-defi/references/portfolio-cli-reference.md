# OKX DeFi — Portfolio CLI Command Reference

Parameter tables and return schemas for the position-viewing commands.

> `defi support-chains` / `defi support-platforms` and full flow examples live in `invest-cli-reference.md`.

## 1. onchainos defi positions

Get user DeFi holdings overview across protocols and chains.

```bash
onchainos defi positions --address <address> --chains <chains>
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | — | User wallet address |
| `--chains` | Yes | — | Comma-separated chain names (e.g. `"ethereum,bsc,solana"`) |

**Return fields** (per platform entry):

| Field | Type | Description |
|---|---|---|
| `analysisPlatformId` | String | Platform ID — used in `position-detail` and `claim --platform-id` |
| `platformName` | String | Protocol name (e.g. `"Aave V3"`) |
| `chainIndex` | String | Chain identifier |
| `totalValue` | String | Total position value in USD |
| `investedValue` | String | Originally invested value in USD |
| `profitValue` | String | Unrealized profit/loss in USD |
| `platformLogo` | String | Protocol logo URL |
| `investTypeList[]` | Array | Investment types active on this platform |
| `rewardDefiTokenInfo[]` | Array | Pending claimable rewards info |

---

## 2. onchainos defi position-detail

Get detailed DeFi holdings for a specific protocol.

```bash
onchainos defi position-detail \
  --address <address> \
  --chain <chain> \
  --platform-id <id>
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | — | User wallet address |
| `--chain` | Yes | — | Chain name |
| `--platform-id` | Yes | — | Protocol platform ID (`analysisPlatformId` from `positions` output) |

**Return fields** (per position entry):

| Field | Type | Description |
|---|---|---|
| `investmentId` | String | Product ID — used in `redeem`, `claim` |
| `investmentName` | String | Product name |
| `investType` | String | Position type (see investType reference below) |
| `coinAmount` | String | Current redeemable balance in token units |
| `coinUsdValue` | String | Current position value in USD |
| `tokenAddress` | String | Receipt/LP token address |
| `tokenSymbol` | String | Receipt/LP token symbol |
| `apy` | String | Current APY |
| `earnedTokenList[]` | Array | Pending reward tokens and amounts |
| `tokenId` | String | V3 Pool NFT tokenId (if applicable — use in `redeem --token-id`) |
| `tickLower` | String | V3 Pool lower tick (if applicable) |
| `tickUpper` | String | V3 Pool upper tick (if applicable) |
| `healthRate` | String | Lending health rate (LENDING type only) |

**investType values**:

| Value | Description |
|---|---|
| `1` | Save (savings / yield) |
| `2` | Pool (liquidity pool) |
| `3` | Farm (yield farming) |
| `4` | Vaults |
| `5` | Stake |
| `6` | Borrow |
| `7` | Staking |
| `8` | Locked |
| `9` | Deposit |
| `10` | Vesting |

---
