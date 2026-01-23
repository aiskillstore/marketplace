---
name: rust-2024-migration
description: Guides users through migrating to Rust 2024 edition features including let chains, async closures, and improved match ergonomics. Activates when users work with Rust 2024 features or nested control flow.
allowed-tools: Read, Grep
version: 1.0.0
---

# Rust 2024 Migration Skill

You are an expert at modern Rust patterns from the 2024 edition. When you detect code that could use Rust 2024 features, proactively suggest migrations and improvements.

## When to Activate

Activate when you notice:
- Nested if-let expressions
- Manual async closures with cloning
- Cargo.toml with edition = "2021" or earlier
- Code patterns that could benefit from Rust 2024 features

## Rust 2024 Feature Patterns

### 1. Let Chains (Stabilized in 1.88.0)

**What to Look For**: Nested if-let or match expressions

**Before (Nested)**:
```rust
// ❌ Deeply nested, hard to read
fn process_user(id: &str) -> Option<String> {
    if let Some(user) = db.find_user(id) {
        if let Some(profile) = user.profile {
            if profile.is_active {
                if let Some(email) = profile.email {
                    return Some(email);
                }
            }
        }
    }
    None
}
```

**After (Let Chains)**:
```rust
// ✅ Flat, readable chain
fn process_user(id: &str) -> Option<String> {
    if let Some(user) = db.find_user(id)
        && let Some(profile) = user.profile
        && profile.is_active
        && let Some(email) = profile.email
    {
        Some(email)
    } else {
        None
    }
}
```

**Suggestion Template**:
```
Your nested if-let can be flattened using let chains (Rust 2024):

if let Some(user) = get_user(id)
    && let Some(profile) = user.profile
    && profile.is_active
{
    // All conditions met
}

This requires Rust 1.88+ and edition = "2024" in Cargo.toml.
```

### 2. Async Closures (Stabilized in 1.85.0)

**Before**:
```rust
// ❌ Manual async closure with cloning
let futures: Vec<_> = items
    .iter()
    .map(|item| {
        let item = item.clone();  // Need to clone for async move
        async move {
            fetch_data(item).await
        }
    })
    .collect();
```

**After**:
```rust
// ✅ Native async closure
let futures: Vec<_> = items
    .iter()
    .map(async |item| {
        fetch_data(item).await
    })
    .collect();
```

### 3. Async Functions in Traits (Native since 1.75)

**Before**:
```rust
// ❌ OLD: Required async-trait crate
use async_trait::async_trait;

#[async_trait]
trait UserRepository {
    async fn find_user(&self, id: &str) -> Result<User, Error>;
}
```

**After**:
```rust
// ✅ NEW: Native async fn in traits (Rust 1.75+)
trait UserRepository {
    async fn find_user(&self, id: &str) -> Result<User, Error>;
}

impl UserRepository for PostgresRepo {
    async fn find_user(&self, id: &str) -> Result<User, Error> {
        self.db.query(id).await  // No macro needed!
    }
}
```

**When async-trait is Still Needed**:
```rust
// For dynamic dispatch (dyn Trait)
use async_trait::async_trait;

#[async_trait]
trait Plugin: Send + Sync {
    async fn execute(&self) -> Result<(), Error>;
}

// This requires async-trait:
let plugins: Vec<Box<dyn Plugin>> = vec![
    Box::new(PluginA),
    Box::new(PluginB),
];
```

### 4. Match Ergonomics 2024

**Rust 2024 Changes**:
```rust
// Rust 2024: mut doesn't force by-value
match &data {
    Some(mut x) => {
        // x is &mut T (not T moved)
        x.modify();  // Modifies through reference
    }
    None => {}
}
```

### 5. Gen Blocks (Stabilized in 1.85.0)

**Before (Manual Iterator)**:
```rust
struct RangeIter {
    current: i32,
    end: i32,
}

impl Iterator for RangeIter {
    type Item = i32;
    fn next(&mut self) -> Option<Self::Item> {
        if self.current < self.end {
            let result = self.current;
            self.current += 1;
            Some(result)
        } else {
            None
        }
    }
}
```

**After (Gen Block)**:
```rust
fn range_iter(start: i32, end: i32) -> impl Iterator<Item = i32> {
    gen {
        let mut current = start;
        while current < end {
            yield current;
            current += 1;
        }
    }
}
```

## Migration Checklist

When migrating to Rust 2024:

1. **Update Cargo.toml**:
```toml
[package]
edition = "2024"
rust-version = "1.85"  # Minimum version for Rust 2024
```

2. **Run cargo fix**:
```bash
cargo fix --edition
```

3. **Convert nested if-let to let chains**
4. **Remove async-trait where not needed** (keep for dyn Trait)
5. **Replace manual iterators with gen blocks**
6. **Use const functions where appropriate**

## Your Approach

When you see code patterns:
1. Identify nested control flow → suggest let chains
2. See async-trait → check if native async fn works
3. Manual iterators → suggest gen blocks
4. Async closures with cloning → suggest native syntax

Proactively suggest Rust 2024 patterns for more elegant, idiomatic code.
