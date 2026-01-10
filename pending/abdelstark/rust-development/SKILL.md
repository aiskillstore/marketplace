---
name: rust-development
description: Rust development best practices for the Guts project - idiomatic code, error handling, async patterns, and commonware integration
---

# Rust Development Skill for Guts

You are developing a Rust project using commonware primitives for decentralized infrastructure.

## Code Style Guidelines

### General Principles

1. **Idiomatic Rust**: Follow Rust idioms and conventions
2. **Memory Safety**: Leverage the borrow checker, avoid unsafe unless absolutely necessary
3. **Error Handling**: Use `thiserror` for library errors, `anyhow` for applications
4. **Documentation**: Every public item needs docs with examples

### Formatting & Linting

```bash
# Always run before committing
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
```

### Error Handling Pattern

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum RepositoryError {
    #[error("repository not found: {0}")]
    NotFound(String),

    #[error("permission denied for repository: {0}")]
    PermissionDenied(String),

    #[error("storage error: {0}")]
    Storage(#[from] StorageError),
}

pub type Result<T> = std::result::Result<T, RepositoryError>;
```

### Async Patterns

Use Tokio for async runtime with structured concurrency:

```rust
use tokio::sync::{mpsc, oneshot};

// Prefer channels over shared state
pub struct Service {
    tx: mpsc::Sender<Command>,
}

impl Service {
    pub async fn query(&self, request: Request) -> Result<Response> {
        let (tx, rx) = oneshot::channel();
        self.tx.send(Command::Query { request, reply: tx }).await?;
        rx.await?
    }
}
```

### Module Structure

```rust
// lib.rs - re-export public API
pub mod error;
pub mod types;
pub mod service;

pub use error::{Error, Result};
pub use types::*;
pub use service::Service;
```

### Testing

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_feature() {
        // Arrange
        let service = Service::new().await;

        // Act
        let result = service.do_something().await;

        // Assert
        assert!(result.is_ok());
    }
}
```

## Commonware Integration

### Key Crates

- `commonware-cryptography`: Use for Ed25519 signatures
- `commonware-p2p`: Use for peer-to-peer networking
- `commonware-consensus`: Use for BFT consensus
- `commonware-storage`: Use for persistent storage
- `commonware-codec`: Use for serialization

### Example: Using Cryptography

```rust
use commonware_cryptography::{Ed25519, Signer, Verifier};

pub struct Identity {
    keypair: Ed25519,
}

impl Identity {
    pub fn new() -> Self {
        Self {
            keypair: Ed25519::generate(),
        }
    }

    pub fn sign(&self, message: &[u8]) -> Signature {
        self.keypair.sign(message)
    }
}
```

## Cargo.toml Best Practices

```toml
[package]
name = "guts-core"
version = "0.1.0"
edition = "2021"
rust-version = "1.75"
license = "MIT OR Apache-2.0"
description = "Core types and traits for Guts"
repository = "https://github.com/AbdelStark/guts"
keywords = ["decentralized", "git", "p2p"]
categories = ["development-tools"]

[dependencies]
# Use workspace dependencies
thiserror = { workspace = true }
tokio = { workspace = true }

[dev-dependencies]
tokio-test = { workspace = true }

[lints.rust]
unsafe_code = "deny"
missing_docs = "warn"

[lints.clippy]
all = "warn"
pedantic = "warn"
nursery = "warn"
```

## Performance Considerations

1. Use `Arc` for shared ownership across async tasks
2. Prefer `bytes::Bytes` for zero-copy networking
3. Use `dashmap` for concurrent hash maps
4. Profile with `flamegraph` before optimizing
