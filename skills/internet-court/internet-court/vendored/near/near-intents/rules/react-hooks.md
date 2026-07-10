---
title: React Hooks
impact: HIGH
tags: react, hooks, tanstack-query
---

Core hooks for 1Click API. See `react-swap-widget.md` for how these fit together.

## Dependencies

```bash
npm install @tanstack/react-query
```

## Hooks

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';

const API = 'https://1click.chaindefuser.com';

// Fetch all supported tokens (cache 5 min)
export function useTokens() {
  return useQuery({
    queryKey: ['1click-tokens'],
    queryFn: () => fetch(`${API}/v0/tokens`).then((r) => r.json()),
    staleTime: 5 * 60 * 1000,
  });
}

// Get dry quote (preview only, no deposit address)
export function useQuote(
  params: {
    originAsset: string;
    destinationAsset: string;
    amount: string;
    recipient: string;
    refundTo: string;
  } | null,
  apiKey?: string
) {
  return useQuery({
    queryKey: ['1click-quote', params],
    queryFn: () =>
      fetch(`${API}/v0/quote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(apiKey && { Authorization: `Bearer ${apiKey}` }),
        },
        body: JSON.stringify({
          dry: true,
          swapType: 'EXACT_INPUT',
          slippageTolerance: 100,
          ...params,
        }),
      }).then((r) => r.json()),
    enabled: !!params?.amount && params.amount !== '0',
    refetchInterval: 10_000,
  });
}

// Poll swap status until terminal
export function useSwapStatus(depositAddress: string | null, apiKey?: string) {
  return useQuery({
    queryKey: ['1click-status', depositAddress],
    queryFn: () =>
      fetch(`${API}/v0/status?depositAddress=${depositAddress}`, {
        headers: apiKey ? { Authorization: `Bearer ${apiKey}` } : {},
      }).then((r) => r.json()),
    enabled: !!depositAddress,
    refetchInterval: (q) =>
      ['SUCCESS', 'FAILED', 'REFUNDED', 'INCOMPLETE_DEPOSIT'].includes(q.state.data?.status)
        ? false
        : 2000,
  });
}

// Execute swap: get wet quote → send tx → submit hash
export function useExecuteSwap(apiKey?: string) {
  return useMutation({
    mutationFn: async ({
      params,
      sendTransaction,
    }: {
      params: { originAsset: string; destinationAsset: string; amount: string; recipient: string; refundTo: string };
      sendTransaction: (depositAddress: string, amount: string) => Promise<string>;
    }) => {
      // 1. Get wet quote
      const quote = await fetch(`${API}/v0/quote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(apiKey && { Authorization: `Bearer ${apiKey}` }),
        },
        body: JSON.stringify({ dry: false, swapType: 'EXACT_INPUT', slippageTolerance: 100, ...params }),
      }).then((r) => r.json());

      // 2. Send deposit
      const txHash = await sendTransaction(quote.quote.depositAddress, quote.quote.amountIn);

      // 3. Notify API
      fetch(`${API}/v0/deposit/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(apiKey && { Authorization: `Bearer ${apiKey}` }) },
        body: JSON.stringify({ txHash, depositAddress: quote.quote.depositAddress }),
      }).catch(() => {});

      return { depositAddress: quote.quote.depositAddress, txHash };
    },
  });
}
```

## Usage Pattern

```tsx
function MySwapComponent() {
  const [depositAddr, setDepositAddr] = useState<string | null>(null);

  const { data: tokens } = useTokens();
  const { data: quote } = useQuote(params);
  const { data: status } = useSwapStatus(depositAddr);
  const swap = useExecuteSwap();

  const handleSwap = async () => {
    const result = await swap.mutateAsync({
      params: { ... },
      sendTransaction: async (addr, amt) => {
        // Your wallet logic here (wagmi, ethers, etc.)
        return txHash;
      },
    });
    setDepositAddr(result.depositAddress);
  };

  // Build your custom UI...
}
```
