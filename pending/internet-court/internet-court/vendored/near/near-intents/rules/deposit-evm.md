---
title: EVM Deposits
impact: CRITICAL
tags: deposit, evm, ethereum, wagmi
---

Chains: Ethereum, Base, Arbitrum, Optimism, Polygon, BSC, Avalanche, Gnosis, Berachain

## Native Token (ETH/MATIC/etc)

```typescript
import { useSendTransaction } from 'wagmi';

const { sendTransactionAsync } = useSendTransaction();

const hash = await sendTransactionAsync({
  to: depositAddress as `0x${string}`,
  value: BigInt(amountIn),
});
```

## ERC-20 Token

```typescript
import { useWriteContract } from 'wagmi';
import { erc20Abi } from 'viem';

const { writeContractAsync } = useWriteContract();

const hash = await writeContractAsync({
  address: tokenAddress as `0x${string}`,
  abi: erc20Abi,
  functionName: 'transfer',
  args: [depositAddress as `0x${string}`, BigInt(amountIn)],
});
```

Use `contractAddress` from token API as `tokenAddress`.
