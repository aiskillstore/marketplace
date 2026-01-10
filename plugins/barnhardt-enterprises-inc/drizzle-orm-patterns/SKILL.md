# Drizzle ORM Patterns - Complete PostgreSQL Reference

**Use when:** Working with database operations, schema design, migrations, or queries in Quetrex.

## Overview

This skill provides comprehensive Drizzle ORM patterns for PostgreSQL with Vercel Edge Runtime support. Drizzle is Quetrex's chosen ORM because it's edge-first, type-safe, and supports all deployment targets.

## Why Drizzle?

- **Edge Runtime Compatible**: Works with Vercel Edge Functions, Cloudflare Workers
- **Type-Safe**: Full TypeScript inference without code generation
- **Zero Dependencies**: No heavy Node.js runtime requirements
- **SQL-Like API**: Familiar to developers who know SQL
- **Lightweight**: ~7.4kb minified (vs Prisma's ~300kb)

## Skill Structure

This skill is organized into focused modules:

### 1. [queries-complete.md](./queries-complete.md)
Complete query patterns: select, insert, update, delete, joins, pagination, filtering, aggregations, subqueries, CTEs.

**When to use:**
- Building any database query
- Fetching data with filters
- Inserting/updating/deleting records
- Pagination or sorting
- Aggregating data (count, sum, avg)
- Complex joins or subqueries

### 2. [transactions.md](./transactions.md)
Transaction patterns: isolation levels, rollback, nested transactions, error handling, deadlock prevention.

**When to use:**
- Multiple operations that must succeed together
- Financial operations (payments, transfers)
- Data consistency requirements
- Race condition prevention
- Complex multi-step workflows

### 3. [relations.md](./relations.md)
Relationship patterns: one-to-one, one-to-many, many-to-many, self-referencing, cascading deletes, nested queries.

**When to use:**
- Defining schema relationships
- Querying related data
- Setting up cascading operations
- Working with hierarchical data
- Optimizing related data fetching

### 4. [migrations.md](./migrations.md)
Migration patterns: schema evolution, data migrations, zero-downtime deployments, rollback strategies.

**When to use:**
- Adding/modifying database schema
- Migrating data between schemas
- Deploying schema changes
- Rolling back problematic migrations
- Renaming tables/columns safely

### 5. [edge-runtime.md](./edge-runtime.md)
Edge deployment patterns: Vercel Edge Functions, Neon serverless, connection pooling, HTTP-based connections.

**When to use:**
- Deploying to Vercel Edge Runtime
- Using Neon serverless PostgreSQL
- Optimizing edge function performance
- Configuring connection pooling
- Understanding edge limitations

### 6. [performance.md](./performance.md)
Performance patterns: indexing, query optimization, N+1 prevention, batch operations, caching.

**When to use:**
- Slow queries
- High database load
- N+1 query problems
- Large data sets
- Performance optimization needed

### 7. [type-inference.md](./type-inference.md)
TypeScript inference patterns: InferModel, InferSelect, InferInsert, schema types, custom types.

**When to use:**
- Defining TypeScript types from schema
- Creating API types
- Type-safe query builders
- Custom type mappers
- Ensuring type safety

### 8. [common-mistakes.md](./common-mistakes.md)
Common pitfalls and fixes: SQL injection risks, N+1 queries, missing indexes, transaction deadlocks, type errors.

**When to use:**
- Debugging database issues
- Code review
- Learning best practices
- Avoiding common errors
- Security audits

### 9. [validate-queries.py](./validate-queries.py)
Python script to validate Drizzle queries for common security and performance issues.

**When to use:**
- Pre-commit validation
- Security audits
- Performance reviews
- Finding SQL injection risks
- Detecting N+1 patterns

## Quick Start

### Installation

```bash
# Core packages
npm install drizzle-orm @neondatabase/serverless

# Development tools
npm install -D drizzle-kit
```

### Basic Setup

```typescript
// src/lib/db.ts
import { drizzle } from 'drizzle-orm/neon-http';
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL!);
export const db = drizzle(sql);
```

### Define Schema

```typescript
// src/lib/schema.ts
import { pgTable, serial, text, timestamp } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});
```

### Basic Query

```typescript
// src/services/user-service.ts
import { db } from '@/lib/db';
import { users } from '@/lib/schema';
import { eq } from 'drizzle-orm';

export async function getUserByEmail(email: string) {
  return await db.select().from(users).where(eq(users.email, email)).limit(1);
}
```

## Common Patterns

### 1. Select with Filter

```typescript
import { db } from '@/lib/db';
import { users } from '@/lib/schema';
import { eq, and, gte } from 'drizzle-orm';

const activeUsers = await db
  .select()
  .from(users)
  .where(
    and(
      eq(users.status, 'active'),
      gte(users.createdAt, new Date('2024-01-01'))
    )
  );
```

### 2. Insert with Returning

```typescript
const [newUser] = await db
  .insert(users)
  .values({
    email: 'test@example.com',
    name: 'Test User',
  })
  .returning();
```

### 3. Update with Returning

```typescript
const [updatedUser] = await db
  .update(users)
  .set({ name: 'Updated Name' })
  .where(eq(users.id, 1))
  .returning();
```

### 4. Transaction

```typescript
await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ email, name }).returning();
  await tx.insert(profiles).values({ userId: user.id, bio });
});
```

### 5. Join Query

```typescript
const usersWithProfiles = await db
  .select({
    userId: users.id,
    userName: users.name,
    bio: profiles.bio,
  })
  .from(users)
  .leftJoin(profiles, eq(users.id, profiles.userId));
```

## Testing Requirements

All database code must have:
- Unit tests with mocked database (90%+ coverage)
- Integration tests with test database
- Transaction rollback tests
- Error handling tests
- Type safety validation

## Security Checklist

Before committing database code:
- [ ] No raw SQL with string interpolation
- [ ] All user input uses parameterized queries
- [ ] Proper indexes on foreign keys
- [ ] No `select *` in production code
- [ ] Run `python validate-queries.py` on changed files
- [ ] Transaction isolation level appropriate for use case
- [ ] Input validation before database operations

## Performance Checklist

Before committing database code:
- [ ] Select only needed fields (avoid `select *`)
- [ ] Indexes on all foreign keys
- [ ] Indexes on frequently queried columns
- [ ] No N+1 queries (use joins or batch loading)
- [ ] Batch operations for multiple inserts
- [ ] Connection pooling configured
- [ ] Query explain analysis for complex queries

## Official Resources

- **Drizzle ORM Docs**: https://orm.drizzle.team/
- **Drizzle Kit Docs**: https://orm.drizzle.team/kit-docs/overview
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Neon Docs**: https://neon.tech/docs/
- **Vercel Postgres**: https://vercel.com/docs/storage/vercel-postgres

## Migration from Prisma

If you're migrating from Prisma, see the [ADR-002-DRIZZLE-ORM-MIGRATION.md](../../../docs/decisions/ADR-002-DRIZZLE-ORM-MIGRATION.md) decision record.

Key differences:
- No client generation step (types inferred from schema)
- SQL-like query builder (not Prisma's fluent API)
- Edge Runtime compatible (Prisma 6.19.0 is not)
- Manual relation queries (no automatic includes)

## Next Steps

1. Read [queries-complete.md](./queries-complete.md) for all query patterns
2. Read [transactions.md](./transactions.md) for transaction safety
3. Read [relations.md](./relations.md) for relationship patterns
4. Run [validate-queries.py](./validate-queries.py) on your code
5. Review [common-mistakes.md](./common-mistakes.md) for pitfalls

## Support

For Drizzle-specific questions:
- GitHub Issues: https://github.com/drizzle-team/drizzle-orm/issues
- Discord: https://discord.gg/drizzle

For Quetrex-specific questions:
- Check CLAUDE.md project documentation
- Review architecture docs in `/docs/architecture/`
- Ask in team Slack channel

---

**Last Updated**: 2025-11-23 by Glen Barnhardt with help from Claude Code
