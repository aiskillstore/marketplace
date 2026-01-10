---
name: python-fastapi
description: Python FastAPI development with uv package manager, modular project structure, SQLAlchemy ORM, and production-ready patterns.
alwaysApply: false
---

# Python FastAPI Development

Expert patterns for building Python APIs with FastAPI, uv package manager, modular architecture, and SQLAlchemy database integration.

## Technology Stack

- **Runtime**: Python 3.12+
- **Package Manager**: uv (fast, Rust-based)
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2
- **Database**: PostgreSQL (or SQLite for dev)
- **Migrations**: Alembic
- **Testing**: pytest, pytest-asyncio
- **Linting**: ruff

## Project Structure

Feature-based modular architecture - code organized by domain, not by layer:

```
my-project/
├── pyproject.toml           # Project config with uv
├── uv.lock                   # Lock file
├── .python-version           # Python version
├── .env                      # Environment variables
├── .env.example
├── alembic.ini               # Alembic config
├── alembic/                  # Migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py           # FastAPI app entry
│       ├── config.py         # Settings
│       ├── database.py       # DB session
│       ├── core/
│       │   ├── __init__.py
│       │   ├── dependencies.py  # Shared dependencies
│       │   ├── exceptions.py    # Custom exceptions
│       │   ├── middleware.py    # Middleware
│       │   └── security.py      # Auth utilities
│       ├── models/
│       │   ├── __init__.py
│       │   └── base.py          # SQLAlchemy base & mixins
│       ├── features/
│       │   ├── __init__.py
│       │   ├── auth/
│       │   │   ├── __init__.py
│       │   │   ├── api.py       # Auth endpoints
│       │   │   ├── schemas.py   # Auth Pydantic schemas
│       │   │   ├── services.py  # Auth business logic
│       │   │   ├── models.py    # Auth SQLAlchemy models
│       │   │   └── utils.py     # Auth helpers (JWT, etc.)
│       │   ├── users/
│       │   │   ├── __init__.py
│       │   │   ├── api.py       # User endpoints
│       │   │   ├── schemas.py   # User Pydantic schemas
│       │   │   ├── services.py  # User business logic
│       │   │   ├── models.py    # User SQLAlchemy models
│       │   │   └── repository.py # User data access
│       │   └── items/
│       │       ├── __init__.py
│       │       ├── api.py
│       │       ├── schemas.py
│       │       ├── services.py
│       │       └── models.py
│       └── api/
│           ├── __init__.py
│           └── router.py        # Aggregates all feature routers
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── features/
    │   ├── auth/
    │   │   └── test_auth.py
    │   └── users/
    │       └── test_users.py
    └── integration/
```

## Quick Setup with uv

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create new project
uv init my-project
cd my-project

# Set Python version
uv python pin 3.12

# Add dependencies
uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg
uv add pydantic pydantic-settings python-dotenv
uv add alembic

# Add dev dependencies
uv add --dev pytest pytest-asyncio pytest-cov httpx ruff mypy

# Create source structure
mkdir -p src/app/{api/v1/endpoints,core,models,schemas,services,repositories}
touch src/app/__init__.py
```

## Core Patterns

### pyproject.toml

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "FastAPI application"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "python-dotenv>=1.0.0",
    "alembic>=1.14.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.28.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]

[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.mypy]
python_version = "3.12"
strict = true
```

### Configuration (src/app/config.py)

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "My API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/db"

    # Security
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

### Database Setup (src/app/database.py)

```python
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### SQLAlchemy Base Model (src/app/models/base.py)

```python
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
```

## Feature Module Pattern

Each feature is self-contained with its own api, schemas, services, models, and utils.

### Feature: users/schemas.py

```python
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
```

### Feature: users/models.py

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
```

### Feature: users/repository.py

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.users.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, data: dict) -> User:
        user = User(**data)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, data: dict) -> User:
        for field, value in data.items():
            if value is not None:
                setattr(user, field, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user
```

### Feature: users/services.py

```python
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.features.users.models import User
from app.features.users.repository import UserRepository
from app.features.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def get(self, user_id: int) -> User | None:
        return await self.repo.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return await self.repo.get_by_email(email)

    async def list(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def create(self, user_in: UserCreate) -> User:
        data = user_in.model_dump()
        data["hashed_password"] = hash_password(data.pop("password"))
        return await self.repo.create(data)

    async def update(self, user: User, user_in: UserUpdate) -> User:
        data = user_in.model_dump(exclude_unset=True)
        if "password" in data:
            data["hashed_password"] = hash_password(data.pop("password"))
        return await self.repo.update(user, data)
```

### Feature: users/api.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.features.users.schemas import UserCreate, UserResponse, UserUpdate
from app.features.users.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_service),
):
    return await service.list(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_service),
):
    user = await service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    service: UserService = Depends(get_service),
):
    if await service.get_by_email(user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return await service.create(user_in)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    service: UserService = Depends(get_service),
):
    user = await service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await service.update(user, user_in)
```

### Feature: users/__init__.py (exports)

```python
from app.features.users.api import router
from app.features.users.models import User
from app.features.users.schemas import UserCreate, UserResponse, UserUpdate
from app.features.users.services import UserService

__all__ = ["router", "User", "UserCreate", "UserResponse", "UserUpdate", "UserService"]
```

### Main Router (src/app/api/router.py)

```python
from fastapi import APIRouter

from app.features.auth import router as auth_router
from app.features.users import router as users_router
from app.features.items import router as items_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(items_router)
```

### FastAPI App (src/app/main.py)

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Database Migrations with Alembic

```bash
# Initialize Alembic
uv run alembic init alembic

# Update alembic/env.py for async
# Then create migration
uv run alembic revision --autogenerate -m "Initial migration"

# Apply migrations
uv run alembic upgrade head
```

### Async Alembic env.py

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.config import settings
from app.models.base import Base
from app.models import user, item  # Import all models

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Testing

### conftest.py

```python
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import get_db
from app.models.base import Base


@pytest.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
```

### Example Test

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/users",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
```

## Running the Application

```bash
# Development
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Run tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Lint and format
uv run ruff check .
uv run ruff format .

# Type check
uv run mypy src/
```

## Best Practices

1. **Layered Architecture**
   - Routes: Handle HTTP, validation, response formatting
   - Services: Business logic, orchestration
   - Repositories: Data access, queries

2. **Dependency Injection**
   - Use FastAPI's `Depends()` for clean DI
   - Inject database sessions, services, configs

3. **Type Safety**
   - Use Pydantic for all request/response schemas
   - Use SQLAlchemy 2.0 mapped columns with types
   - Enable strict mypy

4. **Async First**
   - Use async/await throughout
   - Use asyncpg for PostgreSQL
   - Use aiosqlite for testing

5. **Configuration**
   - Use pydantic-settings for type-safe config
   - Load from environment variables
   - Never commit secrets

6. **Testing**
   - Use in-memory SQLite for unit tests
   - Use test containers for integration tests
   - Mock external services
