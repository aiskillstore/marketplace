# Testing: Integration Tests (near-sandbox + near-api)

Use `near-sandbox` with `near-api` for realistic integration testing with actual contract deployment in a local sandbox environment.

## Why It Matters

Integration tests validate:

- Contract deployment and initialization
- Cross-contract interactions
- Real gas consumption
- Actual blockchain behavior
- End-to-end workflows
- Time-sensitive operations (with fast forward)

## ❌ Incorrect

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_transfer() {
        // Unit test only - doesn't test actual deployment
        let mut contract = Contract::new("owner.near".parse().unwrap());
        contract.transfer("user.near".parse().unwrap(), U128(100));
        // Can't test cross-contract calls, gas usage, etc.
    }
}
```

**Problems:**

- Doesn't test actual deployment
- Can't verify cross-contract calls
- No gas profiling
- Misses blockchain-specific edge cases

## ✅ Correct (near-sandbox + near-api)

```rust
use near_api::{AccountId, NearToken};
use near_sdk::serde_json::json;

async fn create_subaccount(
    sandbox: &near_sandbox::Sandbox,
    name: &str,
) -> testresult::TestResult<near_api::Account> {
    let account_id: AccountId = name.parse().unwrap();
    sandbox
        .create_account(account_id.clone())
        .initial_balance(NearToken::from_near(10))
        .send()
        .await?;
    Ok(near_api::Account(account_id))
}

#[tokio::test]
async fn test_contract_basics() -> testresult::TestResult<()> {
    // Start local sandbox
    let sandbox = near_sandbox::Sandbox::start_sandbox().await?;
    let sandbox_network =
        near_api::NetworkConfig::from_rpc_url("sandbox", sandbox.rpc_addr.parse()?);

    // Create test accounts
    let alice = create_subaccount(&sandbox, "alice.sandbox").await?;
    let contract = create_subaccount(&sandbox, "contract.sandbox")
        .await?
        .as_contract();

    // Setup signer (uses default genesis account)
    let signer = near_api::Signer::from_secret_key(
        near_sandbox::config::DEFAULT_GENESIS_ACCOUNT_PRIVATE_KEY
            .parse()
            .unwrap(),
    )?;

    // Compile contract
    let contract_wasm_path = cargo_near_build::build_with_cli(Default::default())?;
    let contract_wasm = std::fs::read(contract_wasm_path)?;

    // Deploy and initialize contract
    near_api::Contract::deploy(contract.account_id().clone())
        .use_code(contract_wasm)
        .with_init_call("new", json!({"owner_id": alice.account_id()}))?
        .with_signer(signer.clone())
        .send_to(&sandbox_network)
        .await?
        .assert_success();

    // Call a contract method (as alice, the owner)
    contract
        .call_function("set_data", json!({
            "key": alice.account_id(),
            "value": "hello world"
        }))
        .transaction()
        .with_signer(alice.account_id().clone(), signer.clone())
        .send_to(&sandbox_network)
        .await?
        .assert_success();

    // Check alice's balance after interaction
    let balance = alice
        .tokens()
        .near_balance()
        .fetch_from(&sandbox_network)
        .await?
        .total;

    assert!(
        balance > NearToken::from_near(0),
        "Alice should have a positive balance"
    );

    Ok(())
}
```

**Benefits:**

- Tests actual contract deployment
- Validates cross-contract calls
- Measures real gas consumption
- Tests in isolated sandbox environment
- Catches integration issues

## Test Patterns

### Testing Failures

```rust
// Expect a call to fail
contract
    .call_function("invalid_method", ())
    .transaction()
    .with_signer(alice.account_id().clone(), signer.clone())
    .send_to(&sandbox_network)
    .await?
    .assert_failure();
```

### Time Travel (fast forward blocks)

```rust
#[tokio::test]
async fn test_time_sensitive() -> testresult::TestResult<()> {
    let sandbox = near_sandbox::Sandbox::start_sandbox().await?;
    // ... setup ...

    // Fast forward 200 blocks
    sandbox.fast_forward(200).await?;

    // Now test time-dependent logic
    contract
        .call_function("claim", ())
        .transaction()
        .gas(NearGas::from_tgas(30))
        .with_signer(user.account_id().clone(), signer.clone())
        .send_to(&sandbox_network)
        .await?
        .assert_success();

    Ok(())
}
```

### Check Account Balance

```rust
let balance = alice
    .tokens()
    .near_balance()
    .fetch_from(&sandbox_network)
    .await?
    .total;

assert!(balance > NearToken::from_millinear(9990));
```

### Specify Gas for Calls

```rust
contract
    .call_function("expensive_operation", ())
    .transaction()
    .gas(NearGas::from_tgas(30))
    .with_signer(alice.account_id().clone(), signer.clone())
    .send_to(&sandbox_network)
    .await?
    .assert_success();
```

## Cargo.toml Setup

```toml
[dev-dependencies]
near-sandbox = "0.3"
near-api = "0.1"
cargo-near-build = "0.2"
tokio = { version = "1", features = ["full"] }
testresult = "0.4"
```

## Additional Considerations

- Use `near_sandbox::Sandbox::start_sandbox()` to create isolated local environment
- Use `sandbox.fast_forward(blocks)` for time-sensitive tests
- Use `near_api::Contract::deploy()` for deploying contracts
- Use `.assert_success()` and `.assert_failure()` for result validation
- Use `cargo_near_build::build_with_cli()` to compile contracts in tests
- Create helper functions like `create_subaccount()` to reduce boilerplate
- Test both success and failure cases
- Test edge cases with max values

## References

- [Integration Testing](https://docs.near.org/smart-contracts/testing/integration-test)
- [near-sandbox GitHub](https://github.com/near/near-sandbox)
- [near-api-rs GitHub](https://github.com/near/near-api-rs)
- [NEAR Examples with Tests](https://github.com/near-examples)
