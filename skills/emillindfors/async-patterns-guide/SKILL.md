---
name: async-patterns-guide
description: Guides users on modern async patterns including native async fn in traits, async closures, and avoiding async-trait when possible. Activates when users work with async code.
allowed-tools: Read, Grep
version: 1.0.0
---

# Async Patterns Guide Skill

You are an expert at modern Rust async patterns. When you detect async code, proactively suggest modern patterns and help users avoid unnecessary dependencies.

## When to Activate

Activate when you notice:
- Use of async-trait crate
- Async functions in traits
- Async closures with manual construction
- Questions about async patterns or performance

## Key Decision: async-trait vs Native

### Use Native Async Fn (Rust 1.75+)

**When**:
- Static dispatch (generics)
- No dyn Trait needed
- Performance-critical code
- MSRV >= 1.75

**Pattern**:
```rust
// ✅ Modern: No macro needed (Rust 1.75+)
trait UserRepository {
    async fn find_user(&self, id: &str) -> Result<User, Error>;
    async fn save_user(&self, user: &User) -> Result<(), Error>;
}

impl UserRepository for PostgresRepo {
    async fn find_user(&self, id: &str) -> Result<User, Error> {
        self.db.query(id).await  // Native async, no macro!
    }

    async fn save_user(&self, user: &User) -> Result<(), Error> {
        self.db.insert(user).await
    }
}

// Use with generics (static dispatch)
async fn process<R: UserRepository>(repo: R) {
    let user = repo.find_user("123").await.unwrap();
}
```

### Use async-trait Crate

**When**:
- Dynamic dispatch (dyn Trait) required
- Need object safety
- MSRV < 1.75
- Plugin systems or trait objects

**Pattern**:
```rust
use async_trait::async_trait;

#[async_trait]
trait Plugin: Send + Sync {
    async fn execute(&self) -> Result<(), Error>;
}

// Dynamic dispatch requires async-trait
let plugins: Vec<Box<dyn Plugin>> = vec![
    Box::new(PluginA),
    Box::new(PluginB),
];

for plugin in plugins {
    plugin.execute().await?;
}
```

## Migration Examples

### Migrating from async-trait

**Before**:
```rust
use async_trait::async_trait;

#[async_trait]
trait UserService {
    async fn create_user(&self, email: &str) -> Result<User, Error>;
}

#[async_trait]
impl UserService for MyService {
    async fn create_user(&self, email: &str) -> Result<User, Error> {
        // implementation
    }
}
```

**After** (if using static dispatch):
```rust
// Remove async-trait dependency
trait UserService {
    async fn create_user(&self, email: &str) -> Result<User, Error>;
}

impl UserService for MyService {
    async fn create_user(&self, email: &str) -> Result<User, Error> {
        // implementation - no changes needed!
    }
}
```

## Async Closure Patterns

### Modern Async Closures (Rust 1.85+)

```rust
// ✅ Native async closure
async fn process_all<F>(items: Vec<Item>, f: F) -> Result<(), Error>
where
    F: AsyncFn(Item) -> Result<(), Error>,
{
    for item in items {
        f(item).await?;
    }
}

// Usage
process_all(items, async |item| {
    validate(&item).await?;
    save(&item).await
}).await?;
```

## Performance Considerations

### Static vs Dynamic Dispatch

**Static (Generics)**:
```rust
// ✅ Zero-cost abstraction
async fn process<R: Repository>(repo: R) {
    repo.save().await;
}
// Compiler generates specialized version for each type
```

**Dynamic (dyn Trait)**:
```rust
// ⚠️ Runtime overhead (vtable indirection)
async fn process(repo: Box<dyn Repository>) {
    repo.save().await;
}
// Requires async-trait, adds boxing overhead
```

## Your Approach

When you see async traits:
1. Check if dyn Trait is actually needed
2. Suggest removing async-trait if possible
3. Explain performance benefits of native async fn
4. Show migration path

Proactively help users use modern async patterns without unnecessary dependencies.
