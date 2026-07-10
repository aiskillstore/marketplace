---
name: near-intents
description: Cross-chain token swap integration using NEAR Intents 1Click API. Use when building swap widgets, bridge interfaces, or multi-chain transfers across EVM, Solana, NEAR, TON, Stellar, and Tron.
---

# NEAR Intents Integration

Cross-chain token swaps via 1Click REST API. Get a quote, API provides deposit addresses, you build the deposit transaction and receive the resulting token automatically.

## Quick Start - Pick Your Path

| Use Case | Start Here |
|----------|------------|
| **React App** | `react-swap-widget.md` - Example showing the pattern |
| **Node.js / Script** | `server-example.md` - Example showing the pattern |
| **API Reference** | `api-quote.md` → `api-tokens.md` → `api-status.md` |
| **Chain-specific Deposits** | `deposit-{chain}.md` |

## Integration Flow

```
GET /v0/tokens → POST /v0/quote (dry) → POST /v0/quote (wet) → Deposit TX → POST /v0/deposit/submit → GET /v0/status
```

## Rule Categories

| Priority | Category | Files |
|----------|----------|-------|
| 1 | **Examples** | `react-swap-widget.md`, `server-example.md` |
| 2 | **API** | `api-quote.md`, `api-tokens.md`, `api-status.md`, `api-deposit-submit.md` |
| 3 | **Deposits** | `deposit-evm.md`, `deposit-solana.md`, `deposit-near.md`, `deposit-ton.md`, `deposit-tron.md`, `deposit-stellar.md` |
| 4 | **React Hooks** | `react-hooks.md` |
| 5 | **Advanced** | `intents-balance.md`, `passive-deposit.md` |

## Critical Knowledge

1. **Use `assetId` from /v0/tokens** - never construct manually
2. **`dry: true`** = preview only, **`dry: false`** = get deposit address (valid ~10 min)
3. **Poll status** until terminal: `SUCCESS`, `FAILED`, `REFUNDED`, `INCOMPLETE_DEPOSIT`
4. **Chain-to-chain is default** - `depositType` and `recipientType` default to chain endpoints

## Index

1. **Examples (HIGH)**
   - [react-swap-widget](rules/react-swap-widget.md) - Minimum viable React swap implementation with wagmi
   - [server-example](rules/server-example.md) - Node.js script for server-side swaps

2. **API Reference (CRITICAL)**
   - [api-tokens](rules/api-tokens.md) - Fetch supported tokens, cache result
   - [api-quote](rules/api-quote.md) - Get swap quote, dry=true for preview, dry=false for deposit address
   - [api-deposit-submit](rules/api-deposit-submit.md) - Notify API after deposit to speed up processing
   - [api-status](rules/api-status.md) - Poll until terminal state (SUCCESS, FAILED, REFUNDED)
   - [api-any-input-withdrawals](rules/api-any-input-withdrawals.md) - Query withdrawals for ANY_INPUT quotes

3. **Chain Deposits (HIGH)**
   - [deposit-evm](rules/deposit-evm.md) - Ethereum, Base, Arbitrum, Polygon, BSC transfers
   - [deposit-solana](rules/deposit-solana.md) - Native SOL and SPL token transfers
   - [deposit-near](rules/deposit-near.md) - NEP-141 token transfers via wallet selector
   - [deposit-ton](rules/deposit-ton.md) - Native TON transfers via TonConnect
   - [deposit-tron](rules/deposit-tron.md) - Native TRX and TRC-20 transfers
   - [deposit-stellar](rules/deposit-stellar.md) - Stellar transfers (MEMO REQUIRED)

4. **React Hooks (MEDIUM)**
   - [react-hooks](rules/react-hooks.md) - Reusable hooks for tokens, quotes, status polling

5. **Advanced (LOW)**
   - [intents-balance](rules/intents-balance.md) - Hold balances in intents.near for faster swaps
   - [passive-deposit](rules/passive-deposit.md) - QR code flow for manual transfers

6. **References**
   - [concepts](references/concepts.md) - Swap lifecycle, statuses, CEX warning, authentication

## Resources

- Docs: https://docs.near-intents.org/near-intents/integration/distribution-channels/1click-api
- API Keys: https://partners.near-intents.org/
- OpenAPI: https://1click.chaindefuser.com/docs/v0/openapi.yaml
