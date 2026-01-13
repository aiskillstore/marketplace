---
name: pitfalls-blockchain
description: "Blockchain RPC error handling, gas estimation, multi-chain config, and transaction management. Use when interacting with smart contracts, estimating gas, or managing transactions. Triggers on: RPC, contract call, gas, multicall, nonce, transaction, revert."
---

# Blockchain Pitfalls

Common pitfalls and correct patterns for blockchain interactions.

## When to Use

- Making contract calls via RPC
- Estimating gas for transactions
- Handling reverts and errors
- Managing nonces for concurrent txs
- Configuring multi-chain support
- Reviewing blockchain code

## Workflow

### Step 1: Verify Error Handling

Check all contract calls are wrapped in try/catch.

### Step 2: Check Gas Estimation

Ensure gas is estimated with buffer before sending.

### Step 3: Verify Multicall Safety

Confirm multicall uses allowFailure: true.

---

## RPC Error Handling

```typescript
// ✅ Wrap ALL contract calls
async function getQuote(tokenIn: Address, tokenOut: Address) {
  try {
    const quote = await quoter.quoteExactInput(...);
    return quote;
  } catch (error) {
    // Low-liquidity tokens WILL fail - this is expected
    console.warn(`Quote failed for ${tokenIn}->${tokenOut}:`, error.message);
    return null; // Continue processing other tokens
  }
}

// ✅ Validate before calling contracts
if (!isAddress(tokenAddress)) {
  throw new Error('Invalid token address');
}

// ✅ Handle "execution reverted" gracefully
if (error.message.includes('execution reverted')) {
  // Pool doesn't exist or insufficient liquidity
  return null;
}

// ✅ Multicall with individual error handling
const results = await multicall({
  contracts: tokens.map(t => ({ ... })),
  allowFailure: true, // CRITICAL
});
results.forEach((result, i) => {
  if (result.status === 'success') {
    // Use result.result
  } else {
    // Log and skip this token
  }
});
```

## Gas Estimation

```typescript
// ✅ Always estimate gas before sending
const gasEstimate = await contract.estimateGas.swap(...args);

// ✅ Add 10-20% buffer to gas estimates
const gasLimit = gasEstimate.mul(120).div(100);  // 20% buffer

// ✅ EIP-1559 gas pricing
const feeData = await provider.getFeeData();
const tx = {
  maxFeePerGas: feeData.maxFeePerGas,
  maxPriorityFeePerGas: feeData.maxPriorityFeePerGas,
  gasLimit,
};

// ✅ Simulate before execution
try {
  await contract.callStatic.swap(...args);  // Dry run
  const tx = await contract.swap(...args);  // Real execution
} catch (e) {
  // Would revert - don't send
}

// ✅ Handle gas price spikes
if (feeData.maxFeePerGas > MAX_ACCEPTABLE_GAS) {
  throw new Error('Gas too high, waiting...');
}
```

## Multi-Chain Configuration

```typescript
// ✅ Chain-specific configuration
const CHAIN_CONFIG: Record<ChainId, ChainConfig> = {
  ethereum: {
    chainId: 1,
    rpcUrl: process.env.ETHEREUM_RPC_URL,
    blockTime: 12,
    confirmations: 2,
    nativeToken: 'ETH',
  },
  polygon: {
    chainId: 137,
    rpcUrl: process.env.POLYGON_RPC_URL,
    blockTime: 2,
    confirmations: 5,  // More confirmations for faster chains
    nativeToken: 'MATIC',
  },
};
```

## Transaction Management

```typescript
// ✅ Wait for confirmations
const receipt = await tx.wait(2);  // 2 confirmations

// ✅ Nonce management
class NonceManager {
  private pending = new Map<Address, number>();

  async getNextNonce(address: Address, provider: Provider): Promise<number> {
    const onChain = await provider.getTransactionCount(address, 'pending');
    const local = this.pending.get(address) ?? onChain;
    const next = Math.max(onChain, local);
    this.pending.set(address, next + 1);
    return next;
  }
}
```

## Rate Limiting & Retry

```typescript
// ✅ Exponential backoff
async function fetchWithRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429) {  // Rate limited
        const delay = Math.pow(2, attempt) * 1000;
        await sleep(delay);
        continue;
      }
      throw error;
    }
  }
  throw new Error('Max retries exceeded');
}

// ✅ Fallback RPC endpoints
const RPC_ENDPOINTS = [
  'https://eth-mainnet.alchemyapi.io/v2/KEY',
  'https://mainnet.infura.io/v3/KEY',
  'https://rpc.ankr.com/eth',
];
```

## Quick Checklist

- [ ] All contract calls wrapped in try/catch
- [ ] Multicall uses `allowFailure: true`
- [ ] Gas estimation with 20% buffer
- [ ] EIP-1559 gas pricing used
- [ ] Transaction simulation before send
- [ ] Nonce management for concurrent txs
- [ ] Confirmations appropriate per chain
