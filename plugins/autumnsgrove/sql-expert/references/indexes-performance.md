# Indexes and Performance

## Creating Indexes

```sql
-- Single column index
CREATE INDEX idx_users_email ON users(email);

-- Composite index (order matters!)
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);

-- Unique index
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Partial index (PostgreSQL)
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Functional index
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- Full-text search index (PostgreSQL)
CREATE INDEX idx_posts_search ON posts USING GIN(to_tsvector('english', title || ' ' || content));
```

## Index Guidelines

### When to Create Indexes

- ✅ Columns used in WHERE clauses
- ✅ Columns used in JOIN conditions
- ✅ Columns used in ORDER BY
- ✅ Foreign key columns
- ✅ Columns with high selectivity (many unique values)

### When NOT to Create Indexes

- ❌ Small tables (< 1000 rows)
- ❌ Columns with low selectivity (few unique values like boolean)
- ❌ Columns frequently updated
- ❌ Too many indexes on one table (slows INSERTs/UPDATEs)

## Index Maintenance

```sql
-- PostgreSQL: Rebuild index
REINDEX INDEX idx_users_email;

-- MySQL: Optimize table
OPTIMIZE TABLE users;

-- Check index usage (PostgreSQL)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM
    pg_stat_user_indexes
ORDER BY
    idx_scan ASC;
```

## Composite Index Best Practices

The order of columns in a composite index matters significantly:

1. **Most selective column first**: Put the column that narrows down results the most at the front
2. **Equality before range**: Columns used with `=` should come before columns used with `>`, `<`, `BETWEEN`
3. **Common queries first**: Order based on your most frequent query patterns

```sql
-- If you often query: WHERE user_id = ? AND order_date > ?
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);

-- If you often query: WHERE status = ? AND created_at BETWEEN ? AND ?
CREATE INDEX idx_orders_status_created ON orders(status, created_at);
```

## Covering Indexes

A covering index includes all columns needed by a query, allowing an "Index Only Scan":

```sql
-- Query needs: user_id, email, status
CREATE INDEX idx_users_covering ON users(user_id, email, status);

-- This query can use index-only scan
SELECT user_id, email, status FROM users WHERE user_id = 123;
```

## Index Bloat and Cleanup

Over time, indexes can become bloated (especially in PostgreSQL):

```sql
-- PostgreSQL: Check index bloat
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM
    pg_stat_user_indexes
ORDER BY
    pg_relation_size(indexrelid) DESC;

-- Rebuild bloated indexes
REINDEX INDEX CONCURRENTLY idx_users_email;  -- PostgreSQL (doesn't lock table)
```

## Monitoring Index Effectiveness

```sql
-- PostgreSQL: Find unused indexes
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM
    pg_stat_user_indexes
WHERE
    idx_scan = 0
    AND indexrelname NOT LIKE 'pg_toast%'
ORDER BY
    pg_relation_size(indexrelid) DESC;

-- MySQL: Check index cardinality
SHOW INDEX FROM users;
```
