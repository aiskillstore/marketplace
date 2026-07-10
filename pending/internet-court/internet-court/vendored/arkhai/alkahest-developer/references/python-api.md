# Alkahest Python SDK API Reference

> Status: this reference still describes the legacy Python SDK surface. The TypeScript and Rust SDKs have been updated to the current `default`/`unconditional` escrow split and `AtomicPaymentUtils` payment-client settlement helpers; the Python SDK/docs need the same follow-up before this page should be treated as current.

The Python SDK is a PyO3 wrapper around the Rust SDK. It exposes the same functionality with Python-idiomatic naming and types.

## Client Construction

```python
from alkahest_py import PyAlkahestClient

# Full client with all extensions (Base Sepolia default)
client = PyAlkahestClient("0xPRIVATE_KEY", "https://rpc-url")

# With custom addresses
from alkahest_py import (
    DefaultExtensionConfig,
    PyErc20Addresses, PyErc721Addresses, PyErc1155Addresses,
    PyNativeTokenAddresses, PyTokenBundleAddresses, PyAttestationAddresses,
    PyArbitersAddresses, PyStringObligationAddresses, PyCommitRevealObligationAddresses,
)

config = DefaultExtensionConfig(
    erc20_addresses=PyErc20Addresses(eas="0x...", atomic_payment_utils="0x...", ...),
    # ... other address configs
)
client = PyAlkahestClient("0xPRIVATE_KEY", "https://rpc-url", config)
```

## API Access Pattern

The Python SDK uses nested property accessors:

```python
client.<extension>.<category>.<subcategory>.<method>()
```

All async methods use Python's `await` syntax.

## Full API Tree

```
client
├── list_extensions() -> List[str]
├── has_extension(extension_type: str) -> bool
├── extract_obligation_data(attestation) -> str
├── get_escrow_attestation(fulfillment) -> PyOracleAttestation
├── extract_demand_data(escrow_attestation) -> PyTrustedOracleArbiterDemandData
├── get_escrow_and_demand(fulfillment) -> tuple
├── wait_for_fulfillment(contract_address, buy_attestation, from_block?) -> EscowClaimedLog
│
├── erc20
│   ├── util
│   │   └── approve(token_address, amount, purpose)
│   ├── escrow
│   │   ├── default
│   │   │   ├── create(token, amount, arbiter, demand, expiration) -> str (uid)
│   │   │   ├── collect(escrow_uid, fulfillment_uid) -> str (tx_hash)
│   │   │   └── get(uid) -> PyDecodedAttestation
│   │   └── unconditional
│   ├── payment
│   │   ├── pay(token, amount, payee, ...) -> str (uid)
│   │   ├── approve_and_pay(token, amount, payee, ...) -> str (uid)
│   │   └── get(uid) -> PyDecodedAttestation
│   └── barter
│       ├── pay_erc20_and_collect(escrow_uid)
│       ├── permit_and_pay_erc20_and_collect(escrow_uid)
│       ├── pay_erc20_and_collect(escrow_uid)
│       └── ... (other cross-token settlement combinations)
│
├── erc721                            # Same structure as erc20
│   ├── util (.approve)
│   ├── escrow.default / .unconditional
│   ├── payment
│   └── barter
│
├── erc1155                           # Same structure
│   ├── util (.approve_all)
│   ├── escrow.default / .unconditional
│   ├── payment
│   └── barter
│
├── native_token                      # No util
│   ├── escrow.default / .unconditional
│   ├── payment
│   └── barter
│
├── token_bundle
│   ├── util (.approve)
│   ├── escrow.default / .unconditional
│   ├── payment
│   └── barter
│
├── attestation
│   ├── escrow.v1.default / .unconditional
│   ├── escrow.v2.default / .unconditional
│   └── util
│       ├── get_attestation(uid) -> PyAttestation
│       ├── register_schema(schema, resolver, revocable) -> str
│       └── attest(schema, data, ...) -> str (uid)
│
├── string_obligation
│   ├── do_obligation(item, ref_uid?, schema?) -> str (uid)
│   └── get_obligation(uid) -> PyDecodedAttestation[PyStringObligationData]
│
├── commit_reveal
│   ├── do_obligation(payload, salt, schema, ref_uid?) -> str (uid)
│   ├── commit(commitment, bond_amount, commit_deadline) -> str (tx_hash)
│   ├── compute_commitment(ref_uid, claimer, payload, salt, schema) -> str
│   ├── slash_bond(commitment) -> str (tx_hash)
│   ├── slashed_bond_recipient() -> str (address)
│   ├── get_commitment(commitment) -> tuple(u64, u64, str, str, str)
│   ├── is_commitment_claimed(commitment) -> bool
│   └── get_obligation(uid) -> PyDecodedAttestation[PyCommitRevealObligationData]
│
└── arbiters
    ├── trusted_oracle
    │   ├── get_eas_address() -> str
    │   ├── get_trusted_oracle_arbiter_address() -> str
    │   ├── request_arbitration(obligation_uid, oracle, demand) -> str (tx_hash)
    │   ├── extract_obligation_data(attestation) -> str
    │   ├── extract_demand_data(escrow_attestation) -> PyTrustedOracleArbiterDemandData
    │   ├── arbitrate(obligation, demand, decision) -> str (tx_hash)
    │   └── wait_for_arbitration(obligation, demand?, oracle?, from_block?) -> PyArbitrationMadeLog
    │
    ├── logical
    │   ├── all
    │   │   ├── address() -> str
    │   │   ├── encode(arbiters: list, demands: list) -> bytes
    │   │   └── decode(demand_bytes) -> tuple(list, list)
    │   └── any                        # Same API as all
    │
    ├── confirmation
    │   ├── exclusive_revocable
    │   │   ├── confirm(escrow, fulfillment)
    │   │   ├── revoke(escrow, fulfillment)
    │   │   └── is_confirmed(escrow, fulfillment) -> bool
    │   ├── exclusive_unrevocable
    │   ├── nonexclusive_revocable
    │   └── nonexclusive_unrevocable
    │   └── address(arbiter_type) -> str
    │
    ├── attestation_properties
    │   ├── attester                   # .address(), .encode(attester), .decode(bytes)
    │   ├── recipient
    │   ├── schema
    │   ├── uid
    │   ├── ref_uid
    │   ├── revocable
    │   ├── time_after
    │   ├── time_before
    │   ├── time_equal
    │   ├── expiration_time_after
    │   ├── expiration_time_before
    │   └── expiration_time_equal
    │
    ├── eas_address() -> str
    ├── trivial_arbiter_address() -> str
    ├── trusted_oracle_arbiter_address() -> str
    ├── intrinsics_arbiter_address() -> str
    ├── erc8004_arbiter_address() -> str
    ├── any_arbiter_address() -> str
    ├── all_arbiter_address() -> str
    └── confirmation_arbiter_address(arbiter_type) -> str
```

