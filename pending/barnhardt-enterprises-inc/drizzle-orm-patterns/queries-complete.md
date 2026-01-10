# Complete Query Patterns

Comprehensive guide to all Drizzle ORM query operations for PostgreSQL.

## Table of Contents

- [Select Queries](#select-queries)
- [Where Clauses](#where-clauses)
- [Ordering and Pagination](#ordering-and-pagination)
- [Field Selection](#field-selection)
- [Joins](#joins)
- [Insert Queries](#insert-queries)
- [Update Queries](#update-queries)
- [Delete Queries](#delete-queries)
- [Aggregations](#aggregations)
- [Subqueries](#subqueries)
- [Common Table Expressions (CTEs)](#common-table-expressions-ctes)
- [Union Queries](#union-queries)

---

## Select Queries

### Select All Records

```typescript
import { db } from '@/lib/db';
import { users } from '@/lib/schema';

// Get all users (WARNING: Use with caution on large tables)
const allUsers = await db.select().from(users);
```

### Select Single Record

```typescript
import { eq } from 'drizzle-orm';

// Get user by ID
const user = await db
  .select()
  .from(users)
  .where(eq(users.id, 1))
  .limit(1);

// Returns array, use [0] or get() for single record
const [firstUser] = user;
```

### Select with findFirst Pattern

```typescript
// Find first matching user
const user = await db
  .select()
  .from(users)
  .where(eq(users.email, 'test@example.com'))
  .limit(1);

if (user.length === 0) {
  throw new Error('User not found');
}

const foundUser = user[0];
```

### Select with findMany Pattern

```typescript
import { and, eq } from 'drizzle-orm';

// Find all active users
const activeUsers = await db
  .select()
  .from(users)
  .where(eq(users.status, 'active'));

// Find with multiple conditions
const premiumActiveUsers = await db
  .select()
  .from(users)
  .where(
    and(
      eq(users.status, 'active'),
      eq(users.plan, 'premium')
    )
  );
```

---

## Where Clauses

### Equality Operators

```typescript
import { eq, ne } from 'drizzle-orm';

// Equal to
const user = await db
  .select()
  .from(users)
  .where(eq(users.id, 1));

// Not equal to
const nonAdminUsers = await db
  .select()
  .from(users)
  .where(ne(users.role, 'admin'));
```

### Comparison Operators

```typescript
import { gt, gte, lt, lte } from 'drizzle-orm';

// Greater than
const recentUsers = await db
  .select()
  .from(users)
  .where(gt(users.createdAt, new Date('2024-01-01')));

// Greater than or equal
const adultsOrOlder = await db
  .select()
  .from(users)
  .where(gte(users.age, 18));

// Less than
const youngUsers = await db
  .select()
  .from(users)
  .where(lt(users.age, 18));

// Less than or equal
const under30 = await db
  .select()
  .from(users)
  .where(lte(users.age, 30));
```

### Pattern Matching

```typescript
import { like, ilike, notLike, notIlike } from 'drizzle-orm';

// LIKE (case-sensitive)
const gmailUsers = await db
  .select()
  .from(users)
  .where(like(users.email, '%@gmail.com'));

// ILIKE (case-insensitive, PostgreSQL only)
const gmailUsersInsensitive = await db
  .select()
  .from(users)
  .where(ilike(users.email, '%@GMAIL.COM'));

// NOT LIKE
const nonGmailUsers = await db
  .select()
  .from(users)
  .where(notLike(users.email, '%@gmail.com'));

// Starts with pattern
const nameStartsWithA = await db
  .select()
  .from(users)
  .where(like(users.name, 'A%'));

// Contains pattern
const nameContainsMike = await db
  .select()
  .from(users)
  .where(like(users.name, '%Mike%'));
```

### IN Operator

```typescript
import { inArray, notInArray } from 'drizzle-orm';

// IN array
const specificUsers = await db
  .select()
  .from(users)
  .where(inArray(users.id, [1, 2, 3, 4, 5]));

// NOT IN array
const excludedUsers = await db
  .select()
  .from(users)
  .where(notInArray(users.status, ['banned', 'deleted']));

// IN with subquery
const usersWithOrders = await db
  .select()
  .from(users)
  .where(
    inArray(
      users.id,
      db.select({ userId: orders.userId }).from(orders)
    )
  );
```

### NULL Checks

```typescript
import { isNull, isNotNull } from 'drizzle-orm';

// IS NULL
const usersWithoutProfile = await db
  .select()
  .from(users)
  .where(isNull(users.profileId));

// IS NOT NULL
const usersWithProfile = await db
  .select()
  .from(users)
  .where(isNotNull(users.profileId));
```

### Between

```typescript
import { between, notBetween } from 'drizzle-orm';

// BETWEEN
const usersAged20to30 = await db
  .select()
  .from(users)
  .where(between(users.age, 20, 30));

// NOT BETWEEN
const usersNotAged20to30 = await db
  .select()
  .from(users)
  .where(notBetween(users.age, 20, 30));
```

### Logical Operators

```typescript
import { and, or, not } from 'drizzle-orm';

// AND (all conditions must be true)
const premiumActiveUsers = await db
  .select()
  .from(users)
  .where(
    and(
      eq(users.status, 'active'),
      eq(users.plan, 'premium'),
      gte(users.age, 18)
    )
  );

// OR (any condition must be true)
const adminOrModUsers = await db
  .select()
  .from(users)
  .where(
    or(
      eq(users.role, 'admin'),
      eq(users.role, 'moderator')
    )
  );

// NOT
const nonAdminUsers = await db
  .select()
  .from(users)
  .where(not(eq(users.role, 'admin')));

// Complex combination
const complexQuery = await db
  .select()
  .from(users)
  .where(
    and(
      eq(users.status, 'active'),
      or(
        eq(users.plan, 'premium'),
        gte(users.age, 65) // Senior discount
      ),
      not(eq(users.role, 'banned'))
    )
  );
```

### EXISTS

```typescript
import { exists } from 'drizzle-orm';

// Users who have placed orders
const usersWithOrders = await db
  .select()
  .from(users)
  .where(
    exists(
      db.select().from(orders).where(eq(orders.userId, users.id))
    )
  );

// Users who haven't placed orders
const usersWithoutOrders = await db
  .select()
  .from(users)
  .where(
    not(
      exists(
        db.select().from(orders).where(eq(orders.userId, users.id))
      )
    )
  );
```

---

## Ordering and Pagination

### Order By

```typescript
import { asc, desc } from 'drizzle-orm';

// Order by single column (ascending)
const usersByName = await db
  .select()
  .from(users)
  .orderBy(asc(users.name));

// Order by single column (descending)
const newestUsers = await db
  .select()
  .from(users)
  .orderBy(desc(users.createdAt));

// Order by multiple columns
const orderedUsers = await db
  .select()
  .from(users)
  .orderBy(desc(users.isPremium), asc(users.name));
```

### Limit and Offset

```typescript
// Limit results
const first10Users = await db
  .select()
  .from(users)
  .limit(10);

// Offset results (skip first N)
const usersSkip10 = await db
  .select()
  .from(users)
  .offset(10);

// Pagination (limit + offset)
const page = 2;
const pageSize = 20;
const paginatedUsers = await db
  .select()
  .from(users)
  .limit(pageSize)
  .offset((page - 1) * pageSize);
```

### Cursor-Based Pagination

```typescript
// More efficient for large datasets
const pageSize = 20;
const lastUserId = 100; // From previous page

const nextPage = await db
  .select()
  .from(users)
  .where(gt(users.id, lastUserId))
  .orderBy(asc(users.id))
  .limit(pageSize);

// Get cursor for next page
const nextCursor = nextPage.length > 0
  ? nextPage[nextPage.length - 1].id
  : null;
```

---

## Field Selection

### Select Specific Fields

```typescript
// ❌ DON'T: Select all fields (wasteful)
const users = await db.select().from(users);

// ✅ DO: Select only needed fields
const userNames = await db
  .select({
    id: users.id,
    name: users.name,
    email: users.email,
  })
  .from(users);
```

### Select with Aliases

```typescript
// Rename fields in result
const userInfo = await db
  .select({
    userId: users.id,
    fullName: users.name,
    emailAddress: users.email,
  })
  .from(users);

// Result type: { userId: number, fullName: string, emailAddress: string }[]
```

### Select with SQL Expressions

```typescript
import { sql } from 'drizzle-orm';

// Computed fields
const userStats = await db
  .select({
    id: users.id,
    name: users.name,
    fullName: sql`${users.firstName} || ' ' || ${users.lastName}`.as('full_name'),
    isAdult: sql`${users.age} >= 18`.as('is_adult'),
  })
  .from(users);
```

### Select Distinct

```typescript
import { sql } from 'drizzle-orm';

// Distinct values
const distinctRoles = await db
  .selectDistinct({ role: users.role })
  .from(users);

// Using SQL
const distinctEmails = await db
  .select({ email: users.email })
  .from(users)
  .groupBy(users.email);
```

---

## Joins

### Inner Join

```typescript
// INNER JOIN (only matching records)
const usersWithProfiles = await db
  .select({
    userId: users.id,
    userName: users.name,
    bio: profiles.bio,
    avatar: profiles.avatar,
  })
  .from(users)
  .innerJoin(profiles, eq(users.id, profiles.userId));
```

### Left Join

```typescript
// LEFT JOIN (all users, profiles if they exist)
const usersWithOptionalProfiles = await db
  .select({
    userId: users.id,
    userName: users.name,
    bio: profiles.bio, // Can be null
    avatar: profiles.avatar, // Can be null
  })
  .from(users)
  .leftJoin(profiles, eq(users.id, profiles.userId));
```

### Right Join

```typescript
// RIGHT JOIN (all profiles, users if they exist)
const profilesWithUsers = await db
  .select({
    profileId: profiles.id,
    bio: profiles.bio,
    userName: users.name, // Can be null
  })
  .from(users)
  .rightJoin(profiles, eq(users.id, profiles.userId));
```

### Full Join

```typescript
// FULL OUTER JOIN (all records from both tables)
const allUsersAndProfiles = await db
  .select({
    userId: users.id,
    userName: users.name,
    profileId: profiles.id,
    bio: profiles.bio,
  })
  .from(users)
  .fullJoin(profiles, eq(users.id, profiles.userId));
```

### Multiple Joins

```typescript
// Join multiple tables
const usersWithOrdersAndProducts = await db
  .select({
    userName: users.name,
    orderDate: orders.createdAt,
    productName: products.name,
    productPrice: products.price,
  })
  .from(users)
  .innerJoin(orders, eq(users.id, orders.userId))
  .innerJoin(orderItems, eq(orders.id, orderItems.orderId))
  .innerJoin(products, eq(orderItems.productId, products.id));
```

### Join with Where Clause

```typescript
// Filter after join
const recentOrdersWithProducts = await db
  .select({
    userName: users.name,
    orderDate: orders.createdAt,
    productName: products.name,
  })
  .from(users)
  .innerJoin(orders, eq(users.id, orders.userId))
  .innerJoin(orderItems, eq(orders.id, orderItems.orderId))
  .innerJoin(products, eq(orderItems.productId, products.id))
  .where(gte(orders.createdAt, new Date('2024-01-01')));
```

### Self Join

```typescript
// Find users who referred other users
const referrals = await db
  .select({
    referrerName: users.name,
    refereeName: referredUsers.name,
  })
  .from(users)
  .innerJoin(
    referredUsers,
    eq(users.id, referredUsers.referrerId)
  );

// Note: referredUsers is an alias of users table
import { alias } from 'drizzle-orm/pg-core';
const referredUsers = alias(users, 'referred_users');
```

---

## Insert Queries

### Insert Single Record

```typescript
// Basic insert
const result = await db.insert(users).values({
  email: 'test@example.com',
  name: 'Test User',
});

// Insert with returning
const [newUser] = await db
  .insert(users)
  .values({
    email: 'test@example.com',
    name: 'Test User',
  })
  .returning();

console.log(newUser.id); // Newly created ID
```

### Insert Multiple Records (Batch)

```typescript
// Batch insert
const newUsers = await db
  .insert(users)
  .values([
    { email: 'user1@example.com', name: 'User 1' },
    { email: 'user2@example.com', name: 'User 2' },
    { email: 'user3@example.com', name: 'User 3' },
  ])
  .returning();

console.log(`Created ${newUsers.length} users`);
```

### Insert with Default Values

```typescript
// Use database defaults
const [user] = await db
  .insert(users)
  .values({
    email: 'test@example.com',
    name: 'Test User',
    // createdAt will use database default (NOW())
    // status will use database default ('active')
  })
  .returning();
```

### Insert with ON CONFLICT DO NOTHING

```typescript
// Ignore duplicates
const result = await db
  .insert(users)
  .values({
    email: 'existing@example.com', // Already exists
    name: 'Test User',
  })
  .onConflictDoNothing()
  .returning();

if (result.length === 0) {
  console.log('User already exists, skipped insert');
}
```

### Insert with ON CONFLICT DO UPDATE (Upsert)

```typescript
// Update on conflict
const [user] = await db
  .insert(users)
  .values({
    email: 'test@example.com',
    name: 'Test User',
  })
  .onConflictDoUpdate({
    target: users.email,
    set: {
      name: 'Updated Name',
      updatedAt: new Date(),
    },
  })
  .returning();
```

### Upsert with Conditional Update

```typescript
import { sql } from 'drizzle-orm';

// Only update if new value is different
const [user] = await db
  .insert(users)
  .values({
    email: 'test@example.com',
    name: 'New Name',
    loginCount: 1,
  })
  .onConflictDoUpdate({
    target: users.email,
    set: {
      name: sql`EXCLUDED.name`, // Use new value
      loginCount: sql`${users.loginCount} + 1`, // Increment
      lastLoginAt: new Date(),
    },
  })
  .returning();
```

### Insert from Subquery

```typescript
// Copy data from another table
await db
  .insert(archivedUsers)
  .select(
    db
      .select()
      .from(users)
      .where(lt(users.lastLoginAt, new Date('2020-01-01')))
  );
```

---

## Update Queries

### Update Single Record

```typescript
// Update without returning
await db
  .update(users)
  .set({ name: 'Updated Name' })
  .where(eq(users.id, 1));

// Update with returning
const [updatedUser] = await db
  .update(users)
  .set({ name: 'Updated Name' })
  .where(eq(users.id, 1))
  .returning();
```

### Update Multiple Records

```typescript
// Update all matching records
const updatedUsers = await db
  .update(users)
  .set({ status: 'inactive' })
  .where(lt(users.lastLoginAt, new Date('2023-01-01')))
  .returning();

console.log(`Updated ${updatedUsers.length} users`);
```

### Update with SQL Expressions

```typescript
import { sql } from 'drizzle-orm';

// Increment value
await db
  .update(users)
  .set({
    loginCount: sql`${users.loginCount} + 1`,
    lastLoginAt: new Date(),
  })
  .where(eq(users.id, 1));

// Conditional update
await db
  .update(products)
  .set({
    price: sql`CASE WHEN ${products.stock} > 100 THEN ${products.price} * 0.9 ELSE ${products.price} END`,
  })
  .where(eq(products.categoryId, 5));
```

### Update All Records (Use with Caution)

```typescript
// Update all records (no where clause)
// WARNING: This updates EVERY record in the table
await db
  .update(users)
  .set({ migratedToV2: true });
```

### Update with Join (Using Subquery)

```typescript
// Update based on related table data
await db
  .update(users)
  .set({ isPremium: true })
  .where(
    inArray(
      users.id,
      db
        .select({ userId: subscriptions.userId })
        .from(subscriptions)
        .where(eq(subscriptions.status, 'active'))
    )
  );
```

---

## Delete Queries

### Delete Single Record

```typescript
// Delete without returning
await db
  .delete(users)
  .where(eq(users.id, 1));

// Delete with returning
const [deletedUser] = await db
  .delete(users)
  .where(eq(users.id, 1))
  .returning();

console.log(`Deleted user: ${deletedUser.email}`);
```

### Delete Multiple Records

```typescript
// Delete all matching records
const deletedUsers = await db
  .delete(users)
  .where(eq(users.status, 'deleted'))
  .returning();

console.log(`Deleted ${deletedUsers.length} users`);
```

### Delete with Complex Condition

```typescript
// Delete with AND/OR conditions
await db
  .delete(sessions)
  .where(
    and(
      eq(sessions.userId, 1),
      lt(sessions.expiresAt, new Date())
    )
  );

// Delete inactive users from specific date range
await db
  .delete(users)
  .where(
    and(
      eq(users.status, 'inactive'),
      between(users.createdAt, new Date('2020-01-01'), new Date('2021-01-01'))
    )
  );
```

### Delete All Records (Use with EXTREME Caution)

```typescript
// ⚠️ WARNING: Deletes EVERY record in table
await db.delete(temporaryData);

// Better: Add safety check
if (process.env.NODE_ENV === 'production') {
  throw new Error('Cannot truncate table in production');
}
await db.delete(temporaryData);
```

### Delete with Subquery

```typescript
// Delete users who have no orders
await db
  .delete(users)
  .where(
    notInArray(
      users.id,
      db.select({ userId: orders.userId }).from(orders)
    )
  );
```

---

## Aggregations

### Count

```typescript
import { count, sql } from 'drizzle-orm';

// Count all records
const result = await db
  .select({ count: count() })
  .from(users);

console.log(result[0].count); // Total user count

// Count with condition
const activeUserCount = await db
  .select({ count: count() })
  .from(users)
  .where(eq(users.status, 'active'));

// Count distinct
const uniqueEmailCount = await db
  .select({ count: sql`COUNT(DISTINCT ${users.email})`.as('count') })
  .from(users);
```

### Sum

```typescript
import { sum } from 'drizzle-orm';

// Sum all values
const totalRevenue = await db
  .select({ total: sum(orders.total) })
  .from(orders);

// Sum with condition
const monthlyRevenue = await db
  .select({ total: sum(orders.total) })
  .from(orders)
  .where(gte(orders.createdAt, new Date('2024-01-01')));
```

### Average

```typescript
import { avg } from 'drizzle-orm';

// Average value
const avgOrderValue = await db
  .select({ average: avg(orders.total) })
  .from(orders);

// Average by category
const avgPriceByCategory = await db
  .select({
    category: products.categoryId,
    avgPrice: avg(products.price),
  })
  .from(products)
  .groupBy(products.categoryId);
```

### Min and Max

```typescript
import { min, max } from 'drizzle-orm';

// Min value
const cheapestProduct = await db
  .select({ minPrice: min(products.price) })
  .from(products);

// Max value
const mostExpensiveProduct = await db
  .select({ maxPrice: max(products.price) })
  .from(products);

// Multiple aggregations
const priceRange = await db
  .select({
    min: min(products.price),
    max: max(products.price),
    avg: avg(products.price),
  })
  .from(products)
  .where(eq(products.categoryId, 1));
```

### Group By

```typescript
// Group by single column
const ordersByUser = await db
  .select({
    userId: orders.userId,
    orderCount: count(),
    totalSpent: sum(orders.total),
  })
  .from(orders)
  .groupBy(orders.userId);

// Group by multiple columns
const ordersByUserAndStatus = await db
  .select({
    userId: orders.userId,
    status: orders.status,
    count: count(),
  })
  .from(orders)
  .groupBy(orders.userId, orders.status);
```

### Having Clause

```typescript
// Filter groups
const bigSpenders = await db
  .select({
    userId: orders.userId,
    totalSpent: sum(orders.total),
  })
  .from(orders)
  .groupBy(orders.userId)
  .having(sql`SUM(${orders.total}) > 1000`);
```

---

## Subqueries

### Subquery in WHERE

```typescript
// Users who have placed orders
const usersWithOrders = await db
  .select()
  .from(users)
  .where(
    inArray(
      users.id,
      db.select({ userId: orders.userId }).from(orders)
    )
  );

// Products more expensive than average
const expensiveProducts = await db
  .select()
  .from(products)
  .where(
    gt(
      products.price,
      db.select({ avgPrice: avg(products.price) }).from(products)
    )
  );
```

### Subquery in SELECT

```typescript
// Include count from related table
const usersWithOrderCount = await db
  .select({
    id: users.id,
    name: users.name,
    orderCount: sql`(
      SELECT COUNT(*)
      FROM ${orders}
      WHERE ${orders.userId} = ${users.id}
    )`.as('order_count'),
  })
  .from(users);
```

### Subquery in FROM

```typescript
// Query from subquery result
const activeUserOrders = db
  .select()
  .from(users)
  .where(eq(users.status, 'active'))
  .as('active_users');

const orderStats = await db
  .select({
    userName: activeUserOrders.name,
    orderCount: count(),
  })
  .from(activeUserOrders)
  .leftJoin(orders, eq(activeUserOrders.id, orders.userId))
  .groupBy(activeUserOrders.id, activeUserOrders.name);
```

### Correlated Subquery

```typescript
// Find users with above-average order count
const usersWithManyOrders = await db
  .select()
  .from(users)
  .where(
    sql`(
      SELECT COUNT(*)
      FROM ${orders}
      WHERE ${orders.userId} = ${users.id}
    ) > (
      SELECT AVG(order_count)
      FROM (
        SELECT COUNT(*) as order_count
        FROM ${orders}
        GROUP BY ${orders.userId}
      ) counts
    )`
  );
```

---

## Common Table Expressions (CTEs)

### Basic CTE

```typescript
import { sql } from 'drizzle-orm';

// Define CTE
const activeUsers = db.$with('active_users').as(
  db.select().from(users).where(eq(users.status, 'active'))
);

// Use CTE
const result = await db
  .with(activeUsers)
  .select()
  .from(activeUsers);
```

### Multiple CTEs

```typescript
// Define multiple CTEs
const activeUsers = db.$with('active_users').as(
  db.select().from(users).where(eq(users.status, 'active'))
);

const recentOrders = db.$with('recent_orders').as(
  db
    .select()
    .from(orders)
    .where(gte(orders.createdAt, new Date('2024-01-01')))
);

// Use both CTEs
const result = await db
  .with(activeUsers, recentOrders)
  .select({
    userName: activeUsers.name,
    orderDate: recentOrders.createdAt,
  })
  .from(activeUsers)
  .innerJoin(recentOrders, eq(activeUsers.id, recentOrders.userId));
```

### Recursive CTE

```typescript
// Hierarchical data (e.g., organization chart)
const orgTree = db.$with('org_tree').as(
  db
    .select({
      id: employees.id,
      name: employees.name,
      managerId: employees.managerId,
      level: sql`1`.as('level'),
    })
    .from(employees)
    .where(isNull(employees.managerId))
    .unionAll(
      db
        .select({
          id: employees.id,
          name: employees.name,
          managerId: employees.managerId,
          level: sql`org_tree.level + 1`,
        })
        .from(employees)
        .innerJoin(orgTree, eq(employees.managerId, orgTree.id))
    )
);

const hierarchy = await db
  .with(orgTree)
  .select()
  .from(orgTree)
  .orderBy(asc(orgTree.level));
```

---

## Union Queries

### Union

```typescript
// Combine results (removes duplicates)
const allEmails = await db
  .select({ email: users.email })
  .from(users)
  .union(
    db.select({ email: admins.email }).from(admins)
  );
```

### Union All

```typescript
// Combine results (keeps duplicates)
const allActivity = await db
  .select({
    type: sql`'user'`.as('type'),
    id: users.id,
    createdAt: users.createdAt,
  })
  .from(users)
  .unionAll(
    db
      .select({
        type: sql`'order'`.as('type'),
        id: orders.id,
        createdAt: orders.createdAt,
      })
      .from(orders)
  )
  .orderBy(desc(sql`created_at`));
```

### Multiple Unions

```typescript
// Combine multiple queries
const allContacts = await db
  .select({ email: users.email, source: sql`'users'` })
  .from(users)
  .union(
    db.select({ email: customers.email, source: sql`'customers'` }).from(customers)
  )
  .union(
    db.select({ email: subscribers.email, source: sql`'subscribers'` }).from(subscribers)
  );
```

---

## Performance Tips

### 1. Always Select Specific Fields

```typescript
// ❌ BAD: Fetches all fields (wasteful)
const users = await db.select().from(users);

// ✅ GOOD: Fetch only what you need
const users = await db
  .select({
    id: users.id,
    name: users.name,
    email: users.email,
  })
  .from(users);
```

### 2. Use Indexes for Where Clauses

```typescript
// Ensure index exists on frequently queried columns
// In schema.ts:
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(), // Automatically indexed
  status: text('status').notNull(), // Add index if queried often
}, (table) => ({
  statusIdx: index('status_idx').on(table.status),
}));
```

### 3. Avoid N+1 Queries - Use Joins

```typescript
// ❌ BAD: N+1 queries
const users = await db.select().from(users);
for (const user of users) {
  const profile = await db
    .select()
    .from(profiles)
    .where(eq(profiles.userId, user.id));
}

// ✅ GOOD: Single join query
const usersWithProfiles = await db
  .select({
    userId: users.id,
    userName: users.name,
    bio: profiles.bio,
  })
  .from(users)
  .leftJoin(profiles, eq(users.id, profiles.userId));
```

### 4. Use Batch Operations

```typescript
// ❌ BAD: Multiple inserts
for (const user of usersToCreate) {
  await db.insert(users).values(user);
}

// ✅ GOOD: Single batch insert
await db.insert(users).values(usersToCreate);
```

### 5. Use Limit for Large Results

```typescript
// Always limit results to avoid memory issues
const recentUsers = await db
  .select()
  .from(users)
  .orderBy(desc(users.createdAt))
  .limit(100);
```

---

## Security Checklist

- [ ] Never use string interpolation in SQL (use parameterized queries)
- [ ] Always validate user input before querying
- [ ] Use `eq()`, `inArray()`, etc. instead of raw SQL for user input
- [ ] Select specific fields, not `*`
- [ ] Add proper indexes on queried columns
- [ ] Use transactions for multi-step operations
- [ ] Set appropriate query timeouts
- [ ] Log slow queries for optimization

---

**Official Docs**: https://orm.drizzle.team/docs/select
**Next**: [transactions.md](./transactions.md) for transaction patterns
