---
title: POST /v0/deposit/submit
impact: HIGH
tags: api, deposit
---

Optional endpoint to notify 1Click that you've sent a deposit. Speeds up processing.

```typescript
await fetch('https://1click.chaindefuser.com/v0/deposit/submit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${apiKey}`,
  },
  body: JSON.stringify({
    txHash: '0x123abc...', // Your deposit transaction hash
    depositAddress: quote.quote.depositAddress,
  })
});
```

## Additional Fields

| Field | When to include |
|-------|-----------------|
| `nearSenderAccount` | NEAR deposits - sender's account ID |
| `memo` | Stellar MEMO mode - the memo used in transaction |

### NEAR Example

```typescript
await fetch('https://1click.chaindefuser.com/v0/deposit/submit', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    txHash: 'Hk3ds...',
    depositAddress: quote.quote.depositAddress,
    nearSenderAccount: 'user.near',
  })
});
```

### Stellar Example

```typescript
await fetch('https://1click.chaindefuser.com/v0/deposit/submit', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    txHash: 'abc123...',
    depositAddress: quote.quote.depositAddress,
    memo: quote.quote.depositMemo,
  })
});
```

Call immediately after your deposit transaction confirms. Not required, but improves UX.
