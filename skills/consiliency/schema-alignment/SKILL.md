---
name: schema-alignment
description: "Detect and report drift between database schema and code data models. Works with SQLAlchemy, Django ORM, Prisma, TypeORM, and other ORMs. Generic across any project."
---

# Schema Alignment Skill

Detect drift between database schemas and code data models. This skill identifies missing columns, type mismatches, orphaned migrations, and naming inconsistencies.

## Design Principle

This skill is **framework-generic**. It works with any ORM or database:
- SQLAlchemy (Python)
- Django ORM (Python)
- Prisma (TypeScript/JavaScript)
- TypeORM (TypeScript)
- Drizzle (TypeScript)
- Alembic migrations
- Prisma migrations
- Django migrations

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SCHEMA_SOURCE | auto | Schema source: auto, migrations, live_db, models |
| SEVERITY_THRESHOLD | medium | Report issues at this level or higher |
| AUTO_FIX | false | Attempt to generate fix suggestions |
| INCLUDE_TYPES | true | Include type mismatch detection |

## Instructions

**MANDATORY** - Follow the Workflow steps below in order.

1. Detect database technology and ORM in use
2. Extract schema from migrations or live database
3. Extract data models from code
4. Compare and identify drift
5. Generate alignment report

## Red Flags - STOP and Reconsider

If you're about to:
- Modify the database schema directly without a migration
- Assume a column exists without checking the schema
- Skip type checking because "it works in tests"
- Ignore nullable/not-null mismatches

**STOP** -> Check schema alignment -> Generate migration if needed -> Then proceed

## Workflow

### 1. Detect Stack

Identify the database and ORM:

```markdown
Check for these indicators:

| File/Dependency | Technology |
|-----------------|------------|
| alembic.ini, alembic/ | Alembic (SQLAlchemy) |
| prisma/schema.prisma | Prisma |
| manage.py + migrations/ | Django |
| ormconfig.json | TypeORM |
| drizzle.config.ts | Drizzle |
| supabase/migrations/ | Supabase (PostgreSQL) |
```

### 2. Extract Database Schema

#### Option A: From Migrations (Preferred)

Parse migration files to reconstruct current schema:

```python
# Alembic example
from alembic.script import ScriptDirectory
from alembic.config import Config

config = Config("alembic.ini")
scripts = ScriptDirectory.from_config(config)
# Walk revisions to build schema
```

#### Option B: From Live Database

Query information_schema (if accessible):

```sql
SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public';
```

#### Option C: From Model Definitions

Parse ORM model files directly.

### 3. Extract Code Models

Parse model definitions from code:

#### SQLAlchemy

```python
# Look for patterns like:
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
```

#### Prisma

```prisma
model User {
  id    Int     @id @default(autoincrement())
  email String  @unique
  name  String?
}
```

#### Pydantic/TypeScript Types

Also extract related types:
- Pydantic models
- TypeScript interfaces
- BAML type definitions

### 4. Compare and Detect Drift

Run comparisons:

| Check | Source A | Source B | Issue Type |
|-------|----------|----------|------------|
| Missing column | DB schema | ORM model | MISSING_IN_MODEL |
| Missing column | ORM model | DB schema | MISSING_IN_DB |
| Type mismatch | DB type | Code type | TYPE_MISMATCH |
| Nullable mismatch | DB nullable | Model nullable | NULLABLE_MISMATCH |
| Name mismatch | snake_case | camelCase | NAMING_DRIFT |
| Missing migration | Model change | Migration files | MISSING_MIGRATION |
| FK constraint | DB constraint | ORM relationship | FK_MISMATCH |

### 5. Generate Report

Output format:

