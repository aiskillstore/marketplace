# Async SQLAlchemy Patterns

Modern async database patterns with SQLAlchemy 2.0.

## Engine and Session Setup

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

# Create async engine
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=False,            # SQL logging
    pool_size=5,           # Connection pool size
    max_overflow=10,       # Extra connections allowed
    pool_pre_ping=True,    # Test connections before use
    pool_recycle=3600,     # Recycle connections after 1 hour
)

# Session factory (not the session itself)
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
)


# Usage with context manager
async def get_users():
    async with async_session_factory() as session:
        result = await session.execute(select(User))
        return result.scalars().all()
```

## Session Scopes

```python
# Per-request (FastAPI dependency)
async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Explicit transaction control
async def transfer_funds(from_id: int, to_id: int, amount: Decimal):
    async with async_session_factory() as session:
        async with session.begin():  # Auto-commit on success
            from_account = await session.get(Account, from_id)
            to_account = await session.get(Account, to_id)

            from_account.balance -= amount
            to_account.balance += amount
            # Commits automatically if no exception


# Nested transactions (savepoints)
async def complex_operation():
    async with async_session_factory() as session:
        async with session.begin():
            # Outer transaction
            user = User(name="Test")
            session.add(user)

            try:
                async with session.begin_nested():  # Savepoint
                    # Inner operation that might fail
                    await risky_operation(session)
            except RiskyOperationError:
                # Savepoint rolled back, outer continues
                pass

            await session.commit()
```

## Lazy Loading in Async

```python
from sqlalchemy.orm import selectinload, joinedload, subqueryload

# WRONG - lazy loading doesn't work in async
async def bad_example():
    async with async_session_factory() as session:
        user = await session.get(User, 1)
        # This raises an error!
        print(user.posts)  # MissingGreenlet error


# CORRECT - eager loading
async def good_example():
    async with async_session_factory() as session:
        # Option 1: selectinload (separate query per relationship)
        stmt = select(User).options(selectinload(User.posts))
        result = await session.execute(stmt)
        user = result.scalar_one()
        print(user.posts)  # Works!

        # Option 2: joinedload (single JOIN query)
        stmt = select(User).options(joinedload(User.profile))
        result = await session.execute(stmt)
        user = result.scalar_one()


# With nested relationships
stmt = select(User).options(
    selectinload(User.posts).selectinload(Post.comments)
)
```

## Async Session Dependency

```python
from fastapi import Depends
from typing import Annotated, AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI."""
    async with async_session_factory() as session:
        yield session

DB = Annotated[AsyncSession, Depends(get_db)]


# With automatic transaction handling
async def get_db_with_transaction() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

## Batch Operations

```python
from sqlalchemy import insert, update, delete

# Bulk insert
async def bulk_create_users(users_data: list[dict]):
    async with async_session_factory() as session:
        stmt = insert(User).values(users_data)
        await session.execute(stmt)
        await session.commit()


# Bulk update
async def deactivate_users(user_ids: list[int]):
    async with async_session_factory() as session:
        stmt = (
            update(User)
            .where(User.id.in_(user_ids))
            .values(is_active=False)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount


# Bulk delete
async def delete_old_posts(before_date: datetime):
    async with async_session_factory() as session:
        stmt = delete(Post).where(Post.created_at < before_date)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount


# Batch processing with chunks
async def process_all_users(batch_size: int = 100):
    async with async_session_factory() as session:
        offset = 0
        while True:
            stmt = select(User).offset(offset).limit(batch_size)
            result = await session.execute(stmt)
            users = result.scalars().all()

            if not users:
                break

            for user in users:
                await process_user(user)

            await session.commit()
            offset += batch_size
```

## Streaming Results

```python
from sqlalchemy import select

async def stream_large_table():
    """Process large tables without loading all into memory."""
    async with async_session_factory() as session:
        stmt = select(User).execution_options(yield_per=100)
        result = await session.stream(stmt)

        async for user in result.scalars():
            await process_user(user)


# Partitioned streaming
async def stream_partitioned():
    async with async_session_factory() as session:
        stmt = select(User).execution_options(yield_per=100)
        result = await session.stream(stmt)

        async for partition in result.scalars().partitions(100):
            # partition is a list of 100 users
            await process_batch(partition)
```

## Async Raw SQL

```python
from sqlalchemy import text

async def raw_query():
    async with async_session_factory() as session:
        # Simple query
        result = await session.execute(
            text("SELECT * FROM users WHERE is_active = :active"),
            {"active": True}
        )
        rows = result.fetchall()

        # With column access
        for row in rows:
            print(row.id, row.name)


async def raw_insert():
    async with async_session_factory() as session:
        await session.execute(
            text("INSERT INTO logs (message) VALUES (:msg)"),
            {"msg": "Test log"}
        )
        await session.commit()
```

## Testing with Async

```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def async_session(async_engine):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.mark.asyncio
async def test_create_user(async_session):
    user = User(name="Test", email="test@example.com")
    async_session.add(user)
    await async_session.flush()

    assert user.id is not None
```

## Quick Reference

| Pattern | Async SQLAlchemy |
|---------|------------------|
| Create engine | `create_async_engine(url)` |
| Session factory | `async_sessionmaker(engine)` |
| Get session | `async with factory() as session:` |
| Execute | `await session.execute(stmt)` |
| Get one | `result.scalar_one_or_none()` |
| Get all | `result.scalars().all()` |
| Stream | `await session.stream(stmt)` |
| Commit | `await session.commit()` |
| Transaction | `async with session.begin():` |
| Eager load | `.options(selectinload(rel))` |
