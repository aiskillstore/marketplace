# Integration Testing Patterns

Patterns for testing real systems, databases, and APIs.

## Database Testing with Transactions

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine("postgresql://test:test@localhost/testdb")
    return engine

@pytest.fixture(scope="session")
def tables(engine):
    """Create all tables once per session."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, tables):
    """
    Transaction rollback fixture.
    Each test runs in a transaction that's rolled back.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


def test_user_creation(db_session):
    """Test runs in rolled-back transaction."""
    user = User(name="Test")
    db_session.add(user)
    db_session.commit()  # Committed to transaction, not DB
    assert db_session.query(User).count() == 1
    # Rolled back after test - no cleanup needed
```

## Async Database Testing

```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/testdb")
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def async_session(async_engine):
    """Async session with rollback."""
    async with async_engine.connect() as conn:
        await conn.begin()
        async_session = AsyncSession(bind=conn)

        yield async_session

        await async_session.close()
        await conn.rollback()


@pytest.mark.asyncio
async def test_async_query(async_session):
    result = await async_session.execute(select(User))
    users = result.scalars().all()
    assert len(users) == 0
```

## TestContainers

```python
# pip install testcontainers

import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

@pytest.fixture(scope="session")
def postgres():
    """Spin up PostgreSQL container for tests."""
    with PostgresContainer("postgres:15") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def postgres_url(postgres):
    """Get connection URL for containerized PostgreSQL."""
    return postgres.get_connection_url()

@pytest.fixture(scope="session")
def redis():
    """Spin up Redis container for tests."""
    with RedisContainer("redis:7") as redis:
        yield redis

@pytest.fixture
def redis_client(redis):
    """Get Redis client for container."""
    import redis as redis_lib
    client = redis_lib.from_url(redis.get_container_host_ip())
    yield client
    client.flushdb()


def test_with_real_postgres(postgres_url):
    """Test against real PostgreSQL container."""
    engine = create_engine(postgres_url)
    # Use real database
```

## FastAPI / Starlette Testing

```python
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Synchronous testing
@pytest.fixture
def app():
    return create_app()

@pytest.fixture
def client(app):
    """Sync test client."""
    return TestClient(app)

def test_endpoint(client):
    response = client.get("/api/users")
    assert response.status_code == 200
    assert "users" in response.json()


# Async testing with httpx
@pytest.fixture
async def async_client(app):
    """Async test client for async endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    response = await async_client.get("/api/users")
    assert response.status_code == 200


# With database override
@pytest.fixture
def app_with_db(db_session):
    """Override database dependency."""
    app = create_app()

    def get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = get_test_db
    yield app
    app.dependency_overrides.clear()
```

## API Testing Patterns

```python
import pytest
from dataclasses import dataclass

@dataclass
class APITestCase:
    """Structured API test case."""
    method: str
    path: str
    json: dict | None = None
    expected_status: int = 200
    expected_json: dict | None = None
    headers: dict | None = None

@pytest.mark.parametrize("test_case", [
    APITestCase("GET", "/api/users", expected_status=200),
    APITestCase("POST", "/api/users", json={"name": "Test"}, expected_status=201),
    APITestCase("GET", "/api/users/999", expected_status=404),
])
def test_api_endpoints(client, test_case):
    """Parametrized API testing."""
    response = client.request(
        method=test_case.method,
        url=test_case.path,
        json=test_case.json,
        headers=test_case.headers,
    )
    assert response.status_code == test_case.expected_status

    if test_case.expected_json:
        assert response.json() == test_case.expected_json


# Request/Response validation
def test_user_creation_flow(client):
    """Test complete user flow."""
    # Create
    response = client.post("/api/users", json={"name": "Test User"})
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Read
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"

    # Update
    response = client.patch(f"/api/users/{user_id}", json={"name": "Updated"})
    assert response.status_code == 200

    # Delete
    response = client.delete(f"/api/users/{user_id}")
    assert response.status_code == 204
```

## Snapshot Testing

```python
# pip install syrupy

import pytest
from syrupy.assertion import SnapshotAssertion

def test_api_response_snapshot(client, snapshot: SnapshotAssertion):
    """Compare response against stored snapshot."""
    response = client.get("/api/config")
    assert response.json() == snapshot


def test_user_serialization(snapshot):
    """Snapshot complex objects."""
    user = User(id=1, name="Test", email="test@example.com")
    assert user.dict() == snapshot


# Update snapshots: pytest --snapshot-update
```

## External Service Mocking

```python
import pytest
import responses
import respx

# responses (requests library)
@responses.activate
def test_external_api():
    responses.add(
        responses.GET,
        "https://api.example.com/data",
        json={"result": "mocked"},
        status=200
    )

    result = fetch_from_external_api()
    assert result["result"] == "mocked"


# respx (httpx library)
@pytest.fixture
def mock_api():
    with respx.mock:
        yield respx

def test_httpx_external(mock_api):
    mock_api.get("https://api.example.com/data").respond(
        json={"result": "mocked"}
    )

    result = fetch_with_httpx()
    assert result["result"] == "mocked"
```

## Factory Fixtures for Integration Tests

```python
import pytest
from faker import Faker

fake = Faker()

@pytest.fixture
def user_factory(db_session):
    """Factory for creating test users."""
    created_users = []

    def _create_user(**kwargs):
        user = User(
            name=kwargs.get("name", fake.name()),
            email=kwargs.get("email", fake.email()),
            **kwargs
        )
        db_session.add(user)
        db_session.commit()
        created_users.append(user)
        return user

    yield _create_user

    # Cleanup handled by transaction rollback


def test_user_permissions(user_factory):
    admin = user_factory(role="admin")
    user = user_factory(role="user")

    assert admin.can_delete(user)
    assert not user.can_delete(admin)
```

## Quick Reference

| Pattern | Use Case | Key Benefit |
|---------|----------|-------------|
| Transaction rollback | DB tests | Zero cleanup needed |
| TestContainers | Real services | Production-like testing |
| TestClient | API testing | Full HTTP stack |
| Snapshot testing | Complex responses | Easy regression detection |
| Factory fixtures | Data creation | Flexible test data |
| respx/responses | External APIs | Isolated testing |
