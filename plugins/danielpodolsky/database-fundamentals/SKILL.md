---
name: Database Fundamentals
description: Auto-invoke when reviewing schema design, database queries, ORM usage, or migrations. Enforces normalization, indexing awareness, query optimization, and migration safety.
---

# Database Fundamentals Review

> "Your database is the foundation. Build it wrong, and everything above it will crack."

## When to Apply

Activate this skill when reviewing:
- Schema design and migrations
- SQL/NoSQL queries
- ORM model definitions
- Data relationships
- Index creation
- Query performance

---

## Review Checklist

### Schema Design

- [ ] **Normalization**: Is data normalized appropriately (no excessive duplication)?
- [ ] **Denormalization justified**: If denormalized, is there a performance reason?
- [ ] **Primary keys**: Does every table have a clear primary key?
- [ ] **Foreign keys**: Are relationships enforced at the database level?
- [ ] **Data types**: Are appropriate types used (not everything TEXT)?

### Indexes

- [ ] **Query-based**: Are indexes created for frequently queried columns?
- [ ] **Composite indexes**: Are multi-column queries covered?
- [ ] **Not over-indexed**: Are there unnecessary indexes slowing writes?
- [ ] **Unique constraints**: Are unique fields enforced at DB level?

### Queries

- [ ] **No N+1**: Are related records fetched in bulk?
- [ ] **Select specific fields**: Are we avoiding `SELECT *`?
- [ ] **Pagination**: Do list queries limit results?
- [ ] **Parameterized**: Are all queries parameterized (no string concatenation)?

### Migrations

- [ ] **Reversible**: Can this migration be rolled back?
- [ ] **No data loss**: Will existing data survive the migration?
- [ ] **Tested**: Has this been tested against production-like data?
- [ ] **Incremental**: Are large changes broken into smaller migrations?

---

## Common Mistakes (Anti-Patterns)

### 1. The N+1 Query Problem
```
❌ // 1 query for users + N queries for posts
   const users = await User.findAll();
   for (const user of users) {
     user.posts = await Post.findAll({ where: { userId: user.id } });
   }

✅ // 1 query with JOIN
   const users = await User.findAll({
     include: [{ model: Post }]
   });

   // Or 2 queries with IN clause
   const users = await User.findAll();
   const userIds = users.map(u => u.id);
   const posts = await Post.findAll({ where: { userId: userIds } });
```

### 2. Missing Indexes
```
❌ // Queried frequently, but no index
   SELECT * FROM orders WHERE user_id = ?
   SELECT * FROM products WHERE category = ? AND status = 'active'

✅ CREATE INDEX idx_orders_user_id ON orders(user_id);
   CREATE INDEX idx_products_category_status ON products(category, status);
```

### 3. SELECT * Everywhere
```
❌ SELECT * FROM users; // Returns 50 columns

✅ SELECT id, name, email FROM users; // Only what's needed
```

### 4. String Concatenation (SQL Injection)
```
❌ db.query(`SELECT * FROM users WHERE email = '${email}'`);

✅ db.query('SELECT * FROM users WHERE email = ?', [email]);
```

### 5. Destructive Migrations
```
❌ -- Can't be rolled back
   DROP TABLE users;
   ALTER TABLE orders DROP COLUMN status;

✅ -- Add new, migrate data, then drop old (in separate migrations)
   -- Migration 1: Add new column
   ALTER TABLE orders ADD COLUMN status_new VARCHAR(20);
   -- Migration 2: Copy data
   UPDATE orders SET status_new = status;
   -- Migration 3: Drop old (after verification)
   ALTER TABLE orders DROP COLUMN status;
```

---

## Socratic Questions

Ask the junior these questions instead of giving answers:

1. **Schema**: "Why did you choose this data type?"
2. **Relationships**: "What happens if this related record is deleted?"
3. **Indexes**: "Which columns are queried together? Are they indexed?"
4. **N+1**: "How many queries does this operation execute?"
5. **Migration**: "What happens if we need to roll this back?"

---

## Normalization Quick Reference

| Form | Rule | Example Issue |
|------|------|---------------|
| 1NF | No repeating groups | `tags: "js,react,node"` should be separate table |
| 2NF | No partial dependencies | Order item price duplicated from products |
| 3NF | No transitive dependencies | Storing city AND zip code (zip determines city) |

### When to Denormalize

- Read-heavy workloads with rare writes
- Calculated aggregates (e.g., order totals)
- Caching frequently accessed derived data

---

## Index Strategy

```sql
-- Single column (most common)
CREATE INDEX idx_users_email ON users(email);

-- Composite (for multi-column queries)
-- Order matters! Most selective first
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Partial (for filtered queries)
CREATE INDEX idx_active_users ON users(email) WHERE active = true;

-- Unique (enforces constraint)
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);
```

### Index Rules of Thumb

1. Index columns in WHERE clauses
2. Index columns in JOIN conditions
3. Index columns in ORDER BY (if used with WHERE)
4. Don't over-index write-heavy tables
5. Consider composite indexes for multi-column queries

---

## Query Optimization Checklist

1. [ ] Use EXPLAIN to analyze query plan
2. [ ] Avoid SELECT * - specify columns
3. [ ] Use LIMIT for pagination
4. [ ] Add indexes for WHERE/JOIN columns
5. [ ] Use WHERE instead of HAVING when possible
6. [ ] Avoid functions on indexed columns in WHERE
7. [ ] Use EXISTS instead of IN for large subqueries

---

## Red Flags to Call Out

| Flag | Question to Ask |
|------|-----------------|
| Query in a loop | "Can we fetch all this data in one query?" |
| No pagination | "What if there are 1 million records?" |
| SELECT * | "Do we need all 50 columns?" |
| String in query | "Is this protected against SQL injection?" |
| No indexes on foreign keys | "How fast are JOINs on this table?" |
| DROP TABLE in migration | "How do we roll this back?" |
| TEXT for everything | "Should this be an INT or DATE instead?" |
| No foreign key constraints | "What prevents orphaned records?" |

---

## ORM Best Practices

```typescript
// Eager loading (avoid N+1)
const users = await User.findAll({
  include: [{ model: Post, attributes: ['id', 'title'] }]
});

// Select specific fields
const users = await User.findAll({
  attributes: ['id', 'name', 'email']
});

// Pagination
const users = await User.findAll({
  limit: 20,
  offset: (page - 1) * 20
});

// Raw queries for complex operations
const results = await sequelize.query(
  'SELECT ... complex query ...',
  { type: QueryTypes.SELECT }
);
```
