---
name: database-schema-designer
description: Use this skill when designing database schemas for relational (SQL) or document (NoSQL) databases. Provides normalization guidelines, indexing strategies, migration patterns, and performance optimization techniques. Ensures scalable, maintainable, and performant data models.
version: 1.0.0
author: AI Agent Hub
tags: [database, schema-design, sql, nosql, performance, migrations]
---

# Database Schema Designer

## Overview

This skill provides comprehensive guidance for designing robust, scalable database schemas for both SQL and NoSQL databases. Whether building from scratch or evolving existing schemas, this framework ensures data integrity, performance, and maintainability.

**When to use this skill:**
- Designing new database schemas
- Refactoring or migrating existing schemas
- Optimizing database performance
- Choosing between SQL and NoSQL approaches
- Creating database migrations
- Establishing indexing strategies
- Modeling complex relationships
- Planning data archival and partitioning

## Database Design Philosophy

### Core Principles

**1. Model the Domain, Not the UI**
- Schema reflects business entities and relationships
- Don't let UI requirements drive data structure
- Separate presentation concerns from data model

**2. Optimize for Reads or Writes (Not Both)**
- OLTP (transactional): Normalized, optimized for writes
- OLAP (analytical): Denormalized, optimized for reads
- Choose based on access patterns

**3. Plan for Scale From Day One**
- Indexing strategy
- Partitioning approach
- Caching layer
- Read replicas

**4. Data Integrity Over Performance**
- Use constraints, foreign keys, validation
- Performance issues can be optimized later
- Data corruption is costly to fix

---

## SQL Database Design

### Normalization

Database normalization reduces redundancy and ensures data integrity.

#### 1st Normal Form (1NF)
**Rule**: Each column contains atomic (indivisible) values, no repeating groups.

```sql
-- ❌ Violates 1NF (multiple values in one column)
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT,
  product_ids VARCHAR(255)  -- '101,102,103' (bad!)
);

-- ✅ Follows 1NF
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT
);

CREATE TABLE order_items (
  id INT PRIMARY KEY,
  order_id INT,
  product_id INT,
  FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

#### 2nd Normal Form (2NF)
**Rule**: Must be in 1NF + all non-key columns depend on the entire primary key.

```sql
-- ❌ Violates 2NF (customer_name depends only on customer_id, not full key)
CREATE TABLE order_items (
  order_id INT,
  product_id INT,
  customer_id INT,
  customer_name VARCHAR(100),  -- Depends on customer_id only
  quantity INT,
  PRIMARY KEY (order_id, product_id)
);

-- ✅ Follows 2NF (customer data in separate table)
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE order_items (
  order_id INT,
  product_id INT,
  quantity INT,
  PRIMARY KEY (order_id, product_id)
);

CREATE TABLE customers (
  id INT PRIMARY KEY,
  name VARCHAR(100)
);
```

#### 3rd Normal Form (3NF)
**Rule**: Must be in 2NF + no transitive dependencies (non-key columns depend only on primary key).

```sql
-- ❌ Violates 3NF (country depends on postal_code, not on customer_id)
CREATE TABLE customers (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  postal_code VARCHAR(10),
  country VARCHAR(50)  -- Depends on postal_code, not id
);

-- ✅ Follows 3NF
CREATE TABLE customers (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  postal_code VARCHAR(10),
  FOREIGN KEY (postal_code) REFERENCES postal_codes(code)
);

CREATE TABLE postal_codes (
  code VARCHAR(10) PRIMARY KEY,
  country VARCHAR(50)
);
```

#### Denormalization (When to Break Rules)

Sometimes denormalization improves performance for read-heavy applications.

```sql
-- Denormalized for performance (caching derived data)
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT,
  total_amount DECIMAL(10, 2),  -- Calculated from order_items
  item_count INT,               -- Calculated from order_items
  created_at TIMESTAMP
);

-- Trigger or application code keeps denormalized data in sync
```

**When to denormalize:**
- Read-heavy applications (reporting, analytics)
- Frequently joined tables causing performance issues
- Pre-calculated aggregates (counts, sums, averages)
- Caching derived data to avoid complex joins

---

### Data Types

Choose appropriate data types for efficiency and accuracy.

#### String Types

```sql
-- Fixed-length (use for predictable lengths)
CHAR(10)      -- ISO date: '2025-10-31'
CHAR(2)       -- State code: 'CA'

