# near-api-js API Patterns Reference

Detailed patterns and advanced usage examples for near-api-js.

## Table of Contents

1. [Account Methods Reference](#account-methods-reference)
2. [Provider Methods Reference](#provider-methods-reference)
3. [Action Types](#action-types)
4. [Type Definitions](#type-definitions)
5. [Advanced Patterns](#advanced-patterns)

---

## Account Methods Reference

### State & Information

| Method                      | Description                               | Returns                 |
| --------------------------- | ----------------------------------------- | ----------------------- |
| `getState()`                | Account balance, storage usage, code hash | `AccountState`          |
| `getBalance()`              | NEAR balance                              | `bigint`                |
| `getBalance(token)`         | FT balance for given token                | `bigint`                |
| `getAccessKey(publicKey)`   | Single access key info                    | `AccessKeyView`         |
| `getAccessKeyList()`        | All access keys                           | `AccessKeyList`         |
| `getContractCode()`         | Deployed contract WASM                    | `{ code_base64, hash }` |
| `getContractState(prefix?)` | Contract key-value storage                | `{ values }`            |

### Transactions

| Method                                                  | Description                      |
| ------------------------------------------------------- | -------------------------------- |
| `signAndSendTransaction({ receiverId, actions })`       | Sign and broadcast single tx     |
| `signAndSendTransactions({ transactions })`             | Batch multiple transactions      |
| `createTransaction({ receiverId, actions, publicKey })` | Create unsigned tx               |
| `createSignedTransaction({ receiverId, actions })`      | Create signed tx without sending |

### Account Management

| Method                                                                          | Description                                        |
| ------------------------------------------------------------------------------- | -------------------------------------------------- |
| `addFullAccessKey(publicKey)`                                                   | Add full access key                                |
| `addFunctionCallAccessKey({ publicKey, contractId, methodNames?, allowance? })` | Add limited key                                    |
| `deleteKey(publicKeyString)`                                                    | Remove access key (takes string)                   |
| `deleteAccount(beneficiaryAccountId)`                                           | Delete account and send NEAR tokens to beneficiary |
| `createAccount({ newAccountId, publicKey, nearToTransfer? })`                   | Create named accounts and sub-accounts for them    |
| `createSubAccount({ accountOrPrefix, publicKey, nearToTransfer? })`             | Create `prefix.parent.near`                        |

### Tokens

| Method                                    | Description         |
| ----------------------------------------- | ------------------- |
| `transfer({ receiverId, amount, token })` | Transfer NEAR or FT |

---

## Provider Methods Reference

### Account Queries

```typescript
// View account
await provider.viewAccount({ accountId, blockQuery? })  // AccountView

// View access key
await provider.viewAccessKey({ accountId, publicKey, finalityQuery? })

// View all access keys
await provider.viewAccessKeyList({ accountId, finalityQuery? })
```

### Contract Queries

```typescript
// Call view method (read-only)
await provider.callFunction<ReturnType>({
  contractId,
  method,
  args,  // JSON object or Uint8Array
  blockQuery?
})

// View contract code
await provider.viewContractCode({ contractId, blockQuery? })

// View contract state (raw key-values)
await provider.viewContractState({ contractId, prefix?, blockQuery? })
```

### Block & Chunk

```typescript
// View block
await provider.viewBlock({ finality: "final" });
await provider.viewBlock({ blockId: 12345 });
await provider.viewBlock({ blockId: "9eVs..." });

// View chunk
await provider.viewChunk({ chunkId: "HFks..." });
await provider.viewChunk({ blockId: 12345, shardId: 0 });
```

### Transaction

```typescript
// Send signed transaction
await provider.sendTransaction(signedTx)

// Send and wait
await provider.sendTransactionAsync({ signedTx, waitUntil: "EXECUTED_OPTIMISTIC" })

// View transaction status
await provider.viewTransactionStatus({ txHash, accountId, waitUntil? })
await provider.viewTransactionStatusWithReceipts({ txHash, accountId })
```

### Network

```typescript
await provider.viewNodeStatus()
await provider.viewGasPrice(blockId?)
await provider.viewValidators({ blockId? } | { epochId? })
await provider.getNetworkId()
```

---

## Action Types

All actions from `near-api-js`:

```typescript
import { actions } from "near-api-js"

// Transfer NEAR
actions.transfer(amount: bigint)

// Function call
actions.functionCall(
  methodName: string,
  args: object | Uint8Array,
  gas: bigint,
  deposit: bigint
)

// Account creation
actions.createAccount()

// Deploy contract
actions.deployContract(code: Uint8Array)

// Key management
actions.addFullAccessKey(publicKey: PublicKey)
actions.addFunctionAccessKey(
  publicKey: PublicKey,
  contractId: string,
  methodNames: string[],
  allowance?: bigint
)
actions.deleteKey(publicKey: PublicKey)

// Account deletion
actions.deleteAccount(beneficiaryId: string)

// Use global contract
actions.useGlobalContract(identifier: { accountId: string } | { codeHash: string | Uint8Array })

// Deploy global contract
actions.deployGlobalContract(code: Uint8Array, deployMode: 'codeHash' | 'accountId')

// Staking
actions.stake(amount: bigint, publicKey: PublicKey)

// Meta transaction
actions.signedDelegate(signedDelegateAction: SignedDelegateAction)
```

---

## Type Definitions

### Key Types

```typescript
type CurveType = "ed25519" | "secp256k1";
type KeyPairString = `${CurveType}:${string}`;
```

### Block Reference

```typescript
type BlockReference =
  | { finality: "final" | "optimistic" }
  | { blockId: number | string } // height or hash
  | { syncCheckpoint: "genesis" | "earliest_available" };
```

### Transaction Status

```typescript
type TxExecutionStatus =
  | "NONE"
  | "INCLUDED"
  | "INCLUDED_FINAL"
  | "EXECUTED"
  | "EXECUTED_OPTIMISTIC"
  | "FINAL";
```

### AccountState

```typescript
interface AccountState {
  balance: {
    total: bigint;
    usedOnStorage: bigint;
    locked: bigint;
    available: bigint;
  };
  storageUsage: number;
  codeHash: string;
}
```

---

## Advanced Patterns

### Manual Transaction Signing

```typescript
import {
  JsonRpcProvider,
  Account,
  KeyPairSigner,
  actions,
  KeyPairString,
} from "near-api-js";
import { NEAR } from "near-api-js/tokens";

const provider = new JsonRpcProvider({ url: "https://test.rpc.fastnear.com" });

// Signer exists separately from Account
const signer = KeyPairSigner.fromSecretKey(privateKey);

// Account without signer — just needs account ID and provider
const account = new Account(accountId, provider);

// 1. Create transaction (requires public key)
const transaction = await account.createTransaction({
  receiverId: "receiver-account.testnet",
  actions: [actions.transfer(NEAR.toUnits("0.1"))],
  publicKey: await signer.getPublicKey(),
});

// 2. Sign transaction
const signResult = await signer.signTransaction(transaction);

// 3. Send transaction
const sendResult = await provider.sendTransaction(signResult.signedTransaction);
```

### Parallel Transactions with MultiKeySigner

```typescript
import {
  Account,
  actions,
  JsonRpcProvider,
  KeyPair,
  MultiKeySigner,
  KeyPairString,
} from "near-api-js";
import { NEAR } from "near-api-js/tokens";

const provider = new JsonRpcProvider({ url: "https://test.rpc.fastnear.com" });
const account = new Account(accountId, provider, privateKey);

// Create 10 keys and add them to the account on-chain
const keys: KeyPair[] = [];
const txActions: ReturnType<typeof actions.addFullAccessKey>[] = [];
for (let j = 0; j < 10; j++) {
  const newKeyPair = KeyPair.fromRandom("ed25519");
  keys.push(newKeyPair);
  txActions.push(actions.addFullAccessKey(newKeyPair.getPublicKey()));
}

await account.signAndSendTransaction({
  receiverId: accountId,
  actions: txActions,
});

// Use MultiKeySigner for parallel transactions
const multiKeySigner = new MultiKeySigner(keys);
const multiAccount = new Account(accountId, provider, multiKeySigner);

// Send 100 transfers in parallel — no nonce collisions
const transfers = [...Array(100)].map(() =>
  multiAccount.transfer({
    token: NEAR,
    amount: NEAR.toUnits("0.001"),
    receiverId: "influencer.testnet",
  }),
);

const results = await Promise.all(transfers);
```

### Access Key Management

```typescript
import {
  Account,
  JsonRpcProvider,
  KeyPair,
  KeyPairString,
  nearToYocto,
} from "near-api-js";
import { NEAR } from "near-api-js/tokens";

const provider = new JsonRpcProvider({ url: "https://test.rpc.fastnear.com" });

// Query keys via provider
const keys = await provider.viewAccessKeyList({ accountId });

// Create Account without signer, add signer later
const account = new Account(accountId, provider, privateKey as KeyPairString);

// Query keys via account
const accessKeys = await account.getAccessKeyList();

// Generate new keys
const fullKeyPair = KeyPair.fromRandom("ed25519");
const fnKeyPair = KeyPair.fromRandom("ed25519");

// Add full access key
await account.addFullAccessKey(fullKeyPair.getPublicKey());

// Add function call access key — takes an OBJECT
await account.addFunctionCallAccessKey({
  publicKey: fnKeyPair.getPublicKey(),
  contractId: "example-contract.testnet",
  methodNames: ["example_method"],
  allowance: nearToYocto("0.25"), // put "0" for unlimited allowance
});

// Switch signer to use new key
account.setSigner(new KeyPairSigner(fullKeyPair));

// Delete keys
await account.deleteKey(fnKeyPair.getPublicKey());
await account.deleteKey(fullKeyPair.getPublicKey());
```

### Wait for Transaction Finality

```typescript
const result = await account.signAndSendTransaction({
  receiverId: "contract.near",
  actions: [...],
  waitUntil: "FINAL", // Wait for transaction to be fully finalized on-chain
})
```

### Error Handling

```typescript
import {
  AccountDoesNotExistActionError,
  // and many more
} from "near-api-js/rpc-errors";

try {
  await account.signAndSendTransaction({
    receiverId: "unexisted_account.testnet",
    actions: [...]
  });
} catch (error) {
  if (error instanceof AccountDoesNotExistActionError) {
    console.error(
      `Transaction ${error.txHash} failed because recipient ${error.accountId} does not exist!`,
    );
  }
}
```

### Manual Error Handling (not recommended)

```typescript

const result = await account.signAndSendTransaction({
    receiverId: "unexisted_account.testnet",
    actions: [...],
    throwOnFailure: false // Don't throw on failure, return result object instead
  });

// do manual error handling on result
console.log(result);
```
