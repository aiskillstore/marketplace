# TypeScript Type Inference Patterns

Comprehensive guide to TypeScript type safety with Drizzle ORM.

## Table of Contents

- [Schema Type Inference](#schema-type-inference)
- [Query Result Types](#query-result-types)
- [Insert and Update Types](#insert-and-update-types)
- [Relation Types](#relation-types)
- [Custom Type Mappings](#custom-type-mappings)
- [Type-Safe Query Builders](#type-safe-query-builders)
- [Generic Database Functions](#generic-database-functions)

---

## Schema Type Inference

### InferSelectModel

```typescript
// Schema definition
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  age: integer('age'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

// Infer type from schema
export type User = typeof users.$inferSelect;

// Equivalent to:
type User = {
  id: number;
  email: string;
  name: string;
  age: number | null;
  createdAt: Date;
};

// Usage
function processUser(user: User) {
  console.log(user.name); // Type-safe!
  console.log(user.age?.toString()); // Handles nullable
}
```

### InferInsertModel

```typescript
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  age: integer('age'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

// Infer insert type (excludes auto-generated fields)
export type NewUser = typeof users.$inferInsert;

// Equivalent to:
type NewUser = {
  id?: number; // Optional (auto-generated)
  email: string;
  name: string;
  age?: number | null;
  createdAt?: Date; // Optional (has default)
};

// Usage
async function createUser(data: NewUser) {
  const [user] = await db.insert(users).values(data).returning();
  return user;
}

// Valid calls
await createUser({
  email: 'test@example.com',
  name: 'Test User',
});

await createUser({
  email: 'test@example.com',
  name: 'Test User',
  age: 25,
  createdAt: new Date(),
});
```

### Partial Types

```typescript
// For update operations (all fields optional)
type UpdateUser = Partial<typeof users.$inferInsert>;

// Usage
async function updateUser(id: number, data: UpdateUser) {
  await db
    .update(users)
    .set(data)
    .where(eq(users.id, id));
}

// Valid calls
await updateUser(1, { name: 'New Name' });
await updateUser(1, { age: 30 });
await updateUser(1, { name: 'New Name', age: 30 });
```

### Required Types

```typescript
// Make all fields required
type CompleteUser = Required<typeof users.$inferInsert>;

// Usage
function validateCompleteUser(data: CompleteUser) {
  // All fields must be present
  console.log(data.id);
  console.log(data.email);
  console.log(data.name);
  console.log(data.age);
  console.log(data.createdAt);
}
```

---

## Query Result Types

### Select Query Types

```typescript
// Infer type from select query
const users = await db
  .select({
    id: users.id,
    name: users.name,
    email: users.email,
  })
  .from(users);

// Type is automatically inferred:
// { id: number; name: string; email: string }[]

// Extract type
type UserSummary = (typeof users)[0];

// Or use type helper
type UserSummaryAlt = Awaited<ReturnType<typeof getUserSummary>>[0];

async function getUserSummary() {
  return await db
    .select({
      id: users.id,
      name: users.name,
      email: users.email,
    })
    .from(users);
}
```

### Join Query Types

```typescript
const usersWithProfiles = await db
  .select({
    userId: users.id,
    userName: users.name,
    bio: profiles.bio,
    avatar: profiles.avatar,
  })
  .from(users)
  .leftJoin(profiles, eq(users.id, profiles.userId));

// Inferred type:
type UserWithProfile = (typeof usersWithProfiles)[0];
// {
//   userId: number;
//   userName: string;
//   bio: string | null;
//   avatar: string | null;
// }
```

### Aggregation Types

```typescript
const orderStats = await db
  .select({
    userId: orders.userId,
    totalOrders: count(orders.id),
    totalSpent: sum(orders.total),
    avgOrderValue: avg(orders.total),
  })
  .from(orders)
  .groupBy(orders.userId);

// Inferred type:
type OrderStats = (typeof orderStats)[0];
// {
//   userId: number;
//   totalOrders: number;
//   totalSpent: string | null; // sum returns string for numeric types
//   avgOrderValue: string | null;
// }
```

---

## Insert and Update Types

### Type-Safe Insert

```typescript
// Schema
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  role: text('role').$type<'user' | 'admin' | 'moderator'>().notNull().default('user'),
});

// Insert type
type NewUser = typeof users.$inferInsert;

// Type-safe insert
async function createUser(data: NewUser) {
  // TypeScript enforces correct types
  const [user] = await db
    .insert(users)
    .values({
      email: data.email, // Type: string
      name: data.name, // Type: string
      role: data.role, // Type: 'user' | 'admin' | 'moderator'
    })
    .returning();

  return user;
}

// ✅ Valid
await createUser({
  email: 'test@example.com',
  name: 'Test User',
  role: 'admin',
});

// ❌ Type error: role must be 'user' | 'admin' | 'moderator'
await createUser({
  email: 'test@example.com',
  name: 'Test User',
  role: 'superuser', // Error!
});
```

### Type-Safe Update

```typescript
type UpdateUser = Partial<typeof users.$inferInsert>;

async function updateUser(id: number, data: UpdateUser) {
  const [updated] = await db
    .update(users)
    .set(data) // Type-safe: only valid fields allowed
    .where(eq(users.id, id))
    .returning();

  return updated;
}

// ✅ Valid
await updateUser(1, { name: 'New Name' });
await updateUser(1, { role: 'admin' });

// ❌ Type error: 'invalidField' doesn't exist
await updateUser(1, { invalidField: 'value' }); // Error!
```

### Validated Insert Types

```typescript
import { z } from 'zod';

// Zod schema for validation
const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(120).optional(),
});

// Infer type from Zod schema
type CreateUserInput = z.infer<typeof createUserSchema>;

// Type-safe validated insert
async function createValidatedUser(input: unknown) {
  // Validate input
  const data = createUserSchema.parse(input);

  // data is now type-safe
  const [user] = await db
    .insert(users)
    .values(data)
    .returning();

  return user;
}
```

---

## Relation Types

### One-to-One Relation Types

```typescript
// Schema
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
});

export const profiles = pgTable('profiles', {
  id: serial('id').primaryKey(),
  userId: integer('user_id')
    .notNull()
    .unique()
    .references(() => users.id),
  bio: text('bio'),
});

// Relations
export const usersRelations = relations(users, ({ one }) => ({
  profile: one(profiles, {
    fields: [users.id],
    references: [profiles.userId],
  }),
}));

// Query with relation
const userWithProfile = await db.query.users.findFirst({
  with: {
    profile: true,
  },
});

// Inferred type:
type UserWithProfile = typeof userWithProfile;
// {
//   id: number;
//   name: string;
//   profile: { id: number; userId: number; bio: string | null } | null;
// }
```

### One-to-Many Relation Types

```typescript
export const usersRelations = relations(users, ({ many }) => ({
  orders: many(orders),
}));

const userWithOrders = await db.query.users.findFirst({
  with: {
    orders: true,
  },
});

// Inferred type:
type UserWithOrders = typeof userWithOrders;
// {
//   id: number;
//   name: string;
//   orders: Array<{ id: number; userId: number; total: string; ... }>;
// }
```

### Nested Relation Types

```typescript
const userWithOrdersAndItems = await db.query.users.findFirst({
  with: {
    orders: {
      with: {
        orderItems: {
          with: {
            product: true,
          },
        },
      },
    },
  },
});

// Inferred type (deeply nested):
type UserWithOrdersAndItems = typeof userWithOrdersAndItems;
// {
//   id: number;
//   name: string;
//   orders: Array<{
//     id: number;
//     userId: number;
//     orderItems: Array<{
//       id: number;
//       orderId: number;
//       product: { id: number; name: string; price: string };
//     }>;
//   }>;
// }
```

---

## Custom Type Mappings

### Enum Types

```typescript
import { pgEnum } from 'drizzle-orm/pg-core';

// Define enum
export const userRoleEnum = pgEnum('user_role', ['user', 'admin', 'moderator']);

// Use in schema
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  role: userRoleEnum('role').notNull().default('user'),
});

// Inferred type includes enum
type User = typeof users.$inferSelect;
// {
//   id: number;
//   role: 'user' | 'admin' | 'moderator';
// }
```

### JSON Types

```typescript
// Define JSON type
type UserSettings = {
  theme: 'light' | 'dark';
  notifications: boolean;
  language: string;
};

// Use in schema
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  settings: jsonb('settings').$type<UserSettings>().notNull().default({
    theme: 'light',
    notifications: true,
    language: 'en',
  }),
});

// Inferred type
type User = typeof users.$inferSelect;
// {
//   id: number;
//   settings: UserSettings;
// }

// Type-safe access
const user = await db.query.users.findFirst();
console.log(user.settings.theme); // Type: 'light' | 'dark'
console.log(user.settings.notifications); // Type: boolean
```

### Array Types

```typescript
import { text } from 'drizzle-orm/pg-core';

export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  tags: text('tags').array().notNull().default([]),
});

// Inferred type
type Post = typeof posts.$inferSelect;
// {
//   id: number;
//   tags: string[];
// }
```

### Custom Scalar Types

```typescript
// Custom UUID type
import { customType } from 'drizzle-orm/pg-core';

const uuid = customType<{ data: string }>({
  dataType() {
    return 'uuid';
  },
});

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
});

// Inferred type
type User = typeof users.$inferSelect;
// {
//   id: string; // UUID as string
//   email: string;
// }
```

---

## Type-Safe Query Builders

### Type-Safe Where Clauses

```typescript
import { eq, and, or, gt, lt } from 'drizzle-orm';

// Type-safe filters
type UserFilter = {
  email?: string;
  minAge?: number;
  maxAge?: number;
  status?: 'active' | 'inactive';
};

async function findUsers(filter: UserFilter) {
  const conditions = [];

  if (filter.email) {
    conditions.push(eq(users.email, filter.email));
  }

  if (filter.minAge !== undefined) {
    conditions.push(gt(users.age, filter.minAge));
  }

  if (filter.maxAge !== undefined) {
    conditions.push(lt(users.age, filter.maxAge));
  }

  if (filter.status) {
    conditions.push(eq(users.status, filter.status));
  }

  return await db
    .select()
    .from(users)
    .where(conditions.length > 0 ? and(...conditions) : undefined);
}
```

### Type-Safe Sorting

```typescript
import { asc, desc } from 'drizzle-orm';

type SortField = keyof typeof users.$inferSelect;
type SortDirection = 'asc' | 'desc';

async function findUsersWithSort(
  sortField: SortField,
  sortDirection: SortDirection
) {
  const orderBy = sortDirection === 'asc'
    ? asc(users[sortField])
    : desc(users[sortField]);

  return await db
    .select()
    .from(users)
    .orderBy(orderBy);
}

// ✅ Valid
await findUsersWithSort('name', 'asc');
await findUsersWithSort('createdAt', 'desc');

// ❌ Type error: 'invalidField' is not a valid field
await findUsersWithSort('invalidField', 'asc'); // Error!
```

---

## Generic Database Functions

### Generic CRUD Functions

```typescript
import { PgTable } from 'drizzle-orm/pg-core';

// Generic find by ID
async function findById<T extends PgTable>(
  table: T,
  id: number
): Promise<typeof table.$inferSelect | undefined> {
  const [result] = await db
    .select()
    .from(table)
    .where(eq(table.id, id))
    .limit(1);

  return result;
}

// Usage
const user = await findById(users, 1); // Type: User | undefined
const order = await findById(orders, 123); // Type: Order | undefined

// Generic create
async function create<T extends PgTable>(
  table: T,
  data: typeof table.$inferInsert
): Promise<typeof table.$inferSelect> {
  const [result] = await db
    .insert(table)
    .values(data)
    .returning();

  return result;
}

// Usage
const newUser = await create(users, {
  email: 'test@example.com',
  name: 'Test User',
});
```

### Generic Pagination

```typescript
type PaginationParams = {
  page: number;
  pageSize: number;
};

type PaginatedResult<T> = {
  data: T[];
  page: number;
  pageSize: number;
  totalPages: number;
  totalCount: number;
};

async function paginate<T extends PgTable>(
  table: T,
  params: PaginationParams
): Promise<PaginatedResult<typeof table.$inferSelect>> {
  const { page, pageSize } = params;

  // Get total count
  const [{ count: totalCount }] = await db
    .select({ count: count() })
    .from(table);

  // Get paginated data
  const data = await db
    .select()
    .from(table)
    .limit(pageSize)
    .offset((page - 1) * pageSize);

  return {
    data,
    page,
    pageSize,
    totalPages: Math.ceil(totalCount / pageSize),
    totalCount,
  };
}

// Usage
const result = await paginate(users, { page: 1, pageSize: 20 });
// Type: PaginatedResult<User>
```

---

## Type Safety Best Practices

### 1. Always Use Inferred Types

```typescript
// ✅ GOOD: Use inferred types
type User = typeof users.$inferSelect;
type NewUser = typeof users.$inferInsert;

// ❌ BAD: Manually define types (can drift from schema)
type UserBad = {
  id: number;
  email: string;
  name: string;
  // Easy to forget new fields!
};
```

### 2. Extract Types for Reuse

```typescript
// src/lib/schema.ts
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
});

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
export type UpdateUser = Partial<NewUser>;

// Use everywhere
import { User, NewUser, UpdateUser } from '@/lib/schema';
```

### 3. Type-Safe API Responses

```typescript
import { z } from 'zod';

// Schema for API response
const userResponseSchema = z.object({
  id: z.number(),
  email: z.string(),
  name: z.string(),
  createdAt: z.date().transform((date) => date.toISOString()),
});

type UserResponse = z.infer<typeof userResponseSchema>;

// Type-safe API handler
export async function GET(request: Request): Promise<Response> {
  const users = await db.select().from(users);

  // Validate response shape
  const response: UserResponse[] = users.map((user) =>
    userResponseSchema.parse(user)
  );

  return Response.json(response);
}
```

### 4. Use Zod for Runtime Validation

```typescript
import { z } from 'zod';

// Schema matches database schema
const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(120).optional(),
});

// Type inferred from Zod
type CreateUserInput = z.infer<typeof createUserSchema>;

// Matches database insert type
type NewUser = typeof users.$inferInsert;

// Ensure compatibility
const _typeCheck: CreateUserInput = {} as NewUser;
```

---

## Testing Type Safety

```typescript
import { describe, it, expectTypeOf } from 'vitest';

describe('Type Safety', () => {
  it('should infer correct select type', () => {
    type User = typeof users.$inferSelect;

    expectTypeOf<User>().toHaveProperty('id');
    expectTypeOf<User>().toHaveProperty('email');
    expectTypeOf<User>().toHaveProperty('name');

    expectTypeOf<User['id']>().toBeNumber();
    expectTypeOf<User['email']>().toBeString();
  });

  it('should infer correct insert type', () => {
    type NewUser = typeof users.$inferInsert;

    expectTypeOf<NewUser>().toHaveProperty('email');
    expectTypeOf<NewUser>().toHaveProperty('name');

    // id is optional (auto-generated)
    expectTypeOf<NewUser['id']>().toEqualTypeOf<number | undefined>();
  });
});
```

---

**Official Docs**: https://orm.drizzle.team/docs/goodies#type-api
**Next**: [common-mistakes.md](./common-mistakes.md) for pitfalls and fixes
