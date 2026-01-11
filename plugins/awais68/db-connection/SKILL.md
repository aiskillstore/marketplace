---
name: db-connection
description: |
  Use when setting up database connections, especially for Neon PostgreSQL.
  Triggers for: Neon Postgres connection, connection pooling configuration,
  connection string management, SSL configuration, or SQLAlchemy engine setup.
  NOT for: CRUD operations (use @sqlmodel-crud) or migration scripts (use @db-migration).
---

# Database Connection Skill

Expert database connection management for Python/FastAPI with Neon PostgreSQL, connection pooling, and SSL configuration.

## Quick Reference

| Task | File/Method |
|------|-------------|
| Get engine | `get_engine()` |
| Get session | `get_session()` |
| Connection string | `DB_URL` from settings |
| Health check | `check_connection()` |

## Project Structure

```
backend/
├── app/
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py    # Engine and session setup
│   │   └── session.py       # Dependency injection
│   └── config/
│       └── settings.py      # Environment config
├── alembic/
│   └── env.py               # Uses connection from here
└── .env.example
```

## Connection Configuration

### Settings with DB URL

```python
# backend/app/config/settings.py
from functools import lru_cache
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database Configuration
    DB_URL: SecretStr = Field(
        ...,
        description="PostgreSQL connection URL",
        examples=["postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require"],
    )
    DB_POOL_SIZE: int = Field(default=5, ge=1, le=100)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=100)
    DB_POOL_TIMEOUT: int = Field(default=30, ge=1, le=300)
    DB_POOL_RECYCLE: int = Field(default=1800, ge=300)
    DB_ECHO: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### Environment Variables

```bash
# .env.example

# Database (Neon PostgreSQL)
# Get this from Neon Dashboard > Connection Details
# Format: postgresql://user:pass@host/dbname?sslmode=require
DB_URL="postgresql://username:password@ep-xxx.region.neon.tech/dbname?sslmode=require"

# Connection Pool Settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800

# Debug (set to true for development)
DB_ECHO=false
```

## SQLAlchemy Engine Setup

### Connection Module

```python
# backend/app/db/connection.py
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.config.settings import get_settings

logger = logging.getLogger(__name__)


def get_db_url() -> str:
    """Get database URL from settings."""
    settings = get_settings()
    db_url = settings.DB_URL
    # SecretStr has get_secret_value() method
    if hasattr(db_url, 'get_secret_value'):
        return db_url.get_secret_value()
    return str(db_url)


