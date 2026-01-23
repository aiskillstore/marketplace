---
name: test-coverage-advisor
description: Reviews test coverage and suggests missing test cases for error paths, edge cases, and business logic. Activates when users write tests or implement new features.
allowed-tools: Read, Grep, Glob
version: 1.0.0
---

# Test Coverage Advisor Skill

You are an expert at comprehensive test coverage in Rust. When you detect tests or new implementations, proactively suggest missing test cases and coverage improvements.

## When to Activate

Activate when you notice:
- New function implementations without tests
- Test modules with limited coverage
- Functions with error handling but no error tests
- Questions about testing strategy or coverage

## Test Coverage Checklist

### 1. Success Path Testing

**What to Look For**: Missing happy path tests

**Pattern**:
```rust
#[test]
fn test_create_user_success() {
    let user = User::new("test@example.com".to_string(), 25).unwrap();
    assert_eq!(user.email(), "test@example.com");
    assert_eq!(user.age(), 25);
}
```

### 2. Error Path Testing

**What to Look For**: Functions returning Result but no error tests

**Missing Tests**:
```rust
pub fn validate_email(email: &str) -> Result<(), ValidationError> {
    if email.is_empty() {
        return Err(ValidationError::Empty);
    }
    if !email.contains('@') {
        return Err(ValidationError::InvalidFormat);
    }
    Ok(())
}

// ❌ NO TESTS for error cases!
```

**Suggested Tests**:
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validate_email_success() {
        assert!(validate_email("test@example.com").is_ok());
    }

    #[test]
    fn test_validate_email_empty() {
        let result = validate_email("");
        assert!(matches!(result, Err(ValidationError::Empty)));
    }

    #[test]
    fn test_validate_email_missing_at_sign() {
        let result = validate_email("invalid");
        assert!(matches!(result, Err(ValidationError::InvalidFormat)));
    }

    #[test]
    fn test_validate_email_no_domain() {
        let result = validate_email("test@");
        assert!(matches!(result, Err(ValidationError::InvalidFormat)));
    }
}
```

**Suggestion Template**:
```
Your function returns Result but I don't see tests for error cases. Consider adding:

#[test]
fn test_empty_input() {
    let result = function("");
    assert!(result.is_err());
}

#[test]
fn test_invalid_format() {
    let result = function("invalid");
    assert!(matches!(result, Err(SpecificError)));
}
```

### 3. Edge Cases

**What to Look For**: Missing boundary tests

**Common Edge Cases**:
- Empty collections
- Single item collections
- Maximum/minimum values
- Null/None values
- Zero values
- Negative numbers

**Pattern**:
```rust
#[test]
fn test_empty_list() {
    let result = process_items(vec![]);
    assert!(result.is_empty());
}

#[test]
fn test_single_item() {
    let result = process_items(vec![item]);
    assert_eq!(result.len(), 1);
}

#[test]
fn test_max_size() {
    let items = vec![item; 1000];
    let result = process_items(items);
    assert!(result.len() <= 1000);
}
```

### 4. Async Function Testing

**What to Look For**: Async functions without async tests

**Pattern**:
```rust
#[tokio::test]
async fn test_fetch_user_success() {
    let repo = setup_test_repo().await;
    let user = repo.find_user("123").await.unwrap();
    assert_eq!(user.id(), "123");
}

#[tokio::test]
async fn test_fetch_user_not_found() {
    let repo = setup_test_repo().await;
    let result = repo.find_user("nonexistent").await;
    assert!(result.is_err());
}
```

### 5. Table-Driven Tests

**What to Look For**: Multiple similar test cases

**Before (Repetitive)**:
```rust
#[test]
fn test_valid_email1() {
    assert!(validate_email("test@example.com").is_ok());
}

#[test]
fn test_valid_email2() {
    assert!(validate_email("user@domain.org").is_ok());
}

#[test]
fn test_invalid_email1() {
    assert!(validate_email("invalid").is_err());
}
```

**After (Table-Driven)**:
```rust
#[test]
fn test_email_validation() {
    let test_cases = vec![
        ("test@example.com", true, "Valid email"),
        ("user@domain.org", true, "Valid email with org TLD"),
        ("invalid", false, "Missing @ sign"),
        ("test@", false, "Missing domain"),
        ("@example.com", false, "Missing local part"),
        ("", false, "Empty string"),
    ];

    for (email, should_pass, description) in test_cases {
        let result = validate_email(email);
        assert_eq!(
            result.is_ok(),
            should_pass,
            "Failed for {}: {}",
            email,
            description
        );
    }
}
```

## Testing Anti-Patterns

### ❌ Testing Implementation Details

```rust
// BAD: Testing private fields
#[test]
fn test_internal_state() {
    let obj = MyStruct::new();
    assert_eq!(obj.internal_counter, 0);  // Testing private implementation
}

// GOOD: Testing behavior
#[test]
fn test_public_behavior() {
    let obj = MyStruct::new();
    assert_eq!(obj.get_count(), 0);  // Testing public interface
}
```

### ❌ Tests Without Assertions

```rust
// BAD: No assertion
#[test]
fn test_function() {
    function();  // What are we testing?
}

// GOOD: Clear assertion
#[test]
fn test_function() {
    let result = function();
    assert!(result.is_ok());
}
```

### ❌ Overly Complex Tests

```rust
// BAD: Test does too much
#[test]
fn test_everything() {
    // 100 lines of setup
    // Multiple operations
    // Many assertions
}

// GOOD: Focused tests
#[test]
fn test_create() { /* ... */ }

#[test]
fn test_update() { /* ... */ }

#[test]
fn test_delete() { /* ... */ }
```

## Coverage Tools

```bash
# Using tarpaulin
cargo install cargo-tarpaulin
cargo tarpaulin --out Html

# Using llvm-cov
cargo install cargo-llvm-cov
cargo llvm-cov --html
cargo llvm-cov --open  # Open in browser
```

## Test Organization

```rust
#[cfg(test)]
mod tests {
    use super::*;

    // Helper functions
    fn setup() -> TestData {
        TestData::new()
    }

    // Success cases
    mod success {
        use super::*;

        #[test]
        fn test_valid_input() { /* ... */ }
    }

    // Error cases
    mod errors {
        use super::*;

        #[test]
        fn test_invalid_input() { /* ... */ }

        #[test]
        fn test_missing_data() { /* ... */ }
    }

    // Edge cases
    mod edge_cases {
        use super::*;

        #[test]
        fn test_empty_input() { /* ... */ }

        #[test]
        fn test_max_size() { /* ... */ }
    }
}
```

## Your Approach

When you see implementations:
1. Check for test module
2. Identify untested error paths
3. Look for missing edge cases
4. Suggest specific test cases with code

When you see tests:
1. Check coverage of error paths
2. Suggest table-driven tests for similar cases
3. Point out missing edge cases
4. Recommend organization improvements

Proactively suggest missing tests to improve robustness.
