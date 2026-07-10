---
title: Stellar Deposits (MEMO REQUIRED)
impact: HIGH
tags: deposit, stellar, memo
---

Stellar requires `depositMode: 'MEMO'` in quote. Transaction MUST include memo or funds are lost.

## Quote Request

```typescript
const quote = await fetch('https://1click.chaindefuser.com/v0/quote', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    dry: false,
    depositMode: 'MEMO',  // REQUIRED for Stellar
    originAsset: 'nep141:stellar-native.omft.near',
    destinationAsset: 'nep141:wrap.near',
    amount: '10000000', // 1 XLM in stroops
    recipient: 'user.near',
    refundTo: 'GA5X...', // Stellar address
  })
}).then(r => r.json());

// quote.quote.depositMemo = "123456" - MUST include in tx
```

## Transaction

```typescript
import { Horizon, Asset, Memo, Networks, Operation, TransactionBuilder, Keypair } from '@stellar/stellar-sdk';

const server = new Horizon.Server('https://horizon.stellar.org');
const keypair = Keypair.fromSecret(userSecret);
const account = await server.loadAccount(keypair.publicKey());

const tx = new TransactionBuilder(account, { fee: '100', networkPassphrase: Networks.PUBLIC })
  .addOperation(Operation.payment({
    destination: quote.quote.depositAddress,
    asset: Asset.native(),
    amount: quote.quote.amountInFormatted,
  }))
  .addMemo(Memo.text(quote.quote.depositMemo))  // CRITICAL
  .setTimeout(30)
  .build();

tx.sign(keypair);
await server.submitTransaction(tx);
```

## Status Polling

For Stellar, include memo in status query:

```
GET /v0/status?depositAddress=GA5X...&depositMemo=123456
```
