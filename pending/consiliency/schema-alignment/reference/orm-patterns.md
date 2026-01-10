# ORM Patterns Reference

Common patterns for detecting and aligning database schemas across different ORMs.

## ORM Detection Matrix

| Indicator | ORM | Language |
|-----------|-----|----------|
| `alembic.ini` | SQLAlchemy | Python |
| `from sqlalchemy` | SQLAlchemy | Python |
| `prisma/schema.prisma` | Prisma | TypeScript/JS |
| `@prisma/client` | Prisma | TypeScript/JS |
| `manage.py` + `migrations/` | Django | Python |
| `ormconfig.json` | TypeORM | TypeScript |
| `drizzle.config.ts` | Drizzle | TypeScript |
| `sequelize.config.js` | Sequelize | JavaScript |
| `knexfile.js` | Knex.js | JavaScript |

## Type Equivalence Tables

### Python to Database

| Python Type | PostgreSQL | MySQL | SQLite |
|-------------|------------|-------|--------|
| `int` | `INTEGER` | `INT` | `INTEGER` |
| `str` | `TEXT`/`VARCHAR` | `VARCHAR`/`TEXT` | `TEXT` |
| `bool` | `BOOLEAN` | `TINYINT(1)` | `INTEGER` |
| `float` | `DOUBLE PRECISION` | `DOUBLE` | `REAL` |
| `Decimal` | `NUMERIC` | `DECIMAL` | `NUMERIC` |
| `datetime` | `TIMESTAMP` | `DATETIME` | `TEXT` |
| `date` | `DATE` | `DATE` | `TEXT` |
| `time` | `TIME` | `TIME` | `TEXT` |
| `bytes` | `BYTEA` | `BLOB` | `BLOB` |
| `dict` | `JSONB`/`JSON` | `JSON` | `TEXT` |
| `list` | `JSONB`/`JSON` | `JSON` | `TEXT` |
| `UUID` | `UUID` | `CHAR(36)` | `TEXT` |

### TypeScript to Database

| TypeScript Type | PostgreSQL | MySQL | SQLite |
|-----------------|------------|-------|--------|
| `number` | `INTEGER`/`FLOAT` | `INT`/`DOUBLE` | `INTEGER`/`REAL` |
| `string` | `TEXT`/`VARCHAR` | `VARCHAR`/`TEXT` | `TEXT` |
| `boolean` | `BOOLEAN` | `TINYINT(1)` | `INTEGER` |
| `Date` | `TIMESTAMP` | `DATETIME` | `TEXT` |
| `bigint` | `BIGINT` | `BIGINT` | `INTEGER` |
| `Buffer` | `BYTEA` | `BLOB` | `BLOB` |
| `object` | `JSONB`/`JSON` | `JSON` | `TEXT` |

## Common Alignment Patterns

### Pattern 1: ID Columns

**Best Practice**: Always use explicit ID type and generation.

```python
# SQLAlchemy - Recommended
id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

# Or for UUID
id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4
)
```

```prisma
// Prisma - Recommended
id Int @id @default(autoincrement())

// Or for UUID
id String @id @default(uuid())
```

### Pattern 2: Timestamps

**Best Practice**: Use database-generated timestamps.

```python
# SQLAlchemy
from sqlalchemy import func

created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now()
)
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now()
)
```

```prisma
// Prisma
createdAt DateTime @default(now())
updatedAt DateTime @updatedAt
```

### Pattern 3: Soft Deletes

**Best Practice**: Use nullable timestamp for soft deletes.

```python
# SQLAlchemy
deleted_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    default=None
)
```

```prisma
// Prisma
deletedAt DateTime?
```

### Pattern 4: Enums

**Best Practice**: Define enums in both database and code.

```python
# SQLAlchemy with Enum
from enum import Enum as PyEnum
from sqlalchemy import Enum

class Status(PyEnum):
    PENDING = "pending"
    ACTIVE = "active"
    CANCELLED = "cancelled"

status: Mapped[Status] = mapped_column(
    Enum(Status),
    default=Status.PENDING
)
```

```prisma
// Prisma
enum Status {
  PENDING
  ACTIVE
  CANCELLED
}

model Order {
  status Status @default(PENDING)
}
```

### Pattern 5: JSON Fields

**Best Practice**: Use JSONB for PostgreSQL, define structure in code.

```python
# SQLAlchemy - with Pydantic validation
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import BaseModel

class Preferences(BaseModel):
    theme: str = "light"
    notifications: bool = True

preferences: Mapped[dict] = mapped_column(
    JSONB,
    default={"theme": "light", "notifications": True}
)
```

```typescript
// Prisma + TypeScript
// schema.prisma
preferences Json @default("{}")

// TypeScript type
interface Preferences {
  theme: 'light' | 'dark';
  notifications: boolean;
}
```

## Relationship Patterns

### One-to-One

```python
# SQLAlchemy
class User(Base):
    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)

class Profile(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship(back_populates="profile")
```

### One-to-Many

```python
# SQLAlchemy
class User(Base):
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

class Order(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="orders")
```

### Many-to-Many

```python
# SQLAlchemy - with association table
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

class User(Base):
    roles: Mapped[list["Role"]] = relationship(secondary=user_roles)
```

## Migration Pattern Reference

| Change Type | SQLAlchemy/Alembic | Prisma |
|-------------|-------------------|--------|
| Add column | `op.add_column()` | Add field, run migrate |
| Drop column | `op.drop_column()` | Remove field, run migrate |
| Rename column | `op.alter_column(new_column_name=)` | Use `@map()` or migrate |
| Change type | `op.alter_column(type_=)` | Change type, run migrate |
| Add index | `op.create_index()` | Add `@@index()`, run migrate |
| Add FK | `op.create_foreign_key()` | Add relation, run migrate |

## Validation Checklist

Before approving schema alignment:

- [ ] All columns in database exist in model
- [ ] All model fields exist in database
- [ ] Types match (considering ORM type mapping)
- [ ] Nullable constraints match
- [ ] Default values are consistent
- [ ] Foreign keys have corresponding relationships
- [ ] Indexes exist for frequently queried columns
- [ ] Enum values are synchronized
