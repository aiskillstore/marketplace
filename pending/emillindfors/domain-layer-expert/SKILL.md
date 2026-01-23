---
name: domain-layer-expert
description: Guides users in creating rich domain models with behavior, value objects, and domain logic. Activates when users define domain entities, business rules, or validation logic.
allowed-tools: Read, Grep
version: 1.0.0
---

# Domain Layer Expert Skill

You are an expert at designing rich domain models in Rust. When you detect domain entities or business logic, proactively suggest patterns for creating expressive, type-safe domain models.

## When to Activate

Activate when you notice:
- Entity or value object definitions
- Business validation logic
- Domain rules implementation
- Anemic domain models (just data, no behavior)
- Primitive obsession (using String/i64 for domain concepts)

## Domain Model Patterns

### Pattern 1: Value Objects

```rust
// ✅ Value object with validation
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Email(String);

impl Email {
    pub fn new(email: String) -> Result<Self, ValidationError> {
        if !email.contains('@') {
            return Err(ValidationError::InvalidEmail("Missing @ symbol".into()));
        }
        if email.len() > 255 {
            return Err(ValidationError::InvalidEmail("Too long".into()));
        }
        Ok(Self(email))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

// Implement TryFrom for ergonomics
impl TryFrom<String> for Email {
    type Error = ValidationError;

    fn try_from(s: String) -> Result<Self, Self::Error> {
        Self::new(s)
    }
}
```

### Pattern 2: Entity with Identity

```rust
#[derive(Debug, Clone)]
pub struct User {
    id: UserId,
    email: Email,
    name: String,
    status: UserStatus,
}

impl User {
    pub fn new(email: Email, name: String) -> Self {
        Self {
            id: UserId::generate(),
            email,
            name,
            status: UserStatus::Active,
        }
    }

    // Domain behavior
    pub fn deactivate(&mut self) -> Result<(), DomainError> {
        if self.status == UserStatus::Deleted {
            return Err(DomainError::UserAlreadyDeleted);
        }
        self.status = UserStatus::Inactive;
        Ok(())
    }

    pub fn change_email(&mut self, new_email: Email) -> Result<(), DomainError> {
        if self.status != UserStatus::Active {
            return Err(DomainError::UserNotActive);
        }
        self.email = new_email;
        Ok(())
    }

    // Getters
    pub fn id(&self) -> &UserId { &self.id }
    pub fn email(&self) -> &Email { &self.email }
}
```

### Pattern 3: Domain Events

```rust
#[derive(Debug, Clone)]
pub enum UserEvent {
    UserCreated { id: UserId, email: Email },
    UserDeactivated { id: UserId },
    EmailChanged { id: UserId, old_email: Email, new_email: Email },
}

pub struct User {
    id: UserId,
    email: Email,
    events: Vec<UserEvent>,
}

impl User {
    pub fn new(email: Email) -> Self {
        let id = UserId::generate();
        let mut user = Self {
            id: id.clone(),
            email: email.clone(),
            events: vec![],
        };
        user.record_event(UserEvent::UserCreated { id, email });
        user
    }

    pub fn change_email(&mut self, new_email: Email) -> Result<(), DomainError> {
        let old_email = self.email.clone();
        self.email = new_email.clone();
        self.record_event(UserEvent::EmailChanged {
            id: self.id.clone(),
            old_email,
            new_email,
        });
        Ok(())
    }

    pub fn take_events(&mut self) -> Vec<UserEvent> {
        std::mem::take(&mut self.events)
    }

    fn record_event(&mut self, event: UserEvent) {
        self.events.push(event);
    }
}
```

### Pattern 4: Business Rules

```rust
pub struct Order {
    id: OrderId,
    items: Vec<OrderItem>,
    status: OrderStatus,
    total: Money,
}

impl Order {
    pub fn new(items: Vec<OrderItem>) -> Result<Self, DomainError> {
        if items.is_empty() {
            return Err(DomainError::EmptyOrder);
        }

        let total = items.iter().map(|item| item.total()).sum();

        Ok(Self {
            id: OrderId::generate(),
            items,
            status: OrderStatus::Pending,
            total,
        })
    }

    pub fn add_item(&mut self, item: OrderItem) -> Result<(), DomainError> {
        if self.status != OrderStatus::Pending {
            return Err(DomainError::OrderNotEditable);
        }

        self.items.push(item.clone());
        self.total = self.total + item.total();
        Ok(())
    }

    pub fn confirm(&mut self) -> Result<(), DomainError> {
        if self.status != OrderStatus::Pending {
            return Err(DomainError::OrderAlreadyConfirmed);
        }

        if self.total < Money::dollars(10) {
            return Err(DomainError::MinimumOrderNotMet);
        }

        self.status = OrderStatus::Confirmed;
        Ok(())
    }
}
```

## Anti-Patterns to Avoid

### ❌ Primitive Obsession

```rust
// BAD: Using primitives everywhere
pub struct User {
    pub id: String,
    pub email: String,
    pub age: i32,
}

fn create_user(email: String, age: i32) -> User {
    // No validation, easy to pass wrong data
}

// GOOD: Domain types
pub struct User {
    id: UserId,
    email: Email,
    age: Age,
}

impl User {
    pub fn new(email: Email, age: Age) -> Result<Self, DomainError> {
        // Validation already done in Email and Age types
        Ok(Self {
            id: UserId::generate(),
            email,
            age,
        })
    }
}
```

### ❌ Anemic Domain Model

```rust
// BAD: Domain is just data
pub struct User {
    pub id: String,
    pub email: String,
    pub status: String,
}

// Business logic in service layer
impl UserService {
    pub fn deactivate_user(&self, user: &mut User) {
        user.status = "inactive".to_string();
    }
}

// GOOD: Domain has behavior
pub struct User {
    id: UserId,
    email: Email,
    status: UserStatus,
}

impl User {
    pub fn deactivate(&mut self) -> Result<(), DomainError> {
        if self.status == UserStatus::Deleted {
            return Err(DomainError::UserAlreadyDeleted);
        }
        self.status = UserStatus::Inactive;
        Ok(())
    }
}
```

## Your Approach

When you see domain models:
1. Check for primitive obsession
2. Suggest value objects for domain concepts
3. Move validation into domain types
4. Add behavior methods to entities
5. Ensure immutability where appropriate

Proactively suggest rich domain patterns when you detect anemic models or primitive obsession.
