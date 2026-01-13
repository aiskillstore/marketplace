# Common SQL Pitfalls

## 1. N+1 Query Problem

**The Issue:**
Executing one query to get a list, then N additional queries for each item in the list.

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

**Why it's bad:**
- Multiplies database round trips
- Scales poorly with data growth
- Network latency compounds the problem

## 2. Not Using LIMIT for Exploratory Queries

```sql
-- BAD: Returns all rows (could be millions)
SELECT * FROM large_table WHERE status = 'active';

-- GOOD: Limit results for exploratory queries
SELECT * FROM large_table WHERE status = 'active' LIMIT 100;
```

**Why it matters:**
- Prevents accidentally loading huge result sets
- Faster query execution
- Reduces memory usage in application

## 3. Implicit Type Conversions

```sql
-- BAD: String comparison on INT column prevents index usage
SELECT * FROM users WHERE user_id = '123';

-- GOOD: Use correct type
SELECT * FROM users WHERE user_id = 123;

-- BAD: Comparing different numeric types
SELECT * FROM products WHERE price = 19;  -- price is DECIMAL

-- GOOD: Match the type
SELECT * FROM products WHERE price = 19.00;
```

**Impact:**
- Can prevent index usage
- Slower query performance
- Unexpected comparison results

## 4. Using COUNT(*) When You Just Need EXISTS

```sql
-- BAD: Counts all rows (expensive)
SELECT COUNT(*) FROM orders WHERE user_id = 123;

-- GOOD: Just check existence (stops at first match)
SELECT EXISTS(SELECT 1 FROM orders WHERE user_id = 123);
```

**Performance difference:**
- COUNT(*) scans all matching rows
- EXISTS stops at first match
- Huge performance difference for large result sets

## 5. Not Handling NULLs Properly

```sql
-- BAD: NULL comparisons always return NULL (not TRUE or FALSE)
SELECT * FROM users WHERE deleted_at = NULL;  -- Returns no rows!

-- GOOD: Use IS NULL / IS NOT NULL
SELECT * FROM users WHERE deleted_at IS NULL;

-- BAD: Forgetting NULL in aggregations
SELECT SUM(total_amount) FROM orders;  -- NULLs are ignored, might be confusing

-- GOOD: Be explicit about NULL handling
SELECT COALESCE(SUM(total_amount), 0) as total FROM orders;
```

**NULL gotchas:**
- NULL = NULL is NULL (not TRUE)
- NULL != NULL is NULL (not TRUE)
- NULL in arithmetic makes result NULL: 5 + NULL = NULL
- COUNT(*) includes NULLs, COUNT(column) excludes NULLs

## 6. Using SELECT DISTINCT as a Band-Aid

```sql
-- BAD: Using DISTINCT to hide a join problem
SELECT DISTINCT user_id, name FROM users
JOIN orders ON users.id = orders.user_id;

-- GOOD: Fix the underlying issue
SELECT users.id, users.name FROM users
WHERE EXISTS (SELECT 1 FROM orders WHERE orders.user_id = users.id);

-- Or if you want the orders too:
SELECT DISTINCT ON (users.id) users.id, users.name, orders.*
FROM users
JOIN orders ON users.id = orders.user_id;
```

**Why DISTINCT is often wrong:**
- Hides the real problem (wrong join or query structure)
- Performance overhead
- May mask bugs

## 7. Forgetting Transactions for Related Operations

```sql
-- BAD: No transaction (money could be lost if second statement fails)
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;

-- GOOD: Use transaction for atomicity
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
COMMIT;
```

**Critical for:**
- Financial operations
- Related record creation
- Maintaining data consistency

## 8. Using OR in WHERE with Different Columns

```sql
-- BAD: OR with different columns can't use indexes efficiently
SELECT * FROM users WHERE first_name = 'John' OR last_name = 'Smith';

-- GOOD: Use UNION if possible
SELECT * FROM users WHERE first_name = 'John'
UNION
SELECT * FROM users WHERE last_name = 'Smith';
```

**Performance impact:**
- OR often forces full table scan
- UNION can use separate indexes

## 9. Using Functions on Indexed Columns

```sql
-- BAD: Function on indexed column prevents index usage
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';
SELECT * FROM orders WHERE YEAR(order_date) = 2024;

-- GOOD: Avoid function on indexed column
SELECT * FROM users WHERE email = LOWER('user@example.com');
SELECT * FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';

-- ALTERNATIVE: Create functional index
CREATE INDEX idx_email_lower ON users(LOWER(email));
-- Now the first query can use the index
```

## 10. Cartesian Products (Missing JOIN Condition)

```sql
-- BAD: Missing join condition creates cartesian product
SELECT users.name, orders.total
FROM users, orders;  -- Every user paired with every order!

-- GOOD: Always specify join condition
SELECT users.name, orders.total
FROM users
INNER JOIN orders ON users.id = orders.user_id;
```

