# Tokens Guide

Complete guide for NEAR token operations with near-api-js.

## Table of Contents

1. [Native NEAR Token](#native-near-token)
2. [Fungible Tokens (NEP-141)](#fungible-tokens-nep-141)
3. [NFTs (NEP-171)](#nfts-nep-171)
4. [Pre-defined Tokens](#pre-defined-tokens)
5. [Storage Management](#storage-management)
6. [Unit Conversion](#unit-conversion)

---

## Native NEAR Token

```typescript
import { Account } from "near-api-js";
import { NEAR } from "near-api-js/tokens";

// Unit conversion
NEAR.toUnits("1.5"); // 1500000000000000000000000n (yoctoNEAR)
NEAR.toDecimal(1_500_000_000_000_000_000_000_000n); // "1.5"
NEAR.toDecimal(amount, 4); // Limit precision to 4 decimals

// Transfer NEAR
await account.transfer({
  token: NEAR,
  amount: NEAR.toUnits("0.1"),
  receiverId: "bob.testnet",
});

// Get balance
const balance = await account.getBalance();
const { available, locked, total } = (await account.getState()).balance;
```

---

## Fungible Tokens (NEP-141)

### Creating FT Instance

```typescript
import { FungibleToken } from "near-api-js/tokens";

// Create with metadata
const REF = new FungibleToken("ref.fakes.testnet", {
  name: "REF Token",
  symbol: "REF",
  decimals: 18,
});

// Use pre-defined tokens
import { USDC, wNEAR } from "near-api-js/tokens/mainnet";
import { USDT } from "near-api-js/tokens/testnet";
```

### Transfer Operations

```typescript
// Simple transfer (receiver must be registered)
await account.transfer({
  token: USDT,
  amount: USDT.toUnits("1"),
  receiverId: "bob.testnet",
});

// Transfer with contract call (ft_transfer_call)
await token.transferCall({
  from: account,
  receiverId: "dex.near",
  amount: token.toUnits("100"),
  msg: JSON.stringify({ action: "swap", out_token: "near" }),
});
```

### Query Balance

```typescript
const balance = await token.getBalance(account);
console.log(`Balance: ${token.toDecimal(balance)} ${token.metadata.symbol}`);

// Or via account.getBalance with token parameter
const bal = await account.getBalance(USDT);
```

### Account Registration

```typescript
// NEP-141 requires receivers to be registered before receiving tokens (it has to be done once per token)
await USDT.registerAccount({
  accountIdToRegister: "new-user.testnet",
  fundingAccount: account, // Pays for storage
});
```

---

## NFTs (NEP-171)

```typescript
// View NFTs owned by account
const nfts = await provider.callFunction({
  contractId: "nft.near",
  method: "nft_tokens_for_owner",
  args: { account_id: "alice.near", limit: 10 },
});

// Transfer NFT
await account.callFunction({
  contractId: "nft.near",
  methodName: "nft_transfer",
  args: {
    receiver_id: "bob.near",
    token_id: "token-123",
  },
  deposit: 1n, // 1 yoctoNEAR required
});

// Transfer with call
await account.callFunction({
  contractId: "nft.near",
  methodName: "nft_transfer_call",
  args: {
    receiver_id: "marketplace.near",
    token_id: "token-123",
    msg: JSON.stringify({ price: "1000000000000000000000000" }),
  },
  deposit: 1n, // 1 yoctoNEAR required
  gas: teraToGas("50"),
});
```

---

## Pre-defined Tokens

### Mainnet

```typescript
import { USDC, USDT, wNEAR, DAI } from "near-api-js/tokens/mainnet";

await account.transfer({
  receiverId: "bob.near",
  amount: USDC.toUnits("100"),
  token: USDC,
});
```

### Testnet

```typescript
import { USDT } from "near-api-js/tokens/testnet";
```

### Token Metadata

```typescript
token.metadata.name; // "USD Coin"
token.metadata.symbol; // "USDC"
token.metadata.decimals; // 6
token.metadata.icon; // SVG data URI (optional)
token.accountId; // "a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.factory.bridge.near"
```

---

## Storage Management

FT contracts require storage deposits before receiving tokens.

### Register Account

```typescript
await token.registerAccount({
  accountIdToRegister: "new-user.near",
  fundingAccount: account, // Pays for storage
});
```

### Unregister Account

```typescript
await token.unregisterAccount({
  account: account,
  force: false, // true = forfeit remaining tokens
});
```

### Manual Storage Deposit

```typescript
// Check storage requirements
const bounds = await provider.callFunction({
  contractId: token.accountId,
  method: "storage_balance_bounds",
  args: {},
});

// Check if registered
const balance = await provider.callFunction({
  contractId: token.accountId,
  method: "storage_balance_of",
  args: { account_id: "user.near" },
});
// null = not registered, { total, available } = registered

// Deposit storage
await account.callFunction({
  contractId: token.accountId,
  methodName: "storage_deposit",
  args: { account_id: "new-user.near" },
  deposit: bounds.min,
});
```

---

## Unit Conversion

### NEAR/yocto Utilities

```typescript
import { nearToYocto, yoctoToNear, teraToGas, gigaToGas } from "near-api-js";

// nearToYocto — converts NEAR string to yoctoNEAR bigint
nearToYocto("1"); // 1000000000000000000000000n
nearToYocto("0.1"); // 100000000000000000000000n
nearToYocto("0"); // 0n

// yoctoToNear — converts yoctoNEAR to NEAR string
yoctoToNear(1_000_000_000_000_000_000_000_000n); // "1"
yoctoToNear(1_234_000_000_000_000_000_000_000n); // "1.234"

// Gas utilities
teraToGas("30"); // 30_000_000_000_000n (30 TGas)
teraToGas(10); // 10_000_000_000_000n (10 TGas)
gigaToGas("300"); // 300_000_000_000n
```

### Token Unit Methods

```typescript
import { NEAR } from "near-api-js/tokens";

NEAR.toUnits("1.5"); // 1500000000000000000000000n
NEAR.toDecimal(amount); // "1.5"
NEAR.toDecimal(amount, 4); // limit decimal places

// Same interface for FTs
USDC.toUnits("50"); // 50000000n (6 decimals)
USDC.toDecimal(50000000n); // "50"
```

---

## Common Patterns

### Batch Token Operations

```typescript
import { actions, teraToGas } from "near-api-js";

// Multiple FT transfers in one transaction
const calls = [
  actions.functionCall(
    "ft_transfer",
    { receiver_id: "alice.near", amount: "1000000" },
    teraToGas("30"),
    1n,
  ),
  actions.functionCall(
    "ft_transfer",
    { receiver_id: "bob.near", amount: "2000000" },
    teraToGas("30"),
    1n,
  ),
];

await account.signAndSendTransaction({
  receiverId: token.accountId,
  actions: calls,
});
```
