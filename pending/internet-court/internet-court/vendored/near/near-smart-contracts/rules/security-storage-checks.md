# Security: Storage Checks

Always validate storage operations to prevent unauthorized access, data corruption and storage attacks.

## Why It Matters

NEAR smart contracts store data on-chain with associated storage costs (~1 NEAR per 100kb). Improper storage management can lead to:

- Unauthorized data access or modification
- Storage staking attacks (attackers filling your storage)
- Gas inefficiency
- Contract vulnerabilities

## ❌ Incorrect

```rust
#[near]
impl Contract {
    pub fn update_user_data(&mut self, user_id: AccountId, data: String) {
        // No validation - anyone can update any user's data
        // No storage deposit check - contract pays for attacker's data
        self.user_data.insert(user_id, data);
    }
}
```

**Problems:**

- No access control validation
- No storage deposit checks
- Allows unauthorized modifications
- Contract could run out of NEAR for storage

## ✅ Correct

```rust
use near_sdk::{near, env, require, AccountId, NearToken, PanicOnDefault, Promise};
use near_sdk::store::LookupMap;

#[near(contract_state)]
#[derive(PanicOnDefault)]
pub struct Contract {
    user_data: LookupMap<AccountId, String>,
}

#[near]
impl Contract {
    #[init]
    pub fn new() -> Self {
        Self {
            user_data: LookupMap::new(b"u"),
        }
    }

    #[payable]
    pub fn update_user_data(&mut self, user_id: AccountId, data: String) {
        // Verify caller is authorized
        require!(
            env::predecessor_account_id() == user_id,
            "Only the user can update their own data"
        );

        // Check storage deposit if needed
        let initial_storage = env::storage_usage();

        self.user_data.insert(user_id, data);

        // Calculate storage cost
        let storage_used = env::storage_usage() - initial_storage;
        let storage_cost = NearToken::from_yoctonear(
            storage_used as u128 * env::storage_byte_cost().as_yoctonear()
        );

        require!(
            env::attached_deposit() >= storage_cost,
            format!("Insufficient deposit. Required: {} yoctoNEAR", storage_cost.as_yoctonear())
        );

        // Refund excess deposit
        let refund = env::attached_deposit().saturating_sub(storage_cost);
        if refund > NearToken::from_yoctonear(0) {
            Promise::new(env::predecessor_account_id()).transfer(refund).detach();
        }
    }
}
```

**Benefits:**

- Validates caller authorization with `require!`
- Ensures proper storage payment
- Prevents unauthorized access
- Refunds excess deposits
- Clear error messages

## Small Deposit Attack Prevention

Require minimum deposits to prevent spam attacks:

```rust
#[payable]
pub fn register(&mut self) {
    let minimum_deposit = NearToken::from_millinear(10); // 0.01 NEAR
    require!(
        env::attached_deposit() >= minimum_deposit,
        "Minimum deposit of 0.01 NEAR required"
    );
    // ... registration logic
}
```

## Additional Considerations

- Use `env::predecessor_account_id()` for access control
- Use `require!` instead of `assert!` for better error messages
- Calculate and validate storage costs
- Refund excess deposits when appropriate
- Consider NEP-145 for complex storage management
- Test storage edge cases and attack scenarios

## References

- [Storage Staking](https://docs.near.org/concepts/storage/storage-staking)
- [Security - Storage](https://docs.near.org/smart-contracts/security/storage)
- [NEP-145: Storage Management](https://github.com/near/NEPs/blob/master/neps/nep-0145.md)
