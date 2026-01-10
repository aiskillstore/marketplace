# Test Architecture Patterns

Organize tests for maintainability, speed, and confidence.

## Test Pyramid

```
                 ┌─────────────┐
                 │     E2E     │  Few, slow, high confidence
                 │   Browser   │
                 ├─────────────┤
                 │ Integration │  Moderate, real services
                 │   API/DB    │
                 ├─────────────┤
                 │    Unit     │  Many, fast, isolated
                 │  Functions  │
                 └─────────────┘
```

| Layer | Count | Speed | Scope | Tools |
|-------|-------|-------|-------|-------|
| Unit | 70% | <1ms | Single function | pytest, mock |
| Integration | 20% | <1s | Multiple components | testcontainers, FastAPI TestClient |
| E2E | 10% | <30s | Full system | Playwright, Selenium |

## Directory Structure

```
project/
├── src/
│   └── myapp/
│       ├── models/
│       ├── services/
│       └── api/
├── tests/
│   ├── conftest.py           # Shared fixtures
│   ├── unit/                  # Fast, isolated tests
│   │   ├── conftest.py
│   │   ├── test_models.py
│   │   └── test_services.py
│   ├── integration/           # Real services tests
│   │   ├── conftest.py        # DB, Redis fixtures
│   │   ├── test_api.py
│   │   └── test_repositories.py
│   ├── e2e/                   # End-to-end tests
│   │   ├── conftest.py
│   │   └── test_user_flows.py
│   └── fixtures/              # Shared test data
│       └── users.json
└── pytest.ini
```

## pytest Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*

# Markers for test categories
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (requires services)
    e2e: End-to-end tests (full system)
    slow: Slow tests (>1s)

# Default options
addopts =
    -ra                 # Show summary of all except passed
    --strict-markers    # Error on unknown markers
    -q                  # Quiet mode
```

## Test Isolation Strategies

### 1. Database Isolation with Transactions

```python
@pytest.fixture
def db_session(engine):
    """Each test runs in a rolled-back transaction."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

### 2. Schema Isolation (Parallel Safe)

```python
import uuid

@pytest.fixture(scope="session")
def test_schema(engine):
    """Create isolated schema for test session."""
    schema_name = f"test_{uuid.uuid4().hex[:8]}"

    with engine.connect() as conn:
        conn.execute(f"CREATE SCHEMA {schema_name}")
        conn.execute(f"SET search_path TO {schema_name}")

    yield schema_name

    with engine.connect() as conn:
        conn.execute(f"DROP SCHEMA {schema_name} CASCADE")
```

### 3. Container Isolation

```python
@pytest.fixture(scope="session")
def isolated_postgres():
    """Each test session gets fresh PostgreSQL."""
    with PostgresContainer("postgres:15") as pg:
        yield pg.get_connection_url()
```

## conftest.py Patterns

### Root conftest.py

```python
# tests/conftest.py
import pytest
from typing import Generator

# Session-scoped fixtures
@pytest.fixture(scope="session")
def app():
    """Create application once per session."""
    from myapp import create_app
    return create_app(testing=True)

@pytest.fixture(scope="session")
def engine(app):
    """Database engine for session."""
    return app.extensions["db"].engine

# Function-scoped (per-test)
@pytest.fixture
def client(app) -> Generator:
    """Test client per test."""
    with app.test_client() as client:
        yield client
```

### Unit Test conftest.py

```python
# tests/unit/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_db():
    """Mock database for unit tests."""
    return Mock()

@pytest.fixture
def mock_redis():
    """Mock Redis for unit tests."""
    return Mock()

@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Prevent network calls in unit tests."""
    import socket
    monkeypatch.setattr(socket, "socket", Mock(side_effect=Exception("No network in unit tests!")))
```

### Integration Test conftest.py

```python
# tests/integration/conftest.py
import pytest

