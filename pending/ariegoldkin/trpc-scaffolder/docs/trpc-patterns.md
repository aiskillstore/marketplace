## tRPC Advanced Patterns & Best Practices

Extended guide for complex tRPC scenarios in DevPrep AI.

**New to tRPC?** Start with [Quick Start Guide](./quick-start-guide.md) for a step-by-step tutorial.

---

## Table of Contents

1. [Advanced Zod Patterns](#advanced-zod-patterns)
2. [Context Usage](#context-usage)
3. [Error Handling Strategies](#error-handling-strategies)
4. [Testing Procedures](#testing-procedures)
5. [Performance Optimization](#performance-optimization)

---

## Advanced Zod Patterns

### Reusable Schemas

```typescript
// Base schemas that can be composed
const baseEntitySchema = z.object({
  id: z.string(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// Extend base schema
export const userSchema = baseEntitySchema.extend({
  name: z.string().min(1),
  email: z.string().email(),
});

// Partial schemas for updates
export const updateUserSchema = userSchema.partial().omit({
  id: true,
  createdAt: true,
});
```

### Conditional Validation

```typescript
// Different validation based on type
export const questionInputSchema = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("coding"),
    code: z.string().min(1, "Code required for coding questions"),
    language: z.string(),
  }),
  z.object({
    type: z.literal("behavioral"),
    answer: z.string().min(10, "Answer too short"),
  }),
]);
```

### Custom Validation

```typescript
// Custom refinement
export const passwordSchema = z
  .string()
  .min(8, "Password must be at least 8 characters")
  .refine(
    (val) => /[A-Z]/.test(val),
    "Password must contain uppercase letter"
  )
  .refine(
    (val) => /[0-9]/.test(val),
    "Password must contain number"
  );

// Cross-field validation
export const dateRangeSchema = z
  .object({
    startDate: z.string(),
    endDate: z.string(),
  })
  .refine(
    (data) => new Date(data.endDate) > new Date(data.startDate),
    {
      message: "End date must be after start date",
      path: ["endDate"],
    }
  );
```

### Array Validation

```typescript
// Array with constraints
export const tagsSchema = z
  .array(z.string())
  .min(1, "At least one tag required")
  .max(10, "Maximum 10 tags allowed")
  .refine(
    (tags) => new Set(tags).size === tags.length,
    "Duplicate tags not allowed"
  );

// Array of objects
export const questionsArraySchema = z
  .array(questionSchema)
  .min(1)
  .max(20);
```

### Transformations

```typescript
// Transform input before validation
export const emailInputSchema = z
  .string()
  .transform((val) => val.toLowerCase().trim())
  .pipe(z.string().email());

// Transform dates
export const dateInputSchema = z
  .string()
  .or(z.date())
  .transform((val) =>
    typeof val === "string" ? new Date(val) : val
  );
```

---

## Context Usage

### Accessing Context

```typescript
// In context.ts
export type Context = {
  userId?: string;
  sessionId?: string;
};

// In procedure
getUserData: publicProcedure
  .input(z.object({ userId: z.string() }))
  .query(async ({ input, ctx }) => {
    // Access context
    const currentUserId = ctx.userId;

    // Validate authorization
    if (currentUserId !== input.userId) {
      throw new TRPCError({
        code: "FORBIDDEN",
        message: "Cannot access other user's data",
      });
    }

    return fetchUserData(input.userId);
  }),
```

### Protected Procedures

```typescript
// Create authenticated procedure
import { TRPCError } from "@trpc/server";
import { t } from "../init";

const isAuthenticated = t.middleware(({ ctx, next }) => {
  if (!ctx.userId) {
    throw new TRPCError({
      code: "UNAUTHORIZED",
      message: "Must be logged in",
    });
  }

  return next({
    ctx: {
      userId: ctx.userId, // Now guaranteed to exist
    },
  });
});

export const protectedProcedure = t.procedure.use(isAuthenticated);

// Use in router
deleteAccount: protectedProcedure
  .mutation(async ({ ctx }) => {
    // ctx.userId is guaranteed to exist
    await deleteUser(ctx.userId);
    return { success: true };
  }),
```

---

## Error Handling Strategies

### Custom Error Codes

```typescript
import { TRPCError } from "@trpc/server";

// Common error patterns
const throwNotFound = (resource: string, id: string) => {
  throw new TRPCError({
    code: "NOT_FOUND",
    message: `${resource} with id ${id} not found`,
  });
};

const throwValidation = (message: string) => {
  throw new TRPCError({
    code: "BAD_REQUEST",
    message,
  });
};

// In procedure
getQuestion: publicProcedure
  .input(z.object({ id: z.string() }))
  .query(async ({ input }) => {
    const question = await findQuestion(input.id);

    if (!question) {
      throwNotFound("Question", input.id);
    }

    return question;
  }),
```

### Try-Catch Patterns

```typescript
evaluateAnswer: publicProcedure
  .input(evaluateAnswerInputSchema)
  .mutation(async ({ input }) => {
    try {
      const response = await callClaudeAPI(input);
      return {
        feedback: response.data,
        success: true,
      };
    } catch (error) {
      // Handle API errors
      if (error instanceof ApiError) {
        throw new TRPCError({
          code: "INTERNAL_SERVER_ERROR",
          message: `AI service error: ${error.message}`,
          cause: error,
        });
      }

      // Re-throw tRPC errors
      if (error instanceof TRPCError) {
        throw error;
      }

      // Unknown errors
      throw new TRPCError({
        code: "INTERNAL_SERVER_ERROR",
        message: "An unexpected error occurred",
      });
    }
  }),
```

---

## Testing Procedures

### Unit Testing

```typescript
// test/trpc/ai.test.ts
import { describe, it, expect } from "vitest";
import { appRouter } from "@lib/trpc/routers/_app";

describe("AI Router", () => {
  it("should generate questions", async () => {
    const caller = appRouter.createCaller({
      userId: "test-user",
    });

    const result = await caller.ai.generateQuestions({
      profile: {
        role: "frontend",
        experienceLevel: "mid",
      },
      count: 5,
      difficulty: 7,
      type: "coding",
    });

    expect(result.questions).toHaveLength(5);
    expect(result.totalGenerated).toBe(5);
  });

  it("should validate input", async () => {
    const caller = appRouter.createCaller({});

    await expect(
      caller.ai.generateQuestions({
        profile: {} as any,
        count: 0, // Invalid
        difficulty: 7,
        type: "coding",
      })
    ).rejects.toThrow();
  });
});
```

---

## Performance Optimization

### Batching Queries

```typescript
// Instead of multiple separate calls
const q1 = await trpc.questions.get.query({ id: "1" });
const q2 = await trpc.questions.get.query({ id: "2" });

// Use batch procedure
getBatch: publicProcedure
  .input(z.object({ ids: z.array(z.string()) }))
  .query(async ({ input }) => {
    // Single database query
    return await db.questions.findMany({
      where: { id: { in: input.ids } },
    });
  }),
```

### Caching Strategies

```typescript
// In frontend
const { data } = trpc.questions.list.useQuery(
  { limit: 20 },
  {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  }
);
```

### Pagination

```typescript
export const listQuestionsInputSchema = z.object({
  limit: z.number().int().min(1).max(100).default(20),
  cursor: z.string().optional(),
});

listQuestions: publicProcedure
  .input(listQuestionsInputSchema)
  .query(async ({ input }) => {
    const { limit, cursor } = input;

    const questions = await db.questions.findMany({
      take: limit + 1,
      cursor: cursor ? { id: cursor } : undefined,
      orderBy: { createdAt: "desc" },
    });

    let nextCursor: string | undefined;
    if (questions.length > limit) {
      const nextItem = questions.pop();
      nextCursor = nextItem!.id;
    }

    return {
      questions,
      nextCursor,
    };
  }),
```

---

**Version:** 1.0.0 | **Updated:** October 2025
