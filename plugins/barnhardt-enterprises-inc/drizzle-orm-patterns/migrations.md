# Migration Patterns

Comprehensive guide to schema evolution and data migrations with Drizzle Kit.

## Table of Contents

- [Migration Basics](#migration-basics)
- [Schema Changes](#schema-changes)
- [Data Migrations](#data-migrations)
- [Zero-Downtime Deployments](#zero-downtime-deployments)
- [Rollback Strategies](#rollback-strategies)
- [Migration Testing](#migration-testing)
- [Common Migration Scenarios](#common-migration-scenarios)

---

## Migration Basics

### Initial Setup

```typescript
// drizzle.config.ts
import type { Config } from 'drizzle-kit';

export default {
  schema: './src/lib/schema.ts',
  out: './drizzle/migrations',
  driver: 'pg',
  dbCredentials: {
    connectionString: process.env.DATABASE_URL!,
  },
} satisfies Config;
```

### Generate Migration

```bash
# Generate migration from schema changes
npx drizzle-kit generate:pg

# This creates a SQL file in drizzle/migrations/
# Example: 0001_curved_silver_fox.sql
```

### Apply Migration

```bash
# Apply all pending migrations
npx drizzle-kit push:pg

# Or run migrations programmatically
npm run db:migrate
```

### Migration Script

```typescript
// src/scripts/migrate.ts
import { drizzle } from 'drizzle-orm/neon-http';
import { migrate } from 'drizzle-orm/neon-http/migrator';
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL!);
const db = drizzle(sql);

async function runMigrations() {
  console.log('Running migrations...');

  await migrate(db, {
    migrationsFolder: './drizzle/migrations',
  });

  console.log('Migrations complete!');
  process.exit(0);
}

runMigrations().catch((err) => {
  console.error('Migration failed!', err);
  process.exit(1);
});
```

---

## Schema Changes

### Adding a Column

```typescript
// Before
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
});

// After: Add phone column
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  phone: text('phone'), // New nullable column
});

// Generated migration:
// ALTER TABLE "users" ADD COLUMN "phone" text;
```

### Adding a Required Column with Default

```typescript
// Before
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
});

// After: Add status column (required)
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  status: text('status').notNull().default('active'), // Default for existing rows
});

// Generated migration:
// ALTER TABLE "users" ADD COLUMN "status" text NOT NULL DEFAULT 'active';
```

### Renaming a Column

```typescript
// Step 1: Add new column
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  fullName: text('full_name').notNull(), // New column
  name: text('name').notNull(), // Keep old for now
});

// Generate migration 1
// npx drizzle-kit generate:pg

// Step 2: Data migration (copy data)
// See "Data Migrations" section

// Step 3: Remove old column
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  fullName: text('full_name').notNull(),
  // name removed
});

// Generate migration 2
// npx drizzle-kit generate:pg
```

### Changing Column Type

```typescript
// Before
export const products = pgTable('products', {
  id: serial('id').primaryKey(),
  price: integer('price').notNull(), // Cents as integer
});

// After: Change to decimal
export const products = pgTable('products', {
  id: serial('id').primaryKey(),
  price: numeric('price', { precision: 10, scale: 2 }).notNull(), // Dollars as decimal
});

// Generated migration:
// ALTER TABLE "products" ALTER COLUMN "price" SET DATA TYPE numeric(10, 2);

// Note: May require data migration if conversion isn't automatic
```

### Adding an Index

```typescript
// Before
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

// After: Add index on createdAt
export const users = pgTable(
  'users',
  {
    id: serial('id').primaryKey(),
    email: text('email').notNull().unique(),
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => ({
    createdAtIdx: index('users_created_at_idx').on(table.createdAt),
  })
);

// Generated migration:
// CREATE INDEX "users_created_at_idx" ON "users" ("created_at");
```

### Adding a Foreign Key

```typescript
// Before
export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  authorId: integer('author_id').notNull(), // No FK constraint
});

// After: Add foreign key
export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  authorId: integer('author_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
});

// Generated migration:
// ALTER TABLE "posts" ADD CONSTRAINT "posts_author_id_users_id_fk"
//   FOREIGN KEY ("author_id") REFERENCES "users"("id") ON DELETE CASCADE;
```

### Removing a Column

```typescript
// Before
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  legacyField: text('legacy_field'), // To be removed
});

// After: Remove column
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  // legacyField removed
});

// Generated migration:
// ALTER TABLE "users" DROP COLUMN "legacy_field";
```

---

## Data Migrations

### Simple Data Update

```typescript
// Migration: 0003_update_user_status.ts
import { sql } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/neon-http';
import { neon } from '@neondatabase/serverless';

export async function up() {
  const connection = neon(process.env.DATABASE_URL!);
  const db = drizzle(connection);

  // Update all users without status to 'active'
  await db.execute(sql`
    UPDATE users
    SET status = 'active'
    WHERE status IS NULL
  `);
}

export async function down() {
  const connection = neon(process.env.DATABASE_URL!);
  const db = drizzle(connection);

  // Rollback: Set status back to NULL
  await db.execute(sql`
    UPDATE users
    SET status = NULL
    WHERE status = 'active'
  `);
}
```

### Complex Data Transformation

```typescript
// Migration: 0004_split_full_name.ts
import { sql } from 'drizzle-orm';

export async function up() {
  const db = drizzle(neon(process.env.DATABASE_URL!));

  // Split full_name into first_name and last_name
  await db.execute(sql`
    UPDATE users
    SET
      first_name = SPLIT_PART(full_name, ' ', 1),
      last_name = SUBSTRING(full_name FROM POSITION(' ' IN full_name) + 1)
    WHERE full_name IS NOT NULL
      AND first_name IS NULL
      AND last_name IS NULL
  `);
}

export async function down() {
  const db = drizzle(neon(process.env.DATABASE_URL!));

  // Combine first_name and last_name back to full_name
  await db.execute(sql`
    UPDATE users
    SET full_name = first_name || ' ' || last_name
    WHERE first_name IS NOT NULL
      AND last_name IS NOT NULL
      AND full_name IS NULL
  `);
}
```

### Batch Data Migration

```typescript
// Migration: 0005_encrypt_emails.ts
import { eq } from 'drizzle-orm';
import { users } from '@/lib/schema';

export async function up() {
  const db = drizzle(neon(process.env.DATABASE_URL!));

  // Process in batches to avoid memory issues
  const batchSize = 1000;
  let offset = 0;

  while (true) {
    const batch = await db
      .select()
      .from(users)
      .where(isNull(users.encryptedEmail))
      .limit(batchSize)
      .offset(offset);

    if (batch.length === 0) break;

    for (const user of batch) {
      const encrypted = await encryptEmail(user.email);
      await db
        .update(users)
        .set({ encryptedEmail: encrypted })
        .where(eq(users.id, user.id));
    }

    offset += batchSize;
    console.log(`Processed ${offset} users`);
  }
}
```

---

## Zero-Downtime Deployments

### Adding Required Column (Safe)

```typescript
// Step 1: Add nullable column
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  status: text('status'), // Nullable first
});

// Deploy step 1
// npx drizzle-kit generate:pg
// npx drizzle-kit push:pg

// Step 2: Update application to write to new column
// Deploy application code

// Step 3: Backfill existing data
await db.execute(sql`
  UPDATE users
  SET status = 'active'
  WHERE status IS NULL
`);

// Step 4: Make column required
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  status: text('status').notNull().default('active'),
});

// Deploy step 4
// npx drizzle-kit generate:pg
// npx drizzle-kit push:pg
```

### Renaming Table (Safe)

```typescript
// Step 1: Create new table
export const usersNew = pgTable('users_new', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
});

// Step 2: Copy data
await db.execute(sql`
  INSERT INTO users_new (id, email, name)
  SELECT id, email, name FROM users
`);

// Step 3: Write to both tables (dual-write pattern)
// Update application to write to both tables

// Step 4: Switch reads to new table
// Update application to read from users_new

// Step 5: Drop old table
await db.execute(sql`DROP TABLE users`);

// Step 6: Rename new table
await db.execute(sql`ALTER TABLE users_new RENAME TO users`);
```

### Removing Column (Safe)

```typescript
// Step 1: Stop writing to column
// Deploy application that doesn't use the column

// Step 2: Wait for all old deployments to shut down
// (Ensure no running code uses the column)

// Step 3: Remove column from schema
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  // legacyField removed
});

// Step 4: Generate and apply migration
// npx drizzle-kit generate:pg
// npx drizzle-kit push:pg
```

---

## Rollback Strategies

### Migration with Rollback Script

```sql
-- Migration up: 0006_add_user_preferences.sql
CREATE TABLE user_preferences (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  theme TEXT NOT NULL DEFAULT 'light',
  notifications BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX user_preferences_user_id_idx ON user_preferences(user_id);
```

```sql
-- Migration down: 0006_add_user_preferences_rollback.sql
DROP TABLE IF EXISTS user_preferences;
```

### Rollback with Data Backup

```typescript
// Migration: 0007_remove_legacy_data.ts
export async function up() {
  const db = drizzle(neon(process.env.DATABASE_URL!));

  // Step 1: Backup data
  await db.execute(sql`
    CREATE TABLE legacy_data_backup AS
    SELECT * FROM legacy_data
  `);

  // Step 2: Delete data
  await db.execute(sql`
    DELETE FROM legacy_data
    WHERE created_at < NOW() - INTERVAL '1 year'
  `);
}

export async function down() {
  const db = drizzle(neon(process.env.DATABASE_URL!));

  // Restore from backup
  await db.execute(sql`
    INSERT INTO legacy_data
    SELECT * FROM legacy_data_backup
    ON CONFLICT (id) DO NOTHING
  `);

  // Drop backup
  await db.execute(sql`
    DROP TABLE IF EXISTS legacy_data_backup
  `);
}
```

### Test Rollback Before Production

```typescript
// test-migration-rollback.ts
import { describe, it, expect } from 'vitest';

describe('Migration Rollback', () => {
  it('should rollback cleanly', async () => {
    // Apply migration
    await runMigration('0008_add_feature');

    // Verify migration applied
    const tables = await db.execute(sql`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_name = 'new_feature_table'
    `);
    expect(tables.length).toBe(1);

    // Rollback migration
    await rollbackMigration('0008_add_feature');

    // Verify rollback
    const tablesAfter = await db.execute(sql`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_name = 'new_feature_table'
    `);
    expect(tablesAfter.length).toBe(0);
  });
});
```

---

## Migration Testing

### Test Schema Changes

```typescript
// tests/migrations/add-user-status.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { db } from '@/lib/db';
import { users } from '@/lib/schema';

describe('Migration: Add User Status', () => {
  beforeEach(async () => {
    await db.delete(users);
  });

  it('should allow inserting users with status', async () => {
    const [user] = await db
      .insert(users)
      .values({
        email: 'test@example.com',
        name: 'Test User',
        status: 'active',
      })
      .returning();

    expect(user.status).toBe('active');
  });

  it('should use default status for new users', async () => {
    const [user] = await db
      .insert(users)
      .values({
        email: 'test@example.com',
        name: 'Test User',
      })
      .returning();

    expect(user.status).toBe('active'); // Default value
  });
});
```

### Test Data Migrations

```typescript
// tests/migrations/split-full-name.test.ts
describe('Migration: Split Full Name', () => {
  it('should split full name correctly', async () => {
    // Setup: Insert user with full_name
    await db.insert(users).values({
      email: 'test@example.com',
      fullName: 'John Doe',
    });

    // Run migration
    await splitFullNameMigration();

    // Verify
    const [user] = await db
      .select()
      .from(users)
      .where(eq(users.email, 'test@example.com'));

    expect(user.firstName).toBe('John');
    expect(user.lastName).toBe('Doe');
  });

  it('should handle single-word names', async () => {
    await db.insert(users).values({
      email: 'test@example.com',
      fullName: 'Madonna',
    });

    await splitFullNameMigration();

    const [user] = await db
      .select()
      .from(users)
      .where(eq(users.email, 'test@example.com'));

    expect(user.firstName).toBe('Madonna');
    expect(user.lastName).toBe('');
  });
});
```

---

## Common Migration Scenarios

### Scenario 1: Adding JSON Column

```typescript
// Schema
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  settings: jsonb('settings').$type<UserSettings>().notNull().default({}),
});

type UserSettings = {
  theme: 'light' | 'dark';
  notifications: boolean;
  language: string;
};

// Migration
await db.execute(sql`
  ALTER TABLE users
  ADD COLUMN settings JSONB NOT NULL DEFAULT '{
    "theme": "light",
    "notifications": true,
    "language": "en"
  }'::jsonb
`);
```

### Scenario 2: Converting Timestamps

```typescript
// Before: Unix timestamp
export const events = pgTable('events', {
  id: serial('id').primaryKey(),
  occurredAt: bigint('occurred_at', { mode: 'number' }).notNull(),
});

// After: PostgreSQL timestamp
export const events = pgTable('events', {
  id: serial('id').primaryKey(),
  occurredAt: timestamp('occurred_at').notNull(),
});

// Migration
await db.execute(sql`
  ALTER TABLE events
  ALTER COLUMN occurred_at
  TYPE TIMESTAMP
  USING to_timestamp(occurred_at)
`);
```

### Scenario 3: Creating Enum Type

```typescript
// Schema
import { pgEnum } from 'drizzle-orm/pg-core';

export const userRoleEnum = pgEnum('user_role', ['user', 'admin', 'moderator']);

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  role: userRoleEnum('role').notNull().default('user'),
});

// Migration
await db.execute(sql`
  CREATE TYPE user_role AS ENUM ('user', 'admin', 'moderator');
  ALTER TABLE users
  ADD COLUMN role user_role NOT NULL DEFAULT 'user';
`);
```

### Scenario 4: Splitting Table

```typescript
// Before: Single table
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  bio: text('bio'),
  avatar: text('avatar'),
  website: text('website'),
});

// After: Split into users and profiles
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
});

export const profiles = pgTable('profiles', {
  id: serial('id').primaryKey(),
  userId: integer('user_id')
    .notNull()
    .unique()
    .references(() => users.id, { onDelete: 'cascade' }),
  bio: text('bio'),
  avatar: text('avatar'),
  website: text('website'),
});

// Migration
await db.execute(sql`
  -- Create profiles table
  CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    avatar TEXT,
    website TEXT
  );

  -- Copy data
  INSERT INTO profiles (user_id, bio, avatar, website)
  SELECT id, bio, avatar, website FROM users;

  -- Drop columns from users
  ALTER TABLE users
  DROP COLUMN bio,
  DROP COLUMN avatar,
  DROP COLUMN website;
`);
```

### Scenario 5: Adding Full-Text Search

```typescript
// Schema
export const posts = pgTable(
  'posts',
  {
    id: serial('id').primaryKey(),
    title: text('title').notNull(),
    content: text('content').notNull(),
    searchVector: text('search_vector'), // tsvector column
  },
  (table) => ({
    searchIdx: index('posts_search_idx').using('gin', sql`to_tsvector('english', ${table.title} || ' ' || ${table.content})`),
  })
);

// Migration
await db.execute(sql`
  -- Add tsvector column
  ALTER TABLE posts
  ADD COLUMN search_vector tsvector;

  -- Populate search vector
  UPDATE posts
  SET search_vector = to_tsvector('english', title || ' ' || content);

  -- Create GIN index
  CREATE INDEX posts_search_idx ON posts USING gin(search_vector);

  -- Create trigger to auto-update search vector
  CREATE TRIGGER posts_search_vector_update
  BEFORE INSERT OR UPDATE ON posts
  FOR EACH ROW EXECUTE FUNCTION
  tsvector_update_trigger(search_vector, 'pg_catalog.english', title, content);
`);
```

---

**Official Docs**: https://orm.drizzle.team/kit-docs/overview
**Next**: [edge-runtime.md](./edge-runtime.md) for edge deployment patterns
