# Alkahest TypeScript SDK API Reference

## Client Construction

```typescript
import { makeClient, makeMinimalClient } from "@alkahest/ts-sdk";
import { createWalletClient, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { baseSepolia } from "viem/chains";

const walletClient = createWalletClient({
  account: privateKeyToAccount("0xKEY"),
  chain: baseSepolia,
  transport: http("https://rpc"),
});

// Full client (all extensions pre-loaded)
const client = makeClient(walletClient);
// With custom addresses:
const client = makeClient(walletClient, customAddresses);

// Minimal client (extend yourself)
const minimal = makeMinimalClient(walletClient);
const extended = minimal.extend((base) => ({
  myErc20: makeErc20Client(base.viemClient, pickErc20Addresses(base.contractAddresses)),
}));
```

## Address Configuration

```typescript
import { contractAddresses, supportedChains } from "@alkahest/ts-sdk";

// Chains: "Base Sepolia", "Sepolia", "Ethereum"
const addresses = contractAddresses["Base Sepolia"];
```

Auto-detected from viem client's chain. Override with second arg to `makeClient`.

## Core Types

```typescript
type Erc20 = { address: `0x${string}`; value: bigint };
type Erc721 = { address: `0x${string}`; id: bigint };
type Erc1155 = { address: `0x${string}`; id: bigint; value: bigint };
type TokenBundle = { nativeAmount?: bigint; erc20s: Erc20[]; erc721s: Erc721[]; erc1155s: Erc1155[] };
type Demand = { arbiter: `0x${string}`; demand: `0x${string}` };
type Attestation = {
  uid: `0x${string}`; schema: `0x${string}`; time: bigint;
  expirationTime: bigint; revocationTime: bigint; refUID: `0x${string}`;
  recipient: `0x${string}`; attester: `0x${string}`; revocable: boolean;
  data: `0x${string}`;
};
```

## Full API Tree

