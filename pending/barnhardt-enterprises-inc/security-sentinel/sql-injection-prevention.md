# SQL Injection Prevention (Drizzle ORM)

Complete guide to preventing SQL injection in Next.js 15 with Drizzle ORM.

---

## Table of Contents

1. [Understanding SQL Injection](#understanding-sql-injection)
2. [Drizzle Parameterized Queries](#drizzle-parameterized-queries)
3. [Common SQL Injection Patterns](#common-sql-injection-patterns)
4. [Dynamic Queries Safely](#dynamic-queries-safely)
5. [Raw SQL Safety](#raw-sql-safety)
6. [Database Schema Security](#database-schema-security)
7. [Testing for SQL Injection](#testing-for-sql-injection)

---

## Understanding SQL Injection

### What is SQL Injection?

SQL injection is a code injection technique where attackers insert malicious SQL statements into application queries, allowing them to:
- Read sensitive data from database
- Modify database data (Insert/Update/Delete)
- Execute administration operations (shutdown database)
- Recover files from database server
- Issue commands to operating system

### Attack Examples

**Example 1: Authentication Bypass**
```typescript
// ❌ VULNERABLE CODE
const email = req.body.email  // "admin@example.com' OR '1'='1"
const query = `SELECT * FROM users WHERE email = '${email}'`
// Resulting query: SELECT * FROM users WHERE email = 'admin@example.com' OR '1'='1'
// Returns ALL users!
```

**Example 2: Data Exfiltration**
```typescript
// ❌ VULNERABLE CODE
const id = req.params.id  // "1 UNION SELECT password FROM users WHERE id=1"
const query = `SELECT name FROM products WHERE id = ${id}`
// Resulting query: SELECT name FROM products WHERE id = 1 UNION SELECT password FROM users WHERE id=1
// Leaks password!
```

**Example 3: Data Destruction**
```typescript
// ❌ VULNERABLE CODE
const search = req.query.search  // "'; DROP TABLE users; --"
const query = `SELECT * FROM products WHERE name LIKE '%${search}%'`
// Resulting query: SELECT * FROM products WHERE name LIKE '%'; DROP TABLE users; --%'
// Drops entire users table!
```

---

## Drizzle Parameterized Queries

### Basic Queries (Always Safe)

```typescript
import { db } from '@/lib/db'
import { users, projects, posts } from '@/lib/db/schema'
import { eq, and, or, like, gt, lt, inArray, sql } from 'drizzle-orm'

// ✅ SAFE: Select by ID
export async function getUserById(id: string) {
  return db.select()
    .from(users)
    .where(eq(users.id, id))  // Automatically parameterized
    .limit(1)
}

// ✅ SAFE: Select with multiple conditions
export async function getUserByEmailAndStatus(email: string, status: string) {
  return db.select()
    .from(users)
    .where(
      and(
        eq(users.email, email),
        eq(users.status, status)
      )
    )
}

// ✅ SAFE: LIKE queries
export async function searchProjects(searchTerm: string) {
  return db.select()
    .from(projects)
    .where(like(projects.name, `%${searchTerm}%`))  // Safe - parameterized
}

// ✅ SAFE: IN queries
export async function getUsersByIds(ids: string[]) {
  return db.select()
    .from(users)
    .where(inArray(users.id, ids))  // Safe - parameterized
}

// ✅ SAFE: Greater than / Less than
export async function getRecentPosts(days: number) {
  const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000)

  return db.select()
    .from(posts)
    .where(gt(posts.createdAt, cutoff))  // Safe - parameterized
}
```

### Complex Conditions

```typescript
// ✅ SAFE: Multiple OR conditions
export async function searchUsers(query: string) {
  return db.select()
    .from(users)
    .where(
      or(
        like(users.email, `%${query}%`),
        like(users.name, `%${query}%`),
        like(users.username, `%${query}%`)
      )
    )
}

// ✅ SAFE: Nested conditions
export async function getActiveProjectsByUser(userId: string, minBudget: number) {
  return db.select()
    .from(projects)
    .where(
      and(
        eq(projects.userId, userId),
        eq(projects.status, 'active'),
        or(
          gt(projects.budget, minBudget),
          eq(projects.featured, true)
        )
      )
    )
}

// ✅ SAFE: NULL checks
export async function getUsersWithoutEmail() {
  return db.select()
    .from(users)
    .where(sql`${users.email} IS NULL`)
}

// ✅ SAFE: BETWEEN
export async function getProjectsInBudgetRange(min: number, max: number) {
  return db.select()
    .from(projects)
    .where(
      and(
        gt(projects.budget, min),
        lt(projects.budget, max)
      )
    )
}
```

### Insert Operations

```typescript
// ✅ SAFE: Single insert
export async function createUser(data: {
  email: string
  name: string
  password: string
}) {
  return db.insert(users).values({
    email: data.email,  // Automatically parameterized
    name: data.name,
    password: data.password,
  })
}

// ✅ SAFE: Bulk insert
export async function createUsers(userList: Array<{
  email: string
  name: string
  password: string
}>) {
  return db.insert(users).values(userList)  // All parameterized
}

// ✅ SAFE: Insert with returning
export async function createProject(data: {
  name: string
  userId: string
}) {
  const [project] = await db.insert(projects)
    .values({
      name: data.name,
      userId: data.userId,
      createdAt: new Date(),
    })
    .returning()

  return project
}
```

### Update Operations

```typescript
// ✅ SAFE: Update by ID
export async function updateUser(id: string, data: {
  name?: string
  email?: string
}) {
  return db.update(users)
    .set(data)  // Automatically parameterized
    .where(eq(users.id, id))
}

// ✅ SAFE: Update with conditions
export async function deactivateOldProjects(days: number) {
  const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000)

  return db.update(projects)
    .set({ status: 'archived' })
    .where(
      and(
        eq(projects.status, 'active'),
        lt(projects.lastActivityAt, cutoff)
      )
    )
}

// ✅ SAFE: Increment/Decrement
export async function incrementProjectViews(id: string) {
  return db.update(projects)
    .set({ views: sql`${projects.views} + 1` })
    .where(eq(projects.id, id))
}
```

### Delete Operations

```typescript
// ✅ SAFE: Delete by ID
export async function deleteUser(id: string) {
  return db.delete(users)
    .where(eq(users.id, id))
}

// ✅ SAFE: Delete with conditions
export async function deleteExpiredSessions() {
  return db.delete(sessions)
    .where(lt(sessions.expiresAt, new Date()))
}

// ✅ SAFE: Delete with multiple conditions
export async function deleteUserProjects(userId: string, status: string) {
  return db.delete(projects)
    .where(
      and(
        eq(projects.userId, userId),
        eq(projects.status, status)
      )
    )
}
```

---

## Common SQL Injection Patterns

### Pattern 1: String Concatenation

```typescript
// ❌ NEVER DO THIS
export async function getUser(email: string) {
  const query = `SELECT * FROM users WHERE email = '${email}'`
  return db.execute(sql.raw(query))  // VULNERABLE!
}

// ✅ DO THIS
export async function getUser(email: string) {
  return db.select()
    .from(users)
    .where(eq(users.email, email))  // Safe - parameterized
}
```

### Pattern 2: Template Literals in Raw SQL

```typescript
// ❌ NEVER DO THIS
export async function searchUsers(query: string) {
  return db.execute(sql`
    SELECT * FROM users
    WHERE name LIKE '%${query}%'
  `)  // VULNERABLE!
}

// ✅ DO THIS
export async function searchUsers(query: string) {
  return db.select()
    .from(users)
    .where(like(users.name, `%${query}%`))  // Safe - parameterized
}

// ✅ OR THIS (if raw SQL needed)
export async function searchUsers(query: string) {
  return db.execute(sql`
    SELECT * FROM users
    WHERE name LIKE ${`%${query}%`}
  `)  // Safe - Drizzle parameterizes ${...}
}
```

### Pattern 3: Dynamic Table/Column Names

```typescript
// ❌ NEVER DO THIS
export async function sortUsers(sortBy: string, order: string) {
  return db.execute(sql.raw(`
    SELECT * FROM users
    ORDER BY ${sortBy} ${order}
  `))  // VULNERABLE to column injection!
}

// ✅ DO THIS: Whitelist allowed values
export async function sortUsers(
  sortBy: 'email' | 'name' | 'createdAt',
  order: 'asc' | 'desc'
) {
  // TypeScript ensures only valid values
  const columnMap = {
    email: users.email,
    name: users.name,
    createdAt: users.createdAt,
  }

  const column = columnMap[sortBy]

  if (order === 'asc') {
    return db.select().from(users).orderBy(asc(column))
  } else {
    return db.select().from(users).orderBy(desc(column))
  }
}

// ✅ OR THIS: Zod validation
import { z } from 'zod'

const sortSchema = z.object({
  sortBy: z.enum(['email', 'name', 'createdAt']),
  order: z.enum(['asc', 'desc']),
})

export async function sortUsers(input: unknown) {
  const { sortBy, order } = sortSchema.parse(input)

  // Now safe to use
  const column = {
    email: users.email,
    name: users.name,
    createdAt: users.createdAt,
  }[sortBy]

  return db.select()
    .from(users)
    .orderBy(order === 'asc' ? asc(column) : desc(column))
}
```

### Pattern 4: LIKE Wildcards

```typescript
// ❌ POTENTIALLY DANGEROUS
export async function searchProjects(query: string) {
  // User input: "%'; DROP TABLE users; --"
  return db.select()
    .from(projects)
    .where(like(projects.name, `${query}`))  // User controls entire pattern!
}

// ✅ DO THIS: Control wildcards yourself
export async function searchProjects(query: string) {
  // Sanitize input first
  const sanitized = query.replace(/[%_]/g, '\\$&')  // Escape wildcards

  return db.select()
    .from(projects)
    .where(like(projects.name, `%${sanitized}%`))  // You control wildcards
}

// ✅ OR THIS: Use full-text search
export async function searchProjects(query: string) {
  return db.execute(sql`
    SELECT * FROM projects
    WHERE to_tsvector('english', name) @@ plainto_tsquery('english', ${query})
  `)  // PostgreSQL full-text search (parameterized)
}
```

---

## Dynamic Queries Safely

### Conditional Filters

```typescript
interface ProjectFilters {
  userId?: string
  status?: string
  minBudget?: number
  maxBudget?: number
  search?: string
}

// ✅ SAFE: Build query dynamically
export async function getProjects(filters: ProjectFilters) {
  let query = db.select().from(projects)

  const conditions = []

  if (filters.userId) {
    conditions.push(eq(projects.userId, filters.userId))
  }

  if (filters.status) {
    conditions.push(eq(projects.status, filters.status))
  }

  if (filters.minBudget) {
    conditions.push(gt(projects.budget, filters.minBudget))
  }

  if (filters.maxBudget) {
    conditions.push(lt(projects.budget, filters.maxBudget))
  }

  if (filters.search) {
    conditions.push(like(projects.name, `%${filters.search}%`))
  }

  if (conditions.length > 0) {
    query = query.where(and(...conditions))
  }

  return query
}
```

### Dynamic Sorting

```typescript
type SortColumn = 'name' | 'createdAt' | 'budget'
type SortOrder = 'asc' | 'desc'

// ✅ SAFE: Type-safe sorting
export async function getProjectsSorted(
  sortBy: SortColumn = 'createdAt',
  order: SortOrder = 'desc'
) {
  const columnMap = {
    name: projects.name,
    createdAt: projects.createdAt,
    budget: projects.budget,
  }

  const column = columnMap[sortBy]

  return db.select()
    .from(projects)
    .orderBy(order === 'asc' ? asc(column) : desc(column))
}
```

### Dynamic Pagination

```typescript
// ✅ SAFE: Pagination
export async function getProjectsPaginated(
  page: number = 1,
  limit: number = 20
) {
  const offset = (page - 1) * limit

  return db.select()
    .from(projects)
    .limit(limit)    // Parameterized
    .offset(offset)  // Parameterized
}
```

---

## Raw SQL Safety

### When to Use Raw SQL

Use raw SQL only when:
- Drizzle doesn't support the operation
- Performance requires database-specific features
- Complex joins not possible with Drizzle

### Safe Raw SQL Patterns

```typescript
// ✅ SAFE: Use Drizzle's sql template tag
export async function getProjectStats(userId: string) {
  return db.execute(sql`
    SELECT
      COUNT(*) as total,
      SUM(budget) as total_budget,
      AVG(budget) as avg_budget
    FROM projects
    WHERE user_id = ${userId}
  `)  // ${userId} is parameterized automatically
}

// ✅ SAFE: Complex joins with parameters
export async function getUserWithProjects(userId: string) {
  return db.execute(sql`
    SELECT
      u.*,
      json_agg(p.*) as projects
    FROM users u
    LEFT JOIN projects p ON p.user_id = u.id
    WHERE u.id = ${userId}
    GROUP BY u.id
  `)
}

// ✅ SAFE: Use sql.raw() ONLY for static SQL
export async function getDatabaseVersion() {
  return db.execute(sql.raw('SELECT version()'))  // No parameters - OK
}

// ❌ NEVER DO THIS
export async function dangerousQuery(userId: string) {
  return db.execute(sql.raw(`
    SELECT * FROM users WHERE id = '${userId}'
  `))  // VULNERABLE!
}
```

### Escaping for Raw SQL

```typescript
// If you MUST use raw SQL with dynamic values:

import { escape } from 'pg'  // PostgreSQL escaping

// ⚠️ LAST RESORT: Manual escaping
export async function lastResortQuery(userId: string) {
  const escapedId = escape(userId)
  return db.execute(sql.raw(`
    SELECT * FROM users WHERE id = ${escapedId}
  `))
}

// ✅ BETTER: Use Drizzle's parameterization
export async function betterQuery(userId: string) {
  return db.execute(sql`
    SELECT * FROM users WHERE id = ${userId}
  `)
}
```

---

## Database Schema Security

### Use Appropriate Data Types

```typescript
// schema.ts
import { pgTable, uuid, text, integer, timestamp, boolean } from 'drizzle-orm/pg-core'

// ✅ GOOD: Use specific types
export const users = pgTable('users', {
  id: uuid('id').defaultRandom().primaryKey(),  // UUID (not integer)
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  age: integer('age'),  // Integer (not text)
  isActive: boolean('is_active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
})

// ❌ BAD: Using text for everything
export const badUsers = pgTable('bad_users', {
  id: text('id'),  // Should be UUID
  age: text('age'),  // Should be integer
  createdAt: text('created_at'),  // Should be timestamp
})
```

### Constraints and Validation

```typescript
import { pgTable, uuid, text, varchar, check } from 'drizzle-orm/pg-core'

// ✅ GOOD: Database-level constraints
export const users = pgTable('users', {
  id: uuid('id').defaultRandom().primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  username: varchar('username', { length: 50 }).notNull().unique(),
  age: integer('age'),
}, (table) => ({
  // Check constraints
  ageCheck: check('age_check', sql`${table.age} >= 0 AND ${table.age} <= 150`),
  emailFormat: check('email_format', sql`${table.email} ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'`),
}))
```

### Foreign Key Cascades

```typescript
// ✅ GOOD: Proper foreign key cascades
export const projects = pgTable('projects', {
  id: uuid('id').defaultRandom().primaryKey(),
  userId: uuid('user_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),  // Delete projects when user deleted
  name: text('name').notNull(),
})

export const comments = pgTable('comments', {
  id: uuid('id').defaultRandom().primaryKey(),
  projectId: uuid('project_id')
    .notNull()
    .references(() => projects.id, { onDelete: 'cascade' }),  // Delete comments when project deleted
  content: text('content').notNull(),
})
```

---

## Testing for SQL Injection

### Manual Testing

```typescript
// Test with malicious inputs
const maliciousInputs = [
  "' OR '1'='1",
  "'; DROP TABLE users; --",
  "' UNION SELECT password FROM users WHERE id=1 --",
  "admin' --",
  "' OR 1=1 --",
  "1' AND '1'='1",
  "1; UPDATE users SET role='admin' WHERE email='attacker@example.com' --",
]

for (const input of maliciousInputs) {
  try {
    await getUser(input)
    console.log(`✅ Safe against: ${input}`)
  } catch (error) {
    console.log(`⚠️ Error with: ${input}`)
    console.error(error)
  }
}
```

### Automated Testing

```typescript
// tests/security/sql-injection.test.ts
import { describe, it, expect } from 'vitest'
import { getUserByEmail, searchProjects } from '@/lib/db/queries'

describe('SQL Injection Protection', () => {
  it('should prevent SQL injection in email lookup', async () => {
    const maliciousEmail = "admin@example.com' OR '1'='1"

    const result = await getUserByEmail(maliciousEmail)

    // Should return no results (not all users)
    expect(result).toBeNull()
  })

  it('should prevent SQL injection in search', async () => {
    const maliciousSearch = "'; DROP TABLE projects; --"

    // Should not throw error or execute DROP
    const result = await searchProjects(maliciousSearch)

    expect(result).toBeDefined()
    expect(Array.isArray(result)).toBe(true)
  })

  it('should handle special characters safely', async () => {
    const specialChars = ["'", '"', ';', '--', '/*', '*/', '\\']

    for (const char of specialChars) {
      const result = await searchProjects(char)

      expect(result).toBeDefined()
      expect(Array.isArray(result)).toBe(true)
    }
  })
})
```

### Database Query Logging

```typescript
// Log all queries in development
if (process.env.NODE_ENV === 'development') {
  db.$on('query', (e) => {
    console.log('Query: ' + e.query)
    console.log('Params: ' + JSON.stringify(e.params))
    console.log('Duration: ' + e.duration + 'ms')
  })
}
```

---

## Summary Checklist

**SQL Injection Prevention:**

- [ ] All queries use Drizzle ORM (parameterized by default)
- [ ] No raw SQL with string concatenation
- [ ] No user input directly in SQL queries
- [ ] Dynamic table/column names whitelisted
- [ ] LIKE queries control wildcard placement
- [ ] Raw SQL uses `sql` template tag (not `sql.raw()`)
- [ ] Database schema has proper constraints
- [ ] Foreign keys have appropriate cascades
- [ ] Input validated with Zod before queries
- [ ] SQL injection tests in test suite
- [ ] Query logging enabled in development
- [ ] Database user has minimal permissions

**References:**
- Drizzle ORM Docs: https://orm.drizzle.team/docs/overview
- OWASP SQL Injection: https://owasp.org/www-community/attacks/SQL_Injection
- PostgreSQL Security: https://www.postgresql.org/docs/current/sql-syntax.html
