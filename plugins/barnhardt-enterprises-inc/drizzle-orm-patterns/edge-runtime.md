# Edge Runtime Patterns

Comprehensive guide to using Drizzle ORM with Vercel Edge Runtime and serverless PostgreSQL.

## Table of Contents

- [Why Edge Runtime?](#why-edge-runtime)
- [Edge-Compatible Setup](#edge-compatible-setup)
- [Neon Serverless Integration](#neon-serverless-integration)
- [Connection Pooling](#connection-pooling)
- [Query Performance](#query-performance)
- [Limitations and Workarounds](#limitations-and-workarounds)
- [Best Practices](#best-practices)

---

## Why Edge Runtime?

### Benefits

- **Global distribution**: Run database queries closer to users
- **0ms cold starts**: No Lambda cold start delays
- **Lower costs**: Pay only for compute time
- **Better performance**: Reduced latency for database operations
- **Automatic scaling**: Handle traffic spikes without configuration

### Quetrex's Edge-First Architecture

Quetrex uses Drizzle ORM specifically because it's edge-compatible. Prisma 6.19.0 blocks Vercel Edge Runtime due to Node.js dependencies.

**Decision Record**: See `/docs/decisions/ADR-002-DRIZZLE-ORM-MIGRATION.md`

---

## Edge-Compatible Setup

### Database Driver

```typescript
// ✅ GOOD: Edge-compatible driver
import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';

const sql = neon(process.env.DATABASE_URL!);
export const db = drizzle(sql);

// ❌ BAD: Node.js driver (not edge-compatible)
import { Pool } from 'pg';
import { drizzle } from 'drizzle-orm/node-postgres';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
export const db = drizzle(pool);
```

### Next.js 15 App Router (Edge)

```typescript
// app/api/users/route.ts
import { db } from '@/lib/db';
import { users } from '@/lib/schema';
import { eq } from 'drizzle-orm';

// Specify edge runtime
export const runtime = 'edge';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  if (!id) {
    return Response.json({ error: 'Missing id' }, { status: 400 });
  }

  const [user] = await db
    .select()
    .from(users)
    .where(eq(users.id, parseInt(id)))
    .limit(1);

  if (!user) {
    return Response.json({ error: 'User not found' }, { status: 404 });
  }

  return Response.json(user);
}
```

### Server Actions (Edge)

```typescript
// app/actions.ts
'use server';

import { db } from '@/lib/db';
import { users } from '@/lib/schema';

export const runtime = 'edge';

export async function createUser(formData: FormData) {
  const email = formData.get('email') as string;
  const name = formData.get('name') as string;

  const [user] = await db
    .insert(users)
    .values({ email, name })
    .returning();

  return { success: true, user };
}
```

---

## Neon Serverless Integration

### HTTP-Based Connections

```typescript
// src/lib/db.ts
import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';

// HTTP-based connection (edge-compatible)
const sql = neon(process.env.DATABASE_URL!, {
  fetchOptions: {
    // Optional: Add caching headers
    cache: 'no-store',
  },
});

export const db = drizzle(sql);
```

### WebSocket Connections (Node.js Only)

```typescript
// ⚠️ WARNING: WebSocket driver is NOT edge-compatible
// Use only in Node.js runtime (API routes, server components)

import { Pool, neonConfig } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-serverless';
import ws from 'ws';

// Enable WebSocket (Node.js only)
neonConfig.webSocketConstructor = ws;

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
export const db = drizzle(pool);
```

### Environment Variables

```bash
# .env.local
DATABASE_URL="postgresql://user:password@ep-cool-name-123456.us-east-2.aws.neon.tech/dbname?sslmode=require"

# For Vercel deployment
POSTGRES_PRISMA_URL="..." # Not used (Prisma-specific)
POSTGRES_URL_NON_POOLING="..." # Not used
```

---

## Connection Pooling

### Neon Connection Pooling

```typescript
// Enable connection pooling in Neon dashboard
// Use pooled connection string: ?sslmode=require&pooler=true

// src/lib/db.ts
import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';

// Pooled connection string
const sql = neon(process.env.DATABASE_URL_POOLED!);
export const db = drizzle(sql);
```

### Connection Limits

```typescript
// Edge Runtime: HTTP connections (no limit)
// Each request gets a new HTTP connection
// Neon handles connection pooling server-side

// ✅ GOOD: HTTP-based (edge-compatible)
const sql = neon(process.env.DATABASE_URL!);
export const db = drizzle(sql);

// ❌ BAD: WebSocket pool (Node.js only)
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10, // Connection limit (not available in edge)
});
```

### Lazy Connection Initialization

```typescript
// Connections are created on-demand
// No need to manage connection lifecycle in edge runtime

import { db } from '@/lib/db';

export async function GET() {
  // Connection created automatically
  const users = await db.select().from(users);

  // No need to close connection
  return Response.json(users);
}
```

---

## Query Performance

### Edge Runtime Timeouts

```typescript
// ⚠️ WARNING: Edge functions have 25-second timeout (Vercel)
// Keep queries fast (<1 second recommended)

// ✅ GOOD: Fast query
export const runtime = 'edge';

export async function GET() {
  const users = await db
    .select({ id: users.id, name: users.name })
    .from(users)
    .limit(100); // Limit results

  return Response.json(users);
}

// ❌ BAD: Slow query (may timeout)
export const runtime = 'edge';

export async function GET() {
  const users = await db
    .select()
    .from(users)
    .leftJoin(orders, eq(users.id, orders.userId))
    .leftJoin(orderItems, eq(orders.id, orderItems.orderId))
    .leftJoin(products, eq(orderItems.productId, products.id));
  // Complex join across large tables - may timeout

  return Response.json(users);
}
```

### Query Optimization for Edge

```typescript
// ✅ GOOD: Paginated query
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get('page') || '1');
  const pageSize = 20;

  const users = await db
    .select()
    .from(users)
    .limit(pageSize)
    .offset((page - 1) * pageSize);

  return Response.json(users);
}

// ✅ GOOD: Indexed query
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const email = searchParams.get('email');

  // Fast lookup using unique index
  const [user] = await db
    .select()
    .from(users)
    .where(eq(users.email, email))
    .limit(1);

  return Response.json(user);
}
```

### Caching Strategies

```typescript
// Use Next.js cache for expensive queries
import { unstable_cache } from 'next/cache';
import { db } from '@/lib/db';
import { users } from '@/lib/schema';

export const runtime = 'edge';

// Cache for 5 minutes
const getCachedUsers = unstable_cache(
  async () => {
    return await db.select().from(users);
  },
  ['all-users'],
  { revalidate: 300 } // 5 minutes
);

export async function GET() {
  const users = await getCachedUsers();
  return Response.json(users);
}
```

---

## Limitations and Workarounds

### Transaction Limitations

```typescript
// ⚠️ WARNING: Long transactions may timeout on edge

// ❌ BAD: Long transaction (may timeout)
export const runtime = 'edge';

export async function POST() {
  await db.transaction(async (tx) => {
    // Processing thousands of records
    for (const item of largeDataset) {
      await tx.insert(items).values(item); // Slow!
    }
  });
}

// ✅ GOOD: Quick transaction
export const runtime = 'edge';

export async function POST(request: Request) {
  const data = await request.json();

  const result = await db.transaction(async (tx) => {
    const [user] = await tx
      .insert(users)
      .values(data)
      .returning();

    await tx
      .insert(profiles)
      .values({ userId: user.id });

    return user;
  });

  return Response.json(result);
}

// ✅ GOOD: Use background job for large operations
export const runtime = 'edge';

export async function POST(request: Request) {
  const data = await request.json();

  // Create job record
  const [job] = await db
    .insert(jobs)
    .values({
      type: 'import_data',
      data: JSON.stringify(data),
      status: 'pending',
    })
    .returning();

  // Process in background worker (not edge)
  await queueJob(job.id);

  return Response.json({ jobId: job.id });
}
```

### No File System Access

```typescript
// ❌ BAD: Read file (not available in edge)
import fs from 'fs';

export const runtime = 'edge';

export async function GET() {
  const data = fs.readFileSync('./data.json', 'utf-8'); // Error!
  return Response.json(JSON.parse(data));
}

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

### No Native Crypto

```typescript
// ⚠️ WARNING: Some crypto operations not available in edge

// ❌ BAD: Use bcrypt (not edge-compatible)
import bcrypt from 'bcrypt';

export const runtime = 'edge';

export async function POST(request: Request) {
  const { password } = await request.json();
  const hash = await bcrypt.hash(password, 10); // Error!
  return Response.json({ hash });
}

// ✅ GOOD: Use Web Crypto API
export const runtime = 'edge';

export async function POST(request: Request) {
  const { password } = await request.json();

  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hash = btoa(String.fromCharCode(...new Uint8Array(hashBuffer)));

  return Response.json({ hash });
}
```

---

## Best Practices

### 1. Use Edge for Read-Heavy Operations

```typescript
// ✅ GOOD: Fast read queries on edge
export const runtime = 'edge';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get('userId');

  const user = await db.query.users.findFirst({
    where: eq(users.id, parseInt(userId!)),
    with: {
      profile: true,
    },
  });

  return Response.json(user);
}
```

### 2. Use Node.js Runtime for Complex Operations

```typescript
// ✅ GOOD: Complex operation in Node.js runtime
// No runtime = 'edge' declaration (defaults to Node.js)

export async function POST(request: Request) {
  const data = await request.json();

  // Complex transaction with external API calls
  await db.transaction(async (tx) => {
    const [order] = await tx.insert(orders).values(data).returning();

    // Call payment API (may be slow)
    const payment = await stripe.charges.create({
      amount: order.total * 100,
      currency: 'usd',
    });

    await tx.insert(payments).values({
      orderId: order.id,
      stripeId: payment.id,
    });
  });

  return Response.json({ success: true });
}
```

### 3. Optimize Queries for Edge

```typescript
// ✅ GOOD: Optimized edge queries
export const runtime = 'edge';

export async function GET() {
  // Select only needed fields
  const users = await db
    .select({
      id: users.id,
      name: users.name,
      email: users.email,
    })
    .from(users)
    .where(eq(users.status, 'active'))
    .orderBy(desc(users.createdAt))
    .limit(50);

  return Response.json(users);
}
```

### 4. Use Database Indexes

```typescript
// Schema with indexes for edge queries
export const users = pgTable(
  'users',
  {
    id: serial('id').primaryKey(),
    email: text('email').notNull().unique(),
    status: text('status').notNull().default('active'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => ({
    // Index for fast status filtering
    statusIdx: index('users_status_idx').on(table.status),
    // Index for fast sorting by creation date
    createdAtIdx: index('users_created_at_idx').on(table.createdAt),
    // Composite index for common query pattern
    statusCreatedIdx: index('users_status_created_idx').on(
      table.status,
      table.createdAt
    ),
  })
);
```

### 5. Implement Proper Error Handling

```typescript
export const runtime = 'edge';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
      return Response.json(
        { error: 'Missing id parameter' },
        { status: 400 }
      );
    }

    const [user] = await db
      .select()
      .from(users)
      .where(eq(users.id, parseInt(id)))
      .limit(1);

    if (!user) {
      return Response.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    return Response.json(user);
  } catch (error) {
    console.error('Database error:', error);
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

### 6. Monitor Performance

```typescript
export const runtime = 'edge';

export async function GET() {
  const startTime = Date.now();

  try {
    const users = await db
      .select()
      .from(users)
      .limit(100);

    const duration = Date.now() - startTime;

    // Log slow queries
    if (duration > 1000) {
      console.warn(`Slow query: ${duration}ms`);
    }

    return Response.json(users, {
      headers: {
        'X-Query-Duration': duration.toString(),
      },
    });
  } catch (error) {
    const duration = Date.now() - startTime;
    console.error(`Query failed after ${duration}ms:`, error);
    throw error;
  }
}
```

### 7. Use Streaming for Large Results

```typescript
export const runtime = 'edge';

export async function GET() {
  // Stream results for large datasets
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      const users = await db.select().from(users);

      // Send data in chunks
      for (const user of users) {
        const chunk = JSON.stringify(user) + '\n';
        controller.enqueue(encoder.encode(chunk));
      }

      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'application/x-ndjson',
    },
  });
}
```

---

## Performance Benchmarks

### Edge vs Node.js Runtime

```
Query: SELECT * FROM users WHERE email = $1 LIMIT 1

Edge Runtime:
- Cold start: 0ms
- Query time: 15-30ms
- Total: 15-30ms

Node.js Runtime:
- Cold start: 200-500ms
- Query time: 15-30ms
- Total: 215-530ms

Edge is 7-17x faster on first request!
```

### Connection Overhead

```
HTTP Connection (Edge):
- Setup: 5-10ms
- Query: 15-30ms
- Total: 20-40ms

WebSocket Connection (Node.js):
- Setup: 50-100ms
- Query: 15-30ms
- Total: 65-130ms

HTTP is 3-6x faster for single queries!
```

---

**Official Docs**: https://neon.tech/docs/serverless/serverless-driver
**Vercel Edge**: https://vercel.com/docs/functions/edge-functions
**Next**: [performance.md](./performance.md) for optimization patterns
