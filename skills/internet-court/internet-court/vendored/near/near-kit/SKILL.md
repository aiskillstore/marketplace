---
name: near-kit
description: TypeScript library for NEAR Protocol blockchain interaction. Use this skill when writing code that interacts with NEAR Protocol, including viewing contract data, calling contract methods, sending NEAR tokens, building transactions, creating type-safe contract wrappers, integrating wallets (Wallet Selector, HOT Connect), React hooks and providers (@near-kit/react), managing keys, testing with sandbox, meta-transactions (NEP-366), and message signing (NEP-413).
---

# near-kit

A TypeScript library for NEAR Protocol with an intuitive, fetch-like API.

## Quick Start

```typescript
import { Near } from "near-kit";

// Read-only (no key needed)
const near = new Near({ network: "testnet" });
const data = await near.view("contract.near", "get_data", { key: "value" });

// With signing capability
const near = new Near({
  network: "testnet",
  privateKey: "ed25519:...",
  defaultSignerId: "alice.testnet",
});
await near.call("contract.near", "method", { arg: "value" });
await near.send("bob.testnet", "1 NEAR");
```

## Import Cheatsheet

```typescript
// Core
import { Near } from "near-kit";

// Keys
import { generateKey, parseSeedPhrase, generateSeedPhrase } from "near-kit";
import { RotatingKeyStore, InMemoryKeyStore } from "near-kit";
import { FileKeyStore } from "near-kit/keys/file";
import { NativeKeyStore } from "near-kit/keys/native";

// Wallet adapters
import { fromHotConnect, fromWalletSelector } from "near-kit";

// NEP-413 verification
import { verifyNep413Signature } from "near-kit";

// Utilities
import { Amount, Gas, isValidAccountId } from "near-kit";
```

## Core Operations

### View Methods (Read-Only, Free)

```typescript
const result = await near.view("contract.near", "get_data", { key: "value" });
const balance = await near.getBalance("alice.near");
const exists = await near.accountExists("alice.near");
```

### Call Methods (Requires Signing)

```typescript
await near.call(
  "contract.near",
  "method",
  { arg: "value" },
  { gas: "30 Tgas", attachedDeposit: "1 NEAR" },
);
```

### Send NEAR Tokens

```typescript
await near.send("bob.near", "5 NEAR");
```

## Type-Safe Contracts

```typescript
import type { Contract } from "near-kit";

type MyContract = Contract<{
  view: {
    get_balance: (args: { account_id: string }) => Promise<string>;
  };
  call: {
    transfer: (args: { to: string; amount: string }) => Promise<void>;
  };
}>;

const contract = near.contract<MyContract>("token.near");

// View (no options needed)
await contract.view.get_balance({ account_id: "alice.near" });

// Call (options as second arg)
await contract.call.transfer(
  { to: "bob.near", amount: "10" },
  { attachedDeposit: "1 yocto" },
);
```

Untyped contract proxy:

```typescript
const guestbook = near.contract("guestbook.near-examples.testnet");

const total = await guestbook.view.total_messages();
const result = await guestbook.call.add_message(
  { text: "Hello!" },
  { gas: "30 Tgas" },
);
```

## Transaction Builder

Chain multiple actions in a single atomic transaction:

```typescript
const result = await near
  .transaction("alice.near")
  .functionCall("counter.near", "increment", {}, { gas: "30 Tgas" })
  .transfer("counter.near", "0.001 NEAR")
  .send();
```

**For all transaction actions and meta-transactions, see [references/transactions.md](references/transactions.md)**

## Configuration

### Backend/Scripts

```typescript
// Direct private key
const near = new Near({
  network: "testnet",
  privateKey: "ed25519:...",
  defaultSignerId: "alice.testnet",
});

// File-based keystore
import { FileKeyStore } from "near-kit/keys/file";
const near = new Near({
  network: "testnet",
  keyStore: new FileKeyStore("~/.near-credentials", "testnet"),
});

// High-throughput with rotating keys
import { RotatingKeyStore } from "near-kit";
const near = new Near({
  network: "mainnet",
  keyStore: new RotatingKeyStore({
    "bot.near": ["ed25519:key1...", "ed25519:key2...", "ed25519:key3..."],
  }),
});
```

**For all key stores and utilities, see [references/keys-and-testing.md](references/keys-and-testing.md)**

