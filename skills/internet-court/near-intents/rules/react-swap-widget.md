---
title: React Swap Widget Example
impact: HIGH
tags: react, component, widget, wagmi, example
---

Example showing the minimum viable swap implementation. Adapt to your app's architecture and design system.

## Dependencies

```bash
npm install @tanstack/react-query wagmi viem
```

## Example Implementation

```tsx
'use client';

import { useState, useMemo } from 'react';
import { useQuery, useMutation, QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useAccount,
  useConnect,
  useDisconnect,
  useSendTransaction,
  useWriteContract,
  WagmiProvider,
  createConfig,
  http,
} from 'wagmi';
import { mainnet, base, arbitrum, polygon, bsc } from 'wagmi/chains';
import { injected } from 'wagmi/connectors';
import { erc20Abi, parseUnits, formatUnits } from 'viem';

// ============================================================================
// CONFIG
// ============================================================================

const API_BASE = 'https://1click.chaindefuser.com';

const wagmiConfig = createConfig({
  chains: [mainnet, base, arbitrum, polygon, bsc],
  connectors: [injected()],
  transports: {
    [mainnet.id]: http(),
    [base.id]: http(),
    [arbitrum.id]: http(),
    [polygon.id]: http(),
    [bsc.id]: http(),
  },
});

const queryClient = new QueryClient();

// Chain name to wagmi chain ID mapping
const CHAIN_IDS: Record<string, number> = {
  eth: mainnet.id,
  base: base.id,
  arb: arbitrum.id,
  polygon: polygon.id,
  bsc: bsc.id,
};

// ============================================================================
// TYPES
// ============================================================================

interface Token {
  assetId: string;
  symbol: string;
  decimals: number;
  blockchain: string;
  contractAddress?: string;
  price?: string;
}

interface Quote {
  depositAddress: string;
  amountIn: string;
  amountInFormatted: string;
  amountOut: string;
  amountOutFormatted: string;
  deadline: string;
}

interface QuoteResponse {
  correlationId: string;
  quote: Quote;
}

interface StatusResponse {
  status: 'PENDING_DEPOSIT' | 'PROCESSING' | 'SUCCESS' | 'FAILED' | 'REFUNDED' | 'INCOMPLETE_DEPOSIT';
  swapDetails?: {
    destinationChainTxHashes?: Array<{ hash: string; explorerUrl: string }>;
  };
}

// ============================================================================
// API HOOKS
// ============================================================================

function useTokens() {
  return useQuery<Token[]>({
    queryKey: ['1click-tokens'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/v0/tokens`);
      if (!res.ok) throw new Error('Failed to fetch tokens');
      return res.json();
    },
    staleTime: 5 * 60 * 1000,
  });
}

function useQuote(
  params: {
    originAsset: string;
    destinationAsset: string;
    amount: string;
    recipient: string;
    refundTo: string;
  } | null,
  apiKey?: string
) {
  return useQuery<QuoteResponse>({
    queryKey: ['1click-quote', params],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/v0/quote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(apiKey && { Authorization: `Bearer ${apiKey}` }),
        },
        body: JSON.stringify({
          dry: true,
          swapType: 'EXACT_INPUT',
          slippageTolerance: 100, // 1%
          ...params,
        }),
      });
      if (!res.ok) throw new Error('Failed to fetch quote');
      return res.json();
    },
    enabled: !!params?.amount && !!params?.recipient && params.amount !== '0',
    refetchInterval: 10_000,
  });
}

