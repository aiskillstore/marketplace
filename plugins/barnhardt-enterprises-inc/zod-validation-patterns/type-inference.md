# Type Inference - TypeScript Type Extraction

This document covers all type inference patterns in Zod for extracting TypeScript types from schemas.

## Table of Contents

- [Basic Type Inference](#basic-type-inference)
- [Input vs Output Types](#input-vs-output-types)
- [Type Extraction](#type-extraction)
- [Schema to TypeScript](#schema-to-typescript)
- [Discriminated Union Inference](#discriminated-union-inference)
- [Recursive Type Inference](#recursive-type-inference)
- [Branded Type Inference](#branded-type-inference)
- [Generic Schema Types](#generic-schema-types)
- [Utility Types](#utility-types)
- [Advanced Patterns](#advanced-patterns)

---

## Basic Type Inference

### z.infer

```typescript
import { z } from 'zod'

// Basic schema
const userSchema = z.object({
  name: z.string(),
  age: z.number(),
  email: z.string().email()
})

// Extract TypeScript type
type User = z.infer<typeof userSchema>
// {
//   name: string
//   age: number
//   email: string
// }

// Use the type
const user: User = {
  name: 'John',
  age: 30,
  email: 'john@example.com'
}
```

### Primitive Types

```typescript
const stringSchema = z.string()
type StringType = z.infer<typeof stringSchema> // string

const numberSchema = z.number()
type NumberType = z.infer<typeof numberSchema> // number

const booleanSchema = z.boolean()
type BooleanType = z.infer<typeof booleanSchema> // boolean

const dateSchema = z.date()
type DateType = z.infer<typeof dateSchema> // Date
```

### Array Types

```typescript
const stringArraySchema = z.array(z.string())
type StringArray = z.infer<typeof stringArraySchema> // string[]

const userArraySchema = z.array(z.object({
  id: z.string(),
  name: z.string()
}))
type UserArray = z.infer<typeof userArraySchema>
// Array<{ id: string; name: string }>
```

### Enum Types

```typescript
const roleSchema = z.enum(['admin', 'user', 'guest'])
type Role = z.infer<typeof roleSchema> // 'admin' | 'user' | 'guest'

const nativeEnumSchema = z.nativeEnum({
  Admin: 'ADMIN',
  User: 'USER'
} as const)
type NativeRole = z.infer<typeof nativeEnumSchema> // 'ADMIN' | 'USER'
```

### Literal Types

```typescript
const literalSchema = z.literal('hello')
type Literal = z.infer<typeof literalSchema> // 'hello'

const trueLiteralSchema = z.literal(true)
type TrueLiteral = z.infer<typeof trueLiteralSchema> // true (not boolean)

const numberLiteralSchema = z.literal(42)
type NumberLiteral = z.infer<typeof numberLiteralSchema> // 42
```

---

## Input vs Output Types

### z.input and z.output

```typescript
// Schema with transform
const processedSchema = z.string()
  .transform(val => val.toLowerCase())
  .pipe(z.string().min(1))

// Input type (before transform)
type Input = z.input<typeof processedSchema> // string

// Output type (after transform)
type Output = z.output<typeof processedSchema> // string

// Example with type change
const numberTransformSchema = z.string()
  .transform(val => parseInt(val, 10))

type NumberInput = z.input<typeof numberTransformSchema> // string
type NumberOutput = z.output<typeof numberTransformSchema> // number
```

### Default Values

```typescript
const configSchema = z.object({
  timeout: z.number().default(30),
  retries: z.number().default(3)
})

type ConfigInput = z.input<typeof configSchema>
// { timeout?: number; retries?: number }

type ConfigOutput = z.output<typeof configSchema>
// { timeout: number; retries: number }
```

### Optional vs Required

```typescript
const userSchema = z.object({
  name: z.string(),
  age: z.number().optional(),
  email: z.string().nullable()
})

type User = z.infer<typeof userSchema>
// {
//   name: string
//   age?: number
//   email: string | null
// }
```

---

## Type Extraction

### Extract from Nested Objects

```typescript
const addressSchema = z.object({
  street: z.string(),
  city: z.string(),
  country: z.string()
})

const userWithAddressSchema = z.object({
  name: z.string(),
  address: addressSchema
})

type UserWithAddress = z.infer<typeof userWithAddressSchema>
// {
//   name: string
//   address: {
//     street: string
//     city: string
//     country: string
//   }
// }

// Extract nested type
type Address = z.infer<typeof addressSchema>
```

### Extract from Union

```typescript
const stringOrNumberSchema = z.union([z.string(), z.number()])
type StringOrNumber = z.infer<typeof stringOrNumberSchema> // string | number

const shapeUnionSchema = z.union([
  z.object({ type: z.literal('circle'), radius: z.number() }),
  z.object({ type: z.literal('rectangle'), width: z.number(), height: z.number() })
])

type Shape = z.infer<typeof shapeUnionSchema>
// | { type: 'circle'; radius: number }
// | { type: 'rectangle'; width: number; height: number }
```

### Extract from Intersection

```typescript
const personSchema = z.object({
  name: z.string(),
  age: z.number()
})

const employeeSchema = z.object({
  employeeId: z.string(),
  department: z.string()
})

const employeePersonSchema = personSchema.and(employeeSchema)

type EmployeePerson = z.infer<typeof employeePersonSchema>
// {
//   name: string
//   age: number
//   employeeId: string
//   department: string
// }
```

---

## Schema to TypeScript

### Pick and Omit

```typescript
const fullUserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  password: z.string(),
  role: z.enum(['admin', 'user'])
})

const publicUserSchema = fullUserSchema.pick({
  id: true,
  name: true,
  email: true
})

type PublicUser = z.infer<typeof publicUserSchema>
// { id: string; name: string; email: string }

const userWithoutPasswordSchema = fullUserSchema.omit({
  password: true
})

type SafeUser = z.infer<typeof userWithoutPasswordSchema>
// { id: string; name: string; email: string; role: 'admin' | 'user' }
```

### Partial

```typescript
const requiredUserSchema = z.object({
  name: z.string(),
  age: z.number(),
  email: z.string().email()
})

const partialUserSchema = requiredUserSchema.partial()

type PartialUser = z.infer<typeof partialUserSchema>
// {
//   name?: string
//   age?: number
//   email?: string
// }

// Partial specific fields
const specificPartialSchema = requiredUserSchema.partial({
  age: true,
  email: true
})

type SpecificPartial = z.infer<typeof specificPartialSchema>
// {
//   name: string
//   age?: number
//   email?: string
// }
```

### Required

```typescript
const optionalUserSchema = z.object({
  name: z.string().optional(),
  age: z.number().optional(),
  email: z.string().optional()
})

const requiredSchema = optionalUserSchema.required()

type RequiredUser = z.infer<typeof requiredSchema>
// {
//   name: string
//   age: number
//   email: string
// }
```

---

## Discriminated Union Inference

### Basic Discriminated Union

```typescript
const eventSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('click'),
    x: z.number(),
    y: z.number()
  }),
  z.object({
    type: z.literal('keypress'),
    key: z.string()
  })
])

type Event = z.infer<typeof eventSchema>
// | { type: 'click'; x: number; y: number }
// | { type: 'keypress'; key: string }

// Type narrowing works!
function handleEvent(event: Event) {
  if (event.type === 'click') {
    console.log(event.x, event.y) // TypeScript knows these exist
  } else {
    console.log(event.key) // TypeScript knows this exists
  }
}
```

### Complex Discriminated Union

```typescript
const apiResponseSchema = z.discriminatedUnion('status', [
  z.object({
    status: z.literal('success'),
    data: z.object({
      id: z.string(),
      name: z.string()
    })
  }),
  z.object({
    status: z.literal('error'),
    error: z.object({
      code: z.string(),
      message: z.string()
    })
  }),
  z.object({
    status: z.literal('loading')
  })
])

type ApiResponse = z.infer<typeof apiResponseSchema>

function handleResponse(response: ApiResponse) {
  switch (response.status) {
    case 'success':
      console.log(response.data.name) // ✅ TypeScript knows 'data' exists
      break
    case 'error':
      console.log(response.error.message) // ✅ TypeScript knows 'error' exists
      break
    case 'loading':
      // response only has 'status' property
      break
  }
}
```

---

## Recursive Type Inference

### Tree Structure

```typescript
interface Category {
  name: string
  subcategories: Category[]
}

const categorySchema: z.ZodType<Category> = z.lazy(() =>
  z.object({
    name: z.string(),
    subcategories: z.array(categorySchema)
  })
)

type InferredCategory = z.infer<typeof categorySchema>
// {
//   name: string
//   subcategories: InferredCategory[]
// }
```

### Linked List

```typescript
interface LinkedListNode {
  value: number
  next: LinkedListNode | null
}

const linkedListSchema: z.ZodType<LinkedListNode> = z.lazy(() =>
  z.object({
    value: z.number(),
    next: linkedListSchema.nullable()
  })
)

type InferredNode = z.infer<typeof linkedListSchema>
// {
//   value: number
//   next: InferredNode | null
// }
```

### JSON Value

```typescript
type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue }

const jsonValueSchema: z.ZodType<JsonValue> = z.lazy(() =>
  z.union([
    z.string(),
    z.number(),
    z.boolean(),
    z.null(),
    z.array(jsonValueSchema),
    z.record(jsonValueSchema)
  ])
)

type InferredJsonValue = z.infer<typeof jsonValueSchema>
```

---

## Branded Type Inference

### Basic Branded Types

```typescript
const UserIdSchema = z.string().uuid().brand<'UserId'>()
type UserId = z.infer<typeof UserIdSchema>

const PostIdSchema = z.string().uuid().brand<'PostId'>()
type PostId = z.infer<typeof PostIdSchema>

// Types are incompatible
const userId: UserId = UserIdSchema.parse('...')
const postId: PostId = PostIdSchema.parse('...')

function getUser(id: UserId) { /* ... */ }

getUser(userId) // ✅ Works
getUser(postId) // ❌ Type error
```

### Multiple Branded Types

```typescript
const EmailSchema = z.string().email().brand<'Email'>()
type Email = z.infer<typeof EmailSchema>

const UrlSchema = z.string().url().brand<'Url'>()
type Url = z.infer<typeof UrlSchema>

const PositiveIntSchema = z.number().int().positive().brand<'PositiveInt'>()
type PositiveInt = z.infer<typeof PositiveIntSchema>

// Each type is nominally distinct
function sendEmail(to: Email, subject: string) { /* ... */ }
function fetchUrl(url: Url) { /* ... */ }
function repeat(times: PositiveInt) { /* ... */ }
```

---

## Generic Schema Types

### Generic Schema Function

```typescript
function createListSchema<T extends z.ZodTypeAny>(itemSchema: T) {
  return z.object({
    items: z.array(itemSchema),
    total: z.number(),
    page: z.number()
  })
}

const userSchema = z.object({
  id: z.string(),
  name: z.string()
})

const userListSchema = createListSchema(userSchema)

type UserList = z.infer<typeof userListSchema>
// {
//   items: Array<{ id: string; name: string }>
//   total: number
//   page: number
// }
```

### Generic Wrapper

```typescript
function createResponseSchema<T extends z.ZodTypeAny>(dataSchema: T) {
  return z.object({
    success: z.boolean(),
    data: dataSchema.optional(),
    error: z.string().optional()
  })
}

const userResponseSchema = createResponseSchema(z.object({
  id: z.string(),
  name: z.string()
}))

type UserResponse = z.infer<typeof userResponseSchema>
// {
//   success: boolean
//   data?: { id: string; name: string }
//   error?: string
// }
```

### Generic with Constraints

```typescript
function createTimestampedSchema<
  T extends z.ZodRawShape
>(shape: T) {
  return z.object({
    ...shape,
    createdAt: z.date(),
    updatedAt: z.date()
  })
}

const timestampedUserSchema = createTimestampedSchema({
  id: z.string(),
  name: z.string()
})

type TimestampedUser = z.infer<typeof timestampedUserSchema>
// {
//   id: string
//   name: string
//   createdAt: Date
//   updatedAt: Date
// }
```

---

## Utility Types

### Unwrap Arrays

```typescript
const arraySchema = z.array(z.object({
  id: z.string(),
  name: z.string()
}))

type ArrayType = z.infer<typeof arraySchema>
// Array<{ id: string; name: string }>

// Extract element type
type ElementType = ArrayType[number]
// { id: string; name: string }
```

### Unwrap Promise

```typescript
const promiseSchema = z.promise(z.object({
  id: z.string(),
  name: z.string()
}))

type PromiseType = z.infer<typeof promiseSchema>
// Promise<{ id: string; name: string }>

// Extract resolved type
type ResolvedType = Awaited<PromiseType>
// { id: string; name: string }
```

### Record Types

```typescript
const recordSchema = z.record(z.string(), z.number())

type RecordType = z.infer<typeof recordSchema>
// Record<string, number>

// Extract key and value types
type KeyType = keyof RecordType // string
type ValueType = RecordType[string] // number
```

### Tuple Types

```typescript
const tupleSchema = z.tuple([z.string(), z.number(), z.boolean()])

type TupleType = z.infer<typeof tupleSchema>
// [string, number, boolean]

// Extract individual types
type FirstType = TupleType[0] // string
type SecondType = TupleType[1] // number
type ThirdType = TupleType[2] // boolean
```

---

## Advanced Patterns

### Conditional Types

```typescript
type ExtractOptional<T extends z.ZodTypeAny> =
  T extends z.ZodOptional<infer U> ? U : T

const optionalStringSchema = z.string().optional()
type Extracted = ExtractOptional<typeof optionalStringSchema>
// ZodString
```

### Merge Schema Types

```typescript
const baseSchema = z.object({
  id: z.string(),
  createdAt: z.date()
})

const extendedSchema = baseSchema.extend({
  name: z.string(),
  email: z.string().email()
})

type Extended = z.infer<typeof extendedSchema>
// {
//   id: string
//   createdAt: Date
//   name: string
//   email: string
// }
```

### Deep Partial

```typescript
const nestedSchema = z.object({
  user: z.object({
    name: z.string(),
    address: z.object({
      street: z.string(),
      city: z.string()
    })
  })
})

const deepPartialSchema = nestedSchema.deepPartial()

type DeepPartial = z.infer<typeof deepPartialSchema>
// {
//   user?: {
//     name?: string
//     address?: {
//       street?: string
//       city?: string
//     }
//   }
// }
```

### Schema Shape Access

```typescript
const userSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email()
})

// Access shape
type UserShape = typeof userSchema.shape
// {
//   id: ZodString
//   name: ZodString
//   email: ZodString
// }

// Extract individual field schema
type EmailSchema = typeof userSchema.shape.email
// ZodString

// Infer field type
type EmailType = z.infer<typeof userSchema.shape.email>
// string
```

### Enum Values

```typescript
const roleSchema = z.enum(['admin', 'user', 'guest'])

// Get enum values
type RoleEnum = typeof roleSchema.enum
// { admin: 'admin'; user: 'user'; guest: 'guest' }

// Get specific value
type AdminRole = typeof roleSchema.enum.admin
// 'admin'

// Get all options
type RoleOptions = typeof roleSchema.options
// ['admin', 'user', 'guest']
```

### Infer from Refinement

```typescript
const emailSchema = z.string()
  .email()
  .refine(val => val.endsWith('@company.com'))

type Email = z.infer<typeof emailSchema>
// string (refinements don't change the type)

// For stricter typing, use branded types
const companyEmailSchema = z.string()
  .email()
  .refine(val => val.endsWith('@company.com'))
  .brand<'CompanyEmail'>()

type CompanyEmail = z.infer<typeof companyEmailSchema>
// string & Brand<'CompanyEmail'>
```

### Function Schema

```typescript
const funcSchema = z.function()
  .args(z.string(), z.number())
  .returns(z.boolean())

type FuncType = z.infer<typeof funcSchema>
// (args_0: string, args_1: number) => boolean

// Use as function signature
const myFunc: FuncType = (str, num) => str.length === num
```

---

## TypeScript Integration

### Type Guards

```typescript
const userSchema = z.object({
  name: z.string(),
  email: z.string().email()
})

function isUser(obj: unknown): obj is z.infer<typeof userSchema> {
  return userSchema.safeParse(obj).success
}

// Usage
if (isUser(data)) {
  // TypeScript knows data is { name: string; email: string }
  console.log(data.email)
}
```

### Assertion Functions

```typescript
function assertUser(obj: unknown): asserts obj is z.infer<typeof userSchema> {
  userSchema.parse(obj)
}

// Usage
assertUser(data)
// After this line, TypeScript knows data is User
console.log(data.email)
```

### Type Predicates

```typescript
function validateUser(data: unknown): data is z.infer<typeof userSchema> {
  try {
    userSchema.parse(data)
    return true
  } catch {
    return false
  }
}
```

---

## Summary

This document covered:
- ✅ Basic type inference with z.infer
- ✅ Input vs output types for transforms
- ✅ Type extraction from complex schemas
- ✅ Discriminated union type narrowing
- ✅ Recursive type inference
- ✅ Branded types for nominal typing
- ✅ Generic schema types
- ✅ Utility types and advanced patterns
- ✅ TypeScript integration (type guards, assertions)

**Next Steps:**
- **[API Integration](./api-integration.md)** - Use in Next.js routes
- **[Common Schemas](./common-schemas.md)** - Ready-to-use patterns
- **[Schema Patterns](./schema-patterns.md)** - All schema types

---

*Last updated: 2025-11-23 | Zod v4.1.12*
