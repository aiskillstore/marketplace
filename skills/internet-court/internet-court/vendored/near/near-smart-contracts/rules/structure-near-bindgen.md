# Structure: NEAR Contract Macros

Use `#[near(contract_state)]` macro for contract struct and `#[near]` for implementation blocks.

## Why It Matters

The NEAR macros are essential for smart contracts as they:
- Automatically handle Borsh serialization/deserialization
- Expose methods to the NEAR runtime
- Manage contract state lifecycle
- Enable proper initialization patterns

## ❌ Incorrect

```rust
// Missing NEAR macros - contract won't work
pub struct Contract {
    pub owner: AccountId,
    pub data: IterableMap<AccountId, String>,
}

impl Contract {
    pub fn new(owner: AccountId) -> Self {
        Self {
            owner,
            data: IterableMap::new(b"d"),
        }
    }
}
```

**Problems:**
- Contract methods won't be callable
- State won't be properly serialized
- Runtime won't recognize the contract
- No initialization validation

## ✅ Correct

```rust
use near_sdk::{near, env, require, AccountId, PanicOnDefault};
use near_sdk::store::IterableMap;

#[near(contract_state)]
#[derive(PanicOnDefault)]
pub struct Contract {
    owner: AccountId,
    data: IterableMap<AccountId, String>,
}

#[near]
impl Contract {
    #[init]
    pub fn new(owner: AccountId) -> Self {
        Self {
            owner,
            data: IterableMap::new(b"d"),
        }
    }

    /// View function - takes &self, free to call
    pub fn get_owner(&self) -> &AccountId {
        &self.owner
    }

    /// Change function - takes &mut self, costs gas
    pub fn set_data(&mut self, key: AccountId, value: String) {
        require!(
            env::predecessor_account_id() == self.owner,
            "Only owner can set data"
        );
        self.data.insert(key, value);
    }
}
```

**Benefits:**
- `#[near(contract_state)]` handles all serialization automatically
- No need to manually derive `BorshDeserialize`/`BorshSerialize`
- Methods are callable from outside via `#[near]` on impl block
- Initialization validated with `#[init]`
- `PanicOnDefault` prevents uninitialized state access

## Data Structs (Non-Contract)

For data structures used in function arguments/returns:

```rust
/// Use #[near(serializers = [...])] for data structs
#[near(serializers = [json, borsh])]
#[derive(Clone)]
pub struct UserData {
    pub name: String,
    pub score: u64,
}
```

## Additional Considerations

- Use `#[near(contract_state)]` for the main contract struct
- Use `#[near]` for implementation blocks (replaces second `#[near_bindgen]`)
- Use `#[near(serializers = [json, borsh])]` for data structs returned to users
- Use `#[init]` for initialization methods
- Use `PanicOnDefault` to prevent accidental default initialization
- Mark view functions with `&self` (not `&mut self`)
- Use unique byte prefixes for all collections

## References

- [Smart Contract Structure](https://docs.near.org/smart-contracts/anatomy/)
- [Best Practices](https://docs.near.org/smart-contracts/anatomy/best-practices)
