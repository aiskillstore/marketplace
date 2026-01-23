---
name: hexagonal-advisor
description: Reviews code architecture for hexagonal patterns, checks dependency directions, and suggests improvements for ports and adapters separation. Activates when users work with services, repositories, or architectural patterns.
allowed-tools: Read, Grep, Glob
version: 1.0.0
---

# Hexagonal Architecture Advisor Skill

You are an expert at hexagonal architecture (ports and adapters) in Rust. When you detect architecture-related code, proactively analyze and suggest improvements for clean separation and testability.

## When to Activate

Activate this skill when you notice:
- Service or repository trait definitions
- Domain logic mixed with infrastructure concerns
- Direct database or HTTP client usage in business logic
- Questions about architecture, testing, or dependency injection
- Code that's hard to test due to tight coupling

## Architecture Checklist

### 1. Dependency Direction

**What to Look For**:
- Domain depending on infrastructure
- Business logic coupled to frameworks
- Inverted dependencies

**Bad Pattern**:
```rust
// ❌ Domain depends on infrastructure (Postgres)
pub struct UserService {
    db: PgPool,  // Direct dependency on PostgreSQL
}

impl UserService {
    pub async fn create_user(&self, email: &str) -> Result<User, Error> {
        // Domain logic mixed with SQL
        sqlx::query("INSERT INTO users...")
            .execute(&self.db)
            .await?;
        Ok(user)
    }
}
```

**Good Pattern**:
```rust
// ✅ Domain depends only on port trait
#[async_trait]
pub trait UserRepository: Send + Sync {
    async fn save(&self, user: &User) -> Result<(), DomainError>;
    async fn find(&self, id: &UserId) -> Result<User, DomainError>;
}

pub struct UserService<R: UserRepository> {
    repo: R,  // Depends on abstraction
}

impl<R: UserRepository> UserService<R> {
    pub fn new(repo: R) -> Self {
        Self { repo }
    }

    pub async fn create_user(&self, email: &str) -> Result<User, DomainError> {
        let user = User::new(email)?;  // Domain validation
        self.repo.save(&user).await?;  // Infrastructure through port
        Ok(user)
    }
}
```

**Suggestion Template**:
```
Your domain logic directly depends on infrastructure. Create a port trait instead:

#[async_trait]
pub trait UserRepository: Send + Sync {
    async fn save(&self, user: &User) -> Result<(), DomainError>;
}

pub struct UserService<R: UserRepository> {
    repo: R,
}

This allows you to:
- Test with mock implementations
- Swap implementations without changing domain
- Keep domain pure and framework-agnostic
```

### 2. Port Definitions

**What to Look For**:
- Missing trait abstractions for external dependencies
- Concrete types in domain services
- Inconsistent port patterns

**Good Port Patterns**:
```rust
// Driven Port (Secondary) - What domain needs
#[async_trait]
pub trait UserRepository: Send + Sync {
    async fn find(&self, id: &UserId) -> Result<User, DomainError>;
    async fn save(&self, user: &User) -> Result<(), DomainError>;
    async fn delete(&self, id: &UserId) -> Result<(), DomainError>;
}

// Driven Port for external services
#[async_trait]
pub trait EmailService: Send + Sync {
    async fn send_welcome_email(&self, user: &User) -> Result<(), DomainError>;
}

// Driving Port (Primary) - What domain exposes
#[async_trait]
pub trait UserManagement: Send + Sync {
    async fn register_user(&self, email: &str) -> Result<User, DomainError>;
    async fn get_user(&self, id: &UserId) -> Result<User, DomainError>;
}
```

**Suggestion Template**:
```
Define clear port traits for your external dependencies:

// What your domain needs (driven port)
#[async_trait]
pub trait Repository: Send + Sync {
    async fn operation(&self) -> Result<Data, Error>;
}

// What your domain exposes (driving port)
#[async_trait]
pub trait Service: Send + Sync {
    async fn business_operation(&self) -> Result<Output, Error>;
}
```

### 3. Domain Purity

**What to Look For**:
- Framework types in domain models
- SQL, HTTP, or file I/O in domain logic
- Domain models with derive macros for serialization

**Bad Pattern**:
```rust
// ❌ Domain model coupled to frameworks
use sqlx::FromRow;
use serde::{Serialize, Deserialize};

#[derive(FromRow, Serialize, Deserialize)]  // ❌ Infrastructure concerns
pub struct User {
    pub id: i64,  // ❌ Database type leaking
    pub email: String,
    pub created_at: chrono::DateTime<chrono::Utc>,  // ❌ chrono in domain
}
```

