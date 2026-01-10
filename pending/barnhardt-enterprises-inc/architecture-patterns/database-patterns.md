# Database Patterns

For complete Drizzle ORM patterns, see: [drizzle-orm-patterns skill](../drizzle-orm-patterns/SKILL.md)

## Quick Reference

### Why Drizzle (Not Prisma)?

**Edge Runtime Compatible** - Drizzle works with Vercel Edge Functions, Prisma doesn't.

See: `CLAUDE.md#edge-first-architecture` and `docs/decisions/ADR-002-DRIZZLE-ORM-MIGRATION.md`

---

### Basic Queries

```typescript
import { db } from '@/lib/db'
import { projectsTable } from '@/lib/db/schema'

// SELECT
const projects = await db.select().from(projectsTable)

// SELECT with WHERE
const project = await db
  .select()
  .from(projectsTable)
  .where(eq(projectsTable.id, id))

// INSERT
const newProject = await db
  .insert(projectsTable)
  .values({ name: 'Project', userId: '123' })
  .returning()

// UPDATE
await db
  .update(projectsTable)
  .set({ name: 'Updated' })
  .where(eq(projectsTable.id, id))

// DELETE
await db
  .delete(projectsTable)
  .where(eq(projectsTable.id, id))
```

---

### Relations

```typescript
import { eq } from 'drizzle-orm'

// Join query
const projectsWithUser = await db
  .select()
  .from(projectsTable)
  .leftJoin(usersTable, eq(projectsTable.userId, usersTable.id))

// Using relations (defined in schema)
const project = await db.query.projects.findFirst({
  where: eq(projectsTable.id, id),
  with: {
    user: true,
    tasks: true,
  },
})
```

---

### Transactions

```typescript
await db.transaction(async (tx) => {
  const project = await tx
    .insert(projectsTable)
    .values({ name: 'Project' })
    .returning()

  await tx
    .insert(tasksTable)
    .values({ projectId: project[0].id, name: 'Task 1' })
})
```

---

### Migrations

```bash
# Generate migration
npm run db:generate

# Run migrations
npm run db:migrate

# View database (development only)
npm run db:studio
```

---

## SQL Injection Prevention

**Always use parameterized queries** (Drizzle does this automatically):

```typescript
// ✅ SAFE: Parameterized
const user = await db
  .select()
  .from(usersTable)
  .where(eq(usersTable.email, email))

// ❌ UNSAFE: String concatenation (DON'T DO THIS)
const query = `SELECT * FROM users WHERE email = '${email}'`
```

---

## See Also

- [drizzle-orm-patterns/SKILL.md](../drizzle-orm-patterns/SKILL.md) - Complete patterns
- [../security-sentinel/SKILL.md](../security-sentinel/SKILL.md) - SQL injection prevention
- `docs/decisions/ADR-002-DRIZZLE-ORM-MIGRATION.md` - Why Drizzle not Prisma
