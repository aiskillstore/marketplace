---
name: rust-cargo-assistant
description: Cargo build system, crate management, and Rust project configuration assistance.
---

# Rust Cargo and Crate Management Skill

Cargo build system, crate management, and Rust project configuration assistance.

## Instructions

You are a Rust and Cargo ecosystem expert. When invoked:

1. **Cargo Management**:
   - Initialize and configure Cargo projects
   - Manage Cargo.toml and Cargo.lock files
   - Configure build profiles and features
   - Handle workspace and multi-crate projects
   - Use cargo commands effectively

2. **Dependency Management**:
   - Add, update, and remove crates
   - Handle feature flags and optional dependencies
   - Use semantic versioning and version resolution
   - Manage dev, build, and target-specific dependencies
   - Work with path and git dependencies

3. **Project Setup**:
   - Initialize libraries and binaries
   - Configure project structure
   - Set up testing and benchmarking
   - Configure documentation
   - Manage cross-compilation

4. **Troubleshooting**:
   - Fix dependency resolution errors
   - Debug compilation issues
   - Handle version conflicts
   - Clean build artifacts
   - Resolve linker errors

5. **Best Practices**: Provide guidance on Rust project organization, crate publishing, and performance optimization

## Cargo Basics

### Project Initialization
```bash
# Create new binary project
cargo new my-project

# Create new library
cargo new --lib my-lib

# Create project with specific name
cargo new --name my_awesome_project my-project

# Initialize in existing directory
cargo init

# Initialize as library
cargo init --lib

# Project structure created:
# my-project/
# ├── Cargo.toml
# ├── .gitignore
# └── src/
#     └── main.rs  (or lib.rs for library)
```

### Basic Commands
```bash
# Build project
cargo build

# Build with release optimizations
cargo build --release

# Run project
cargo run

# Run with arguments
cargo run -- arg1 arg2

# Run specific binary
cargo run --bin my-binary

# Check code (faster than build)
cargo check

# Run tests
cargo test

# Run benchmarks
cargo bench

# Generate documentation
cargo doc --open

# Format code
cargo fmt

# Lint code
cargo clippy

# Clean build artifacts
cargo clean

# Update dependencies
cargo update

# Search for crates
cargo search tokio

# Install binary
cargo install ripgrep
```

## Usage Examples

```
@rust-cargo-assistant
@rust-cargo-assistant --init-project
@rust-cargo-assistant --add-dependencies
@rust-cargo-assistant --optimize-build
@rust-cargo-assistant --troubleshoot
@rust-cargo-assistant --publish-crate
```

## Cargo.toml Configuration

### Complete Example
```toml
[package]
name = "my-awesome-project"
version = "0.1.0"
edition = "2021"
authors = ["Your Name <email@example.com>"]
description = "A brief description of the project"
documentation = "https://docs.rs/my-awesome-project"
homepage = "https://github.com/user/my-awesome-project"
repository = "https://github.com/user/my-awesome-project"
readme = "README.md"
license = "MIT OR Apache-2.0"
keywords = ["cli", "tool", "utility"]
categories = ["command-line-utilities"]
rust-version = "1.74.0"

[dependencies]
# Regular dependencies
tokio = { version = "1.35", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
clap = { version = "4.4", features = ["derive"] }

# Optional dependencies (feature-gated)
redis = { version = "0.24", optional = true }

[dev-dependencies]
# Test and benchmark dependencies
criterion = "0.5"
mockall = "0.12"
proptest = "1.4"

[build-dependencies]
# Build script dependencies
cc = "1.0"

[features]
# Feature flags
default = ["json"]
json = ["serde_json"]
cache = ["redis"]
full = ["json", "cache"]

[[bin]]
# Binary configuration
name = "my-app"
path = "src/main.rs"

[lib]
# Library configuration
name = "my_lib"
path = "src/lib.rs"
crate-type = ["lib", "cdylib"]  # For FFI

[profile.release]
# Release profile optimization
opt-level = 3
lto = true
codegen-units = 1
strip = true

[profile.dev]
# Development profile
opt-level = 0
debug = true

[workspace]
# Workspace configuration
members = ["crates/*", "examples/*"]
exclude = ["archived/*"]
```

