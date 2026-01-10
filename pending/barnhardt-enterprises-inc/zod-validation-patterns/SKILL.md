# Zod Validation Patterns Skill

**Use this skill when:** Working with user input validation, API request validation, form data validation, or data transformation in Quetrex.

## Purpose

This skill provides comprehensive patterns for using Zod validation library in TypeScript applications. It ensures input validation is done correctly, securely, and consistently across the codebase.

## What's Covered

1. **[Schema Patterns](./schema-patterns.md)** - Complete guide to all Zod schema types
   - Primitives (string, number, boolean, date)
   - Collections (array, object, map, set, record)
   - Advanced types (union, intersection, discriminated unions)
   - Optional/nullable patterns
   - Branded types and recursive schemas

2. **[Error Handling](./error-handling.md)** - Robust error management
   - Custom error messages
   - Internationalization (i18n)
   - Error formatting for UI display
   - Safe parsing patterns
   - Error recovery strategies

3. **[Refinements](./refinements.md)** - Custom validation logic
   - Basic and chained refinements
   - Cross-field validation
   - Conditional validation
   - Business logic validation
   - File upload validation

4. **[Transforms](./transforms.md)** - Data transformation and normalization
   - Type coercion
   - Data cleaning and normalization
   - Computed fields
   - Preprocessing patterns

5. **[Async Validation](./async-validation.md)** - Asynchronous validation patterns
   - Database uniqueness checks
   - API validations
   - Concurrent async validations
   - Error handling and timeouts

6. **[Type Inference](./type-inference.md)** - TypeScript type extraction
   - z.infer patterns
   - Input vs output types
   - Generic schema types
   - Discriminated union inference

7. **[API Integration](./api-integration.md)** - Next.js integration patterns
   - API routes validation
   - Server Actions validation
   - Form data and file uploads
   - Error response formatting

8. **[Common Schemas](./common-schemas.md)** - Reusable schema library
   - Email, password, phone validation
   - URL, UUID, date schemas
   - Address, credit card validation
   - Username, slug, color schemas

## Quick Start

### Basic Usage

```typescript
import { z } from 'zod'

// Define schema
const userSchema = z.object({
  email: z.string().email(),
  age: z.number().int().positive(),
  role: z.enum(['admin', 'user'])
})

// Parse data (throws on error)
const user = userSchema.parse(data)

// Safe parse (returns result object)
const result = userSchema.safeParse(data)
if (result.success) {
  console.log(result.data)
} else {
  console.error(result.error)
}
```

### Type Inference

```typescript
// Extract TypeScript type from schema
type User = z.infer<typeof userSchema>
// { email: string; age: number; role: 'admin' | 'user' }
```

### API Route Example

```typescript
// src/app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

const createUserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

export async function POST(request: NextRequest) {
  const body = await request.json()

  const result = createUserSchema.safeParse(body)
  if (!result.success) {
    return NextResponse.json(
      { error: 'Validation failed', details: result.error.format() },
      { status: 400 }
    )
  }

  // Process validated data
  const { email, password } = result.data
  // ...
}
```

## When to Use This Skill

### DO Use for:
- **API request validation** - All incoming data to API routes
- **Form submission validation** - Client and server-side
- **Database input validation** - Before inserting/updating
- **Configuration validation** - Environment variables, config files
- **File upload validation** - Size, type, content validation
- **External API responses** - Validate third-party data

### DON'T Use for:
- **Simple type checks** - Use TypeScript types when validation isn't needed
- **Runtime performance-critical paths** - Validation has overhead
- **Already validated data** - Don't re-validate trusted internal data

## Best Practices

1. **Validate at boundaries** - API routes, Server Actions, external data sources
2. **Use safe parsing** - Prefer `safeParse()` over `parse()` for better error handling
3. **Provide clear error messages** - Customize messages for user-facing validation
4. **Reuse common schemas** - Use schemas from `common-schemas.md`
5. **Type inference** - Always use `z.infer<typeof schema>` for TypeScript types
6. **Test edge cases** - Write tests for validation logic
7. **Document complex schemas** - Add JSDoc comments for business rules

## Common Patterns

### 1. Optional Fields with Defaults

```typescript
const configSchema = z.object({
  timeout: z.number().int().positive().default(30),
  retries: z.number().int().min(0).default(3),
  debug: z.boolean().optional()
})
```

### 2. Conditional Required Fields

```typescript
const addressSchema = z.object({
  country: z.string(),
  state: z.string().optional()
}).refine(
  data => data.country === 'US' ? !!data.state : true,
  { message: 'State is required for US addresses', path: ['state'] }
)
```

### 3. Transform and Validate

```typescript
const emailSchema = z.string()
  .trim()
  .toLowerCase()
  .email()
```

### 4. Discriminated Unions

```typescript
const eventSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('click'), x: z.number(), y: z.number() }),
  z.object({ type: z.literal('keypress'), key: z.string() })
])
```

### 5. Async Database Check

```typescript
const usernameSchema = z.string()
  .min(3)
  .max(20)
  .regex(/^[a-zA-Z0-9_-]+$/)
  .refine(async (username) => {
    const existing = await db.user.findUnique({ where: { username } })
    return !existing
  }, { message: 'Username already taken' })
```

## Integration with Quetrex

### TypeScript Strict Mode Compliance

All schemas must work with TypeScript strict mode:
- No `any` types
- No `@ts-ignore` comments
- Explicit type inference with `z.infer`

### Testing Requirements

Validation logic requires comprehensive tests:
- **Happy path** - Valid data passes
- **Edge cases** - Boundary values, empty strings, null/undefined
- **Error cases** - Invalid data produces expected errors
- **Custom validations** - All refinements and transforms tested

### Server Actions Pattern

```typescript
'use server'

import { z } from 'zod'

const createProjectSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional()
})

export async function createProject(formData: FormData) {
  const result = createProjectSchema.safeParse({
    name: formData.get('name'),
    description: formData.get('description')
  })

  if (!result.success) {
    return { error: result.error.format() }
  }

  // Process validated data
  return { success: true, data: result.data }
}
```

## Resources

- **Zod Documentation**: https://zod.dev/
- **TypeScript Handbook**: https://www.typescriptlang.org/docs/handbook/
- **Next.js Server Actions**: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations

## Navigation

Start with:
1. **[Schema Patterns](./schema-patterns.md)** - Learn all schema types
2. **[Common Schemas](./common-schemas.md)** - Use ready-made schemas
3. **[API Integration](./api-integration.md)** - Integrate with Next.js

Then explore:
- **[Error Handling](./error-handling.md)** - Better error messages
- **[Refinements](./refinements.md)** - Custom validation logic
- **[Transforms](./transforms.md)** - Data transformation
- **[Async Validation](./async-validation.md)** - Database/API checks
- **[Type Inference](./type-inference.md)** - Advanced TypeScript patterns

---

*Last updated: 2025-11-23 | Zod v4.1.12*
