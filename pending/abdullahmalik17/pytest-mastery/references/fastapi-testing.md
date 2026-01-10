# FastAPI Testing Patterns

## TestClient Setup

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from myapp.main import app

@pytest.fixture
def client():
    return TestClient(app)
```

Basic test:
```python
def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

## Async Testing with httpx

For async endpoints, use `pytest-asyncio` and `httpx`:

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from myapp.main import app

@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
```

```python
import pytest

@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    response = await async_client.get("/async-endpoint")
    assert response.status_code == 200
```

Configure in pyproject.toml:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

## Database Testing

### SQLAlchemy with Test Database

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from myapp.database import Base, get_db
from myapp.main import app
from fastapi.testclient import TestClient

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

## Dependency Overrides

Override any FastAPI dependency for testing:

```python
# myapp/dependencies.py
async def get_current_user():
    # Real auth logic
    ...

# tests/conftest.py
from myapp.dependencies import get_current_user
from myapp.main import app

@pytest.fixture
def authenticated_client():
    def mock_current_user():
        return {"id": 1, "username": "testuser", "role": "admin"}

    app.dependency_overrides[get_current_user] = mock_current_user
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
```

## Testing Authentication

### JWT Token Testing

```python
@pytest.fixture
def auth_headers():
    # Create test token
    token = create_access_token(data={"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}

def test_protected_endpoint(client, auth_headers):
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 200
```

### OAuth2 Password Flow

```python
def test_login(client):
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Testing Request/Response Models

```python
from pydantic import ValidationError
from myapp.schemas import UserCreate

def test_user_schema_valid():
    user = UserCreate(email="test@example.com", password="secure123")
    assert user.email == "test@example.com"

def test_user_schema_invalid():
    with pytest.raises(ValidationError):
        UserCreate(email="invalid", password="")
```

## Testing File Uploads

```python
def test_upload_file(client):
    files = {"file": ("test.txt", b"file content", "text/plain")}
    response = client.post("/upload", files=files)
    assert response.status_code == 200
```

## Testing WebSockets

```python
def test_websocket(client):
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("hello")
        data = websocket.receive_text()
        assert data == "Message: hello"
```

## Testing Background Tasks

```python
from unittest.mock import patch

def test_with_background_task(client):
    with patch("myapp.tasks.send_email") as mock_send:
        response = client.post("/register", json={"email": "test@example.com"})
        assert response.status_code == 201
        mock_send.assert_called_once()
```

## Testing Error Responses

```python
def test_not_found(client):
    response = client.get("/items/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_validation_error(client):
    response = client.post("/items", json={"price": "invalid"})
    assert response.status_code == 422
```

## Testing with Lifespan Events

```python
@pytest.fixture
def client():
    # TestClient handles lifespan automatically
    with TestClient(app) as client:
        yield client
```

## Mocking External Services

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_external_api_call(async_client):
    mock_response = {"data": "mocked"}

    with patch("myapp.services.external_api.fetch", new_callable=AsyncMock) as mock:
        mock.return_value = mock_response
        response = await async_client.get("/external-data")
        assert response.status_code == 200
        mock.assert_called_once()
```

## Factory Pattern for Test Data

```python
# tests/factories.py
from myapp.models import User

class UserFactory:
    @staticmethod
    def create(db, **overrides):
        defaults = {
            "email": "test@example.com",
            "hashed_password": "hashed",
            "is_active": True
        }
        defaults.update(overrides)
        user = User(**defaults)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

# In tests
def test_get_user(client, db):
    user = UserFactory.create(db, email="specific@example.com")
    response = client.get(f"/users/{user.id}")
    assert response.json()["email"] == "specific@example.com"
```
