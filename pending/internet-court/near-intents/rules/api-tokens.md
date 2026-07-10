---
title: GET /v0/tokens
impact: CRITICAL
tags: api, tokens
---

Fetch supported tokens. Cache result (changes infrequently).

```typescript
const response = await fetch('https://1click.chaindefuser.com/v0/tokens');
const tokens = await response.json();
```

## Response

```typescript
interface Token {
  assetId: string;          // Use in originAsset/destinationAsset
  decimals: number;         // For amount conversion
  blockchain: string;       // 'eth', 'sol', 'near', 'base', 'arb', 'bsc', etc.
  symbol: string;           // 'USDC', 'ETH', 'wNEAR'
  price: string;            // USD price
  priceUpdatedAt: string;   // ISO timestamp
  contractAddress?: string; // Token contract (for transfers)
}
```

## Helper

```typescript
const findToken = (tokens: Token[], symbol: string, blockchain: string) =>
  tokens.find(t =>
    t.symbol.toLowerCase() === symbol.toLowerCase() &&
    t.blockchain === blockchain
  );

// Example
const usdcEth = findToken(tokens, 'USDC', 'eth');
// usdcEth.assetId = "nep141:eth-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.omft.near"
// usdcEth.contractAddress = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
```

**Important:** Always use `assetId` from this endpoint. Never construct asset IDs manually.
