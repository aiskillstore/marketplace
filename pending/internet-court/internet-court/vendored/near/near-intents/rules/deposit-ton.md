---
title: TON Deposits
impact: HIGH
tags: deposit, ton, jetton
---

## Native TON

```typescript
import { useTonConnectUI } from '@tonconnect/ui-react';

const [tonConnect] = useTonConnectUI();

const result = await tonConnect.sendTransaction({
  validUntil: Math.floor(Date.now() / 1000) + 600, // 10 min
  messages: [{
    address: depositAddress,
    amount: amountIn, // in nanoton
  }],
});

const txHash = result.boc;
```

## Jetton (TON Token)

```typescript
import { useTonConnectUI } from '@tonconnect/ui-react';
import { beginCell, Address, toNano } from '@ton/core';

const [tonConnect] = useTonConnectUI();

// Build jetton transfer message
const forwardPayload = beginCell().endCell();
const body = beginCell()
  .storeUint(0xf8a7ea5, 32)  // transfer op code
  .storeUint(0, 64)          // query_id
  .storeCoins(BigInt(amountIn))
  .storeAddress(Address.parse(depositAddress))
  .storeAddress(Address.parse(tonConnect.account!.address)) // response destination
  .storeBit(0)               // no custom payload
  .storeCoins(toNano('0.01')) // forward amount
  .storeBit(1)
  .storeRef(forwardPayload)
  .endCell();

const result = await tonConnect.sendTransaction({
  validUntil: Math.floor(Date.now() / 1000) + 600,
  messages: [{
    address: jettonWalletAddress, // User's jetton wallet, not token contract
    amount: toNano('0.1').toString(), // Gas for transfer
    payload: body.toBoc().toString('base64'),
  }],
});
```

Note: `jettonWalletAddress` is the user's jetton wallet address, not the token contract address. Query it from the jetton master contract.
