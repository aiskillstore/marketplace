# Database Migrations with Alembic

Schema migration patterns for SQLAlchemy projects.

## Setup

```bash
# Install
pip install alembic

# Initialize in project root
alembic init alembic

# For async projects
alembic init -t async alembic
```

## Configuration

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.models import Base  # Your declarative base
from app.config import settings

config = context.config

# Set database URL from settings
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online():
    import asyncio
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Common Commands

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "add users table"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --indicate-current
```

## Migration Script Example

```python
"""Add users table

Revision ID: abc123
Revises:
Create Date: 2024-01-15 10:00:00.000000
"""
from typing import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = 'abc123'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])


def downgrade() -> None:
    op.drop_index('ix_users_email')
    op.drop_table('users')
```

## Data Migrations

```python
"""Migrate user names to lowercase

Revision ID: def456
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

revision = 'def456'
down_revision = 'abc123'


def upgrade() -> None:
    # Define table structure for data migration
    users = table(
        'users',
        column('id', sa.Integer),
        column('name', sa.String),
    )

    # Update data
    op.execute(
        users.update().values(name=sa.func.lower(users.c.name))
    )


def downgrade() -> None:
    # Data migrations are often one-way
    pass


# For complex data migrations
def upgrade() -> None:
    connection = op.get_bind()

    # Read in batches
    results = connection.execute(
        sa.text("SELECT id, name FROM users")
    )

    for batch in results.partitions(1000):
        for row in batch:
            connection.execute(
                sa.text("UPDATE users SET name = :name WHERE id = :id"),
                {"id": row.id, "name": row.name.lower()}
            )
```

## Adding Columns Safely

```python
"""Add nullable column first, then populate

Production-safe column addition for large tables.
"""

def upgrade() -> None:
    # Step 1: Add nullable column (fast, no table rewrite)
    op.add_column(
        'users',
        sa.Column('phone', sa.String(20), nullable=True)
    )

    # Step 2: Populate data (can be done in batches)
    # This is often done in a separate migration or script

    # Step 3: Add constraint (in a later migration after data is populated)
    # op.alter_column('users', 'phone', nullable=False)


def downgrade() -> None:
    op.drop_column('users', 'phone')
```

## Renaming Columns

```python
"""Rename column with zero downtime

Use a multi-step approach for production.
"""

# Migration 1: Add new column
def upgrade() -> None:
    op.add_column('users', sa.Column('full_name', sa.String(200)))
    # Copy data
    op.execute("UPDATE users SET full_name = name")

def downgrade() -> None:
    op.drop_column('users', 'full_name')


# Migration 2: Drop old column (after app updated to use new column)
def upgrade() -> None:
    op.drop_column('users', 'name')

def downgrade() -> None:
    op.add_column('users', sa.Column('name', sa.String(100)))
    op.execute("UPDATE users SET name = full_name")
```

## Index Management

```python
"""Add index concurrently (PostgreSQL)

Non-blocking index creation for large tables.
"""
from alembic import op

def upgrade() -> None:
    # Create index without locking table (PostgreSQL)
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
        ix_users_created_at ON users (created_at)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_users_created_at")


# Note: CONCURRENTLY cannot run inside a transaction
# Add to migration script:
# from alembic import context
# context.execute_ddl_statements = True
```

## Multi-Database Migrations

```python
# alembic.ini
[alembic]
script_location = alembic

[primary]
sqlalchemy.url = postgresql://user:pass@primary/db

[analytics]
sqlalchemy.url = postgresql://user:pass@analytics/db
```

```bash
# Run migrations for specific database
alembic -n primary upgrade head
alembic -n analytics upgrade head
```

## Testing Migrations

```python
import pytest
from alembic import command
from alembic.config import Config

@pytest.fixture
def alembic_config():
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", "sqlite:///:memory:")
    return config

def test_migrations_up_down(alembic_config):
    """Test that all migrations apply and rollback cleanly."""
    # Apply all migrations
    command.upgrade(alembic_config, "head")

    # Rollback all migrations
    command.downgrade(alembic_config, "base")

    # Apply again
    command.upgrade(alembic_config, "head")


def test_migration_idempotent(alembic_config):
    """Test migrations can be run multiple times."""
    command.upgrade(alembic_config, "head")
    command.upgrade(alembic_config, "head")  # Should be no-op
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `alembic revision --autogenerate -m "msg"` | Generate migration |
| `alembic upgrade head` | Apply all migrations |
| `alembic downgrade -1` | Rollback one |
| `alembic current` | Show current version |
| `alembic history` | List all migrations |

| Operation | Method |
|-----------|--------|
| Create table | `op.create_table()` |
| Drop table | `op.drop_table()` |
| Add column | `op.add_column()` |
| Drop column | `op.drop_column()` |
| Alter column | `op.alter_column()` |
| Create index | `op.create_index()` |
| Execute SQL | `op.execute()` |
