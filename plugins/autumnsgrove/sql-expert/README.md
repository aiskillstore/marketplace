# SQL Expert Skill

Expert SQL query writing, optimization, and database schema design with support for PostgreSQL, MySQL, SQLite, and SQL Server.

## Overview

Expert guidance for writing, optimizing, and managing SQL databases. This skill covers complex queries with JOINs and window functions, query optimization using EXPLAIN plans, database schema design with proper normalization, index creation for performance, safe migrations, and SQL debugging.

## Installation

Install database drivers for your target database:

```bash
# PostgreSQL
pip install psycopg2-binary sqlalchemy

# MySQL/MariaDB
pip install mysql-connector-python sqlalchemy

# SQLite (built into Python)
pip install sqlite3

# SQL Server
pip install pyodbc sqlalchemy
```

## What's Included

### SKILL.md
Comprehensive guide covering SQL query writing, optimization techniques, schema design with normalization, index strategies, migration patterns, advanced patterns (CTEs, window functions, recursive queries), best practices, and common pitfalls.

### scripts/
- `sql_helper.py` - Utility functions for:
  - Query building and parameterization
  - Schema introspection
  - Index analysis and recommendations
  - Migration helpers

### examples/
- `complex_queries.sql` - Advanced query patterns with CTEs, window functions, subqueries
- `schema_examples.sql` - Complete schema design examples for various use cases
- `migrations.sql` - Safe migration patterns and zero-downtime techniques

### references/
- `query-optimization.md` - Comprehensive optimization techniques and EXPLAIN analysis
- `indexes-performance.md` - Detailed index strategies, maintenance, monitoring
- `advanced-patterns.md` - UPSERT, bulk operations, pivot tables, JSON operations, recursive queries
- `best-practices.md` - Complete SQL best practices guide
- `common-pitfalls.md` - Common mistakes and how to avoid them

## Quick Start

### Basic SELECT with JOINs

```sql
-- Simple SELECT with filtering
SELECT
    users.name,
    orders.order_date,
    orders.total_amount
FROM
    users
INNER JOIN
    orders ON users.id = orders.user_id
WHERE
    orders.status = 'completed'
ORDER BY
    orders.order_date DESC
LIMIT 10;

-- LEFT JOIN (include all users, even without orders)
SELECT
    users.name,
    COUNT(orders.id) as order_count,
    COALESCE(SUM(orders.total_amount), 0) as total_spent
FROM
    users
LEFT JOIN
    orders ON users.id = orders.user_id
GROUP BY
    users.id, users.name;
```

### Common Table Expressions (CTEs)

```sql
WITH high_value_customers AS (
    SELECT
        user_id,
        SUM(total_amount) as lifetime_value
    FROM orders
    GROUP BY user_id
    HAVING SUM(total_amount) > 1000
)
SELECT
    users.name,
    users.email,
    hvc.lifetime_value
FROM users
INNER JOIN high_value_customers hvc ON users.id = hvc.user_id;
```

### Window Functions

```sql
-- Ranking within groups
SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank
FROM
    employees;

-- Running totals
SELECT
    order_date,
    total_amount,
    SUM(total_amount) OVER (ORDER BY order_date) as running_total
FROM
    orders;
```

See `examples/complex_queries.sql` for more advanced patterns.

## Core Capabilities

### Query Writing
- Complex SQL queries with JOINs, subqueries, CTEs, and window functions
- Aggregations with GROUP BY and HAVING
- Set operations (UNION, INTERSECT, EXCEPT)
- Recursive CTEs for hierarchical data
- JSON/JSONB operations (PostgreSQL)

### Query Optimization
- EXPLAIN plan analysis
- Index recommendations
- Query rewriting for performance
- Execution plan understanding
- Performance bottleneck identification

### Schema Design
- Database normalization (1NF, 2NF, 3NF, BCNF)
- Entity-relationship modeling
- Foreign key constraints
- Check constraints and validation
- Default values and triggers

### Index Management
- Single column and composite indexes
- Unique indexes
- Partial indexes (PostgreSQL)
- Index maintenance and monitoring
- When to create or avoid indexes

### Database Migrations
- Safe schema changes
- Zero-downtime migrations
- Rollback strategies
- Data backfilling
- Version control for schemas

### Debugging
- SQL error interpretation
- Query troubleshooting
- Data integrity issues
- Performance debugging
- Constraint violation resolution

## Query Optimization

### Using EXPLAIN

```sql
-- Analyze query performance
EXPLAIN ANALYZE
SELECT
    users.name,
    COUNT(orders.id) as order_count
FROM users
LEFT JOIN orders ON users.id = orders.user_id
GROUP BY users.id, users.name;

-- Look for:
-- - Seq Scan (bad) vs Index Scan (good)
-- - High cost numbers
-- - Large row counts being processed
```

### Quick Optimization Tips

```sql
-- BAD: Function on indexed column
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- GOOD: Keep indexed column clean
SELECT * FROM users WHERE email = LOWER('user@example.com');

-- BAD: SELECT *
SELECT * FROM large_table WHERE id = 123;

-- GOOD: Select only needed columns
SELECT id, name, email FROM large_table WHERE id = 123;
```

For comprehensive optimization techniques, see `references/query-optimization.md`.

## Schema Design

### Normalization Example

```sql
-- GOOD: Separate table for order items (1NF)
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    order_date DATE
);

CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_name VARCHAR(100),
    quantity INT,
    price DECIMAL(10, 2)
);
```

