# Query Optimization

## Using EXPLAIN

```sql
-- PostgreSQL EXPLAIN
EXPLAIN ANALYZE
SELECT
    users.name,
    COUNT(orders.id) as order_count
FROM
    users
LEFT JOIN
    orders ON users.id = orders.user_id
GROUP BY
    users.id, users.name;

-- Look for:
-- - Seq Scan (bad) vs Index Scan (good)
-- - High cost numbers
-- - Large row counts being processed
```

## Key Performance Indicators

- **Seq Scan**: Table scan without index (slow for large tables)
- **Index Scan**: Using an index (fast)
- **Index Only Scan**: Best case - all data from index
- **Nested Loop**: Good for small datasets
- **Hash Join**: Good for larger datasets
- **Merge Join**: Good for sorted data

## Optimization Techniques

```sql
-- BAD: Using OR with different columns
SELECT * FROM users WHERE first_name = 'John' OR last_name = 'Smith';

-- GOOD: Use UNION if possible
SELECT * FROM users WHERE first_name = 'John'
UNION
SELECT * FROM users WHERE last_name = 'Smith';

-- BAD: Function on indexed column prevents index usage
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- GOOD: Use functional index or store lowercase
SELECT * FROM users WHERE email = LOWER('user@example.com');
-- Create index: CREATE INDEX idx_email_lower ON users(LOWER(email));

-- BAD: SELECT *
SELECT * FROM large_table WHERE id = 123;

-- GOOD: Select only needed columns
SELECT id, name, email FROM large_table WHERE id = 123;

-- BAD: Subquery in SELECT (executes for each row)
SELECT
    name,
    (SELECT COUNT(*) FROM orders WHERE user_id = users.id) as order_count
FROM
    users;

-- GOOD: Use JOIN instead
SELECT
    users.name,
    COUNT(orders.id) as order_count
FROM
    users
LEFT JOIN
    orders ON users.id = orders.user_id
GROUP BY
    users.id, users.name;
```

## N+1 Query Problem

```python
# BAD: N+1 queries (1 + N queries total)
users = db.query("SELECT * FROM users")
for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user.id)
    # This executes a query for EACH user

# GOOD: Single query with JOIN
result = db.query("""
    SELECT
        users.*,
        orders.*
    FROM users
    LEFT JOIN orders ON users.id = orders.user_id
""")
```

## Performance Tips

### Use LIMIT Appropriately

```sql
-- BAD: Returns all rows (could be millions)
SELECT * FROM large_table WHERE status = 'active';

-- GOOD: Limit results for exploratory queries
SELECT * FROM large_table WHERE status = 'active' LIMIT 100;
```

### Avoid Implicit Type Conversions

```sql
-- BAD: String comparison on INT column prevents index usage
SELECT * FROM users WHERE user_id = '123';

-- GOOD: Use correct type
SELECT * FROM users WHERE user_id = 123;
```

### Use EXISTS Instead of COUNT(*)

```sql
-- BAD: Counts all rows
SELECT COUNT(*) FROM orders WHERE user_id = 123;

-- GOOD: Just check existence
SELECT EXISTS(SELECT 1 FROM orders WHERE user_id = 123);
```

### Avoid SELECT DISTINCT as Band-Aid

```sql
-- BAD: Band-aid solution
SELECT DISTINCT user_id, name FROM users
JOIN orders ON users.id = orders.user_id;

-- GOOD: Fix the underlying issue
SELECT users.id, users.name FROM users
WHERE EXISTS (SELECT 1 FROM orders WHERE orders.user_id = users.id);
```
