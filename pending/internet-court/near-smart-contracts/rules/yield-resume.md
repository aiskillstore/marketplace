# Yield & Resume

Use yield/resume pattern to pause contract execution while waiting for external services to provide data.

## Why It Matters

Traditional smart contracts execute synchronously. Yield/Resume enables:

- Waiting for off-chain oracle responses
- Integration with AI/ML services
- External data validation before continuing
- Complex multi-step workflows with external dependencies

The contract yields a cross-contract call to itself, waiting up to ~200 blocks (~2 minutes) for an external service to signal resume.

## ❌ Incorrect

```rust
// DON'T: Panic on timeout
#[private]
pub fn on_external_response(&mut self, response: Option<String>) -> String {
    // WRONG: Panicking reverts state changes made before yield
    response.expect("External service did not respond")
}

// DON'T: Leave resume method unprotected
pub fn respond(&mut self, yield_id: CryptoHash, data: String) {
    // WRONG: Anyone can call this and provide fake data!
    env::promise_yield_resume(&yield_id, &data.into_bytes());
}

// DON'T: Forget to clean up state on timeout
pub fn on_response(&mut self, request_id: u64, data: Option<String>) {
    if data.is_some() {
        self.pending_requests.remove(&request_id);  // Only cleanup on success
    }
    // WRONG: State not cleaned up on timeout - storage waste
}
```

**Problems:**

- Panicking on timeout wastes gas and reverts beneficial state changes
- Unprotected resume allows data injection attacks
- Not cleaning up on timeout causes storage bloat

## ✅ Correct

```rust
// Reference: https://docs.near.org/smart-contracts/anatomy/yield-resume
// Example: https://github.com/near-examples/yield-resume
use near_sdk::store::{IterableMap, LookupSet};
use near_sdk::{near, env, require, AccountId, BorshStorageKey, CryptoHash, Gas, GasWeight, PanicOnDefault, PromiseError};
use serde_json;

const YIELD_REGISTER: u64 = 0;

#[near]
#[derive(BorshStorageKey)]
enum Keys {
    Requests,
    Responders,
}

#[near(serializers = [borsh, json])]
#[derive(Clone)]
pub struct PendingRequest {
    pub yield_id: CryptoHash,
    pub requester: AccountId,
    pub prompt: String,
    pub created_at: u64,
}

// #[handle_result] converts Err into a panic, which reverts state changes
// in the callback. The official pattern uses an enum to avoid this.
#[near(serializers = [json])]
pub enum Response {
    Answer(String),
    TimeOutError,
}

#[near(contract_state)]
#[derive(PanicOnDefault)]
pub struct Contract {
    pending_requests: IterableMap<u64, PendingRequest>,
    next_id: u64,
    authorized_responders: LookupSet<AccountId>,
}

#[near]
impl Contract {
    #[init]
    pub fn new() -> Self {
        Self {
            pending_requests: IterableMap::new(Keys::Requests),
            next_id: 0,
            authorized_responders: LookupSet::new(Keys::Responders),
        }
    }

    /// Create a yielded promise that waits for external response.
    /// Requires attached deposit to cover storage for the pending request.
    #[payable]
    pub fn request_ai_response(&mut self, prompt: String) {
        let request_id = self.next_id;
        self.next_id += 1;

        env::log_str(&format!("Creating yield for request #{}", request_id));

        // Create callback arguments
        let callback_args = serde_json::to_vec(&serde_json::json!({
            "request_id": request_id
        })).unwrap();

        // Create yielded promise
        let promise = env::promise_yield_create(
            "on_ai_response",
            &callback_args,
            Gas::from_tgas(5),
            GasWeight::default(),
            YIELD_REGISTER,
        );

        // Retrieve the yield ID from register
        let yield_id: CryptoHash = env::read_register(YIELD_REGISTER)
            .expect("Failed to read yield ID")
            .try_into()
            .expect("Yield ID should be 32 bytes");

        self.pending_requests.insert(request_id, PendingRequest {
            yield_id,
            requester: env::predecessor_account_id(),
            prompt,
            created_at: env::block_timestamp(),
        });

        env::promise_return(promise);
    }

    /// External service calls this to provide response.
    ///
    /// If the call panics (e.g. invalid data), the external service
    /// can attempt to respond again before the promise times out.
    /// See: https://docs.near.org/smart-contracts/anatomy/yield-resume#managing-state
    pub fn respond(&mut self, request_id: u64, response: String) -> bool {
        require!(
            self.authorized_responders.contains(&env::predecessor_account_id()),
            "Caller not authorized to respond"
        );

        // Validate response before resuming — panic is safe here (allows retries)
        require!(!response.is_empty(), "Response cannot be empty");
        require!(response.len() <= 1024, "Response exceeds maximum length");

        let request = self.pending_requests.get(&request_id)
            .expect("No pending request with this ID");

        let yield_id = request.yield_id;

        let response_data = serde_json::to_vec(&response).unwrap();

        // Signal resume
        env::promise_yield_resume(&yield_id, &response_data)
    }

    /// Called when promise resumes (success or timeout).
    ///
    /// State changes in this callback are final. If you changed state before yielding,
    /// you must revert it here on timeout.
    #[private]
    pub fn on_ai_response(
        &mut self,
        request_id: u64,
        #[callback_result] response: Result<String, PromiseError>,
    ) -> Response {
        // (#9) Always clean up state regardless of success/timeout.
        // State changed before the yield (in request_ai_response) is already committed.
        // We must remove the request here to avoid orphaned entries on timeout.
        self.pending_requests.remove(&request_id);

        match response {
            Ok(answer) => {
                env::log_str(&format!("Request #{} completed successfully", request_id));
                Response::Answer(answer)
            }
            Err(_) => {
                // Timeout after ~200 blocks (~2 min). Don't panic — gracefully return.
                env::log_str(&format!("Request #{} timed out after ~200 blocks", request_id));
                Response::TimeOutError
            }
        }
    }

    pub fn list_requests(&self) -> Vec<(u64, PendingRequest)> {
        self.pending_requests
            .iter()
            .map(|(id, req)| (*id, req.clone()))
            .collect()
    }

    #[private]
    pub fn add_authorized_responder(&mut self, account_id: AccountId) {
        self.authorized_responders.insert(account_id);
    }
}
```

