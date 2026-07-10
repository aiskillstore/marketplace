# Alkahest Rust SDK API Reference

## Client Construction

```rust
use alkahest_rs::AlkahestClient;

// Full client with all extensions (Base Sepolia default)
let client = AlkahestClient::with_base_extensions(
    "0xPRIVATE_KEY",
    "https://rpc-url",
    None, // uses BASE_SEPOLIA_ADDRESSES
).await?;

// With specific chain addresses
use alkahest_rs::{ETHEREUM_SEPOLIA_ADDRESSES, ETHEREUM_ADDRESSES};
let client = AlkahestClient::with_base_extensions(
    "0xPRIVATE_KEY",
    "https://rpc-url",
    Some(ETHEREUM_SEPOLIA_ADDRESSES),
).await?;

// Bare client (no extensions)
let bare = AlkahestClient::new("0xPRIVATE_KEY", "https://rpc-url").await?;

// Add extensions individually
let extended = bare.extend::<Erc20Module>(Some(erc20_config)).await?;
let more = extended.extend_default::<ArbitersModule>().await?;
```

**Type alias:** `DefaultAlkahestClient = AlkahestClient<BaseExtensions>`

## Extension Access

```rust
client.erc20()               // -> &Erc20Module
client.erc721()              // -> &Erc721Module
client.erc1155()             // -> &Erc1155Module
client.native_token()        // -> &NativeTokenModule
client.token_bundle()        // -> &TokenBundleModule
client.attestation()         // -> &AttestationModule
client.string_obligation()   // -> &StringObligationModule
client.commit_reveal()       // -> &CommitRevealObligationModule
client.arbiters()            // -> &ArbitersModule
client.oracle()              // -> &OracleModule (alias for TrustedOracle)
```

Extension access uses trait bounds: e.g., `client.erc20()` requires `Extensions: HasErc20`.

## Full API Tree

```
client
├── get_attested_event(receipt) -> Log<Attested>
├── wait_for_fulfillment(contract, buy_uid, from_block) -> Log<EscrowClaimed>
├── extract_obligation_data::<T: SolType>(attestation) -> T
├── extract_demand_data::<T: SolType>(attestation) -> T
├── get_escrow_attestation(fulfillment) -> Attestation
├── get_escrow_and_demand::<T: SolType>(fulfillment) -> (Attestation, T)
│
├── erc20()
│   ├── approve(&token, purpose) -> Receipt
│   ├── approve_if_less(&token, purpose) -> Option<Receipt>
│   ├── escrow()
│   │   ├── default()
│   │   │   ├── make_statement(token, amount, arbiter, demand, expiration) -> Receipt
│   │   │   ├── collect_payment(escrow_uid, fulfillment_uid) -> Receipt
│   │   │   ├── get_statement(uid) -> DecodedAttestation<ObligationData>
│   │   │   └── decode_statement(bytes) -> ObligationData
│   │   └── unconditional()              // (no default fulfillment checks)
│   ├── payment()
│   │   ├── make_statement(token, amount, payee, expiration, ref_uid) -> Receipt
│   │   ├── get_statement(uid) -> DecodedAttestation<ObligationData>
│   │   ├── decode_statement(bytes) -> ObligationData
│   │   ├── pay_erc20_and_collect(escrow_uid) -> Receipt
│   │   └── permit_and_pay_erc20_and_collect(escrow_uid) -> Receipt
│   └── util()
│       └── permit-related helpers
│
├── erc721()                         // Same structure as erc20
│   ├── approve(&token, purpose)
│   ├── escrow().default() / .unconditional()
│   └── payment()
│
├── erc1155()
│   ├── approve_all(token_address, purpose)
│   ├── escrow().default() / .unconditional()
│   └── payment()
│
├── native_token()                   // No approval needed
│   ├── escrow().default() / .unconditional()
│   └── payment()
│
├── token_bundle()
│   ├── approve(&bundle, purpose)
│   ├── escrow().default() / .unconditional()
│   └── payment()
│
├── attestation()
│   ├── escrow().default() / .reference()
│   └── util()
│
├── string_obligation()
│   ├── do_obligation(item, schema, ref_uid) -> Receipt
│   ├── do_obligation_json(data, schema, ref_uid) -> Receipt
│   ├── get_obligation(uid) -> DecodedAttestation<ObligationData>
│   ├── decode(bytes) -> ObligationData
│   ├── decode_json::<T>(bytes) -> T
│   └── encode(&data) -> Bytes
│
├── commit_reveal()
│   ├── do_obligation(&data, ref_uid) -> Receipt
│   ├── do_obligation_for(&data, recipient, ref_uid) -> Receipt
│   ├── do_obligation_raw(data, expiration_time, ref_uid, value) -> Receipt
│   ├── reveal_and_collect(&data, recipient, escrow_contract, escrow_uid) -> Receipt
│   ├── commit(commitment, bond_amount, commit_deadline) -> Receipt
│   ├── compute_commitment(ref_uid, claimer, &data) -> FixedBytes<32>
│   ├── slash_bond(commitment) -> Receipt
│   ├── get_obligation(uid) -> DecodedAttestation<ObligationData>
│   ├── decode(bytes) -> ObligationData
│   └── encode(&data) -> Bytes
│
├── arbiters()
│   ├── trusted_oracle()
│   │   ├── arbitrate(obligation, demand, decision) -> Receipt
│   │   └── request_arbitration(obligation, oracle, demand) -> Receipt
│   ├── logical()
│   │   ├── decode_all_demand(bytes) -> (Vec<Address>, Vec<Bytes>)
│   │   └── decode_any_demand(bytes) -> (Vec<Address>, Vec<Bytes>)
│   ├── attestation_properties()
│   │   ├── decode_attester_demand(bytes) -> Address
│   │   ├── decode_recipient_demand(bytes) -> Address
│   │   ├── decode_schema_demand(bytes) -> FixedBytes<32>
│   │   ├── decode_uid_demand(bytes) -> FixedBytes<32>
│   │   ├── decode_ref_uid_demand(bytes) -> FixedBytes<32>
│   │   ├── decode_revocable_demand(bytes) -> bool
│   │   ├── decode_time_after_demand(bytes) -> u64
│   │   ├── decode_time_before_demand(bytes) -> u64
│   │   └── ... (all property arbiters)
│   └── decode_arbiter_demand(arbiter_addr, &bytes) -> DecodedDemand
│
└── oracle()                         // Alias for trusted_oracle
    ├── arbitrate(obligation, demand, decision) -> Receipt
    └── request_arbitration(obligation, oracle, demand) -> Receipt
```