function useSwapStatus(depositAddress: string | null, apiKey?: string) {
  return useQuery<StatusResponse>({
    queryKey: ['1click-status', depositAddress],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/v0/status?depositAddress=${depositAddress}`, {
        headers: apiKey ? { Authorization: `Bearer ${apiKey}` } : {},
      });
      if (!res.ok) throw new Error('Failed to fetch status');
      return res.json();
    },
    enabled: !!depositAddress,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (['SUCCESS', 'FAILED', 'REFUNDED', 'INCOMPLETE_DEPOSIT'].includes(status || '')) {
        return false;
      }
      return 2000;
    },
  });
}

function useExecuteSwap(apiKey?: string) {
  return useMutation({
    mutationFn: async ({
      params,
      sendTransaction,
    }: {
      params: {
        originAsset: string;
        destinationAsset: string;
        amount: string;
        recipient: string;
        refundTo: string;
      };
      sendTransaction: (depositAddress: string, amount: string) => Promise<string>;
    }) => {
      // Get real quote with deposit address
      const quoteRes = await fetch(`${API_BASE}/v0/quote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(apiKey && { Authorization: `Bearer ${apiKey}` }),
        },
        body: JSON.stringify({
          dry: false,
          swapType: 'EXACT_INPUT',
          slippageTolerance: 100,
          ...params,
        }),
      });
      if (!quoteRes.ok) throw new Error('Failed to get quote');
      const wetQuote: QuoteResponse = await quoteRes.json();

      // Send deposit transaction
      const txHash = await sendTransaction(
        wetQuote.quote.depositAddress,
        wetQuote.quote.amountIn
      );

      // Notify API (speeds up processing)
      await fetch(`${API_BASE}/v0/deposit/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(apiKey && { Authorization: `Bearer ${apiKey}` }),
        },
        body: JSON.stringify({
          txHash,
          depositAddress: wetQuote.quote.depositAddress,
        }),
      }).catch(() => {}); // Non-critical

      return { depositAddress: wetQuote.quote.depositAddress, txHash };
    },
  });
}

// ============================================================================
// COMPONENTS
// ============================================================================

function TokenSelect({
  tokens,
  value,
  onChange,
  blockchain,
  label,
}: {
  tokens: Token[];
  value: Token | null;
  onChange: (token: Token) => void;
  blockchain?: string;
  label: string;
}) {
  const filtered = blockchain
    ? tokens.filter((t) => t.blockchain === blockchain)
    : tokens;

  return (
    <div>
      <label className="block text-sm font-medium mb-1">{label}</label>
      <select
        value={value?.assetId || ''}
        onChange={(e) => {
          const token = tokens.find((t) => t.assetId === e.target.value);
          if (token) onChange(token);
        }}
        className="w-full p-2 border rounded"
      >
        <option value="">Select token</option>
        {filtered.map((token) => (
          <option key={token.assetId} value={token.assetId}>
            {token.symbol} ({token.blockchain})
          </option>
        ))}
      </select>
    </div>
  );
}

function SwapWidgetInner({ apiKey }: { apiKey?: string }) {
  const { address, isConnected, chain } = useAccount();
  const { connect, connectors } = useConnect();
  const { disconnect } = useDisconnect();
  const { sendTransactionAsync } = useSendTransaction();
  const { writeContractAsync } = useWriteContract();

  const [fromToken, setFromToken] = useState<Token | null>(null);
  const [toToken, setToToken] = useState<Token | null>(null);
  const [amount, setAmount] = useState('');
  const [recipient, setRecipient] = useState('');
  const [depositAddress, setDepositAddress] = useState<string | null>(null);

  const { data: tokens = [] } = useTokens();
  const executeSwap = useExecuteSwap(apiKey);
  const { data: statusData } = useSwapStatus(depositAddress, apiKey);

  // Filter EVM tokens for source (what user can send from wallet)
  const evmTokens = useMemo(
    () => tokens.filter((t) => ['eth', 'base', 'arb', 'polygon', 'bsc'].includes(t.blockchain)),
    [tokens]
  );

  // Convert amount to smallest unit
  const amountRaw = useMemo(() => {
    if (!amount || !fromToken) return '';
    try {
      return parseUnits(amount, fromToken.decimals).toString();
    } catch {
      return '';
    }
  }, [amount, fromToken]);

  // Build quote params
  const quoteParams = useMemo(() => {
    if (!fromToken || !toToken || !amountRaw || !recipient || !address) return null;
    return {
      originAsset: fromToken.assetId,
      destinationAsset: toToken.assetId,
      amount: amountRaw,
      recipient,
      refundTo: address,
    };
  }, [fromToken, toToken, amountRaw, recipient, address]);

  const { data: quoteData, isLoading: quoteLoading } = useQuote(quoteParams, apiKey);

  const handleSwap = async () => {
    if (!quoteParams || !fromToken) return;

    // Check if on correct chain
    const targetChainId = CHAIN_IDS[fromToken.blockchain];
    if (chain?.id !== targetChainId) {
      alert(`Please switch to ${fromToken.blockchain} network`);
      return;
    }

    const result = await executeSwap.mutateAsync({
      params: quoteParams,
      sendTransaction: async (depositAddr, depositAmount) => {
        if (fromToken.contractAddress) {
          // ERC-20 transfer
          return writeContractAsync({
            address: fromToken.contractAddress as `0x${string}`,
            abi: erc20Abi,
            functionName: 'transfer',
            args: [depositAddr as `0x${string}`, BigInt(depositAmount)],
          });
        }
        // Native token transfer
        return sendTransactionAsync({
          to: depositAddr as `0x${string}`,
          value: BigInt(depositAmount),
        });
      },
    });

    setDepositAddress(result.depositAddress);
  };

  const isTerminal =
    statusData?.status &&
    ['SUCCESS', 'FAILED', 'REFUNDED', 'INCOMPLETE_DEPOSIT'].includes(statusData.status);

  const isSwapping = executeSwap.isPending || (depositAddress && !isTerminal);

  return (
    <div className="space-y-4 p-4 border rounded-lg max-w-md mx-auto">
      <h2 className="text-xl font-bold">Swap</h2>

      {/* Wallet Connection */}
      {!isConnected ? (
        <button
          onClick={() => connect({ connector: connectors[0] })}
          className="w-full py-2 bg-blue-600 text-white rounded"
        >
          Connect Wallet
        </button>
      ) : (
        <div className="flex justify-between items-center text-sm">
          <span className="truncate">{address}</span>
          <button onClick={() => disconnect()} className="text-red-600">
            Disconnect
          </button>
        </div>
      )}

      {/* Token Selection */}
      <TokenSelect
        tokens={evmTokens}
        value={fromToken}
        onChange={setFromToken}
        label="From"
      />

      <TokenSelect
        tokens={tokens}
        value={toToken}
        onChange={setToToken}
        label="To"
      />

      {/* Amount Input */}
      <div>
        <label className="block text-sm font-medium mb-1">
          Amount {fromToken && `(${fromToken.symbol})`}
        </label>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="0.0"
          className="w-full p-2 border rounded"
        />
      </div>

      {/* Recipient Input */}
      <div>
        <label className="block text-sm font-medium mb-1">
          Recipient {toToken && `(${toToken.blockchain} address)`}
        </label>
        <input
          value={recipient}
          onChange={(e) => setRecipient(e.target.value)}
          placeholder="Enter destination address"
          className="w-full p-2 border rounded"
        />
      </div>

      {/* Quote Preview */}
      {quoteLoading && <div className="text-sm text-gray-500">Getting quote...</div>}
      {quoteData?.quote && (
        <div className="p-3 bg-gray-50 rounded text-sm">
          You'll receive: <strong>{quoteData.quote.amountOutFormatted} {toToken?.symbol}</strong>
        </div>
      )}

      {/* Error Display */}
      {executeSwap.error && (
        <div className="p-3 bg-red-50 text-red-700 rounded text-sm">
          {executeSwap.error.message}
        </div>
      )}

      {/* Status Display */}
      {statusData && (
        <div className="p-3 bg-blue-50 rounded text-sm">
          Status: <strong>{statusData.status}</strong>
          {statusData.status === 'SUCCESS' &&
            statusData.swapDetails?.destinationChainTxHashes?.[0] && (
              <a
                href={statusData.swapDetails.destinationChainTxHashes[0].explorerUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-blue-600 underline"
              >
                View TX
              </a>
            )}
        </div>
      )}

      {/* Swap Button */}
      <button
        onClick={handleSwap}
        disabled={!isConnected || !quoteData?.quote || isSwapping}
        className="w-full py-3 bg-blue-600 text-white rounded font-medium disabled:opacity-50"
      >
        {!isConnected
          ? 'Connect Wallet'
          : executeSwap.isPending
            ? 'Confirming...'
            : depositAddress && !isTerminal
              ? `${statusData?.status || 'Processing'}...`
              : 'Swap'}
      </button>
    </div>
  );
}

// ============================================================================
// EXPORT - Wrap with providers
// ============================================================================

export function SwapWidget({ apiKey }: { apiKey?: string }) {
  return (
    <WagmiProvider config={wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        <SwapWidgetInner apiKey={apiKey} />
      </QueryClientProvider>
    </WagmiProvider>
  );
}

// Usage in your app:
// import { SwapWidget } from './SwapWidget';
// <SwapWidget apiKey={process.env.NEXT_PUBLIC_ONE_CLICK_API_KEY} />
```

## What This Example Shows

1. **Flow**: Tokens → dry quote (preview) → wet quote (deposit address) → send TX → poll status
2. **Hooks pattern**: `useQuery` for fetching, `useMutation` for swap execution
3. **EVM deposit**: Native token vs ERC-20 handling
4. **Status polling**: Auto-stop on terminal states

## Adapt For Your App

- Replace wagmi config with your existing wallet setup
- Use your design system instead of inline Tailwind
- Add your token filtering/ordering logic
- Integrate with your state management
- Add error handling appropriate for your UX