### Many-to-Many Relationship

```sql
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100)
);

-- Junction table
CREATE TABLE enrollments (
    enrollment_id INT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrollment_date DATE,
    grade CHAR(2),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    UNIQUE (student_id, course_id)
);
```

See `examples/schema_examples.sql` for more patterns.

## Indexes and Performance

### Creating Indexes

```sql
-- Single column index
CREATE INDEX idx_users_email ON users(email);

-- Composite index (order matters!)
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);

-- Unique index
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Partial index (PostgreSQL)
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';
```

### Index Guidelines

**When to create indexes:**
- ✅ Columns used in WHERE clauses
- ✅ Columns used in JOIN conditions
- ✅ Columns used in ORDER BY
- ✅ Foreign key columns

**When NOT to create indexes:**
- ❌ Small tables (< 1000 rows)
- ❌ Columns with low selectivity (boolean fields)
- ❌ Columns frequently updated

For detailed index strategies, see `references/indexes-performance.md`.

## Migrations

### Safe Migration Pattern

```sql
-- Step 1: Add column as nullable
ALTER TABLE users ADD COLUMN status VARCHAR(20);

-- Step 2: Populate existing rows
UPDATE users SET status = 'active' WHERE status IS NULL;

-- Step 3: Make it NOT NULL
ALTER TABLE users ALTER COLUMN status SET NOT NULL;

-- Step 4: Add default for new rows
ALTER TABLE users ALTER COLUMN status SET DEFAULT 'active';

-- Rollback plan
ALTER TABLE users DROP COLUMN status;
```

See `examples/migrations.sql` for more migration patterns.

## Advanced Patterns

### UPSERT (Insert or Update)

```sql
-- PostgreSQL
INSERT INTO users (user_id, name, email, updated_at)
VALUES (1, 'John Doe', 'john@example.com', NOW())
ON CONFLICT (user_id)
DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    updated_at = NOW();

-- MySQL
INSERT INTO users (user_id, name, email, updated_at)
VALUES (1, 'John Doe', 'john@example.com', NOW())
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    email = VALUES(email),
    updated_at = NOW();
```

### Recursive CTEs

```sql
-- Hierarchical data traversal
WITH RECURSIVE employee_hierarchy AS (
    -- Anchor: top-level employees
    SELECT id, name, manager_id, 1 as level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive: employees reporting to previous level
    SELECT e.id, e.name, e.manager_id, eh.level + 1
    FROM employees e
    INNER JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM employee_hierarchy ORDER BY level, name;
```

For more advanced patterns, see `references/advanced-patterns.md`.

## Best Practices

### Critical Guidelines

1. **Always use parameterized queries** to prevent SQL injection
2. **Use transactions for related operations** to ensure atomicity
3. **Add appropriate constraints** (PRIMARY KEY, FOREIGN KEY, NOT NULL, CHECK)
4. **Include timestamps** (created_at, updated_at) on tables
5. **Use meaningful names** for tables and columns
6. **Avoid SELECT *** - specify only needed columns
7. **Index foreign keys** for join performance
8. **Use VARCHAR instead of CHAR** for variable-length strings
9. **Handle NULL values properly** with IS NULL / IS NOT NULL
10. **Use appropriate data types** (DECIMAL for money, not FLOAT)

For comprehensive best practices, see `references/best-practices.md`.

## Common Pitfalls

1. **N+1 Query Problem** - Use JOINs instead of loops with queries
2. **Not using LIMIT** for exploratory queries on large tables
3. **Implicit type conversions** preventing index usage
4. **Using COUNT(\*) when EXISTS is sufficient**
5. **Not handling NULLs properly** (NULL = NULL is always NULL, not TRUE)
6. **Using SELECT DISTINCT** as a band-aid instead of fixing the query
7. **Forgetting transactions** for related operations
8. **Using functions on indexed columns** preventing index usage

For a complete list of pitfalls and solutions, see `references/common-pitfalls.md`.

## Supported Database Systems

### PostgreSQL
**Best for**: Complex queries, JSON data, advanced features, ACID compliance

### MySQL/MariaDB
**Best for**: Web applications, WordPress, high-read workloads

### SQLite
**Best for**: Local development, embedded databases, testing

### SQL Server
**Best for**: Enterprise applications, Windows environments

## Workflow

When working with SQL databases:

1. **Understand requirements** - What data needs to be queried or stored?
2. **Design schema** - Apply normalization, choose appropriate data types
3. **Create indexes** - Index foreign keys and frequently queried columns
4. **Write queries** - Start simple, add complexity as needed
5. **Optimize** - Use EXPLAIN to identify bottlenecks
6. **Test** - Verify with sample data and edge cases
7. **Document** - Add comments for complex queries

For migrations:
1. **Plan changes** - Identify affected tables and dependencies
2. **Write migration** - Create both up and down migrations
3. **Test on copy** - Test on development database first
4. **Backup** - Always backup before running migrations
5. **Execute** - Run migrations during low-traffic periods
6. **Verify** - Check data integrity after migration

## Documentation

See `SKILL.md` for comprehensive documentation, detailed workflows, and advanced techniques.

## Requirements

- Python 3.7+ (for helper scripts)
- Database-specific drivers (psycopg2, mysql-connector-python, pyodbc)
- SQLAlchemy (optional, for ORM functionality)
- Access to a database server (PostgreSQL, MySQL, SQLite, or SQL Server)
