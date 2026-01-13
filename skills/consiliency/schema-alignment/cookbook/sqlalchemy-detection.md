# SQLAlchemy Detection Cookbook

How to detect and extract SQLAlchemy model definitions for schema alignment.

## Detection Patterns

### SQLAlchemy 2.0 (Mapped Columns)

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str | None] = mapped_column(String(100))
```

Extract:
- Table name: `users`
- Columns: `id` (int, PK), `email` (varchar(255), unique), `name` (varchar(100), nullable)

### SQLAlchemy 1.x (Classic Style)

```python
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=True)
```

Extract the same schema information.

## Type Mapping

| SQLAlchemy Type | PostgreSQL Type | Python Type |
|-----------------|-----------------|-------------|
| `Integer` | `INTEGER` | `int` |
| `BigInteger` | `BIGINT` | `int` |
| `String(n)` | `VARCHAR(n)` | `str` |
| `Text` | `TEXT` | `str` |
| `Boolean` | `BOOLEAN` | `bool` |
| `DateTime` | `TIMESTAMP` | `datetime` |
| `Date` | `DATE` | `date` |
| `Float` | `FLOAT` | `float` |
| `Numeric(p,s)` | `NUMERIC(p,s)` | `Decimal` |
| `JSON` | `JSON` | `dict` |
| `JSONB` | `JSONB` | `dict` |
| `UUID` | `UUID` | `uuid.UUID` |
| `LargeBinary` | `BYTEA` | `bytes` |

## Relationship Detection

### One-to-Many

```python
class User(Base):
    orders = relationship("Order", back_populates="user")

class Order(Base):
    user_id = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="orders")
```

### Many-to-Many

```python
association_table = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("role_id", ForeignKey("roles.id")),
)

class User(Base):
    roles = relationship("Role", secondary=association_table)
```

## Common Issues

### Issue: Nullable Mismatch

```python
# Model says nullable
name: Mapped[str | None] = mapped_column(String(100))

# But database has NOT NULL constraint
# Fix: Add nullable=False or update DB
name: Mapped[str] = mapped_column(String(100), nullable=False)
```

### Issue: String Length Mismatch

```python
# Model has no length constraint
email: Mapped[str] = mapped_column(String)  # Unlimited

# Database has VARCHAR(255)
# Fix: Add length constraint
email: Mapped[str] = mapped_column(String(255))
```

### Issue: Missing Default

```python
# Database has DEFAULT
# created_at TIMESTAMP DEFAULT now()

# Model missing default
created_at: Mapped[datetime] = mapped_column()

# Fix: Add server_default
created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

## File Patterns to Search

```bash
# Find SQLAlchemy models
find . -name "*.py" -exec grep -l "from sqlalchemy" {} \;
find . -name "*.py" -exec grep -l "class.*Base\):" {} \;
find . -name "models*.py"
find . -path "*/models/*.py"
```

## Parsing Strategy

1. Find all Python files with SQLAlchemy imports
2. Parse class definitions inheriting from Base
3. Extract `__tablename__` attribute
4. Parse column definitions
5. Extract relationships
6. Build schema representation
