# BAML Schema Synchronization Cookbook

How to keep BAML schemas in sync with the rest of your codebase.

## When to Sync

Sync BAML schema when:
1. Database schema changes (new columns, type changes)
2. API contracts change (request/response shapes)
3. Frontend types need updating
4. New LLM functions are added

## Synchronization Workflow

### 1. Identify Sources of Truth

| Domain | Source of Truth | Syncs To |
|--------|-----------------|----------|
| Database | Migrations/ORM models | BAML types |
| API | OpenAPI/BAML | Frontend types |
| LLM | BAML functions | Python/TS clients |

### 2. Database → BAML

When database schema changes:

```python
# 1. SQLAlchemy model updated
class Book(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    isbn: Mapped[str] = mapped_column(String(13))
    published_date: Mapped[date] = mapped_column(Date)
    genre: Mapped[str | None] = mapped_column(String(50))
```

```baml
// 2. Update BAML type to match
class Book {
  id int
  title string
  author string
  isbn string @description("13-character ISBN")
  published_date string @description("ISO date format: YYYY-MM-DD")
  genre string?
}
```

### 3. BAML → Generated Clients

After BAML changes:

```bash
# Generate updated clients
baml-cli generate

# Verify generation
ls -la baml_client/
# Should show updated timestamps
```

### 4. Verify Type Alignment

Create a verification script:

```python
# scripts/verify_baml_sync.py
from baml_client.types import Book as BAMLBook
from app.models import Book as DBBook

def verify_book_alignment():
    """Verify BAML Book matches DB Book."""
    db_fields = {c.name for c in DBBook.__table__.columns}
    baml_fields = set(BAMLBook.__annotations__.keys())

    missing_in_baml = db_fields - baml_fields
    extra_in_baml = baml_fields - db_fields

    if missing_in_baml:
        print(f"Missing in BAML: {missing_in_baml}")
    if extra_in_baml:
        print(f"Extra in BAML: {extra_in_baml}")

    return not (missing_in_baml or extra_in_baml)
```

## Common Sync Patterns

### Pattern 1: Add New Field

```baml
// Before
class User {
  id int
  email string
  name string
}

// After - add preferences
class User {
  id int
  email string
  name string
  preferences UserPreferences?  // New optional field
}

class UserPreferences {
  theme string @description("light or dark")
  notifications bool
}
```

Then regenerate: `baml-cli generate`

### Pattern 2: Change Field Type

```baml
// Before
class Order {
  id int
  total float  // Was float
}

// After - change to Decimal for precision
class Order {
  id int
  total string @description("Decimal as string: '123.45'")
}
```

Update consumers to handle the new type.

### Pattern 3: Add Enum

```baml
// Define enum
enum OrderStatus {
  PENDING
  PROCESSING
  SHIPPED
  DELIVERED
  CANCELLED
}

// Use in class
class Order {
  id int
  status OrderStatus
}
```

Ensure database enum matches:

```python
# SQLAlchemy
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
```

### Pattern 4: Rename Field

```baml
// Before
class User {
  user_id int
}

// After - use alias for backward compatibility
class User {
  id int @alias("user_id")  // JSON still uses user_id
}
```

## Pre-Commit Hook

Add a pre-commit check for BAML sync:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: baml-check
        name: Check BAML syntax
        entry: baml-cli check
        language: system
        pass_filenames: false
        files: \.baml$

      - id: baml-generate
        name: Regenerate BAML clients
        entry: baml-cli generate
        language: system
        pass_filenames: false
        files: \.baml$
```

## CI Integration

```yaml
# .github/workflows/baml-check.yml
name: BAML Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install BAML CLI
        run: pip install baml-cli

      - name: Check BAML syntax
        run: baml-cli check

      - name: Generate clients
        run: baml-cli generate

      - name: Check for uncommitted changes
        run: |
          if [[ -n $(git status --porcelain baml_client/) ]]; then
            echo "BAML clients out of sync! Run: baml-cli generate"
            exit 1
          fi
```

## Troubleshooting Sync Issues

### Issue: Type Mismatch After Sync

```
Error: Type 'int' is not assignable to type 'string'
```

**Fix**: Check BAML type vs code type, ensure consistency.

### Issue: Missing Field in Generated Client

```
AttributeError: 'User' object has no attribute 'preferences'
```

**Fix**: Run `baml-cli generate` and restart application.

### Issue: Enum Value Not Found

```
ValueError: 'PENDING' is not a valid OrderStatus
```

**Fix**: Ensure enum values match exactly (case-sensitive).
