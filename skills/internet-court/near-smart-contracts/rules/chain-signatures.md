# Chain Signatures

Use Chain Signatures to control accounts on other blockchains (Bitcoin, Ethereum, Solana, Cosmos, XRP, Aptos, Sui, and any ECDSA/EdDSA chain) from NEAR smart contracts.

## Why It Matters

Chain Signatures enable NEAR accounts and smart contracts to:

- Sign transactions for any blockchain supporting ECDSA or EdDSA
- Control foreign blockchain accounts without bridges
- Build multichain DeFi applications
- Create unified account abstraction across all chains

The MPC (Multi-Party Computation) service signs transactions without any single party controlling the private key. The MPC network is composed of 8 independent nodes that jointly produce signatures.

## ❌ Incorrect

```rust
// DON'T: Try to store private keys in contract
#[near(contract_state)]
pub struct Contract {
    // NEVER store private keys on-chain!
    eth_private_key: String,  // CRITICAL SECURITY ISSUE
}

// DON'T: Assume synchronous signature generation
pub fn sign_eth_tx(&self, payload: Vec<u8>) -> Vec<u8> {
    // MPC signing is async - this won't work
    self.call_mpc_and_return_immediately(payload)
}

// DON'T: Send args without the "request" wrapper
let args = json!({
    "path": path,
    "payload_v2": payload_v2,
    "domain_id": 0
}).to_string().into_bytes();
// The MPC contract expects args wrapped in a "request" key
```

**Problems:**

- Private keys on-chain are visible to everyone
- MPC signing requires async pattern (yield/resume or callbacks)
- Insufficient gas allocation causes failures
- Missing `"request"` wrapper causes the MPC call to fail

## ✅ Correct

```rust
use near_sdk::{near, env, require, AccountId, Promise, Gas, NearToken, PromiseError};
use near_sdk::serde_json::{json, Value};

const MPC_GAS: Gas = Gas::from_tgas(250);  // MPC needs significant gas

#[near(contract_state)]
pub struct Contract {
    mpc_contract: AccountId,
}

impl Default for Contract {
    fn default() -> Self {
        Self {
            mpc_contract: "v1.signer-prod.testnet".parse().unwrap(),
        }
    }
}

#[near]
impl Contract {
    #[init]
    pub fn new(mpc_contract: AccountId) -> Self {
        Self { mpc_contract }
    }

    /// Request MPC signature for a transaction payload.
    /// `payload_hex`: hex-encoded hash to sign (64 hex chars for ECDSA, 64-2464 for EdDSA)
    /// `path`: derivation path (e.g., "ethereum-1", "bitcoin-main")
    /// `domain_id`: 0 = Secp256k1 (Bitcoin, Ethereum), 1 = Ed25519 (Solana, NEAR)
    #[payable]
    pub fn sign_transaction(
        &mut self,
        payload_hex: String,
        path: String,
        domain_id: u64,
    ) -> Promise {
        require!(
            env::attached_deposit() >= NearToken::from_yoctonear(1),
            "Requires at least 1 yoctoNEAR deposit"
        );

        // Build the payload variant based on domain_id
        let payload_v2 = match domain_id {
            0 => json!({ "Ecdsa": payload_hex }),
            1 => json!({ "Eddsa": payload_hex }),
            _ => env::panic_str("Unsupported domain_id: use 0 (Secp256k1) or 1 (Ed25519)"),
        };

        // Args must be wrapped in a "request" key (near-sdk deserializes by parameter name)
        let args = json!({
            "request": {
                "path": path,
                "payload_v2": payload_v2,
                "domain_id": domain_id
            }
        }).to_string().into_bytes();

        Promise::new(self.mpc_contract.clone())
            .function_call(
                "sign".to_string(),
                args,
                NearToken::from_yoctonear(1),
                MPC_GAS,
            )
            .then(
                Self::ext(env::current_account_id())
                    .with_static_gas(Gas::from_tgas(20))
                    .on_signature_received()
            )
    }

    #[private]
    pub fn on_signature_received(
        &self,
        #[callback_result] result: Result<Value, PromiseError>,
    ) -> Option<Value> {
        match result {
            Ok(signature) => {
                env::log_str(&format!("MPC signature received: {}", signature));
                // The response is a SignatureResponse enum (see structs below).
                // Parse according to the domain: Secp256k1 or Ed25519.
                Some(signature)
            }
            Err(_) => {
                env::log_str("MPC signature request failed - check gas, deposit, and payload format");
                None
            }
        }
    }
}
```

### Signature Response Types

The MPC contract returns a tagged enum. Parse according to the domain used:

