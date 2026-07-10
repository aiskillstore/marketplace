---
title: GET /v0/any-input/withdrawals
impact: MEDIUM
tags: api, any-input, withdrawals
---

Retrieves all withdrawals for an ANY_INPUT quote. Use with accumulating deposit flows.

```typescript
const response = await fetch(
  `https://1click.chaindefuser.com/v0/any-input/withdrawals?depositAddress=${depositAddress}`,
  { headers: { Authorization: `Bearer ${apiKey}` } }
);
const withdrawals = await response.json();
```

## Query Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `depositAddress` | Yes | The deposit address from quote |
| `depositMemo` | No | Include for Stellar MEMO mode |
| `timestampFrom` | No | Filter withdrawals from this timestamp (ISO string) |
| `page` | No | Page number (default: 1) |
| `limit` | No | Withdrawals per page (max: 50, default: 50) |
| `sortOrder` | No | `asc` or `desc` |

## Response

```typescript
interface GetAnyInputQuoteWithdrawals {
  asset: string;
  recipient: string;
  affiliateRecipient: string;
  withdrawals: AnyInputQuoteWithdrawal[];
}

interface AnyInputQuoteWithdrawal {
  status: 'SUCCESS' | 'FAILED';
  amountOutFormatted: string;
  amountOutUsd: string;
  amountOut: string;
  withdrawFeeFormatted: string;
  withdrawFee: string;
  withdrawFeeUsd: string;
  timestamp: string;
  hash: string;
}
```

## Example

```typescript
async function getWithdrawals(depositAddress: string, apiKey?: string) {
  const params = new URLSearchParams({ depositAddress });
  
  const res = await fetch(
    `https://1click.chaindefuser.com/v0/any-input/withdrawals?${params}`,
    { headers: apiKey ? { Authorization: `Bearer ${apiKey}` } : {} }
  );
  
  if (!res.ok) throw new Error(`Failed: ${res.status}`);
  return res.json();
}

const data = await getWithdrawals(quote.quote.depositAddress, apiKey);
console.log(`Total withdrawals: ${data.withdrawals.length}`);

for (const w of data.withdrawals) {
  console.log(`${w.status}: ${w.amountOutFormatted} (fee: ${w.withdrawFeeFormatted})`);
}
```

Used with `swapType: 'ANY_INPUT'` quotes where multiple deposits accumulate until deadline, then withdraw.
