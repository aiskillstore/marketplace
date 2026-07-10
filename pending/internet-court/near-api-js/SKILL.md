---
name: near-api-js
description: >-
  Guide for developing with near-api-js v7 - the JavaScript/TypeScript library for NEAR blockchain interaction.
  Use when: (1) building apps that interact with NEAR blockchain, (2) creating/signing transactions,
  (3) calling smart contracts, (4) managing accounts and keys, (5) working with NEAR RPC API,
  (6) handling FT/NFT tokens on NEAR, (7) using NEAR cryptographic operations (KeyPair, signing),
  (8) converting between NEAR units (yocto, gas), (9) gasless/meta transactions with relayers,
  (10) NEP-413 message signing for authentication,
  (11) storage deposit management for FT contracts. Triggers on any NEAR blockchain development tasks.
---

# near-api-js Skill

JavaScript/TypeScript library for NEAR blockchain interaction. Works in browser and Node.js.

## Quick Start

```typescript
import { Account, JsonRpcProvider, KeyPairString } from "near-api-js";
import { NEAR } from "near-api-js/tokens";

// Connect to testnet
const provider = new JsonRpcProvider({ url: "https://test.rpc.fastnear.com" });

// Create account with signer
const account = new Account(
  "my-account.testnet",
  provider,
  "ed25519:..." as KeyPairString,
);

// View call (read-only, via provider)
const data = await provider.callFunction({
  contractId: "guestbook.near-examples.testnet",
  method: "get_messages",
  args: {},
});

// Change call (requires account)
await account.callFunction({
  contractId: "guestbook.near-examples.testnet",
  methodName: "add_message",
  args: { text: "Hello!" },
  gas: teraToGas("30"),
  deposit: nearToYocto("0.1"),
});
```

## Import Cheatsheet

```typescript
// Core
import { Account, JsonRpcProvider, FailoverRpcProvider } from "near-api-js";
import { KeyPair, PublicKey, KeyType, KeyPairString } from "near-api-js";

// Signers
import { KeyPairSigner, MultiKeySigner, Signer } from "near-api-js";

// Units
import { nearToYocto, yoctoToNear, teraToGas, gigaToGas } from "near-api-js";

// Tokens
import { NEAR, FungibleToken } from "near-api-js/tokens";
import { USDC, wNEAR } from "near-api-js/tokens/mainnet";
import { USDT } from "near-api-js/tokens/testnet";

// Seed phrases
import { generateSeedPhrase, parseSeedPhrase } from "near-api-js/seed-phrase";

// Transactions
import { createTransaction, signTransaction, actions } from "near-api-js";

// Contract with ABI
import { Contract } from "near-api-js";

// Transform key into implicit account ID
import { keyToImplicitAddress } from "near-api-js";

// NEP-413 signing & verification
import { verifyMessage, signMessage } from "near-api-js/nep413";

import {
  RpcError,
  RpcMethodNotFoundError,
  RpcRequestParseError,
  ContractMethodNotFoundError,
  AccountDoesNotExistError,
  // and many more
} from "near-api-js/rpc-errors";
```

## Core Modules

### Account

Main class for account operations.

```typescript
// With signer (can sign transactions)
const account = new Account(accountId, provider, privateKey);

// Without signer (read-only, can add signer later)
const account = new Account(accountId, provider);

// Add signer later
const signer = KeyPairSigner.fromSecretKey(privateKey);
account.setSigner(signer);

// Get state
const state = await account.getState(); // { balance: { total, available, locked }, storageUsage }

// Get balance (with optional token parameter)
const balance = await account.getBalance(); // NEAR balance
const balance = await account.getBalance(USDC); // FT balance

// Transfer NEAR
await account.transfer({
  receiverId: "bob.testnet",
  amount: NEAR.toUnits("0.1"),
  token: NEAR,
});

// Transfer USDC
await account.transfer({
  receiverId: "bob.testnet",
  amount: USDC.toUnits("0.1"),
  token: USDC,
});

// Call contract
await account.callFunction({
  contractId: "contract.testnet",
  methodName: "set_greeting",
  args: { message: "Hello" },
  deposit: nearToYocto("0"),
  gas: teraToGas("30"),
});

// Sign and send transaction with multiple actions
await account.signAndSendTransaction({
  receiverId: "contract.testnet",
  actions: [
    actions.functionCall(
      "method",
      { arg: "value" },
      teraToGas("30"),
      nearToYocto("0"),
    ),
    actions.transfer(nearToYocto("1")),
  ],
});
```

