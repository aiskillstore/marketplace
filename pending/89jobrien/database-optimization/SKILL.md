---
name: database-optimization
description: SQL query optimization and database performance specialist. Use when
  optimizing slow queries, fixing N+1 problems, designing indexes, implementing caching,
  or improving database performance. Works with PostgreSQL, MySQL, and other databases.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Database Optimization

This skill optimizes database performance including query optimization, indexing strategies, N+1 problem resolution, and caching implementation.

## When to Use This Skill

- When optimizing slow database queries
- When fixing N+1 query problems
- When designing indexes
- When implementing caching strategies
- When optimizing database migrations
- When improving database performance

## What This Skill Does

1. **Query Optimization**: Analyzes and optimizes SQL queries
2. **Index Design**: Creates appropriate indexes
3. **N+1 Resolution**: Fixes N+1 query problems
4. **Caching**: Implements caching layers (Redis, Memcached)
5. **Migration Optimization**: Optimizes database migrations
6. **Performance Monitoring**: Sets up query performance monitoring

## How to Use

### Optimize Queries

```
Optimize this slow database query
```

```
Fix the N+1 query problem in this code
```

### Specific Analysis

```
Analyze query performance and suggest indexes
```

## Optimization Areas

### Query Optimization

**Techniques:**

- Use EXPLAIN ANALYZE
- Optimize JOINs
- Reduce data scanned
- Use appropriate indexes
- Avoid SELECT *

### Index Design

**Strategies:**

- Index frequently queried columns
- Composite indexes for multi-column queries
- Avoid over-indexing
- Monitor index usage
- Remove unused indexes

### N+1 Problem

**Pattern:**

```python
# Bad: N+1 queries
users = User.all()
for user in users:
    posts = Post.where(user_id=user.id)  # N queries

# Good: Single query with JOIN
users = User.all().includes(:posts)  # 1 query
```

## Examples

### Example 1: Query Optimization

**Input**: Optimize slow user query

**Output**:

```markdown
## Database Optimization: User Query

### Current Query
```sql
SELECT * FROM users
WHERE email = 'user@example.com';
-- Execution time: 450ms
```

### Analysis

- Full table scan (no index on email)
- Scanning 1M+ rows

### Optimization

```sql
-- Add index
CREATE INDEX idx_users_email ON users(email);

-- Optimized query
SELECT id, email, name FROM users
WHERE email = 'user@example.com';
-- Execution time: 2ms
```

### Impact

- Query time: 450ms → 2ms (99.5% improvement)
- Index size: ~50MB

```

## Best Practices

### Database Optimization

1. **Measure First**: Use EXPLAIN ANALYZE
2. **Index Strategically**: Not every column needs an index
3. **Monitor**: Track slow query logs
4. **Cache**: Cache expensive queries
5. **Denormalize**: When justified by read patterns

## Reference Files

- **`references/query_patterns.md`** - Common query optimization patterns, anti-patterns, and caching strategies

## Related Use Cases

- Query optimization
- Index design
- N+1 problem resolution
- Caching implementation
- Database performance improvement
