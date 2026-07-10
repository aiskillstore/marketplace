---
name: near-smart-contracts
description: NEAR Protocol smart contract development in Rust. Use when writing, reviewing, or deploying NEAR smart contracts. Covers contract structure, state management, cross-contract calls, testing, security, and optimization patterns. Based on near-sdk v5.x with modern macro syntax.
license: MIT
metadata:
  author: near
  version: "1.0.0"
---

# NEAR Smart Contracts Development

Comprehensive guide for developing secure and efficient smart contracts on NEAR Protocol using Rust and the NEAR SDK (v5.x).

## When to Apply

Reference these guidelines when:

- Writing new NEAR smart contracts in Rust
- Reviewing existing contract code for security and optimization
- Implementing cross-contract calls and callbacks
- Managing contract state and storage
- Testing and deploying NEAR contracts
- Optimizing gas usage and performance

## Getting Started

### Prerequisites

Install the required tools before starting development:

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add wasm32 target for compiling contracts
rustup target add wasm32-unknown-unknown

# Install cargo-near (build, deploy, and manage contracts)
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/near/cargo-near/releases/latest/download/cargo-near-installer.sh | sh

# Install near-cli-rs (interact with NEAR network)
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/near/near-cli-rs/releases/latest/download/near-cli-rs-installer.sh | sh
```

### Create a New Project

> **CRITICAL**: ALWAYS run `cargo near new` to create new projects. NEVER manually create Cargo.toml, lib.rs, or any project files. The command generates all required files with correct configurations.

```bash
# REQUIRED: Create a new contract project using the official template
cargo near new my-contract

# Navigate to project directory
cd my-contract

# Build the contract
cargo near build

# Run tests
cargo test
```

**Why `cargo near new` is mandatory:**
- Generates correct `Cargo.toml` with proper dependencies and build settings
- Creates proper project structure with `src/lib.rs` template
- Includes integration test setup in `tests/` directory
- Configures release profile with `overflow-checks = true`
- Sets up correct crate-type for WASM compilation
- Avoids common configuration mistakes that cause build failures

**DO NOT:**
- Manually create `Cargo.toml`
- Manually create `src/lib.rs`
- Copy-paste project structure from examples
- Skip this step and create files directly

### Project Structure

```
my-contract/
├── Cargo.toml          # Dependencies and project config
├── src/
│   └── lib.rs          # Main contract code
├── tests/              # Integration tests
│   └── test_basics.rs
└── README.md
```

### Deploy to Testnet

```bash
# Create a testnet account (if needed)
near account create-account sponsor-by-faucet-service my-contract.testnet autogenerate-new-keypair save-to-keychain network-config testnet create

# Build in release mode
cargo near build --release

# Deploy to testnet
cargo near deploy my-contract.testnet without-init-call network-config testnet sign-with-keychain send
```

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
| --------- | ---------- | -------- | --------- |
| 1 | Security & Safety | CRITICAL | `security-` |
| 2 | Contract Structure | HIGH | `structure-` |
| 3 | State Management | HIGH | `state-` |
| 4 | Cross-Contract Calls | MEDIUM-HIGH | `xcc-` |
| 5 | Contract Upgrades | MEDIUM-HIGH | `upgrade-` |
| 6 | Chain Signatures | MEDIUM-HIGH | `chain-` |
| 7 | Gas Optimization | MEDIUM | `gas-` |
| 8 | Yield & Resume | MEDIUM | `yield-` |
| 9 | Testing | MEDIUM | `testing-` |
| 10 | Best Practices | MEDIUM | `best-` |

### 1. Security & Safety (CRITICAL)

- `security-storage-checks` - Always validate storage operations and check deposits
- `security-access-control` - Implement proper access control using `predecessor_account_id`
- `security-reentrancy` - Protect against reentrancy attacks (update state before external calls)
- `security-overflow` - Use `overflow-checks = true` in Cargo.toml to prevent overflow
- `security-callback-validation` - Validate callback results and handle failures
- `security-private-callbacks` - Mark callbacks as `#[private]` to prevent external calls
- `security-yoctonear-validation` - Validate attached deposits with `#[payable]` functions
- `security-sybil-resistance` - Implement minimum deposit checks to prevent spam

### 2. Contract Structure (HIGH)

- `structure-near-bindgen` - Use `#[near(contract_state)]` macro for contract struct (replaces old `#[near_bindgen]`)
- `structure-initialization` - Implement proper initialization with `#[init]` patterns
- `structure-versioning` - Plan for contract upgrades with versioning mechanisms
- `structure-events` - Use `env::log_str()` and structured event logging (NEP-297)
- `structure-standards` - Follow NEAR Enhancement Proposals (NEPs) for standards
- `structure-serializers` - Use `#[near(serializers = [json, borsh])]` for data structs
- `structure-panic-default` - Use `#[derive(PanicOnDefault)]` to require initialization

