# SQL Indexing Strategies

Comprehensive guide to database indexing for query optimization.

## Index Types

### B-Tree (Default)

Best for: range queries, equality, ORDER BY, LIKE prefix

```sql
-- Standard index
CREATE INDEX idx_users_email ON users(email);

-- Unique index
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Works well for:
WHERE email = 'x@y.com'           -- equality
WHERE email LIKE 'john%'          -- prefix search
WHERE created_at > '2024-01-01'   -- range
ORDER BY created_at               -- sorting
```

### Hash Index

Best for: exact equality only (PostgreSQL)

```sql
CREATE INDEX idx_users_email ON users USING hash(email);

-- Only good for:
WHERE email = 'x@y.com'

-- NOT useful for:
WHERE email LIKE '%@gmail.com'
WHERE email > 'a'
ORDER BY email
```

### GIN (Generalized Inverted Index)

Best for: arrays, JSONB, full-text search

```sql
-- Array containment
CREATE INDEX idx_posts_tags ON posts USING gin(tags);
WHERE tags @> ARRAY['python', 'sql']

-- JSONB queries
CREATE INDEX idx_data_json ON events USING gin(payload jsonb_path_ops);
WHERE payload @> '{"type": "click"}'

-- Full-text search
CREATE INDEX idx_posts_fts ON posts USING gin(to_tsvector('english', content));
WHERE to_tsvector('english', content) @@ to_tsquery('database & optimization')
```

### GiST (Generalized Search Tree)

Best for: geometric data, ranges, full-text

```sql
-- Range types
CREATE INDEX idx_bookings_dates ON bookings USING gist(daterange(start_date, end_date));
WHERE daterange(start_date, end_date) && '[2024-01-01, 2024-01-31]'

-- Geometric
CREATE INDEX idx_locations_point ON locations USING gist(coordinates);
WHERE coordinates <-> point(40.7, -74.0) < 10
```

## Composite Indexes

### Column Order Matters

```sql
-- Leftmost prefix rule
CREATE INDEX idx_orders ON orders(user_id, status, created_at);

-- This index supports:
WHERE user_id = 123                              -- ✓
WHERE user_id = 123 AND status = 'pending'       -- ✓
WHERE user_id = 123 AND status = 'pending' AND created_at > '2024-01-01'  -- ✓
WHERE user_id = 123 AND created_at > '2024-01-01'  -- Partial (user_id only)
WHERE status = 'pending'                          -- ✗ (user_id not present)
```

### Optimal Column Order

```sql
-- Rule: Most selective first, then equality, then range
-- If filtering by status (high cardinality) and date range:
CREATE INDEX idx_orders_status_date ON orders(status, created_at);

-- If status has few values, but user_id is selective:
CREATE INDEX idx_orders_user_status_date ON orders(user_id, status, created_at);
```

## Covering Indexes

Include columns to avoid table lookup:

```sql
-- Query needs name but filters by email
SELECT name FROM users WHERE email = 'x@y.com';

-- Covering index (PostgreSQL)
CREATE INDEX idx_users_email_name ON users(email) INCLUDE (name);

-- Now the query uses index-only scan
-- (no need to read the actual table row)
```

### When to Use

```sql
-- Frequently accessed columns
CREATE INDEX idx_orders_status ON orders(status)
INCLUDE (total, created_at);

-- Supports without table access:
SELECT total, created_at FROM orders WHERE status = 'pending';
```

## Partial Indexes

Index only rows matching a condition:

```sql
-- Only index active users (smaller, faster index)
CREATE INDEX idx_users_active ON users(email)
WHERE status = 'active';

-- Only works for queries that include the condition:
SELECT * FROM users WHERE email = 'x@y.com' AND status = 'active';  -- ✓
SELECT * FROM users WHERE email = 'x@y.com';                        -- ✗

-- Index only recent data
CREATE INDEX idx_orders_recent ON orders(created_at)
WHERE created_at > '2024-01-01';
```

## Expression Indexes

Index computed values:

```sql
-- Case-insensitive search
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
WHERE LOWER(email) = 'john@example.com'  -- ✓
WHERE email = 'John@Example.com'          -- ✗

-- Date extraction
CREATE INDEX idx_orders_year ON orders(EXTRACT(YEAR FROM created_at));
WHERE EXTRACT(YEAR FROM created_at) = 2024  -- ✓
WHERE created_at >= '2024-01-01'            -- ✗ (use regular index)

-- JSON field
CREATE INDEX idx_events_type ON events((payload->>'type'));
WHERE payload->>'type' = 'click'
```

## Query Analysis

### EXPLAIN

```sql
EXPLAIN SELECT * FROM users WHERE email = 'x@y.com';

-- Key things to look for:
-- Seq Scan       - Full table scan (bad for large tables)
-- Index Scan     - Using index, then fetching rows
-- Index Only Scan - Using covering index (best)
-- Bitmap Scan    - Multiple index conditions combined
```

### EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE status = 'pending';

-- Shows actual execution:
-- Planning Time: 0.5 ms
-- Execution Time: 12.3 ms
-- Rows: actual rows returned
-- Loops: how many times operation ran
```

### Identifying Slow Queries

```sql
-- PostgreSQL: Enable slow query logging
SET log_min_duration_statement = 1000;  -- Log queries > 1 second

-- Find missing indexes (PostgreSQL)
SELECT
    schemaname || '.' || relname as table,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / NULLIF(seq_scan, 0) as avg_seq_rows
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 10;
```

## Anti-Patterns

### Functions on Indexed Columns

```sql
-- BAD: Function prevents index use
WHERE YEAR(created_at) = 2024

-- GOOD: Rewrite as range
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
```

### OR Conditions

```sql
-- BAD: May not use index efficiently
WHERE status = 'pending' OR status = 'processing'

-- GOOD: Use IN
WHERE status IN ('pending', 'processing')

-- Or use UNION for complex OR
SELECT * FROM orders WHERE status = 'pending'
UNION ALL
SELECT * FROM orders WHERE user_id = 123 AND status != 'pending'
```

### Leading Wildcards

```sql
-- BAD: Can't use index
WHERE email LIKE '%@gmail.com'

-- GOOD: Use prefix
WHERE email LIKE 'john%'

-- Alternative: Full-text search or trigram index
CREATE INDEX idx_email_trigram ON users USING gin(email gin_trgm_ops);
```

## Maintenance

### Index Health

```sql
-- Check index usage (PostgreSQL)
SELECT
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0  -- Unused indexes
ORDER BY pg_relation_size(indexrelid) DESC;

-- Index size
SELECT
    indexrelname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Rebuild Indexes

```sql
-- Rebuild index (locks table)
REINDEX INDEX idx_users_email;

-- Concurrent rebuild (PostgreSQL 12+)
REINDEX INDEX CONCURRENTLY idx_users_email;

-- Rebuild all indexes on table
REINDEX TABLE users;
```

## Quick Reference

| Scenario | Index Strategy |
|----------|---------------|
| Equality lookup | B-tree on column |
| Range queries | B-tree on column |
| Multiple conditions | Composite index (selective first) |
| Avoid table access | Covering index with INCLUDE |
| Subset of rows | Partial index |
| Case-insensitive | Expression index on LOWER() |
| JSON/array queries | GIN index |
| Full-text search | GIN with tsvector |
| Geometric/range | GiST index |
