# Common Mistakes and How to Fix Them

Comprehensive guide to avoiding common pitfalls when using Drizzle ORM.

## Table of Contents

- [SQL Injection Vulnerabilities](#sql-injection-vulnerabilities)
- [N+1 Query Problems](#n1-query-problems)
- [Missing Indexes](#missing-indexes)
- [Transaction Deadlocks](#transaction-deadlocks)
- [Type Safety Issues](#type-safety-issues)
- [Performance Problems](#performance-problems)
- [Edge Runtime Errors](#edge-runtime-errors)
- [Migration Mistakes](#migration-mistakes)

---

## SQL Injection Vulnerabilities

### Mistake 1: String Interpolation in Queries

```typescript
// ❌ DANGEROUS: SQL injection vulnerability
const email = request.query.email; // User input
const users = await db.execute(
  sql`SELECT * FROM users WHERE email = '${email}'`
);

// Attack: email = "'; DROP TABLE users; --"
// Results in: SELECT * FROM users WHERE email = ''; DROP TABLE users; --'
```

**Fix: Use Parameterized Queries**

```typescript
// ✅ SAFE: Parameterized query
import { eq } from 'drizzle-orm';

const email = request.query.email;
const users = await db
  .select()
  .from(users)
  .where(eq(users.email, email)); // Automatically escaped

// Or with sql.placeholder:
const users = await db.execute(
  sql`SELECT * FROM users WHERE email = ${sql.placeholder('email')}`,
  { email }
);
```

### Mistake 2: Dynamic Column Names

```typescript
// ❌ DANGEROUS: Column name from user input
const sortBy = request.query.sortBy; // User input: "id; DROP TABLE users"
const users = await db.execute(
  sql`SELECT * FROM users ORDER BY ${sql.raw(sortBy)}`
);
```

**Fix: Whitelist Valid Columns**

```typescript
// ✅ SAFE: Whitelist approach
const validColumns = ['id', 'name', 'email', 'createdAt'] as const;
type ValidColumn = typeof validColumns[number];

function isValidColumn(column: string): column is ValidColumn {
  return validColumns.includes(column as ValidColumn);
}

const sortBy = request.query.sortBy;

if (!isValidColumn(sortBy)) {
  throw new Error('Invalid sort column');
}

const users = await db
  .select()
  .from(users)
  .orderBy(asc(users[sortBy]));
```

### Mistake 3: LIKE Pattern Injection

```typescript
// ❌ VULNERABLE: Pattern injection
const search = request.query.search; // User input: "%'; DROP TABLE users; --"
const users = await db
  .select()
  .from(users)
  .where(sql`name LIKE '%${search}%'`);
```

**Fix: Escape LIKE Patterns**

```typescript
// ✅ SAFE: Properly escaped LIKE
import { like, sql } from 'drizzle-orm';

const search = request.query.search;

// Option 1: Use like() with parameterized value
const users = await db
  .select()
  .from(users)
  .where(like(users.name, `%${search}%`)); // Automatically escaped

// Option 2: Escape manually
function escapeLikePattern(pattern: string): string {
  return pattern.replace(/[%_\\]/g, '\\$&');
}

const escaped = escapeLikePattern(search);
const users = await db
  .select()
  .from(users)
  .where(like(users.name, `%${escaped}%`));
```

---

## N+1 Query Problems

### Mistake 4: Loop Queries

```typescript
// ❌ BAD: N+1 queries
const users = await db.select().from(users).limit(100); // 1 query

for (const user of users) {
  const orders = await db
    .select()
    .from(orders)
    .where(eq(orders.userId, user.id)); // 100 queries!

  console.log(`${user.name}: ${orders.length} orders`);
}

// Total: 101 queries (very slow)
```

**Fix: Use Joins or Batch Loading**

```typescript
// ✅ GOOD: Single query with join
const usersWithOrderCount = await db
  .select({
    userId: users.id,
    userName: users.name,
    orderCount: count(orders.id),
  })
  .from(users)
  .leftJoin(orders, eq(users.id, orders.userId))
  .groupBy(users.id, users.name);

// Total: 1 query (fast)

// ✅ GOOD: Batch load all orders
const users = await db.select().from(users).limit(100); // 1 query

const userIds = users.map((u) => u.id);
const allOrders = await db
  .select()
  .from(orders)
  .where(inArray(orders.userId, userIds)); // 1 query

const ordersByUser = allOrders.reduce((acc, order) => {
  if (!acc[order.userId]) acc[order.userId] = [];
  acc[order.userId].push(order);
  return acc;
}, {} as Record<number, typeof allOrders>);

for (const user of users) {
  const orders = ordersByUser[user.id] || [];
  console.log(`${user.name}: ${orders.length} orders`);
}

// Total: 2 queries (fast)
```

### Mistake 5: Nested Loop Queries

```typescript
// ❌ TERRIBLE: N*M queries
const users = await db.select().from(users); // 1 query

for (const user of users) {
  const orders = await db
    .select()
    .from(orders)
    .where(eq(orders.userId, user.id)); // N queries

  for (const order of orders) {
    const items = await db
      .select()
      .from(orderItems)
      .where(eq(orderItems.orderId, order.id)); // N*M queries!
  }
}
```

**Fix: Use Drizzle Relations**

```typescript
// ✅ GOOD: Use relations (optimized by Drizzle)
const usersWithOrders = await db.query.users.findMany({
  with: {
    orders: {
      with: {
        orderItems: true,
      },
    },
  },
});

// Drizzle optimizes this into minimal queries
```

---

## Missing Indexes

### Mistake 6: No Index on Foreign Keys

```typescript
// ❌ BAD: Foreign key without index
export const orders = pgTable('orders', {
  id: serial('id').primaryKey(),
  userId: integer('user_id')
    .notNull()
    .references(() => users.id),
  total: numeric('total').notNull(),
});

// Slow join query (table scan)
const usersWithOrders = await db
  .select()
  .from(users)
  .leftJoin(orders, eq(users.id, orders.userId));
```

**Fix: Always Index Foreign Keys**

```typescript
// ✅ GOOD: Index on foreign key
export const orders = pgTable(
  'orders',
  {
    id: serial('id').primaryKey(),
    userId: integer('user_id')
      .notNull()
      .references(() => users.id),
    total: numeric('total').notNull(),
  },
  (table) => ({
    userIdIdx: index('orders_user_id_idx').on(table.userId),
  })
);

// Fast join query (index scan)
```

### Mistake 7: No Index on Frequently Queried Columns

```typescript
// ❌ BAD: No index on status field
export const orders = pgTable('orders', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').notNull(),
  status: text('status').notNull(),
});

// Slow query (full table scan)
const pendingOrders = await db
  .select()
  .from(orders)
  .where(eq(orders.status, 'pending'));
```

**Fix: Add Index on Queried Columns**

```typescript
// ✅ GOOD: Index on status field
export const orders = pgTable(
  'orders',
  {
    id: serial('id').primaryKey(),
    userId: integer('user_id').notNull(),
    status: text('status').notNull(),
  },
  (table) => ({
    statusIdx: index('orders_status_idx').on(table.status),
  })
);

// Fast query (index scan)
```

---

## Transaction Deadlocks

### Mistake 8: Inconsistent Lock Order

```typescript
// ❌ BAD: Can cause deadlock
// Transaction A: locks account 1, then account 2
// Transaction B: locks account 2, then account 1
// = DEADLOCK!

async function transferMoney(from: number, to: number, amount: number) {
  await db.transaction(async (tx) => {
    await tx
      .select()
      .from(accounts)
      .where(eq(accounts.id, from))
      .for('update'); // Lock account 'from'

    await tx
      .select()
      .from(accounts)
      .where(eq(accounts.id, to))
      .for('update'); // Lock account 'to'

    // ... perform transfer
  });
}

// Deadlock scenario:
// transferMoney(1, 2, 100) and transferMoney(2, 1, 50) run concurrently
```

**Fix: Always Lock in Same Order**

```typescript
// ✅ GOOD: Consistent lock order (by ID)
async function transferMoney(from: number, to: number, amount: number) {
  await db.transaction(async (tx) => {
    // Always lock accounts in ascending ID order
    const [firstId, secondId] = [from, to].sort((a, b) => a - b);

    await tx
      .select()
      .from(accounts)
      .where(eq(accounts.id, firstId))
      .for('update');

    await tx
      .select()
      .from(accounts)
      .where(eq(accounts.id, secondId))
      .for('update');

    // ... perform transfer
  });
}
```

### Mistake 9: Long-Running Transactions

```typescript
// ❌ BAD: External calls inside transaction
await db.transaction(async (tx) => {
  const [order] = await tx.insert(orders).values({ total: 99.99 }).returning();

  // External API call (slow, can fail, holds transaction lock)
  const payment = await stripe.charges.create({ amount: 9999 });

  await tx.insert(payments).values({ orderId: order.id, stripeId: payment.id });
});
```

**Fix: Keep Transactions Short**

```typescript
// ✅ GOOD: External calls outside transaction
const [order] = await db
  .insert(orders)
  .values({ total: 99.99, status: 'pending' })
  .returning();

try {
  const payment = await stripe.charges.create({ amount: 9999 });

  await db.transaction(async (tx) => {
    await tx.insert(payments).values({ orderId: order.id, stripeId: payment.id });
    await tx
      .update(orders)
      .set({ status: 'paid' })
      .where(eq(orders.id, order.id));
  });
} catch (error) {
  await db
    .update(orders)
    .set({ status: 'failed' })
    .where(eq(orders.id, order.id));
}
```

---

## Type Safety Issues

### Mistake 10: Using `any` Type

```typescript
// ❌ BAD: Loses type safety
async function getUser(id: any) {
  return await db.select().from(users).where(eq(users.id, id));
}

// No type checking!
await getUser('not-a-number'); // Runtime error
await getUser({ id: 1 }); // Runtime error
```

**Fix: Use Proper Types**

```typescript
// ✅ GOOD: Type-safe function
async function getUser(id: number) {
  return await db
    .select()
    .from(users)
    .where(eq(users.id, id))
    .limit(1);
}

// Type errors caught at compile time
await getUser('not-a-number'); // Error!
await getUser({ id: 1 }); // Error!
await getUser(1); // OK
```

### Mistake 11: Not Using Inferred Types

```typescript
// ❌ BAD: Manually defined type (can drift from schema)
type User = {
  id: number;
  email: string;
  name: string;
  // Easy to forget new fields added to schema!
};

async function getUsers(): Promise<User[]> {
  return await db.select().from(users);
}
```

**Fix: Use Inferred Types**

```typescript
// ✅ GOOD: Inferred type (always matches schema)
type User = typeof users.$inferSelect;

async function getUsers(): Promise<User[]> {
  return await db.select().from(users);
}

// Type automatically updates when schema changes!
```

### Mistake 12: Ignoring Nullable Fields

```typescript
// ❌ BAD: Assumes field is never null
const [user] = await db.select().from(users).limit(1);
console.log(user.age.toString()); // Runtime error if age is null!
```

**Fix: Handle Nullable Fields**

```typescript
// ✅ GOOD: Check for null
const [user] = await db.select().from(users).limit(1);
console.log(user.age?.toString() ?? 'Age not set');

// Or use type guard
if (user.age !== null) {
  console.log(user.age.toString());
}
```

---

## Performance Problems

### Mistake 13: Selecting All Columns

```typescript
// ❌ BAD: Fetches unnecessary data
const users = await db.select().from(users); // Includes all fields

// Transfers 10KB per row (large text fields, blobs, etc.)
// For 1000 rows: 10MB transferred!
```

**Fix: Select Only Needed Fields**

```typescript
// ✅ GOOD: Select specific fields
const users = await db
  .select({
    id: users.id,
    name: users.name,
    email: users.email,
  })
  .from(users);

// Transfers 1KB per row
// For 1000 rows: 1MB transferred (10x faster!)
```

### Mistake 14: No Pagination

```typescript
// ❌ BAD: Fetches all rows (millions!)
const orders = await db.select().from(orders);

// Out of memory error!
```

**Fix: Always Paginate**

```typescript
// ✅ GOOD: Paginate results
const pageSize = 50;
const page = 1;

const orders = await db
  .select()
  .from(orders)
  .limit(pageSize)
  .offset((page - 1) * pageSize);

// ✅ BETTER: Cursor-based pagination
const lastId = 100;
const orders = await db
  .select()
  .from(orders)
  .where(gt(orders.id, lastId))
  .orderBy(asc(orders.id))
  .limit(pageSize);
```

### Mistake 15: Using Count for Existence Check

```typescript
// ❌ BAD: Counts all rows (slow)
const [result] = await db
  .select({ count: count() })
  .from(orders)
  .where(eq(orders.userId, 1));

const hasOrders = result.count > 0;
```

**Fix: Use Limit 1**

```typescript
// ✅ GOOD: Stops after finding first row
const orders = await db
  .select({ id: orders.id })
  .from(orders)
  .where(eq(orders.userId, 1))
  .limit(1);

const hasOrders = orders.length > 0;
```

---

## Edge Runtime Errors

### Mistake 16: Using Node.js APIs in Edge

```typescript
// ❌ ERROR: fs not available in Edge Runtime
import fs from 'fs';

export const runtime = 'edge';

export async function GET() {
  const data = fs.readFileSync('./data.json'); // Error!
  return Response.json(JSON.parse(data));
}
```

**Fix: Use Web APIs or Database**

```typescript
// ✅ GOOD: Store data in database
export const runtime = 'edge';

export async function GET() {
  const [config] = await db
    .select()
    .from(configs)
    .where(eq(configs.key, 'app_settings'))
    .limit(1);

  return Response.json(JSON.parse(config.value));
}
```

### Mistake 17: Long Transactions in Edge

```typescript
// ❌ BAD: May timeout (25 second limit)
export const runtime = 'edge';

export async function POST() {
  await db.transaction(async (tx) => {
    for (const item of largeDataset) {
      await tx.insert(items).values(item); // Slow!
    }
  });
}
```

**Fix: Use Background Jobs**

```typescript
// ✅ GOOD: Queue job for background processing
export const runtime = 'edge';

export async function POST(request: Request) {
  const data = await request.json();

  const [job] = await db
    .insert(jobs)
    .values({
      type: 'import_data',
      data: JSON.stringify(data),
      status: 'pending',
    })
    .returning();

  await queueJob(job.id);

  return Response.json({ jobId: job.id });
}
```

---

## Migration Mistakes

### Mistake 18: Dropping Columns Without Backfilling

```typescript
// ❌ BAD: Data loss!
// Migration 1: Remove column
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  // name removed - DATA LOST!
});
```

**Fix: Multi-Step Migration**

```typescript
// Step 1: Add new column
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  fullName: text('full_name'), // New column
  name: text('name').notNull(), // Keep old
});

// Step 2: Backfill data
await db.execute(sql`UPDATE users SET full_name = name WHERE full_name IS NULL`);

// Step 3: Make new column required
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  fullName: text('full_name').notNull(),
  name: text('name').notNull(), // Still keeping
});

// Step 4: Remove old column
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  fullName: text('full_name').notNull(),
  // name removed safely
});
```

### Mistake 19: No Rollback Plan

```typescript
// ❌ BAD: Can't undo migration
// Migration: Add required column
ALTER TABLE users ADD COLUMN status TEXT NOT NULL;

// Breaks production if deployed without backfill!
```

**Fix: Always Have Rollback**

```sql
-- Migration up: Add nullable column first
ALTER TABLE users ADD COLUMN status TEXT;

-- Backfill
UPDATE users SET status = 'active' WHERE status IS NULL;

-- Make required
ALTER TABLE users ALTER COLUMN status SET NOT NULL;

-- Migration down: Rollback
ALTER TABLE users DROP COLUMN status;
```

---

## Quick Checklist

Before committing code:

- [ ] No string interpolation in SQL queries
- [ ] Use parameterized queries for user input
- [ ] No N+1 queries (check for loops with queries)
- [ ] Indexes on all foreign keys
- [ ] Indexes on frequently queried columns
- [ ] Transactions lock in consistent order
- [ ] Transactions are short (< 1 second)
- [ ] Use inferred types, not manual types
- [ ] Handle nullable fields properly
- [ ] Select only needed fields (no `select *`)
- [ ] Pagination for large result sets
- [ ] No Node.js APIs in edge runtime
- [ ] Migration has rollback plan
- [ ] Run `python validate-queries.py` on changed files

---

**Official Docs**: https://orm.drizzle.team/docs/overview
**Validation Tool**: [validate-queries.py](./validate-queries.py)
