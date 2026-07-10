# Keys and Testing

Key management options and local testing with Sandbox.

## Table of Contents

- [Key Stores](#key-stores)
- [Key Utilities](#key-utilities)
- [Sandbox Testing](#sandbox-testing)
- [NEP-413 Message Signing](#nep-413-message-signing)

---

## Key Stores

### InMemoryKeyStore

Ephemeral storage for runtime use.

```typescript
import { Near, InMemoryKeyStore } from "near-kit";

const keyStore = new InMemoryKeyStore({
  "alice.near": "ed25519:...",
  "bob.near": "ed25519:...",
});

const near = new Near({
  network: "mainnet",
  keyStore,
});
```

### FileKeyStore

Persistent file-based storage (NEAR CLI compatible).

```typescript
import { Near } from "near-kit";
import { FileKeyStore } from "near-kit/keys/file";

const near = new Near({
  network: "mainnet",
  keyStore: new FileKeyStore("~/.near-credentials", "mainnet"),
});
```

### NativeKeyStore

OS keyring integration (macOS Keychain, Windows Credential Manager).

```typescript
import { Near } from "near-kit";
import { NativeKeyStore } from "near-kit/keys/native";

const near = new Near({
  network: "mainnet",
  keyStore: new NativeKeyStore(),
});
```

### RotatingKeyStore

High-throughput concurrent transactions with multiple keys.

```typescript
import { Near, generateKey, RotatingKeyStore } from "near-kit";

const accountId = "alice.testnet";
const keyStore = new RotatingKeyStore();

// First, create Near instance with a single key for setup
const near = new Near({
  network: "testnet",
  privateKey: "ed25519:...",
  defaultSignerId: accountId,
});

// Generate and add multiple keys
const keys = [];
for (let i = 0; i < 5; i++) {
  const newKey = generateKey();
  keys.push(newKey);

  // Add key to account on-chain
  await near
    .transaction(accountId)
    .addKey(newKey.publicKey.toString(), { type: "fullAccess" })
    .send();

  // Add key to the rotating store
  await keyStore.add(accountId, newKey);
}

// Create new Near client with the rotating keystore
const nearWithRotating = new Near({
  network: "testnet",
  keyStore,
  defaultSignerId: accountId,
});

// Send concurrent transactions — no nonce conflicts
const transfers = Array.from({ length: 10 }, () =>
  nearWithRotating.send("influencer.testnet", "0.001 NEAR"),
);
const results = await Promise.all(transfers);
```

### Direct Private Key

Simplest option for scripts.

```typescript
const near = new Near({
  network: "testnet",
  privateKey: "ed25519:...",
  defaultSignerId: "alice.testnet",
});
```

---

## Key Utilities

```typescript
import {
  generateKey,
  generateSeedPhrase,
  parseSeedPhrase,
  isValidAccountId,
  isPrivateKey,
  isValidPublicKey,
  validatePrivateKey,
} from "near-kit";
```

### generateKey()

```typescript
const key = generateKey();
// key.publicKey  — PublicKey-like object, use .toString() for "ed25519:..."
// key.secretKey  — string "ed25519:..."
```

### generateSeedPhrase()

```typescript
const seedPhrase = generateSeedPhrase();
// "word1 word2 word3 ... word12"
```

### parseSeedPhrase()

```typescript
const keyPair = parseSeedPhrase(seedPhrase);
const publicKey = keyPair.publicKey.toString(); // "ed25519:..."

await near.call("testnet", "create_account", {
  new_account_id: "new-account.testnet",
  new_public_key: publicKey,
});
```

### Full Seed Phrase Flow

```typescript
import { Near, generateSeedPhrase, parseSeedPhrase } from "near-kit";

const near = new Near({
  network: "testnet",
  privateKey: "ed25519:...",
  defaultSignerId: accountId,
});

// Generate seed phrase (returns a string)
const seedPhrase = generateSeedPhrase();

// Parse to get key pair
const keyPair = parseSeedPhrase(seedPhrase);
const publicKey = keyPair.publicKey.toString();

// Create account using the derived public key
const newAccountId = `acc-${Date.now()}.testnet`;
await near.call("testnet", "create_account", {
  new_account_id: newAccountId,
  new_public_key: publicKey,
});
```

### Validation

```typescript
isValidAccountId("alice.near"); // true
isValidAccountId("INVALID"); // false
isPrivateKey("ed25519:..."); // true
isValidPublicKey("ed25519:..."); // true
validatePrivateKey("ed25519:..."); // throws if invalid
```

---

## Sandbox Testing

Local NEAR node for integration testing.

### Basic Usage

```typescript
import { Near } from "near-kit";
import { Sandbox } from "near-kit/sandbox";

const sandbox = await Sandbox.start();
const near = new Near({ network: sandbox });

// Root account available for setup
console.log("Root account:", sandbox.rootAccount.id);
// e.g., "test.near"

// Create test account
const testAccount = `test-${Date.now()}.${sandbox.rootAccount.id}`;
await near
  .transaction(sandbox.rootAccount.id)
  .createAccount(testAccount)
  .transfer(testAccount, "10 NEAR")
  .send();

// Run tests...

await sandbox.stop();
```

### Vitest Integration

```typescript
import { describe, test, beforeAll, afterAll, expect } from "vitest";
import { Near } from "near-kit";
import { Sandbox } from "near-kit/sandbox";

describe("My Contract Tests", () => {
  let sandbox: Sandbox;
  let near: Near;

  beforeAll(async () => {
    sandbox = await Sandbox.start();
    near = new Near({ network: sandbox });
  }, 60000); // Sandbox startup timeout

  afterAll(async () => {
    await sandbox.stop();
  });

  test("should create account", async () => {
    const account = `test-${Date.now()}.${sandbox.rootAccount.id}`;

    await near
      .transaction(sandbox.rootAccount.id)
      .createAccount(account)
      .transfer(account, "5 NEAR")
      .send();

    const exists = await near.accountExists(account);
    expect(exists).toBe(true);

    const balance = await near.getBalance(account);
    expect(balance).toContain("NEAR");
  });

  test("should deploy and call contract", async () => {
    const contractWasm = await fs.readFile("./contract.wasm");
    const contract = `contract-${Date.now()}.${sandbox.rootAccount.id}`;

    await near
      .transaction(sandbox.rootAccount.id)
      .createAccount(contract)
      .transfer(contract, "10 NEAR")
      .deployContract(contract, contractWasm)
      .functionCall(contract, "init", { owner: sandbox.rootAccount.id })
      .send();

    const result = await near.view(contract, "get_owner", {});
    expect(result).toBe(sandbox.rootAccount.id);
  });
});
```

### Unique Account Names

Always use unique names to avoid conflicts:

```typescript
const uniqueAccount = `test-${Date.now()}.${sandbox.rootAccount.id}`;
// e.g., "test-1706012345678.test.near"
```

---

## NEP-413 Message Signing

Gasless authentication using cryptographic signatures.

### Client Side (Sign Message)

```typescript
import { Near, generateNonce } from "near-kit";

const near = new Near({
  network: "mainnet",
  privateKey: "ed25519:...",
  defaultSignerId: "user.near",
});

// Generate random nonce for replay protection
const nonce = generateNonce();

// Sign message (no gas cost)
const signedMessage = await near.signMessage({
  message: "Sign in to My App",
  recipient: "myapp.com",
  nonce,
});

// Send to server for verification
await fetch("/api/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    signedMessage,
    nonce: Array.from(nonce),
  }),
});
```

### Server Side (Verify Signature)

```typescript
import { Near, verifyNep413Signature } from "near-kit";

const near = new Near({ network: "testnet" });

const isValid = await verifyNep413Signature(
  signedMessage,
  {
    message: MESSAGE,
    recipient: APP,
    nonce: CHALLENGE,
  },
  {
    near,
    maxAge: 300000, // 5 mins
  },
);

console.log("Signature valid:", isValid);
```

### SignedMessage Structure

```typescript
interface SignedMessage {
  accountId: string;
  publicKey: string;
  signature: string;
  message: string;
  recipient: string;
  nonce: number[];
}
```