-- Variable-length (use for variable lengths)
VARCHAR(255)  -- Email, name, short text
TEXT          -- Long text (articles, descriptions)

-- ✅ Good: Appropriate sizes
email VARCHAR(255)
phone_number VARCHAR(20)
postal_code VARCHAR(10)

-- ❌ Bad: Wasteful or too small
email VARCHAR(500)       -- Too large
description VARCHAR(50)  -- Too small for long text
```

#### Numeric Types

```sql
-- Integer types
TINYINT    -- -128 to 127 (age, status codes)
SMALLINT   -- -32,768 to 32,767 (quantities)
INT        -- -2.1B to 2.1B (IDs, counts)
BIGINT     -- Large numbers (timestamps, large IDs)

-- Decimal types
DECIMAL(10, 2)  -- Exact precision (money: $99,999,999.99)
FLOAT           -- Approximate (scientific calculations)
DOUBLE          -- Higher precision approximations

-- ✅ Use DECIMAL for money
CREATE TABLE products (
  id INT PRIMARY KEY,
  price DECIMAL(10, 2)  -- Exact precision
);

-- ❌ Don't use FLOAT for money
price FLOAT  -- Rounding errors!
```

#### Date/Time Types

```sql
DATE       -- Date only: 2025-10-31
TIME       -- Time only: 14:30:00
DATETIME   -- Date + time: 2025-10-31 14:30:00
TIMESTAMP  -- Unix timestamp (auto-converts timezone)

-- ✅ Always store in UTC
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

#### Boolean

```sql
-- PostgreSQL
is_active BOOLEAN DEFAULT TRUE

-- MySQL
is_active TINYINT(1) DEFAULT 1
```

---

### Indexing Strategies

Indexes speed up reads but slow down writes. Use strategically.

#### When to Create Indexes

```sql
-- ✅ Index foreign keys
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- ✅ Index frequently queried columns
CREATE INDEX idx_users_email ON users(email);

-- ✅ Index columns used in WHERE, ORDER BY, GROUP BY
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- ✅ Composite index for multi-column queries
CREATE INDEX idx_orders_customer_status ON orders(customer_id, status);
```

#### Index Types

**B-Tree Index (Default)**
```sql
-- Best for equality and range queries
CREATE INDEX idx_products_price ON products(price);

-- Queries that benefit:
SELECT * FROM products WHERE price > 100;
SELECT * FROM products WHERE price BETWEEN 50 AND 150;
```

**Hash Index**
```sql
-- Best for exact matches only (not ranges)
CREATE INDEX idx_users_email USING HASH ON users(email);

-- Queries that benefit:
SELECT * FROM users WHERE email = 'user@example.com';
```

**Full-Text Index**
```sql
-- Best for text search
CREATE FULLTEXT INDEX idx_articles_content ON articles(title, content);

-- Queries that benefit:
SELECT * FROM articles WHERE MATCH(title, content) AGAINST('database design');
```

**Partial Index (PostgreSQL)**
```sql
-- Index only specific rows
CREATE INDEX idx_active_users ON users(email) WHERE is_active = TRUE;
```

#### Composite Indexes (Column Order Matters)

```sql
-- ✅ Good: Index supports both queries
CREATE INDEX idx_orders_customer_status ON orders(customer_id, status);

-- Query 1: Uses index efficiently
SELECT * FROM orders WHERE customer_id = 123 AND status = 'pending';

-- Query 2: Uses index (customer_id only)
SELECT * FROM orders WHERE customer_id = 123;

-- ❌ Query 3: Doesn't use index (status is second column)
SELECT * FROM orders WHERE status = 'pending';
```

**Rule of Thumb**: Put most selective column first, or most frequently queried alone.

---

### Constraints

Use constraints to enforce data integrity at the database level.

#### Primary Key

```sql
-- Auto-incrementing integer
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL
);

-- UUID (better for distributed systems)
CREATE TABLE users (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  email VARCHAR(255) UNIQUE NOT NULL
);
```

#### Foreign Key

```sql
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
    ON DELETE CASCADE      -- Delete orders when customer deleted
    ON UPDATE CASCADE      -- Update orders when customer ID changes
);

-- Alternatives:
ON DELETE RESTRICT   -- Prevent deletion if referenced
ON DELETE SET NULL   -- Set to NULL when parent deleted
ON DELETE NO ACTION  -- Same as RESTRICT
```

