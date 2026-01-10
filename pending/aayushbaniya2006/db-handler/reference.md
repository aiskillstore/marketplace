# Database Architecture Reference

## 1. Schema Definition
**Location:** `src/db/schema/{domain}.ts`

### Standard Imports
```typescript
import { pgTable, text, timestamp, boolean, integer, jsonb, index, primaryKey } from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";
```

### Primary Keys & Timestamps
```typescript
id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),
createdAt: timestamp("createdAt", { mode: "date" }).defaultNow()
```

### JSONB with Zod (MANDATORY)
```typescript
import { z } from "zod";
export const settingsSchema = z.object({ ... });
settings: jsonb("settings").$type<z.infer<typeof settingsSchema>>()
```

## 2. Performance & Indexes
Always define indexes for Foreign Keys and filter columns.

```typescript
export const posts = pgTable("posts", {
  userId: text("userId").references(() => users.id),
  status: text("status"),
}, (t) => [
  // Index Foreign Key (Crucial for Joins)
  index("posts_user_id_idx").on(t.userId),
  // Index Filter Column
  index("posts_status_idx").on(t.status)
]);
```

## 3. Solving N+1 Queries
**Problem**: Fetching related data in a loop (1 query per item).
**Solution**: Use Relational Queries or Joins.

### Using Query Builder (Preferred)
```typescript
const usersWithPosts = await db.query.users.findMany({
  with: {
    posts: true, // Fetches posts automatically in 1 round-trip
    profile: true
  }
});
```

### Using Joins (Advanced)
```typescript
const result = await db
  .select()
  .from(users)
  .leftJoin(posts, eq(users.id, posts.userId));
```

## 4. Relations
- Use `relations` helper to enable the Query Builder syntax above.
```typescript
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));
```

## 5. Best Practices
- **Normalization**: Default to 3NF. Use JSONB only for tightly coupled data.
- **Safety**: Confirm complex changes.
- **File Org**: Group by domain. Export in `src/db/schema/index.ts`.
- **Migrations**: We use `drizzle-kit push` for prototyping/development. Do not generate migration files manually unless strictly required for production versioning.