### 3. State Management (HIGH)

- `state-collections` - Use SDK collections from `near_sdk::store`: `IterableMap`, `IterableSet`, `Vector`, `LookupMap`, `LookupSet`, `UnorderedMap`, `UnorderedSet`, `TreeMap`
- `state-serialization` - Use Borsh for state, JSON for external interfaces
- `state-lazy-loading` - Use SDK collections for lazy loading to save gas (loaded on-demand, not all at once)
- `state-pagination` - Implement pagination with `.skip()` and `.take()` for large datasets
- `state-migration` - Plan state migration strategies using versioning
- `state-storage-cost` - Remember: 1 NEAR ≈ 100kb storage, contracts pay for their storage
- `state-unique-prefixes` - Use unique byte prefixes for all collections (avoid collisions)
- `state-native-vs-sdk` - Native collections (Vec, HashMap) load all data; use only for <100 entries

### 4. Cross-Contract Calls (MEDIUM-HIGH)

- `xcc-promise-chaining` - Chain promises correctly
- `xcc-callback-handling` - Handle all callback scenarios (success, failure)
- `xcc-gas-management` - Allocate appropriate gas for cross-contract calls
- `xcc-error-handling` - Implement robust error handling
- `xcc-result-unwrap` - Never unwrap promise results without checks

### 5. Contract Upgrades & Migration (MEDIUM-HIGH)

- `upgrade-migration` - Use enums for state versioning and implement `migrate` method with `#[init(ignore_state)]`
- `upgrade-self-update` - Pattern for contracts that can update themselves programmatically
- `upgrade-cleanup-old-state` - Always remove old state structures to free storage
- `upgrade-dao-controlled` - Use multisig or DAO for production upgrade governance

### 6. Chain Signatures (MEDIUM-HIGH)

- `chain-signatures` - Derive foreign blockchain addresses, request MPC signatures, and build multichain transactions
- `chain-callback-handling` - Handle MPC signature callbacks properly
- `chain-gas-allocation` - Allocate sufficient gas for MPC calls (yield/resume pattern)

### 7. Gas Optimization (MEDIUM)

- `gas-batch-operations` - Batch operations to reduce transaction costs
- `gas-minimal-state-reads` - Minimize state reads and writes (cache in memory)
- `gas-efficient-collections` - Choose appropriate collection types (LookupMap vs IterableMap)
- `gas-view-functions` - Mark read-only functions as view (`&self` in Rust)
- `gas-avoid-cloning` - Avoid unnecessary cloning of large data structures
- `gas-early-validation` - Use `require!` early to save gas on invalid inputs
- `gas-prepaid-gas` - Attach appropriate gas for cross-contract calls (recommended: 30 TGas)

### 8. Yield & Resume (MEDIUM)

- `yield-resume` - Create yielded promises, signal resume, handle timeouts, and manage state between yield/resume
- `yield-gatekeeping` - Protect resume methods from unauthorized callers

### 9. Testing (MEDIUM)

- `testing-integration-tests` - Use `near-sandbox` + `near-api` for integration tests
- `testing-unit-tests` - Write comprehensive unit tests with mock contexts
- `testing-sandbox` - Test with local sandbox environment before testnet/mainnet
- `testing-edge-cases` - Test boundary conditions, overflow, and empty states
- `testing-gas-profiling` - Profile gas usage in integration tests
- `testing-cross-contract` - Test cross-contract calls and callbacks thoroughly
- `testing-failure-scenarios` - Test promise failures and timeout scenarios
- `testing-time-travel` - Use `sandbox.fast_forward()` for time-sensitive tests

### 10. Best Practices (MEDIUM)