#### Unique Constraint

```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(50) UNIQUE NOT NULL
);

-- Composite unique constraint
CREATE TABLE enrollments (
  student_id INT,
  course_id INT,
  UNIQUE (student_id, course_id)  -- Prevent duplicate enrollments
);
```

#### Check Constraint

```sql
CREATE TABLE products (
  id INT PRIMARY KEY,
  price DECIMAL(10, 2) CHECK (price >= 0),
  stock INT CHECK (stock >= 0),
  discount_percent INT CHECK (discount_percent BETWEEN 0 AND 100)
);
```

#### Not Null Constraint

```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  email VARCHAR(255) NOT NULL,
  name VARCHAR(100) NOT NULL,
  bio TEXT  -- Nullable (optional)
);
```

---

### Common Schema Patterns

#### One-to-Many (Orders → Order Items)

```sql
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
  id INT PRIMARY KEY,
  order_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL,
  price DECIMAL(10, 2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);
```

#### Many-to-Many (Students ↔ Courses)

```sql
CREATE TABLE students (
  id INT PRIMARY KEY,
  name VARCHAR(100) NOT NULL
);

CREATE TABLE courses (
  id INT PRIMARY KEY,
  title VARCHAR(200) NOT NULL
);

-- Junction table (also called join table, linking table)
CREATE TABLE enrollments (
  student_id INT,
  course_id INT,
  enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  grade VARCHAR(2),
  PRIMARY KEY (student_id, course_id),
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
```

#### Self-Referencing (Employees → Manager)

```sql
CREATE TABLE employees (
  id INT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  manager_id INT,
  FOREIGN KEY (manager_id) REFERENCES employees(id)
);
```

#### Polymorphic Relationships (Comments on Posts/Photos)

```sql
-- Approach 1: Separate foreign keys with CHECK constraint
CREATE TABLE comments (
  id INT PRIMARY KEY,
  content TEXT NOT NULL,
  post_id INT,
  photo_id INT,
  CHECK (
    (post_id IS NOT NULL AND photo_id IS NULL) OR
    (post_id IS NULL AND photo_id IS NOT NULL)
  ),
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE
);

-- Approach 2: commentable_type + commentable_id (Rails-style)
CREATE TABLE comments (
  id INT PRIMARY KEY,
  content TEXT NOT NULL,
  commentable_type VARCHAR(50) NOT NULL,  -- 'Post' or 'Photo'
  commentable_id INT NOT NULL
);
-- Note: No foreign key constraint possible (less data integrity)
```

---

## NoSQL Database Design

### Document Databases (MongoDB)

**When to use**:
- Schema flexibility needed
- Rapid iteration
- Hierarchical data
- Read-heavy workloads

#### Embedding vs Referencing

**Embedding (Denormalization)**
```json
{
  "_id": "order_123",
  "customer": {
    "id": "cust_456",
    "name": "Jane Smith",
    "email": "jane@example.com"
  },
  "items": [
    { "product_id": "prod_789", "quantity": 2, "price": 29.99 },
    { "product_id": "prod_101", "quantity": 1, "price": 49.99 }
  ],
  "total": 109.97,
  "created_at": "2025-10-31T10:30:00Z"
}
```

**When to embed:**
- Data accessed together frequently
- 1:few relationships (few items)
- Child documents don't need independent existence

**Referencing (Normalization)**
```json
{
  "_id": "order_123",
  "customer_id": "cust_456",
  "item_ids": ["item_1", "item_2"],
  "total": 109.97,
  "created_at": "2025-10-31T10:30:00Z"
}
```

**When to reference:**
- Data accessed independently
- 1:many relationships (many items)
- Large documents (approaching 16MB limit)
- Frequently updated data

#### Indexing in MongoDB

```javascript
// Create index
db.users.createIndex({ email: 1 }, { unique: true });

// Composite index
db.orders.createIndex({ customer_id: 1, created_at: -1 });

// Text index for search
db.articles.createIndex({ title: "text", content: "text" });

// Geospatial index
db.stores.createIndex({ location: "2dsphere" });
```

---

## Database Migrations

### Migration Best Practices

**1. Always Reversible**
```sql
-- Up migration
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Down migration
ALTER TABLE users DROP COLUMN phone;
```

