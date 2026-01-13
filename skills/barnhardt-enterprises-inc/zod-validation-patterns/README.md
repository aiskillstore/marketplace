# Zod Validation Patterns - Complete Skill Summary

## Overview

Comprehensive Zod validation skill for Quetrex providing production-ready patterns for all input validation scenarios.

## Statistics

- **Total Files**: 9 (including SKILL.md index)
- **Total Lines**: 8,018
- **Total Code Examples**: 351+
- **Ready-to-Use Schemas**: 20+
- **Documentation Size**: 171 KB

## File Breakdown

### 1. SKILL.md (271 lines, 9 examples)
Entry point and quick start guide
- Purpose and scope overview
- Quick start examples
- Best practices
- Navigation to all other files

### 2. schema-patterns.md (1,414 lines, 78 examples)
Complete guide to ALL Zod schema types
- String validation (email, url, uuid, regex, etc.)
- Number validation (int, positive, range, etc.)
- Boolean, Date, Array, Object validation
- Enum, Literal, Union, Intersection
- Tuple, Record, Map, Set
- Optional, Nullable, Default values
- Branded types, Recursive schemas
- Discriminated unions

### 3. error-handling.md (977 lines, 32 examples)
Robust error management patterns
- Default and custom error messages
- Error map customization
- Internationalization (i18n)
- Error formatting for UI/API
- Error flattening
- Safe parsing patterns
- Try-catch best practices
- Error recovery strategies

### 4. refinements.md (943 lines, 37 examples)
Custom validation logic
- Basic and chained refinements
- Cross-field validation
- Conditional validation
- Business logic validation
- File upload validation
- Date range validation
- Uniqueness checks
- Complex validation patterns

### 5. transforms.md (776 lines, 43 examples)
Data transformation and normalization
- Basic transformations (trim, case conversion)
- Type coercion (string to number, etc.)
- Data normalization (phone, email, URL)
- Default value injection
- Data cleaning
- Computed fields
- Date/JSON/URL parsing
- Transform pipelines

### 6. async-validation.md (828 lines, 29 examples)
Asynchronous validation patterns
- Async refinements
- Database uniqueness checks
- Email/URL verification
- API validations
- Error and timeout handling
- Concurrent validations
- Caching strategies (TTL, LRU, Redis)
- Advanced patterns (debounce, batch, retry)

### 7. type-inference.md (863 lines, 38 examples)
TypeScript type extraction
- z.infer basics
- Input vs output types
- Type extraction from complex schemas
- Discriminated union inference
- Recursive type inference
- Branded types
- Generic schema types
- Utility types and advanced patterns

### 8. api-integration.md (938 lines, 26 examples)
Next.js integration patterns
- API route validation (GET, POST, PATCH, DELETE)
- Server Actions with FormData
- Middleware validation
- Request body, query params, path params
- Form data validation
- File upload validation
- Error response formatting
- Try-catch patterns

### 9. common-schemas.md (1,008 lines, 59 examples)
Ready-to-use validation library
- Email (basic, business, disposable check)
- Password (strength levels, confirmation)
- Phone (US, international)
- URL (basic, HTTPS, with path)
- UUID, CUID (basic and branded)
- Date (ISO, range, future/past, birthdate)
- Currency (USD, multi-currency, price range)
- Address (US, international)
- Credit Card (Luhn, CVV, expiry, full card)
- Username (basic, reserved check)
- Slug (URL-safe, auto-generate)
- Hex Color (6-char, 8-char with alpha, RGB)
- IP Address (v4, v6, both)
- JSON (string parsing, typed)
- File Upload (image, document, avatar)
- Pagination (basic, with sorting, cursor-based)
- Social Media (Twitter, Instagram, GitHub)
- Tax IDs (SSN, EIN)
- Timezone (IANA, UTC offset)

## Reusable Schemas (20+)

### Authentication & User Data
1. `emailSchema` - RFC 5322 compliant email
2. `passwordSchema` - Strong password with all requirements
3. `passwordWithConfirmationSchema` - Password + confirmation
4. `usernameSchema` - Alphanumeric with constraints
5. `birthdateSchema` - 18+ age verification

### Contact Information
6. `usPhoneSchema` - US phone number normalization
7. `internationalPhoneSchema` - E.164 format
8. `usAddressSchema` - Complete US address
9. `internationalAddressSchema` - Global address

### Identifiers
10. `uuidSchema` - UUID v4 validation
11. `userIdSchema` - Branded UUID for users
12. `slugSchema` - URL-safe slug
13. `cuidSchema` - CUID v2 validation

### Web & URLs
14. `urlSchema` - URL with auto-HTTPS
15. `secureUrlSchema` - HTTPS only
16. `hexColorSchema` - #RRGGBB format
17. `ipAddressSchema` - IPv4/IPv6

### Payment
18. `creditCardNumberSchema` - Luhn algorithm validation
19. `cvvSchema` - CVV validation
20. `usdCurrencySchema` - USD with 2 decimal places

### Files & Media
21. `imageFileSchema` - Image upload (JPEG, PNG, WebP)
22. `documentFileSchema` - Document upload (PDF, Word)
23. `avatarSchema` - Avatar with dimension check

