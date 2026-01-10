---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: database-optimization
---

# Database Query Optimization Patterns

## EXPLAIN ANALYZE Usage

### PostgreSQL

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM users WHERE email = 'test@example.com';
```

### MySQL

```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'test@example.com';
```

## Common Query Anti-Patterns

### 1. SELECT * Instead of Specific Columns

```sql
-- Bad: Fetches all columns
SELECT * FROM users WHERE id = 1;

-- Good: Fetch only needed columns
SELECT id, email, name FROM users WHERE id = 1;
```

### 2. Missing WHERE Clause Index

```sql
-- Bad: Full table scan
SELECT * FROM orders WHERE status = 'pending';

-- Good: Add index on status
CREATE INDEX idx_orders_status ON orders(status);
```

### 3. Leading Wildcard in LIKE

```sql
-- Bad: Cannot use index
SELECT * FROM users WHERE email LIKE '%@gmail.com';

-- Good: Use suffix column or full-text search
SELECT * FROM users WHERE email_domain = 'gmail.com';
```

### 4. Functions on Indexed Columns

```sql
-- Bad: Index not used
SELECT * FROM orders WHERE YEAR(created_at) = 2024;

-- Good: Use range comparison
SELECT * FROM orders
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';
```

### 5. OR Conditions

```sql
-- Bad: May not use index efficiently
SELECT * FROM users WHERE status = 'active' OR role = 'admin';

-- Good: Use UNION for separate index scans
SELECT * FROM users WHERE status = 'active'
UNION
SELECT * FROM users WHERE role = 'admin';
```

## Index Design Patterns

### Composite Index Order

```sql
-- Index columns in order of: equality, range, sort
-- Query: WHERE status = 'active' AND created_at > '2024-01-01' ORDER BY name
CREATE INDEX idx_composite ON users(status, created_at, name);
```

### Covering Index

```sql
-- Include all columns needed by query to avoid table lookup
CREATE INDEX idx_covering ON orders(customer_id, status)
INCLUDE (total, created_at);
```

### Partial Index

```sql
-- Index only frequently queried subset
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';
```

## N+1 Query Solutions

### ORM Eager Loading

**SQLAlchemy:**

```python
# Bad: N+1
users = session.query(User).all()
for user in users:
    print(user.posts)  # Triggers query per user

# Good: Eager load
users = session.query(User).options(joinedload(User.posts)).all()
```

**Django:**

```python
# Bad: N+1
users = User.objects.all()
for user in users:
    print(user.posts.all())

# Good: Prefetch
users = User.objects.prefetch_related('posts').all()
```

**ActiveRecord:**

```ruby
# Bad: N+1
User.all.each { |u| puts u.posts }

# Good: Includes
User.includes(:posts).each { |u| puts u.posts }
```

## Caching Strategies

### Query Result Caching

```python
# Redis caching pattern
import redis
import json

def get_user(user_id):
    cache_key = f"user:{user_id}"
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    redis.setex(cache_key, 3600, json.dumps(user))  # 1 hour TTL
    return user
```

### Cache Invalidation Patterns

- **Time-based**: Set TTL on cached entries
- **Event-based**: Invalidate on write operations
- **Version-based**: Include version in cache key