```rust
use near_sdk::near;

/// ECDSA response (domain_id = 0, for Bitcoin/Ethereum/EVM chains)
#[near(serializers = [json])]
pub struct Secp256k1Signature {
    pub big_r: String,  // hex-encoded compressed point (remove "04" prefix for r)
    pub s: String,      // hex-encoded 32-byte scalar
    pub recovery_id: u8,
}

/// EdDSA response (domain_id = 1, for Solana/NEAR/Aptos/SUI)
#[near(serializers = [json])]
pub struct Ed25519Signature {
    pub signature: Vec<u8>,  // 64-byte Ed25519 signature
}

/// The full response is an enum:
/// { "Secp256k1": { "big_r": "04...", "s": "...", "recovery_id": 0 } }
/// or
/// { "Ed25519": { "signature": [/* 64 bytes */] } }
```

**Benefits:**

- No private keys stored on-chain
- Decentralized MPC signing
- Works with any blockchain supporting ECDSA or EdDSA

## Building Multichain Transactions

Use `omni-transaction-rs` to build transactions for different chains inside NEAR smart contracts:

```toml
# In Cargo.toml:
[dependencies]
omni-transaction = "0.4"
```

### EVM Transaction (Ethereum, Base, Polygon, etc.)

```rust
use omni_transaction::evm::EVMTransaction;
use omni_transaction::evm::utils::parse_eth_address;
use omni_transaction::TransactionBuilder;
use omni_transaction::EVM;

// Build an unsigned EIP-1559 transaction
let evm_tx: EVMTransaction = TransactionBuilder::new::<EVM>()
    .chain_id(1)        // Ethereum mainnet (use 11155111 for Sepolia)
    .nonce(0)
    .to(parse_eth_address("d8dA6BF26964aF9D7eEd9e03E53415D37aA96045"))
    .value(10_000_000_000_000_000u128) // 0.01 ETH in wei
    .input(vec![])      // empty for simple transfer, or ABI-encoded calldata
    .gas_limit(21_000)
    .max_fee_per_gas(20_000_000_000)
    .max_priority_fee_per_gas(1_000_000_000)
    .build();

// Get the signing payload (Keccak-256 hash this, then send to MPC)
let payload: Vec<u8> = evm_tx.build_for_signing();
```

### Bitcoin Transaction

```rust
use omni_transaction::bitcoin::types::{
    Amount, EcdsaSighashType, Hash, LockTime, OutPoint, ScriptBuf,
    Sequence, TxIn, TxOut, Txid, Version, Witness,
};
use omni_transaction::bitcoin::BitcoinTransaction;
use omni_transaction::TransactionBuilder;
use omni_transaction::BITCOIN;

let tx_in = TxIn {
    previous_output: OutPoint::new(
        Txid(Hash::from_hex("abcdef1234...").unwrap()),
        0, // vout
    ),
    script_sig: ScriptBuf::default(),
    sequence: Sequence::MAX,
    witness: Witness::new(),
};

let tx_out = TxOut {
    value: Amount::from_sat(50_000),
    script_pubkey: ScriptBuf::from_hex("0014<20-byte-witness-program>").unwrap(),
};

let mut btc_tx: BitcoinTransaction = TransactionBuilder::new::<BITCOIN>()
    .version(Version::Two)
    .lock_time(LockTime::from_height(0).unwrap())
    .inputs(vec![tx_in])
    .outputs(vec![tx_out])
    .build();

// For legacy (P2PKH): btc_tx.build_for_signing_legacy(EcdsaSighashType::All)
// For SegWit (P2WPKH): btc_tx.build_for_signing_segwit(EcdsaSighashType::All, input_index, &script_code, utxo_value)
// Double-SHA256 hash the result, then send to MPC
```

## Formatting the Signature and Relaying

After receiving the MPC signature, you must format it and attach it to the transaction. This is typically done **off-chain** (in your dApp frontend/backend):

### EVM: Attach Signature and Broadcast

```rust
use omni_transaction::evm::types::Signature;

// Parse the MPC response (Secp256k1 variant)
// big_r -> r bytes (hex string, remove "04" prefix, take first 32 bytes)
// s -> s bytes (hex string)
// recovery_id -> v
let signature = Signature {
    v: recovery_id as u64,
    r: r_bytes.to_vec(),
    s: s_bytes.to_vec(),
};

// Build signed transaction (RLP-encoded, ready for broadcast)
let signed_tx: Vec<u8> = evm_tx.build_with_signature(&signature);
// Broadcast via eth_sendRawTransaction
```

