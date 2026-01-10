# Relationship Patterns

Comprehensive guide to defining and querying table relationships with Drizzle ORM.

## Table of Contents

- [Defining Relations](#defining-relations)
- [One-to-One Relations](#one-to-one-relations)
- [One-to-Many Relations](#one-to-many-relations)
- [Many-to-Many Relations](#many-to-many-relations)
- [Self-Referencing Relations](#self-referencing-relations)
- [Querying Relations](#querying-relations)
- [Cascading Operations](#cascading-operations)
- [Circular Relations](#circular-relations)
- [Performance Optimization](#performance-optimization)

---

## Defining Relations

Drizzle uses a separate `relations` object to define relationships between tables.

### Basic Setup

```typescript
// src/lib/schema.ts
import { pgTable, serial, text, integer, timestamp } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

// Define tables first
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const profiles = pgTable('profiles', {
  id: serial('id').primaryKey(),
  userId: integer('user_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  bio: text('bio'),
  avatar: text('avatar'),
});

// Define relations separately
export const usersRelations = relations(users, ({ one, many }) => ({
  profile: one(profiles, {
    fields: [users.id],
    references: [profiles.userId],
  }),
  orders: many(orders),
}));

export const profilesRelations = relations(profiles, ({ one }) => ({
  user: one(users, {
    fields: [profiles.userId],
    references: [users.id],
  }),
}));
```

---

## One-to-One Relations

### Schema Definition

```typescript
// Users table
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
});

// Profiles table (one per user)
export const profiles = pgTable('profiles', {
  id: serial('id').primaryKey(),
  userId: integer('user_id')
    .notNull()
    .unique() // Enforces one-to-one
    .references(() => users.id, { onDelete: 'cascade' }),
  bio: text('bio'),
  avatar: text('avatar'),
  website: text('website'),
});

// Relations
export const usersRelations = relations(users, ({ one }) => ({
  profile: one(profiles, {
    fields: [users.id],
    references: [profiles.userId],
  }),
}));

export const profilesRelations = relations(profiles, ({ one }) => ({
  user: one(users, {
    fields: [profiles.userId],
    references: [users.id],
  }),
}));
```

### Query One-to-One

```typescript
import { db } from '@/lib/db';
import { users } from '@/lib/schema';

// Query with relation
const usersWithProfiles = await db.query.users.findMany({
  with: {
    profile: true,
  },
});

// Result type:
// {
//   id: number;
//   email: string;
//   name: string;
//   profile: { id: number; bio: string; ... } | null;
// }[]
```

### Create One-to-One

```typescript
// Create user and profile together
const result = await db.transaction(async (tx) => {
  const [user] = await tx
    .insert(users)
    .values({
      email: 'test@example.com',
      name: 'Test User',
    })
    .returning();

  const [profile] = await tx
    .insert(profiles)
    .values({
      userId: user.id,
      bio: 'Hello world',
      avatar: 'https://example.com/avatar.jpg',
    })
    .returning();

  return { user, profile };
});
```

---

## One-to-Many Relations

### Schema Definition

```typescript
// Users table (one)
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
});

// Orders table (many)
export const orders = pgTable('orders', {
  id: serial('id').primaryKey(),
  userId: integer('user_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  total: numeric('total', { precision: 10, scale: 2 }).notNull(),
  status: text('status').notNull().default('pending'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

// Relations
export const usersRelations = relations(users, ({ many }) => ({
  orders: many(orders),
}));

export const ordersRelations = relations(orders, ({ one }) => ({
  user: one(users, {
    fields: [orders.userId],
    references: [users.id],
  }),
}));
```

### Query One-to-Many

```typescript
// Get users with all their orders
const usersWithOrders = await db.query.users.findMany({
  with: {
    orders: true,
  },
});

// Result type:
// {
//   id: number;
//   email: string;
//   name: string;
//   orders: Array<{ id: number; total: string; status: string; ... }>;
// }[]

// Get user with filtered orders
const userWithRecentOrders = await db.query.users.findFirst({
  where: eq(users.id, 1),
  with: {
    orders: {
      where: eq(orders.status, 'completed'),
      orderBy: desc(orders.createdAt),
      limit: 10,
    },
  },
});
```

### Create One-to-Many

```typescript
// Create user with multiple orders
const result = await db.transaction(async (tx) => {
  const [user] = await tx
    .insert(users)
    .values({
      email: 'test@example.com',
      name: 'Test User',
    })
    .returning();

  const orders = await tx
    .insert(orders)
    .values([
      { userId: user.id, total: '99.99', status: 'pending' },
      { userId: user.id, total: '149.99', status: 'completed' },
      { userId: user.id, total: '29.99', status: 'pending' },
    ])
    .returning();

  return { user, orders };
});
```

---

## Many-to-Many Relations

### Schema Definition

```typescript
// Students table
export const students = pgTable('students', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
});

// Courses table
export const courses = pgTable('courses', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  code: text('code').notNull().unique(),
});

// Junction table (enrollments)
export const enrollments = pgTable('enrollments', {
  id: serial('id').primaryKey(),
  studentId: integer('student_id')
    .notNull()
    .references(() => students.id, { onDelete: 'cascade' }),
  courseId: integer('course_id')
    .notNull()
    .references(() => courses.id, { onDelete: 'cascade' }),
  enrolledAt: timestamp('enrolled_at').defaultNow().notNull(),
  grade: text('grade'),
});

// Relations
export const studentsRelations = relations(students, ({ many }) => ({
  enrollments: many(enrollments),
}));

export const coursesRelations = relations(courses, ({ many }) => ({
  enrollments: many(enrollments),
}));

export const enrollmentsRelations = relations(enrollments, ({ one }) => ({
  student: one(students, {
    fields: [enrollments.studentId],
    references: [students.id],
  }),
  course: one(courses, {
    fields: [enrollments.courseId],
    references: [courses.id],
  }),
}));
```

### Query Many-to-Many

```typescript
// Get students with their courses
const studentsWithCourses = await db.query.students.findMany({
  with: {
    enrollments: {
      with: {
        course: true,
      },
    },
  },
});

// Result type:
// {
//   id: number;
//   name: string;
//   email: string;
//   enrollments: Array<{
//     id: number;
//     enrolledAt: Date;
//     grade: string | null;
//     course: { id: number; name: string; code: string };
//   }>;
// }[]

// Get courses with enrolled students
const coursesWithStudents = await db.query.courses.findMany({
  with: {
    enrollments: {
      with: {
        student: true,
      },
    },
  },
});
```

### Create Many-to-Many

```typescript
// Enroll student in multiple courses
const studentId = 1;
const courseIds = [101, 102, 103];

await db.insert(enrollments).values(
  courseIds.map((courseId) => ({
    studentId,
    courseId,
  }))
);

// Enroll multiple students in a course
const courseId = 101;
const studentIds = [1, 2, 3, 4, 5];

await db.insert(enrollments).values(
  studentIds.map((studentId) => ({
    studentId,
    courseId,
  }))
);
```

### Query Many-to-Many with Filters

```typescript
// Get students enrolled in specific course
const courseStudents = await db.query.courses.findFirst({
  where: eq(courses.code, 'CS101'),
  with: {
    enrollments: {
      where: isNotNull(enrollments.grade), // Only graded enrollments
      with: {
        student: true,
      },
      orderBy: desc(enrollments.enrolledAt),
    },
  },
});

// Get students with high grades
const topStudents = await db.query.students.findMany({
  with: {
    enrollments: {
      where: inArray(enrollments.grade, ['A', 'A+']),
      with: {
        course: true,
      },
    },
  },
});
```

---

## Self-Referencing Relations

### Schema Definition (Tree Structure)

```typescript
// Categories with parent-child relationship
export const categories = pgTable('categories', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  parentId: integer('parent_id').references(() => categories.id, {
    onDelete: 'set null',
  }),
});

// Relations
export const categoriesRelations = relations(categories, ({ one, many }) => ({
  parent: one(categories, {
    fields: [categories.parentId],
    references: [categories.id],
    relationName: 'categoryHierarchy',
  }),
  children: many(categories, {
    relationName: 'categoryHierarchy',
  }),
}));
```

### Schema Definition (User Referrals)

```typescript
// Users who can refer other users
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  referrerId: integer('referrer_id').references(() => users.id, {
    onDelete: 'set null',
  }),
});

// Relations
export const usersRelations = relations(users, ({ one, many }) => ({
  referrer: one(users, {
    fields: [users.referrerId],
    references: [users.id],
    relationName: 'userReferrals',
  }),
  referrals: many(users, {
    relationName: 'userReferrals',
  }),
}));
```

### Query Self-Referencing

```typescript
// Get category with parent and children
const categoryTree = await db.query.categories.findFirst({
  where: eq(categories.id, 5),
  with: {
    parent: true,
    children: true,
  },
});

// Result:
// {
//   id: 5;
//   name: 'Electronics';
//   parentId: 1;
//   parent: { id: 1; name: 'Products'; parentId: null };
//   children: [
//     { id: 10; name: 'Laptops'; parentId: 5 },
//     { id: 11; name: 'Phones'; parentId: 5 }
//   ];
// }

// Get user with referrer and referrals
const userWithNetwork = await db.query.users.findFirst({
  where: eq(users.id, 1),
  with: {
    referrer: true,
    referrals: true,
  },
});
```

### Create Tree Structure

```typescript
// Create category hierarchy
const result = await db.transaction(async (tx) => {
  // Root category
  const [root] = await tx
    .insert(categories)
    .values({ name: 'All Products' })
    .returning();

  // Child categories
  const [electronics] = await tx
    .insert(categories)
    .values({ name: 'Electronics', parentId: root.id })
    .returning();

  const [clothing] = await tx
    .insert(categories)
    .values({ name: 'Clothing', parentId: root.id })
    .returning();

  // Grandchild categories
  await tx.insert(categories).values([
    { name: 'Laptops', parentId: electronics.id },
    { name: 'Phones', parentId: electronics.id },
    { name: 'Shirts', parentId: clothing.id },
    { name: 'Pants', parentId: clothing.id },
  ]);

  return { root, electronics, clothing };
});
```

---

## Querying Relations

### Basic With Clause

```typescript
// Single level relation
const users = await db.query.users.findMany({
  with: {
    profile: true,
  },
});

// Multiple relations
const users = await db.query.users.findMany({
  with: {
    profile: true,
    orders: true,
  },
});
```

### Nested Relations

```typescript
// Two levels deep
const users = await db.query.users.findMany({
  with: {
    orders: {
      with: {
        orderItems: true,
      },
    },
  },
});

// Three levels deep
const users = await db.query.users.findMany({
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
```

### Filtered Relations

```typescript
// Filter related records
const users = await db.query.users.findMany({
  with: {
    orders: {
      where: eq(orders.status, 'completed'),
      orderBy: desc(orders.createdAt),
      limit: 5,
    },
  },
});

// Complex filters
const users = await db.query.users.findMany({
  with: {
    orders: {
      where: and(
        eq(orders.status, 'completed'),
        gte(orders.total, '100.00'),
        gte(orders.createdAt, new Date('2024-01-01'))
      ),
      orderBy: [desc(orders.total), desc(orders.createdAt)],
      limit: 10,
    },
  },
});
```

### Partial Field Selection

```typescript
// Select specific fields from relations
const users = await db.query.users.findMany({
  columns: {
    id: true,
    name: true,
    email: true,
  },
  with: {
    profile: {
      columns: {
        bio: true,
        avatar: true,
      },
    },
    orders: {
      columns: {
        id: true,
        total: true,
        status: true,
      },
      limit: 5,
    },
  },
});
```

### Excluding Fields

```typescript
// Exclude sensitive fields
const users = await db.query.users.findMany({
  columns: {
    passwordHash: false, // Exclude password
  },
  with: {
    profile: {
      columns: {
        privateNotes: false, // Exclude private notes
      },
    },
  },
});
```

---

## Cascading Operations

### On Delete Cascade

```typescript
// When user is deleted, profile is automatically deleted
export const profiles = pgTable('profiles', {
  id: serial('id').primaryKey(),
  userId: integer('user_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  bio: text('bio'),
});

// Delete user (profile is automatically deleted)
await db.delete(users).where(eq(users.id, 1));
```

### On Delete Set Null

```typescript
// When user is deleted, posts remain but authorId becomes null
export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  authorId: integer('author_id').references(() => users.id, {
    onDelete: 'set null',
  }),
});

// Delete user (posts remain with authorId = null)
await db.delete(users).where(eq(users.id, 1));
```

### On Delete Restrict

```typescript
// Prevent deletion if related records exist
export const orders = pgTable('orders', {
  id: serial('id').primaryKey(),
  userId: integer('user_id')
    .notNull()
    .references(() => users.id, { onDelete: 'restrict' }),
});

// This will fail if user has orders
try {
  await db.delete(users).where(eq(users.id, 1));
} catch (error) {
  console.error('Cannot delete user with existing orders');
}
```

### On Delete Set Default

```typescript
// When user is deleted, use default value
export const comments = pgTable('comments', {
  id: serial('id').primaryKey(),
  content: text('content').notNull(),
  authorId: integer('author_id')
    .notNull()
    .default(0) // Default to system user
    .references(() => users.id, { onDelete: 'set default' }),
});
```

### Manual Cascade with Transaction

```typescript
// Custom cascade logic
async function deleteUserWithOrders(userId: number) {
  await db.transaction(async (tx) => {
    // 1. Delete order items
    await tx
      .delete(orderItems)
      .where(
        inArray(
          orderItems.orderId,
          tx.select({ id: orders.id }).from(orders).where(eq(orders.userId, userId))
        )
      );

    // 2. Delete orders
    await tx.delete(orders).where(eq(orders.userId, userId));

    // 3. Delete profile
    await tx.delete(profiles).where(eq(profiles.userId, userId));

    // 4. Delete user
    await tx.delete(users).where(eq(users.id, userId));
  });
}
```

---

## Circular Relations

### Schema with Circular Dependencies

```typescript
// Users and Teams with circular relationship
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  teamId: integer('team_id'), // References teams
});

export const teams = pgTable('teams', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  leaderId: integer('leader_id'), // References users
});

// Add foreign keys after both tables are defined
export const usersWithFK = pgTable(
  'users',
  {
    id: serial('id').primaryKey(),
    name: text('name').notNull(),
    teamId: integer('team_id').references(() => teams.id),
  }
);

export const teamsWithFK = pgTable(
  'teams',
  {
    id: serial('id').primaryKey(),
    name: text('name').notNull(),
    leaderId: integer('leader_id').references(() => users.id),
  }
);

// Relations
export const usersRelations = relations(users, ({ one, many }) => ({
  team: one(teams, {
    fields: [users.teamId],
    references: [teams.id],
  }),
  ledTeams: many(teams),
}));

export const teamsRelations = relations(teams, ({ one, many }) => ({
  leader: one(users, {
    fields: [teams.leaderId],
    references: [users.id],
  }),
  members: many(users),
}));
```

### Query Circular Relations

```typescript
// Get team with leader and members
const team = await db.query.teams.findFirst({
  where: eq(teams.id, 1),
  with: {
    leader: true,
    members: true,
  },
});

// Get user with their team and teams they lead
const user = await db.query.users.findFirst({
  where: eq(users.id, 1),
  with: {
    team: true,
    ledTeams: true,
  },
});
```

---

## Performance Optimization

### N+1 Query Problem

```typescript
// ❌ BAD: N+1 queries
const users = await db.select().from(users);
for (const user of users) {
  const orders = await db
    .select()
    .from(orders)
    .where(eq(orders.userId, user.id)); // N additional queries!
  console.log(`User ${user.name} has ${orders.length} orders`);
}

// ✅ GOOD: Single query with join
const usersWithOrders = await db.query.users.findMany({
  with: {
    orders: true,
  },
});

for (const user of usersWithOrders) {
  console.log(`User ${user.name} has ${user.orders.length} orders`);
}
```

### Batch Loading

```typescript
// Load all orders for multiple users at once
const userIds = [1, 2, 3, 4, 5];

const orders = await db
  .select()
  .from(orders)
  .where(inArray(orders.userId, userIds));

// Group by userId
const ordersByUser = orders.reduce((acc, order) => {
  if (!acc[order.userId]) acc[order.userId] = [];
  acc[order.userId].push(order);
  return acc;
}, {} as Record<number, typeof orders>);
```

### Limit Nested Relations

```typescript
// ❌ BAD: Load all orders (could be thousands)
const users = await db.query.users.findMany({
  with: {
    orders: true, // All orders
  },
});

// ✅ GOOD: Limit nested data
const users = await db.query.users.findMany({
  with: {
    orders: {
      orderBy: desc(orders.createdAt),
      limit: 5, // Only recent 5 orders
    },
  },
});
```

### Use Indexes on Foreign Keys

```typescript
// Add indexes for better join performance
export const orders = pgTable(
  'orders',
  {
    id: serial('id').primaryKey(),
    userId: integer('user_id')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    total: numeric('total', { precision: 10, scale: 2 }).notNull(),
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => ({
    // Index on foreign key for faster joins
    userIdIdx: index('orders_user_id_idx').on(table.userId),
    // Composite index for common queries
    userStatusIdx: index('orders_user_status_idx').on(table.userId, table.status),
  })
);
```

### Pagination for Large Relations

```typescript
// Paginate related data
async function getUserOrders(userId: number, page: number, pageSize: number) {
  return await db.query.users.findFirst({
    where: eq(users.id, userId),
    with: {
      orders: {
        orderBy: desc(orders.createdAt),
        limit: pageSize,
        offset: (page - 1) * pageSize,
      },
    },
  });
}

// Usage
const userWithOrders = await getUserOrders(1, 2, 20); // Page 2, 20 per page
```

---

## Testing Relations

```typescript
import { describe, it, expect, beforeEach } from 'vitest';

describe('User Relations', () => {
  beforeEach(async () => {
    // Clear tables
    await db.delete(profiles);
    await db.delete(orders);
    await db.delete(users);
  });

  it('should load user with profile', async () => {
    // Arrange
    const [user] = await db
      .insert(users)
      .values({ email: 'test@example.com', name: 'Test' })
      .returning();

    await db.insert(profiles).values({ userId: user.id, bio: 'Hello' });

    // Act
    const result = await db.query.users.findFirst({
      where: eq(users.id, user.id),
      with: { profile: true },
    });

    // Assert
    expect(result).toBeDefined();
    expect(result?.profile).toBeDefined();
    expect(result?.profile?.bio).toBe('Hello');
  });

  it('should cascade delete profile when user is deleted', async () => {
    // Arrange
    const [user] = await db
      .insert(users)
      .values({ email: 'test@example.com', name: 'Test' })
      .returning();

    const [profile] = await db
      .insert(profiles)
      .values({ userId: user.id, bio: 'Hello' })
      .returning();

    // Act
    await db.delete(users).where(eq(users.id, user.id));

    // Assert
    const profileStillExists = await db
      .select()
      .from(profiles)
      .where(eq(profiles.id, profile.id));

    expect(profileStillExists).toHaveLength(0);
  });
});
```

---

**Official Docs**: https://orm.drizzle.team/docs/rqb
**Next**: [migrations.md](./migrations.md) for schema evolution patterns