### Dependency Specification
```toml
[dependencies]
# Crates.io dependencies
serde = "1.0"              # ^1.0.0 (latest 1.x)
tokio = "1.35.0"           # ^1.35.0
regex = "~1.10.0"          # >=1.10.0, <1.11.0

# Version operators
reqwest = ">= 0.11, < 0.13"
actix-web = "= 4.4.0"      # Exact version

# Git dependencies
my-lib = { git = "https://github.com/user/my-lib" }
my-lib = { git = "https://github.com/user/my-lib", branch = "main" }
my-lib = { git = "https://github.com/user/my-lib", tag = "v1.0.0" }
my-lib = { git = "https://github.com/user/my-lib", rev = "abc123" }

# Path dependencies (local development)
my-local-lib = { path = "../my-local-lib" }

# Features
tokio = { version = "1.35", features = ["full"] }
serde = { version = "1.0", features = ["derive"], default-features = false }

# Optional dependencies
redis = { version = "0.24", optional = true }

# Renamed dependencies
web-framework = { package = "actix-web", version = "4.4" }

# Platform-specific dependencies
[target.'cfg(windows)'.dependencies]
winapi = "0.3"

[target.'cfg(unix)'.dependencies]
nix = "0.27"

[target.'cfg(target_arch = "wasm32")'.dependencies]
wasm-bindgen = "0.2"
```

## Project Structure Patterns

### Binary Project
```
my-app/
├── Cargo.toml
├── Cargo.lock
├── src/
│   ├── main.rs
│   ├── lib.rs (optional)
│   ├── config.rs
│   └── utils.rs
├── tests/
│   └── integration_test.rs
├── benches/
│   └── benchmark.rs
├── examples/
│   └── example.rs
└── README.md
```

### Library Project
```
my-lib/
├── Cargo.toml
├── src/
│   ├── lib.rs
│   ├── error.rs
│   └── types.rs
├── tests/
│   └── lib_test.rs
├── benches/
│   └── performance.rs
├── examples/
│   └── basic_usage.rs
└── README.md
```

### Workspace Project
```
workspace/
├── Cargo.toml (workspace root)
├── crates/
│   ├── core/
│   │   ├── Cargo.toml
│   │   └── src/lib.rs
│   ├── api/
│   │   ├── Cargo.toml
│   │   └── src/lib.rs
│   └── cli/
│       ├── Cargo.toml
│       └── src/main.rs
├── examples/
│   └── demo/
│       ├── Cargo.toml
│       └── src/main.rs
└── README.md
```

```toml
# Workspace Cargo.toml
[workspace]
members = [
    "crates/core",
    "crates/api",
    "crates/cli",
]

[workspace.package]
edition = "2021"
license = "MIT OR Apache-2.0"
rust-version = "1.74.0"

[workspace.dependencies]
# Shared dependency versions
tokio = { version = "1.35", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
```

## Dependency Management

### Adding Dependencies
```bash
# Add latest version
cargo add serde

# Add with features
cargo add tokio --features full

# Add dev dependency
cargo add --dev proptest

# Add build dependency
cargo add --build cc

# Add optional dependency
cargo add redis --optional

# Add from git
cargo add --git https://github.com/user/repo

# Add specific version
cargo add serde@1.0.193
```

### Updating Dependencies
```bash
# Update all dependencies
cargo update

# Update specific dependency
cargo update serde

# Update to breaking version
cargo upgrade

# Check for outdated dependencies
cargo outdated

# Show dependency tree
cargo tree

# Show dependency tree for specific package
cargo tree -p tokio

# Show duplicate dependencies
cargo tree --duplicates

# Explain why dependency is included
cargo tree -i serde
```

### Managing Features
```toml
[features]
default = ["std"]
std = []
async = ["tokio", "async-trait"]
serde = ["dep:serde", "dep:serde_json"]
full = ["std", "async", "serde"]
```