### Account Management

```typescript
// Add full access key
await account.addFullAccessKey(
  keyPair.getPublicKey(), // or string "ed25519:2ASWc..."
);

// Add function call access key
await account.addFunctionCallAccessKey({
  publicKey: keyPair.getPublicKey(), // or string "ed25519:2ASWc..."
  contractId: "contract.testnet",
  methodNames: ["example_method"],
  allowance: nearToYocto("0.25"), // use "0" for unlimited
});

// Delete key
await account.deleteKey(keyPair.getPublicKey()); // or string "ed25519:2ASWc..."

// Delete account and transfer remaining NEAR tokens to beneficiary (FTs and NFTs must be transferred manually before deleting account)
await account.deleteAccount("beneficiary.testnet");
```

### Provider

RPC client for querying blockchain.

```typescript
const provider = new JsonRpcProvider({ url: "https://rpc.mainnet.near.org" });

// Failover provider
const failover = new FailoverRpcProvider([
  new JsonRpcProvider({ url: "https://rpc.mainnet.near.org" }),
  new JsonRpcProvider({ url: "https://free.rpc.fastnear.com" }),
  new JsonRpcProvider({ url: "https://rpc.mainnet.near.org" }),
]);

// Query methods
await provider.viewAccount({ accountId: "alice.near" });
await provider.viewAccessKey({
  accountId: "alice.near",
  publicKey: keyPair.getPublicKey(), // or string "ed25519:2ASWc..."
});
await provider.viewAccessKeyList({ accountId: "alice.near" });
// read-only call to contract method
await provider.callFunction({
  contractId: "contract.testnet",
  method: "get_greeting",
  args: {},
});
await provider.viewBlock({ finality: "final" });
await provider.sendTransaction(signedTx);
```

### Signers

```typescript
import { KeyPairSigner, MultiKeySigner } from "near-api-js";

// signer shouldn't be used directly for most use cases, instead it's used internally by Account class
const signer = KeyPairSigner.fromSecretKey(privateKey); // or "new KeyPairSigner(keyPair)"

const account = new Account(accountId, provider, signer);
```

### Contract (with ABI)

```typescript
import { Contract, AbiRoot } from "near-api-js";

// ABI definition requires "as const" (const assertions), otherwise types won't be inferred correctly
const abi = {
  schema_version: "0.4.0",
  metadata: {},
  body: {
    functions: [
      {
        name: "add_message",
        kind: "call",
        modifiers: ["payable"],
        params: {
          serialization_type: "json",
          args: [
            {
              name: "text",
              type_schema: {
                type: "string",
              },
            },
          ],
        },
      },
      {
        name: "total_messages",
        kind: "view",
        result: {
          serialization_type: "json",
          type_schema: {
            type: "integer",
            format: "uint32",
            minimum: 0.0,
          },
        },
      },
    ],
    root_schema: {},
  },
} as const satisfies AbiRoot;

const contract = new Contract({
  contractId: "guestbook.near-examples.testnet",
  provider: provider,
  abi: abi,
});

// the interface of view and call methods are fully inferred from the ABI, including argument and return types
const total = await contract.view.total_messages();
await contract.call.add_message({
  account: account,
  args: { text: "Hello, NEAR!" },
  deposit: nearToYocto("0.1"),
});
```

### Contract (without ABI)

```typescript
import { Contract, AbiRoot } from "near-api-js";

const contract = new Contract({
  contractId: "guestbook.near-examples.testnet",
  provider: provider,
});

// the interface of view and call methods are generic and not inferred without ABI, so you need to specify argument and return types manually using generics
const total = await contract.view.total_messages<number>({ args: {} });
await contract.call.add_message<void>({
  account: account,
  args: { text: "Hello, NEAR!" },
  deposit: nearToYocto("0.1"),
});
```

### Seed Phrases

