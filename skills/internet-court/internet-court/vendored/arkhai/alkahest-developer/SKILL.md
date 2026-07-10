---
name: alkahest-developer
description: Help developers write code that interacts with Alkahest escrow contracts using the TypeScript, Rust, or Python SDK
---

# Alkahest Developer Skill

## When to Use

Use this skill when a developer wants to write code that interacts with Alkahest escrow contracts. This covers:

- Integrating Alkahest into an application
- Writing bots/agents that create escrows, fulfill obligations, or arbitrate
- Building custom arbiters or obligation contracts
- Understanding SDK patterns and APIs

## SDK Overview

| SDK | Language | Package | Foundation |
|-----|----------|---------|------------|
| TypeScript | TypeScript/JavaScript | `@alkahest/ts-sdk` | viem |
| Rust | Rust | `alkahest-rs` | alloy |
| Python | Python | `alkahest-py` | PyO3 wrapper around Rust SDK |

## Client Setup

### TypeScript

```typescript
import { createWalletClient, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { baseSepolia } from "viem/chains";
import { makeClient } from "@alkahest/ts-sdk";

const walletClient = createWalletClient({
  account: privateKeyToAccount("0xPRIVATE_KEY"),
  chain: baseSepolia,
  transport: http("https://rpc-url"),
});

// Full client with all extensions
const client = makeClient(walletClient);

// Custom addresses (optional)
const client = makeClient(walletClient, customAddresses);

// Minimal client for custom extension patterns
const minimal = makeMinimalClient(walletClient);
const extended = minimal.extend((base) => ({
  custom: makeErc20Client(base.viemClient, pickErc20Addresses(base.contractAddresses)),
}));
```

### Rust

```rust
use alkahest_rs::AlkahestClient;

// Full client with all extensions (Base Sepolia default)
let client = AlkahestClient::with_base_extensions(
    "0xPRIVATE_KEY",
    "https://rpc-url",
    None, // uses Base Sepolia addresses
).await?;

// Custom addresses
use alkahest_rs::{DefaultExtensionConfig, ETHEREUM_SEPOLIA_ADDRESSES};
let client = AlkahestClient::with_base_extensions(
    "0xPRIVATE_KEY",
    "https://rpc-url",
    Some(ETHEREUM_SEPOLIA_ADDRESSES),
).await?;

// Bare client + custom extensions
let bare = AlkahestClient::new("0xPRIVATE_KEY", "https://rpc-url").await?;
let extended = bare.extend::<Erc20Module>(Some(erc20_config)).await?;
```

### Python

```python
from alkahest_py import PyAlkahestClient

# Full client with all extensions (Base Sepolia default)
client = PyAlkahestClient("0xPRIVATE_KEY", "https://rpc-url")

# Custom addresses
from alkahest_py import DefaultExtensionConfig, PyErc20Addresses, ...
config = DefaultExtensionConfig(erc20_addresses=..., ...)
client = PyAlkahestClient("0xPRIVATE_KEY", "https://rpc-url", config)
```

## Core Patterns

### Creating an Escrow

**TypeScript:**
```typescript
// 1. Approve token
await client.erc20.util.approve({ address: TOKEN, value: amount }, "escrow");

// 2. Create escrow
const { hash, attested } = await client.erc20.escrow.default.doObligation(
  client.erc20.escrow.default.encodeObligationRaw({
    token: TOKEN, amount, arbiter: ARBITER, demand: DEMAND_BYTES,
  }),
);
const escrowUid = attested.uid;
```

**Rust:**
```rust
// 1. Approve
client.erc20().approve(&Erc20Data { address: token, value: amount }, ApprovalPurpose::Escrow).await?;

// 2. Create escrow
let receipt = client.erc20().escrow().default().make_statement(
    token, amount, arbiter, demand_bytes, expiration,
).await?;
let attested = client.get_attested_event(receipt)?;
```

**Python:**
```python
# 1. Approve
await client.erc20.util.approve(token_address, amount, "escrow")

# 2. Create escrow
uid = await client.erc20.escrow.default.create(
    token=token_address, amount=amount,
    arbiter=arbiter_address, demand=demand_bytes,
    expiration=expiration,
)
```

### Fulfilling with StringObligation

**TypeScript:**
```typescript
const { attested } = await client.stringObligation.doObligation(
  "fulfillment content",
  undefined,  // schema
  escrowUid,  // refUID
);
```

**Rust:**
```rust
let receipt = client.string_obligation().do_obligation(
    "fulfillment content", None, Some(escrow_uid),
).await?;
```

**Python:**
```python
uid = await client.string_obligation.do_obligation(
    "fulfillment content",
    ref_uid=escrow_uid,
)
```

### Collecting Escrow

**TypeScript:**
```typescript
const { hash } = await client.erc20.escrow.default.collectObligation(
  escrowUid,
  fulfillmentUid,
);
```

**Rust:**
```rust
let receipt = client.erc20().escrow().default().collect_payment(
    escrow_uid, fulfillment_uid,
).await?;
```

