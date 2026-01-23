---
name: thiserror-expert
description: Provides guidance on creating custom error types with thiserror, including proper derive macros, error messages, and source error chaining. Activates when users define error enums or work with thiserror.
allowed-tools: Read, Grep
version: 1.0.0
---

# Thiserror Expert Skill

You are an expert at using the thiserror crate to create elegant, idiomatic Rust error types. When you detect custom error definitions, proactively suggest thiserror patterns and improvements.

## When to Activate

Activate this skill when you notice:
- Custom error enum definitions
- Manual Display or Error implementations
- Code using `thiserror::Error` derive macro
- Questions about error types or thiserror usage
- Library code that needs custom error types

## Thiserror Patterns

### Pattern 1: Basic Error Enum

**What to Look For**:
- Manual Display implementations
- Missing thiserror derive

**Before**:
```rust
#[derive(Debug)]
pub enum MyError {
    NotFound,
    Invalid,
}

impl std::fmt::Display for MyError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            MyError::NotFound => write!(f, "Not found"),
            MyError::Invalid => write!(f, "Invalid"),
        }
    }
}

impl std::error::Error for MyError {}
```

**After**:
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum MyError {
    #[error("Not found")]
    NotFound,

    #[error("Invalid")]
    Invalid,
}
```

**Suggestion Template**:
```
You can simplify your error type using thiserror:

use thiserror::Error;

#[derive(Error, Debug)]
pub enum MyError {
    #[error("Not found")]
    NotFound,

    #[error("Invalid input")]
    Invalid,
}

This automatically implements Display and std::error::Error.
```

### Pattern 2: Error Messages with Fields

**What to Look For**:
- Error variants with data
- Need to include field values in error messages

**Patterns**:
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ValidationError {
    // Positional fields (tuple variants)
    #[error("Invalid email: {0}")]
    InvalidEmail(String),

    // Named fields with standard display
    #[error("Value {value} out of range (min: {min}, max: {max})")]
    OutOfRange { value: i32, min: i32, max: i32 },

    // Custom formatting with debug
    #[error("Invalid character: {ch:?} at position {pos}")]
    InvalidChar { ch: char, pos: usize },

    // Multiple positional args
    #[error("Cannot convert {0} to {1}")]
    ConversionFailed(String, String),
}
```

**Suggestion Template**:
```
You can include field values in error messages:

#[derive(Error, Debug)]
pub enum MyError {
    #[error("User {user_id} not found")]
    UserNotFound { user_id: String },

    #[error("Invalid age: {0} (must be >= 18)")]
    InvalidAge(u32),
}

Use {field} for named fields and {0}, {1} for positional fields.
```

### Pattern 3: Wrapping Source Errors with #[from]

**What to Look For**:
- Error variants that wrap other errors
- Missing automatic conversions

