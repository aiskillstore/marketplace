---
title: Solana Deposits
impact: HIGH
tags: deposit, solana, spl
---

## Native SOL

```typescript
import { useWallet, useConnection } from '@solana/wallet-adapter-react';
import { SystemProgram, Transaction, PublicKey } from '@solana/web3.js';

const { publicKey, sendTransaction } = useWallet();
const { connection } = useConnection();

const tx = new Transaction().add(
  SystemProgram.transfer({
    fromPubkey: publicKey!,
    toPubkey: new PublicKey(depositAddress),
    lamports: BigInt(amountIn),
  })
);
const signature = await sendTransaction(tx, connection);
await connection.confirmTransaction(signature);
```

## SPL Token

```typescript
import { useWallet, useConnection } from '@solana/wallet-adapter-react';
import { PublicKey, Transaction } from '@solana/web3.js';
import {
  getAssociatedTokenAddressSync,
  createTransferInstruction,
  createAssociatedTokenAccountInstruction,
  getAccount,
} from '@solana/spl-token';

const { publicKey, sendTransaction } = useWallet();
const { connection } = useConnection();

const mintPubkey = new PublicKey(tokenMint); // contractAddress from token API
const toPubkey = new PublicKey(depositAddress);
const fromATA = getAssociatedTokenAddressSync(mintPubkey, publicKey!);
const toATA = getAssociatedTokenAddressSync(mintPubkey, toPubkey);

const tx = new Transaction();

// Create destination ATA if needed
try {
  await getAccount(connection, toATA);
} catch {
  tx.add(createAssociatedTokenAccountInstruction(publicKey!, toATA, toPubkey, mintPubkey));
}

tx.add(createTransferInstruction(fromATA, toATA, publicKey!, BigInt(amountIn)));

const signature = await sendTransaction(tx, connection);
await connection.confirmTransaction(signature);
```

Use `contractAddress` from token API as `tokenMint`.