**Benefits:**

- Graceful timeout handling without panicking
- Protected resume method with authorization
- Proper state cleanup on both success and timeout
- View method for external services to query pending requests

## Timeout Behavior

Timeout occurs after ~200 blocks (~2 minutes). When timeout happens:

1. The callback (e.g. `on_ai_response`) is called with `response = Err(PromiseError)`
2. State changes made **before** the yield are already committed and preserved
3. State changes in the callback are preserved **only if the callback does not panic**

**Do not panic in the callback.** Panicking reverts the callback's state changes, but state changes from the yielding function are already committed — leading to inconsistent state.

## Additional Considerations

- Maximum wait time: ~200 blocks (~2 minutes)
- Allocate sufficient gas for both yield creation and callback
- Always clean up state in callback (success AND timeout)
- Protect resume method with proper access control
- Consider storing yield IDs for multiple concurrent requests
- External service should monitor for pending requests
- Use view methods to expose pending requests to external services
- Consider emitting NEP-297 events on success/timeout to help indexers and external services track request lifecycle
- Require attached deposit on yield-creating methods to cover storage for pending requests (see storage checks rule)

## References

- [Yield & Resume Documentation](https://docs.near.org/smart-contracts/anatomy/yield-resume)
- [Yield Resume Blog Post](https://docs.near.org/blog/yield-resume)
- [Example Implementation](https://github.com/near-examples/yield-resume)
- [Shade Agent AI DAO Tutorial (yield/resume in practice)](https://docs.near.org/ai/shade-agents/tutorials/ai-dao/overview)