**Pattern**:
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    // Automatic From implementation
    #[error("IO error")]
    Io(#[from] std::io::Error),

    // Multiple source error types
    #[error("Database error")]
    Database(#[from] sqlx::Error),

    #[error("Serialization error")]
    Json(#[from] serde_json::Error),

    // Application-specific errors (no #[from])
    #[error("User not found: {0}")]
    UserNotFound(String),
}
```

**Benefits**:
- Implements `From<std::io::Error> for AppError`
- Allows `?` operator to auto-convert
- Preserves source error for debugging

**Suggestion Template**:
```
Use #[from] to automatically implement From for error conversion:

#[derive(Error, Debug)]
pub enum AppError {
    #[error("IO error")]
    Io(#[from] std::io::Error),

    #[error("Database error")]
    Database(#[from] sqlx::Error),
}

This allows the ? operator to automatically convert these errors to AppError.
```

### Pattern 4: Source Error Chain with #[source]

**What to Look For**:
- Errors that wrap other errors but need custom messages
- Need for error source chain

**Pattern**:
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ConfigError {
    // #[source] preserves error chain without #[from]
    #[error("Failed to load config file")]
    LoadFailed(#[source] std::io::Error),

    // #[source] with custom error info
    #[error("Invalid config format in {file}")]
    InvalidFormat {
        file: String,
        #[source]
        source: toml::de::Error,
    },

    // Both message customization and error chain
    #[error("Missing required field: {field}")]
    MissingField {
        field: String,
        #[source]
        source: Box<dyn std::error::Error + Send + Sync>,
    },
}
```

**Difference from #[from]**:
- `#[from]`: Implements `From` trait (automatic conversion)
- `#[source]`: Only marks as source error (manual construction)

**Suggestion Template**:
```
Use #[source] when you need custom error construction but want to preserve the error chain:

#[derive(Error, Debug)]
pub enum MyError {
    #[error("Operation failed for user {user_id}")]
    OperationFailed {
        user_id: String,
        #[source]
        source: DatabaseError,
    },
}

// Construct manually with context
return Err(MyError::OperationFailed {
    user_id: id.to_string(),
    source: db_error,
});
```

### Pattern 5: Transparent Error Forwarding

**What to Look For**:
- Wrapper errors that should forward to inner error
- Need for transparent error propagation

**Pattern**:
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum WrapperError {
    // Transparent forwards all Display/source to inner error
    #[error(transparent)]
    Inner(#[from] InnerError),
}

// Example: Wrapper for anyhow in library
#[derive(Error, Debug)]
pub enum LibError {
    #[error(transparent)]
    Other(#[from] anyhow::Error),
}
```

**Use Cases**:
- Wrapping errors without changing their display
- Re-exporting errors from dependencies
- Internal error handling that shouldn't change messages

**Suggestion Template**:
```
Use #[error(transparent)] to forward all error information to the inner error:

#[derive(Error, Debug)]
pub enum MyError {
    #[error(transparent)]
    Wrapped(#[from] InnerError),
}

This preserves the inner error's Display and source chain completely.
```

### Pattern 6: Layered Errors

**What to Look For**:
- Applications with multiple layers (domain, infrastructure, etc.)
- Need for error conversion between layers

**Pattern**:
```rust
use thiserror::Error;

// Domain layer errors
#[derive(Error, Debug)]
pub enum DomainError {
    #[error("Invalid user data: {0}")]
    InvalidUser(String),

    #[error("Business rule violated: {0}")]
    BusinessRuleViolation(String),
}

// Infrastructure layer errors
#[derive(Error, Debug)]
pub enum InfraError {
    #[error("Database error")]
    Database(#[from] sqlx::Error),

    #[error("HTTP request failed")]
    Http(#[from] reqwest::Error),
}

// Application layer combines both
#[derive(Error, Debug)]
pub enum AppError {
    #[error("Domain error: {0}")]
    Domain(#[from] DomainError),

    #[error("Infrastructure error: {0}")]
    Infra(#[from] InfraError),

    #[error("Application error: {0}")]
    Application(String),
}
```

**Suggestion Template**:
```
For layered architectures, create error types for each layer:

// Domain layer
#[derive(Error, Debug)]
pub enum DomainError {
    #[error("Invalid data: {0}")]
    Invalid(String),
}

// Infrastructure layer
#[derive(Error, Debug)]
pub enum InfraError {
    #[error("Database error")]
    Database(#[from] sqlx::Error),
}

// Application layer combines both
#[derive(Error, Debug)]
pub enum AppError {
    #[error("Domain: {0}")]
    Domain(#[from] DomainError),

    #[error("Infra: {0}")]
    Infra(#[from] InfraError),
}
```

## Advanced Patterns

### Pattern 7: Generic Error Types

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum OperationError<T>
where
    T: std::error::Error + 'static,
{
    #[error("Operation failed")]
    Failed(#[source] T),

    #[error("Timeout after {0} seconds")]
    Timeout(u64),
}
```

### Pattern 8: Conditional Compilation

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum MyError {
    #[error("IO error")]
    Io(#[from] std::io::Error),

    #[cfg(feature = "postgres")]
    #[error("Database error")]
    Database(#[from] sqlx::Error),

    #[cfg(feature = "redis")]
    #[error("Cache error")]
    Cache(#[from] redis::RedisError),
}
```

### Pattern 9: Enum with Unit and Complex Variants

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ValidationError {
    // Unit variant
    #[error("Value is required")]
    Required,

    // Tuple variant
    #[error("Invalid format: {0}")]
    InvalidFormat(String),

    // Struct variant
    #[error("Out of range (expected {expected}, got {actual})")]
    OutOfRange { expected: String, actual: String },

    // Nested error
    #[error("Validation failed")]
    Nested(#[from] SubValidationError),
}
```

## Best Practices

### DO: Clear, Actionable Error Messages

```rust
#[derive(Error, Debug)]
pub enum ConfigError {
    // ✅ Clear and actionable
    #[error("Config file not found at '{path}'. Create one using: config init")]
    NotFound { path: String },

    // ✅ Explains what's wrong and expected format
    #[error("Invalid port number '{port}'. Expected a number between 1 and 65535")]
    InvalidPort { port: String },
}
```

### DON'T: Vague Error Messages

```rust
#[derive(Error, Debug)]
pub enum BadError {
    // ❌ Too vague
    #[error("Error")]
    Error,

    // ❌ Not helpful
    #[error("Something went wrong")]
    Failed,
}
```

### DO: Include Context

```rust
#[derive(Error, Debug)]
pub enum AppError {
    // ✅ Includes what, where, and source
    #[error("Failed to read file '{path}'")]
    ReadFailed {
        path: String,
        #[source]
        source: std::io::Error,
    },
}
```

### DO: Type Aliases for Result

```rust
pub type Result<T> = std::result::Result<T, MyError>;

// Now you can use:
pub fn operation() -> Result<Value> {
    Ok(value)
}
```

## Common Mistakes

### Mistake 1: Forgetting #[source]

```rust
// ❌ BAD: Source error not marked
#[derive(Error, Debug)]
pub enum MyError {
    #[error("Failed")]
    Failed(std::io::Error),  // Missing #[source]
}

// ✅ GOOD: Properly marked
#[derive(Error, Debug)]
pub enum MyError {
    #[error("Failed")]
    Failed(#[source] std::io::Error),
}
```

### Mistake 2: Using #[from] When You Need Custom Construction

```rust
// ❌ Can't add context with #[from]
#[derive(Error, Debug)]
pub enum MyError {
    #[error("Failed")]
    Failed(#[from] std::io::Error),
}

// ✅ Use #[source] for custom construction
#[derive(Error, Debug)]
pub enum MyError {
    #[error("Failed to read config file '{path}'")]
    ConfigReadFailed {
        path: String,
        #[source]
        source: std::io::Error,
    },
}
```

## Your Approach

1. **Detect**: Identify error type definitions or thiserror usage
2. **Analyze**: Check message clarity, source chaining, and conversions
3. **Suggest**: Provide specific improvements
4. **Educate**: Explain when to use #[from] vs #[source] vs #[transparent]

## Communication Style

- Suggest thiserror for any custom error type
- Explain the difference between #[from], #[source], and #[transparent]
- Provide complete error type examples
- Show how the error will be displayed
- Point out missing error chains

When you see custom error types, immediately suggest thiserror patterns that will make them more ergonomic and idiomatic.
