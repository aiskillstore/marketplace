---
name: Senior Rust Practices
description: This skill should be used when the user asks about "rust workspace", "rust best practices", "cargo workspace setup", "rust code organization", "rust dependency management", "rust testing strategy", "rust project", "scalable rust", "rust CI setup", or needs guidance on senior-level Rust development patterns, workspace design, code organization strategies, or production-ready Rust architectures.
---

# Senior Rust Development Practices

Battle-tested patterns for Rust workspace architecture, code organization, dependencies, and testing that scale from prototype to production.

## Git Worktree Workflow Compliance

**All coding work MUST happen in git worktrees.** Before making any code changes:

1. Create a worktree: `git worktree add ~/.claude/worktrees/$(basename $(pwd))/<task> -b feat/<task>`
2. Work in that directory
3. Use `/merge` to consolidate changes back to main

Never edit files directly in the main worktree.

## Completion Requirements

**Before completing ANY Rust task, you MUST:**

1. Run tests: `cargo test --workspace`
2. Run linting: `trunk check`
3. Fix any issues before declaring done

If trunk has formatting issues, run `trunk fmt` to auto-fix.

## Workspace Architecture

### Start from "One Product = One Repo = One Workspace"

Use a Rust workspace when you have:

- Multiple crates that ship together (binary + libraries)
- Shared tooling / CI
- Shared versioning policy

**Canonical workspace structure:**

```text
repo/
  Cargo.toml            # workspace root
  crates/
    core/               # pure domain logic (no IO)
    storage/            # DB, filesystem, etc.
    api/                # HTTP/GRPC handlers, DTOs
    cli/                # binary
  tools/                # optional: internal binaries (codegen, migration, etc.)
  tests/                # optional: black-box integration tests
```

### Keep Crates "Thin" and Boundaries "Hard"

**Layered architecture:**

- **core**: Pure logic, types, validation, algorithms. Minimal deps.
- **adapters**: IO boundaries (db, network, rpc, filesystem). Trait-based boundary, minimal leakage.
- **app / service**: Wiring (DI), config, runtime, orchestration.
- **bins**: CLI/daemon that just calls "app".

**Critical rule:** If `core` imports `tokio`, `reqwest`, or `sqlx`, you've already lost the separation.

### Default to a Small Number of Crates

Too many crates is busywork. Start with 2–5 max.

**Split only when:**

- Compile times are painful and boundaries are real
- You need separate release cadence
- You need different dependency profiles (no-std, wasm, etc.)

### Workspace Dependencies: Centralize Versions, Not Architecture

In root `Cargo.toml`, use workspace dependencies to keep versions aligned:

```toml
[workspace]
members = ["crates/*"]
resolver = "2"

[workspace.dependencies]
anyhow = "*"  # use latest
thiserror = "*"  # use latest
serde = { version = "*", features = ["derive"] }  # use latest
tokio = { version = "*", features = ["macros", "rt-multi-thread"] }  # use latest
```

In crate `Cargo.toml`:

```toml
[dependencies]
serde = { workspace = true }
```

This reduces version drift and security churn.

### Be Ruthless with Features

- Prefer additive features (enable more capabilities) vs "feature flags that change semantics"
- Put "heavy" deps behind features (db, http, metrics)
- Avoid default features that pull the world

**Pattern for optional dependencies:**

```toml
[dependencies]
sqlx = { workspace = true, optional = true }

[features]
db = ["dep:sqlx"]
```

### Enforce a Policy: MSRV + Toolchain

- Pin toolchain with `rust-toolchain.toml`
- Decide MSRV (minimum supported Rust version) and test it in CI
- Keep clippy/rustfmt consistent

## Code Organization

### Modules Should Match How You Reason, Not File-Per-Type

Organize by capability / domain, not by "models/handlers/utils" spaghetti.

**Good organization:**

```text
core/
  src/
    lib.rs
    payment/
      mod.rs
      validation.rs
      pricing.rs
    user/
      mod.rs
      id.rs
      rules.rs
```

**Avoid:**

```text
models.rs
handlers.rs
utils.rs
```

### Public API: Small Surface Area, Explicit Re-Exports

- Make most things `pub(crate)` by default
- Re-export a curated API from `lib.rs`

```rust
mod payment;
pub use payment::{Payment, PaymentError};
```

If everything is `pub` you've created an accidental framework.

### Avoid "Prelude" Unless You Truly Need It

Preludes tend to hide dependencies and make code review harder. Prefer explicit imports.

### Error Strategy: Pick One and Stick to It

**Common approach:**

- Library crates: `thiserror` for typed errors
- Binaries: `anyhow` at the top level

Don't leak `anyhow::Error` across library boundaries unless you explicitly want "opaque".

