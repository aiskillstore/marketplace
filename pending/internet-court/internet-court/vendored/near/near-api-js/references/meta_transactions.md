# Meta Transactions Guide

Gasless (relayer-sponsored) transaction patterns in near-api-js.

## Table of Contents

1. [Overview](#overview)
2. [Creating Signed Delegate Actions](#creating-signed-delegate-actions)
3. [Relayer Integration](#relayer-integration)
4. [Block Height TTL](#block-height-ttl)
5. [Error Handling](#error-handling)

---

## Overview

Meta transactions allow users to sign transactions without paying gas. A relayer submits the transaction on their behalf and covers gas costs.

**Flow:**

1. User creates and signs a `DelegateAction`
2. User sends signed delegate to relayer (off-chain)
3. Relayer wraps it in a transaction and submits to NEAR
4. Relayer pays gas, user's action executes

---

## Creating Signed Delegate Actions

```typescript
import { Account, actions, teraToGas, nearToYocto } from "near-api-js";

const account = new Account(accountId, provider, privateKey);

// Create signed meta transaction
const metaTx = await account.createSignedMetaTransaction({
  receiverId: "contract.near",
  actions: [
    actions.functionCall(
      "some_method",
      { arg: "value" },
      teraToGas(10), // 10 TGas
      nearToYocto("0"), // No deposit
    ),
  ],
});

// metaTx contains:
// - signedDelegate: { delegateAction, signature }
// - delegateAction: { senderId, receiverId, actions, nonce, maxBlockHeight, publicKey }
```

### With Custom TTL

```typescript
const metaTx = await account.createSignedMetaTransaction({
  receiverId: "contract.near",
  actions: [
    actions.functionCall("method", {}, teraToGas(10), nearToYocto("0")),
  ],
  blockHeightTtl: 100, // Valid for next 100 blocks (~100 seconds)
});
```

### Multiple Actions

```typescript
const metaTx = await account.createSignedMetaTransaction({
  receiverId: "contract.near",
  actions: [
    actions.functionCall("method1", { a: 1 }, teraToGas(10), nearToYocto("0")),
    actions.functionCall("method2", { b: 2 }, teraToGas(10), nearToYocto("0")),
    actions.transfer(1_000_000_000_000_000_000_000n),
  ],
});
```

---

## Relayer Integration

### Using `relayMetaTransaction()`

The simplest way to relay — use `account.relayMetaTransaction()`:

```typescript
import {
  Account,
  actions,
  teraToGas,
  nearToYocto,
  KeyPairString,
} from "near-api-js";

// User creates signed meta transaction
const metaTx = await userAccount.createSignedMetaTransaction({
  receiverId: "hello.near-examples.testnet",
  actions: [
    actions.functionCall(
      "set_greeting",
      { greeting: "meta" },
      teraToGas(10),
      nearToYocto("0"),
    ),
  ],
});

// Relayer submits using relayMetaTransaction()
const result = await relayerAccount.relayMetaTransaction(metaTx.signedDelegate);
console.log("Meta-transaction result:", result);
```

### Full Example: User + Relayer via HTTP

```typescript
// =====================
// USER SIDE
// =====================
const userAccount = new Account("user.near", provider, userPrivateKey);

const metaTx = await userAccount.createSignedMetaTransaction({
  receiverId: "nft.near",
  actions: [
    actions.functionCall(
      "nft_mint",
      { token_id: "123", receiver_id: "user.near" },
      teraToGas(50),
      nearToYocto("0"),
    ),
  ],
});

// Send to relayer via HTTP
const response = await fetch("https://relayer.example.com/relay", {
  method: "POST",
  body: JSON.stringify({
    signedDelegate: {
      delegateAction: metaTx.signedDelegate.delegateAction,
      signature: Array.from(metaTx.signedDelegate.signature.data),
    },
  }),
});

// =====================
// RELAYER SIDE (e.g. server endpoint)
// =====================
const relayerAccount = new Account("relayer.near", provider, relayerPrivateKey);

const { signedDelegate } = await request.json();
const result = await relayerAccount.relayMetaTransaction(signedDelegate);
```

---

## Block Height TTL

Meta transactions expire after a certain block height to prevent replay attacks.

```typescript
// Default: 100 blocks (~100 seconds at 1 block/second)
const metaTx = await account.createSignedMetaTransaction({
  receiverId: "contract.near",
  actions: [...],
  blockHeightTtl: 100,
});

// Check expiration
const currentBlock = await provider.viewBlock({ finality: "final" });
const expiresAt = metaTx.signedDelegate.delegateAction.maxBlockHeight;
const blocksRemaining = Number(expiresAt) - currentBlock.header.height;

if (blocksRemaining <= 0) {
  throw new Error("Meta transaction expired");
}
```

### Short TTL for Security

```typescript
// Very short window (10 blocks = ~10 seconds)
const metaTx = await account.createSignedMetaTransaction({
  receiverId: "contract.near",
  actions: [
    actions.functionCall(
      "sensitive_action",
      {},
      teraToGas(30),
      nearToYocto("0"),
    ),
  ],
  blockHeightTtl: 10,
});
```

---

## Error Handling

### Expired Meta Transaction

```typescript
try {
  await relayerAccount.relayMetaTransaction(metaTx.signedDelegate);
} catch (error) {
  if (error instanceof DelegateActionExpiredActionError) {
  }
}
```

### Nonce Issues

```typescript
try {
  await relayerAccount.relayMetaTransaction(signedDelegate);
} catch (error) {
  if (error instanceof DelegateActionInvalidNonceActionError) {
    // Meta transaction already used
  }
}
```

---

## Use Cases

### Gasless NFT Minting

```typescript
const metaTx = await userAccount.createSignedMetaTransaction({
  receiverId: "nft.near",
  actions: [
    actions.functionCall(
      "nft_mint",
      { token_id: "1" },
      teraToGas(50),
      nearToYocto("0"),
    ),
  ],
});
// Relayer sponsors the gas
await relayerAccount.relayMetaTransaction(metaTx.signedDelegate);
```

### Batch Onboarding

```typescript
// Multiple users create meta txs
const metaTxs = await Promise.all(
  users.map((user) => user.account.createSignedMetaTransaction({ ... })),
);

// Submit all in parallel
await Promise.all(
  metaTxs.map((metaTx) =>
    relayerAccount.relayMetaTransaction(metaTx.signedDelegate),
  ),
);
```
