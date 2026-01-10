# Advanced Fixture Patterns

Deep dive into pytest fixtures for complex testing scenarios.

## Factory Fixtures

```python
import pytest
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str

@pytest.fixture
def user_factory():
    """Factory to create users with custom attributes."""
    def _create_user(
        id: int = 1,
        name: str = "Test User",
        email: str = "test@example.com"
    ) -> User:
        return User(id=id, name=name, email=email)
    return _create_user

def test_user_factory(user_factory):
    user1 = user_factory()
    user2 = user_factory(id=2, name="Another User")
    assert user1.id != user2.id
```

## Fixture Dependencies

```python
@pytest.fixture
def database():
    """Base database fixture."""
    db = connect_to_test_db()
    yield db
    db.close()

@pytest.fixture
def clean_database(database):
    """Depends on database, adds cleanup."""
    database.clear_all()
    yield database
    database.clear_all()

@pytest.fixture
def seeded_database(clean_database):
    """Depends on clean_database, adds seed data."""
    clean_database.insert(SEED_DATA)
    return clean_database
```

## Autouse Fixtures

```python
@pytest.fixture(autouse=True)
def reset_environment():
    """Runs automatically before each test."""
    os.environ.clear()
    os.environ.update(TEST_ENV)
    yield
    os.environ.clear()

@pytest.fixture(autouse=True, scope="module")
def setup_logging():
    """Module-level autouse fixture."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)
```

## Request Fixture

```python
@pytest.fixture
def temp_file(request, tmp_path):
    """Fixture that adapts based on test parameters."""
    # Access test-specific data
    filename = getattr(request, "param", "default.txt")
    file_path = tmp_path / filename
    file_path.write_text("test content")
    return file_path

@pytest.mark.parametrize("temp_file", ["custom.txt"], indirect=True)
def test_with_custom_filename(temp_file):
    assert temp_file.name == "custom.txt"
```

## Fixture Finalization

```python
@pytest.fixture
def resource_with_finalizer(request):
    """Using request.addfinalizer for cleanup."""
    resource = allocate_resource()

    def cleanup():
        resource.release()

    request.addfinalizer(cleanup)
    return resource

# Prefer yield-based cleanup when possible
@pytest.fixture
def resource_with_yield():
    """Preferred: yield-based cleanup."""
    resource = allocate_resource()
    yield resource
    resource.release()
```

## Fixture Caching

```python
@pytest.fixture(scope="session")
def expensive_computation():
    """Computed once, cached for entire session."""
    return perform_expensive_setup()

@pytest.fixture(scope="module")
def module_cache():
    """Cached per test module."""
    return load_module_data()
```

## Parametrized Fixtures

```python
@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database_backend(request):
    """Test runs 3 times, once per backend."""
    backend = request.param
    db = create_database(backend)
    yield db
    db.close()

def test_database_operations(database_backend):
    """This test runs against all 3 databases."""
    database_backend.insert({"key": "value"})
    assert database_backend.get("key") == "value"
```

## Fixture with IDs

```python
@pytest.fixture(
    params=[
        pytest.param({"user": "admin"}, id="admin-user"),
        pytest.param({"user": "guest"}, id="guest-user"),
    ]
)
def user_context(request):
    return request.param
```

## conftest.py Organization

```
tests/
├── conftest.py              # Session/package-wide fixtures
├── unit/
│   ├── conftest.py          # Unit test fixtures
│   └── test_module.py
├── integration/
│   ├── conftest.py          # Integration fixtures
│   └── test_api.py
└── e2e/
    ├── conftest.py          # E2E fixtures
    └── test_flows.py
```

### conftest.py Example

```python
# tests/conftest.py
import pytest

def pytest_configure(config):
    """Called after command line parsing."""
    config.addinivalue_line("markers", "slow: marks slow tests")

def pytest_collection_modifyitems(config, items):
    """Modify collected tests."""
    if config.getoption("--quick"):
        skip_slow = pytest.mark.skip(reason="--quick mode")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

@pytest.fixture(scope="session")
def app():
    """Application for all tests."""
    from myapp import create_app
    return create_app(testing=True)

@pytest.fixture
def client(app):
    """Test client per test."""
    return app.test_client()

@pytest.fixture
def authenticated_client(client):
    """Client with auth token."""
    client.post("/login", json={"user": "test", "pass": "test"})
    return client
```

## Fixture Best Practices

1. **Single responsibility** - Each fixture does one thing
2. **Use factory fixtures** - When tests need variations
3. **Scope appropriately** - Don't over-cache or under-cache
4. **Prefer yield** - Over request.addfinalizer
5. **Name clearly** - `db_connection` not `fixture1`
6. **Document** - Explain what fixture provides and when to use
7. **Minimize side effects** - Clean up after yourself