```bash
# Build with specific features
cargo build --features async

# Build with multiple features
cargo build --features "async,serde"

# Build with all features
cargo build --all-features

# Build with no default features
cargo build --no-default-features

# Build with no default but specific features
cargo build --no-default-features --features std
```

## Build Profiles and Optimization

### Profile Configuration
```toml
[profile.dev]
opt-level = 0              # No optimization
debug = true               # Include debug info
split-debuginfo = "unpacked"
debug-assertions = true
overflow-checks = true
lto = false
panic = 'unwind'
incremental = true
codegen-units = 256

[profile.release]
opt-level = 3              # Maximum optimization
debug = false
strip = true               # Strip symbols
lto = true                 # Link-time optimization
codegen-units = 1          # Better optimization
panic = 'abort'            # Smaller binary

[profile.release-with-debug]
inherits = "release"
debug = true
strip = false

# Custom profile
[profile.production]
inherits = "release"
lto = "fat"
codegen-units = 1
opt-level = 3
```

```bash
# Build with specific profile
cargo build --profile production

# Release build
cargo build --release

# Development build (default)
cargo build
```

### Size Optimization
```toml
[profile.release]
opt-level = "z"            # Optimize for size
lto = true
codegen-units = 1
strip = true
panic = "abort"

[profile.release.package."*"]
opt-level = "z"
```

```bash
# Additional size reduction tools
cargo install cargo-bloat

# Show what's taking space
cargo bloat --release

# Show per-crate sizes
cargo bloat --release --crates

# Use UPX for compression
upx --best --lzma target/release/my-app
```

## Testing and Benchmarking

### Testing
```rust
// src/lib.rs
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 2), 4);
    }

    #[test]
    #[should_panic]
    fn test_panic() {
        panic!("This test should panic");
    }

    #[test]
    #[ignore]
    fn expensive_test() {
        // Long-running test
    }
}
```

```bash
# Run all tests
cargo test

# Run specific test
cargo test test_add

# Run tests matching pattern
cargo test add

# Run ignored tests
cargo test -- --ignored

# Run with output
cargo test -- --nocapture

# Run tests in single thread
cargo test -- --test-threads=1

# Run doc tests
cargo test --doc

# Run integration tests
cargo test --test integration_test
```

### Integration Tests
```rust
// tests/integration_test.rs
use my_lib::add;

#[test]
fn integration_test() {
    assert_eq!(add(5, 5), 10);
}
```

### Benchmarking with Criterion
```toml
[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "my_benchmark"
harness = false
```

```rust
// benches/my_benchmark.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};
use my_lib::add;

fn benchmark_add(c: &mut Criterion) {
    c.bench_function("add", |b| {
        b.iter(|| add(black_box(5), black_box(5)))
    });
}

criterion_group!(benches, benchmark_add);
criterion_main!(benches);
```

```bash
# Run benchmarks
cargo bench

# Run specific benchmark
cargo bench benchmark_add

# Save baseline
cargo bench -- --save-baseline main

# Compare to baseline
cargo bench -- --baseline main
```

## Common Issues & Solutions

### Issue: Linker Errors
```bash
# Error: linking with `cc` failed

# Solution: Install C compiler
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS (install Xcode Command Line Tools)
xcode-select --install

# Windows (install Visual Studio Build Tools)
# Or use rustup:
rustup toolchain install stable-x86_64-pc-windows-gnu
```

### Issue: Dependency Version Conflicts
```bash
# Check dependency tree
cargo tree

# See all versions of a package
cargo tree -i serde

# Force specific version in Cargo.toml
[dependencies]
serde = "=1.0.193"  # Exact version

# Or use workspace to unify versions
[workspace.dependencies]
serde = "1.0"
```

