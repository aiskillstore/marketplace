---
title: Server/Script Example (Node.js)
impact: HIGH
tags: server, script, node, typescript, viem, example
---

Example showing minimum viable server-side swap. Adapt to your use case.

> **Note:** This example uses chain-to-chain mode (deposit on origin chain → receive on destination chain). For high-frequency trading or faster execution, consider using Intents balance mode instead - see `intents-balance.md`.

## Dependencies

```bash
npm install viem
```

## Example Implementation

```typescript
import { createWalletClient, http, parseUnits, erc20Abi, publicActions } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { mainnet, base, arbitrum } from 'viem/chains';

// ============================================================================
// CONFIG
// ============================================================================

const API_BASE = 'https://1click.chaindefuser.com';
const PRIVATE_KEY = process.env.PRIVATE_KEY as `0x${string}`;
const API_KEY = process.env.ONE_CLICK_API_KEY; // Optional, avoids 0.1% fee

const CHAINS = { eth: mainnet, base: base, arb: arbitrum };

// ============================================================================
// TYPES
// ============================================================================

interface Token {
  assetId: string;
  symbol: string;
  decimals: number;
  blockchain: string;
  contractAddress?: string;
}

interface QuoteResponse {
  correlationId: string;
  quote: {
    depositAddress: string;
    amountIn: string;
    amountOut: string;
    amountOutFormatted: string;
    deadline: string;
  };
}

interface StatusResponse {
  status: 'PENDING_DEPOSIT' | 'PROCESSING' | 'SUCCESS' | 'FAILED' | 'REFUNDED' | 'INCOMPLETE_DEPOSIT';
  swapDetails?: {
    amountOut: string;
    destinationChainTxHashes?: Array<{ hash: string; explorerUrl: string }>;
  };
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

async function fetchTokens(): Promise<Token[]> {
  const res = await fetch(`${API_BASE}/v0/tokens`);
  if (!res.ok) throw new Error('Failed to fetch tokens');
  return res.json();
}

async function getQuote(params: {
  originAsset: string;
  destinationAsset: string;
  amount: string;
  recipient: string;
  refundTo: string;
}): Promise<QuoteResponse> {
  const res = await fetch(`${API_BASE}/v0/quote`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(API_KEY && { Authorization: `Bearer ${API_KEY}` }),
    },
    body: JSON.stringify({
      dry: false, // Get real deposit address
      swapType: 'EXACT_INPUT',
      slippageTolerance: 100, // 1%
      ...params,
    }),
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Quote failed: ${error}`);
  }
  return res.json();
}

