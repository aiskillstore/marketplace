---
name: drizzle-patterns
description: Drizzle ORM patterns for PostgreSQL.
---

# Drizzle ORM Patterns

## Schema Definition

```typescript
// db/schema/users.ts
import { pgTable, uuid, varchar, timestamp, boolean } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  name: varchar('name', { length: 255 }),
  emailVerified: boolean('email_verified').default(false),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
```

## Relations

```typescript
// db/schema/relations.ts
import { relations } from 'drizzle-orm';
import { users } from './users';
import { posts } from './posts';

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}));
```

## Database Client

```typescript
// db/index.ts
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from './schema';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const db = drizzle(pool, { schema });
```

## Queries

```typescript
import { eq, and, or, like, desc, asc } from 'drizzle-orm';

// Find one
const user = await db.query.users.findFirst({
  where: eq(users.id, userId),
});

// Find many with relations
const usersWithPosts = await db.query.users.findMany({
  with: { posts: true },
  where: eq(users.emailVerified, true),
  orderBy: [desc(users.createdAt)],
  limit: 10,
});

// Complex where
const results = await db.query.posts.findMany({
  where: and(
    eq(posts.published, true),
    or(
      like(posts.title, '%search%'),
      like(posts.content, '%search%')
    )
  ),
});
```

## Mutations

```typescript
// Insert
const [newUser] = await db.insert(users).values({
  email: 'test@example.com',
  name: 'Test User',
}).returning();

// Insert many
await db.insert(users).values([
  { email: 'user1@example.com', name: 'User 1' },
  { email: 'user2@example.com', name: 'User 2' },
]);

// Update
await db.update(users)
  .set({ name: 'New Name', updatedAt: new Date() })
  .where(eq(users.id, userId));

// Delete
await db.delete(users)
  .where(eq(users.id, userId));
```

## Transactions

```typescript
await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values(userData).returning();
  await tx.insert(profiles).values({ userId: user.id, ...profileData });
  await tx.insert(settings).values({ userId: user.id, ...defaultSettings });
});
```

## Migrations

```bash
# Generate migration
pnpm drizzle-kit generate

# Push to database
pnpm drizzle-kit push

# Open Drizzle Studio
pnpm drizzle-kit studio
```

## drizzle.config.ts

```typescript
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './db/schema/index.ts',
  out: './db/migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});
```