### Issue: Slow Compilation
```bash
# Use sccache for caching
cargo install sccache
export RUSTC_WRAPPER=sccache

# Add to Cargo.toml
[profile.dev]
incremental = true

# Use mold linker (Linux)
sudo apt install mold
export RUSTFLAGS="-C link-arg=-fuse-ld=mold"

# Or add to .cargo/config.toml
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]

# Reduce codegen units in dev
[profile.dev]
codegen-units = 128  # Default is 256
```

### Issue: Cargo.lock Conflicts
```bash
# Regenerate lock file
rm Cargo.lock
cargo build

# Update specific dependency
cargo update -p serde

# For libraries: don't commit Cargo.lock
echo "Cargo.lock" >> .gitignore

# For binaries: always commit Cargo.lock
```

### Issue: Out of Disk Space
```bash
# Clean build artifacts
cargo clean

# Clean all projects
cargo cache --autoclean

# Install cargo-cache
cargo install cargo-cache

# Clean registry cache
cargo cache -a
```

## Cross-Compilation

### Setup Target
```bash
# List installed targets
rustup target list --installed

# Add target
rustup target add x86_64-unknown-linux-musl
rustup target add x86_64-pc-windows-gnu
rustup target add aarch64-unknown-linux-gnu

# Build for target
cargo build --target x86_64-unknown-linux-musl
```

### Cross-Compilation Configuration
```toml
# .cargo/config.toml
[target.x86_64-unknown-linux-musl]
linker = "x86_64-linux-musl-gcc"

[target.aarch64-unknown-linux-gnu]
linker = "aarch64-linux-gnu-gcc"
```

### Using Cross
```bash
# Install cross
cargo install cross

# Build with cross
cross build --target x86_64-unknown-linux-musl
cross build --target aarch64-unknown-linux-gnu

# Cross supports many targets out of the box
cross build --target armv7-unknown-linux-gnueabihf
```

## Publishing to Crates.io

### Prepare for Publishing
```toml
[package]
name = "my-crate"
version = "0.1.0"
edition = "2021"
authors = ["Your Name <email@example.com>"]
description = "A brief description (required)"
license = "MIT OR Apache-2.0"
repository = "https://github.com/user/my-crate"
documentation = "https://docs.rs/my-crate"
homepage = "https://github.com/user/my-crate"
readme = "README.md"
keywords = ["cli", "tool"]  # Max 5
categories = ["command-line-utilities"]  # From crates.io list

# Exclude files from package
exclude = [
    "tests/*",
    "examples/*",
    ".github/*",
    "*.sh",
]

# Or specify what to include
include = [
    "src/**/*",
    "Cargo.toml",
    "README.md",
    "LICENSE*",
]
```

### Publishing Workflow
```bash
# Login to crates.io
cargo login <your-api-token>

# Check package before publishing
cargo package

# List files that will be published
cargo package --list

# Test package
cargo package --verify

# Publish (dry run first)
cargo publish --dry-run

# Publish for real
cargo publish

# Yank a version (remove from new dependencies)
cargo yank --vers 0.1.0

# Un-yank a version
cargo yank --vers 0.1.0 --undo
```

### Versioning Strategy
```bash
# Update version
# In Cargo.toml, update version field

# Breaking changes (0.1.0 -> 1.0.0)
# Major version bump

# New features (1.0.0 -> 1.1.0)
# Minor version bump

# Bug fixes (1.1.0 -> 1.1.1)
# Patch version bump

# Pre-release versions
0.1.0-alpha.1
0.1.0-beta.1
0.1.0-rc.1
```

## Useful Cargo Tools

### cargo-edit
```bash
# Install
cargo install cargo-edit

# Add dependency
cargo add serde

# Remove dependency
cargo rm serde

# Upgrade dependencies
cargo upgrade
```

### cargo-watch
```bash
# Install
cargo install cargo-watch

# Watch and rebuild on changes
cargo watch

# Watch and run tests
cargo watch -x test

# Watch and run
cargo watch -x run

# Clear screen on each run
cargo watch -c -x run
```

### cargo-expand
```bash
# Install
cargo install cargo-expand

# Expand macros
cargo expand

# Expand specific module
cargo expand module::path
```

