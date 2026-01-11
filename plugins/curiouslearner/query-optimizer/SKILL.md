---
name: query-optimizer
description: Analyze and optimize SQL queries for better performance and efficiency.
---

# Query Optimizer Skill

Analyze and optimize SQL queries for better performance and efficiency.

## Instructions

You are a database performance optimization expert. When invoked:

1. **Analyze Query Performance**:
   - Use EXPLAIN/EXPLAIN ANALYZE to understand execution plan
   - Identify slow queries from logs
   - Measure query execution time
   - Detect full table scans and missing indexes

2. **Identify Bottlenecks**:
   - Find N+1 query problems
   - Detect inefficient JOINs
   - Identify missing or unused indexes
   - Spot suboptimal WHERE clauses

3. **Optimize Queries**:
   - Add appropriate indexes
   - Rewrite queries for better performance
   - Suggest caching strategies
   - Recommend query restructuring

4. **Provide Recommendations**:
   - Index creation suggestions
   - Query rewriting alternatives
   - Database configuration tuning
   - Monitoring and alerting setup

## Supported Databases

- **SQL**: PostgreSQL, MySQL, MariaDB, SQL Server, SQLite
- **Analysis Tools**: EXPLAIN, EXPLAIN ANALYZE, Query Profiler
- **Monitoring**: pg_stat_statements, slow query log, performance schema

## Usage Examples

```
@query-optimizer
@query-optimizer --analyze-slow-queries
@query-optimizer --suggest-indexes
@query-optimizer --explain SELECT * FROM users WHERE email = 'test@example.com'
@query-optimizer --fix-n-plus-one
```

## Query Analysis Tools

### PostgreSQL - EXPLAIN ANALYZE
```sql
-- Basic EXPLAIN
EXPLAIN
SELECT u.id, u.username, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.active = true
GROUP BY u.id, u.username;

-- EXPLAIN ANALYZE - actually runs the query
EXPLAIN ANALYZE
SELECT u.id, u.username, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.active = true
GROUP BY u.id, u.username;

-- EXPLAIN with all options (PostgreSQL)
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
SELECT * FROM orders
WHERE user_id = 123
  AND created_at >= '2024-01-01';
```

**Reading EXPLAIN Output:**
```
Seq Scan on users  (cost=0.00..1234.56 rows=10000 width=32)
  Filter: (active = true)

-- Seq Scan = Sequential Scan (full table scan) - BAD for large tables
-- cost=0.00..1234.56 = startup cost..total cost
-- rows=10000 = estimated rows
-- width=32 = average row size in bytes
```

```
Index Scan using idx_users_email on users  (cost=0.29..8.30 rows=1 width=32)
  Index Cond: (email = 'test@example.com'::text)

-- Index Scan = Using index - GOOD
-- Much lower cost than Seq Scan
-- rows=1 = accurate estimate
```

### MySQL - EXPLAIN
```sql
-- MySQL EXPLAIN
EXPLAIN
SELECT u.id, u.username, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.active = true
GROUP BY u.id, u.username;

-- EXPLAIN with execution stats (MySQL 8.0+)
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE user_id = 123;

-- Show warnings for optimization info
EXPLAIN
SELECT * FROM users WHERE email = 'test@example.com';
SHOW WARNINGS;
```

**MySQL EXPLAIN Output:**
```
+----+-------------+-------+------+---------------+---------+---------+-------+------+-------------+
| id | select_type | table | type | possible_keys | key     | key_len | ref   | rows | Extra       |
+----+-------------+-------+------+---------------+---------+---------+-------+------+-------------+
|  1 | SIMPLE      | users | ALL  | NULL          | NULL    | NULL    | NULL  | 1000 | Using where |
+----+-------------+-------+------+---------------+---------+---------+-------+------+-------------+

-- type=ALL means full table scan - BAD
-- key=NULL means no index used

+----+-------------+-------+------+---------------+----------------+---------+-------+------+-------+
| id | select_type | table | type | possible_keys | key            | key_len | ref   | rows | Extra |
+----+-------------+-------+------+---------------+----------------+---------+-------+------+-------+
|  1 | SIMPLE      | users | ref  | idx_users_email| idx_users_email| 767     | const |    1 | NULL  |
+----+-------------+-------+------+---------------+----------------+---------+-------+------+-------+

-- type=ref means index lookup - GOOD
-- key shows index being used
```