### API & Data
24. `paginationSchema` - Page + limit
25. `jsonStringSchema` - JSON parsing
26. `isoDateSchema` - ISO date string to Date

## Coverage Checklist

### String Validation
- [x] Email (RFC 5322)
- [x] URL (with protocol normalization)
- [x] UUID v4
- [x] CUID v2
- [x] Regex patterns
- [x] Length constraints (min, max, exact)
- [x] String transformations (trim, lowercase, uppercase)
- [x] Starts/ends with
- [x] Contains/includes
- [x] DateTime (ISO 8601)
- [x] IP address (v4, v6)

### Number Validation
- [x] Integer validation
- [x] Range constraints (min, max, gt, gte, lt, lte)
- [x] Positive/negative/nonnegative/nonpositive
- [x] Finite numbers
- [x] Safe integers
- [x] Multiple of
- [x] Currency (2 decimal places)

### Complex Types
- [x] Arrays (with length constraints)
- [x] Objects (strict, strip, passthrough)
- [x] Enums (string and native)
- [x] Literals
- [x] Unions (OR logic)
- [x] Intersections (AND logic)
- [x] Tuples (fixed-length arrays)
- [x] Records (key-value pairs)
- [x] Maps and Sets
- [x] Discriminated unions

### Advanced Features
- [x] Optional/nullable/nullish fields
- [x] Default values (static and computed)
- [x] Branded types (nominal typing)
- [x] Recursive schemas (trees, linked lists)
- [x] Type inference (z.infer)
- [x] Input vs output types
- [x] Generic schema types

### Validation Patterns
- [x] Basic refinements
- [x] Chained refinements
- [x] Cross-field validation
- [x] Conditional validation
- [x] Business logic validation
- [x] File upload validation
- [x] Async validation (database, API)
- [x] Uniqueness checks

### Transformations
- [x] Type coercion
- [x] Data normalization
- [x] Data cleaning
- [x] Computed fields
- [x] Date parsing
- [x] JSON parsing
- [x] URL parsing
- [x] Transform pipelines

### Error Handling
- [x] Custom error messages
- [x] Error maps
- [x] Internationalization
- [x] Error formatting for UI
- [x] Error flattening
- [x] Safe parsing
- [x] Try-catch patterns
- [x] Error recovery

### Next.js Integration
- [x] API routes (all methods)
- [x] Server Actions
- [x] Middleware
- [x] Query parameters
- [x] Path parameters
- [x] Form data
- [x] File uploads
- [x] Error responses

## Usage Guide

### 1. Quick Start

```typescript
import { z } from 'zod'

// Define schema
const userSchema = z.object({
  email: z.string().email(),
  age: z.number().int().positive()
})

// Validate data
const user = userSchema.parse(data)

// Safe parse
const result = userSchema.safeParse(data)
if (result.success) {
  console.log(result.data)
}
```

### 2. Use Common Schemas

```typescript
import { emailSchema, passwordSchema } from '@/lib/schemas'

const registerSchema = z.object({
  email: emailSchema,
  password: passwordSchema
})
```

### 3. API Route Integration

```typescript
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const body = await request.json()
  const result = schema.safeParse(body)

  if (!result.success) {
    return NextResponse.json(
      { error: result.error.format() },
      { status: 400 }
    )
  }

  // Process validated data
  return NextResponse.json({ success: true })
}
```

### 4. Server Action

```typescript
'use server'

export async function createUser(formData: FormData) {
  const result = userSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email')
  })

  if (!result.success) {
    return { success: false, errors: result.error.flatten().fieldErrors }
  }

  // Process
  return { success: true }
}
```

## When to Use This Skill

### Use for:
- API request validation
- Form submission validation
- Database input validation
- Configuration validation
- File upload validation
- External API response validation

### Don't use for:
- Simple type checks (use TypeScript)
- Performance-critical paths
- Already validated data

## Best Practices

1. **Validate at boundaries** - API routes, Server Actions, external data
2. **Use safe parsing** - Prefer `safeParse()` over `parse()`
3. **Provide clear errors** - Customize messages for users
4. **Reuse schemas** - Import from common-schemas.md
5. **Type inference** - Always use `z.infer<typeof schema>`
6. **Test thoroughly** - Edge cases, boundary values
7. **Document complexity** - JSDoc for business rules

## Resources

- **Zod Documentation**: https://zod.dev/
- **TypeScript Handbook**: https://www.typescriptlang.org/docs/handbook/
- **Next.js Server Actions**: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations

## Navigation

Start with:
1. **SKILL.md** - Overview and quick start
2. **common-schemas.md** - Ready-to-use schemas (FASTEST WAY)
3. **api-integration.md** - Next.js integration

Deep dive:
4. **schema-patterns.md** - All schema types
5. **error-handling.md** - Better error messages
6. **refinements.md** - Custom validation
7. **transforms.md** - Data transformation
8. **async-validation.md** - Database/API checks
9. **type-inference.md** - TypeScript patterns

---

*Last updated: 2025-11-23 | Zod v4.1.12*