```
client
├── address                           // Connected wallet address
├── contractAddresses                 // All deployed addresses for this chain
├── viemClient                        // Underlying viem client
│
├── getAttestation(uid)               // Fetch EAS attestation
├── getAttestedEventFromTxHash(hash)  // Extract Attested event from tx
├── waitForFulfillment(contract, escrowUid, pollingInterval?)
├── extractObligationData(abi, attestation)
├── getEscrowAttestation(fulfillment)
├── decodeEscrowCondition(escrowAttestation)
├── decodeDemand({ arbiter, demand })
│
├── arbiters
│   ├── general
│   │   ├── intrinsics               // (no methods — use address only)
│   │   └── trustedOracle
│   │       ├── encodeDemand({ oracle, data })
│   │       ├── decodeDemand(bytes)   // => { oracle, data }
│   │       ├── arbitrate(attestation, decision)
│   │       └── arbitrateMany({ mode, pollingInterval, onAfterArbitrate, ... })
│   │
│   ├── logical
│   │   ├── all
│   │   │   ├── encodeDemand({ arbiters[], demands[] })
│   │   │   ├── decodeDemand(bytes)
│   │   │   └── decodeDemandRecursive(bytes, decoders)
│   │   └── any                       // (same API as all)
│   │
│   ├── attestationProperties
│   │   ├── attester     .encodeDemand({ attester }) / .decodeDemand(bytes)
│   │   ├── recipient    .encodeDemand({ recipient }) / .decodeDemand(bytes)
│   │   ├── schema       .encodeDemand({ schema }) / .decodeDemand(bytes)
│   │   ├── uid          .encodeDemand({ uid }) / .decodeDemand(bytes)
│   │   ├── refUid       .encodeDemand({ refUID }) / .decodeDemand(bytes)
│   │   ├── revocable    .encodeDemand({ revocable }) / .decodeDemand(bytes)
│   │   ├── timeAfter    .encodeDemand({ time }) / .decodeDemand(bytes)
│   │   ├── timeBefore   .encodeDemand({ time }) / .decodeDemand(bytes)
│   │   ├── timeEqual    .encodeDemand({ time }) / .decodeDemand(bytes)
│   │   ├── expirationTimeAfter  .encodeDemand({ expirationTime }) / .decodeDemand(bytes)
│   │   ├── expirationTimeBefore .encodeDemand({ expirationTime }) / .decodeDemand(bytes)
│   │   └── expirationTimeEqual  .encodeDemand({ expirationTime }) / .decodeDemand(bytes)
│   │
│   └── confirmation
│       ├── exclusiveRevocable
│       │   ├── confirm(escrow, fulfillment)
│       │   ├── revokeConfirmation(escrow, fulfillment)
│       │   └── isConfirmed(escrow, fulfillment)
│       ├── exclusiveUnrevocable      // confirm, isConfirmed (no revoke)
│       ├── nonexclusiveRevocable     // confirm, revokeConfirmation, isConfirmed
│       └── nonexclusiveUnrevocable   // confirm, isConfirmed
│
├── erc20
│   ├── util
│   │   ├── signPermit(props)
│   │   ├── getPermitSignature(spender, token, deadline)
│   │   └── getPermitDeadline()
│   ├── escrow
│   │   ├── default
│   │   │   ├── address
│   │   │   ├── getSchema()
│   │   │   ├── encodeObligation(token: Erc20, demand: Demand)
│   │   │   ├── encodeObligationRaw({ token, amount, arbiter, demand })
│   │   │   ├── decodeObligation(bytes)    // => { token, amount, arbiter, demand }
│   │   │   ├── getObligation(uid)
│   │   │   ├── doObligation(encodedData, refUID?)
│   │   │   ├── collectObligation(escrowUid, fulfillmentUid)
│   │   │   └── arbitrate(escrowUid, fulfillmentUid, decision)
│   │   └── unconditional                  // (no default fulfillment checks)
│   ├── payment
│   │   ├── address
│   │   ├── getSchema()
│   │   ├── encodeObligation(token: Erc20, payee)
│   │   ├── encodeObligationRaw({ token, amount, payee })
│   │   ├── decodeObligation(bytes)        // => { token, amount, payee }
│   │   ├── getObligation(uid)
│   │   ├── doObligation(encodedData, refUID?)
│   │   ├── payErc20AndCollect(escrowUid)
│   │   └── permitAndPayErc20AndCollect(escrowUid)
│
├── erc721                                 // Same structure as erc20
│   ├── util (.approve)
│   ├── escrow.default / .unconditional
│   └── payment                            // includes payErc721AndCollect
│
├── erc1155                                // Same structure
│   ├── util (.approveAll)
│   ├── escrow.default / .unconditional
│   └── payment                            // includes payErc1155AndCollect
│
├── nativeToken                            // No util (no approvals needed)
│   ├── escrow.default / .unconditional
│   └── payment                            // includes payNativeAndCollect
│
├── bundle
│   ├── util (.approve)
│   ├── escrow.default / .unconditional
│   └── payment                            // includes payBundleAndCollect
│
├── attestation
│   ├── util
│   └── escrow.default / .reference
│
├── stringObligation
│   ├── address
│   ├── encode({ item, schema })
│   ├── decode(bytes)                      // => { item, schema }
│   ├── decodeJson(bytes)                  // => parsed JSON
│   ├── decodeZod(bytes, zodSchema)
│   ├── decodeArkType(bytes, arkTypeSchema)
│   ├── doObligation(item, schema?, refUID?)
│   ├── doObligationJson(item, schema?, refUID?)
│   ├── getSchema()
│   ├── getObligation(uid)
│   └── getJsonObligation(uid)
│
└── commitReveal
    ├── address
    ├── encode({ payload, salt, schema })
    ├── decode(bytes)                      // => { payload, salt, schema }
    ├── doObligation(data, refUID?)
    ├── doObligationFor(data, recipient, refUID?)
    ├── doObligationRaw(data, expirationTime?, refUID?, value?)
    ├── revealAndCollect(data, recipient, escrowContract, escrowUid)
    ├── commit(commitment, bondAmount, commitDeadline)
    ├── computeCommitment(refUID, claimer, data)
    ├── slashBond(commitment)
    ├── getSlashedBondRecipient()
    ├── getCommitment(commitment)
    ├── isCommitmentClaimed(commitment)
    ├── getSchema()
    └── getObligation(uid)
```

## Static Encode/Decode Exports

For use without a client instance:

```typescript
import {
  encodeAttesterDemand, decodeAttesterDemand,
  encodeRecipientDemand, decodeRecipientDemand,
  encodeTrustedOracleDemand, decodeTrustedOracleDemand,
  encodeIntrinsics2Demand, decodeIntrinsics2Demand,
  // ... all attestation property arbiters
} from "@alkahest/ts-sdk";
```

## Permit vs Approve

ERC20 tokens supporting EIP-2612 can use gasless approvals:

```typescript
// Standard approve (separate transaction)
await client.erc20.util.approve({ address: TOKEN, value: amount }, "escrow");

// Permit (signature-based, no separate tx)
const permit = await client.erc20.util.getPermitSignature(
  spenderAddress, TOKEN, deadline,
);
// Pass permit to atomic payment helpers that accept it
```

Atomic payment helpers have `permitAnd*` variants that accept permit signatures.

## Return Types

Most write methods return `{ hash: `0x${string}`, attested?: { uid, schema, ... } }`.

- `hash` — transaction hash
- `attested` — present when the transaction creates an EAS attestation (escrows, payments, obligations)

Read methods return typed data directly.
