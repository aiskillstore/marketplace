---
name: python-fastapi-patterns
description: "FastAPI web framework patterns. Triggers on: fastapi, api endpoint, dependency injection, pydantic model, openapi, swagger, starlette, async api, rest api, uvicorn."
compatibility: "FastAPI 0.100+, Pydantic v2, Python 3.10+. Requires uvicorn for production."
allowed-tools: "Read Write Bash"
depends-on: [python-typing-patterns, python-async-patterns]
related-skills: [python-database-patterns, python-observability-patterns, python-pytest-patterns]
---

# FastAPI Patterns

Modern async API development with FastAPI.

## Basic Application

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    app.state.db = await create_db_pool()
    yield
    # Shutdown
    await app.state.db.close()

app = FastAPI(
    title="My API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Request/Response Models

```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    """Request model with validation."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)

class UserResponse(BaseModel):
    """Response model."""
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}  # Enable ORM mode

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    db_user = await create_user_in_db(user)
    return db_user
```

## Path and Query Parameters

```python
from fastapi import Query, Path
from typing import Annotated

@app.get("/users/{user_id}")
async def get_user(
    user_id: Annotated[int, Path(..., ge=1, description="User ID")],
):
    return await fetch_user(user_id)

@app.get("/users")
async def list_users(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    search: str | None = None,
):
    return await fetch_users(skip=skip, limit=limit, search=search)
```

## Dependency Injection

```python
from fastapi import Depends
from typing import Annotated

async def get_db():
    """Database session dependency."""
    async with async_session() as session:
        yield session

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Authenticate and return current user."""
    user = await authenticate_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# Annotated types for reuse
DB = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@app.get("/me")
async def get_me(user: CurrentUser):
    return user
```

## Exception Handling

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Built-in HTTP exceptions
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    item = await fetch_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Custom exception handler
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Item {exc.item_id} not found"},
    )
```

## Router Organization

```python
from fastapi import APIRouter

# users.py
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def list_users():
    return []

@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id}

# main.py
from app.routers import users, items

app.include_router(users.router)
app.include_router(items.router, prefix="/api/v1")
```

## Quick Reference

| Feature | Usage |
|---------|-------|
| Path param | `@app.get("/items/{id}")` |
| Query param | `def f(q: str = None)` |
| Body | `def f(item: ItemCreate)` |
| Dependency | `Depends(get_db)` |
| Auth | `Depends(get_current_user)` |
| Response model | `response_model=ItemResponse` |
| Status code | `status_code=201` |

## Additional Resources

- `./references/dependency-injection.md` - Advanced DI patterns, scopes, caching
- `./references/middleware-patterns.md` - Middleware chains, CORS, error handling
- `./references/validation-serialization.md` - Pydantic v2 patterns, custom validators
- `./references/background-tasks.md` - Background tasks, async workers, scheduling

## Scripts

- `./scripts/scaffold-api.sh` - Generate API endpoint boilerplate

## Assets

- `./assets/fastapi-template.py` - Production-ready FastAPI app skeleton

---

## See Also

**Prerequisites:**
- `python-typing-patterns` - Pydantic models and type hints
- `python-async-patterns` - Async endpoint patterns

**Related Skills:**
- `python-database-patterns` - SQLAlchemy integration
- `python-observability-patterns` - Logging, metrics, tracing middleware
- `python-pytest-patterns` - API testing with TestClient
