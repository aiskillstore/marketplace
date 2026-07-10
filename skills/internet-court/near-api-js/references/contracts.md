# Contracts

Contract usage with ABI.

## Table of Contents

1. [Contract with ABI](#contract-with-abi)
2. [Contract without ABI](#contract-without-abi)

---

## Contract with ABI

### Basic Usage

```typescript
import {
  nearToYocto,
  Account,
  Contract,
  JsonRpcProvider,
  KeyPairString,
} from "near-api-js";

const provider = new JsonRpcProvider({ url: "https://test.rpc.fastnear.com" });
const account = new Account(accountId, provider, privateKey);

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

### ABI Definition

ABI definitions require `as const` for proper type inference:

```typescript
// This is WRONG, abi won't be inferred
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
              type_schema: { type: "string" },
            },
          ],
        },
      },
      {
        name: "total_messages",
        kind: "view",
        result: {
          serialization_type: "json",
          type_schema: { type: "integer", format: "uint32", minimum: 0.0 },
        },
      },
    ],
    root_schema: {},
  },
};

// This is also WRONG, abi won't be inferred:
import abi from "abi.json" assert { type: "json" };

// This is CORRECT, abi will be properly inferred:
import { AbiRoot } from "near-api-js";

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
              type_schema: { type: "string" },
            },
          ],
        },
      },
      {
        name: "total_messages",
        kind: "view",
        result: {
          serialization_type: "json",
          type_schema: { type: "integer", format: "uint32", minimum: 0.0 },
        },
      },
    ],
    root_schema: {},
  },
} as const satisfies AbiRoot;
```

### View vs Call Methods

```typescript
// View methods: free, read-only, no account needed
const value = await contract.view.get_data();

// Call methods: require account, may require deposit/gas
await contract.call.set_data({
  account: account, // required — who signs the transaction
  args: { key: "value" }, // method arguments
  deposit: nearToYocto("0.1"), // optional — attached deposit
  gas: teraToGas("30"), // optional — gas limit
});
```

---

## Contract without ABI

When no ABI is available, use generics for type safety:

```typescript
import { Contract } from "near-api-js";

const contract = new Contract({
  contractId: "guestbook.near-examples.testnet",
  provider: provider,
});

// View methods — specify return type with generic
const total = await contract.view.total_messages<number>({ args: {} });

// Call methods — specify return type with generic
await contract.call.add_message<void>({
  account: account,
  args: { text: "Hello, NEAR!" },
  deposit: nearToYocto("0.1"),
});
```