**Result:**
- Returns user_count × order_count rows
- Extremely slow
- Wrong results

## 11. Not Using LIMIT in DELETE/UPDATE on Large Tables

```sql
-- BAD: Can lock table for extended period
DELETE FROM logs WHERE created_at < '2020-01-01';  -- Could be millions of rows

-- GOOD: Delete in batches
DELETE FROM logs
WHERE log_id IN (
    SELECT log_id FROM logs
    WHERE created_at < '2020-01-01'
    LIMIT 10000
);
-- Repeat until no more rows
```

**Why batch:**
- Prevents long-running locks
- Allows other queries to run
- Can be paused/resumed

## 12. Storing Encrypted/Hashed Data Without Length Consideration

```sql
-- BAD: Hash output is 64 chars but column is 50
CREATE TABLE users (
    password_hash VARCHAR(50)  -- SHA-256 outputs 64 characters!
);

-- GOOD: Know your data size requirements
CREATE TABLE users (
    password_hash VARCHAR(64),  -- Exact size for SHA-256
    email_encrypted VARCHAR(255)  -- Allow for encryption overhead
);
```

## 13. Using Float for Currency

```sql
-- BAD: Floating point precision errors
CREATE TABLE orders (
    total FLOAT
);
-- Can lead to: 10.10 being stored as 10.099999...

-- GOOD: Use DECIMAL for exact precision
CREATE TABLE orders (
    total DECIMAL(10, 2)  -- 10 digits, 2 after decimal
);
```

**Why DECIMAL:**
- Exact precision
- No rounding errors
- Essential for financial calculations

## 14. Not Considering NULL in Unique Constraints

```sql
-- In most databases, multiple NULLs are allowed in UNIQUE columns
CREATE TABLE users (
    email VARCHAR(255) UNIQUE  -- Multiple NULL emails allowed!
);

-- If you want only one NULL, use partial unique index (PostgreSQL)
CREATE UNIQUE INDEX idx_users_email_unique ON users(email) WHERE email IS NOT NULL;
```

## 15. Inefficient Pagination

```sql
-- BAD: Gets slower as offset increases
SELECT * FROM products
ORDER BY created_at
LIMIT 20 OFFSET 100000;  -- Scans first 100,020 rows

-- GOOD: Use keyset pagination
SELECT * FROM products
WHERE created_at > '2024-01-01 12:34:56'  -- Last seen value
ORDER BY created_at
LIMIT 20;
```

## 16. Forgetting Index Column Order in Composite Indexes

```sql
-- Index on (user_id, created_at)
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);

-- CAN use index (leftmost column)
SELECT * FROM orders WHERE user_id = 123;

-- CANNOT use index efficiently (not leftmost)
SELECT * FROM orders WHERE created_at > '2024-01-01';

-- CAN use index (both columns)
SELECT * FROM orders WHERE user_id = 123 AND created_at > '2024-01-01';
```

## 17. Using VARCHAR(255) for Everything

```sql
-- BAD: Unnecessarily large VARCHAR limits
CREATE TABLE users (
    email VARCHAR(255),        -- Email max is ~254
    state VARCHAR(255),        -- US state is 2 chars
    username VARCHAR(255)      -- Your app limits to 30
);

-- GOOD: Use appropriate sizes
CREATE TABLE users (
    email VARCHAR(254),        -- Industry standard max
    state CHAR(2),            -- Fixed size
    username VARCHAR(30)       -- Match business rules
);
```

**Why it matters:**
- Wastes space in indexes
- Can allow invalid data
- Self-documenting schema

## 18. Not Handling Connection Pooling Properly

```python
# BAD: Creating new connection for each query
def get_user(user_id):
    conn = create_connection()  # Expensive!
    result = conn.execute("SELECT * FROM users WHERE id = ?", user_id)
    conn.close()
    return result

# GOOD: Use connection pooling
pool = create_connection_pool(min_size=5, max_size=20)

def get_user(user_id):
    with pool.get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", user_id)
```

## 19. Using String Concatenation Instead of Parameterized Queries

```python
# BAD: SQL injection vulnerability
user_input = "admin'; DROP TABLE users; --"
query = f"SELECT * FROM users WHERE username = '{user_input}'"
# Result: SELECT * FROM users WHERE username = 'admin'; DROP TABLE users; --'

# GOOD: Parameterized queries
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (user_input,))
```

**Never concatenate user input into SQL!**

## 20. Assuming Database Triggers Will Always Work

```sql
-- Problem: Triggers don't fire for bulk operations in some databases
CREATE TRIGGER update_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
SET NEW.updated_at = NOW();

-- Bulk operations might bypass trigger
LOAD DATA INFILE 'users.csv' INTO TABLE users;  -- Trigger might not fire!
```

**Best practice:**
- Don't rely solely on triggers
- Validate in application too
- Test bulk operations specifically
