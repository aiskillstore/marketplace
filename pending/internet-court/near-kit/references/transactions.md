# Transaction Builder

Fluent API for constructing multi-action NEAR transactions.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Available Actions](#available-actions)
- [Multi-Action Transactions](#multi-action-transactions)
- [Meta-Transactions (NEP-366)](#meta-transactions-nep-366)
- [Manual Sign Flow](#manual-sign-flow)

---

## Basic Usage

```typescript
const receipt = await near
  .transaction("alice.near")  // Signer account
  .transfer("bob.near", "1 NEAR")
  .send()

console.log("Transaction hash:", receipt.transaction.hash)
```

---

## Available Actions

### Transfer

```typescript
await near
  .transaction("alice.near")
  .transfer("bob.near", "10 NEAR")
  .send()
```

### Function Call

```typescript
await near
  .transaction("alice.near")
  .functionCall(
    "contract.near",
    "store_data",
    { key: "value" },
    { gas: "30 Tgas", attachedDeposit: "0.1 NEAR" }
  )
  .send()
```

### Create Account

```typescript
await near
  .transaction("alice.near")
  .createAccount("sub.alice.near")
  .transfer("sub.alice.near", "1 NEAR")
  .send()
```

### Delete Account

```typescript
await near
  .transaction("account-to-delete.near")
  .deleteAccount({ beneficiary: "alice.near" })
  .send()
```

### Deploy Contract

```typescript

const wasm = await fs.readFile("./contract.wasm")
await near
  .transaction("alice.near")
  .deployContract("contract.alice.near", wasm)
  .send()
```

### Add Key

```typescript
// Full access key
await near
  .transaction("alice.near")
  .addKey("ed25519:...", { type: "fullAccess" })
  .send()

// Function call access key
await near
  .transaction("alice.near")
  .addKey("ed25519:...", {
    type: "functionCall",
    receiverId: "contract.near",
    methodNames: ["transfer", "approve"],
    allowance: "1 NEAR",
  })
  .send()
```

### Delete Key

```typescript
await near
  .transaction("alice.near")
  .deleteKey("alice.near", "ed25519:...")
  .send()
```

### Stake

```typescript
await near
  .transaction("alice.near")
  .stake("100 NEAR", "ed25519:...")
  .send()
```

### Signed Delegate Action

```typescript
// Used by relayers to submit meta-transactions
await near
  .transaction("relayer.near")
  .signedDelegateAction(signedDelegate)
  .send()
```

---

## Multi-Action Transactions

Chain multiple actions in a single atomic transaction:

```typescript
// Batch function call + transfer
const result = await near.transaction(accountId)
  .functionCall("counter.near-examples.testnet", "increment", {}, { gas: "30 Tgas" })
  .transfer("counter.near-examples.testnet", "0.001 NEAR")
  .send()

// Create + fund + deploy + initialize
await near
  .transaction("alice.near")
  .createAccount("app.alice.near")
  .transfer("app.alice.near", "5 NEAR")
  .addKey(publicKey, { type: "fullAccess" })
  .deployContract("app.alice.near", contractWasm)
  .functionCall("app.alice.near", "init", { owner: "alice.near" })
  .send()
```

---

## Meta-Transactions (NEP-366)

Gasless transactions where a relayer pays for gas.

### User Side (Signs Off-Chain)

```typescript
import { Near } from "near-kit"

const userNear = new Near({
  network: "testnet",
  privateKey: "ed25519:...",
  defaultSignerId: "user.testnet",
})

// Build and sign delegate action (no gas cost)
const { payload, signedDelegateAction } = await userNear
  .transaction("user.testnet")
  .functionCall(
    "contract.near",
    "do_something",
    { arg: "value" },
    { gas: "30 Tgas" }
  )
  .delegate({
    blockHeightOffset: 100, // Valid for 100 blocks (~100 seconds)
  })

// Send payload to relayer via API
await fetch("/api/relay", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ payload }),
})
```

### Relayer Side (Pays Gas)

```typescript
import { decodeSignedDelegateAction, Near } from "near-kit"

const relayerNear = new Near({
  network: "testnet",
  privateKey: "ed25519:...",
  defaultSignerId: "relayer.testnet",
})

// Decode the payload from user
const signedDelegate = decodeSignedDelegateAction(payload)

// Submit to blockchain (relayer pays gas)
const result = await relayerNear
  .transaction("relayer.testnet")
  .signedDelegateAction(signedDelegate)
  .send()

// Contract sees user as the signer, relayer paid the gas
```

---

## Manual Sign Flow

Build, sign, inspect, and send transactions separately.

```typescript
import { Near } from "near-kit"

// No private key needed in the Near instance for manual signing
const near = new Near({ network: "testnet" })

// Build a transaction and attach a signer key
const tx = near
  .transaction(accountId)
  .transfer("receiver-account.testnet", "0.001 NEAR")
  .signWith(privateKey)  // specify which key signs

// Sign the transaction (but don't send yet)
await tx.sign()

// Get the transaction hash before sending
const hash = tx.getHash()
console.log("Transaction hash:", hash)

// Serialize the signed transaction (for offline use or external sending)
const serialized = tx.serialize()
console.log("Serialized transaction bytes:", serialized.length)

// Now send the signed transaction
const result = await tx.send()
console.log("Transaction sent:", result.transaction.hash)
```

### Wait Until Options

```typescript
await near
  .transaction("alice.near")
  .transfer("bob.near", "1 NEAR")
  .send({ waitUntil: "FINAL" })  // Wait for finality

// Options: "NONE" | "INCLUDED" | "EXECUTED_OPTIMISTIC" | "FINAL"
```