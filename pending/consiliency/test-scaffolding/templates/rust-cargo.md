# Rust + cargo test Template

Template for generating Rust test scaffolds using the built-in test harness.

## Variables

| Variable | Description |
|----------|-------------|
| `{module_name}` | Module name (e.g., `login`) |
| `{function_name}` | Name of function being tested |
| `{struct_name}` | Name of struct being tested |
| `{method_name}` | Name of method being tested |

## Inline Test Module Template

Rust tests are typically inline in the same file:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    {function_tests}

    {struct_tests}
}
```

## Function Test Template

```rust
    #[test]
    fn test_{function_name}() {
        // TODO: Implement test for {function_name}
        // - Test happy path
        // - Test edge cases
        // - Test error conditions
        todo!("Test not yet implemented")
    }
```

## Async Function Test Template

```rust
    #[tokio::test]
    async fn test_{function_name}() {
        // TODO: Implement test for {function_name}
        // - Test happy path
        // - Test edge cases
        // - Test error conditions
        todo!("Test not yet implemented")
    }
```

## Struct Method Test Template

```rust
    mod {struct_name_snake} {
        use super::*;

        fn setup() -> {StructName} {
            // TODO: Configure instance with appropriate test data
            {StructName}::new()
        }

        #[test]
        fn test_{method_name}() {
            let instance = setup();
            // TODO: Implement this test
            let _ = instance;
            todo!("Test not yet implemented")
        }
    }
```

## Error Test Template

```rust
    #[test]
    fn test_{function_name}_returns_error_on_invalid_input() {
        // TODO: Implement error case test
        let result = {function_name}(/* invalid input */);
        assert!(result.is_err());
    }
```

## Parameterized Test Template

Using `rstest`:

```rust
    use rstest::rstest;

    #[rstest]
    #[case(/* TODO: input */, /* TODO: expected */)]
    #[case(/* TODO: input */, /* TODO: expected */)]
    fn test_{function_name}_parametrized(
        #[case] input: /* TODO: type */,
        #[case] expected: /* TODO: type */,
    ) {
        let result = {function_name}(input);
        assert_eq!(result, expected);
    }
```

## Example Output

Given source file `src/auth/login.rs`:
```rust
pub struct UserSession {
    pub user_id: String,
}

impl UserSession {
    pub fn new(user_id: String) -> Self { ... }

    pub fn refresh(&self) -> bool { ... }

    pub fn invalidate(&mut self) { ... }
}

pub fn authenticate(username: &str, password: &str) -> Result<UserSession, AuthError> { ... }

pub fn logout(session: &UserSession) -> bool { ... }
```

Generated scaffold (appended to `src/auth/login.rs`):
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_authenticate() {
        // TODO: Implement test for authenticate
        // - Test happy path
        // - Test edge cases
        // - Test error conditions
        todo!("Test not yet implemented")
    }

    #[test]
    fn test_logout() {
        // TODO: Implement test for logout
        // - Test happy path
        // - Test edge cases
        // - Test error conditions
        todo!("Test not yet implemented")
    }

    mod user_session {
        use super::*;

        fn setup() -> UserSession {
            // TODO: Configure instance with appropriate test data
            UserSession::new("test-user-id".to_string())
        }

        #[test]
        fn test_refresh() {
            let instance = setup();
            // TODO: Implement this test
            let _ = instance;
            todo!("Test not yet implemented")
        }

        #[test]
        fn test_invalidate() {
            let mut instance = setup();
            // TODO: Implement this test
            let _ = &mut instance;
            todo!("Test not yet implemented")
        }
    }
}
```

## Naming Rules

| Location | Test Location |
|----------|---------------|
| `src/auth/login.rs` | Inline `#[cfg(test)] mod tests` |
| `src/lib.rs` | Inline or `tests/` directory |

## Rust Test Conventions

- Use `#[cfg(test)]` to conditionally compile tests
- Use `#[test]` attribute for test functions
- Use `todo!()` macro for unimplemented tests
- Use `assert!`, `assert_eq!`, `assert_ne!` for assertions
- Use `#[should_panic]` for panic tests
- Use `#[tokio::test]` for async tests with tokio
