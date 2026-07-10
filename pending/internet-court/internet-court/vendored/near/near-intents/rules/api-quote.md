---
title: POST /v0/quote
impact: CRITICAL
tags: api, quote, swap
---

# POST /v0/quote

Generates swap quote. Use `dry: true` for preview, `dry: false` to get deposit address.

## Request Fields

### Required

| Field | Type | Description |
|-------|------|-------------|
| `dry` | boolean | `true` = preview only (no deposit address generated). `false` = commit quote, returns deposit address valid ~10 minutes |
| `swapType` | string | How to interpret `amount`. See Swap Types below |
| `originAsset` | string | Source token `assetId` from GET /v0/tokens |
| `destinationAsset` | string | Destination token `assetId` from GET /v0/tokens |
| `amount` | string | Amount in smallest unit (wei, lamports, satoshis). Interpreted based on `swapType` |
| `recipient` | string | Address to receive output tokens. Format depends on destination chain |
| `refundTo` | string | Address for refunds if swap fails. Must be valid for origin chain |

### Optional - Routing

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `depositType` | string | `ORIGIN_CHAIN` | Where you'll deposit from. `ORIGIN_CHAIN` = deposit on source blockchain. `INTENTS` = deposit from intents.near balance |
| `recipientType` | string | `DESTINATION_CHAIN` | Where output goes. `DESTINATION_CHAIN` = send to destination blockchain. `INTENTS` = credit to intents.near balance |
| `refundType` | string | `ORIGIN_CHAIN` | Where refunds go. `ORIGIN_CHAIN` = refund to source blockchain. `INTENTS` = refund to intents.near balance |
| `depositMode` | string | `SIMPLE` | `SIMPLE` = standard deposit address. `MEMO` = deposit address + memo (required for Stellar) |

### Optional - Pricing

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `slippageTolerance` | number | - | Max acceptable slippage in basis points. 100 = 1%. Affects `minAmountOut` |
| `deadline` | string | ~10min | ISO timestamp. Quote expires after this. User must deposit before deadline |
| `quoteWaitingTimeMs` | number | 3000 | How long to wait for market maker quotes (ms). Use `0` for fastest response |

### Optional - Fees & Tracking

| Field | Type | Description |
|-------|------|-------------|
| `referral` | string | Your app identifier (lowercase). Shown in on-chain data and analytics |
| `appFees` | array | Your fee: `[{ recipient: "yourfee.near", fee: 100 }]`. Fee in basis points (100 = 1%) |
| `sessionId` | string | Client session ID for tracking |
| `connectedWallets` | string[] | User's connected wallet addresses (helps with routing) |

### Optional - Virtual Chain (Advanced)

| Field | Type | Description |
|-------|------|-------------|
| `virtualChainRecipient` | string | EVM address for virtual chain recipient |
| `virtualChainRefundRecipient` | string | EVM address for virtual chain refunds |
| `customRecipientMsg` | string | Message for `ft_transfer_call` on NEAR. WARNING: Funds lost if recipient doesn't implement `ft_on_transfer` |

---

## Swap Types

### EXACT_INPUT (most common)

Fixed input amount, variable output.

```typescript
{ swapType: 'EXACT_INPUT', amount: '1000000' } // I want to swap exactly 1 USDC
```

**Behavior:**
- Deposit exactly `amountIn` → receive `amountOut`
- Deposit < `amountIn` → refunded by deadline
- Deposit > `amountIn` → swap processed, excess refunded after completion

### EXACT_OUTPUT

Fixed output amount, variable input.

```typescript
{ swapType: 'EXACT_OUTPUT', amount: '1000000000000000000' } // I want exactly 1 ETH out
```

**Response includes:** `minAmountIn`, `maxAmountIn`

**Behavior:**
- Deposit between `minAmountIn` and `maxAmountIn` → receive exact `amountOut`
- Deposit < `minAmountIn` → refunded
- Deposit > `maxAmountIn` → swap processed, excess refunded

### FLEX_INPUT

Variable input with slippage range. Good for "swap all" scenarios.

```typescript
{ swapType: 'FLEX_INPUT', amount: '1000000', slippageTolerance: 100 }
```

**Response includes:** `minAmountIn`, `minAmountOut`

**Behavior:**
- Any deposit ≥ `minAmountIn` accepted
- Output guaranteed ≥ `minAmountOut`
- Slippage applies to both input and output ranges

