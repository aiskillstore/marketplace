# Schema Patterns - Complete Guide

This document covers every Zod schema type and pattern for comprehensive input validation.

## Table of Contents

- [String Validation](#string-validation)
- [Number Validation](#number-validation)
- [Boolean Validation](#boolean-validation)
- [Date Validation](#date-validation)
- [Array Validation](#array-validation)
- [Object Validation](#object-validation)
- [Enum Validation](#enum-validation)
- [Literal Validation](#literal-validation)
- [Union Validation](#union-validation)
- [Intersection Validation](#intersection-validation)
- [Tuple Validation](#tuple-validation)
- [Record Validation](#record-validation)
- [Map Validation](#map-validation)
- [Set Validation](#set-validation)
- [Optional Fields](#optional-fields)
- [Default Values](#default-values)
- [Branded Types](#branded-types)
- [Recursive Schemas](#recursive-schemas)
- [Discriminated Unions](#discriminated-unions)

---

## String Validation

### Basic String

```typescript
import { z } from 'zod'

// Basic string
const nameSchema = z.string()

// Non-empty string
const requiredSchema = z.string().min(1)

// String with custom message
const usernameSchema = z.string({
  required_error: 'Username is required',
  invalid_type_error: 'Username must be a string'
})
```

### String Length Constraints

```typescript
// Minimum length
const passwordSchema = z.string().min(8, 'Password must be at least 8 characters')

// Maximum length
const bioSchema = z.string().max(500, 'Bio cannot exceed 500 characters')

// Exact length
const pinSchema = z.string().length(4, 'PIN must be exactly 4 digits')

// Range
const usernameSchema = z.string().min(3).max(20)
```

### Email Validation

```typescript
// Basic email validation
const emailSchema = z.string().email()

// Email with custom message
const emailSchemaCustom = z.string().email('Invalid email address')

// Email with additional constraints
const businessEmailSchema = z.string()
  .email()
  .endsWith('@company.com', 'Must be a company email')
```

### URL Validation

```typescript
// Basic URL
const urlSchema = z.string().url()

// URL with custom message
const websiteSchema = z.string().url('Invalid URL format')

// HTTPS only
const secureUrlSchema = z.string()
  .url()
  .startsWith('https://', 'Only HTTPS URLs allowed')
```

### UUID Validation

```typescript
// UUID v4
const idSchema = z.string().uuid()

// UUID with custom message
const userIdSchema = z.string().uuid('Invalid user ID format')
```

### CUID Validation

```typescript
// CUID (Collision-resistant Unique ID)
const cuidSchema = z.string().cuid()

// CUID2 (newer version)
const cuid2Schema = z.string().cuid2()
```

### Regex Validation

```typescript
// Basic regex
const phoneSchema = z.string().regex(/^\+?[1-9]\d{1,14}$/)

// Regex with custom message
const alphanumericSchema = z.string().regex(
  /^[a-zA-Z0-9]+$/,
  'Only alphanumeric characters allowed'
)

// Username (alphanumeric, underscores, hyphens)
const usernameSchema = z.string().regex(
  /^[a-zA-Z0-9_-]+$/,
  'Username can only contain letters, numbers, underscores, and hyphens'
)

// Hex color
const hexColorSchema = z.string().regex(
  /^#[0-9A-Fa-f]{6}$/,
  'Invalid hex color format'
)
```

### String Starts/Ends With

```typescript
// Starts with
const httpUrlSchema = z.string().startsWith('http://')

// Ends with
const imageFileSchema = z.string().endsWith('.jpg')

// Combined
const httpsImageSchema = z.string()
  .startsWith('https://')
  .endsWith('.png')
```

### String Includes

```typescript
// Contains substring
const codeSchema = z.string().includes('CODE')

// Case-insensitive check (use transform)
const caseInsensitiveSchema = z.string()
  .transform(val => val.toLowerCase())
  .pipe(z.string().includes('keyword'))
```

### String DateTime

```typescript
// ISO 8601 datetime
const datetimeSchema = z.string().datetime()

// With offset
const datetimeOffsetSchema = z.string().datetime({ offset: true })

// With precision
const datetimePrecisionSchema = z.string().datetime({ precision: 3 }) // milliseconds
```

### IP Address

```typescript
// IPv4 or IPv6
const ipSchema = z.string().ip()

// IPv4 only
const ipv4Schema = z.string().ip({ version: 'v4' })

// IPv6 only
const ipv6Schema = z.string().ip({ version: 'v6' })
```

### String Trim

```typescript
// Remove whitespace
const trimmedSchema = z.string().trim()

// Trim and validate
const nameSchema = z.string().trim().min(1)
```

### String Transform

```typescript
// Lowercase
const lowercaseSchema = z.string().toLowerCase()

// Uppercase
const uppercaseSchema = z.string().toUpperCase()

// Combined transformations
const normalizedEmailSchema = z.string()
  .trim()
  .toLowerCase()
  .email()
```

---

## Number Validation

### Basic Number

```typescript
// Basic number
const ageSchema = z.number()

// Number with custom message
const priceSchema = z.number({
  required_error: 'Price is required',
  invalid_type_error: 'Price must be a number'
})
```

### Integer Validation

```typescript
// Integer (no decimals)
const countSchema = z.number().int()

// Integer with message
const quantitySchema = z.number().int('Quantity must be a whole number')
```

### Number Range Constraints

```typescript
// Minimum value
const ageSchema = z.number().min(0, 'Age cannot be negative')

// Maximum value
const percentageSchema = z.number().max(100, 'Percentage cannot exceed 100')

// Exact range
const scoreSchema = z.number().min(0).max(100)

// Greater than (exclusive)
const positiveSchema = z.number().gt(0)

// Greater than or equal
const nonNegativeSchema = z.number().gte(0)

// Less than (exclusive)
const belowMaxSchema = z.number().lt(1000)

// Less than or equal
const maxValueSchema = z.number().lte(999)
```

### Number Type Checks

```typescript
// Positive number (> 0)
const positiveSchema = z.number().positive()

// Negative number (< 0)
const negativeSchema = z.number().negative()

// Non-negative (>= 0)
const nonNegativeSchema = z.number().nonnegative()

// Non-positive (<= 0)
const nonPositiveSchema = z.number().nonpositive()

// Finite number (not Infinity or -Infinity)
const finiteSchema = z.number().finite()

// Safe integer (within JavaScript safe integer range)
const safeIntSchema = z.number().int().safe()
```

### Multiple of

```typescript
// Multiple of 5
const multipleOf5Schema = z.number().multipleOf(5)

// Multiple of 0.01 (for currency)
const currencySchema = z.number().multipleOf(0.01)

// Even number
const evenSchema = z.number().int().multipleOf(2)
```

### Number Coercion

```typescript
// Coerce string to number
const coercedSchema = z.coerce.number()

// Example: "123" -> 123
const result = coercedSchema.parse('123') // 123

// With validation
const priceSchema = z.coerce.number().positive().multipleOf(0.01)
```

---

## Boolean Validation

### Basic Boolean

```typescript
// Basic boolean
const isActiveSchema = z.boolean()

// Boolean with custom message
const acceptTermsSchema = z.boolean({
  required_error: 'You must accept the terms',
  invalid_type_error: 'Invalid value'
})
```

### Boolean Coercion

```typescript
// Coerce to boolean
const coercedBoolSchema = z.coerce.boolean()

// Examples:
// true, 'true', 1 -> true
// false, 'false', 0 -> false
```

### Boolean Refinement

```typescript
// Must be true
const mustAcceptSchema = z.boolean().refine(val => val === true, {
  message: 'You must accept the terms and conditions'
})

// Literal true
const acceptedSchema = z.literal(true)
```

---

## Date Validation

### Basic Date

```typescript
// Basic date
const birthdateSchema = z.date()

// Date with custom message
const eventDateSchema = z.date({
  required_error: 'Event date is required',
  invalid_type_error: 'Invalid date'
})
```

### Date Range Constraints

```typescript
// Minimum date
const futureEventSchema = z.date().min(
  new Date(),
  'Event must be in the future'
)

// Maximum date
const pastEventSchema = z.date().max(
  new Date(),
  'Event must be in the past'
)

// Date range
const validPeriodSchema = z.date()
  .min(new Date('2024-01-01'))
  .max(new Date('2024-12-31'))
```

### Date Coercion

```typescript
// Coerce string/number to date
const coercedDateSchema = z.coerce.date()

// Examples:
// '2024-01-01' -> Date object
// 1704067200000 -> Date object
```

### Date Validation Patterns

```typescript
// 18+ age verification
const eighteenYearsAgo = new Date()
eighteenYearsAgo.setFullYear(eighteenYearsAgo.getFullYear() - 18)

const birthdateSchema = z.date().max(
  eighteenYearsAgo,
  'You must be at least 18 years old'
)

// Event scheduling (7 days in advance)
const sevenDaysFromNow = new Date()
sevenDaysFromNow.setDate(sevenDaysFromNow.getDate() + 7)

const eventDateSchema = z.date().min(
  sevenDaysFromNow,
  'Events must be scheduled at least 7 days in advance'
)
```

---

## Array Validation

### Basic Array

```typescript
// Array of strings
const tagsSchema = z.array(z.string())

// Array of numbers
const scoresSchema = z.array(z.number())

// Array of objects
const usersSchema = z.array(
  z.object({
    id: z.string(),
    name: z.string()
  })
)
```

### Array Length Constraints

```typescript
// Minimum length
const minItemsSchema = z.array(z.string()).min(1, 'At least one item required')

// Maximum length
const maxItemsSchema = z.array(z.string()).max(10, 'Maximum 10 items allowed')

// Exact length
const exactLengthSchema = z.array(z.number()).length(5, 'Must have exactly 5 items')

// Range
const rangeSchema = z.array(z.string()).min(1).max(100)

// Non-empty array
const nonEmptySchema = z.array(z.string()).nonempty('Array cannot be empty')
```

### Array Element Validation

```typescript
// Unique elements
const uniqueTagsSchema = z.array(z.string()).refine(
  arr => new Set(arr).size === arr.length,
  { message: 'Tags must be unique' }
)

// All elements match condition
const positiveNumbersSchema = z.array(z.number().positive())

// Complex element validation
const emailListSchema = z.array(
  z.string().email('Each item must be a valid email')
).min(1)
```

---

## Object Validation

### Basic Object

```typescript
// Simple object
const userSchema = z.object({
  name: z.string(),
  age: z.number(),
  email: z.string().email()
})

// Nested object
const addressSchema = z.object({
  street: z.string(),
  city: z.string(),
  country: z.string(),
  coordinates: z.object({
    lat: z.number(),
    lng: z.number()
  })
})
```

### Object Modes

```typescript
// STRICT mode (default) - unknown keys cause error
const strictSchema = z.object({
  name: z.string()
}).strict()

// STRIP mode - unknown keys removed
const stripSchema = z.object({
  name: z.string()
}).strip()

// PASSTHROUGH mode - unknown keys passed through
const passthroughSchema = z.object({
  name: z.string()
}).passthrough()
```

### Partial Objects

```typescript
// All fields optional
const partialUserSchema = z.object({
  name: z.string(),
  age: z.number(),
  email: z.string().email()
}).partial()

// Equivalent to:
const manualPartialSchema = z.object({
  name: z.string().optional(),
  age: z.number().optional(),
  email: z.string().email().optional()
})

// Partial with specific fields
const partialFieldsSchema = userSchema.partial({
  age: true,
  email: true
})
```

### Required Objects

```typescript
// All fields required (opposite of partial)
const requiredSchema = partialUserSchema.required()

// Specific fields required
const specificRequiredSchema = partialUserSchema.required({
  name: true,
  email: true
})
```

### Pick and Omit

```typescript
const fullUserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  password: z.string(),
  role: z.enum(['admin', 'user'])
})

// Pick specific fields
const publicUserSchema = fullUserSchema.pick({
  id: true,
  name: true,
  email: true
})

// Omit specific fields
const userWithoutPasswordSchema = fullUserSchema.omit({
  password: true
})
```

### Extend Objects

```typescript
const baseUserSchema = z.object({
  name: z.string(),
  email: z.string().email()
})

// Extend with new fields
const extendedUserSchema = baseUserSchema.extend({
  age: z.number(),
  role: z.string()
})

// Override fields
const overrideSchema = baseUserSchema.extend({
  email: z.string() // Now just a string, not email validated
})
```

### Merge Objects

```typescript
const personSchema = z.object({
  name: z.string(),
  age: z.number()
})

const employeeSchema = z.object({
  employeeId: z.string(),
  department: z.string()
})

// Merge two schemas
const employeePersonSchema = personSchema.merge(employeeSchema)
// Result: { name, age, employeeId, department }
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

// Make all nested fields optional
const deepPartialSchema = nestedSchema.deepPartial()
```

---

## Enum Validation

### Basic Enum

```typescript
// Enum from array
const roleSchema = z.enum(['admin', 'user', 'guest'])

// Type inference
type Role = z.infer<typeof roleSchema> // 'admin' | 'user' | 'guest'

// With custom error message
const statusSchema = z.enum(['active', 'inactive'], {
  errorMap: () => ({ message: 'Status must be active or inactive' })
})
```

### Native Enum

```typescript
// TypeScript enum
enum Role {
  Admin = 'ADMIN',
  User = 'USER',
  Guest = 'GUEST'
}

// Validate against native enum
const nativeEnumSchema = z.nativeEnum(Role)

// Numeric enum
enum Status {
  Pending,
  Approved,
  Rejected
}

const numericEnumSchema = z.nativeEnum(Status)
```

### Enum Methods

```typescript
const fruitSchema = z.enum(['apple', 'banana', 'orange'])

// Get enum values
const values = fruitSchema.options // ['apple', 'banana', 'orange']

// Get specific value
const apple = fruitSchema.Enum.apple // 'apple'
```

---

## Literal Validation

### Basic Literal

```typescript
// Single literal value
const acceptedSchema = z.literal(true)
const versionSchema = z.literal('v1')
const portSchema = z.literal(3000)

// Type inference
type Accepted = z.infer<typeof acceptedSchema> // true (not boolean)
```

### Literal Use Cases

```typescript
// API version
const apiVersionSchema = z.literal('2024-01-01')

// Constant values
const productionEnvSchema = z.literal('production')

// Boolean flags that must be true
const termsAcceptedSchema = z.literal(true)

// Specific numbers
const defaultPortSchema = z.literal(8080)
```

---

## Union Validation

### Basic Union (OR)

```typescript
// String or number
const idSchema = z.union([z.string(), z.number()])

// Multiple types
const inputSchema = z.union([
  z.string(),
  z.number(),
  z.boolean()
])

// Shorthand
const shorthandSchema = z.string().or(z.number())
```

### Union with Objects

```typescript
// Different object shapes
const paymentSchema = z.union([
  z.object({
    type: z.literal('card'),
    cardNumber: z.string(),
    cvv: z.string()
  }),
  z.object({
    type: z.literal('paypal'),
    email: z.string().email()
  })
])
```

### Nullable and Optional Unions

```typescript
// Nullable (value or null)
const nullableSchema = z.string().nullable()
// Equivalent to: z.union([z.string(), z.null()])

// Optional (value or undefined)
const optionalSchema = z.string().optional()
// Equivalent to: z.union([z.string(), z.undefined()])

// Nullish (value, null, or undefined)
const nullishSchema = z.string().nullish()
// Equivalent to: z.union([z.string(), z.null(), z.undefined()])
```

---

## Intersection Validation

### Basic Intersection (AND)

```typescript
// Both conditions must be met
const personSchema = z.object({
  name: z.string()
})

const employeeSchema = z.object({
  employeeId: z.string()
})

// Intersection
const employeePersonSchema = z.intersection(
  personSchema,
  employeeSchema
)
// Result: { name: string, employeeId: string }

// Shorthand
const shorthandSchema = personSchema.and(employeeSchema)
```

### Intersection Use Cases

```typescript
// Base + Extension
const baseConfigSchema = z.object({
  timeout: z.number(),
  retries: z.number()
})

const advancedConfigSchema = z.object({
  caching: z.boolean(),
  compression: z.boolean()
})

const fullConfigSchema = baseConfigSchema.and(advancedConfigSchema)
```

---

## Tuple Validation

### Basic Tuple

```typescript
// Fixed-length array with specific types
const coordinatesSchema = z.tuple([z.number(), z.number()])
// [number, number]

// Mixed types
const userTupleSchema = z.tuple([
  z.string(), // name
  z.number(), // age
  z.boolean() // isActive
])
```

### Tuple with Rest

```typescript
// Tuple with variable length tail
const logEntrySchema = z.tuple([
  z.string(), // timestamp
  z.string()  // level
]).rest(z.string()) // ...args

// Type: [string, string, ...string[]]
```

---

## Record Validation

### Basic Record

```typescript
// Record<string, number>
const scoresSchema = z.record(z.string(), z.number())

// Record<string, any> (key only)
const metadataSchema = z.record(z.string())

// Type inference
type Scores = z.infer<typeof scoresSchema> // Record<string, number>
```

### Record with Specific Keys

```typescript
// Enum keys
const colorCodeSchema = z.record(
  z.enum(['red', 'green', 'blue']),
  z.string()
)

// Literal union keys
const configSchema = z.record(
  z.union([z.literal('dev'), z.literal('prod')]),
  z.object({ apiUrl: z.string() })
)
```

### Record Use Cases

```typescript
// User preferences (any key allowed)
const preferencesSchema = z.record(z.string(), z.boolean())

// Translations
const translationsSchema = z.record(z.string(), z.string())

// Configuration map
const envConfigSchema = z.record(
  z.enum(['development', 'staging', 'production']),
  z.object({
    apiUrl: z.string().url(),
    debug: z.boolean()
  })
)
```

---

## Map Validation

### Basic Map

```typescript
// Map<string, number>
const userScoresSchema = z.map(z.string(), z.number())

// Map<number, object>
const usersMapSchema = z.map(
  z.number(),
  z.object({
    name: z.string(),
    email: z.string().email()
  })
)
```

### Map Size Constraints

```typescript
// Minimum entries
const minMapSchema = z.map(z.string(), z.number()).min(1)

// Maximum entries
const maxMapSchema = z.map(z.string(), z.number()).max(100)

// Exact size
const exactMapSchema = z.map(z.string(), z.number()).size(10)
```

---

## Set Validation

### Basic Set

```typescript
// Set<string>
const tagsSetSchema = z.set(z.string())

// Set<number>
const numbersSetSchema = z.set(z.number())
```

### Set Size Constraints

```typescript
// Minimum size
const minSetSchema = z.set(z.string()).min(1, 'At least one tag required')

// Maximum size
const maxSetSchema = z.set(z.string()).max(10, 'Maximum 10 tags allowed')

// Exact size
const exactSetSchema = z.set(z.number()).size(5)
```

### Set Use Cases

```typescript
// Unique tags (Set automatically enforces uniqueness)
const uniqueTagsSchema = z.set(z.string()).min(1)

// Unique IDs
const uniqueIdsSchema = z.set(z.string().uuid())
```

---

## Optional Fields

### Optional

```typescript
// Field can be undefined
const userSchema = z.object({
  name: z.string(),
  age: z.number().optional() // number | undefined
})
```

### Nullable

```typescript
// Field can be null
const userSchema = z.object({
  name: z.string(),
  middleName: z.string().nullable() // string | null
})
```

### Nullish

```typescript
// Field can be null or undefined
const userSchema = z.object({
  name: z.string(),
  nickname: z.string().nullish() // string | null | undefined
})
```

### Optional with Default

```typescript
// Optional field with fallback value
const configSchema = z.object({
  timeout: z.number().optional().default(30),
  retries: z.number().default(3) // implicitly optional
})
```

---

## Default Values

### Basic Default

```typescript
// Primitive defaults
const nameSchema = z.string().default('Anonymous')
const ageSchema = z.number().default(0)
const activeSchema = z.boolean().default(false)

// Object defaults
const configSchema = z.object({
  timeout: z.number().default(30),
  retries: z.number().default(3),
  debug: z.boolean().default(false)
})
```

### Function Defaults

```typescript
// Computed default
const timestampSchema = z.date().default(() => new Date())

// Random default
const idSchema = z.string().default(() => crypto.randomUUID())

// Context-based default
const userSchema = z.object({
  createdAt: z.date().default(() => new Date()),
  id: z.string().default(() => crypto.randomUUID())
})
```

### Default with Optional

```typescript
// Optional field with default (if undefined, use default)
const settingsSchema = z.object({
  theme: z.enum(['light', 'dark']).optional().default('light')
})

// Behavior:
// undefined -> 'light'
// 'dark' -> 'dark'
// null -> error (not optional for null)
```

---

## Branded Types

### Basic Branded Type

```typescript
// Create nominal type
const UserIdSchema = z.string().uuid().brand<'UserId'>()
type UserId = z.infer<typeof UserIdSchema>

const PostIdSchema = z.string().uuid().brand<'PostId'>()
type PostId = z.infer<typeof PostIdSchema>

// TypeScript won't allow mixing
function getUser(id: UserId) { /* ... */ }
const postId = PostIdSchema.parse('...') // PostId
getUser(postId) // ❌ Type error: PostId is not assignable to UserId
```

### Branded Type Use Cases

```typescript
// Email branded type
const EmailSchema = z.string().email().brand<'Email'>()
type Email = z.infer<typeof EmailSchema>

// URL branded type
const UrlSchema = z.string().url().brand<'Url'>()
type Url = z.infer<typeof UrlSchema>

// Positive integer branded type
const PositiveIntSchema = z.number().int().positive().brand<'PositiveInt'>()
type PositiveInt = z.infer<typeof PositiveIntSchema>

// Usage
function sendEmail(to: Email) { /* ... */ }
const email = EmailSchema.parse('user@example.com')
sendEmail(email) // ✅ Works
sendEmail('user@example.com') // ❌ Type error
```

---

## Recursive Schemas

### Basic Recursive Schema

```typescript
// Define base type first
interface Category {
  name: string
  subcategories: Category[]
}

// Create recursive schema
const categorySchema: z.ZodType<Category> = z.lazy(() =>
  z.object({
    name: z.string(),
    subcategories: z.array(categorySchema)
  })
)
```

### Tree Structure

```typescript
interface TreeNode {
  value: string
  children: TreeNode[]
}

const treeNodeSchema: z.ZodType<TreeNode> = z.lazy(() =>
  z.object({
    value: z.string(),
    children: z.array(treeNodeSchema)
  })
)

// Usage
const tree = {
  value: 'root',
  children: [
    {
      value: 'child1',
      children: [
        { value: 'grandchild1', children: [] }
      ]
    },
    { value: 'child2', children: [] }
  ]
}

const validated = treeNodeSchema.parse(tree)
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
```

### JSON Value (Recursive Union)

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
```

---

## Discriminated Unions

### Basic Discriminated Union

```typescript
// Shape distinguished by 'type' field
const eventSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('click'),
    x: z.number(),
    y: z.number()
  }),
  z.object({
    type: z.literal('keypress'),
    key: z.string()
  }),
  z.object({
    type: z.literal('focus'),
    elementId: z.string()
  })
])

// Type inference
type Event = z.infer<typeof eventSchema>
// { type: 'click', x: number, y: number }
// | { type: 'keypress', key: string }
// | { type: 'focus', elementId: string }
```

### API Response Discriminated Union

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

// Type-safe handling
function handleResponse(response: z.infer<typeof apiResponseSchema>) {
  if (response.status === 'success') {
    console.log(response.data.name) // ✅ TypeScript knows 'data' exists
  } else if (response.status === 'error') {
    console.log(response.error.message) // ✅ TypeScript knows 'error' exists
  }
}
```

### Payment Method Discriminated Union

```typescript
const paymentMethodSchema = z.discriminatedUnion('method', [
  z.object({
    method: z.literal('card'),
    cardNumber: z.string().length(16),
    cvv: z.string().length(3),
    expiryMonth: z.number().min(1).max(12),
    expiryYear: z.number()
  }),
  z.object({
    method: z.literal('paypal'),
    email: z.string().email()
  }),
  z.object({
    method: z.literal('bank_transfer'),
    accountNumber: z.string(),
    routingNumber: z.string()
  })
])
```

### User Role Discriminated Union

```typescript
const userSchema = z.discriminatedUnion('role', [
  z.object({
    role: z.literal('admin'),
    permissions: z.array(z.string()),
    canManageUsers: z.boolean()
  }),
  z.object({
    role: z.literal('user'),
    subscription: z.enum(['free', 'pro', 'enterprise'])
  }),
  z.object({
    role: z.literal('guest'),
    expiresAt: z.date()
  })
])
```

---

## Advanced Patterns

### Conditional Schema

```typescript
// Different validation based on condition
function getSchema(userType: 'admin' | 'user') {
  if (userType === 'admin') {
    return z.object({
      username: z.string(),
      permissions: z.array(z.string())
    })
  }
  return z.object({
    username: z.string()
  })
}
```

### Schema Composition

```typescript
// Reusable pieces
const timestampFields = {
  createdAt: z.date(),
  updatedAt: z.date()
}

const userSchema = z.object({
  id: z.string(),
  name: z.string(),
  ...timestampFields
})

const postSchema = z.object({
  id: z.string(),
  title: z.string(),
  ...timestampFields
})
```

### Catch-all Validation

```typescript
// Catch invalid values and replace with default
const safeNumberSchema = z.number().catch(0)

// Example:
safeNumberSchema.parse(123) // 123
safeNumberSchema.parse('invalid') // 0

// Catch with function
const timestampSchema = z.date().catch(() => new Date())
```

### Pipe Transformation

```typescript
// Transform then validate
const trimmedEmailSchema = z.string()
  .transform(val => val.trim().toLowerCase())
  .pipe(z.string().email())

// Multi-step pipeline
const processedSchema = z.string()
  .transform(val => val.trim())
  .pipe(z.string().min(1))
  .transform(val => val.toUpperCase())
```

---

## Summary

This document covered:
- ✅ 19 schema types (string, number, boolean, date, array, object, enum, etc.)
- ✅ 50+ validation patterns
- ✅ Length, range, and type constraints
- ✅ Optional, nullable, and default values
- ✅ Advanced types (branded, recursive, discriminated unions)
- ✅ Schema composition and transformation

**Next Steps:**
- **[Error Handling](./error-handling.md)** - Custom error messages
- **[Common Schemas](./common-schemas.md)** - Ready-to-use schemas
- **[API Integration](./api-integration.md)** - Use in Next.js

---

*Last updated: 2025-11-23 | Zod v4.1.12*
