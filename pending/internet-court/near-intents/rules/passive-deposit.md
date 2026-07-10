---
title: Passive Deposit (QR Code)
impact: MEDIUM
tags: passive, qr, bitcoin, cex
---

Display address for manual transfer from wallet instead of implementing deposit

```typescript
// Get wet quote for passive chains
const quote = await fetch('https://1click.chaindefuser.com/v0/quote', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    dry: false,
    swapType: 'FLEX_INPUT',
    slippageTolerance: 100,  // 1% - allows slight amount variation
    originAsset: 'nep141:btc.omft.near',  // Bitcoin
    destinationAsset: 'nep141:wrap.near',
    amount: '100000000',  // 1 BTC in satoshis
    recipient: 'user.near',
    refundTo: 'bc1q...',  // Bitcoin refund address
  })
}).then(r => r.json());
```

```tsx
function PassiveDeposit({ quote, originSymbol }) {
  const { depositAddress, depositMemo, amountInFormatted, deadline } = quote.quote;

  return (
    <div>
      <QRCode value={depositAddress} />

      <div>
        <span>Send exactly: {amountInFormatted} {originSymbol}</span>
      </div>

      <div>
        <span>To: {depositAddress}</span>
        <button onClick={() => navigator.clipboard.writeText(depositAddress)}>Copy</button>
      </div>

      {depositMemo && (
        <div style={{ color: 'red' }}>
          <span>MEMO (REQUIRED): {depositMemo}</span>
          <button onClick={() => navigator.clipboard.writeText(depositMemo)}>Copy</button>
        </div>
      )}

      <div>Expires: {new Date(deadline).toLocaleString()}</div>
    </div>
  );
}
```