### Browser Wallets

```typescript
import { NearConnector } from "@hot-labs/near-connect";
import { Near, fromHotConnect } from "near-kit";

const connector = new NearConnector({ network: "mainnet" });

connector.on("wallet:signIn", async (event) => {
  const near = new Near({
    network: "mainnet",
    wallet: fromHotConnect(connector),
  });

  await near.call("contract.near", "method", { arg: "value" });
});

connector.connect();
```

**For HOT Connect and Wallet Selector integration, see [references/wallets.md](references/wallets.md)**

## React Bindings (@near-kit/react)

```tsx
import { NearProvider, useNear, useView, useCall } from "@near-kit/react";

function App() {
  return (
    <NearProvider config={{ network: "testnet" }}>
      <Counter />
    </NearProvider>
  );
}

function Counter() {
  const { data: count, isLoading } = useView<{}, number>({
    contractId: "counter.testnet",
    method: "get_count",
  });

  const { mutate: increment, isPending } = useCall({
    contractId: "counter.testnet",
    method: "increment",
  });

  if (isLoading) return <div>Loading...</div>;
  return (
    <button onClick={() => increment({})} disabled={isPending}>
      Count: {count}
    </button>
  );
}
```

**For all React hooks, React Query/SWR integration, and SSR patterns, see [references/react.md](references/react.md)**

## Testing with Sandbox

```typescript
import { Near } from "near-kit";
import { Sandbox } from "near-kit/sandbox";

const sandbox = await Sandbox.start();
const near = new Near({ network: sandbox });

const testAccount = `test-${Date.now()}.${sandbox.rootAccount.id}`;
await near
  .transaction(sandbox.rootAccount.id)
  .createAccount(testAccount)
  .transfer(testAccount, "10 NEAR")
  .send();

await sandbox.stop();
```

**For sandbox patterns and Vitest integration, see [references/keys-and-testing.md](references/keys-and-testing.md)**

## Error Handling

```typescript
import {
  InsufficientBalanceError,
  FunctionCallError,
  NetworkError,
  TimeoutError,
} from "near-kit";

try {
  await near.call("contract.near", "method", {});
} catch (error) {
  if (error instanceof InsufficientBalanceError) {
    console.log(`Need ${error.required}, have ${error.available}`);
  } else if (error instanceof FunctionCallError) {
    console.log(`Panic: ${error.panic}`, `Logs: ${error.logs}`);
  }
}
```

## Unit Formatting

All amounts accept human-readable formats:

```typescript
"10 NEAR"; // 10 NEAR
"10"; // 10 NEAR
10; // 10 NEAR
("30 Tgas"); // 30 trillion gas units
```

Programmatic formatting:

```typescript
import { Amount, Gas } from "near-kit";

Amount.NEAR(0.1);
Amount.yocto(1000n);
Amount.parse("5 NEAR");
Gas.parse("30 Tgas");
```

## Key Utilities

```typescript
import {
  generateKey,
  generateSeedPhrase,
  parseSeedPhrase,
  isValidAccountId,
} from "near-kit";

// Generate new keypair
const key = generateKey();
// key.publicKey, key.secretKey

// generateSeedPhrase() returns a string (just the phrase)
const seedPhrase = generateSeedPhrase();
// "word1 word2 word3 ... word12"

// parseSeedPhrase() returns a KeyPair-like object
const keyPair = parseSeedPhrase("word1 word2 ... word12");
// keyPair.publicKey, keyPair.secretKey

// Validation
isValidAccountId("alice.near"); // true
```

## NEP-413 Verification

```typescript
import { Near, verifyNep413Signature } from "near-kit";

const near = new Near({ network: "testnet" });

const isValid = await verifyNep413Signature(
  signedMessage,
  { message: "log me in", recipient: "myapp.com", nonce: challengeBuffer },
  { near, maxAge: Infinity },
);
```

## References

For detailed documentation on specific topics:

- **[React Bindings](references/react.md)** - Provider, hooks, React Query/SWR, SSR/Next.js
- **[Wallet Integration](references/wallets.md)** - HOT Connect, Wallet Selector, universal patterns
- **[Transaction Builder](references/transactions.md)** - All actions, meta-transactions (NEP-366)
- **[Keys and Testing](references/keys-and-testing.md)** - Key stores, utilities, sandbox, NEP-413 signing