async function submitDeposit(txHash: string, depositAddress: string): Promise<void> {
  await fetch(`${API_BASE}/v0/deposit/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(API_KEY && { Authorization: `Bearer ${API_KEY}` }),
    },
    body: JSON.stringify({ txHash, depositAddress }),
  });
}

async function pollStatus(depositAddress: string): Promise<StatusResponse> {
  const terminalStates = ['SUCCESS', 'FAILED', 'REFUNDED', 'INCOMPLETE_DEPOSIT'];

  for (let i = 0; i < 180; i++) { // Max 6 minutes
    const res = await fetch(
      `${API_BASE}/v0/status?depositAddress=${depositAddress}`,
      { headers: API_KEY ? { Authorization: `Bearer ${API_KEY}` } : {} }
    );
    const status: StatusResponse = await res.json();

    console.log(`Status: ${status.status}`);

    if (terminalStates.includes(status.status)) {
      return status;
    }

    await new Promise((r) => setTimeout(r, 2000)); // Poll every 2s
  }

  throw new Error('Timeout waiting for swap completion');
}

// ============================================================================
// SWAP EXECUTION
// ============================================================================

async function executeSwap(params: {
  fromToken: Token;
  toToken: Token;
  amount: string; // Human readable (e.g., "100" for 100 USDC)
  recipient: string;
}): Promise<StatusResponse> {
  const { fromToken, toToken, amount, recipient } = params;
  const chain = CHAINS[fromToken.blockchain as keyof typeof CHAINS];
  if (!chain) throw new Error(`Unsupported chain: ${fromToken.blockchain}`);

  // Setup wallet
  const account = privateKeyToAccount(PRIVATE_KEY);
  const client = createWalletClient({
    account,
    chain,
    transport: http(),
  }).extend(publicActions);

  // Convert to smallest unit
  const amountRaw = parseUnits(amount, fromToken.decimals).toString();

  console.log(`Swapping ${amount} ${fromToken.symbol} → ${toToken.symbol}`);

  // 1. Get quote with deposit address
  const quote = await getQuote({
    originAsset: fromToken.assetId,
    destinationAsset: toToken.assetId,
    amount: amountRaw,
    recipient,
    refundTo: account.address,
  });

  console.log(`Deposit ${quote.quote.amountIn} to ${quote.quote.depositAddress}`);
  console.log(`Expected output: ${quote.quote.amountOutFormatted} ${toToken.symbol}`);

  // 2. Send deposit transaction
  let txHash: string;

  if (fromToken.contractAddress) {
    // ERC-20 token
    txHash = await client.writeContract({
      address: fromToken.contractAddress as `0x${string}`,
      abi: erc20Abi,
      functionName: 'transfer',
      args: [quote.quote.depositAddress as `0x${string}`, BigInt(quote.quote.amountIn)],
    });
  } else {
    // Native token (ETH, etc.)
    txHash = await client.sendTransaction({
      to: quote.quote.depositAddress as `0x${string}`,
      value: BigInt(quote.quote.amountIn),
    });
  }

  console.log(`Deposit TX: ${txHash}`);

  // 3. Notify API (speeds up processing)
  await submitDeposit(txHash, quote.quote.depositAddress);

  // 4. Poll until complete
  const result = await pollStatus(quote.quote.depositAddress);

  if (result.status === 'SUCCESS') {
    console.log(`Swap complete! Received: ${result.swapDetails?.amountOut}`);
    if (result.swapDetails?.destinationChainTxHashes?.[0]) {
      console.log(`TX: ${result.swapDetails.destinationChainTxHashes[0].explorerUrl}`);
    }
  } else {
    console.log(`Swap ended with status: ${result.status}`);
  }

  return result;
}

// ============================================================================
// HELPER: Find token by symbol and chain
// ============================================================================

function findToken(tokens: Token[], symbol: string, blockchain: string): Token {
  const token = tokens.find(
    (t) => t.symbol.toLowerCase() === symbol.toLowerCase() && t.blockchain === blockchain
  );
  if (!token) throw new Error(`Token not found: ${symbol} on ${blockchain}`);
  return token;
}

// ============================================================================
// USAGE EXAMPLE
// ============================================================================

async function main() {
  // Fetch available tokens
  const tokens = await fetchTokens();

  // Find tokens
  const usdc = findToken(tokens, 'USDC', 'eth');
  const wNear = findToken(tokens, 'wNEAR', 'near');

  // Execute swap: 100 USDC (Ethereum) → wNEAR (NEAR)
  await executeSwap({
    fromToken: usdc,
    toToken: wNear,
    amount: '100',
    recipient: 'your-account.near',
  });
}

main().catch(console.error);
```

## Run

```bash
PRIVATE_KEY=0x... ONE_CLICK_API_KEY=... npx tsx bot.ts
```

## What This Example Shows

1. **Flow**: Fetch tokens → get quote → send deposit TX → poll until done
2. **No framework** - Plain TypeScript with viem
3. **EVM deposit** - Native token vs ERC-20 handling

## Adapt For Your Use Case

- Add your business logic
- Add proper error handling and retries
- Add logging/monitoring for production
- Handle multiple source chains if needed

## Other Chain Examples

### Solana Source

```typescript
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, sendAndConfirmTransaction } from '@solana/web3.js';
import { getAssociatedTokenAddress, createTransferInstruction } from '@solana/spl-token';

async function sendSolanaDeposit(
  depositAddress: string,
  amount: string,
  tokenMint?: string // undefined for native SOL
): Promise<string> {
  const connection = new Connection('https://api.mainnet-beta.solana.com');
  const keypair = Keypair.fromSecretKey(/* your secret key */);
  const destination = new PublicKey(depositAddress);

  const tx = new Transaction();

  if (tokenMint) {
    // SPL token
    const mint = new PublicKey(tokenMint);
    const sourceAta = await getAssociatedTokenAddress(mint, keypair.publicKey);
    const destAta = await getAssociatedTokenAddress(mint, destination);

    tx.add(
      createTransferInstruction(sourceAta, destAta, keypair.publicKey, BigInt(amount))
    );
  } else {
    // Native SOL
    tx.add(
      SystemProgram.transfer({
        fromPubkey: keypair.publicKey,
        toPubkey: destination,
        lamports: BigInt(amount),
      })
    );
  }

  return sendAndConfirmTransaction(connection, tx, [keypair]);
}
```