**Python:**
```python
tx_hash = await client.erc20.escrow.default.collect(escrow_uid, fulfillment_uid)
```

### Waiting for Fulfillment

**TypeScript:**
```typescript
const result = await client.waitForFulfillment(
  client.contractAddresses.erc20EscrowObligation,
  escrowUid,
);
```

**Rust:**
```rust
let log = client.wait_for_fulfillment(
    client.erc20_address(Erc20Contract::EscrowObligation),
    escrow_uid,
    None, // from_block
).await?;
```

**Python:**
```python
result = await client.wait_for_fulfillment(
    escrow_contract_address,
    escrow_uid,
)
```

### Encoding Demands

**TypeScript:**
```typescript
// Trusted oracle
const demand = client.arbiters.general.trustedOracle.encodeDemand({
  oracle: ORACLE, data: "0x",
});

// Logical composition
const demand = client.arbiters.logical.all.encodeDemand({
  arbiters: [ARBITER_A, ARBITER_B],
  demands: [DEMAND_A, DEMAND_B],
});

// Attestation properties
const demand = client.arbiters.attestationProperties.attester.encodeDemand({
  attester: REQUIRED_ATTESTER,
});
```

**Rust:**
```rust
// Trusted oracle (ABI encoding)
use alloy::sol_types::SolValue;
let demand = TrustedOracleArbiter::DemandData { oracle, data: Bytes::new() }.abi_encode();

// Decode arbiter demand (auto-detects)
let decoded = client.arbiters().decode_arbiter_demand(arbiter_addr, &demand_bytes)?;
```

**Python:**
```python
# Trusted oracle
demand = client.arbiters.trusted_oracle.encode_demand(oracle=ORACLE, data=b"")

# Logical composition
demand = client.arbiters.logical.all.encode(
    arbiters=[ARBITER_A, ARBITER_B],
    demands=[DEMAND_A, DEMAND_B],
)
```

### Commit-Reveal Pattern

**TypeScript:**
```typescript
// 1. Compute commitment
const commitment = await client.commitReveal.computeCommitment(
  escrowUid, claimerAddress, { payload, salt, schema },
);
// 2. Commit (sends bond as ETH)
await client.commitReveal.commit(commitment, bondAmount, commitDeadline);
// 3. Wait 1+ blocks, then reveal. The matching bond is reclaimed on reveal.
await client.commitReveal.doObligation(
  { payload, salt, schema }, escrowUid,
);
```

**Rust:**
```rust
let commitment = client.commit_reveal().compute_commitment(
    escrow_uid, claimer, &obligation_data,
).await?;
client.commit_reveal().commit(commitment, bond_amount, commit_deadline).await?;
// wait 1+ blocks; the matching bond is reclaimed on reveal
let receipt = client.commit_reveal().do_obligation(&obligation_data, Some(escrow_uid)).await?;
```

**Python:**
```python
commitment = await client.commit_reveal.compute_commitment(
    escrow_uid, claimer, payload, salt, schema,
)
await client.commit_reveal.commit(commitment, bond_amount, commit_deadline)
# wait 1+ blocks; the matching bond is reclaimed on reveal
uid = await client.commit_reveal.do_obligation(payload, salt, schema, ref_uid=escrow_uid)
```

## Atomic Payment Utilities

Atomic payment utilities provide single-transaction payment and collection for existing escrows:

**TypeScript:**
```typescript
await client.erc20.payment.payErc20AndCollect(escrowUid);
```

**Rust:**
```rust
client.erc20().payment().pay_erc20_and_collect(escrow_uid).await?;
```

## Key Type Differences

| Concept | TypeScript | Rust | Python |
|---------|-----------|------|--------|
| Addresses | `` `0x${string}` `` | `Address` | `str` (hex) |
| Big integers | `bigint` | `U256` | `str` (decimal) |
| Bytes | `` `0x${string}` `` | `Bytes` / `FixedBytes<32>` | `bytes` / `str` (hex) |
| Receipts | `{ hash, attested }` | `TransactionReceipt` | `str` (tx hash or uid) |
| Attestations | `Attestation` object | `IEAS::Attestation` | `PyAttestation` |

## Reference Documentation

- `references/typescript-api.md` — full TS SDK API tree
- `references/rust-api.md` — full Rust SDK API tree
- `references/python-api.md` — full Python SDK API tree
- `references/contracts.md` — contract addresses and data schemas
- `docs/website/Escrow Flow/Token Trading.mdx` — token trading walkthrough
- `docs/website/Escrow Flow/Job Trading.mdx` — oracle arbitration walkthrough
- `docs/drafts/Escrow Flow (pt 2b - Frontrunning Protection).md` — commit-reveal frontrunning protection
- `docs/website/Escrow Flow/Composing Demands.mdx` — composing demands with logical arbiters
- `docs/website/Writing Arbiters/` — custom arbiter development
- `docs/website/Writing Escrow Contracts.md` and `docs/website/Writing Fulfillment Contracts.md` — custom escrow/obligation development
- `docs/mcp-server/` — MCP server for looking up contract details
