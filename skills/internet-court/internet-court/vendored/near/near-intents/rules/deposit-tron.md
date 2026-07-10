---
title: Tron Deposits
impact: HIGH
tags: deposit, tron, trc20
---

## Native TRX

```typescript
import TronWeb from 'tronweb';

// amount in SUN (1 TRX = 1,000,000 SUN)
const tx = await tronWeb.transactionBuilder.sendTrx(
  depositAddress,
  Number(amountIn),
  tronWeb.defaultAddress.base58
);
const signedTx = await tronWeb.trx.sign(tx);
const result = await tronWeb.trx.sendRawTransaction(signedTx);

const txHash = result.txid;
```

## TRC-20 Token

```typescript
import TronWeb from 'tronweb';

const result = await tronWeb.transactionBuilder.triggerSmartContract(
  tokenAddress, // contractAddress from token API
  'transfer(address,uint256)',
  {},
  [
    { type: 'address', value: depositAddress },
    { type: 'uint256', value: amountIn },
  ],
  tronWeb.defaultAddress.base58
);

if (!result?.result) throw new Error('Failed to build transaction');

const signedTx = await tronWeb.trx.sign(result.transaction);
const broadcast = await tronWeb.trx.sendRawTransaction(signedTx);

const txHash = broadcast.txid;
```