## Common Performance Issues

### 1. Missing Indexes

**Problem:**
```sql
-- Slow query - full table scan
SELECT * FROM users WHERE email = 'john@example.com';

-- EXPLAIN shows:
-- Seq Scan on users (cost=0.00..1500.00 rows=1 width=100)
--   Filter: (email = 'john@example.com')
```

**Solution:**
```sql
-- Add index on email column
CREATE INDEX idx_users_email ON users(email);

-- Now EXPLAIN shows:
-- Index Scan using idx_users_email on users (cost=0.29..8.30 rows=1 width=100)
--   Index Cond: (email = 'john@example.com')

-- Query becomes 100x faster
```

### 2. N+1 Query Problem

**Problem:**
```javascript
// ORM code causing N+1 queries
const users = await User.findAll(); // 1 query

for (const user of users) {
  const orders = await Order.findAll({
    where: { userId: user.id }  // N queries (one per user)
  });
  console.log(`${user.name}: ${orders.length} orders`);
}

// Total: 1 + N queries for N users
// For 100 users = 101 queries!
```

**Solution:**
```javascript
// Use eager loading - single query with JOIN
const users = await User.findAll({
  include: [{
    model: Order,
    attributes: ['id', 'total_amount']
  }]
});

for (const user of users) {
  console.log(`${user.name}: ${user.orders.length} orders`);
}

// Total: 1 query regardless of user count
```

**SQL Equivalent:**
```sql
-- Instead of multiple queries:
SELECT * FROM users;
SELECT * FROM orders WHERE user_id = 1;
SELECT * FROM orders WHERE user_id = 2;
-- ... (N more queries)

-- Use single JOIN query:
SELECT
  u.id,
  u.name,
  COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

### 3. SELECT * Inefficiency

**Problem:**
```sql
-- Fetching all columns when only need few
SELECT * FROM products
WHERE category_id = 5;

-- Fetches: id, name, description (large text), image_url, specs (json),
--         price, stock, created_at, updated_at, etc.
```

**Solution:**
```sql
-- Only select needed columns
SELECT id, name, price, stock
FROM products
WHERE category_id = 5;

-- Benefits:
-- - Less data transferred
-- - Faster query execution
-- - Lower memory usage
-- - Can use covering indexes
```

### 4. Inefficient Pagination

**Problem:**
```sql
-- OFFSET becomes slow with large offsets
SELECT * FROM users
ORDER BY created_at DESC
LIMIT 20 OFFSET 10000;

-- Database must:
-- 1. Sort all rows
-- 2. Skip 10,000 rows
-- 3. Return next 20
-- Gets slower as offset increases
```

**Solution:**
```sql
-- Use cursor-based (keyset) pagination
SELECT * FROM users
WHERE created_at < '2024-01-01 12:00:00'
  AND (created_at < '2024-01-01 12:00:00' OR id < 12345)
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Or with indexed column:
SELECT * FROM users
WHERE id < 10000
ORDER BY id DESC
LIMIT 20;

-- Benefits:
-- - Consistent performance regardless of page
-- - Uses index efficiently
-- - No need to skip rows
```

### 5. Function on Indexed Column

**Problem:**
```sql
-- Function prevents index usage
SELECT * FROM users
WHERE LOWER(email) = 'john@example.com';

-- EXPLAIN shows Seq Scan (index not used)
```

**Solution 1 - Store lowercase:**
```sql
-- Add computed column
ALTER TABLE users ADD COLUMN email_lower VARCHAR(255)
  GENERATED ALWAYS AS (LOWER(email)) STORED;