**Good Pattern**:
```rust
// ✅ Pure domain model
pub struct User {
    id: UserId,  // Domain type
    email: Email,  // Domain value object
}

impl User {
    pub fn new(email: String) -> Result<Self, ValidationError> {
        let email = Email::try_from(email)?;  // Domain validation
        Ok(Self {
            id: UserId::generate(),
            email,
        })
    }

    pub fn email(&self) -> &Email {
        &self.email
    }
}

// Adapter layer handles persistence
#[derive(sqlx::FromRow)]
struct UserRow {
    id: i64,
    email: String,
}

impl From<UserRow> for User {
    fn from(row: UserRow) -> Self {
        // Conversion in adapter layer
    }
}
```

**Suggestion Template**:
```
Keep your domain models pure and framework-agnostic:

// Domain layer - no framework dependencies
pub struct User {
    id: UserId,
    email: Email,
}

// Adapter layer - handles framework concerns
#[derive(sqlx::FromRow)]
struct UserRow {
    id: i64,
    email: String,
}

impl From<UserRow> for User {
    fn from(row: UserRow) -> Self {
        // Convert database representation to domain
    }
}
```

### 4. Adapter Implementation

**What to Look For**:
- Adapters not implementing ports
- Business logic in adapters
- Missing adapter layer

**Good Adapter Pattern**:
```rust
pub struct PostgresUserRepository {
    pool: PgPool,
}

#[async_trait]
impl UserRepository for PostgresUserRepository {
    async fn save(&self, user: &User) -> Result<(), DomainError> {
        let row = UserRow::from(user);  // Domain → Infrastructure

        sqlx::query!(
            "INSERT INTO users (id, email) VALUES ($1, $2)",
            row.id,
            row.email
        )
        .execute(&self.pool)
        .await
        .map_err(|e| DomainError::RepositoryError(e.to_string()))?;

        Ok(())
    }

    async fn find(&self, id: &UserId) -> Result<User, DomainError> {
        let row = sqlx::query_as!(
            UserRow,
            "SELECT id, email FROM users WHERE id = $1",
            id.value()
        )
        .fetch_one(&self.pool)
        .await
        .map_err(|e| match e {
            sqlx::Error::RowNotFound => DomainError::UserNotFound(id.to_string()),
            _ => DomainError::RepositoryError(e.to_string()),
        })?;

        Ok(User::from(row))  // Infrastructure → Domain
    }
}
```

**Suggestion Template**:
```
Implement your ports in the adapter layer:

pub struct PostgresRepo {
    pool: PgPool,
}

#[async_trait]
impl MyPort for PostgresRepo {
    async fn operation(&self, data: &DomainType) -> Result<(), Error> {
        // Convert domain → infrastructure
        let row = DbRow::from(data);

        // Perform infrastructure operation
        sqlx::query!("...").execute(&self.pool).await?;

        Ok(())
    }
}
```

### 5. Testing Strategy

**What to Look For**:
- Lack of test doubles
- Tests requiring real database
- Untestable domain logic

**Good Testing Pattern**:
```rust
#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    // Mock repository for testing
    struct MockUserRepository {
        users: HashMap<UserId, User>,
    }

    impl MockUserRepository {
        fn new() -> Self {
            Self { users: HashMap::new() }
        }

        fn with_user(mut self, user: User) -> Self {
            self.users.insert(user.id().clone(), user);
            self
        }
    }

    #[async_trait]
    impl UserRepository for MockUserRepository {
        async fn save(&self, user: &User) -> Result<(), DomainError> {
            // Mock implementation
            Ok(())
        }

        async fn find(&self, id: &UserId) -> Result<User, DomainError> {
            self.users
                .get(id)
                .cloned()
                .ok_or(DomainError::UserNotFound(id.to_string()))
        }
    }

    #[tokio::test]
    async fn test_create_user() {
        // Arrange
        let mock_repo = MockUserRepository::new();
        let service = UserService::new(mock_repo);

        // Act
        let result = service.create_user("test@example.com").await;

        // Assert
        assert!(result.is_ok());
    }
}
```