def create_sqlalchemy_engine() -> Engine:
    """Create SQLAlchemy engine with optimal settings for Neon/PostgreSQL."""
    settings = get_settings()
    db_url = get_db_url()

    engine = create_engine(
        db_url,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        echo=settings.DB_ECHO,
        # PostgreSQL-specific settings
        pool_pre_ping=True,  # Verify connections before use
        isolation_level="AUTOCOMMIT",
    )

    # Enable connection health checks
    @event.listens_for(engine, "connect")
    def set_session_vars(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        # Set session characteristics
        cursor.execute("SET statement_timeout = '30s'")
        cursor.execute("SET idle_in_transaction_session_timeout = '60000'")
        cursor.close()

    logger.info(f"Database engine created with pool_size={settings.DB_POOL_SIZE}")
    return engine


def get_engine() -> Engine:
    """Get or create database engine (singleton pattern)."""
    return create_sqlalchemy_engine()
```

### Session Management

```python
# backend/app/db/session.py
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.db.connection import get_engine


# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=get_engine(),
)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.

    Usage:
        @router.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> Generator[Session, None, None]:
    """
    Async database session dependency (for async routes).
    Note: Use with SQLModel async sessions or asyncpg.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Neon PostgreSQL Setup

### Neon Connection String Format

```
postgresql://[user]:[password]@[host]/[dbname]?sslmode=require
```

Components:
- **user**: Database username (from Neon)
- **password**: Database password (from Neon)
- **host**: Endpoint ID + region, e.g., `ep-xxx-12345.us-east-1.aws.neon.tech`
- **dbname**: Your database name
- **sslmode**: Must be `require` for Neon

### Getting Connection Details from Neon

1. Go to [Neon Dashboard](https://console.neon.tech)
2. Select your project
3. Go to **Connection Details**
4. Copy the connection string
5. Add to Vercel/Dashboard environment variables

### Connection Pooling for Neon

```python
# For serverless/edge functions, use lower pool sizes
# backend/app/db/connection.py

def create_serverless_engine() -> Engine:
    """Create engine optimized for serverless/Vercel functions."""
    settings = get_settings()

    # Smaller pool for serverless to avoid connection limits
    return create_engine(
        get_db_url(),
        pool_size=2,  # Keep small for serverless
        max_overflow=0,  # No overflow in serverless
        pool_timeout=10,  # Faster timeout
        pool_recycle=300,  # Recycle more frequently
        pool_pre_ping=True,
        echo=settings.DB_ECHO,
    )
```

## FastAPI Integration

### Application Setup

```python
# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.connection import get_engine
from app.db.session import get_db
from app.config.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Verify database connection
    settings = get_settings()
    engine = get_engine()

    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection verified successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

    yield

    # Shutdown: Close all connections
    engine.dispose()
    logger.info("Database connections closed")


app = FastAPI(lifespan=lifespan)


# Dependency injection works with any route
@app.get("/users/")
def get_users(db=Depends(get_db)):
    return db.query(User).all()
```

### Database Health Check

```python
# backend/app/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()


@router.get("/health/db")
def database_health(db: Session = Depends(get_db)) -> dict:
    """
    Check database connectivity.

    Returns:
        {
            "status": "healthy",
            "latency_ms": <response_time>,
            "database": <db_name>
        }
    """
    import time

    start = time.time()
    result = db.execute(text("SELECT 1"))
    latency_ms = (time.time() - start) * 1000

    return {
        "status": "healthy",
        "latency_ms": round(latency_ms, 2),
        "database": "postgresql",
    }
```

## SSL Configuration

### Required SSL Settings

```python
# Neon requires SSL - this is the default behavior
# No additional configuration needed when using ?sslmode=require

# Verify SSL certificate in production
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED
```

### Testing SSL Connection

```bash
# Test connection with SSL
psql "postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require" -c "SELECT 1"
```

## Connection Pool Monitoring

### Pool Statistics

```python
# backend/app/db/monitoring.py
from sqlalchemy.pool import QueuePool
from app.db.connection import get_engine


def get_pool_stats() -> dict:
    """Get connection pool statistics."""
    engine = get_engine()
    pool = engine.pool

    if isinstance(pool, QueuePool):
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkout(),
            "overflow": pool.overflow(),
            "status": "healthy" if pool.checkedin() >= 0 else "exhausted",
        }
    return {"status": "unknown", "pool_type": type(pool).__name__}


def check_connection_leaks() -> list:
    """Check for connection leaks."""
    stats = get_pool_stats()
    warnings = []

    if stats.get("checked_out", 0) > stats.get("size", 0) * 0.8:
        warnings.append("High connection checkout rate - possible leak")

    if stats.get("overflow", 0) > 10:
        warnings.append("High overflow - consider increasing pool size")

    return warnings
```

### Logging Queries (Debug)

```python
# backend/app/db/connection.py
import logging

logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)

# Add this to create_engine for query logging
# echo=True already handles basic logging

# For more detailed logging:
# from sqlalchemy import event
# @event.listens_for(Engine, "before_cursor_execute")
# def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
#     logger.info(f"Executing: {statement[:100]}...")
```

## Alembic Integration

### env.py Configuration

```python
# alembic/env.py
import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic.runtime.migration import MigrationContext

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import get_settings
from app.db.connection import get_engine
from app.models import Base  # Import all SQLModels


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    settings = get_settings()
    db_url = settings.DB_URL
    if hasattr(db_url, 'get_secret_value'):
        db_url = db_url.get_secret_value()

    context.configure(
        url=db_url,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    engine = get_engine()

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Quality Checklist

- [ ] **Connections reused**: Use pool_pre_ping, don't create new connections
- [ ] **No connection leaks**: Always close sessions in finally blocks
- [ ] **Production SSL enabled**: `?sslmode=require` in connection string
- [ ] **Local dev easy**: Can connect from local environment
- [ ] **Timeouts configured**: Pool timeout, statement timeout set
- [ ] **Pool size tuned**: Appropriate for expected concurrency
- [ ] **Health check endpoint**: `/health/db` returns status

## Integration Points

| Skill | Integration |
|-------|-------------|
| `@env-config` | Read DB_URL and pool settings from environment |
| `@sqlmodel-crud` | Uses session from get_db() dependency |
| `@db-migration` | Uses same engine/connection logic |
| `@fastapi-app` | Database dependency injection |
| `@error-handling` | Handle connection errors gracefully |

## Troubleshooting

### Connection Refused

```
Solution: Check DB_URL format, ensure Neon allows your IP
```

### Too Many Connections

```
Solution: Reduce pool_size, check for connection leaks
```

### SSL Certificate Error

```
Solution: Ensure sslmode=require in connection string
```

### Connection Timeout

```
Solution: Increase pool_timeout, check network latency
```

### Idle Connections

```
Solution: Set DB_POOL_RECYCLE lower, check application shutdown
```

## Environment-Specific Settings

```python
# backend/app/config/settings.py

class Settings(BaseSettings):
    # ... base settings

    @property
    def is_production(self) -> bool:
        return not self.DEBUG

    def get_pool_config(self) -> dict:
        """Get pool configuration based on environment."""
        if self.is_production:
            return {
                "pool_size": self.DB_POOL_SIZE,
                "max_overflow": self.DB_MAX_OVERFLOW,
                "pool_timeout": self.DB_POOL_TIMEOUT,
                "pool_recycle": self.DB_POOL_RECYCLE,
            }
        else:
            # Development: smaller pool, more lenient settings
            return {
                "pool_size": 2,
                "max_overflow": 5,
                "pool_timeout": 10,
                "pool_recycle": 300,
            }
```