- `best-contract-tools` - Use `near-sdk-contract-tools` for NEP standards (FT, NFT, etc.) and NEP-297 structured events
- `best-panic-messages` - Provide clear, actionable panic messages
- `best-logging` - Use `env::log_str()` for debugging and event emission
- `best-documentation` - Document public methods, parameters, and complex logic
- `best-error-types` - Define custom error types or use descriptive strings
- `best-constants` - Use constants for magic numbers and configuration
- `best-require-macro` - Use `require!` instead of `assert!` for better error messages
- `best-promise-return` - Return promises from cross-contract calls for proper tracking
- `best-sdk-crates` - Reuse SDK-exported crates (borsh, serde, base64, etc.)
- `best-account-id-encoding` - Encode AccountIds in base32 for 40% storage savings

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/security-storage-checks.md
rules/structure-near-bindgen.md
rules/state-collections.md
rules/xcc-promise-chaining.md
rules/upgrade-migration.md
rules/chain-signatures.md
rules/yield-resume.md
rules/best-contract-tools.md
rules/testing-integration-tests.md
```

Each rule file contains:

- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Additional context and NEAR-specific considerations

## Latest Tools & Versions

### Development Tools

- **cargo-near**: Latest - Build, deploy, and manage contracts (`cargo near build`, `cargo near deploy`)
- **near-cli-rs**: Latest - Command-line interface for NEAR (`near contract call`, `near contract view`)
- **rustc**: Latest stable - Rust compiler
- **near-sandbox**: Latest - Local sandbox environment for integration testing
- **near-api-rs**: Latest - Rust API client for interacting with NEAR (replaces near-workspaces-rs for tests)
- **omni-transaction-rs**: Latest - Build transactions for multiple blockchains (Bitcoin, Ethereum, etc.)

### SDK Versions

- **near-sdk-rs**: v5.x (v6.x coming with structured errors support)
- **near-sdk-contract-tools**: Latest - Derive macros for NEP standards (FT, NFT, Storage Management)

### Key Features

- **Unified macro syntax**: `#[near(contract_state)]` replaces `#[near_bindgen]` + derives
- **Flexible serialization**: `#[near(serializers = [json, borsh])]` for data structs
- **Store collections**: `near_sdk::store::IterableMap`, `IterableSet`, `LookupMap`, `LookupSet`, `Vector`, `UnorderedMap`, `UnorderedSet`, `TreeMap`
- **Simplified cross-contract calls**: High-level promise API with `Promise::new()` and `.then()`
- **Built-in NEP support**: FT (NEP-141), NFT (NEP-171), and other standards
- **Result handling**: `#[handle_result]` for methods returning `Result<T, E>` without panicking
- **Yield/Resume**: Contracts can yield execution and wait for external services to resume
- **Chain Signatures**: Sign transactions for other blockchains (Bitcoin, Ethereum, Solana, etc.)
- **Contract Tools**: Derive macros for Owner, Pause, Role-based access control patterns

## Resources

- NEAR Documentation: <https://docs.near.org>
- Smart Contract Quickstart: <https://docs.near.org/smart-contracts/quickstart>
- Contract Anatomy: <https://docs.near.org/smart-contracts/anatomy/>
- NEAR SDK Rust: <https://docs.near.org/tools/sdk>
- SDK Rust Reference: <https://docs.rs/near-sdk>
- Storage & Collections: <https://docs.near.org/smart-contracts/anatomy/collections>
- Best Practices: <https://docs.near.org/smart-contracts/anatomy/best-practices>
- Cross-Contract Calls: <https://docs.near.org/smart-contracts/anatomy/crosscontract>
- Yield & Resume: <https://docs.near.org/smart-contracts/anatomy/yield-resume>
- Contract Upgrades: <https://docs.near.org/smart-contracts/release/upgrade>
- Chain Signatures: <https://docs.near.org/chain-abstraction/chain-signatures>
- Chain Signatures Implementation: <https://docs.near.org/chain-abstraction/chain-signatures/implementation>
- Security Best Practices: <https://docs.near.org/smart-contracts/security/welcome>
- Integration Testing: <https://docs.near.org/smart-contracts/testing/integration-test>
- NEP-297 Events: <https://github.com/near/NEPs/blob/master/neps/nep-0297.md>
- NEAR Standards (NEPs): <https://github.com/near/NEPs>
- NEAR Examples: <https://github.com/near-examples>
- Sandbox Testing: <https://github.com/near/near-sandbox>
- NEAR API Rust: <https://github.com/near/near-api-rs>
- Omni Transaction RS: <https://github.com/near/omni-transaction-rs>
- Contract Tools: <https://github.com/near/near-sdk-contract-tools>

## Storage Costs Reference

| Storage | Cost | Notes |
|---------|------|-------|
| 1 byte | 0.00001 NEAR | ~10kb per 0.1 NEAR |
| 100 KB | ~1 NEAR | Approximate reference |
| AccountId | 64+ bytes | Can save 40% with base32 encoding |
| Contract code | Variable | Paid by contract account |

## SDK Collections Reference

| Collection | Iterable | Clear | Ordered | Range | Use Case |
|------------|----------|-------|---------|-------|----------|
| `Vector` | Yes | Yes | Yes | Yes | Ordered list with index access |
| `LookupMap` | No | No | No | No | Fast key-value, no iteration needed |
| `LookupSet` | No | No | No | No | Fast membership checks |
| `IterableMap` | Yes | Yes | Yes | No | Key-value with iteration |
| `IterableSet` | Yes | Yes | Yes | No | Set with iteration |
| `UnorderedMap` | Yes | Yes | No | No | Key-value, unordered iteration |
| `UnorderedSet` | Yes | Yes | No | No | Set, unordered iteration |
| `TreeMap` | Yes | Yes | Yes | Yes | Sorted key-value with range queries |
