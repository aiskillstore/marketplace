---
name: mock-strategy-guide
description: Guides users on creating mock implementations for testing with traits, providing test doubles, and avoiding tight coupling to test infrastructure. Activates when users need to test code with external dependencies.
allowed-tools: Read, Grep
version: 1.0.0
---

# Mock Strategy Guide Skill

You are an expert at testing strategies for Rust, especially creating mock implementations for hexagonal architecture. When you detect testing needs for code with dependencies, proactively suggest mocking strategies.

## When to Activate

Activate when you notice:
- Code with external dependencies (DB, HTTP, etc.)
- Trait-based abstractions for repositories or services
- Tests that require real infrastructure
- Questions about mocking or test doubles

## Mock Implementation Patterns

### Pattern 1: Simple Mock Repository

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    struct MockUserRepository {
        users: HashMap<String, User>,
    }

    impl MockUserRepository {
        fn new() -> Self {
            Self {
                users: HashMap::new(),
            }
        }

        fn with_user(mut self, user: User) -> Self {
            self.users.insert(user.id.clone(), user);
            self
        }
    }

    #[async_trait]
    impl UserRepository for MockUserRepository {
        async fn find(&self, id: &str) -> Result<User, Error> {
            self.users
                .get(id)
                .cloned()
                .ok_or(Error::NotFound)
        }

        async fn save(&self, user: &User) -> Result<(), Error> {
            // Mock just succeeds
            Ok(())
        }
    }

    #[tokio::test]
    async fn test_user_service() {
        // Arrange
        let user = User { id: "1".to_string(), email: "test@example.com".to_string() };
        let mock_repo = MockUserRepository::new().with_user(user.clone());
        let service = UserService::new(mock_repo);

        // Act
        let result = service.get_user("1").await;

        // Assert
        assert!(result.is_ok());
        assert_eq!(result.unwrap().id, "1");
    }
}
```

### Pattern 2: Mock with Verification

```rust
#[cfg(test)]
mod tests {
    use std::sync::{Arc, Mutex};

    struct MockEmailService {
        sent_emails: Arc<Mutex<Vec<Email>>>,
    }

    impl MockEmailService {
        fn new() -> Self {
            Self {
                sent_emails: Arc::new(Mutex::new(Vec::new())),
            }
        }

        fn emails_sent(&self) -> Vec<Email> {
            self.sent_emails.lock().unwrap().clone()
        }
    }

    #[async_trait]
    impl EmailService for MockEmailService {
        async fn send(&self, email: Email) -> Result<(), Error> {
            self.sent_emails.lock().unwrap().push(email);
            Ok(())
        }
    }

    #[tokio::test]
    async fn test_sends_welcome_email() {
        let mock_email = MockEmailService::new();
        let service = UserService::new(mock_email.clone());

        service.register_user("test@example.com").await.unwrap();

        // Verify email was sent
        let emails = mock_email.emails_sent();
        assert_eq!(emails.len(), 1);
        assert_eq!(emails[0].to, "test@example.com");
        assert!(emails[0].subject.contains("Welcome"));
    }
}
```

### Pattern 3: Mock with Controlled Failures

```rust
#[cfg(test)]
mod tests {
    enum MockBehavior {
        Success,
        NotFound,
        DatabaseError,
    }

    struct MockRepository {
        behavior: MockBehavior,
    }

    impl MockRepository {
        fn with_behavior(behavior: MockBehavior) -> Self {
            Self { behavior }
        }
    }

    #[async_trait]
    impl UserRepository for MockRepository {
        async fn find(&self, id: &str) -> Result<User, Error> {
            match self.behavior {
                MockBehavior::Success => Ok(test_user()),
                MockBehavior::NotFound => Err(Error::NotFound),
                MockBehavior::DatabaseError => Err(Error::Database("Connection failed".into())),
            }
        }
    }

    #[tokio::test]
    async fn test_handles_not_found() {
        let mock = MockRepository::with_behavior(MockBehavior::NotFound);
        let service = UserService::new(mock);

        let result = service.get_user("1").await;

        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), Error::NotFound));
    }

    #[tokio::test]
    async fn test_handles_database_error() {
        let mock = MockRepository::with_behavior(MockBehavior::DatabaseError);
        let service = UserService::new(mock);

        let result = service.get_user("1").await;

        assert!(result.is_err());
    }
}
```

### Pattern 4: Builder Pattern for Mocks

```rust
#[cfg(test)]
mod tests {
    struct MockRepositoryBuilder {
        users: HashMap<String, User>,
        find_error: Option<Error>,
        save_error: Option<Error>,
    }

    impl MockRepositoryBuilder {
        fn new() -> Self {
            Self {
                users: HashMap::new(),
                find_error: None,
                save_error: None,
            }
        }

        fn with_user(mut self, user: User) -> Self {
            self.users.insert(user.id.clone(), user);
            self
        }

        fn with_find_error(mut self, error: Error) -> Self {
            self.find_error = Some(error);
            self
        }

        fn build(self) -> MockRepository {
            MockRepository {
                users: self.users,
                find_error: self.find_error,
                save_error: self.save_error,
            }
        }
    }

    #[tokio::test]
    async fn test_with_builder() {
        let mock = MockRepositoryBuilder::new()
            .with_user(test_user())
            .with_save_error(Error::Database("Save failed".into()))
            .build();

        let service = UserService::new(mock);

        // Can find user
        let user = service.get_user("1").await.unwrap();

        // But save fails
        let result = service.update_user(user).await;
        assert!(result.is_err());
    }
}
```

## In-Memory Test Implementations

For integration tests with real logic but no infrastructure:

```rust
pub struct InMemoryUserRepository {
    users: Arc<Mutex<HashMap<String, User>>>,
}

impl InMemoryUserRepository {
    pub fn new() -> Self {
        Self {
            users: Arc::new(Mutex::new(HashMap::new())),
        }
    }
}

#[async_trait]
impl UserRepository for InMemoryUserRepository {
    async fn find(&self, id: &str) -> Result<User, Error> {
        self.users
            .lock()
            .unwrap()
            .get(id)
            .cloned()
            .ok_or(Error::NotFound)
    }

    async fn save(&self, user: &User) -> Result<(), Error> {
        self.users
            .lock()
            .unwrap()
            .insert(user.id.clone(), user.clone());
        Ok(())
    }

    async fn delete(&self, id: &str) -> Result<(), Error> {
        self.users
            .lock()
            .unwrap()
            .remove(id)
            .ok_or(Error::NotFound)?;
        Ok(())
    }
}
```

## Test Fixture Helpers

```rust
#[cfg(test)]
mod fixtures {
    use super::*;

    pub fn test_user() -> User {
        User {
            id: "test-id".to_string(),
            email: "test@example.com".to_string(),
            name: "Test User".to_string(),
        }
    }

    pub fn test_user_with_id(id: &str) -> User {
        User {
            id: id.to_string(),
            email: "test@example.com".to_string(),
            name: "Test User".to_string(),
        }
    }

    pub fn test_users(count: usize) -> Vec<User> {
        (0..count)
            .map(|i| test_user_with_id(&format!("user-{}", i)))
            .collect()
    }
}
```

## Your Approach

When you see code needing tests:
1. Identify external dependencies (traits)
2. Suggest mock implementation structure
3. Show verification patterns
4. Provide test fixture helpers

When you see tests without mocks:
1. Suggest extracting trait if tightly coupled
2. Show how to create mock implementations
3. Demonstrate verification patterns

Proactively suggest mocking strategies for testable, maintainable code.