CREATE INDEX idx_users_email_lower ON users(email_lower);

-- Query:
SELECT * FROM users
WHERE email_lower = 'john@example.com';
```

**Solution 2 - Functional index (PostgreSQL):**
```sql
-- Create index on function result
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- Now original query uses index
SELECT * FROM users
WHERE LOWER(email) = 'john@example.com';
```

**Solution 3 - Case-insensitive collation:**
```sql
-- PostgreSQL - use citext type
ALTER TABLE users ALTER COLUMN email TYPE citext;

-- Query without LOWER:
SELECT * FROM users WHERE email = 'john@example.com';
-- Automatically case-insensitive
```

### 6. Inefficient JOINs

**Problem:**
```sql
-- Multiple JOINs without proper indexes
SELECT
  u.username,
  o.id as order_id,
  p.name as product_name
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE u.email = 'john@example.com';

-- Slow if missing indexes on:
-- - users.email
-- - orders.user_id
-- - order_items.order_id
-- - order_items.product_id
```

**Solution:**
```sql
-- Add necessary indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- Now query uses indexes for all JOINs
-- EXPLAIN will show "Index Scan" for each table
```

### 7. OR Conditions

**Problem:**
```sql
-- OR prevents efficient index usage
SELECT * FROM users
WHERE username = 'john' OR email = 'john@example.com';

-- May not use indexes optimally
```

**Solution:**
```sql
-- Use UNION for better index usage
SELECT * FROM users WHERE username = 'john'
UNION
SELECT * FROM users WHERE email = 'john@example.com';

-- Each subquery uses its own index
-- Deduplicates results automatically
```

### 8. NOT IN with Subquery

**Problem:**
```sql
-- Slow subquery execution
SELECT * FROM users
WHERE id NOT IN (
  SELECT user_id FROM banned_users
);

-- Can be very slow with large subquery results
```

**Solution:**
```sql
-- Use LEFT JOIN with NULL check
SELECT u.*
FROM users u
LEFT JOIN banned_users bu ON u.id = bu.user_id
WHERE bu.user_id IS NULL;

-- Or use NOT EXISTS (often faster):
SELECT u.*
FROM users u
WHERE NOT EXISTS (
  SELECT 1 FROM banned_users bu
  WHERE bu.user_id = u.id
);
```

## Index Optimization

### When to Add Indexes

**Add indexes for:**
- Primary keys (automatic in most databases)
- Foreign keys (critical for JOINs)
- Columns in WHERE clauses
- Columns in ORDER BY clauses
- Columns in GROUP BY clauses
- Columns in JOIN conditions
- Columns with high cardinality (many unique values)

### Index Types

**B-Tree Index (Default):**
```sql
-- Best for: equality (=) and range (<, >, BETWEEN) queries
CREATE INDEX idx_users_created_at ON users(created_at);

-- Good for:
SELECT * FROM users WHERE created_at > '2024-01-01';
SELECT * FROM users WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31';
```

**Composite Index:**
```sql
-- Index on multiple columns
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Used for queries filtering both columns
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';

-- Also used for queries on first column only
SELECT * FROM orders WHERE user_id = 123;

-- NOT used for queries on second column only
SELECT * FROM orders WHERE status = 'pending'; -- Won't use this index

-- Column order matters! Most selective first
```

**Partial Index (PostgreSQL):**
```sql
-- Index only subset of rows
CREATE INDEX idx_active_users ON users(email)
WHERE active = true;

-- Smaller index, faster queries for active users
SELECT * FROM users WHERE email = 'john@example.com' AND active = true;
```

**GIN Index (PostgreSQL - for arrays, JSONB, full-text):**
```sql
-- For JSONB columns
CREATE INDEX idx_products_metadata ON products USING GIN(metadata);

-- Query JSONB data
SELECT * FROM products
WHERE metadata @> '{"brand": "Apple"}';