### Bitcoin: Attach Signature and Broadcast

```rust
use omni_transaction::bitcoin::types::{ScriptBuf, TransactionType};

// For SegWit (P2WPKH):
let signed_tx = btc_tx.build_with_witness(
    0, // input_index
    vec![signature_bytes.to_vec(), public_key_bytes.to_vec()],
    TransactionType::P2WPKH,
);
// Broadcast via Bitcoin RPC sendrawtransaction
```

**Note:** `btc_tx` must be declared as mutable (`let mut btc_tx`) since `build_with_witness` takes `&mut self`.

## Deriving Foreign Addresses

Address derivation is typically done **off-chain** by calling the `derived_public_key` view method on the MPC signer contract, then computing the target chain address from the derived public key.

```bash
# Call the MPC contract to get a derived public key
near contract call-function as-read-only v1.signer-prod.testnet derived_public_key \
  json-args '{"predecessor": "your-account.testnet", "path": "ethereum-1", "key_version": 0}' \
  network-config testnet now

# Different paths = different addresses on the same chain
# "ethereum-1" -> 0x1234...
# "ethereum-2" -> 0x5678...
# "bitcoin-main" -> bc1q...

# Same NEAR account + same path always derives the same public key
```

Contracts can also derive addresses via a cross-contract call to `derived_public_key` if needed (e.g., for autonomous agents or Shade Agents).

## JavaScript/TypeScript: Using chainsig.js

For off-chain operations (steps 1, 2, 4, 5), the `chainsig.js` library provides a unified interface across all supported chains:

```bash
npm install chainsig.js
```

```typescript
import { chainAdapters, contracts } from "chainsig.js";
import { KeyPair, type KeyPairString } from "@near-js/crypto";
import { createPublicClient, http } from "viem";
import { mainnet } from "viem/chains";

// Initialize NEAR connection with credentials from environment
const accountId = process.env.NEAR_ACCOUNT_ID;
const privateKey = process.env.NEAR_PRIVATE_KEY as KeyPairString;

if (!accountId || !privateKey) {
  throw new Error(
    "NEAR_ACCOUNT_ID and NEAR_PRIVATE_KEY must be set in environment",
  );
}

const keypair = KeyPair.fromString(privateKey);

const contract = new contracts.near.ChainSignatureContract({
  networkId: "testnet",
  contractId: "v1.signer-prod.testnet",
  accountId,
  keypair,
});

const publicClient = createPublicClient({
  chain: mainnet,
  transport: http(),
});

const evmChain = new chainAdapters.evm.EVM({
  publicClient,
  contract,
});

// Derive address and public key
const { address, publicKey } = await evmChain.deriveAddressAndPublicKey(
  accountId,
  "any_string",
);

// Check balance
const { balance, decimals } = await evmChain.getBalance(address);

// Create and sign transaction
const { transaction, hashesToSign } =
  await evmChain.prepareTransactionForSigning({
    from: "0x...",
    to: "0x...",
    value: 1n,
  });

// Sign with MPC
const signature = await contract.sign({
  payload: hashesToSign[0].payload,
  path: "any_string",
  key_version: 0,
});

// Add signature
const signedTx = evmChain.finalizeTransactionSigning({
  transaction,
  rsvSignatures: [signature],
});

// Broadcast transaction
const txHash = await evmChain.broadcastTx(signedTx);
```

Available chain adapters: `evm.EVM`, `bitcoin.Bitcoin`, `solana.Solana`, `cosmos.Cosmos`, `xrp.XRP`, `aptos.Aptos`, `sui.SUI`.

## Additional Considerations

- Allocate at least 250 TGas for MPC calls
- The MPC service uses yield/resume internally; signatures take ~2-3 seconds
- Same NEAR account + path = same derived address (deterministic)
- External account still needs native tokens for gas on target chain
- Use callbacks to handle signature results in smart contracts
- `key_version` is deprecated; use `domain_id` + `payload_v2` for new code
- The derived account must be funded with native tokens on the target chain before it can send transactions

## References

- [Chain Signatures Overview](https://docs.near.org/chain-abstraction/chain-signatures)
- [Getting Started](https://docs.near.org/chain-abstraction/chain-signatures/getting-started)
- [Implementation Guide](https://docs.near.org/chain-abstraction/chain-signatures/implementation)
- [MPC Contract](https://nearblocks.io/address/v1.signer)
- [chainsig.js Library](https://github.com/NearDeFi/chainsig.js)
- [Omni Transaction RS](https://github.com/near/omni-transaction-rs)
- [Multichain Examples](https://github.com/near-examples/near-multichain)