### cargo-audit
```bash
# Install
cargo install cargo-audit

# Audit dependencies for security vulnerabilities
cargo audit

# Fix vulnerabilities
cargo audit fix
```

### cargo-outdated
```bash
# Install
cargo install cargo-outdated

# Check for outdated dependencies
cargo outdated

# Show detailed information
cargo outdated -v
```

### cargo-tarpaulin (Code Coverage)
```bash
# Install
cargo install cargo-tarpaulin

# Generate coverage report
cargo tarpaulin --out Html

# With verbose output
cargo tarpaulin --verbose --out Html
```

## Advanced Cargo Features

### Build Scripts
```toml
[package]
build = "build.rs"

[build-dependencies]
cc = "1.0"
```

```rust
// build.rs
fn main() {
    // Compile C code
    cc::Build::new()
        .file("src/native/foo.c")
        .compile("foo");

    // Emit cargo directives
    println!("cargo:rerun-if-changed=src/native/foo.c");
    println!("cargo:rustc-link-lib=static=foo");
}
```

### Cargo Aliases
```toml
# .cargo/config.toml
[alias]
b = "build"
c = "check"
t = "test"
r = "run"
rr = "run --release"
br = "build --release"
wr = "watch -x run"
```

```bash
# Use aliases
cargo b     # Same as cargo build
cargo rr    # Same as cargo run --release
```

### Environment Variables
```bash
# Offline mode
cargo build --offline

# Custom registry
export CARGO_REGISTRY_DEFAULT=my-registry

# Custom target directory
export CARGO_TARGET_DIR=/tmp/cargo-target

# Additional rustc flags
export RUSTFLAGS="-C target-cpu=native"

# Build jobs
export CARGO_BUILD_JOBS=4
```

## Best Practices Summary

### Project Organization
- Use workspaces for multi-crate projects
- Keep src/ for source code
- Use tests/ for integration tests
- Use benches/ for benchmarks
- Use examples/ for usage examples
- Include comprehensive README.md

### Dependency Management
- Use semantic versioning
- Commit Cargo.lock for binaries
- Don't commit Cargo.lock for libraries
- Minimize dependencies
- Use features for optional functionality
- Audit dependencies regularly

### Performance
- Use release profile for production
- Enable LTO for smaller binaries
- Consider codegen-units = 1 for optimization
- Use cargo-bloat to analyze binary size
- Profile before optimizing

### Testing
- Write unit tests in each module
- Write integration tests in tests/
- Use doc tests for examples
- Aim for high test coverage
- Run tests in CI/CD

### Publishing
- Follow semver strictly
- Document breaking changes
- Include examples in documentation
- Choose appropriate keywords and categories
- Test package before publishing
- Maintain CHANGELOG.md

## Quick Reference Commands

```bash
# Project management
cargo new <name>              # Create new project
cargo init                    # Initialize in current dir
cargo build                   # Build project
cargo run                     # Build and run
cargo check                   # Check without building

# Dependencies
cargo add <crate>             # Add dependency
cargo update                  # Update dependencies
cargo tree                    # Show dependency tree

# Testing and quality
cargo test                    # Run tests
cargo bench                   # Run benchmarks
cargo fmt                     # Format code
cargo clippy                  # Lint code
cargo doc --open              # Generate and open docs

# Maintenance
cargo clean                   # Clean build artifacts
cargo publish                 # Publish to crates.io
cargo install <crate>         # Install binary

# Advanced
cargo build --release         # Optimized build
cargo build --target <target> # Cross-compile
cargo package                 # Create package for publishing
```

## Notes

- Always commit Cargo.lock for binaries and applications
- Use workspaces to share dependencies across crates
- Enable LTO and optimize codegen-units for production
- Run cargo clippy regularly for better code quality
- Use cargo fmt to maintain consistent style
- Audit dependencies for security vulnerabilities
- Test on multiple platforms before releasing
- Follow semantic versioning strictly
- Document all public APIs thoroughly
- Use features for optional functionality
