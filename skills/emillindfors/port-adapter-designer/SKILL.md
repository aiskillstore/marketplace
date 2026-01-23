---
name: port-adapter-designer
description: Helps design port traits and adapter implementations for external dependencies. Activates when users need to abstract away databases, APIs, or other external systems.
allowed-tools: Read, Grep
version: 1.0.0
---

# Port and Adapter Designer Skill

You are an expert at designing ports (trait abstractions) and adapters (implementations) for hexagonal architecture in Rust. When you detect external dependencies or integration needs, proactively suggest port/adapter patterns.

## When to Activate

Activate when you notice:
- Direct usage of databases, HTTP clients, or file systems
- Need to swap implementations for testing
- External service integrations
- Questions about abstraction or dependency injection

## Port Design Patterns

### Pattern 1: Repository Port

```rust
#[async_trait]
pub trait UserRepository: Send + Sync {
    async fn find_by_id(&self, id: &UserId) -> Result<User, RepositoryError>;
    async fn find_by_email(&self, email: &Email) -> Result<User, RepositoryError>;
    async fn save(&self, user: &User) -> Result<(), RepositoryError>;
    async fn delete(&self, id: &UserId) -> Result<(), RepositoryError>;
    async fn list(&self, limit: usize, offset: usize) -> Result<Vec<User>, RepositoryError>;
}
```

### Pattern 2: External Service Port

```rust
#[async_trait]
pub trait PaymentGateway: Send + Sync {
    async fn process_payment(&self, amount: Money, card: &CardDetails) -> Result<PaymentId, PaymentError>;
    async fn refund(&self, payment_id: &PaymentId) -> Result<RefundId, PaymentError>;
    async fn get_status(&self, payment_id: &PaymentId) -> Result<PaymentStatus, PaymentError>;
}
```

### Pattern 3: Notification Port

```rust
#[async_trait]
pub trait NotificationService: Send + Sync {
    async fn send_email(&self, to: &Email, subject: &str, body: &str) -> Result<(), NotificationError>;
    async fn send_sms(&self, phone: &PhoneNumber, message: &str) -> Result<(), NotificationError>;
}
```

## Adapter Implementation Patterns

### PostgreSQL Adapter

```rust
pub struct PostgresUserRepository {
    pool: PgPool,
}

impl PostgresUserRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }
}

#[async_trait]
impl UserRepository for PostgresUserRepository {
    async fn find_by_id(&self, id: &UserId) -> Result<User, RepositoryError> {
        let row = sqlx::query_as!(
            UserRow,
            "SELECT id, email, name FROM users WHERE id = $1",
            id.as_str()
        )
        .fetch_one(&self.pool)
        .await
        .map_err(|e| match e {
            sqlx::Error::RowNotFound => RepositoryError::NotFound,
            _ => RepositoryError::Database(e.to_string()),
        })?;

        Ok(User::try_from(row)?)
    }

    async fn save(&self, user: &User) -> Result<(), RepositoryError> {
        sqlx::query!(
            "INSERT INTO users (id, email, name) VALUES ($1, $2, $3)
             ON CONFLICT (id) DO UPDATE SET email = $2, name = $3",
            user.id().as_str(),
            user.email().as_str(),
            user.name()
        )
        .execute(&self.pool)
        .await
        .map_err(|e| RepositoryError::Database(e.to_string()))?;

        Ok(())
    }
}
```

### HTTP Client Adapter

```rust
pub struct StripePaymentGateway {
    client: reqwest::Client,
    api_key: String,
}

#[async_trait]
impl PaymentGateway for StripePaymentGateway {
    async fn process_payment(&self, amount: Money, card: &CardDetails) -> Result<PaymentId, PaymentError> {
        #[derive(Serialize)]
        struct PaymentRequest {
            amount: u64,
            currency: String,
            card: CardDetailsDto,
        }

        let response = self
            .client
            .post("https://api.stripe.com/v1/charges")
            .bearer_auth(&self.api_key)
            .json(&PaymentRequest {
                amount: amount.cents(),
                currency: amount.currency().to_string(),
                card: CardDetailsDto::from(card),
            })
            .send()
            .await
            .map_err(|e| PaymentError::Network(e.to_string()))?;

        if !response.status().is_success() {
            return Err(PaymentError::GatewayRejected(response.status().to_string()));
        }

        let data: PaymentResponse = response
            .json()
            .await
            .map_err(|e| PaymentError::ParseError(e.to_string()))?;

        Ok(PaymentId::from(data.id))
    }
}
```

### In-Memory Adapter (for testing)

```rust
pub struct InMemoryUserRepository {
    users: Arc<Mutex<HashMap<UserId, User>>>,
}

impl InMemoryUserRepository {
    pub fn new() -> Self {
        Self {
            users: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn with_users(users: Vec<User>) -> Self {
        let map = users.into_iter().map(|u| (u.id().clone(), u)).collect();
        Self {
            users: Arc::new(Mutex::new(map)),
        }
    }
}

#[async_trait]
impl UserRepository for InMemoryUserRepository {
    async fn find_by_id(&self, id: &UserId) -> Result<User, RepositoryError> {
        self.users
            .lock()
            .await
            .get(id)
            .cloned()
            .ok_or(RepositoryError::NotFound)
    }

    async fn save(&self, user: &User) -> Result<(), RepositoryError> {
        self.users
            .lock()
            .await
            .insert(user.id().clone(), user.clone());
        Ok(())
    }
}
```

## Port Design Guidelines

1. **Use domain types**: Parameters and return types should be domain objects
2. **Async by default**: Most I/O is async in Rust
3. **Return domain errors**: Convert infrastructure errors at the boundary
4. **Send + Sync**: Required for multi-threaded async runtimes
5. **Focused interfaces**: Each port should have a single responsibility

## Your Approach

When you see external dependencies:
1. Identify the interface needed
2. Design a port trait with domain types
3. Suggest adapter implementations
4. Show testing strategy with mocks

Proactively suggest port/adapter patterns when you detect tight coupling to external systems.
