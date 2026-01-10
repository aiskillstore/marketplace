# Performance Optimization Patterns

Comprehensive guide to optimizing database queries and preventing common performance issues with Drizzle ORM.

## Table of Contents

- [Query Optimization](#query-optimization)
- [Indexing Strategies](#indexing-strategies)
- [N+1 Query Prevention](#n1-query-prevention)
- [Batch Operations](#batch-operations)
- [Connection Pooling](#connection-pooling)
- [Caching Strategies](#caching-strategies)
- [Query Analysis](#query-analysis)
- [Performance Monitoring](#performance-monitoring)

---

## Query Optimization

### Select Only Needed Fields

```typescript
// ❌ BAD: Select all fields (wasteful)
const users = await db.select().from(users);

// ✅ GOOD: Select specific fields
const users = await db
  .select({
    id: users.id,
    name: users.name,
    email: users.email,
  })
  .from(users);

// Performance difference:
// Bad: Transfers 10KB per row (includes blob fields, long text, etc.)
// Good: Transfers 1KB per row (only needed data)
// For 1000 rows: 10MB vs 1MB = 10x faster!
```

### Use Limit and Offset Wisely

```typescript
// ❌ BAD: No limit (fetches millions of rows)
const users = await db.select().from(users);

// ✅ GOOD: Paginate results
const pageSize = 50;
const page = 1;
const users = await db
  .select()
  .from(users)
  .limit(pageSize)
  .offset((page - 1) * pageSize);

// ✅ BETTER: Cursor-based pagination (faster for large offsets)
const lastId = 100;
const users = await db
  .select()
  .from(users)
  .where(gt(users.id, lastId))
  .orderBy(asc(users.id))
  .limit(pageSize);
```

### Avoid Unnecessary Joins

```typescript
// ❌ BAD: Join when not needed
const users = await db
  .select({
    id: users.id,
    name: users.name,
  })
  .from(users)
  .leftJoin(profiles, eq(users.id, profiles.userId)); // Profile data not used!

// ✅ GOOD: Only join when needed
const users = await db
  .select({
    id: users.id,
    name: users.name,
  })
  .from(users);

// ✅ GOOD: Join with specific fields
const usersWithBio = await db
  .select({
    id: users.id,
    name: users.name,
    bio: profiles.bio, // Using profile data
  })
  .from(users)
  .leftJoin(profiles, eq(users.id, profiles.userId));
```

### Use Exists Instead of Count

```typescript
// ❌ BAD: Count when you only need existence check
const [result] = await db
  .select({ count: count() })
  .from(orders)
  .where(eq(orders.userId, 1));

const hasOrders = result.count > 0; // Counts all rows (slow)

// ✅ GOOD: Use exists (stops after finding first row)
const hasOrders = await db
  .select({ id: orders.id })
  .from(orders)
  .where(eq(orders.userId, 1))
  .limit(1);

const userHasOrders = hasOrders.length > 0;
```

### Optimize Where Clauses

```typescript
// ❌ BAD: Function in where clause (prevents index usage)
const users = await db
  .select()
  .from(users)
  .where(sql`LOWER(${users.email}) = 'test@example.com'`);

// ✅ GOOD: Direct comparison (uses index)
const users = await db
  .select()
  .from(users)
  .where(eq(users.email, 'test@example.com'));

// ✅ GOOD: Case-insensitive with citext type
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email', { mode: 'citext' }).notNull().unique(),
});
```

---

## Indexing Strategies

### Primary Keys (Automatic Index)

```typescript
// Automatically indexed
export const users = pgTable('users', {
  id: serial('id').primaryKey(), // Index created automatically
  email: text('email').notNull().unique(), // Index created automatically
  name: text('name').notNull(),
});
```

### Single Column Index

```typescript
export const users = pgTable(
  'users',
  {
    id: serial('id').primaryKey(),
    email: text('email').notNull().unique(),
    status: text('status').notNull().default('active'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => ({
    // Index for fast filtering by status
    statusIdx: index('users_status_idx').on(table.status),
  })
);

// Query uses index
const activeUsers = await db
  .select()
  .from(users)
  .where(eq(users.status, 'active')); // Fast!
```

### Composite Index

```typescript
export const orders = pgTable(
  'orders',
  {
    id: serial('id').primaryKey(),
    userId: integer('user_id').notNull(),
    status: text('status').notNull(),
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => ({
    // Composite index for common query pattern
    userStatusIdx: index('orders_user_status_idx').on(
      table.userId,
      table.status
    ),
  })
);

// Query uses composite index
const userOrders = await db
  .select()
  .from(orders)
  .where(
    and(
      eq(orders.userId, 123),
      eq(orders.status, 'pending')
    )
  );
```

### Foreign Key Index

```typescript
// ✅ GOOD: Always index foreign keys
export const orders = pgTable(
  'orders',
  {
    id: serial('id').primaryKey(),
    userId: integer('user_id')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    total: numeric('total', { precision: 10, scale: 2 }).notNull(),
  },
  (table) => ({
    // Index on foreign key for fast joins
    userIdIdx: index('orders_user_id_idx').on(table.userId),
  })
);

// Fast join using index
const usersWithOrders = await db
  .select()
  .from(users)
  .leftJoin(orders, eq(users.id, orders.userId));
```

### Partial Index

```typescript
export const users = pgTable(
  'users',
  {
    id: serial('id').primaryKey(),
    email: text('email').notNull().unique(),
    status: text('status').notNull(),
    deletedAt: timestamp('deleted_at'),
  },
  (table) => ({
    // Index only active (non-deleted) users
    activeUsersIdx: index('active_users_idx')
      .on(table.email)
      .where(sql`${table.deletedAt} IS NULL`),
  })
);
```

### Full-Text Search Index

```typescript
export const posts = pgTable(
  'posts',
  {
    id: serial('id').primaryKey(),
    title: text('title').notNull(),
    content: text('content').notNull(),
  },
  (table) => ({
    // GIN index for full-text search
    searchIdx: index('posts_search_idx')
      .using(
        'gin',
        sql`to_tsvector('english', ${table.title} || ' ' || ${table.content})`
      ),
  })
);

// Fast full-text search
const posts = await db
  .select()
  .from(posts)
  .where(
    sql`to_tsvector('english', ${posts.title} || ' ' || ${posts.content}) @@ plainto_tsquery('english', 'search term')`
  );
```

---

## N+1 Query Prevention

### Problem: N+1 Queries

```typescript
// ❌ BAD: N+1 queries (1 query + N queries for each user)
const users = await db.select().from(users).limit(10); // 1 query

for (const user of users) {
  const orders = await db
    .select()
    .from(orders)
    .where(eq(orders.userId, user.id)); // N queries!

  console.log(`User ${user.name} has ${orders.length} orders`);
}

// Total: 11 queries for 10 users
// For 1000 users: 1001 queries! (Very slow)
```

### Solution 1: Join Query

```typescript
// ✅ GOOD: Single join query
const usersWithOrders = await db
  .select({
    userId: users.id,
    userName: users.name,
    orderCount: count(orders.id),
  })
  .from(users)
  .leftJoin(orders, eq(users.id, orders.userId))
  .groupBy(users.id, users.name);

// Total: 1 query for any number of users!
```

### Solution 2: Batch Loading

```typescript
// ✅ GOOD: Load all orders at once
const users = await db.select().from(users).limit(10); // 1 query

const userIds = users.map((u) => u.id);
const orders = await db
  .select()
  .from(orders)
  .where(inArray(orders.userId, userIds)); // 1 query

// Group orders by userId
const ordersByUser = orders.reduce((acc, order) => {
  if (!acc[order.userId]) acc[order.userId] = [];
  acc[order.userId].push(order);
  return acc;
}, {} as Record<number, typeof orders>);

// Use grouped data
for (const user of users) {
  const userOrders = ordersByUser[user.id] || [];
  console.log(`User ${user.name} has ${userOrders.length} orders`);
}

// Total: 2 queries for any number of users!
```

### Solution 3: Drizzle Relations

```typescript
// ✅ GOOD: Use Drizzle's built-in relations
const usersWithOrders = await db.query.users.findMany({
  with: {
    orders: true, // Efficiently loaded
  },
});

// Drizzle optimizes this into minimal queries
for (const user of usersWithOrders) {
  console.log(`User ${user.name} has ${user.orders.length} orders`);
}
```

### Detecting N+1 Queries

```typescript
// Wrap database calls to log queries
let queryCount = 0;

const originalQuery = db.select;
db.select = function (...args: any[]) {
  queryCount++;
  console.log(`Query #${queryCount}`);
  return originalQuery.apply(this, args);
};

// Run your code
await fetchUsersAndOrders();

console.log(`Total queries: ${queryCount}`);
// If queryCount grows with data size, you have N+1 problem!
```

---

## Batch Operations

### Batch Insert

```typescript
// ❌ BAD: Multiple inserts
for (const user of usersToCreate) {
  await db.insert(users).values(user); // N queries
}

// ✅ GOOD: Single batch insert
await db.insert(users).values(usersToCreate); // 1 query

// Performance:
// Bad: 1000 users = 1000 queries = ~10 seconds
// Good: 1000 users = 1 query = ~100ms
// 100x faster!
```

### Batch Update

```typescript
// ❌ BAD: Multiple updates
for (const user of usersToUpdate) {
  await db
    .update(users)
    .set({ status: 'inactive' })
    .where(eq(users.id, user.id)); // N queries
}

// ✅ GOOD: Single update with IN clause
const userIds = usersToUpdate.map((u) => u.id);
await db
  .update(users)
  .set({ status: 'inactive' })
  .where(inArray(users.id, userIds)); // 1 query
```

### Batch Delete

```typescript
// ❌ BAD: Multiple deletes
for (const id of idsToDelete) {
  await db.delete(users).where(eq(users.id, id)); // N queries
}

// ✅ GOOD: Single delete with IN clause
await db.delete(users).where(inArray(users.id, idsToDelete)); // 1 query
```

### Chunked Batch Operations

```typescript
// For very large datasets, process in chunks
async function batchInsertWithChunks<T>(
  table: any,
  data: T[],
  chunkSize = 1000
) {
  for (let i = 0; i < data.length; i += chunkSize) {
    const chunk = data.slice(i, i + chunkSize);
    await db.insert(table).values(chunk);
    console.log(`Inserted ${i + chunk.length} / ${data.length}`);
  }
}

// Usage
await batchInsertWithChunks(users, largeUserArray, 1000);
```

---

## Connection Pooling

### Node.js Connection Pool

```typescript
// src/lib/db.ts
import { Pool } from 'pg';
import { drizzle } from 'drizzle-orm/node-postgres';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20, // Maximum connections
  min: 5, // Minimum connections
  idleTimeoutMillis: 30000, // Close idle connections after 30s
  connectionTimeoutMillis: 2000, // Timeout after 2s
});

export const db = drizzle(pool);

// Graceful shutdown
process.on('SIGTERM', async () => {
  await pool.end();
  process.exit(0);
});
```

### Neon Serverless (Automatic Pooling)

```typescript
// src/lib/db.ts
import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';

// Neon handles connection pooling automatically
const sql = neon(process.env.DATABASE_URL!);
export const db = drizzle(sql);

// No pool management needed!
```

### Connection Pool Monitoring

```typescript
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
});

// Log pool stats
setInterval(() => {
  console.log('Pool stats:', {
    total: pool.totalCount,
    idle: pool.idleCount,
    waiting: pool.waitingCount,
  });
}, 10000); // Every 10 seconds
```

---

## Caching Strategies

### Application-Level Cache

```typescript
// Simple in-memory cache
const cache = new Map<string, { data: any; expires: number }>();

async function getCachedUsers() {
  const cacheKey = 'all_users';
  const cached = cache.get(cacheKey);

  if (cached && cached.expires > Date.now()) {
    return cached.data; // Return cached data
  }

  // Fetch from database
  const users = await db.select().from(users);

  // Cache for 5 minutes
  cache.set(cacheKey, {
    data: users,
    expires: Date.now() + 5 * 60 * 1000,
  });

  return users;
}
```

### Redis Cache

```typescript
import { Redis } from '@upstash/redis';
import { db } from '@/lib/db';
import { users } from '@/lib/schema';

const redis = new Redis({
  url: process.env.REDIS_URL!,
  token: process.env.REDIS_TOKEN!,
});

async function getCachedUser(userId: number) {
  // Try cache first
  const cached = await redis.get(`user:${userId}`);
  if (cached) return cached;

  // Fetch from database
  const [user] = await db
    .select()
    .from(users)
    .where(eq(users.id, userId))
    .limit(1);

  if (!user) return null;

  // Cache for 1 hour
  await redis.setex(`user:${userId}`, 3600, JSON.stringify(user));

  return user;
}

// Invalidate cache on update
async function updateUser(userId: number, data: any) {
  await db
    .update(users)
    .set(data)
    .where(eq(users.id, userId));

  // Invalidate cache
  await redis.del(`user:${userId}`);
}
```

### Next.js Cache

```typescript
import { unstable_cache } from 'next/cache';
import { db } from '@/lib/db';
import { users } from '@/lib/schema';

// Cache with Next.js
export const getCachedUsers = unstable_cache(
  async () => {
    return await db.select().from(users);
  },
  ['all-users'], // Cache key
  {
    revalidate: 300, // Revalidate every 5 minutes
    tags: ['users'], // Tags for cache invalidation
  }
);

// Invalidate cache
import { revalidateTag } from 'next/cache';

export async function createUser(data: any) {
  await db.insert(users).values(data);

  // Invalidate users cache
  revalidateTag('users');
}
```

---

## Query Analysis

### EXPLAIN ANALYZE

```typescript
import { sql } from 'drizzle-orm';

// Analyze query performance
const plan = await db.execute(sql`
  EXPLAIN ANALYZE
  SELECT u.id, u.name, COUNT(o.id) as order_count
  FROM users u
  LEFT JOIN orders o ON u.id = o.user_id
  GROUP BY u.id, u.name
`);

console.log(plan);

// Look for:
// - Seq Scan (bad - needs index)
// - Index Scan (good)
// - Execution time
// - Row estimates vs actual
```

### Slow Query Logging

```typescript
// Wrap queries to measure performance
const originalSelect = db.select;

db.select = function (...args: any[]) {
  const startTime = Date.now();

  const result = originalSelect.apply(this, args);

  // Log slow queries
  const duration = Date.now() - startTime;
  if (duration > 1000) {
    console.warn(`Slow query (${duration}ms):`, args);
  }

  return result;
};
```

### Query Statistics

```typescript
// Track query performance
const queryStats = {
  total: 0,
  slow: 0,
  errors: 0,
  totalTime: 0,
};

async function queryWithStats<T>(queryFn: () => Promise<T>): Promise<T> {
  const startTime = Date.now();
  queryStats.total++;

  try {
    const result = await queryFn();
    const duration = Date.now() - startTime;
    queryStats.totalTime += duration;

    if (duration > 1000) {
      queryStats.slow++;
    }

    return result;
  } catch (error) {
    queryStats.errors++;
    throw error;
  }
}

// Usage
const users = await queryWithStats(() =>
  db.select().from(users)
);

// Log stats
console.log('Query stats:', {
  ...queryStats,
  avgTime: queryStats.totalTime / queryStats.total,
});
```

---

## Performance Monitoring

### Database Metrics

```typescript
// Monitor database performance
async function getDatabaseMetrics() {
  // Active connections
  const [connections] = await db.execute(sql`
    SELECT count(*) as active_connections
    FROM pg_stat_activity
    WHERE state = 'active'
  `);

  // Database size
  const [size] = await db.execute(sql`
    SELECT pg_database_size(current_database()) as size_bytes
  `);

  // Table sizes
  const tableSizes = await db.execute(sql`
    SELECT
      schemaname,
      tablename,
      pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
    FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
  `);

  // Slowest queries
  const slowQueries = await db.execute(sql`
    SELECT
      query,
      calls,
      total_time,
      mean_time,
      max_time
    FROM pg_stat_statements
    ORDER BY mean_time DESC
    LIMIT 10
  `);

  return {
    connections,
    size,
    tableSizes,
    slowQueries,
  };
}
```

### Performance Testing

```typescript
import { describe, it, expect } from 'vitest';

describe('Performance Tests', () => {
  it('should fetch users in under 100ms', async () => {
    const startTime = Date.now();

    await db
      .select()
      .from(users)
      .limit(100);

    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(100);
  });

  it('should handle 1000 concurrent queries', async () => {
    const queries = Array.from({ length: 1000 }, (_, i) =>
      db
        .select()
        .from(users)
        .where(eq(users.id, i + 1))
        .limit(1)
    );

    const startTime = Date.now();
    await Promise.all(queries);
    const duration = Date.now() - startTime;

    // Should complete in under 5 seconds
    expect(duration).toBeLessThan(5000);
  });
});
```

---

## Performance Checklist

Before deploying database code:

- [ ] Select only needed fields (no `select *`)
- [ ] Add indexes on foreign keys
- [ ] Add indexes on frequently queried columns
- [ ] Use composite indexes for common query patterns
- [ ] Check for N+1 queries
- [ ] Use batch operations for multiple inserts/updates
- [ ] Add pagination (limit/offset or cursor)
- [ ] Run EXPLAIN ANALYZE on complex queries
- [ ] Test performance with realistic data volume
- [ ] Monitor slow query logs
- [ ] Implement caching where appropriate
- [ ] Set up connection pooling
- [ ] Add query timeout limits
- [ ] Test concurrent query load

---

**Official Docs**: https://orm.drizzle.team/docs/indexes-constraints
**Next**: [type-inference.md](./type-inference.md) for TypeScript type patterns
