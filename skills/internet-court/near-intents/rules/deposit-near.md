---
title: NEAR Deposits
impact: HIGH
tags: deposit, near, nep141
---

## NEP-141 Token

```typescript
import { useWalletSelector } from '@near-wallet-selector/react';

const { selector } = useWalletSelector();
const wallet = await selector.wallet();

const result = await wallet.signAndSendTransactions({
  transactions: [{
    receiverId: tokenContract, // contractAddress from token API
    actions: [{
      type: 'FunctionCall',
      params: {
        methodName: 'ft_transfer',
        args: { receiver_id: depositAddress, amount: amountIn },
        gas: '50000000000000', // 50 TGas
        deposit: '1', // 1 yoctoNEAR required
      },
    }],
  }],
});

const txHash = result?.[0]?.transaction?.hash;
```

## Native NEAR (wrap first)

Native NEAR must be wrapped to wNEAR before transfer:

```typescript
const { selector } = useWalletSelector();
const wallet = await selector.wallet();

const result = await wallet.signAndSendTransactions({
  transactions: [{
    receiverId: 'wrap.near',
    actions: [
      // 1. Wrap NEAR to wNEAR
      {
        type: 'FunctionCall',
        params: {
          methodName: 'near_deposit',
          args: {},
          gas: '30000000000000',
          deposit: amountIn, // Amount to wrap
        },
      },
      // 2. Transfer wNEAR
      {
        type: 'FunctionCall',
        params: {
          methodName: 'ft_transfer',
          args: { receiver_id: depositAddress, amount: amountIn },
          gas: '50000000000000',
          deposit: '1',
        },
      },
    ],
  }],
});
```

For `/v0/deposit/submit`, include `nearSenderAccount: 'user.near'`.