@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL container for integration tests."""
    from testcontainers.postgres import PostgresContainer
    with PostgresContainer("postgres:15") as pg:
        yield pg

@pytest.fixture
def db_session(postgres_container):
    """Database session with rollback."""
    # Transaction rollback pattern
    ...
```

## Test Markers and Selection

```python
import pytest

# Mark tests by category
@pytest.mark.unit
def test_calculate_total():
    assert calculate_total([1, 2, 3]) == 6

@pytest.mark.integration
def test_save_to_database(db_session):
    user = User(name="Test")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None

@pytest.mark.e2e
def test_user_signup_flow(browser):
    browser.goto("/signup")
    browser.fill("email", "test@example.com")
    browser.click("Submit")
    assert browser.url == "/dashboard"

@pytest.mark.slow
def test_data_migration():
    migrate_all_records()  # Takes 30 seconds
```

```bash
# Run specific categories
pytest -m unit            # Only unit tests
pytest -m integration     # Only integration tests
pytest -m "not slow"      # Exclude slow tests
pytest -m "unit or integration"  # Both
```

## Parallel Testing

```python
# pytest.ini
[pytest]
# Safe for parallel execution
addopts = -n auto  # Use pytest-xdist

# conftest.py - ensure isolation
@pytest.fixture(scope="session")
def worker_id(request):
    """Get unique worker ID for parallel runs."""
    if hasattr(request.config, "workerinput"):
        return request.config.workerinput["workerid"]
    return "master"

@pytest.fixture(scope="session")
def db_name(worker_id):
    """Unique database per worker."""
    return f"testdb_{worker_id}"
```

## Test Naming Conventions

```python
# Pattern: test_<unit>_<condition>_<expected>

def test_user_creation_with_valid_data_succeeds():
    pass

def test_user_creation_with_missing_email_raises_validation_error():
    pass

def test_calculate_total_with_empty_list_returns_zero():
    pass

def test_api_users_get_without_auth_returns_401():
    pass


# Or use classes for grouping
class TestUserCreation:
    def test_with_valid_data_succeeds(self):
        pass

    def test_with_missing_email_raises_validation_error(self):
        pass

    def test_with_duplicate_email_raises_conflict_error(self):
        pass
```

## Fixture Organization

```python
# tests/fixtures/factories.py
import factory
from faker import Faker

fake = Faker()

class UserFactory(factory.Factory):
    class Meta:
        model = User

    name = factory.LazyAttribute(lambda _: fake.name())
    email = factory.LazyAttribute(lambda _: fake.email())

class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    total = factory.LazyAttribute(lambda _: fake.pydecimal(min_value=1, max_value=1000))


# tests/conftest.py
from tests.fixtures.factories import UserFactory, OrderFactory

@pytest.fixture
def user():
    return UserFactory()

@pytest.fixture
def order(user):
    return OrderFactory(user=user)
```

## Performance Testing

```python
# pip install pytest-benchmark

def test_sort_performance(benchmark):
    """Benchmark sorting algorithm."""
    data = list(range(10000, 0, -1))
    result = benchmark(sort, data)
    assert result == sorted(data)


# pip install pytest-timeout
@pytest.mark.timeout(5)  # Fail if takes >5 seconds
def test_with_timeout():
    slow_operation()


# Track memory
# pip install pytest-memray
@pytest.mark.limit_memory("100 MB")
def test_memory_usage():
    large_operation()
```

## Quick Reference

| Pattern | When to Use |
|---------|-------------|
| Transaction rollback | Database tests, fast isolation |
| TestContainers | Real service behavior needed |
| Schema isolation | Parallel test execution |
| Factory fixtures | Complex test data |
| Markers | Categorize and filter tests |
| conftest layers | Scope fixtures appropriately |

| Command | Purpose |
|---------|---------|
| `pytest -m unit` | Run unit tests only |
| `pytest -n auto` | Parallel execution |
| `pytest --lf` | Last failed only |
| `pytest -x` | Stop on first failure |
| `pytest --cov=src` | Coverage report |
