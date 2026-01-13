# Transaction Patterns

Database transaction management for data integrity.

## Basic Transaction Patterns

```python
from sqlalchemy.ext.asyncio import AsyncSession

# Pattern 1: Context manager (auto-commit/rollback)
async with async_session_factory() as session:
    async with session.begin():
        user = User(name="Test")
        session.add(user)
        # Auto-commits on exit, rollback on exception


# Pattern 2: Explicit control
async with async_session_factory() as session:
    try:
        user = User(name="Test")
        session.add(user)
        await session.commit()
    except Exception:
        await session.rollback()
        raise


# Pattern 3: Dependency with auto-commit
async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Nested Transactions (Savepoints)

```python
async def complex_operation():
    async with async_session_factory() as session:
        async with session.begin():
            # Create user (outer transaction)
            user = User(name="Test")
            session.add(user)
            await session.flush()  # Get user.id

            try:
                # Nested operation (savepoint)
                async with session.begin_nested():
                    profile = Profile(user_id=user.id, bio="Hello")
                    session.add(profile)
                    await session.flush()

                    # This might fail
                    await validate_profile(profile)

            except ValidationError:
                # Savepoint rolled back, but user is preserved
                logger.warning("Profile creation failed")

            # Commit user (profile may or may not exist)
            await session.commit()
```

## Unit of Work Pattern

```python
from typing import TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")

class UnitOfWork:
    """Coordinate multiple repository operations in a transaction."""

    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self):
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    @property
    def users(self) -> "UserRepository":
        return UserRepository(self._session)

    @property
    def orders(self) -> "OrderRepository":
        return OrderRepository(self._session)


# Usage
async def create_order_with_items(user_id: int, items: list):
    async with UnitOfWork(async_session_factory) as uow:
        user = await uow.users.get(user_id)
        if not user:
            raise NotFoundError("User not found")

        order = Order(user_id=user_id)
        order = await uow.orders.add(order)

        for item in items:
            await uow.orders.add_item(order.id, item)

        await uow.commit()
        return order
```

## Isolation Levels

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Engine-level default
engine = create_engine(
    "postgresql://...",
    isolation_level="REPEATABLE READ"  # Default for all sessions
)


# Per-session isolation
async with async_session_factory() as session:
    await session.connection(
        execution_options={"isolation_level": "SERIALIZABLE"}
    )
    # This session uses SERIALIZABLE isolation


# Transaction-level in raw SQL
async with async_session_factory() as session:
    await session.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
    # Perform operations
    await session.commit()
```

### Isolation Level Reference

| Level | Dirty Read | Non-repeatable Read | Phantom Read |
|-------|------------|---------------------|--------------|
| READ UNCOMMITTED | Possible | Possible | Possible |
| READ COMMITTED | No | Possible | Possible |
| REPEATABLE READ | No | No | Possible* |
| SERIALIZABLE | No | No | No |

*PostgreSQL prevents phantoms in REPEATABLE READ

## Optimistic Locking

```python
from sqlalchemy import Column, Integer
from sqlalchemy.orm import Mapped, mapped_column

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[int]
    version: Mapped[int] = mapped_column(default=0)

    __mapper_args__ = {"version_id_col": version}


async def transfer_funds(from_id: int, to_id: int, amount: int):
    """Transfer with optimistic locking."""
    async with async_session_factory() as session:
        from_account = await session.get(Account, from_id)
        to_account = await session.get(Account, to_id)

        if from_account.balance < amount:
            raise InsufficientFunds()

        from_account.balance -= amount
        to_account.balance += amount

        try:
            await session.commit()
        except StaleDataError:
            # Concurrent modification detected
            await session.rollback()
            raise ConcurrentModificationError()
```

## Pessimistic Locking

```python
from sqlalchemy import select

async def transfer_with_lock(from_id: int, to_id: int, amount: int):
    """Transfer with row-level lock."""
    async with async_session_factory() as session:
        async with session.begin():
            # Lock rows for update
            stmt = (
                select(Account)
                .where(Account.id.in_([from_id, to_id]))
                .with_for_update()  # SELECT ... FOR UPDATE
            )
            result = await session.execute(stmt)
            accounts = {a.id: a for a in result.scalars()}

            from_account = accounts[from_id]
            to_account = accounts[to_id]

            if from_account.balance < amount:
                raise InsufficientFunds()

            from_account.balance -= amount
            to_account.balance += amount
            # Commit releases locks


# Lock with options
stmt = select(Account).with_for_update(
    nowait=True,     # Fail immediately if locked
    skip_locked=True # Skip locked rows (for queue processing)
)
```

## Retry on Serialization Failure

```python
from sqlalchemy.exc import OperationalError
import asyncio

async def retry_on_conflict(
    func,
    max_retries: int = 3,
    base_delay: float = 0.1,
):
    """Retry transaction on serialization failure."""
    for attempt in range(max_retries):
        try:
            return await func()
        except OperationalError as e:
            if "serialization" in str(e).lower() or "deadlock" in str(e).lower():
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
            raise


# Usage
async def process_order(order_id: int):
    async def _process():
        async with async_session_factory() as session:
            async with session.begin():
                order = await session.get(Order, order_id)
                order.status = "processed"
                await session.commit()

    await retry_on_conflict(_process)
```

## Quick Reference

| Pattern | Use Case |
|---------|----------|
| `session.begin()` | Auto-commit/rollback |
| `session.begin_nested()` | Savepoint (partial rollback) |
| `with_for_update()` | Row-level locking |
| `version_id_col` | Optimistic concurrency |
| Isolation levels | Control visibility |

| Isolation Level | When to Use |
|-----------------|-------------|
| READ COMMITTED | Default, most apps |
| REPEATABLE READ | Reports, analytics |
| SERIALIZABLE | Financial, inventory |