```typescript
import { generateSeedPhrase, parseSeedPhrase } from "near-api-js/seed-phrase";

const { seedPhrase, keyPair } = generateSeedPhrase();

const keyPair = parseSeedPhrase("word1 word2 ... word12");

// Use with Account
const account = new Account(accountId, provider, new KeyPairSigner(keyPair));
```

### Tokens

```typescript
import { NEAR, FungibleToken } from "near-api-js/tokens";
import { USDT } from "near-api-js/tokens/testnet";

// Unit conversion
NEAR.toUnits("1.5"); // 1500000000000000000000000n (yoctoNEAR)
NEAR.toDecimal("1500000000000000000000000"); // "1.5" (NEAR)

// Transfer NEAR
await account.transfer({
  token: NEAR,
  amount: NEAR.toUnits("0.1"),
  receiverId: "bob.testnet",
});

// Transfer USDT
await account.transfer({
  token: USDT,
  amount: USDT.toUnits("1"),
  receiverId: "bob.testnet",
});

// Transfer custom Fungible Token
const REF = new FungibleToken("ref.fakes.testnet", {
  decimals: 18,
  symbol: "REF",
  name: "REF Token",
});
await account.transfer({
  token: REF,
  amount: REF.toUnits("1"),
  receiverId: "bob.testnet",
});

// NEP-141 requires the receiver to be registered before receiving tokens, usually it's the receiver's responsibility to register their account, but in some cases the sender might want to cover the registration cost for the receiver
await USDT.registerAccount({
  accountIdToRegister: "bob.testnet",
  fundingAccount: account,
});
```

### Actions

All transaction actions.

```typescript
import { actions } from "near-api-js";

actions.transfer(amount);
actions.functionCall(methodName, args, gas, deposit);
actions.createAccount();
actions.deployContract(wasmBytes);
actions.addFullAccessKey(publicKey);
actions.addFunctionAccessKey(publicKey, contractId, methodNames, allowance);
actions.deleteKey(publicKey);
actions.deleteAccount(beneficiaryId);
actions.stake(amount, publicKey);
actions.signedDelegate(signedDelegateAction);
```

## RPC Endpoints

| Network            | URL                             |
| ------------------ | ------------------------------- |
| Mainnet            | `https://rpc.mainnet.near.org`  |
| Mainnet (FastNEAR) | `https://free.rpc.fastnear.com` |
| Testnet            | `https://rpc.testnet.near.org`  |
| Testnet (FastNEAR) | `https://test.rpc.fastnear.com` |

## Common Patterns

### Batch Actions

```typescript
await account.signAndSendTransaction({
  receiverId: account.accountId,
  actions: [
    actions.addFullAccessKey(key1.getPublicKey()),
    actions.addFullAccessKey(key2.getPublicKey()),
  ],
});
```

### Meta Transactions

```typescript
// Create and sign meta tx (user side)
const metaTx = await userAccount.createSignedMetaTransaction({
  receiverId: "contract.near",
  actions: [
    actions.functionCall("method", {}, teraToGas(10), nearToYocto("0")),
  ],
});

// Relay via funded account
const result = await relayerAccount.relayMetaTransaction(metaTx.signedDelegate);
```

### Implicit Accounts

```typescript
// keep in mind that implicit accounts don't actually exist on-chain until they receive at least 1 yoctoNEAR
const account = new Account(
  keyToImplicitAddress(keyPair.getPublicKey()), // implicit account ID derived from public key
  provider,
  new KeyPairSigner(keyPair),
);
```

### NEP-413

```typescript
import { signMessage, verifyMessage } from "near-api-js/nep413";

const account = new Account("bob.near", provider, new KeyPairSigner(keyPair));

const signedMessage = await signMessage({
  signerAccount: account, // requires signer to be set on account
  payload: {
    message: "Hello, world!",
    recipient: "alice.near",
    nonce: new Uint8Array(new Array(32)), // random 32 bytes
  },
});

// throws an Error if verification fails
await verifyMessage({
  signerAccountId: account.accountId,
  signerPublicKey: keyPair.getPublicKey(),
  signature: signedMessage.signature,
  payload: {
    message: "Hello, world!",
    recipient: "alice.near",
    nonce: new Uint8Array(new Array(32)),
  }, // exact payload that was used above for signing
  provider: provider,
});
```

### Manual Transaction Signing

