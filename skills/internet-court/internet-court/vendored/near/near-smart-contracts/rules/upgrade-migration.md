# Upgrade: State Migration

Implement proper state migration when updating contracts with breaking state changes.

## Why It Matters

NEAR separates contract code from state. When you redeploy a contract with modified state structures, the existing state persists and may cause deserialization errors. Proper migration ensures:

- Smooth upgrades without data loss
- Clean removal of obsolete state structures
- Controlled upgrade process with governance

## ❌ Incorrect

```rust
// Deploying new contract with changed state structure
// WITHOUT migration leads to: "Cannot deserialize the contract state"

// OLD contract
#[near(contract_state)]
pub struct Contract {
    owner: AccountId,
    data: Vec<String>,
}

// NEW contract - deployed directly will FAIL
#[near(contract_state)]
pub struct Contract {
    owner: AccountId,
    data: Vec<String>,
    version: u32,  // New field causes deserialization failure
}
```

**Problems:**

- Contract becomes unusable after upgrade
- State cannot be read with new structure
- No way to recover without migration method
- Data may be lost

## ✅ Correct

```rust
use near_sdk::{near, env, require, AccountId, PanicOnDefault, Promise, Gas};

// Define old state for migration
#[near(serializers = [borsh])]
pub struct OldContract {
    owner: AccountId,
    data: Vec<String>,
}

// New contract state
#[near(contract_state)]
#[derive(PanicOnDefault)]
pub struct Contract {
    owner: AccountId,
    data: Vec<String>,
    version: u32,
}

#[near]
impl Contract {
    /// Migration method - call immediately after deploying new code
    /// #[init(ignore_state)] allows reading raw state bytes
    #[init(ignore_state)]
    #[private]  // Only callable by the contract itself
    pub fn migrate() -> Self {
        // Read old state
        let old_state: OldContract = env::state_read()
            .expect("Failed to read old state");

        env::log_str("Migration: Converting old state to new format");

        // Return new state with migrated data
        Self {
            owner: old_state.owner,
            data: old_state.data,
            version: 1,
        }
    }

    /// Self-update pattern for DAO-controlled upgrades
    pub fn update_contract(&self) -> Promise {
        // Verify caller is authorized (e.g., DAO, multisig)
        require!(
            env::predecessor_account_id() == self.owner,
            "Only owner can upgrade"
        );

        // Get new contract code from input
        let code = env::input().expect("No code provided");

        // Deploy new code and call migrate
        Promise::new(env::current_account_id())
            .deploy_contract(code)
            .then(
                Self::ext(env::current_account_id())
                    .with_static_gas(Gas::from_tgas(50))
                    .migrate()
            )
    }
}
```

**Benefits:**

- Smooth state transition
- No data loss
- Controlled upgrade process
- Clear migration path

## State Versioning Pattern

Use enums to simplify future migrations:

```rust
use near_sdk::{near, env};

#[near(serializers = [borsh])]
pub enum VersionedData {
    V1(DataV1),
    V2(DataV2),  // Add new versions without breaking changes
}

#[near(serializers = [borsh])]
pub struct DataV1 {
    pub value: String,
}

#[near(serializers = [borsh])]
pub struct DataV2 {
    pub value: String,
    pub timestamp: u64,  // New field in V2
}

impl VersionedData {
    pub fn upgrade(self) -> Self {
        match self {
            VersionedData::V1(v1) => VersionedData::V2(DataV2 {
                value: v1.value,
                timestamp: env::block_timestamp(),
            }),
            v2 => v2,  // Already latest version
        }
    }
}

#[near(contract_state)]
pub struct Contract {
    data: VersionedData,
}

impl Default for Contract {
    fn default() -> Self {
        Self {
            data: VersionedData::V2(DataV2 {
                value: String::new(),
                timestamp: 0,
            }),
        }
    }
}

#[near]
impl Contract {
    pub fn get_value(&self) -> &str {
        match &self.data {
            VersionedData::V1(v1) => &v1.value,
            VersionedData::V2(v2) => &v2.value,
        }
    }

    pub fn set_value(&mut self, value: String) {
        self.data = VersionedData::V2(DataV2 {
            value,
            timestamp: env::block_timestamp(),
        });
    }
}
```

## Additional Considerations

- Always test migrations on testnet before mainnet
- Use `#[private]` on migration methods to prevent external calls
- Clean up old state structures with `.clear()` to free storage
- Consider DAO or multisig governance for production upgrades
- Keep old state struct definitions for reading legacy data
- Version your contract state from the beginning

## References

- [Contract Upgrades](https://docs.near.org/smart-contracts/release/upgrade)
- [State Migration Example](https://github.com/near-examples/update-migrate-rust)
- [Self-Update Pattern](https://github.com/near-examples/update-migrate-rust/tree/main/self-updates)