## Key Type Differences from Rust/TypeScript

| Concept | Python type | Notes |
|---------|------------|-------|
| Addresses | `str` | Hex with `0x` prefix |
| U256 / big integers | `str` | Decimal string representation |
| Bytes | `bytes` or `str` | Hex strings for hashes, raw bytes for payloads |
| Transaction receipts | `str` | Returns tx hash as hex string |
| Attestation UIDs | `str` | Returned directly from write methods |
| Boolean | `bool` | Standard Python bool |

## Data Type Classes

### Obligation data (with static encode/decode)

```python
from alkahest_py import (
    PyERC20EscrowObligationData,      # token, amount, arbiter, demand
    PyERC20PaymentObligationData,     # token, amount, payee
    PyERC721EscrowObligationData,     # token, token_id, arbiter, demand
    PyERC721PaymentObligationData,    # token, token_id, payee
    PyERC1155EscrowObligationData,    # token, token_id, amount, arbiter, demand
    PyERC1155PaymentObligationData,   # token, token_id, amount, payee
    PyStringObligationData,           # item
    PyCommitRevealObligationData,     # payload, salt, schema
)

# Static encode/decode
encoded = PyCommitRevealObligationData.encode(obligation_data)
decoded = PyCommitRevealObligationData.decode(encoded_bytes)
```

### Arbiter demand data

```python
from alkahest_py import (
    PyTrustedOracleArbiterDemandData,
    ERC8004ArbiterDemandData,         # validation_registry, validator_address, min_response
    AttesterArbiterDemandData,
    RecipientArbiterDemandData,
    # ... all property arbiter demand data types
)
```

### Attestation types

```python
from alkahest_py import PyAttestation

attestation.uid           # str
attestation.schema        # str
attestation.time          # int
attestation.expiration_time  # int
attestation.revocation_time  # int
attestation.ref_uid       # str
attestation.recipient     # str
attestation.attester      # str
attestation.revocable     # bool
attestation.data          # str (hex)

attestation.is_expired()  # bool
attestation.is_revoked()  # bool
attestation.is_valid()    # bool
```

### Event log types

```python
from alkahest_py import (
    PyArbitrationMadeLog,        # decision_key, obligation, oracle, decision
    PyConfirmationMadeLog,
    PyConfirmationRequestedLog,
    AttestedLog,                 # recipient, attester, uid, schema_uid
    EscowClaimedLog,             # payment, fulfillment, fulfiller
)
```

## Async Usage

All write operations and most reads are async:

```python
import asyncio

async def main():
    client = PyAlkahestClient("0xKEY", "https://rpc")
    uid = await client.string_obligation.do_obligation("hello", ref_uid=escrow_uid)
    attestation = await client.string_obligation.get_obligation(uid)
    print(attestation.data.item)

asyncio.run(main())
```

## Test Utilities

```python
from alkahest_py import EnvTestManager, PyMockERC20, PyMockERC721, PyMockERC1155

manager = EnvTestManager()
# Properties: rpc_url, god, alice, bob, alice_private_key, bob_private_key, addresses
```
