# Cross-Contract Calls: Promise Chaining

Chain promises correctly for sequential cross-contract calls and callback handling.

## Why It Matters

Cross-contract calls on NEAR are asynchronous and use promises. Proper promise chaining:

- Ensures correct execution order
- Handles errors gracefully
- Manages gas allocation
- Prevents lost funds or state inconsistencies

## ❌ Incorrect

```rust
#[near]
impl Contract {
    pub fn transfer_and_notify(&mut self, token: AccountId, amount: U128) {
        // Incorrect: Not returning promise, not chaining
        Promise::new(token)
            .function_call(
                "ft_transfer".to_string(),
                serde_json::to_vec(&json!({"receiver_id": env::current_account_id(), "amount": amount})).unwrap(),
                NearToken::from_yoctonear(1),
                Gas::from_tgas(5),
            );

        // This executes IMMEDIATELY, not after transfer completes!
        self.mark_transferred(amount);
    }
}
```

**Problems:**

- State changes happen before cross-contract call completes
- No error handling if transfer fails
- Promise not returned - caller can't track completion
- Race conditions possible
- Can't rollback if transfer fails

## ✅ Correct (SDK v5.x)

```rust
use near_sdk::{near, env, AccountId, NearToken, Gas, Promise, PromiseError};
use near_sdk::json_types::U128;

#[near(contract_state)]
#[derive(Default)]
pub struct Contract {
    total_transferred: U128,
}

#[near]
impl Contract {
    /// Return Promise so caller can track completion
    pub fn transfer_and_notify(&mut self, token: AccountId, amount: U128) -> Promise {
        // Chain the promise with a callback
        Promise::new(token)
            .function_call(
                "ft_transfer".to_string(),
                serde_json::to_vec(&serde_json::json!({
                    "receiver_id": env::current_account_id(),
                    "amount": amount
                })).unwrap(),
                NearToken::from_yoctonear(1), // 1 yoctoNEAR for security
                Gas::from_tgas(10),
            )
            .then(
                Promise::new(env::current_account_id())
                    .function_call(
                        "on_transfer_complete".to_string(),
                        serde_json::to_vec(&serde_json::json!({"amount": amount})).unwrap(),
                        NearToken::from_near(0),
                        Gas::from_tgas(10),
                    )
            )
    }

    /// Callback - marked #[private] so only this contract can call it
    #[private]
    pub fn on_transfer_complete(
        &mut self,
        amount: U128,
        #[callback_result] result: Result<(), PromiseError>,
    ) -> bool {
        match result {
            Ok(_) => {
                self.mark_transferred(amount);
                env::log_str(&format!("Transfer of {} completed", amount.0));
                true
            }
            Err(_) => {
                env::log_str("Transfer failed, not marking as transferred");
                false
            }
        }
    }

    fn mark_transferred(&mut self, amount: U128) {
        self.total_transferred = U128(self.total_transferred.0 + amount.0);
    }
}
```

**Benefits:**

- Proper promise chaining with callbacks
- Error handling with promise results
- State changes only after verification
- Callback marked `#[private]` for security
- Returns Promise so caller can track result

## Promise Patterns

### Multiple Sequential Calls

```rust
Promise::new(contract_a)
    .function_call(...)
    .then(Promise::new(contract_b).function_call(...))
    .then(Promise::new(env::current_account_id()).function_call(...)) // callback
```

### Parallel Calls with Join

```rust
let promise1 = Promise::new(contract_a).function_call(...);
let promise2 = Promise::new(contract_b).function_call(...);

promise1.and(promise2)
    .then(Promise::new(env::current_account_id()).function_call(...)) // callback
```

### Gas Recommendations

- Simple callback: 5-10 TGas
- Callback with state changes: 10-20 TGas
- Complex callback with more calls: 30+ TGas
- Default recommendation: 30 TGas for safety

## Additional Considerations

- Always return the Promise from cross-contract call functions
- Mark callbacks with `#[private]` to prevent external calls
- Use `#[callback_result] result: Result<T, PromiseError>` in callbacks to handle success/failure
- Allocate sufficient gas for callbacks
- Update state ONLY in callback after verifying success
- Consider using Yield/Resume for waiting on external services

## References

- [Cross-Contract Calls](https://docs.near.org/smart-contracts/anatomy/crosscontract)
- [Yield and Resume](https://docs.near.org/smart-contracts/anatomy/yield-resume)
- [Best Practices - Return Promise](https://docs.near.org/smart-contracts/anatomy/best-practices#return-promise)
