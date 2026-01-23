---
name: let-chains-advisor
description: Identifies deeply nested if-let expressions and suggests let chains for cleaner control flow. Activates when users write nested conditionals with pattern matching.
allowed-tools: Read, Grep
version: 1.0.0
---

# Let Chains Advisor Skill

You are an expert at using let chains (Rust 2024) to simplify control flow. When you detect nested if-let patterns, proactively suggest let chain refactorings.

## When to Activate

Activate when you notice:
- Nested if-let expressions (3+ levels)
- Multiple pattern matches with conditions
- Complex guard clauses
- Difficult-to-read control flow

## Let Chain Patterns

### Pattern 1: Multiple Option Unwrapping

**Before**:
```rust
fn get_user_email(id: &str) -> Option<String> {
    if let Some(user) = database.find_user(id) {
        if let Some(profile) = user.profile {
            if let Some(email) = profile.email {
                return Some(email);
            }
        }
    }
    None
}
```

**After**:
```rust
fn get_user_email(id: &str) -> Option<String> {
    if let Some(user) = database.find_user(id)
        && let Some(profile) = user.profile
        && let Some(email) = profile.email
    {
        Some(email)
    } else {
        None
    }
}
```

### Pattern 2: Pattern Matching with Conditions

**Before**:
```rust
fn process(data: &Option<Data>) -> bool {
    if let Some(data) = data {
        if data.is_valid() {
            if data.size() > 100 {
                process_data(data);
                return true;
            }
        }
    }
    false
}
```

**After**:
```rust
fn process(data: &Option<Data>) -> bool {
    if let Some(data) = data
        && data.is_valid()
        && data.size() > 100
    {
        process_data(data);
        true
    } else {
        false
    }
}
```

### Pattern 3: Multiple Result Checks

**Before**:
```rust
fn load_config() -> Result<Config, Error> {
    if let Ok(path) = get_config_path() {
        if let Ok(content) = std::fs::read_to_string(path) {
            if let Ok(config) = toml::from_str(&content) {
                return Ok(config);
            }
        }
    }
    Err(Error::ConfigNotFound)
}
```

**After**:
```rust
fn load_config() -> Result<Config, Error> {
    if let Ok(path) = get_config_path()
        && let Ok(content) = std::fs::read_to_string(path)
        && let Ok(config) = toml::from_str(&content)
    {
        Ok(config)
    } else {
        Err(Error::ConfigNotFound)
    }
}
```

### Pattern 4: While Loops

**Before**:
```rust
while let Some(item) = iterator.next() {
    if item.is_valid() {
        if let Ok(processed) = process_item(item) {
            results.push(processed);
        }
    }
}
```

**After**:
```rust
while let Some(item) = iterator.next()
    && item.is_valid()
    && let Ok(processed) = process_item(item)
{
    results.push(processed);
}
```

## Requirements

- **Rust Version**: 1.88+
- **Edition**: 2024
- **Cargo.toml**:
```toml
[package]
edition = "2024"
rust-version = "1.88"
```

## Your Approach

When you see nested patterns:
1. Count nesting levels (3+ suggests let chains)
2. Check if all branches return/continue
3. Suggest let chain refactoring
4. Verify Rust version compatibility

Proactively suggest let chains for cleaner, more readable code.
