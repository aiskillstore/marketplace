# Best Practice: Contract Tools & NEP-297 Events

Use `near-sdk-contract-tools` to simplify implementation of NEP standards, common patterns with derive macros, and NEP-297 compliant structured events.

## Why It Matters

Implementing NEP standards (FT, NFT, storage management) from scratch is:

- Error-prone and requires extensive testing
- Time-consuming with boilerplate code
- Difficult to maintain across updates

`near-sdk-contract-tools` provides derive macros similar to OpenZeppelin for Ethereum, enabling:

- One-line implementation of complex standards
- Battle-tested, audited code
- Consistent patterns across contracts
- Automatic NEP-297 compliant event emission

NEP-297 defines a standard format for contract events that:

- Enables indexers (The Graph, Pikespeak, etc.) to parse events
- Provides structured data for analytics and monitoring
- Creates auditable event history on-chain
- Allows building reactive systems that respond to contract events

## ❌ Incorrect

```rust
// DON'T: Implement FT standard manually (hundreds of lines)
#[near]
impl Contract {
    pub fn ft_transfer(&mut self, receiver_id: AccountId, amount: U128, memo: Option<String>) {
        // Manual implementation - error prone
        let sender_id = env::predecessor_account_id();
        let amount = amount.0;

        // Missing: deposit check, storage check, event emission, etc.
        let sender_balance = self.balances.get(&sender_id).unwrap_or(0);
        self.balances.insert(sender_id, sender_balance - amount);
        // ... many more lines with potential bugs
    }

    // ... 20+ more methods to implement
}
```

```rust
// DON'T: Use unstructured log messages
env::log_str("Token transferred");

// DON'T: Use inconsistent formats
env::log_str(&format!("transfer: {} -> {} amount {}", from, to, amount));

// DON'T: Forget to include required NEP-297 fields
log!(r#"{{"event":"transfer","data":{}}}"#);  // Missing standard and version
```

**Problems:**

- Easy to miss edge cases in manual implementations
- No standard event emission
- Missing storage management
- Indexers cannot reliably parse unstructured logs
- Missing fields make events non-compliant with NEP-297

## ✅ Correct: Fungible Token

```rust
use near_sdk::{env, near, AccountId, PanicOnDefault};
use near_sdk_contract_tools::{ft::*, owner::Owner, standard::nep141::Nep141Controller, Owner};

#[derive(FungibleToken, Owner, PanicOnDefault)]
#[near(contract_state)]
pub struct Contract {}

#[near]
impl Contract {
    #[init]
    pub fn new(owner_id: AccountId) -> Self {
        let mut contract = Self {};

        Owner::init(&mut contract, &owner_id);

        contract.set_metadata(&ContractMetadata {
            name: "My Token".to_string(),
            symbol: "MTK".to_string(),
            decimals: 18,
            icon: Some("data:image/svg+xml...".to_string()),
            spec: "ft-1.0.0".to_string(),
            reference: None,
            reference_hash: None,
        });

        contract
    }

    /// Custom mint function - only owner can mint
    pub fn mint(&mut self, account_id: AccountId, amount: u128) {
        Self::require_owner();

        Nep141Controller::mint(self, &Nep141Mint::new(amount, account_id))
            .unwrap_or_else(|e| env::panic_str(&format!("Minting failed: {e}")));
    }

    /// Custom burn function
    pub fn burn(&mut self, amount: u128) {
        let account_id = env::predecessor_account_id();

        Nep141Controller::burn(self, &Nep141Burn::new(amount, account_id))
            .unwrap_or_else(|e| env::panic_str(&format!("Burning failed: {e}")));
    }
}

// All NEP-141 methods are automatically implemented:
// - ft_transfer
// - ft_transfer_call
// - ft_total_supply
// - ft_balance_of
// Plus NEP-145 storage management
```

**Benefits:**

- Complete NEP-141 + NEP-145 in a few lines
- Automatic event emission (NEP-297)
- Built-in storage management
- Audited, tested implementation

## ✅ Correct: NFT Implementation

