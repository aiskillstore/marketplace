# Rust dialect

How the universal core is spelled in Rust, plus Rust-specific idioms. Distilled
from the Rust API Guidelines, the Performance Book, and production crates
(ripgrep, tokio, serde, axum).

## Tooling baseline

```sh
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test
```

Lints worth setting at the crate/workspace root:

```rust
#![warn(clippy::all, clippy::pedantic)]   // pedantic selectively; allow the noisy ones
#![deny(clippy::correctness)]
#![warn(missing_docs)]                      // for libraries
```

Deny `clippy::inline_always` and `clippy::unnecessary_wraps` (the latter catches
functions that claim fallibility they do not have). Configure lints in
`Cargo.toml` `[lints]` for a workspace.

## Illegal states (core 1, 4)

- **Newtypes with private fields + smart constructors.** Not
  `pub struct UserId(pub String)` (a public field is a trapdoor). Use a private
  field and a constructor that parses:
  ```rust
  pub struct Email(String);
  impl Email {
      pub fn parse(raw: &str) -> Result<Self, EmailError> { /* check, then wrap */ }
      pub fn as_str(&self) -> &str { &self.0 }
  }
  ```
- **Enums for states.** Model mutually exclusive states as an `enum` with data on
  the variant. Use `#[non_exhaustive]` on public enums/structs you may extend.
- **Typestate** for compile-time state machines (a builder that only exposes
  `.build()` once required fields are set), `PhantomData` for type-level markers.
- **Do not derive your way around an invariant.** Be careful with `From`,
  `Deref`/`DerefMut`, and `#[serde(...)]` on checked types; deserialization can
  reconstruct an invalid value unless it goes through the parser (use
  `#[serde(try_from = "Raw")]`).
- Wrap IDs and units: `OrderId(u64)`, `Cents(i64)`. `#[repr(transparent)]` for
  FFI-safe newtypes.

## Parse, don't validate (core 2)

- Raw serde structs at the boundary, a checked domain type inside, a parser
  between. Name the checked form: `CheckedConfig`, `VerifiedPlan`.
- Return the parsed value, not `Result<(), E>`. `clippy::unnecessary_wraps`
  helps; treat `parse* -> Result<()>` and `validate* -> Result<()>` as smells.
- Accept the most general input: `&str` not `&String`, `&[T]` not `&Vec<T>`,
  `impl AsRef<Path>` for paths, `impl Into<String>` where you will own a string.

## Errors (core 3)

- **Libraries:** typed errors with `thiserror`, one enum of failure modes,
  `#[from]` for conversions, `#[source]` to chain. Document them with a
  `# Errors` section.
- **Applications / top level:** `anyhow` (or `color_eyre`), `.context(...)` /
  `.with_context(...)` as the error propagates, `?` for propagation.
- **Bugs only:** `.expect("invariant: ...")` for things that cannot happen;
  never `.unwrap()` in production paths. `panic!`/`unreachable!` for genuine
  invariant violations, with a message.
- **Fail closed:** a gate that errors or times out returns the block verdict, not
  a default pass.
- Error messages: lowercase, no trailing period.

## Ownership and copies (core 5)

- Borrow over clone; clone only when you need owned data (storage, `'static` for
  a spawned task) and make it explicit.
- `Cow<'a, T>` for conditional ownership (borrow the common case, own only when
  you must mutate). `Arc<T>` for shared ownership across threads, `Rc<T>`
  single-threaded.
- Interior mutability: `Mutex`/`RwLock` (multi-thread), `RefCell` (single).
  `RwLock` when reads dominate.
- `with_capacity` when the size is known; reuse buffers with `clear()` in loops;
  `write!` into a buffer instead of `format!` in hot paths. `SmallVec`/`ArrayVec`
  for usually-small collections. Box large enum variants so the enum is not sized
  to its biggest case.
- Prefer iterators over manual indexing (avoids bounds checks, clearer); keep
  them lazy, `collect()` once at the end.

## Async (Rust-specific)

- Tokio for production. **Never hold a `Mutex`/`RwLock` guard across `.await`**
  (clippy `await_holding_lock`): clone the needed data and drop the guard first,
  or use `tokio::sync` primitives deliberately.
- `tokio::join!` for parallel awaits, `try_join!` when fallible, `select!` for
  racing/timeouts, `JoinSet` for dynamic task groups. `spawn_blocking` for CPU
  work or sync IO. `tokio::fs` not `std::fs` in async code.
- Channels: bounded `mpsc` for backpressure, `oneshot` for request/response,
  `watch` for latest-value, `broadcast` for pub/sub. `CancellationToken` for
  shutdown.

## Naming

`UpperCamelCase` types/traits/variants, `snake_case` fns/methods/modules,
`SCREAMING_SNAKE_CASE` consts. Conversions: `as_` (cheap borrow), `to_`
(expensive), `into_` (consumes). No `get_` prefix on simple getters. `is_`/`has_`
for booleans. Acronyms as words (`Uuid`, not `UUID`). Crates: no `-rs` suffix.

## Project structure

Keep `main.rs` thin, logic in `lib.rs`. Modules by feature, not by type. Flat
while small. `pub(crate)`/`pub(super)` for internal visibility, `pub use` to
curate the public surface. Workspaces for large multi-crate projects with shared
`[workspace.dependencies]`.

## Testing (core 6)

- Inline `#[cfg(test)] mod tests { use super::*; }` while a module is small;
  migrate a large test body to a sibling `tests.rs` (`#[cfg(test)] mod tests;`)
  if test edits start forcing library recompiles.
- `#[tokio::test]` for async, `#[should_panic]` for panic paths.
- No mocks. Real pure functions, `tempfile` dirs, throwaway `git init` repos,
  `sqlx::test` for Postgres. A deterministic in-memory implementation of a trait
  is fine; recording mocks are not.
- `proptest` for properties, `criterion` with `black_box` for benchmarks. Keep
  doctests runnable (use `?` in examples, `#` to hide setup lines).
- For internal apps prefer `src/` unit tests over many `tests/*.rs` binaries; use
  at most one modular integration crate for a real external boundary.

## Docs

`///` on public items, `//!` for module docs. `# Examples` (runnable),
`# Errors`, `# Panics`, `# Safety` (for `unsafe`) sections. Intra-doc links
(`[Vec]`). Document every `unsafe` block with a `// SAFETY:` comment
(`clippy::undocumented_unsafe_blocks`).

## Anti-patterns to refuse

`.unwrap()`/`.expect()` on recoverable errors; cloning where a borrow works;
holding a lock across `.await`; `&String`/`&Vec<T>` in signatures; indexing where
an iterator reads cleaner; `panic!` on expected errors; empty `if let Err(_) =`;
`Box<dyn Trait>` where `impl Trait` works; stringly-typed data; `format!` in hot
paths; over-generic abstractions with one caller.

## Release profile (for performance-sensitive binaries)

```toml
[profile.release]
opt-level = 3
lto = "fat"
codegen-units = 1
strip = true
```
