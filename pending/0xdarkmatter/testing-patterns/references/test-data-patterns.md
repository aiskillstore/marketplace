# Test Data Patterns

Strategies for managing test data effectively.

## Fixtures

### Basic Fixture

```python
import pytest

@pytest.fixture
def user():
    return User(id=1, name="Test User", email="test@example.com")

def test_user_greeting(user):
    assert user.greeting() == "Hello, Test User!"
```

### Fixture with Cleanup

```python
@pytest.fixture
def temp_database():
    db = create_test_database()
    yield db
    db.drop()  # Cleanup after test
```

### Shared Fixtures (conftest.py)

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def app():
    """Application shared across all tests."""
    return create_app(testing=True)

@pytest.fixture(scope="function")
def client(app):
    """Fresh client for each test."""
    return app.test_client()
```

## Factory Pattern

### Simple Factory

```python
def make_user(**overrides):
    """Factory function for creating test users."""
    defaults = {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "active": True,
    }
    return User(**{**defaults, **overrides})

def test_inactive_user():
    user = make_user(active=False)
    assert not user.can_login()
```

### Factory Fixture

```python
@pytest.fixture
def user_factory():
    """Factory fixture for creating multiple users."""
    created = []

    def _create(**overrides):
        user = make_user(**overrides)
        created.append(user)
        return user

    yield _create

    # Cleanup
    for user in created:
        user.delete()

def test_user_comparison(user_factory):
    user1 = user_factory(name="Alice")
    user2 = user_factory(name="Bob")
    assert user1 != user2
```

### Factory Boy (Python)

```python
import factory
from factory import Faker

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    name = Faker("name")
    email = Faker("email")
    created_at = Faker("date_time_this_year")

# Usage
def test_users():
    user = UserFactory()
    admin = UserFactory(role="admin")
    users = UserFactory.create_batch(10)
```

## Builder Pattern

```python
class UserBuilder:
    """Fluent builder for test users."""

    def __init__(self):
        self._data = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
            "role": "user",
            "active": True,
        }

    def with_name(self, name: str) -> "UserBuilder":
        self._data["name"] = name
        return self

    def as_admin(self) -> "UserBuilder":
        self._data["role"] = "admin"
        return self

    def inactive(self) -> "UserBuilder":
        self._data["active"] = False
        return self

    def build(self) -> User:
        return User(**self._data)

# Usage
def test_admin_access():
    admin = UserBuilder().as_admin().build()
    assert admin.can_access_admin_panel()

def test_inactive_user():
    user = UserBuilder().inactive().build()
    assert not user.can_login()
```

## Mother Pattern

```python
class ObjectMother:
    """Pre-configured test objects for common scenarios."""

    @staticmethod
    def valid_user() -> User:
        return User(
            id=1,
            name="Valid User",
            email="valid@example.com",
            active=True
        )

    @staticmethod
    def admin_user() -> User:
        return User(
            id=2,
            name="Admin User",
            email="admin@example.com",
            role="admin",
            active=True
        )

    @staticmethod
    def expired_subscription() -> Subscription:
        return Subscription(
            user_id=1,
            expires_at=datetime.now() - timedelta(days=30),
            plan="basic"
        )

# Usage
def test_admin_permissions():
    admin = ObjectMother.admin_user()
    assert admin.can_delete_users()
```

## Fixture Composition

```python
@pytest.fixture
def address():
    return Address(street="123 Main St", city="Test City")

@pytest.fixture
def user(address):
    return User(name="Test User", address=address)

@pytest.fixture
def order(user):
    return Order(user=user, items=[])

def test_order_address(order):
    assert order.shipping_address.city == "Test City"
```

## Data Files

### JSON Fixtures

```python
# tests/fixtures/users.json
[
    {"id": 1, "name": "Alice", "role": "admin"},
    {"id": 2, "name": "Bob", "role": "user"}
]

# tests/conftest.py
@pytest.fixture
def sample_users():
    with open("tests/fixtures/users.json") as f:
        return json.load(f)
```

### YAML Fixtures

```yaml
# tests/fixtures/config.yaml
database:
  host: localhost
  port: 5432
  name: test_db

users:
  - id: 1
    name: Alice
  - id: 2
    name: Bob
```

```python
@pytest.fixture
def config():
    with open("tests/fixtures/config.yaml") as f:
        return yaml.safe_load(f)
```

## Randomized Data

```python
from faker import Faker

fake = Faker()

def test_user_email_validation():
    # Random but valid email
    email = fake.email()
    user = User(email=email)
    assert user.is_valid_email()

def test_with_seed():
    # Reproducible random data
    Faker.seed(12345)
    user = make_user(name=fake.name())
    # Same name every time with seed 12345
```

## Best Practices

### 1. Keep Fixtures Close to Tests

```
tests/
├── conftest.py          # Shared fixtures
├── unit/
│   ├── conftest.py      # Unit test fixtures
│   └── test_user.py
└── integration/
    ├── conftest.py      # Integration fixtures
    └── test_api.py
```

### 2. Use Descriptive Names

```python
# BAD
@pytest.fixture
def data():
    return {...}

# GOOD
@pytest.fixture
def user_with_expired_subscription():
    return {...}
```

### 3. Minimize Fixture Scope

```python
# Use function scope (default) unless you have a reason
@pytest.fixture(scope="function")  # Default
def user(): ...

# Session scope only for expensive, read-only fixtures
@pytest.fixture(scope="session")
def database_schema(): ...
```

### 4. Avoid Test Data Dependencies

```python
# BAD - Tests depend on each other
def test_create_user():
    user = create_user("test@example.com")
    # User exists in DB after this test

def test_get_user():
    user = get_user("test@example.com")  # Depends on previous test!

# GOOD - Each test is independent
def test_create_user(db):
    user = create_user("test@example.com")
    assert user.email == "test@example.com"

def test_get_user(db, user_factory):
    user_factory(email="test@example.com")  # Create own data
    found = get_user("test@example.com")
    assert found is not None
```