**2. Backward Compatible**
```sql
-- ✅ Good: Add nullable column
ALTER TABLE users ADD COLUMN middle_name VARCHAR(50);

-- ❌ Bad: Add required column (breaks existing code)
ALTER TABLE users ADD COLUMN middle_name VARCHAR(50) NOT NULL;

-- ✅ Better: Add nullable, then populate, then make required
-- Migration 1: Add column
ALTER TABLE users ADD COLUMN middle_name VARCHAR(50);

-- Migration 2: Populate with default
UPDATE users SET middle_name = '' WHERE middle_name IS NULL;

-- Migration 3: Make required
ALTER TABLE users MODIFY COLUMN middle_name VARCHAR(50) NOT NULL;
```

**3. Data Migrations Separate from Schema Changes**
```sql
-- Migration 1: Schema change
ALTER TABLE orders ADD COLUMN status VARCHAR(20) DEFAULT 'pending';

-- Migration 2: Data migration
UPDATE orders SET status = 'completed' WHERE completed_at IS NOT NULL;
```

**4. Test Migrations on Production Copy**
- Test on staging with production data snapshot
- Measure migration duration
- Plan for downtime (if needed)

---

### Zero-Downtime Migrations

**Adding a Column:**
```sql
-- Step 1: Add nullable column
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Step 2: Deploy code that writes to new column
-- (Application now writes to both old and new column)

-- Step 3: Backfill existing rows
UPDATE users SET phone = old_phone WHERE phone IS NULL;

-- Step 4: Make column required (if needed)
ALTER TABLE users MODIFY COLUMN phone VARCHAR(20) NOT NULL;
```

**Renaming a Column:**
```sql
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);

-- Step 2: Copy data
UPDATE users SET email_address = email;

-- Step 3: Deploy code that reads from new column

-- Step 4: Deploy code that writes to new column

-- Step 5: Drop old column
ALTER TABLE users DROP COLUMN email;
```

---

## Performance Optimization

### Query Optimization

**Use EXPLAIN to analyze queries:**
```sql
EXPLAIN SELECT * FROM orders WHERE customer_id = 123 AND status = 'pending';
```

**Look for:**
- **Type**: ALL (table scan - bad), index, ref, eq_ref
- **Possible keys**: Indexes available
- **Key**: Index actually used
- **Rows**: Estimated rows scanned

**Optimization techniques:**
- Add indexes on WHERE, ORDER BY, GROUP BY columns
- Avoid SELECT * (fetch only needed columns)
- Use LIMIT for pagination
- Denormalize for read-heavy queries

### N+1 Query Problem

```python
# ❌ Bad: N+1 queries (1 query for orders + N queries for customers)
orders = db.query("SELECT * FROM orders")
for order in orders:
    customer = db.query(f"SELECT * FROM customers WHERE id = {order.customer_id}")
    print(f"{customer.name} ordered {order.total}")

# ✅ Good: Single query with JOIN
results = db.query("""
    SELECT orders.*, customers.name
    FROM orders
    JOIN customers ON orders.customer_id = customers.id
""")
for result in results:
    print(f"{result.name} ordered {result.total}")
```

---

## Integration with Agents

### Backend System Architect
- Uses this skill when designing data models
- Applies normalization and indexing strategies
- Plans for scalability and performance

### Code Quality Reviewer
- Validates schema design follows best practices
- Checks for missing indexes and constraints
- Reviews migration safety

### AI/ML Engineer
- Uses denormalization patterns for analytics
- Designs data pipelines and aggregation tables

---

## Quick Start Checklist

When designing a new schema:

- [ ] Identify entities and relationships
- [ ] Choose SQL or NoSQL based on requirements
- [ ] Normalize to 3NF (SQL) or decide embed/reference (NoSQL)
- [ ] Define primary keys (INT auto-increment or UUID)
- [ ] Add foreign key constraints
- [ ] Choose appropriate data types
- [ ] Add unique constraints where needed
- [ ] Plan indexing strategy (foreign keys, WHERE columns)
- [ ] Add NOT NULL constraints for required fields
- [ ] Create CHECK constraints for validation
- [ ] Plan for soft deletes (deleted_at column) if needed
- [ ] Add timestamps (created_at, updated_at)
- [ ] Design migration scripts (up and down)
- [ ] Test migrations on staging

---

**Skill Version**: 1.0.0
**Last Updated**: 2025-10-31
**Maintained by**: AI Agent Hub Team
