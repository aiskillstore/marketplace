# Transforms - Data Transformation

This document covers all transformation patterns in Zod for cleaning, normalizing, and transforming validated data.

## Table of Contents

- [Basic Transform](#basic-transform)
- [Type Coercion](#type-coercion)
- [Data Normalization](#data-normalization)
- [Default Value Injection](#default-value-injection)
- [Data Cleaning](#data-cleaning)
- [Computed Fields](#computed-fields)
- [Date Parsing and Formatting](#date-parsing-and-formatting)
- [JSON Parsing](#json-parsing)
- [URL Parsing](#url-parsing)
- [Transform with Validation](#transform-with-validation)

---

## Basic Transform

### Simple Transformations

```typescript
import { z } from 'zod'

// String transformations
const lowercaseSchema = z.string().transform(val => val.toLowerCase())

const uppercaseSchema = z.string().transform(val => val.toUpperCase())

const trimmedSchema = z.string().transform(val => val.trim())

// Number transformations
const doubleSchema = z.number().transform(val => val * 2)

const roundedSchema = z.number().transform(val => Math.round(val))

const absoluteSchema = z.number().transform(val => Math.abs(val))
```

### Chained Transformations

```typescript
// Multiple transforms in sequence
const normalizedEmailSchema = z.string()
  .transform(val => val.trim())
  .transform(val => val.toLowerCase())

// Combined with validation
const emailSchema = z.string()
  .transform(val => val.trim())
  .transform(val => val.toLowerCase())
  .pipe(z.string().email())
```

### Transform with Type Change

```typescript
// String to number
const stringToNumberSchema = z.string().transform(val => parseInt(val, 10))

// String to array
const csvSchema = z.string().transform(val => val.split(','))

// Array to set
const arrayToSetSchema = z.array(z.string()).transform(val => new Set(val))

// Object to array
const objectToArraySchema = z.record(z.number()).transform(obj =>
  Object.entries(obj).map(([key, value]) => ({ key, value }))
)
```

---

## Type Coercion

### Coerce to Number

```typescript
// String to number (built-in)
const numberSchema = z.coerce.number()

numberSchema.parse('123') // 123
numberSchema.parse(123) // 123
numberSchema.parse('12.5') // 12.5

// With validation
const positiveNumberSchema = z.coerce.number().positive()

const priceSchema = z.coerce.number().positive().multipleOf(0.01)
```

### Coerce to Boolean

```typescript
// String/number to boolean
const boolSchema = z.coerce.boolean()

boolSchema.parse(true) // true
boolSchema.parse('true') // true
boolSchema.parse(1) // true
boolSchema.parse(false) // false
boolSchema.parse('false') // false
boolSchema.parse(0) // false
```

### Coerce to Date

```typescript
// String/number to Date
const dateSchema = z.coerce.date()

dateSchema.parse('2024-01-01') // Date object
dateSchema.parse(1704067200000) // Date object
dateSchema.parse(new Date()) // Date object

// With validation
const futureDateSchema = z.coerce.date().min(new Date())
```

### Coerce to String

```typescript
// Any value to string
const stringSchema = z.coerce.string()

stringSchema.parse(123) // '123'
stringSchema.parse(true) // 'true'
stringSchema.parse(null) // 'null'
```

### Custom Coercion

```typescript
// Custom coercion logic
const parseIntSchema = z.string().transform(val => {
  const parsed = parseInt(val, 10)
  if (isNaN(parsed)) {
    throw new Error('Invalid number')
  }
  return parsed
})

const parseFloatSchema = z.string().transform(val => {
  const parsed = parseFloat(val)
  if (isNaN(parsed)) {
    throw new Error('Invalid number')
  }
  return parsed
})
```

---

## Data Normalization

### Phone Number Normalization

```typescript
function normalizePhoneNumber(phone: string): string {
  // Remove all non-digit characters
  return phone.replace(/\D/g, '')
}

const phoneSchema = z.string()
  .transform(normalizePhoneNumber)
  .pipe(z.string().regex(/^\d{10}$/, 'Phone must be 10 digits'))

phoneSchema.parse('(555) 123-4567') // '5551234567'
phoneSchema.parse('555-123-4567') // '5551234567'
```

### Email Normalization

```typescript
const normalizedEmailSchema = z.string()
  .trim()
  .toLowerCase()
  .pipe(z.string().email())

normalizedEmailSchema.parse('  USER@EXAMPLE.COM  ') // 'user@example.com'
```

### URL Normalization

```typescript
function normalizeUrl(url: string): string {
  // Add https:// if no protocol
  if (!url.match(/^https?:\/\//i)) {
    return `https://${url}`
  }
  return url
}

const urlSchema = z.string()
  .transform(normalizeUrl)
  .pipe(z.string().url())

urlSchema.parse('example.com') // 'https://example.com'
urlSchema.parse('http://example.com') // 'http://example.com'
```

### Whitespace Normalization

```typescript
// Trim and collapse multiple spaces
function normalizeWhitespace(text: string): string {
  return text.trim().replace(/\s+/g, ' ')
}

const textSchema = z.string().transform(normalizeWhitespace)

textSchema.parse('  hello    world  ') // 'hello world'
```

### Case Normalization

```typescript
// Title case
function toTitleCase(text: string): string {
  return text.replace(/\w\S*/g, word =>
    word.charAt(0).toUpperCase() + word.substr(1).toLowerCase()
  )
}

const nameSchema = z.string().transform(toTitleCase)

nameSchema.parse('john DOE') // 'John Doe'

// Slug normalization
function toSlug(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim()
}

const slugSchema = z.string().transform(toSlug)

slugSchema.parse('Hello World! 123') // 'hello-world-123'
```

---

## Default Value Injection

### Static Defaults

```typescript
// Simple default
const nameSchema = z.string().default('Anonymous')

nameSchema.parse(undefined) // 'Anonymous'
nameSchema.parse('John') // 'John'

// Object with defaults
const configSchema = z.object({
  timeout: z.number().default(30),
  retries: z.number().default(3),
  debug: z.boolean().default(false)
})

configSchema.parse({})
// { timeout: 30, retries: 3, debug: false }
```

### Dynamic Defaults

```typescript
// Function-based default
const timestampSchema = z.date().default(() => new Date())

const idSchema = z.string().default(() => crypto.randomUUID())

// Context-based default
const userSchema = z.object({
  id: z.string().default(() => crypto.randomUUID()),
  createdAt: z.date().default(() => new Date()),
  role: z.string().default('user')
})
```

### Defaults with Transform

```typescript
// Apply default, then transform
const emailSchema = z.string()
  .default('')
  .transform(val => val.toLowerCase())

// Transform, then apply default
const normalizedSchema = z.string()
  .transform(val => val.trim())
  .pipe(z.string().default('N/A'))
```

---

## Data Cleaning

### Remove Extra Spaces

```typescript
const cleanTextSchema = z.string().transform(val =>
  val.trim().replace(/\s+/g, ' ')
)

cleanTextSchema.parse('  hello    world  ') // 'hello world'
```

### Remove Special Characters

```typescript
const alphanumericSchema = z.string().transform(val =>
  val.replace(/[^a-zA-Z0-9]/g, '')
)

alphanumericSchema.parse('hello-world_123!') // 'helloworld123'
```

### Sanitize HTML

```typescript
function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, '')
}

const sanitizedSchema = z.string().transform(stripHtml)

sanitizedSchema.parse('<p>Hello <b>World</b></p>') // 'Hello World'
```

### Remove Null/Undefined from Objects

```typescript
const cleanObjectSchema = z.record(z.any()).transform(obj => {
  const cleaned: Record<string, any> = {}
  for (const [key, value] of Object.entries(obj)) {
    if (value !== null && value !== undefined) {
      cleaned[key] = value
    }
  }
  return cleaned
})

cleanObjectSchema.parse({ a: 1, b: null, c: undefined, d: 2 })
// { a: 1, d: 2 }
```

### Remove Empty Strings

```typescript
const removeEmptySchema = z.object({
  name: z.string(),
  bio: z.string().optional()
}).transform(data => ({
  name: data.name,
  ...(data.bio && data.bio.trim() !== '' ? { bio: data.bio } : {})
}))
```

---

## Computed Fields

### Full Name from Parts

```typescript
const personSchema = z.object({
  firstName: z.string(),
  lastName: z.string()
}).transform(data => ({
  ...data,
  fullName: `${data.firstName} ${data.lastName}`
}))

type Person = z.infer<typeof personSchema>
// { firstName: string, lastName: string, fullName: string }

personSchema.parse({ firstName: 'John', lastName: 'Doe' })
// { firstName: 'John', lastName: 'Doe', fullName: 'John Doe' }
```

### Calculated Age

```typescript
function calculateAge(birthdate: Date): number {
  const today = new Date()
  let age = today.getFullYear() - birthdate.getFullYear()
  const monthDiff = today.getMonth() - birthdate.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthdate.getDate())) {
    age--
  }
  return age
}

const userSchema = z.object({
  name: z.string(),
  birthdate: z.date()
}).transform(data => ({
  ...data,
  age: calculateAge(data.birthdate)
}))
```

### Price with Tax

```typescript
const TAX_RATE = 0.08

const productSchema = z.object({
  name: z.string(),
  price: z.number()
}).transform(data => ({
  ...data,
  tax: data.price * TAX_RATE,
  total: data.price * (1 + TAX_RATE)
}))

productSchema.parse({ name: 'Widget', price: 100 })
// { name: 'Widget', price: 100, tax: 8, total: 108 }
```

### Duration Calculation

```typescript
const eventSchema = z.object({
  startDate: z.date(),
  endDate: z.date()
}).transform(data => ({
  ...data,
  durationMs: data.endDate.getTime() - data.startDate.getTime(),
  durationDays: Math.ceil(
    (data.endDate.getTime() - data.startDate.getTime()) / (1000 * 60 * 60 * 24)
  )
}))
```

---

## Date Parsing and Formatting

### Parse Date Strings

```typescript
// ISO 8601 string to Date
const isoDateSchema = z.string().transform(val => new Date(val))

// Custom date format
function parseDate(dateStr: string): Date {
  const [month, day, year] = dateStr.split('/')
  return new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
}

const usDateSchema = z.string()
  .regex(/^\d{1,2}\/\d{1,2}\/\d{4}$/)
  .transform(parseDate)

usDateSchema.parse('12/31/2024') // Date object
```

### Format Dates

```typescript
const dateSchema = z.date().transform(date => {
  return date.toISOString().split('T')[0] // YYYY-MM-DD
})

const localeSchema = z.date().transform(date => {
  return date.toLocaleDateString('en-US')
})
```

### Unix Timestamp

```typescript
// Timestamp to Date
const timestampSchema = z.number().transform(ts => new Date(ts * 1000))

// Date to timestamp
const dateToTimestampSchema = z.date().transform(date =>
  Math.floor(date.getTime() / 1000)
)
```

---

## JSON Parsing

### Parse JSON String

```typescript
// Basic JSON parsing
const jsonSchema = z.string().transform(val => JSON.parse(val))

// With validation
const userJsonSchema = z.string()
  .transform(val => JSON.parse(val))
  .pipe(z.object({
    name: z.string(),
    email: z.string().email()
  }))

userJsonSchema.parse('{"name":"John","email":"john@example.com"}')
// { name: 'John', email: 'john@example.com' }
```

### Safe JSON Parsing

```typescript
const safeJsonSchema = z.string().transform((val, ctx) => {
  try {
    return JSON.parse(val)
  } catch {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'Invalid JSON'
    })
    return z.NEVER
  }
})
```

### Stringify Objects

```typescript
const stringifySchema = z.object({
  name: z.string(),
  age: z.number()
}).transform(val => JSON.stringify(val))

stringifySchema.parse({ name: 'John', age: 30 })
// '{"name":"John","age":30}'
```

---

## URL Parsing

### Parse URL Components

```typescript
const urlSchema = z.string().url().transform(urlStr => {
  const url = new URL(urlStr)
  return {
    protocol: url.protocol,
    hostname: url.hostname,
    pathname: url.pathname,
    search: url.search,
    hash: url.hash
  }
})

urlSchema.parse('https://example.com/path?query=1#hash')
// {
//   protocol: 'https:',
//   hostname: 'example.com',
//   pathname: '/path',
//   search: '?query=1',
//   hash: '#hash'
// }
```

### Extract Query Parameters

```typescript
const urlWithParamsSchema = z.string().url().transform(urlStr => {
  const url = new URL(urlStr)
  const params: Record<string, string> = {}
  url.searchParams.forEach((value, key) => {
    params[key] = value
  })
  return { url: urlStr, params }
})

urlWithParamsSchema.parse('https://example.com?name=John&age=30')
// { url: 'https://...', params: { name: 'John', age: '30' } }
```

### Build URL

```typescript
const buildUrlSchema = z.object({
  base: z.string().url(),
  path: z.string(),
  params: z.record(z.string()).optional()
}).transform(data => {
  const url = new URL(data.path, data.base)
  if (data.params) {
    Object.entries(data.params).forEach(([key, value]) => {
      url.searchParams.set(key, value)
    })
  }
  return url.toString()
})
```

---

## Transform with Validation

### Preprocess then Validate

```typescript
// Transform then validate with pipe
const emailSchema = z.string()
  .transform(val => val.trim().toLowerCase())
  .pipe(z.string().email())

// Multiple steps
const strongPasswordSchema = z.string()
  .transform(val => val.trim())
  .pipe(
    z.string()
      .min(8)
      .regex(/[A-Z]/, 'Must contain uppercase')
      .regex(/[a-z]/, 'Must contain lowercase')
      .regex(/[0-9]/, 'Must contain number')
  )
```

### Validate then Transform

```typescript
// Validate first
const validatedSchema = z.string().email()
  .transform(val => val.toLowerCase())

// Ensures transformation only happens on valid data
```

### Transform with Refinement

```typescript
const usernameSchema = z.string()
  .transform(val => val.trim().toLowerCase())
  .pipe(
    z.string()
      .min(3)
      .max(20)
      .regex(/^[a-z0-9_-]+$/)
  )
  .refine(
    async username => {
      const exists = await checkUsernameExists(username)
      return !exists
    },
    { message: 'Username already taken' }
  )
```

### Multi-Step Pipeline

```typescript
const processedSchema = z.string()
  // Step 1: Clean
  .transform(val => val.trim())
  // Step 2: Validate non-empty
  .pipe(z.string().min(1))
  // Step 3: Normalize
  .transform(val => val.toLowerCase())
  // Step 4: Validate format
  .pipe(z.string().regex(/^[a-z0-9-]+$/))
  // Step 5: Transform to slug
  .transform(val => val.replace(/\s+/g, '-'))
```

### Conditional Transform

```typescript
const conditionalSchema = z.object({
  type: z.enum(['uppercase', 'lowercase', 'titlecase']),
  text: z.string()
}).transform(data => {
  let transformed = data.text
  if (data.type === 'uppercase') {
    transformed = transformed.toUpperCase()
  } else if (data.type === 'lowercase') {
    transformed = transformed.toLowerCase()
  } else if (data.type === 'titlecase') {
    transformed = transformed.replace(/\w\S*/g, w =>
      w.charAt(0).toUpperCase() + w.substr(1).toLowerCase()
    )
  }
  return { ...data, result: transformed }
})
```

---

## Advanced Transform Patterns

### Batch Transform Array Elements

```typescript
const normalizedArraySchema = z.array(z.string())
  .transform(arr => arr.map(item => item.trim().toLowerCase()))

normalizedArraySchema.parse(['  HELLO  ', 'WORLD'])
// ['hello', 'world']
```

### Transform Object Keys

```typescript
const camelCaseSchema = z.record(z.any()).transform(obj => {
  const camelCased: Record<string, any> = {}
  for (const [key, value] of Object.entries(obj)) {
    const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
    camelCased[camelKey] = value
  }
  return camelCased
})

camelCaseSchema.parse({ first_name: 'John', last_name: 'Doe' })
// { firstName: 'John', lastName: 'Doe' }
```

### Flatten Nested Objects

```typescript
const flattenSchema = z.object({
  user: z.object({
    name: z.string(),
    email: z.string()
  }),
  meta: z.object({
    created: z.date()
  })
}).transform(data => ({
  userName: data.user.name,
  userEmail: data.user.email,
  created: data.meta.created
}))
```

### Merge and Transform

```typescript
const mergeSchema = z.object({
  defaults: z.record(z.string()),
  overrides: z.record(z.string())
}).transform(data => ({
  ...data.defaults,
  ...data.overrides
}))
```

---

## Summary

This document covered:
- ✅ Basic transformations (trim, lowercase, uppercase)
- ✅ Type coercion (string to number, boolean, date)
- ✅ Data normalization (phone, email, URL, whitespace)
- ✅ Default value injection (static and dynamic)
- ✅ Data cleaning (remove spaces, special chars, HTML)
- ✅ Computed fields (full name, age, price with tax)
- ✅ Date parsing and formatting
- ✅ JSON parsing and stringifying
- ✅ URL parsing and building
- ✅ Transform pipelines with validation

**Next Steps:**
- **[Async Validation](./async-validation.md)** - Database/API checks
- **[Type Inference](./type-inference.md)** - TypeScript types
- **[API Integration](./api-integration.md)** - Use in Next.js

---

*Last updated: 2025-11-23 | Zod v4.1.12*
