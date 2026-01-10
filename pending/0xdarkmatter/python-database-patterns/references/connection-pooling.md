# Connection Pool Configuration

Database connection pool patterns for production.

## SQLAlchemy Pool Settings

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

# Sync engine with pool config
engine = create_engine(
    "postgresql://user:pass@localhost/db",

    # Pool size
    pool_size=5,           # Persistent connections (default: 5)
    max_overflow=10,       # Extra connections when pool exhausted
    # Total max connections = pool_size + max_overflow = 15

    # Timeouts
    pool_timeout=30,       # Wait for connection (seconds)
    pool_recycle=3600,     # Recycle connections after N seconds
    pool_pre_ping=True,    # Test connections before use

    # Connection args
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000",  # 30s query timeout
    },
)


# Async engine
async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
)
```

## Pool Sizing Guidelines

```python
"""
Connection Pool Sizing

Rule of thumb:
    pool_size = (CPU cores × 2) + disk spindles

For async applications:
    pool_size = expected_concurrent_requests / avg_queries_per_request

Examples:
    - Web app, 4 cores, SSD:  pool_size=10, max_overflow=10
    - Worker, 4 cores, HDD:   pool_size=12, max_overflow=5
    - High-traffic API:       pool_size=20, max_overflow=30
"""

import os

def calculate_pool_size() -> tuple[int, int]:
    """Calculate pool size based on environment."""
    cpu_count = os.cpu_count() or 4

    if os.getenv("ENV") == "production":
        pool_size = cpu_count * 2 + 4
        max_overflow = pool_size
    else:
        pool_size = 5
        max_overflow = 5

    return pool_size, max_overflow

pool_size, max_overflow = calculate_pool_size()
```

## Pool Events and Monitoring

```python
from sqlalchemy import event
from sqlalchemy.pool import Pool
import logging

logger = logging.getLogger(__name__)

@event.listens_for(Pool, "connect")
def on_connect(dbapi_conn, connection_record):
    """Called when a new connection is created."""
    logger.debug("New database connection created")

@event.listens_for(Pool, "checkout")
def on_checkout(dbapi_conn, connection_record, connection_proxy):
    """Called when a connection is retrieved from pool."""
    logger.debug("Connection checked out from pool")

@event.listens_for(Pool, "checkin")
def on_checkin(dbapi_conn, connection_record):
    """Called when a connection is returned to pool."""
    logger.debug("Connection returned to pool")

@event.listens_for(Pool, "invalidate")
def on_invalidate(dbapi_conn, connection_record, exception):
    """Called when a connection is invalidated."""
    logger.warning(f"Connection invalidated: {exception}")


# Pool statistics
def log_pool_status(engine):
    """Log current pool status."""
    pool = engine.pool
    logger.info(
        f"Pool status: "
        f"size={pool.size()}, "
        f"checked_out={pool.checkedout()}, "
        f"overflow={pool.overflow()}, "
        f"checkedin={pool.checkedin()}"
    )
```

## Health Check Endpoint

```python
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
import asyncio

app = FastAPI()

async def check_database_health(timeout: float = 5.0) -> dict:
    """Check database connectivity and response time."""
    try:
        start = asyncio.get_event_loop().time()

        async with async_session_factory() as session:
            await asyncio.wait_for(
                session.execute(text("SELECT 1")),
                timeout=timeout
            )

        latency = (asyncio.get_event_loop().time() - start) * 1000

        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "pool_size": async_engine.pool.size(),
            "pool_checked_out": async_engine.pool.checkedout(),
        }
    except asyncio.TimeoutError:
        return {"status": "unhealthy", "error": "timeout"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/health/db")
async def database_health():
    health = await check_database_health()
    if health["status"] != "healthy":
        raise HTTPException(status_code=503, detail=health)
    return health
```

## Connection Pool per Service

```python
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

@dataclass
class DatabaseConfig:
    url: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600

class DatabasePool:
    """Manage multiple database connections."""

    def __init__(self):
        self._engines: dict[str, AsyncEngine] = {}

    def add_database(self, name: str, config: DatabaseConfig):
        """Add a database connection pool."""
        self._engines[name] = create_async_engine(
            config.url,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_timeout=config.pool_timeout,
            pool_recycle=config.pool_recycle,
            pool_pre_ping=True,
        )

    def get_engine(self, name: str) -> AsyncEngine:
        return self._engines[name]

    async def close_all(self):
        """Close all connection pools."""
        for engine in self._engines.values():
            await engine.dispose()


# Usage
db_pool = DatabasePool()

db_pool.add_database("primary", DatabaseConfig(
    url="postgresql+asyncpg://user:pass@primary/db",
    pool_size=10,
))

db_pool.add_database("replica", DatabaseConfig(
    url="postgresql+asyncpg://user:pass@replica/db",
    pool_size=20,  # More connections for read replica
))
```

## Read/Write Splitting

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Separate session factories for read/write
write_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@primary/db",
    pool_size=10,
)

read_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@replica/db",
    pool_size=20,
)

write_session = async_sessionmaker(write_engine, expire_on_commit=False)
read_session = async_sessionmaker(read_engine, expire_on_commit=False)


# FastAPI dependencies
async def get_write_db():
    async with write_session() as session:
        yield session

async def get_read_db():
    async with read_session() as session:
        yield session

WriteDB = Annotated[AsyncSession, Depends(get_write_db)]
ReadDB = Annotated[AsyncSession, Depends(get_read_db)]


@app.get("/users")
async def list_users(db: ReadDB):  # Read from replica
    result = await db.execute(select(User))
    return result.scalars().all()

@app.post("/users")
async def create_user(user: UserCreate, db: WriteDB):  # Write to primary
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    return db_user
```

## Graceful Shutdown

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - engines already created
    yield
    # Shutdown - close all pools gracefully
    await async_engine.dispose()
    logger.info("Database connections closed")

app = FastAPI(lifespan=lifespan)
```

## Quick Reference

| Setting | Purpose | Typical Value |
|---------|---------|---------------|
| `pool_size` | Persistent connections | 5-20 |
| `max_overflow` | Extra connections | 10-30 |
| `pool_timeout` | Wait for connection | 30s |
| `pool_recycle` | Recycle connection age | 3600s |
| `pool_pre_ping` | Test before use | True |

| Scenario | pool_size | max_overflow |
|----------|-----------|--------------|
| Development | 5 | 5 |
| Small API | 10 | 10 |
| High-traffic | 20 | 30 |
| Background worker | 5 | 5 |