```markdown
# Schema Alignment Report

**Generated**: 2025-12-24T10:00:00Z
**Database**: PostgreSQL (via Supabase)
**ORM**: SQLAlchemy 2.0

## Summary

| Severity | Count |
|----------|-------|
| HIGH | 2 |
| MEDIUM | 3 |
| LOW | 5 |

## Issues

### 1. MISSING_IN_MODEL (HIGH)

**Table**: `curation_jobs`
**Column**: `retry_count` (INTEGER NOT NULL DEFAULT 0)
**Model**: `src/models/curation_job.py:CurationJob`

The column exists in the database but is not defined in the ORM model.

**Fix**:
```python
retry_count: Mapped[int] = mapped_column(Integer, default=0)
```

### 2. TYPE_MISMATCH (MEDIUM)

**Table**: `books`
**Column**: `isbn` (VARCHAR(13))
**Model**: `src/models/book.py:Book.isbn` -> `str`

Database constrains to 13 characters but model allows unbounded string.

**Fix**:
```python
isbn: Mapped[str] = mapped_column(String(13))
```

### 3. MISSING_MIGRATION (LOW)

**Model Change**: `User.preferences` added (JSONB)
**Migration**: Not found

A new column was added to the model but no migration exists.

**Fix**:
```bash
alembic revision --autogenerate -m "add user preferences"
```
```

## Cookbook

### SQLAlchemy Detection
- IF: Parsing SQLAlchemy models
- THEN: Read and execute `./cookbook/sqlalchemy-detection.md`

### Prisma Detection
- IF: Parsing Prisma schema
- THEN: Read and execute `./cookbook/prisma-detection.md`

### Alembic Migrations
- IF: Generating migration fix
- THEN: Read and execute `./cookbook/alembic-migration.md`

## Issue Severity Matrix

| Issue Type | Default Severity | Upgrade If |
|------------|-----------------|------------|
| MISSING_IN_MODEL | HIGH | Column is NOT NULL |
| MISSING_IN_DB | MEDIUM | Model references it |
| TYPE_MISMATCH | MEDIUM | Could cause data loss |
| NULLABLE_MISMATCH | LOW | NOT NULL in code, nullable in DB |
| NAMING_DRIFT | LOW | - |
| MISSING_MIGRATION | LOW | - |
| FK_MISMATCH | MEDIUM | Causes ORM errors |

## Integration

### With /ai-dev-kit:check-schema

Direct invocation:

```bash
# Full check
/ai-dev-kit:check-schema

# Check specific tables
/ai-dev-kit:check-schema --tables=users,orders

# Generate fixes
/ai-dev-kit:check-schema --auto-fix

# Output to file
/ai-dev-kit:check-schema --output=alignment-report.md
```

### With /ai-dev-kit:execute-lane

Runs as pre-flight check for database-related lanes:

```markdown
Lane: SL-DB (Database Schema)

Pre-flight checks:
1. ✓ Git worktree clean
2. ✗ Schema alignment check failed
   - 2 HIGH severity issues found
   - See alignment-report.md

Action: Resolve schema issues before proceeding.
```

### With /ai-dev-kit:plan-phase

Runs during phase planning:

```markdown
Planning Phase P1...

Schema Alignment: ⚠️ 3 issues detected
- 1 missing migration
- 2 type mismatches

Recommendation: Add schema alignment task to SL-DB lane.
```

## Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "generated_at": {"type": "string", "format": "date-time"},
    "database": {"type": "string"},
    "orm": {"type": "string"},
    "summary": {
      "type": "object",
      "properties": {
        "high": {"type": "integer"},
        "medium": {"type": "integer"},
        "low": {"type": "integer"}
      }
    },
    "issues": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {"type": "string"},
          "severity": {"enum": ["HIGH", "MEDIUM", "LOW"]},
          "table": {"type": "string"},
          "column": {"type": "string"},
          "model_location": {"type": "string"},
          "description": {"type": "string"},
          "fix": {"type": "string"}
        }
      }
    }
  }
}
```

## Best Practices

1. **Run regularly**: Check schema alignment before each PR
2. **CI integration**: Add to CI pipeline for automatic detection
3. **Migration hygiene**: Always generate migrations for model changes
4. **Type consistency**: Use explicit types in models matching DB constraints
5. **Document drift**: If drift is intentional, document why