## Address Helpers

```rust
client.erc20_address(Erc20Contract::EscrowObligation)     // -> Address
client.erc20_address(Erc20Contract::PaymentObligation)
client.erc20_address(Erc20Contract::AtomicPaymentUtils)
client.erc721_address(Erc721Contract::EscrowObligation)
// ... same pattern for all modules
client.arbiters_address(ArbitersContract::TrustedOracleArbiter)
client.arbiters_address(ArbitersContract::AllArbiter)
client.commit_reveal_obligation_address(CommitRevealObligationContract::Obligation)
```

## Key Types

```rust
// Token data
struct Erc20Data { address: Address, value: U256 }
struct Erc721Data { address: Address, id: U256 }
struct Erc1155Data { address: Address, id: U256, value: U256 }
struct NativeTokenData { value: U256 }
struct TokenBundleData { erc20s: Vec<Erc20Data>, erc721s: Vec<Erc721Data>, erc1155s: Vec<Erc1155Data>, native_amount: U256 }

// Demand
struct ArbiterData { arbiter: Address, demand: Bytes }

// Decoded attestation
struct DecodedAttestation<T> { attestation: IEAS::Attestation, data: T }

// Approval
enum ApprovalPurpose { Escrow, Payment, AtomicPayment }
```

## Important Patterns

### Single-return-value calls

Alloy returns primitives directly for single-return contract calls:

```rust
// Returns U256, not a struct
let balance: U256 = contract.balanceOf(addr).call().await?;

// Returns bool directly
let is_claimed: bool = contract.isCommitmentClaimed(commitment).call().await?;
```

Only multi-return functions return structs with named fields.

### Getting attestation UID from receipt

```rust
let receipt = client.erc20().escrow().default().make_statement(...).await?;
let attested_event = client.get_attested_event(receipt)?;
let uid = attested_event.inner.uid;
```

### ABI encoding demands

Use alloy's `SolValue` trait:

```rust
use alloy::sol_types::SolValue;

// Encode TrustedOracle demand
let demand = TrustedOracleArbiter::DemandData {
    oracle: oracle_address,
    data: Bytes::new(),
}.abi_encode();

// Encode AllArbiter demand
let demand = AllArbiter::DemandData {
    arbiters: vec![arbiter_a, arbiter_b],
    demands: vec![demand_a.into(), demand_b.into()],
}.abi_encode();
```

## Predefined Address Configs

```rust
use alkahest_rs::{
    BASE_SEPOLIA_ADDRESSES,           // Default
    ETHEREUM_SEPOLIA_ADDRESSES,
    ETHEREUM_ADDRESSES,
};
```
