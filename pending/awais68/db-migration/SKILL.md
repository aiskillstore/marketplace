---
name: db-migration
description: |
  Use when setting up Alembic migrations or making database schema changes.
  Triggers for: initializing Alembic, generating migrations, applying upgrades,
  rolling back changes, or creating data migrations.
  NOT for: raw SQL execution outside migration context or non-database schema updates.
---

# Database Migration Skill

Expert Alembic migration management for SQLModel/FastAPI projects with safe schema evolution and rollback capabilities.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `alembic init alembic` | Initialize Alembic in project |
| `alembic revision --autogenerate -m "message"` | Generate migration from model changes |
| `alembic revision -m "message"` | Create empty migration manually |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic upgrade +1` | Apply one migration at a time |
| `alembic downgrade -1` | Rollback last migration |
| `alembic downgrade base` | Rollback all migrations |
| `alembic current` | Show current revision |
| `alembic history` | Show migration history |

## Initial Setup

### 1. Initialize Alembic

```bash
alembic init alembic
```

### 2. Configure alembic.ini

```ini
# alembic.ini
sqlalchemy.url = driver://user:pass@localhost/dbname
file_template = %%(year)s_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
timezone = UTC
```

### 3. Configure env.py for SQLModel

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic.runtime.migration import MigrationContext
from sqlmodel import SQLModel, create_engine
from myapp.models import *  # Import all SQLModel classes

config = context.config
config.set_main_option("sqlalchemy.url", "postgresql://user:pass@localhost/dbname")

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Generating Migrations

### Auto-Generate from Model Changes

```bash
# Generate migration automatically based on model diffs
alembic revision --autogenerate -m "add_fees_table"

# With specific revision range
alembic revision --autogenerate -m "add_user_email" --rev-id=abc123
```

### Manual Migration

```bash
# Create empty migration for manual changes
alembic revision -m "add_status_column"
```

### Example: Adding a New Table

```python
# alembic/versions/2024_01_15_1200_add_fees_table.py
"""add_fees_table

Revision ID: abc123
Revises: def456
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlmodel import SQLModel

# revision identifiers
revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'fees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
    )
    op.create_index('ix_fees_student_id', 'fees', ['student_id'])
    op.create_index('ix_fees_status', 'fees', ['status'])


def downgrade() -> None:
    op.drop_index('ix_fees_status', table_name='fees')
    op.drop_index('ix_fees_student_id', table_name='fees')
    op.drop_table('fees')
```

### Example: Adding a Column

```python
# alembic/versions/2024_01_16_0900_add_fees_description.py
"""add_fees_description

Revision ID: ghi789
Revises: abc123
Create Date: 2024-01-16 09:00:00.000000

"""
from alembic import op


def upgrade() -> None:
    op.add_column('fees', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('fees', 'description')
```

## Applying Migrations

### Standard Upgrade

```bash
# Upgrade to latest revision
alembic upgrade head

# Upgrade one step at a time
alembic upgrade +1

# Upgrade to specific revision
alembic upgrade abc123
```

### Dry Run (Check What Would Happen)

```bash
# Show pending migrations without applying
alembic show heads
alembic history --verbose
```

## Rollback (Downgrade)

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Rollback all migrations (empty database)
alembic downgrade base
```

### Safe Downgrade Pattern

```python
def downgrade() -> None:
    # Always drop indexes before table
    op.drop_index('ix_fees_status', table_name='fees')
    op.drop_index('ix_fees_student_id', table_name='fees')
    # Drop foreign keys before table
    op.drop_constraint('fees_student_id_fkey', 'fees', type_='foreignkey')
    op.drop_table('fees')
```

## Data Migrations

### Example: Data Migration with Batch Update

```python
# alembic/versions/2024_01_17_1400_update_fees_status.py
"""update_fees_status_values

Revision ID: jkl012
Revises: ghi789
Create Date: 2024-01-17 14:00:00.000000

"""
from alembic import op
from sqlalchemy import text


def upgrade() -> None:
    # Update existing records
    op.execute(
        text("UPDATE fees SET status = 'pending' WHERE status = 'unpaid'")
    )


def downgrade() -> None:
    # Revert status values
    op.execute(
        text("UPDATE fees SET status = 'unpaid' WHERE status = 'pending'")
    )
```

### Example: Enum Migration

```python
def upgrade() -> None:
    # Add new enum type
    op.execute("CREATE TYPE fee_status_new AS ENUM ('pending', 'paid', 'overdue', 'waived')")
    # Copy data to new type
    op.execute("ALTER TABLE fees ALTER COLUMN status TYPE fee_status_new USING status::text::fee_status_new")
    # Drop old type
    op.execute("DROP TYPE fee_status_old")


def downgrade() -> None:
    # Reverse the process
    op.execute("ALTER TABLE fees ALTER COLUMN status TYPE VARCHAR(20)")
    op.execute("DROP TYPE fee_status_new")
```

## Quality Checklist

- [ ] **Data migrations**: Handle existing data when modifying columns/tables
- [ ] **Test migrations**: Run `alembic upgrade` then `alembic downgrade` in test
- [ ] **Idempotent operations**: up() and down() can run multiple times safely
- [ ] **No data loss**: Use `DROP TABLE IF EXISTS`, `DROP COLUMN IF EXISTS`
- [ ] **Indexes created**: Include index creation in upgrade, drop in downgrade
- [ ] **Foreign keys**: Handle constraint ordering (create before, drop after)
- [ ] **Backwards compatible**: Don't break existing application during migration

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| `@sqlmodel-crud` | Model changes trigger migrations |
| `@fastapi-app` | Migrations run at startup or via CLI |
| `@jwt-auth` | May need to handle auth during migrations |

## Migration Best Practices

### 1. Always Generate Before Manual Edit

```bash
alembic revision --autogenerate -m "describe_change"
# Then review and edit the generated file
```

### 2. Review Generated Migrations

```python
# Check that:
# - Column types match SQLModel definitions
# - Foreign key constraints are correct
# - Indexes are appropriate
# - Default values are set
```

### 3. Test Migration Cycle

```bash
# In test environment
alembic downgrade base
alembic upgrade head

# Verify all data is intact
```

### 4. Handle Long-Running Migrations

```python
# For large tables, use batch updates
def upgrade():
    op.execute("""
        UPDATE fees SET status = 'pending'
        WHERE status IS NULL
        LIMIT 10000
    """)
```

## Directory Structure

```
project/
├── alembic/
│   ├── env.py              # Migration configuration
│   ├── script.py.mako      # Template for new migrations
│   ├── README              # Alembic documentation
│   └── versions/
│       ├── 2024_01_15_1200_add_fees_table.py
│       └── 2024_01_16_0900_add_fees_description.py
├── myapp/
│   └── models.py           # SQLModel definitions
└── alembic.ini             # Alembic configuration
```
