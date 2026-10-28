---
name: okx-defi
description: "Discover and manage OKX-aggregated DeFi products and positions across protocols and chains. Use for generic or venue-agnostic yield, APY, or TVL discovery and history; DeFi deposits, staking, liquidity, withdrawals, rewards, lending, CLMM analysis; and DeFi portfolio or position views. Requests targeting a named protocol belong to DApp discovery. Triggers include earn yield, best APY, DeFi product, APY/TVL history, deposit, stake, withdraw, redeem, provide or remove liquidity, claim rewards, borrow or repay, CLMM, V3 liquidity charts, DeFi portfolio, and DeFi holdings."
license: MIT
metadata:
  author: okx
  version: "4.6.6"
  homepage: "https://web3.okx.com"
---

# OKX DeFi

Discover and manage multi-chain, OKX-aggregated DeFi products and positions through the `onchainos defi` CLI group.

## Preflight

Preflight checks: At the start of each thread, complete the checks in `../okx-agentic-wallet/_shared/preflight.md`. If missing, read `_shared/preflight.md`.

## Intent Routing

Load only the reference files required by the selected route.

| User Intent | Reference |
|---|---|
| Discover / search DeFi products, find best APY | [invest.md](references/invest.md) |
| Product detail (APY, TVL, accepted tokens) | [invest.md](references/invest.md) |
| Deposit / stake / provide liquidity | [invest.md](references/invest.md) |
| Withdraw / redeem a position (full or partial) | [invest.md](references/invest.md) |
| Claim rewards (platform / investment / V3 fee / bonus / unlocked principal) | [invest.md](references/invest.md) |
| APY history, TVL history, V3 depth / price charts | [invest.md](references/invest.md) |
| View DeFi positions / holdings overview | [portfolio.md](references/portfolio.md) |
| Per-protocol position detail | [portfolio.md](references/portfolio.md) |
| Exact parameters / return schemas — invest, shared support, and charts commands | [invest-cli-reference.md](references/invest-cli-reference.md) |
| Exact parameters / return schemas — positions commands | [portfolio-cli-reference.md](references/portfolio-cli-reference.md) |
| Errors / failed deposits / expired calldata | [invest-troubleshooting.md](references/invest-troubleshooting.md) |
| Errors / empty positions / address-format issues | [portfolio-troubleshooting.md](references/portfolio-troubleshooting.md) |

Typical flow spans both: view positions (Portfolio) → redeem or claim (Invest). Read both reference files when the request chains them.

Route a named third-party DApp request—including protocol-specific APY, TVL,
volume, history, or timeframe analysis—to `okx-dapp-discovery`. Generic
cross-protocol yield/APY/TVL and V3-liquidity analysis stays here. Route token
search/price/chart requests to `okx-dex-market`, and spot swaps, wallet
balances, login, contract calls, or transaction broadcasts to
`okx-agentic-wallet`.

## Chain Name Support

The CLI resolves chain names automatically (for example, `ethereum` → `1`, `bsc` → `56`, `solana` → `501`). Use the Chain Support table in [portfolio.md](references/portfolio.md) for the DeFi-specific aliases.

## Security

### Address Resolution

When the user does NOT provide a wallet address, resolve it automatically from the Agentic Wallet **before** running any defi command:

```
1. onchainos wallet status          → check if logged in, get active account
2. onchainos wallet addresses       → get addresses grouped by chain category:
                                       - XLayer addresses
                                       - EVM addresses (Ethereum, BSC, Polygon, etc.)
                                       - Solana addresses
3. Match address to target chain:
   - EVM chains → use EVM address
   - Solana     → use Solana address
   - XLayer     → use XLayer address
```

Rules:
- If the user provides an explicit address, use it directly — skip this step
- If wallet is not logged in, ask the user to log in first (→ `okx-agentic-wallet`) or provide an address manually
- If the user says "check all accounts" or "all wallets", use `wallet balance --all` to get all account IDs, then `wallet switch <id>` + `wallet addresses` for each account
- Always confirm the resolved address with the user before proceeding if the account has multiple addresses of the same type

### Address-Chain Compatibility

The `--address` and chain parameters must be compatible. EVM addresses (`0x…`) can only query EVM chains; Solana addresses (base58) can only query `solana`. Never mix them — the API will return error 84019 (Address format error).

- `0x…` address → only pass EVM chains: `ethereum,bsc,polygon,arbitrum,base,xlayer,avalanche,optimism,fantom,linea,scroll,zksync`
- base58 address → only pass `solana`
- Sui address → only pass `sui`; Tron address (`T…`) → only pass `tron`; TON address → only pass `ton`
- If the user wants positions across both EVM and Solana, make **two separate calls** with the respective addresses

## Global Notes

- The wallet address parameter for ALL defi commands is `--address`
- `defi positions` uses `--chains` (plural, comma-separated); `defi position-detail` uses `--chain` (singular)
- Before reporting completion, verify the selected command succeeded, apply the output format and safety checks from its routed reference, and report any partial or failed on-chain step explicitly.
