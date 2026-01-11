# SQL Best Practices

## 1. Always Use Parameterized Queries

Prevent SQL injection by using parameterized queries:

```python
# BAD: SQL injection vulnerable
query = f"SELECT * FROM users WHERE email = '{user_input}'"

# GOOD: Parameterized query
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (user_input,))
```

**Why it matters:**
- Prevents SQL injection attacks
- Handles special characters correctly
- Improves query plan caching

## 2. Use Transactions for Related Operations

```sql
BEGIN TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;

COMMIT;
-- Or ROLLBACK if something goes wrong
```

**When to use transactions:**
- Multiple related DML statements
- Financial operations
- Data consistency is critical
- Need atomicity (all-or-nothing execution)

## 3. Add Appropriate Constraints

```sql
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_amount DECIMAL(10, 2) CHECK (total_amount >= 0),
    status VARCHAR(20) CHECK (status IN ('pending', 'completed', 'cancelled')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**Essential constraints:**
- `PRIMARY KEY`: Uniquely identifies rows
- `FOREIGN KEY`: Maintains referential integrity
- `NOT NULL`: Prevents missing data
- `UNIQUE`: Prevents duplicates
- `CHECK`: Validates data values
- `DEFAULT`: Provides sensible defaults

## 4. Use VARCHAR Instead of CHAR

```sql
-- BAD: Wastes space
CREATE TABLE users (name CHAR(100));

-- GOOD: Only uses needed space
CREATE TABLE users (name VARCHAR(100));
```

**Why VARCHAR:**
- Only stores the actual string length
- More efficient for variable-length data
- CHAR is only appropriate for fixed-length codes (like state abbreviations)

## 5. Include Timestamps

```sql
CREATE TABLE posts (
    post_id INT PRIMARY KEY,
    title VARCHAR(200),
    content TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Benefits:**
- Track when records were created
- Monitor when records were modified
- Enable time-based queries and analytics
- Support audit trails

## 6. Use Meaningful Names

```sql
-- BAD
CREATE TABLE t1 (id INT, n VARCHAR(100));

-- GOOD
CREATE TABLE customers (customer_id INT, customer_name VARCHAR(100));
```

**Naming conventions:**
- Tables: Plural nouns (users, orders, products)
- Columns: Descriptive names (email_address, not e)
- Primary keys: table_name_id (user_id, order_id)
- Foreign keys: referenced_table_id (user_id referencing users.user_id)
- Indexes: idx_table_column (idx_users_email)

## 7. Avoid SELECT *

```sql
-- BAD: Retrieves unnecessary data
SELECT * FROM users WHERE user_id = 123;

-- GOOD: Select only needed columns
SELECT user_id, name, email FROM users WHERE user_id = 123;
```

**Why avoid SELECT *:**
- Reduces network transfer
- Improves query performance
- Makes code more maintainable
- Prevents issues when schema changes

## 8. Use Explicit JOIN Syntax

```sql
-- BAD: Implicit joins (old style)
SELECT u.name, o.total
FROM users u, orders o
WHERE u.id = o.user_id;

-- GOOD: Explicit JOIN syntax
SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```

**Benefits:**
- Clearer intent
- Easier to spot missing join conditions
- Separates join logic from filter logic
- Industry standard

## 9. Handle NULL Values Properly

```sql
-- BAD: This doesn't work as expected
SELECT * FROM users WHERE deleted_at = NULL;

-- GOOD: Use IS NULL / IS NOT NULL
SELECT * FROM users WHERE deleted_at IS NULL;

-- GOOD: Use COALESCE for defaults
SELECT name, COALESCE(phone, 'No phone') as phone FROM users;
```

**NULL handling tips:**
- Use `IS NULL` and `IS NOT NULL` for comparisons
- Use `COALESCE()` to provide default values
- Consider `NOT NULL` constraints when appropriate
- Remember: NULL != NULL (it's unknown)

## 10. Index Foreign Keys

```sql
-- Always index foreign key columns
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
```

**Why index foreign keys:**
- Speeds up joins
- Improves referential integrity checks
- Essential for delete cascades
- Often used in WHERE clauses

## 11. Use Appropriate Data Types

```sql
-- BAD: Using wrong data types
CREATE TABLE events (
    event_date VARCHAR(50),  -- Should be DATE or TIMESTAMP
    price VARCHAR(20),       -- Should be DECIMAL
    is_active VARCHAR(5)     -- Should be BOOLEAN
);

-- GOOD: Use appropriate types
CREATE TABLE events (
    event_date TIMESTAMP NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT true
);
```

**Type selection guidelines:**
- Dates/times: DATE, TIMESTAMP, TIME
- Money: DECIMAL (never FLOAT for currency)
- Yes/No: BOOLEAN
- Whole numbers: INT, BIGINT
- Text: VARCHAR (with reasonable limits)

## 12. Normalize to Third Normal Form (Usually)

Follow normalization principles:

1. **First Normal Form (1NF)**: No repeating groups
2. **Second Normal Form (2NF)**: No partial dependencies
3. **Third Normal Form (3NF)**: No transitive dependencies

**When to denormalize:**
- Read-heavy workloads
- Reporting databases
- When joins become too expensive
- After measuring actual performance issues

## 13. Add Appropriate Indexes

```sql
-- Index columns used in WHERE, JOIN, ORDER BY
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_products_category ON products(category_id);
```

**Indexing guidelines:**
- Start with foreign keys
- Add indexes for common WHERE clauses
- Include ORDER BY columns
- Monitor query performance and add as needed
- Don't over-index (slows writes)

## 14. Use Database-Level Defaults

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT false
);
```

**Benefits:**
- Ensures consistent defaults
- Reduces application code complexity
- Works across all applications accessing the database
- Self-documenting

## 15. Comment Complex Schema Elements

```sql
COMMENT ON TABLE users IS 'Application user accounts';
COMMENT ON COLUMN users.verified_at IS 'Email verification timestamp, NULL if unverified';

-- Or inline comments for complex queries
SELECT
    u.name,
    COUNT(o.id) as order_count  -- Total lifetime orders
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'  -- New users only
GROUP BY u.id, u.name;
```

## 16. Use Transactions Appropriately

```sql
-- Good: Multiple related operations
BEGIN;
INSERT INTO orders (user_id, total) VALUES (1, 100.00);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (LAST_INSERT_ID(), 5, 2);
UPDATE products SET stock = stock - 2 WHERE product_id = 5;
COMMIT;

-- Bad: Single operation doesn't need explicit transaction
BEGIN;
INSERT INTO logs (message) VALUES ('Test');
COMMIT;
```

## 17. Validate Data at Database Level

```sql
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) CHECK (price > 0),
    stock INT CHECK (stock >= 0),
    email VARCHAR(255) CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);
```

**Defense in depth:**
- Validate in application AND database
- Database validation catches bugs
- Ensures data integrity even with multiple applications

## 18. Plan for Soft Deletes When Appropriate

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    deleted_at TIMESTAMP NULL,
    -- Other columns...
);

-- Query only active users
SELECT * FROM users WHERE deleted_at IS NULL;

-- Index for performance
CREATE INDEX idx_users_deleted_at ON users(deleted_at);
```

**When to use soft deletes:**
- Need to maintain referential integrity
- Regulatory compliance requirements
- Audit trail needed
- Accidental deletes are common