### Keep Async at the Edge

If you can keep core synchronous and pure, you gain:

- Simpler tests
- Portability
- Less lifetime/pinning headaches

## Dependency Hygiene

### Be Picky: Fewer Deps, Higher-Quality Deps

Every dependency adds:

- Build time
- Audit surface
- Semver risk

Prefer "boring" crates with strong maintenance.

### Use `cargo-deny` + `cargo-audit`

Make dependency issues visible early (licenses, advisories, duplicate versions).

### Don't Use `unwrap()` in Libraries

In binaries/tests it's fine (especially in test scaffolding). In libraries, return errors with context.

## Testing Strategy That Scales

Think "pyramid":

### 1. Unit Tests: Fast, Deterministic, Lots

- Put most tests close to code: `mod tests {}` in the same file for private access
- Test invariants and edge cases, not just happy paths
- Avoid hitting the filesystem/network in unit tests

### 2. Integration Tests: Black-Box the Public API

Use `crates/<crate>/tests/*.rs` for API-level tests.

- Treat it as "a consumer of the crate"
- Don't reach into private internals

### 3. End-to-End Tests: Few, But Real

If you have a service:

- Spin up dependencies (db) in CI (containers)
- Run a small set of scenario tests

### 4. Property Tests + Fuzzing When Correctness Matters

- `proptest` for invariants ("decode(encode(x)) == x")
- `cargo-fuzz` for parsers/decoders/inputs from outside

### 5. Doctests Are Underrated

Doctests enforce that examples compile and keep your public API honest.

## Logging and Tracing

### Never Use `println!` - Use Tracing Instead

**NEVER use `println!`, `eprintln!`, or `dbg!` for output.** Always use the `tracing` crate:

```rust
use tracing::{debug, info, warn, error, trace};

// Good - structured logging
info!("Processing request for user {user_id}");
debug!("Cache hit: {key}");
warn!("Retry attempt {attempt} of {max_retries}");
error!("Failed to connect: {err}");

// Bad - never do this
println!("Processing request for user {}", user_id);
dbg!(value);
```

**Why:**

- Structured logging with levels (filter noise in production)
- Spans for distributed tracing
- Configurable output (JSON, pretty, etc.)
- Zero-cost when disabled

### Use `test-log` for Tests

Always use `test_log::test` attribute for tests to capture tracing output:

```rust
use test_log::test;

#[test]
fn test_something() {
    info!("This will be visible when test fails or with --nocapture");
    assert!(true);
}

#[test(tokio::test)]
async fn test_async_something() {
    debug!("Async test with tracing");
}
```

Add to `Cargo.toml` (use latest versions):

```toml
[dev-dependencies]
test-log = { version = "*", features = ["trace"] }  # use latest
tracing-subscriber = { version = "*", features = ["env-filter"] }  # use latest
```

Run tests with visible logs: `RUST_LOG=debug cargo test -- --nocapture`

## Clippy Rules to Follow

### Inline Format Arguments (`clippy::uninlined_format_args`)

Always use variables directly in format strings instead of passing them as arguments:

```rust
// Good - variable inlined
let name = "world";
info!("Hello, {name}!");
format!("Value: {value}, Count: {count}")

// Bad - uninlined arguments
info!("Hello, {}!", name);
format!("Value: {}, Count: {}", value, count)
```

This improves readability and reduces potential argument ordering mistakes.

## CI / Quality Gates (Minimum Set)

```bash
cargo fmt --check
cargo clippy --all-targets --all-features -D warnings
cargo test --workspace --all-features
```

**Additional gates:**

- MSRV check (if you claim one)
- `cargo deny` / `cargo audit`
- (optional) `cargo llvm-cov` for coverage, but don't worship %

## Compile Times and Ergonomics

- Use `resolver = "2"` and avoid unnecessary default features
- Split "heavy" crates (like DB codegen, protobuf) into separate crates if they dominate rebuild time
- Prefer incremental-friendly patterns: fewer proc-macros, fewer generics in hot paths unless needed

## Practical Rules of Thumb

**One-way dependencies:**

- `core` → (nothing)
- `adapters` → `core`
- `app` → `adapters` + `core`
- `bin` → `app`

**Visibility:**

- Everything private by default
- Public API is a deliberate design artifact

**IO placement:**

- No IO in `core`

**Test distribution:**

- Unit tests everywhere
- Integration tests at boundaries
- E2E tests sparingly

**Tooling:**

- Pin toolchain
- Centralize versions
- Police features

## Project-Type Patterns

**CLI:** Thin binary → lib (for testability)

**Services:** Separate protocol definitions; feature-flag transport layers

**ZK/crypto:** Isolate no_std core; separate proving/verification crates

**WASM:** Separate bindings; platform-agnostic core