-- For array columns
CREATE INDEX idx_tags ON posts USING GIN(tags);

-- Query arrays
SELECT * FROM posts WHERE tags @> ARRAY['postgresql'];
```

**Full-Text Search Index:**
```sql
-- PostgreSQL
CREATE INDEX idx_products_search ON products
USING GIN(to_tsvector('english', name || ' ' || description));

-- Full-text search query
SELECT * FROM products
WHERE to_tsvector('english', name || ' ' || description)
  @@ to_tsquery('english', 'laptop & gaming');
```

### Covering Index

**Concept:**
```sql
-- Covering index includes all columns needed by query
CREATE INDEX idx_users_email_username ON users(email, username);

-- This query can be answered entirely from index (no table access)
SELECT username FROM users WHERE email = 'john@example.com';

-- PostgreSQL: Index-Only Scan
-- MySQL: Using index
```

**With INCLUDE (PostgreSQL 11+):**
```sql
-- Include non-indexed columns in index leaf nodes
CREATE INDEX idx_users_email ON users(email)
INCLUDE (username, created_at);

-- Query can use index without table access
SELECT username, created_at
FROM users
WHERE email = 'john@example.com';
```

### Index Maintenance

**Find Unused Indexes (PostgreSQL):**
```sql
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Drop unused indexes to save space and improve write performance
```

**Find Duplicate Indexes:**
```sql
-- PostgreSQL query to find duplicate indexes
SELECT
  indrelid::regclass AS table_name,
  array_agg(indexrelid::regclass) AS indexes
FROM pg_index
GROUP BY indrelid, indkey
HAVING COUNT(*) > 1;
```

**Rebuild Fragmented Indexes:**
```sql
-- PostgreSQL
REINDEX INDEX idx_users_email;
REINDEX TABLE users;

-- MySQL
OPTIMIZE TABLE users;
```

## Query Rewriting Examples

### Example 1: Aggregation Optimization

**Before:**
```sql
SELECT
  u.id,
  u.username,
  (SELECT COUNT(*) FROM orders WHERE user_id = u.id) as order_count,
  (SELECT SUM(total_amount) FROM orders WHERE user_id = u.id) as total_spent
FROM users u
WHERE u.active = true;

-- N+1 problem: 1 query + 2 subqueries per user
```

**After:**
```sql
SELECT
  u.id,
  u.username,
  COUNT(o.id) as order_count,
  COALESCE(SUM(o.total_amount), 0) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.active = true
GROUP BY u.id, u.username;

-- Single query with JOIN
-- Much faster!
```

### Example 2: EXISTS vs IN

**Before:**
```sql
SELECT * FROM products
WHERE id IN (
  SELECT product_id FROM order_items
  WHERE created_at >= '2024-01-01'
);

-- Subquery returns all product_ids (potentially large result set)
```

**After:**
```sql
SELECT p.* FROM products p
WHERE EXISTS (
  SELECT 1 FROM order_items oi
  WHERE oi.product_id = p.id
    AND oi.created_at >= '2024-01-01'
);

-- EXISTS stops at first match (more efficient)
```

### Example 3: Avoid Cartesian Products

**Before:**
```sql
-- Accidental cartesian product
SELECT *
FROM users u, orders o
WHERE u.active = true
  AND o.status = 'completed';

-- Returns every user combined with every completed order!
-- Missing JOIN condition
```

**After:**
```sql
SELECT u.*, o.*
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE u.active = true
  AND o.status = 'completed';

-- Proper JOIN condition
```

### Example 4: Optimize DISTINCT

**Before:**
```sql
SELECT DISTINCT user_id
FROM orders
WHERE status = 'completed';

-- DISTINCT requires sorting/deduplication
```

**After:**
```sql
SELECT user_id
FROM orders
WHERE status = 'completed'
GROUP BY user_id;

