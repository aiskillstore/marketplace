---
name: pitfalls-drizzle-orm
description: Drizzle ORM patterns and migration safety rules. Use when defining schemas, running migrations, or debugging database issues. Triggers on: Drizzle, schema, migration, db:push, $inferSelect, array column.
---

# Drizzle ORM Pitfalls

Common pitfalls and correct patterns for Drizzle ORM.

## When to Use

- Defining database schemas
- Running migrations (db:push)
- Creating insert/select types
- Working with array columns
- Reviewing Drizzle ORM code

## Workflow

### Step 1: Verify Schema Types

Check that types are exported correctly.

### Step 2: Check Array Syntax

Verify array columns use correct syntax.

### Step 3: Test Migrations Safely

Never change primary key types in production.

---

## Critical Rules

```typescript
// ❌ NEVER change primary key types
// serial → varchar or varchar → uuid BREAKS migrations

// ✅ Array columns - correct syntax
allowedTokens: text('allowed_tokens').array()  // CORRECT
// ❌ WRONG: array(text('allowed_tokens'))

// ✅ Always create insert/select types
export type Strategy = typeof strategies.$inferSelect;
export type NewStrategy = typeof strategies.$inferInsert;

// ✅ Use drizzle-zod for validation
import { createInsertSchema } from 'drizzle-zod';
export const insertStrategySchema = createInsertSchema(strategies);
```

## Migration Safety

```bash
# Safe schema sync
npm run db:push

# If data-loss warning and you're sure
npm run db:push --force

# NEVER in production without backup
```

## Type Inference Pattern

```typescript
// ✅ Infer types from schema
import { strategies } from './schema';

type Strategy = typeof strategies.$inferSelect;
type NewStrategy = typeof strategies.$inferInsert;

// ✅ With Zod validation
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import { z } from 'zod';

const insertSchema = createInsertSchema(strategies);
type StrategyInput = z.infer<typeof insertSchema>;
```

## Quick Checklist

- [ ] No primary key type changes
- [ ] Array columns use `text().array()` syntax
- [ ] Insert/select types exported for models
- [ ] Using drizzle-zod for validation
- [ ] Migration tested in dev before prod
