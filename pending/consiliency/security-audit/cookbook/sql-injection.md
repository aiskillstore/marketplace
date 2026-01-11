# SQL Injection Prevention Cookbook

How to prevent SQL injection vulnerabilities in your code.

## Understanding SQL Injection

SQL injection occurs when user input is included directly in SQL queries without proper sanitization or parameterization.

### The Attack

```python
# User input
user_input = "'; DROP TABLE users; --"

# Vulnerable code
query = f"SELECT * FROM users WHERE name = '{user_input}'"
# Results in: SELECT * FROM users WHERE name = ''; DROP TABLE users; --'
```

## Prevention Patterns

### Python + SQLAlchemy

```python
# BAD - String formatting
session.execute(f"SELECT * FROM users WHERE id = {user_id}")
session.execute("SELECT * FROM users WHERE name = '%s'" % name)

# GOOD - Use ORM methods
user = session.query(User).filter(User.id == user_id).first()
users = session.query(User).filter(User.name == name).all()

# GOOD - Parameterized raw SQL when needed
from sqlalchemy import text
result = session.execute(
    text("SELECT * FROM users WHERE id = :user_id"),
    {"user_id": user_id}
)
```

### Python + psycopg2

```python
import psycopg2

# BAD - String formatting
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
cursor.execute("SELECT * FROM users WHERE name = '" + name + "'")

# GOOD - Parameterized query (tuple)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# GOOD - Named parameters (dict)
cursor.execute(
    "SELECT * FROM users WHERE name = %(name)s AND age > %(age)s",
    {"name": name, "age": min_age}
)
```

### Python + SQLite

```python
import sqlite3

# BAD
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# GOOD - Parameterized query
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# GOOD - Named parameters
cursor.execute(
    "SELECT * FROM users WHERE name = :name",
    {"name": name}
)
```

### TypeScript + Prisma

```typescript
// BAD - Raw query with interpolation
await prisma.$queryRaw`SELECT * FROM users WHERE id = ${userId}`;  // Actually safe!
await prisma.$queryRawUnsafe(`SELECT * FROM users WHERE id = ${userId}`);  // UNSAFE!

// GOOD - Prisma methods
const user = await prisma.user.findUnique({ where: { id: userId } });
const users = await prisma.user.findMany({
  where: { name: { equals: name } }
});

// GOOD - Tagged template (safe in Prisma)
await prisma.$queryRaw`SELECT * FROM users WHERE id = ${userId}`;
```

### TypeScript + Node-Postgres

```typescript
import { Pool } from 'pg';

// BAD
await pool.query(`SELECT * FROM users WHERE id = ${userId}`);

// GOOD - Parameterized query
await pool.query('SELECT * FROM users WHERE id = $1', [userId]);

// GOOD - Named parameters (with helper)
await pool.query({
  text: 'SELECT * FROM users WHERE id = $1 AND name = $2',
  values: [userId, name]
});
```

## Detection Patterns

### Regex Patterns (for scanning)

```python
VULNERABLE_PATTERNS = [
    # f-strings in execute
    r'execute\(f["\']',
    r'execute\(f`',

    # String concatenation in execute
    r'execute\(["\'].*\+',
    r'execute\(.*\+\s*["\']',

    # % formatting in execute
    r'execute\(["\'].*%[sd]',
    r'execute\(["\'].*%\s*\(',

    # .format() in execute
    r'execute\(["\'].*\.format\(',

    # Unsafe raw queries
    r'\$queryRawUnsafe',
    r'raw_sql\s*=\s*f["\']',
]
```

### Static Analysis Tools

```bash
# Python - bandit
pip install bandit
bandit -r src/ -f json

# JavaScript/TypeScript - eslint-plugin-security
npm install eslint-plugin-security
# Add to .eslintrc: plugins: ['security']

# SQL - sqlfluff
pip install sqlfluff
sqlfluff lint my_queries.sql
```

## Remediation Examples

### Before/After: Simple Query

```python
# BEFORE (vulnerable)
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return cursor.execute(query).fetchone()

# AFTER (safe)
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    return cursor.execute(query, (user_id,)).fetchone()
```

### Before/After: Search Query

```python
# BEFORE (vulnerable)
def search_users(name, email):
    query = f"""
        SELECT * FROM users
        WHERE name LIKE '%{name}%'
        AND email LIKE '%{email}%'
    """
    return cursor.execute(query).fetchall()

# AFTER (safe)
def search_users(name, email):
    query = """
        SELECT * FROM users
        WHERE name LIKE %s
        AND email LIKE %s
    """
    return cursor.execute(query, (f"%{name}%", f"%{email}%")).fetchall()
```

### Before/After: Dynamic Columns

```python
# BEFORE (vulnerable - column names can be injected)
def get_user_field(user_id, field):
    query = f"SELECT {field} FROM users WHERE id = %s"
    return cursor.execute(query, (user_id,)).fetchone()

# AFTER (safe - whitelist column names)
ALLOWED_FIELDS = {'name', 'email', 'created_at'}

def get_user_field(user_id, field):
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Invalid field: {field}")
    query = f"SELECT {field} FROM users WHERE id = %s"
    return cursor.execute(query, (user_id,)).fetchone()
```

### Before/After: IN Clause

```python
# BEFORE (vulnerable)
def get_users_by_ids(ids):
    ids_str = ",".join(str(id) for id in ids)
    query = f"SELECT * FROM users WHERE id IN ({ids_str})"
    return cursor.execute(query).fetchall()

# AFTER (safe)
def get_users_by_ids(ids):
    placeholders = ",".join(["%s"] * len(ids))
    query = f"SELECT * FROM users WHERE id IN ({placeholders})"
    return cursor.execute(query, tuple(ids)).fetchall()
```

## Edge Cases

### ORDER BY / LIMIT

```python
# These can't be parameterized directly
# Use whitelist validation

ALLOWED_ORDER = {'name', 'created_at', 'id'}
ALLOWED_DIRECTION = {'ASC', 'DESC'}

def get_users_sorted(order_by, direction, limit):
    if order_by not in ALLOWED_ORDER:
        order_by = 'id'
    if direction.upper() not in ALLOWED_DIRECTION:
        direction = 'ASC'
    if not isinstance(limit, int) or limit < 1:
        limit = 10

    query = f"SELECT * FROM users ORDER BY {order_by} {direction} LIMIT %s"
    return cursor.execute(query, (limit,)).fetchall()
```

### Table Names

```python
# Table names can't be parameterized
# Use whitelist validation

ALLOWED_TABLES = {'users', 'posts', 'comments'}

def get_from_table(table_name, id):
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table: {table_name}")
    query = f"SELECT * FROM {table_name} WHERE id = %s"
    return cursor.execute(query, (id,)).fetchall()
```

## Testing for SQL Injection

### Manual Tests

```python
# Test payloads
PAYLOADS = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "1; UPDATE users SET role='admin' WHERE id=1; --",
    "' UNION SELECT * FROM passwords --",
]

for payload in PAYLOADS:
    try:
        result = vulnerable_function(payload)
        print(f"Possible vulnerability: {payload}")
    except Exception as e:
        print(f"Blocked or error: {e}")
```

### Automated Testing

```bash
# sqlmap for comprehensive testing
sqlmap -u "http://localhost/api/users?id=1" --batch --dbs

# Custom pytest
pytest tests/security/test_sql_injection.py -v
```