```typescript
const signer = KeyPairSigner.fromSecretKey(privateKey);

const account = new Account(accountId, provider); // no signer needed

const transaction = await account.createTransaction({
  receiverId: "receiver.testnet",
  actions: [actions.transfer(nearToYocto("0.1"))],
  publicKey: await signer.getPublicKey(),
});

const signResult = await signer.signTransaction(transaction);
const result = await provider.sendTransaction(signResult.signedTransaction);
```

### Concurrent Transactions

```typescript
// Account is optimized for handling concurrent transactions efficiently, put as many transactions as you want in the array and they will be executed in parallel (usually within 1-2 blocks, depending on the amount)
await Promise.all([
  account.transfer({
    amount: nearToYocto(1),
    receiverId: "user1.testnet",
  }),
  account.transfer({
    amount: nearToYocto(2),
    receiverId: "user2.testnet",
  }),
  account.transfer({
    amount: nearToYocto(3),
    receiverId: "user3.testnet",
  }),
]);
```

## Error Handling

```typescript
import {
  AccountDoesNotExistActionError,
  RpcRequestParseError,
  UnknownBlockError,
  RpcError,
  // and many more
} from "near-api-js/rpc-errors";

// End users can catch action-level errors (e.g. when a transaction fails because the recipient account does not exist):
try {
  await account.transfer({
    amount: nearToYocto(0.01),
    receiverId: "unexisted_account.testnet",
  });
} catch (error) {
  if (error instanceof AccountDoesNotExistActionError) {
    console.error(
      `Transaction ${error.txHash} failed because recipient ${error.accountId} does not exist!`,
    );
  }
}

// Or, RPC request validation and parsing errors can also be handled explicitly (e.g. when an invalid account ID format is included in a transaction):
try {
  await account.transfer({
    amount: nearToYocto(0.001),
    receiverId: "account_name_that_fail_validation%.testnet",
  });
} catch (error) {
  if (error instanceof RpcRequestParseError) {
    // Failed parsing args: the value could not be decoded from borsh due to:
    // invalid value: "account_name_that_fail_validation%.testnet",
    // the Account ID contains an invalid character '%' at index 33
    console.error(error.message);
  }
}

// Or, some requests may reference data that is no longer available or cannot be resolved by the node (e.g. querying a block that cannot be found):
const unexistedBlockHeight = 1_000_000_000_000_000;

try {
  await provider.viewBlock({ blockId: unexistedBlockHeight });
} catch (error) {
  if (error instanceof UnknownBlockError) {
    console.error(
      `Block at height ${unexistedBlockHeight} could not be found on the node!`,
    );
  }
}

// All exported errors ultimately extend the RpcError base class, so applications can also catch and handle any RPC-related error in a single place when fine-grained handling is not required:
try {
  await provider.viewAccessKey({
    accountId: "user.testnet",
    publicKey: "ed25519:EaQnZxCMwh9yhkqW2XE2umd21iNmXep1BkM6Wtw2Qr1b",
  });
} catch (error) {
  if (error instanceof RpcError) {
    // Access key ed25519:EaQnZx... does not exist at block height ...
    console.error(error.message);
  }
}

try {
  await provider.viewAccessKey({
    accountId: "user.testnet",
    publicKey: "ed25519:EaQnZxCMwh9yhkqW2XE2umd21iNmXep1BkM6Wtw2Qr1bxxxx", // invalid key here
  });
} catch (error) {
  if (error instanceof RpcError) {
    // Failed parsing args: invalid key length: expected the input of 32 bytes, but 33 was given
    console.error(error.message);
  }
}
```

## Reference Documentation

For detailed patterns and advanced usage, see:

- [API Patterns Reference](references/api_patterns.md) - Complete Account/Provider method reference, manual signing, parallel transactions
- [Tokens Guide](references/tokens_guide.md) - FT/NFT operations, storage deposits, pre-defined tokens
- [Key Management](references/key_management.md) - KeyPair types, seed phrases, signers, access keys
- [Meta Transactions](references/meta_transactions.md) - Gasless transactions, relayer integration
- [NEP-413](references/nep413.md) - NEP-413 message signing & verification
- [Contracts](references/contracts.md) - Typed Contract with ABI, Contract without ABI
