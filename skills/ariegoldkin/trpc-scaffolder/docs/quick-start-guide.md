# tRPC Quick Start Guide

Complete walkthrough for creating your first tRPC endpoint in DevPrep AI.

---

## Overview

This guide shows you how to create a complete tRPC endpoint from scratch, including:
1. Creating a Zod schema for validation
2. Creating a router with procedures
3. Registering the router
4. Testing the endpoint

**Time**: ~10-15 minutes

---

## Step 1: Create the Schema

First, create a schema file to define your input/output types with runtime validation.

```bash
./.claude/skills/trpc-scaffolder/scripts/create-schema.sh hint
```

This creates `frontend/src/lib/trpc/schemas/hint.schema.ts`. Now edit it:

```typescript
/**
 * Hint Schemas
 * Zod schemas for hint-related types
 */
import { z } from "zod";

// Constants for validation
const MIN_HINT_LEVEL = 0;
const MAX_HINT_LEVEL = 3;

/**
 * Get Hints Input Schema
 */
export const getHintsInputSchema = z.object({
  questionId: z.string().min(1, "Question ID is required"),
  currentLevel: z
    .number()
    .int()
    .min(MIN_HINT_LEVEL)
    .max(MAX_HINT_LEVEL),
});

/**
 * Get Hints Output Schema
 */
export const getHintsOutputSchema = z.object({
  hints: z.array(z.string()),
  nextLevel: z.number().int(),
  hasMore: z.boolean(),
  success: z.boolean(),
});

// Export inferred types
export type GetHintsInput = z.infer<typeof getHintsInputSchema>;
export type GetHintsOutput = z.infer<typeof getHintsOutputSchema>;
```

**Key points:**
- Define constants for validation rules
- Create separate input and output schemas
- Always export inferred types
- Add descriptive JSDoc comments

---

## Step 2: Add Procedure to Router

Since this is a hint-related feature for AI functionality, we'll add it to the existing `ai.ts` router.

```bash
./.claude/skills/trpc-scaffolder/scripts/add-procedure.sh ai getHints query
```

This outputs a code snippet. Now edit `frontend/src/lib/trpc/routers/ai.ts`:

**1. Import the schemas at the top:**

```typescript
import {
  getHintsInputSchema,
  getHintsOutputSchema,
} from "../schemas/hint.schema";
```

**2. Add the procedure to the router:**

```typescript
export const aiRouter = router({
  // ... existing procedures (generateQuestions, evaluateAnswer)

  /**
   * Get Hints Procedure
   * Retrieves progressive hints for a question
   *
   * @input questionId, currentLevel
   * @output hints, nextLevel, hasMore, success
   */
  getHints: publicProcedure
    .input(getHintsInputSchema)
    .output(getHintsOutputSchema)
    .query(async ({ input }) => {
      const { questionId, currentLevel } = input;

      // Fetch hints from your service/database
      const hints = await fetchHintsForQuestion(questionId, currentLevel);

      return {
        hints: hints.slice(0, currentLevel + 1),
        nextLevel: currentLevel + 1,
        hasMore: currentLevel < 3,
        success: true,
      };
    }),
});
```

**Key points:**
- Use `.query()` for fetching data (GET operations)
- Use `.mutation()` for modifying data (POST/PUT/DELETE)
- Destructure input for clarity
- Return data matching the output schema exactly

---

## Step 3: Validate Your Setup

Run the validation script to ensure everything is configured correctly:

```bash
./.claude/skills/trpc-scaffolder/scripts/validate-trpc.sh
```

You should see:
```
✅ _app.ts found
✅ All routers properly registered
✅ All schemas export types
✅ tRPC validation complete
```

If you see errors:
- ❌ Router not registered → Check Step 4
- ❌ Missing type exports → Add `export type X = z.infer<...>`

---

## Step 4: Use in Frontend

Now you can use the endpoint in your React components with full type safety:

```typescript
"use client";

import { trpc } from "@/lib/trpc/client";

export function HintsPanel({ questionId }: { questionId: string }) {
  const [level, setLevel] = useState(0);

  // Auto-generated hook with full type inference!
  const { data, isLoading } = trpc.ai.getHints.useQuery({
    questionId,
    currentLevel: level,
  });

  if (isLoading) return <div>Loading hints...</div>;

  return (
    <div>
      {data?.hints.map((hint, i) => (
        <div key={i}>{hint}</div>
      ))}

      {data?.hasMore && (
        <button onClick={() => setLevel(level + 1)}>
          Show Next Hint
        </button>
      )}
    </div>
  );
}
```

**Benefits:**
- ✅ Full autocomplete on input/output
- ✅ Runtime validation via Zod
- ✅ Type errors if schema changes
- ✅ React Query integration (caching, refetching, etc.)

---

## Creating a New Router (Optional)

If you need a completely new router (not adding to an existing one):

### 1. Create the router

```bash
./.claude/skills/trpc-scaffolder/scripts/create-router.sh user
```

### 2. Edit the router file

Edit `frontend/src/lib/trpc/routers/user.ts` and add your procedures.

### 3. Register in _app.ts

Edit `frontend/src/lib/trpc/routers/_app.ts`:

```typescript
import { aiRouter } from "./ai";
import { userRouter } from "./user";  // ⬅️ Add import

export const appRouter = router({
  ai: aiRouter,
  user: userRouter,  // ⬅️ Add router
});
```

### 4. Validate

```bash
./.claude/skills/trpc-scaffolder/scripts/validate-trpc.sh
```

---

## Troubleshooting

### "Router not found" error

**Problem**: Can't import router in _app.ts

**Solution**: Check the router file exports `export const nameRouter = router({ ... })`

---

### Type errors in frontend

**Problem**: `Property 'user' does not exist on type 'Router'`

**Solution**: Restart your TypeScript server (VS Code: Cmd+Shift+P → "Restart TS Server")

---

### Validation errors at runtime

**Problem**: Zod throwing validation errors

**Solution**:
1. Check your input matches the schema
2. Use `.optional()` for optional fields
3. Add `.min()` constraints to required strings

---

### Procedure not showing in autocomplete

**Problem**: New procedure doesn't appear in `trpc.ai.___`

**Solution**:
1. Check procedure is inside `router({ ... })`
2. Check input/output schemas are imported
3. Restart TypeScript server

---

## Next Steps

**Learn more:**
- [Advanced Zod patterns](./trpc-patterns.md#advanced-zod-patterns)
- [Error handling strategies](./trpc-patterns.md#error-handling-strategies)
- [Testing procedures](./trpc-patterns.md#testing-procedures)

**Full documentation:**
- [API Design](../../../Docs/api-design.md)
- [tRPC Migration Guide](../../../Docs/api-transition/trpc-migration.md)

---

**Version:** 1.0.0 | **Updated:** October 2025
