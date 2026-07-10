---
title: GET /v0/status
impact: CRITICAL
tags: api, status, polling
---

Check swap execution status. Poll until terminal state.

```typescript
const response = await fetch(
  `https://1click.chaindefuser.com/v0/status?depositAddress=${depositAddress}`,
  { headers: { Authorization: `Bearer ${apiKey}` } }
);
const status = await response.json();
```

For Stellar (MEMO mode), include memo:
```
?depositAddress=GABCD...&depositMemo=123456
```

## Status Values

| Status | Terminal | Description |
|--------|----------|-------------|
| `PENDING_DEPOSIT` | No | Waiting for deposit to arrive |
| `PROCESSING` | No | Deposit detected, swap executing |
| `SUCCESS` | Yes | Complete - tokens delivered |
| `INCOMPLETE_DEPOSIT` | Yes | Deposit below required amount |
| `REFUNDED` | Yes | Failed, funds returned to refundTo |
| `FAILED` | Yes | Error occurred |

## Response

```typescript
interface StatusResponse {
  correlationId: string;
  status: string;
  updatedAt: string;
  quoteResponse: QuoteResponse; // Original quote
  swapDetails: {
    amountIn: string;
    amountInFormatted: string;
    amountOut: string;
    amountOutFormatted: string;
    slippage: number;
    originChainTxHashes: Array<{ hash: string; explorerUrl: string }>;
    destinationChainTxHashes: Array<{ hash: string; explorerUrl: string }>;
    refundedAmount?: string;
    refundReason?: string;
    depositedAmount?: string;
  };
}
```

## Polling Pattern

```typescript
async function pollUntilComplete(depositAddress: string, apiKey?: string) {
  const headers = apiKey ? { Authorization: `Bearer ${apiKey}` } : {};

  for (let i = 0; i < 120; i++) { // Max ~4 minutes
    const res = await fetch(
      `https://1click.chaindefuser.com/v0/status?depositAddress=${depositAddress}`,
      { headers }
    );
    const status = await res.json();

    if (['SUCCESS', 'FAILED', 'REFUNDED', 'INCOMPLETE_DEPOSIT'].includes(status.status)) {
      return status;
    }

    await new Promise(r => setTimeout(r, 2000)); // Poll every 2s
  }

  throw new Error('Timeout waiting for swap completion');
}
```