### ANY_INPUT

Accumulating deposits. Multiple deposits accepted until deadline.

```typescript
{ swapType: 'ANY_INPUT', amount: '0' } // No fixed amount
```

**Use case:** Aggregate multiple deposits, then withdraw via `/v0/any-input/withdrawals`

---

## Response Fields

```typescript
{
  correlationId: string;      // Unique quote ID
  timestamp: string;          // When quote was generated
  quoteRequest: { ... };      // Echo of your request
  quote: {
    // Deposit info (only when dry: false)
    depositAddress: string;   // Send tokens HERE
    depositMemo: string | null; // Include in tx if non-null (Stellar)

    // Amounts
    amountIn: string;         // Expected input (smallest unit)
    amountInFormatted: string; // Human readable "1.00"
    amountInUsd: string;      // USD value (display only)

    minAmountIn?: string;     // For EXACT_OUTPUT, FLEX_INPUT
    maxAmountIn?: string;     // For EXACT_OUTPUT

    amountOut: string;        // Expected output (smallest unit)
    amountOutFormatted: string; // Human readable
    amountOutUsd: string;     // USD value (DISPLAY ONLY - never use in logic)

    minAmountOut?: string;    // Guaranteed minimum after slippage

    // Timing
    deadline: string;         // ISO timestamp - deposit must arrive before this
    timeWhenInactive: string; // When quote becomes stale (only when dry: false)
    timeEstimate: number;     // Expected completion time in seconds
  }
}
```

---

## Examples

### Basic Swap (ETH USDC → NEAR)

```typescript
// Preview
const preview = await fetch('https://1click.chaindefuser.com/v0/quote', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    dry: true,
    swapType: 'EXACT_INPUT',
    originAsset: 'nep141:eth-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.omft.near',
    destinationAsset: 'nep141:wrap.near',
    amount: '1000000', // 1 USDC (6 decimals)
    recipient: 'user.near',
    refundTo: '0xYourEthAddress',
    slippageTolerance: 100, // 1%
  })
}).then(r => r.json());

// preview.quote.amountOutFormatted = "0.35" (wNEAR)
```

### Commit & Get Deposit Address

```typescript
const committed = await fetch('https://1click.chaindefuser.com/v0/quote', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_API_KEY' // Avoid 0.1% fee
  },
  body: JSON.stringify({
    dry: false, // Commit!
    swapType: 'EXACT_INPUT',
    originAsset: 'nep141:eth-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.omft.near',
    destinationAsset: 'nep141:wrap.near',
    amount: '1000000',
    recipient: 'user.near',
    refundTo: '0xYourEthAddress',
    slippageTolerance: 100,
    referral: 'myapp',
    appFees: [{ recipient: 'myfees.near', fee: 50 }], // 0.5% fee
  })
}).then(r => r.json());

// committed.quote.depositAddress = "0x..." → send 1 USDC here
// committed.quote.deadline = "2025-01-16T15:00:00Z" → must deposit before
```

### Stellar (MEMO Required)

```typescript
const stellarQuote = await fetch('https://1click.chaindefuser.com/v0/quote', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    dry: false,
    depositMode: 'MEMO', // REQUIRED for Stellar
    swapType: 'EXACT_INPUT',
    originAsset: 'nep141:stellar-native.omft.near',
    destinationAsset: 'nep141:wrap.near',
    amount: '10000000', // 1 XLM (7 decimals)
    recipient: 'user.near',
    refundTo: 'GAXYZ...', // Stellar address
  })
}).then(r => r.json());

// stellarQuote.quote.depositAddress = "GABCD..."
// stellarQuote.quote.depositMemo = "123456" → MUST include in Stellar tx or funds lost
```

### Intents Balance (Deposit to Balance)

```typescript
const toIntents = await fetch('https://1click.chaindefuser.com/v0/quote', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    dry: false,
    swapType: 'EXACT_INPUT',
    originAsset: 'nep141:eth-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.omft.near',
    destinationAsset: 'nep141:eth-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.omft.near', // Same!
    depositType: 'ORIGIN_CHAIN',
    recipientType: 'INTENTS', // Credit to intents balance
    recipient: 'user.near', // NEAR account to credit
    refundTo: '0xYourEthAddress',
    amount: '1000000',
  })
}).then(r => r.json());
```