```rust
use near_sdk::{env, near, AccountId, PanicOnDefault};
use near_sdk_contract_tools::{
    nft::*,
    owner::Owner,
    pause::{hooks::Pausable, Pause},
    NonFungibleToken, Owner, Pause,
};

/// NFT with automatic NEP-171, NEP-177 (metadata), NEP-178 (approval) implementation
#[derive(NonFungibleToken, Owner, Pause, PanicOnDefault)]
#[non_fungible_token(transfer_hook = "Pausable")]
#[near(contract_state)]
pub struct Contract {}

#[near]
impl Contract {
    #[init]
    pub fn new(owner_id: AccountId) -> Self {
        let mut contract = Self {};
        Owner::init(&mut contract, &owner_id);
        contract.set_contract_metadata(&ContractMetadata::new(
            "My NFT Collection".to_string(),
            "MNFT".to_string(),
            Some("https://ipfs.io/ipfs/".to_string()),
        ));
        contract
    }

    /// Mint new NFT - pausable and owner-only
    pub fn mint(&mut self, token_id: TokenId, receiver_id: AccountId) {
        Self::require_unpaused();
        Self::require_owner();
        Nep171Controller::mint(
            self,
            &Nep171Mint::new(vec![token_id], receiver_id),
        )
        .unwrap_or_else(|e| env::panic_str(&format!("Minting failed: {e}")));
    }

    /// Burn NFT - owner of token can burn
    pub fn burn(&mut self, token_id: TokenId) {
        let caller = env::predecessor_account_id();
        Nep171Controller::burn(
            self,
            &Nep171Burn::new(vec![token_id], caller),
        )
        .unwrap_or_else(|e| env::panic_str(&format!("Burning failed: {e}")));
    }
}
```

## Available Derive Macros

### High-Level (Composite) Macros

| Macro | Description | NEPs Implemented |
|-------|-------------|------------------|
| `FungibleToken` | Complete FT implementation | NEP-141, NEP-145, NEP-148 |
| `NonFungibleToken` | Complete NFT implementation | NEP-171, NEP-177, NEP-178, NEP-181 |

### Individual Standard Macros

| Macro | Description | NEP |
|-------|-------------|-----|
| `Nep141` | Fungible token core (transfer, balance) | NEP-141 |
| `Nep145` | Storage management | NEP-145 |
| `Nep148` | Fungible token metadata | NEP-148 |
| `Nep171` | Non-fungible token core (transfer, ownership) | NEP-171 |
| `Nep177` | NFT metadata | NEP-177 |
| `Nep178` | NFT approval management | NEP-178 |
| `Nep181` | NFT enumeration | NEP-181 |
| `Nep297` | NEP-297 event emission | NEP-297 |

### Utility Macros

| Macro | Description |
|-------|-------------|
| `Owner` | Ownership pattern with proposal/accept transfer |
| `Pause` | Pausable contract |
| `Rbac` | Role-based access control |
| `Escrow` | Escrow pattern |
| `Migrate` | Schema migration support |
| `Upgrade` | Contract upgrade support |
| `SimpleMultisig` | Multisig component |

## Hooks for Customization

```rust
use near_sdk::{env, near, require, AccountId, PanicOnDefault};
use near_sdk_contract_tools::hook::Hook;
use near_sdk_contract_tools::standard::nep141::Nep141Transfer;
use near_sdk_contract_tools::{ft::*, owner::Owner, FungibleToken, Owner};

// Define a custom hook type
pub struct MinimumTransferHook;

// Hook<C, A> where C = contract type, A = action type
// The hook is implemented on the hook type, NOT on the contract
impl Hook<Contract, Nep141Transfer<'_>> for MinimumTransferHook {
    fn hook<R>(
        contract: &mut Contract,
        args: &Nep141Transfer<'_>,
        f: impl FnOnce(&mut Contract) -> R,
    ) -> R {
        // Custom logic BEFORE transfer
        require!(
            args.amount >= 1_000_000,
            "Minimum transfer is 1 token"
        );

        // Execute transfer
        let result = f(contract);

        // Custom logic AFTER transfer
        env::log_str("Transfer completed with custom hook");

        result
    }
}

// Register the hook on the contract via the transfer_hook attribute
#[derive(FungibleToken, Owner, PanicOnDefault)]
#[fungible_token(transfer_hook = "MinimumTransferHook")]
#[near(contract_state)]
pub struct Contract {}
```