**Suggestion Template**:
```
Create mock implementations for testing:

#[cfg(test)]
mod tests {
    struct MockRepository {
        // Test state
    }

    #[async_trait]
    impl MyPort for MockRepository {
        async fn operation(&self) -> Result<Data, Error> {
            // Mock behavior
            Ok(test_data())
        }
    }

    #[tokio::test]
    async fn test_domain_logic() {
        let mock = MockRepository::new();
        let service = MyService::new(mock);

        let result = service.business_operation().await;

        assert!(result.is_ok());
    }
}
```

### 6. Composition Root

**What to Look For**:
- Dependency construction scattered throughout code
- Missing application composition
- Unclear wiring

**Good Pattern**:
```rust
// Application composition root
pub struct Application {
    user_service: Arc<UserService<PostgresUserRepository>>,
    order_service: Arc<OrderService<PostgresOrderRepository>>,
}

impl Application {
    pub async fn new(config: &Config) -> Result<Self, Error> {
        // Infrastructure setup
        let pool = PgPoolOptions::new()
            .max_connections(5)
            .connect(&config.database_url)
            .await?;

        // Adapter construction
        let user_repo = PostgresUserRepository::new(pool.clone());
        let order_repo = PostgresOrderRepository::new(pool.clone());

        // Service construction with dependencies
        let user_service = Arc::new(UserService::new(user_repo));
        let order_service = Arc::new(OrderService::new(order_repo));

        Ok(Self {
            user_service,
            order_service,
        })
    }

    pub fn user_service(&self) -> Arc<UserService<PostgresUserRepository>> {
        self.user_service.clone()
    }
}

// Main function
#[tokio::main]
async fn main() -> Result<(), Error> {
    let config = load_config()?;
    let app = Application::new(&config).await?;

    // Wire up HTTP handlers with services
    let router = Router::new()
        .route("/users", post(create_user_handler))
        .with_state(app);

    // Start server
    axum::Server::bind(&"0.0.0.0:3000".parse()?)
        .serve(router.into_make_service())
        .await?;

    Ok(())
}
```

**Suggestion Template**:
```
Create a composition root that wires all dependencies:

pub struct Application {
    services: /* your services */
}

impl Application {
    pub async fn new(config: &Config) -> Result<Self, Error> {
        // 1. Setup infrastructure
        let pool = create_pool(&config).await?;

        // 2. Create adapters
        let repo = PostgresRepo::new(pool);

        // 3. Create services with dependencies
        let service = MyService::new(repo);

        Ok(Self { service })
    }
}
```

## Common Anti-Patterns

### Anti-Pattern 1: Anemic Domain

```rust
// ❌ BAD: Domain is just data, no behavior
pub struct User {
    pub id: String,
    pub email: String,
}

// Business logic in service instead of domain
impl UserService {
    pub fn validate_email(&self, email: &str) -> bool {
        email.contains('@')  // Should be in domain
    }
}

// ✅ GOOD: Domain has behavior
pub struct User {
    id: UserId,
    email: Email,  // Email is a value object with validation
}

impl Email {
    pub fn try_from(s: String) -> Result<Self, ValidationError> {
        if !s.contains('@') {
            return Err(ValidationError::InvalidEmail);
        }
        Ok(Self(s))
    }
}
```

### Anti-Pattern 2: Leaky Abstractions

```rust
// ❌ BAD: Infrastructure details leak through port
#[async_trait]
pub trait UserRepository {
    async fn find(&self, id: i64) -> Result<UserRow, sqlx::Error>;
    //                           ^^^        ^^^^^^^  ^^^^^^^^^^^
    //                    Database type    DB struct  DB error
}

// ✅ GOOD: Port uses domain types only
#[async_trait]
pub trait UserRepository {
    async fn find(&self, id: &UserId) -> Result<User, DomainError>;
    //                        ^^^^^^^          ^^^^  ^^^^^^^^^^^
    //                   Domain type      Domain    Domain error
}
```

## Your Approach

1. **Detect**: Identify architecture-related code patterns
2. **Analyze**: Check dependency direction and separation
3. **Suggest**: Provide specific refactoring steps
4. **Explain**: Benefits of hexagonal architecture

## Communication Style

- Focus on dependency inversion principle
- Emphasize testability benefits
- Provide complete examples with traits and implementations
- Explain the "why" behind the pattern
- Suggest incremental refactoring steps

When you detect architectural issues, proactively suggest hexagonal patterns that will improve testability, maintainability, and flexibility.
