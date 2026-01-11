# Alembic Migration Cookbook

How to generate and manage Alembic migrations for schema alignment fixes.

## Project Structure

```
project/
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial.py
│       └── 002_add_users.py
```

## Generating Migrations

### Auto-generate from Model Changes

```bash
# Generate migration by comparing models to database
alembic revision --autogenerate -m "description"
```

### Manual Migration

```bash
# Create empty migration file
alembic revision -m "description"
```

## Migration File Structure

```python
"""description

Revision ID: abc123
Revises: def456
Create Date: 2025-12-24 10:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None

def upgrade():
    # Forward migration
    pass

def downgrade():
    # Reverse migration
    pass
```

## Common Operations

### Add Column

```python
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

def downgrade():
    op.drop_column('users', 'phone')
```

### Add Column with Default

```python
def upgrade():
    op.add_column('orders',
        sa.Column('retry_count', sa.Integer(),
                  nullable=False, server_default='0'))

def downgrade():
    op.drop_column('orders', 'retry_count')
```

### Modify Column Type

```python
def upgrade():
    op.alter_column('users', 'email',
        existing_type=sa.String(100),
        type_=sa.String(255))

def downgrade():
    op.alter_column('users', 'email',
        existing_type=sa.String(255),
        type_=sa.String(100))
```

### Change Nullable

```python
def upgrade():
    op.alter_column('users', 'name',
        existing_type=sa.String(100),
        nullable=False)

def downgrade():
    op.alter_column('users', 'name',
        existing_type=sa.String(100),
        nullable=True)
```

### Add Foreign Key

```python
def upgrade():
    op.add_column('orders',
        sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(
        'fk_orders_user', 'orders', 'users',
        ['user_id'], ['id'])

def downgrade():
    op.drop_constraint('fk_orders_user', 'orders', type_='foreignkey')
    op.drop_column('orders', 'user_id')
```

### Add Index

```python
def upgrade():
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

def downgrade():
    op.drop_index('ix_users_email', 'users')
```

### Create Table

```python
def upgrade():
    op.create_table('roles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(),
                  server_default=sa.func.now())
    )

def downgrade():
    op.drop_table('roles')
```

## Data Migrations

For migrations that need to transform data:

```python
from sqlalchemy.sql import table, column

def upgrade():
    # 1. Add new column
    op.add_column('users',
        sa.Column('full_name', sa.String(200), nullable=True))

    # 2. Migrate data
    users = table('users',
        column('id', sa.Integer),
        column('first_name', sa.String),
        column('last_name', sa.String),
        column('full_name', sa.String)
    )

    connection = op.get_bind()
    connection.execute(
        users.update().values(
            full_name=users.c.first_name + ' ' + users.c.last_name
        )
    )

    # 3. Make non-nullable after population
    op.alter_column('users', 'full_name', nullable=False)

    # 4. Drop old columns
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
```

## Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade abc123

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade def456

# Show current revision
alembic current

# Show migration history
alembic history
```

## Best Practices

1. **Always test migrations**: Run upgrade and downgrade in test environment
2. **Use transactions**: Alembic wraps migrations in transactions by default
3. **Handle data carefully**: Data migrations are harder to reverse
4. **Name migrations clearly**: Use descriptive names like `add_user_email_verification`
5. **Review auto-generated**: Auto-generate may miss some changes or generate suboptimal SQL
6. **Version control**: Commit migrations with the code that requires them

## Fixing Schema Alignment Issues

### Issue: Missing Column in Model

```python
# 1. Database has column that model doesn't
# Option A: Add to model (preferred)
# Option B: Remove from database

# If removing from database:
def upgrade():
    op.drop_column('users', 'legacy_field')

def downgrade():
    op.add_column('users',
        sa.Column('legacy_field', sa.String(100)))
```

### Issue: Missing Column in Database

```python
# Model has column that database doesn't
def upgrade():
    op.add_column('users',
        sa.Column('new_field', sa.String(100), nullable=True))

def downgrade():
    op.drop_column('users', 'new_field')
```

### Issue: Type Mismatch

```python
# Model says String(255) but database has TEXT
def upgrade():
    op.alter_column('users', 'bio',
        existing_type=sa.Text(),
        type_=sa.String(255))

def downgrade():
    op.alter_column('users', 'bio',
        existing_type=sa.String(255),
        type_=sa.Text())
```