## NEP-297 Events

All derive macros automatically emit NEP-297 compliant events. For custom events or manual emission, use the following approaches.

### Custom Events with Derive Macro

```rust
use near_sdk::{env, near, serde::Serialize, AccountId, PanicOnDefault};
use near_sdk_contract_tools::standard::nep297::Event;
use near_sdk_contract_tools::Nep297;

#[derive(Nep297, Serialize)]
#[nep297(standard = "myapp", version = "1.0.0")]
pub enum MyAppEvent {
    #[nep297(name = "user_registered")]
    UserRegistered {
        user_id: AccountId,
        timestamp: u64,
    },
    #[nep297(name = "item_purchased")]
    ItemPurchased {
        buyer: AccountId,
        item_id: String,
        price: u128,
    },
}

// Usage inside a contract impl block
#[derive(PanicOnDefault)]
#[near(contract_state)]
pub struct Contract {}

#[near]
impl Contract {
    pub fn register_user(&mut self) {
        MyAppEvent::UserRegistered {
            user_id: env::predecessor_account_id(),
            timestamp: env::block_timestamp(),
        }
        .emit();
    }

    pub fn purchase_item(&mut self, item_id: String, price: u128) {
        MyAppEvent::ItemPurchased {
            buyer: env::predecessor_account_id(),
            item_id,
            price,
        }
        .emit();
    }
}
```

### Manual Event Emission (Fallback)

When not using `near-sdk-contract-tools`, emit NEP-297 events manually. Prefer the derive macro approach above whenever possible.

```rust
use near_sdk::{env, log, AccountId};

/// NEP-297 compliant event emission
/// Format: EVENT_JSON:{"standard":"<standard>","version":"<version>","event":"<event>","data":[<data>]}
fn emit_event(standard: &str, version: &str, event: &str, data: &str) {
    log!(
        r#"EVENT_JSON:{{"standard":"{}","version":"{}","event":"{}","data":[{}]}}"#,
        standard,
        version,
        event,
        data
    );
}

// Example usage
fn emit_custom_event(user: &AccountId, action: &str, metadata: &str) {
    emit_event(
        "myapp",
        "1.0.0",
        action,
        &format!(
            r#"{{"user":"{}","metadata":{}}}"#,
            user, metadata
        ),
    );
}
```

### Standard Event Names

| Standard | Events |
|----------|--------|
| nep141 (FT) | `ft_transfer`, `ft_mint`, `ft_burn` |
| nep171 (NFT) | `nft_mint`, `nft_transfer`, `nft_burn` |
| nep145 (Storage) | `storage_deposit`, `storage_withdraw` |

## Cargo.toml Setup

```toml
[dependencies]
near-sdk = "5.24"
near-sdk-contract-tools = "3.0"
```

## Additional Considerations

- Combine multiple derives for complex contracts
- Use hooks for custom business logic
- All derives emit NEP-297 compliant events
- Owner pattern includes proposal/accept for secure transfers
- Pause pattern can protect specific functions with `require_unpaused()`
- RBAC allows fine-grained permission control
- Always include `standard`, `version`, and `event` fields in manual events
- Data should be a JSON array (even for single items)
- Use lowercase snake_case for event names
- Version your events to handle schema changes
- Large numbers should be strings to avoid JSON precision issues
- Emit events AFTER state changes succeed
- Keep event data minimal but sufficient for indexing

## References

- [near-sdk-contract-tools](https://github.com/near/near-sdk-contract-tools)
- [FT Tutorial with Contract Tools](https://docs.near.org/primitives/ft/sdk-contract-tools)
- [NFT Tutorial with Contract Tools](https://docs.near.org/primitives/nft/nft-contract-tools)
- [Examples](https://github.com/near/near-sdk-contract-tools/tree/develop/examples)
- [NEP-297 Standard](https://github.com/near/NEPs/blob/master/neps/nep-0297.md)
- [Events in Contract Standards](https://docs.near.org/smart-contracts/anatomy/events)
