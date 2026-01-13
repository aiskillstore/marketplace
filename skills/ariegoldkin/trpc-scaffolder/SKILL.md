---
name: trpc-scaffolder
description: Scaffolds tRPC routers, procedures, and Zod schemas with full type safety following DevPrep AI patterns
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# tRPC Scaffolder

Automate creation of type-safe tRPC endpoints with Zod validation.

**TL;DR**: Run scripts to create routers/schemas, register in `_app.ts`, validate with scripts.

---

## Auto-Triggers

Auto-triggered by keywords:
- "new endpoint", "create endpoint", "tRPC procedure"
- "new router", "API", "Zod schema"

---

## Quick Standards

### File Locations
```
lib/trpc/routers/
  _app.ts          # Register all routers here ⚠️
  {name}.ts        # Router files

lib/trpc/schemas/
  {entity}.schema.ts  # Zod schemas
```

### Router Pattern
```typescript
export const nameRouter = router({
  doThing: publicProcedure
    .input(inputSchema)
    .output(outputSchema)
    .mutation(async ({ input }) => { /* logic */ }),
});
```

### Schema Pattern
```typescript
export const inputSchema = z.object({
  field: z.string().min(1),
});

export type Input = z.infer<typeof inputSchema>;  // ⚠️ Required!
```

### Registration (Required!)
```typescript
// In _app.ts
export const appRouter = router({
  ai: aiRouter,
  name: nameRouter,  // ⬅️ Add new routers here
});
```

---

## Run Scripts

### Create Router
```bash
./.claude/skills/trpc-scaffolder/scripts/create-router.sh user
# Creates: lib/trpc/routers/user.ts
# ⚠️ Remember to register in _app.ts!
```

### Add Procedure
```bash
./.claude/skills/trpc-scaffolder/scripts/add-procedure.sh ai getHints query
# Outputs code snippet to add to router
```

### Create Schema
```bash
./.claude/skills/trpc-scaffolder/scripts/create-schema.sh hint
# Creates: lib/trpc/schemas/hint.schema.ts
```

### Validate Setup
```bash
./.claude/skills/trpc-scaffolder/scripts/validate-trpc.sh
# Checks: router registration, type exports
```

---

## Quick Reference

### Query vs Mutation
| Type | Use For | Method |
|------|---------|--------|
| Query | Fetch data (GET) | `.query(async ({ input }) => ...)` |
| Mutation | Modify data (POST/PUT/DELETE) | `.mutation(async ({ input }) => ...)` |

### Common Zod Patterns
| Type | Pattern | Example |
|------|---------|---------|
| String | `z.string().min(1).max(100)` | Name validation |
| Number | `z.number().int().min(0).max(10)` | Difficulty 0-10 |
| Email | `z.string().email()` | Email validation |
| Optional | `z.string().optional()` | Optional field |
| Array | `z.array(z.string()).min(1)` | At least 1 item |
| Enum | `z.enum(["a", "b", "c"])` | Fixed choices |
| Object | `z.object({ field: z.string() })` | Nested object |

### Naming Conventions
- **Routers**: `{domain}Router` (e.g., `aiRouter`, `userRouter`)
- **Procedures**: `camelCase` (e.g., `generateQuestions`, `getHints`)
- **Schemas**: `{action}{Entity}{Input\|Output}Schema`
- **Files**: `{entity}.schema.ts`, `{domain}.ts`

### Error Codes
| Code | When | Example |
|------|------|---------|
| `NOT_FOUND` | Resource doesn't exist | User not found |
| `BAD_REQUEST` | Invalid input | Validation failed |
| `UNAUTHORIZED` | Not authenticated | Login required |
| `FORBIDDEN` | Not authorized | Access denied |
| `INTERNAL_SERVER_ERROR` | Server error | API failure |

---

## Common Fixes

### Router Not Registered
```typescript
// ❌ Forgot this step
// ✅ Add to _app.ts:
import { userRouter } from "./user";
export const appRouter = router({ ai: aiRouter, user: userRouter });
```

### Missing Type Exports
```typescript
// ❌ Schema without types
export const userSchema = z.object({ name: z.string() });

// ✅ Always export inferred types
export type User = z.infer<typeof userSchema>;
```

### Wrong Procedure Type
```typescript
// ❌ Using mutation for fetching data
getData: publicProcedure.mutation(...)

// ✅ Use query for GET operations
getData: publicProcedure.query(...)
```

### Schema Validation Error
```typescript
// ❌ No validation
field: z.string()

// ✅ Add constraints
field: z.string().min(1, "Field is required")
```

---

## When to Load Additional Docs

**SKILL.md is self-sufficient for:**
- Creating routers and schemas
- Running scripts
- Fixing common errors

**Load additional docs when needed:**

| Need | Load |
|------|------|
| Step-by-step tutorial | `docs/quick-start-guide.md` |
| Advanced Zod patterns | `docs/trpc-patterns.md` (lines 1-80) |
| Error handling strategies | `docs/trpc-patterns.md` (lines 150-220) |
| Testing procedures | `docs/trpc-patterns.md` (lines 220-270) |
| Context & middleware | `docs/trpc-patterns.md` (lines 80-150) |

**Code examples:**
- ✅ Perfect: `examples/good-router.ts`, `examples/good-schema.ts`

**Full project docs:** `Docs/api-design.md`, `Docs/api-transition/trpc-migration.md`

---

**Version:** 1.0.0 | **Updated:** October 2025
**Pattern**: Follows quality-reviewer structure (optimized)