-- GROUP BY often faster than DISTINCT
-- Or if unique constraint exists:
SELECT DISTINCT ON (user_id) user_id, created_at
FROM orders
WHERE status = 'completed'
ORDER BY user_id, created_at DESC;
```

## Monitoring Slow Queries

### PostgreSQL - pg_stat_statements

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slowest queries
SELECT
  substring(query, 1, 50) AS short_query,
  round(total_exec_time::numeric, 2) AS total_time,
  calls,
  round(mean_exec_time::numeric, 2) AS mean_time,
  round((100 * total_exec_time / sum(total_exec_time) OVER ())::numeric, 2) AS percentage
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Find queries with most calls
SELECT
  substring(query, 1, 50) AS short_query,
  calls,
  round(mean_exec_time::numeric, 2) AS mean_time
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 10;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

### MySQL - Slow Query Log

```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1; -- Log queries taking > 1 second
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow-query.log';

-- Log queries not using indexes
SET GLOBAL log_queries_not_using_indexes = 'ON';

-- Analyze slow query log
-- Use mysqldumpslow tool:
-- mysqldumpslow -s t -t 10 /var/log/mysql/slow-query.log
```

### Performance Schema (MySQL)

```sql
-- Enable performance schema
SET GLOBAL performance_schema = ON;

-- Find slowest statements
SELECT
  DIGEST_TEXT,
  COUNT_STAR AS executions,
  ROUND(AVG_TIMER_WAIT / 1000000000, 2) AS avg_ms,
  ROUND(SUM_TIMER_WAIT / 1000000000, 2) AS total_ms
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;
```

## Best Practices

### DO ✓
- **Use EXPLAIN** before and after optimization
- **Add indexes on foreign keys** - Critical for JOINs
- **Use covering indexes** when possible
- **Paginate large result sets** - Avoid loading all data
- **Monitor query performance** - Use pg_stat_statements or slow query log
- **Test on production-like data** - Performance differs with data volume
- **Use connection pooling** - Reduce connection overhead
- **Cache frequently accessed data** - Redis, Memcached
- **Archive old data** - Keep active tables smaller
- **Regular VACUUM/ANALYZE** (PostgreSQL) - Update statistics

### DON'T ✗
- **Don't use SELECT *** - Fetch only needed columns
- **Don't over-index** - Each index slows down writes
- **Don't ignore EXPLAIN warnings** - They indicate problems
- **Don't use functions on indexed columns** - Prevents index usage
- **Don't fetch more data than needed** - Use LIMIT
- **Don't use OFFSET for deep pagination** - Use cursor-based instead
- **Don't ignore database logs** - Monitor for errors
- **Don't optimize prematurely** - Profile first, optimize bottlenecks
- **Don't forget about write performance** - Indexes slow down INSERTs
- **Don't skip testing** - Verify optimizations actually help

## Query Optimization Checklist

```markdown
## Query Optimization Checklist

- [ ] Run EXPLAIN/EXPLAIN ANALYZE on query
- [ ] Check if query uses indexes (no Seq Scan on large tables)
- [ ] Verify indexes exist on:
  - [ ] Foreign key columns
  - [ ] WHERE clause columns
  - [ ] JOIN condition columns
  - [ ] ORDER BY columns
- [ ] SELECT only needed columns (avoid SELECT *)
- [ ] Use appropriate JOIN type (INNER vs LEFT)
- [ ] Avoid N+1 queries (use JOINs or eager loading)
- [ ] Use pagination for large result sets
- [ ] Check for unused indexes (slow down writes)
- [ ] Consider query caching for frequent queries
- [ ] Test with production-like data volumes
- [ ] Monitor query performance over time
```

## Notes

- Always measure before and after optimization
- Index creation can take time on large tables
- Too many indexes slow down INSERT/UPDATE/DELETE
- Keep database statistics up to date (ANALYZE)
- Consider read replicas for read-heavy workloads
- Use database-specific features when beneficial
- Document optimization decisions for team
- Regular performance audits prevent degradation
