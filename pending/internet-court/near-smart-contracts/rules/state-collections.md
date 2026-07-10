# State: Collections

Use NEAR SDK collections from `near_sdk::store` for efficient on-chain storage instead of standard Rust collections.

## Why It Matters

Standard Rust collections (HashMap, Vec, etc.) load entire data structures into memory, which:

- Wastes gas on large datasets
- Can exceed gas limits
- Inefficiently uses storage
- Causes performance issues

NEAR SDK collections provide lazy loading - only accessed data is loaded from storage.

**Rule of thumb:** Use native collections for <100 entries, SDK collections for larger datasets.

## ❌ Incorrect

```rust
use std::collections::HashMap;

#[near(contract_state)]
pub struct Contract {
    // Don't use standard Rust collections for large contract state
    pub users: HashMap<AccountId, User>,
    pub items: Vec<Item>,
}

#[near]
impl Contract {
    pub fn add_user(&mut self, user: User) {
        // Entire HashMap is loaded and saved on EVERY method call
        self.users.insert(env::predecessor_account_id(), user);
    }
}
```

**Problems:**

- Entire collection loaded into memory on every contract call
- High gas costs for large datasets
- Can hit gas limits with moderate data
- Inefficient serialization/deserialization

## ✅ Correct

```rust
use near_sdk::{near, env, AccountId, PanicOnDefault};
use near_sdk::store::{IterableMap, Vector, LookupMap};

#[near(serializers = [json, borsh])]
#[derive(Clone)]
pub struct User {
    pub name: String,
}

#[near(serializers = [json, borsh])]
#[derive(Clone)]
pub struct Item {
    pub title: String,
}

#[near(serializers = [json, borsh])]
#[derive(Clone)]
pub struct UserMetadata {
    pub role: String,
}

#[near(contract_state)]
#[derive(PanicOnDefault)]
pub struct Contract {
    // Use NEAR SDK store collections for efficient storage
    pub users: IterableMap<AccountId, User>,
    pub items: Vector<Item>,
    pub quick_lookup: LookupMap<AccountId, UserMetadata>,
}

#[near]
impl Contract {
    #[init]
    pub fn new() -> Self {
        Self {
            // Use unique byte prefixes for each collection
            users: IterableMap::new(b"u"),
            items: Vector::new(b"i"),
            quick_lookup: LookupMap::new(b"m"),
        }
    }

    pub fn add_user(&mut self, user: User) {
        // Only the specific entry is loaded and saved
        self.users.insert(env::predecessor_account_id(), user);
    }

    /// Pagination example for large collections
    pub fn get_users(&self, from_index: u64, limit: u64) -> Vec<(AccountId, User)> {
        self.users
            .iter()
            .skip(from_index as usize)
            .take(limit as usize)
            .map(|(k, v)| (k.clone(), v.clone()))
            .collect()
    }
}
```

**Benefits:**

- Lazy loading - only accessed data is loaded
- Lower gas costs for operations
- Scales to large datasets
- Efficient memory usage

## Collection Types Guide (near_sdk::store)

| Collection | Iterable | Use Case |
|------------|----------|----------|
| `LookupMap` | ❌ | Fastest key-value lookups, no iteration needed |
| `LookupSet` | ❌ | Fast membership checks, no iteration |
| `IterableMap` | ✅ | Key-value with iteration, preserves insertion order |
| `IterableSet` | ✅ | Set with iteration, preserves insertion order |
| `UnorderedMap` | ✅ | Key-value with iteration, no order guarantee |
| `UnorderedSet` | ✅ | Set with iteration, no order guarantee |
| `Vector` | ✅ | Ordered list with index access |
| `TreeMap` | ✅ | Sorted key-value with range queries |

## Additional Considerations

- Use unique byte prefixes for each collection (e.g., `b"u"`, `b"i"`)
- Choose the right collection type for your use case
- Implement pagination with `.skip()` and `.take()` for large collections
- Storage cost: ~1 NEAR per 100kb of data
- Never mix standard Rust collections with SDK collections for state
- Be careful with nested collections - each needs unique prefix

## References

- [Collections](https://docs.near.org/smart-contracts/anatomy/collections)
- [Storage Management](https://docs.near.org/concepts/storage/storage-staking)
