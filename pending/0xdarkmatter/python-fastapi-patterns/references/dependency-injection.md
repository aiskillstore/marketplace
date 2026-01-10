# FastAPI Dependency Injection Patterns

Advanced patterns for managing dependencies in FastAPI.

## Basic Dependencies

```python
from fastapi import Depends, FastAPI
from typing import Annotated

app = FastAPI()

# Simple dependency
async def get_db():
    db = DatabaseSession()
    try:
        yield db
    finally:
        await db.close()

# Use with Annotated for reusability
DB = Annotated[DatabaseSession, Depends(get_db)]

@app.get("/items")
async def get_items(db: DB):
    return await db.fetch_all("SELECT * FROM items")
```

## Dependency Hierarchy

```python
from fastapi import Depends, HTTPException, Header
from typing import Annotated

# Base dependency
async def get_db():
    async with async_session() as session:
        yield session

# Depends on get_db
async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Header()],
) -> User:
    user = await db.execute(
        select(User).where(User.token == token)
    )
    if not user:
        raise HTTPException(status_code=401)
    return user.scalar_one()

# Depends on get_current_user
async def get_admin_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403)
    return user

# Reusable annotated types
DB = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(get_admin_user)]

@app.get("/admin/users")
async def admin_list_users(admin: AdminUser, db: DB):
    return await db.execute(select(User)).scalars().all()
```

## Class-Based Dependencies

```python
from dataclasses import dataclass
from fastapi import Depends, Query
from typing import Annotated

@dataclass
class Pagination:
    """Reusable pagination parameters."""
    skip: int = 0
    limit: int = 10

    def __init__(
        self,
        skip: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 10,
    ):
        self.skip = skip
        self.limit = limit

# Use as dependency
@app.get("/items")
async def list_items(pagination: Annotated[Pagination, Depends()]):
    return await fetch_items(
        skip=pagination.skip,
        limit=pagination.limit
    )


# Class with injected dependencies
class UserService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def get_user(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends()],
):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404)
    return user
```

## Cached Dependencies

```python
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    api_key: str

    model_config = {"env_file": ".env"}

@lru_cache
def get_settings() -> Settings:
    """Cached settings - loaded once."""
    return Settings()

# Use in dependencies
async def get_db(settings: Annotated[Settings, Depends(get_settings)]):
    engine = create_async_engine(settings.database_url)
    async with AsyncSession(engine) as session:
        yield session
```

## Request-Scoped State

```python
from fastapi import Request
from contextvars import ContextVar
from uuid import uuid4

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar("request_id")

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid4())
    request_id_var.set(request_id)
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Access in dependencies
def get_request_id() -> str:
    return request_id_var.get()

@app.get("/trace")
async def trace_request(request_id: Annotated[str, Depends(get_request_id)]):
    return {"request_id": request_id}
```

## Dependency Overrides for Testing

```python
from fastapi.testclient import TestClient

# Production dependency
async def get_db():
    async with async_session() as session:
        yield session

# Test override
async def get_test_db():
    async with test_session() as session:
        yield session

def test_create_user():
    app.dependency_overrides[get_db] = get_test_db

    with TestClient(app) as client:
        response = client.post("/users", json={"name": "Test"})
        assert response.status_code == 201

    app.dependency_overrides.clear()


# Context manager for cleaner tests
from contextlib import contextmanager

@contextmanager
def override_dependency(original, replacement):
    app.dependency_overrides[original] = replacement
    try:
        yield
    finally:
        app.dependency_overrides.pop(original, None)

def test_with_override():
    with override_dependency(get_db, get_test_db):
        # Test code here
        pass
```

## Parameterized Dependencies

```python
from fastapi import Depends
from typing import Callable

def require_permission(permission: str):
    """Factory for permission-checking dependencies."""
    async def check_permission(
        user: Annotated[User, Depends(get_current_user)],
    ):
        if permission not in user.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Missing permission: {permission}"
            )
        return user
    return check_permission

@app.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    user: Annotated[User, Depends(require_permission("items:delete"))],
):
    return {"deleted": item_id}


# Rate limiting factory
def rate_limit(requests: int, window: int):
    """Create rate limit dependency."""
    async def check_rate(
        request: Request,
        redis: Annotated[Redis, Depends(get_redis)],
    ):
        key = f"rate:{request.client.host}"
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, window)
        if count > requests:
            raise HTTPException(status_code=429, detail="Rate limited")
    return check_rate

@app.get("/api/search")
async def search(
    q: str,
    _: Annotated[None, Depends(rate_limit(requests=100, window=60))],
):
    return {"query": q}
```

## Sub-Application Dependencies

```python
from fastapi import FastAPI, Depends

# Shared dependency for sub-app
async def get_api_key(x_api_key: Annotated[str, Header()]):
    if x_api_key != "secret":
        raise HTTPException(status_code=401)
    return x_api_key

# Sub-application with its own dependencies
api_v1 = FastAPI(dependencies=[Depends(get_api_key)])

@api_v1.get("/items")
async def list_items():
    return []

# Mount on main app
app = FastAPI()
app.mount("/api/v1", api_v1)
```

## Quick Reference

| Pattern | Use Case |
|---------|----------|
| `Annotated[T, Depends(f)]` | Reusable dependency type |
| Class dependency | Group related params |
| `@lru_cache` | Cache settings/config |
| Dependency factory | Parameterized checks |
| `dependency_overrides` | Testing isolation |
| Hierarchy | Auth → User → Admin chain |
| `ContextVar` | Request-scoped state |
