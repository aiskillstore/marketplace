# Input Validation Complete Reference

Comprehensive Zod validation patterns for all input types in Next.js applications.

---

## Table of Contents

1. [Basic Validation](#basic-validation)
2. [User Input Validation](#user-input-validation)
3. [File Upload Validation](#file-upload-validation)
4. [API Request Validation](#api-request-validation)
5. [Database Query Validation](#database-query-validation)
6. [Custom Validators](#custom-validators)
7. [Async Validation](#async-validation)
8. [Error Handling](#error-handling)

---

## Basic Validation

### String Validation

```typescript
import { z } from 'zod'

// ✅ Basic string
const stringSchema = z.string()

// ✅ String with length constraints
const usernameSchema = z.string()
  .min(3, 'Username must be at least 3 characters')
  .max(20, 'Username must not exceed 20 characters')

// ✅ Email validation
const emailSchema = z.string()
  .email('Invalid email address')
  .toLowerCase()  // Normalize to lowercase

// ✅ URL validation
const urlSchema = z.string()
  .url('Invalid URL')
  .refine(
    (url) => {
      const parsed = new URL(url)
      return ['http:', 'https:'].includes(parsed.protocol)
    },
    { message: 'Only HTTP and HTTPS URLs are allowed' }
  )

// ✅ UUID validation
const uuidSchema = z.string().uuid('Invalid UUID')

// ✅ Phone number (E.164 format)
const phoneSchema = z.string()
  .regex(/^\+[1-9]\d{1,14}$/, 'Invalid phone number (use E.164 format: +15551234567)')

// ✅ Alphanumeric only
const alphanumericSchema = z.string()
  .regex(/^[a-zA-Z0-9]+$/, 'Only letters and numbers allowed')

// ✅ Slug (URL-friendly)
const slugSchema = z.string()
  .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'Invalid slug format')
  .min(3)
  .max(100)

// ✅ Hex color
const colorSchema = z.string()
  .regex(/^#[0-9A-Fa-f]{6}$/, 'Invalid hex color (e.g., #FF5733)')

// ✅ IP address (v4)
const ipv4Schema = z.string()
  .regex(
    /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
    'Invalid IPv4 address'
  )

// ✅ Date string (ISO 8601)
const dateStringSchema = z.string()
  .datetime({ message: 'Invalid datetime (use ISO 8601 format)' })

// ✅ Non-empty string (trim whitespace)
const nonEmptySchema = z.string()
  .trim()
  .min(1, 'This field is required')
```

### Number Validation

```typescript
// ✅ Basic number
const numberSchema = z.number()

// ✅ Integer only
const integerSchema = z.number().int('Must be an integer')

// ✅ Positive number
const positiveSchema = z.number().positive('Must be positive')

// ✅ Non-negative (0 or positive)
const nonNegativeSchema = z.number().nonnegative('Must be 0 or positive')

// ✅ Number with range
const ageSchema = z.number()
  .int()
  .min(0, 'Age must be at least 0')
  .max(150, 'Age must not exceed 150')

// ✅ Price (2 decimal places)
const priceSchema = z.number()
  .positive('Price must be positive')
  .refine(
    (val) => {
      const decimals = val.toString().split('.')[1]
      return !decimals || decimals.length <= 2
    },
    { message: 'Price must have at most 2 decimal places' }
  )

// ✅ Percentage (0-100)
const percentageSchema = z.number()
  .min(0, 'Percentage must be at least 0')
  .max(100, 'Percentage must not exceed 100')

// ✅ Latitude
const latitudeSchema = z.number()
  .min(-90, 'Latitude must be >= -90')
  .max(90, 'Latitude must be <= 90')

// ✅ Longitude
const longitudeSchema = z.number()
  .min(-180, 'Longitude must be >= -180')
  .max(180, 'Longitude must be <= 180')
```

### Boolean and Enum Validation

```typescript
// ✅ Boolean
const booleanSchema = z.boolean()

// ✅ Boolean with coercion (accepts "true", "false", 0, 1)
const booleanCoerceSchema = z.coerce.boolean()

// ✅ Enum
const roleSchema = z.enum(['ADMIN', 'MANAGER', 'USER', 'GUEST'], {
  errorMap: () => ({ message: 'Invalid role' }),
})

// ✅ Native enum
enum Status {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
}

const statusSchema = z.nativeEnum(Status)

// ✅ Literal values
const literalSchema = z.literal('exact-value')

// ✅ Union of literals
const sortOrderSchema = z.union([
  z.literal('asc'),
  z.literal('desc'),
])
// Or shorter:
const sortOrderSchema2 = z.enum(['asc', 'desc'])
```

### Array Validation

```typescript
// ✅ Array of strings
const tagsSchema = z.array(z.string())

// ✅ Array with length constraints
const tagsMinMaxSchema = z.array(z.string())
  .min(1, 'At least one tag is required')
  .max(10, 'Maximum 10 tags allowed')

// ✅ Non-empty array
const nonEmptyArraySchema = z.array(z.string()).nonempty('Array cannot be empty')

// ✅ Unique array elements
const uniqueTagsSchema = z.array(z.string())
  .refine(
    (arr) => new Set(arr).size === arr.length,
    { message: 'Tags must be unique' }
  )

// ✅ Array of objects
const usersSchema = z.array(
  z.object({
    id: z.string().uuid(),
    name: z.string(),
    email: z.string().email(),
  })
)
```

### Object Validation

```typescript
// ✅ Basic object
const userSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().positive(),
})

// ✅ Optional fields
const userUpdateSchema = z.object({
  email: z.string().email().optional(),
  name: z.string().min(1).max(100).optional(),
  age: z.number().int().positive().optional(),
})

// ✅ Partial object (all fields optional)
const partialUserSchema = userSchema.partial()

// ✅ Required fields (convert optional to required)
const requiredUserSchema = userUpdateSchema.required()

// ✅ Pick specific fields
const userLoginSchema = userSchema.pick({ email: true, password: true })

// ✅ Omit specific fields
const userPublicSchema = userSchema.omit({ password: true })

// ✅ Extend object
const userWithTimestampsSchema = userSchema.extend({
  createdAt: z.date(),
  updatedAt: z.date(),
})

// ✅ Merge objects
const schema1 = z.object({ a: z.string() })
const schema2 = z.object({ b: z.number() })
const mergedSchema = schema1.merge(schema2)  // { a: string, b: number }

// ✅ Nested objects
const addressSchema = z.object({
  street: z.string(),
  city: z.string(),
  state: z.string().length(2),  // US state code
  zipCode: z.string().regex(/^\d{5}(-\d{4})?$/),
})

const userWithAddressSchema = z.object({
  name: z.string(),
  email: z.string().email(),
  address: addressSchema,
})

// ✅ Record (dynamic keys)
const metadataSchema = z.record(z.string(), z.any())

// ✅ Strict object (reject unknown keys)
const strictUserSchema = z.object({
  name: z.string(),
  email: z.string().email(),
}).strict()
```

---

## User Input Validation

### Registration

```typescript
// ✅ Password validation
const passwordSchema = z.string()
  .min(8, 'Password must be at least 8 characters')
  .max(128, 'Password must not exceed 128 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')
  .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character')

// ✅ Registration form
const registerSchema = z.object({
  email: z.string()
    .email('Invalid email address')
    .toLowerCase()
    .max(255, 'Email must not exceed 255 characters'),
  password: passwordSchema,
  confirmPassword: z.string(),
  name: z.string()
    .min(1, 'Name is required')
    .max(100, 'Name must not exceed 100 characters')
    .trim(),
  agreedToTerms: z.literal(true, {
    errorMap: () => ({ message: 'You must agree to the terms and conditions' }),
  }),
}).refine(
  (data) => data.password === data.confirmPassword,
  {
    message: 'Passwords do not match',
    path: ['confirmPassword'],  // Show error on confirmPassword field
  }
)

// Usage
const result = registerSchema.safeParse(formData)
if (!result.success) {
  console.log(result.error.flatten())
}
```

### Login

```typescript
// ✅ Login form
const loginSchema = z.object({
  email: z.string().email('Invalid email address').toLowerCase(),
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional(),
})
```

### Profile Update

```typescript
// ✅ Profile update
const profileUpdateSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  bio: z.string().max(500).optional(),
  website: z.string().url().optional(),
  avatar: z.string().url().optional(),
  location: z.string().max(100).optional(),
  dateOfBirth: z.coerce.date().max(new Date(), 'Date of birth cannot be in the future').optional(),
  phoneNumber: z.string().regex(/^\+[1-9]\d{1,14}$/).optional(),
})
```

### Password Reset

```typescript
// ✅ Password reset request
const passwordResetRequestSchema = z.object({
  email: z.string().email('Invalid email address').toLowerCase(),
})

// ✅ Password reset
const passwordResetSchema = z.object({
  token: z.string().min(1),
  password: passwordSchema,
  confirmPassword: z.string(),
}).refine(
  (data) => data.password === data.confirmPassword,
  {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  }
)
```

---

## File Upload Validation

### Image Upload

```typescript
// ✅ Image file validation
const MAX_FILE_SIZE = 5 * 1024 * 1024  // 5MB
const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']

const imageFileSchema = z.instanceof(File)
  .refine(
    (file) => file.size <= MAX_FILE_SIZE,
    { message: 'File size must not exceed 5MB' }
  )
  .refine(
    (file) => ACCEPTED_IMAGE_TYPES.includes(file.type),
    { message: 'Only JPEG, PNG, and WebP images are allowed' }
  )
  .refine(
    (file) => {
      // Check file extension matches MIME type
      const ext = file.name.split('.').pop()?.toLowerCase()
      const mimeExt = file.type.split('/')[1]
      return ext === mimeExt || (ext === 'jpg' && mimeExt === 'jpeg')
    },
    { message: 'File extension does not match file type' }
  )

// ✅ Multiple images
const multipleImagesSchema = z.array(imageFileSchema)
  .min(1, 'At least one image is required')
  .max(10, 'Maximum 10 images allowed')
```

### Document Upload

```typescript
// ✅ PDF file validation
const MAX_PDF_SIZE = 10 * 1024 * 1024  // 10MB

const pdfFileSchema = z.instanceof(File)
  .refine(
    (file) => file.size <= MAX_PDF_SIZE,
    { message: 'PDF size must not exceed 10MB' }
  )
  .refine(
    (file) => file.type === 'application/pdf',
    { message: 'Only PDF files are allowed' }
  )
  .refine(
    (file) => file.name.endsWith('.pdf'),
    { message: 'File must have .pdf extension' }
  )

// ✅ CSV file validation
const csvFileSchema = z.instanceof(File)
  .refine(
    (file) => file.size <= 5 * 1024 * 1024,
    { message: 'CSV size must not exceed 5MB' }
  )
  .refine(
    (file) => file.type === 'text/csv' || file.type === 'application/csv',
    { message: 'Only CSV files are allowed' }
  )
```

### File Metadata

```typescript
// ✅ File upload with metadata
const fileUploadSchema = z.object({
  file: imageFileSchema,
  title: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
  tags: z.array(z.string()).max(10).optional(),
  visibility: z.enum(['public', 'private', 'organization']),
})
```

---

## API Request Validation

### Pagination

```typescript
// ✅ Pagination parameters
const paginationSchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20),
  sortBy: z.enum(['createdAt', 'updatedAt', 'name', 'email']).default('createdAt'),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
})

// Usage in API route
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)

  const params = paginationSchema.parse({
    page: searchParams.get('page'),
    limit: searchParams.get('limit'),
    sortBy: searchParams.get('sortBy'),
    sortOrder: searchParams.get('sortOrder'),
  })

  // params is now validated and has defaults
  const { page, limit, sortBy, sortOrder } = params
}
```

### Search and Filters

```typescript
// ✅ Search parameters
const searchSchema = z.object({
  query: z.string().min(1).max(100).optional(),
  category: z.string().optional(),
  minPrice: z.coerce.number().nonnegative().optional(),
  maxPrice: z.coerce.number().nonnegative().optional(),
  inStock: z.coerce.boolean().optional(),
  tags: z.string().transform((val) => val.split(',')).optional(),  // Convert "a,b,c" to ["a", "b", "c"]
})
.refine(
  (data) => {
    if (data.minPrice !== undefined && data.maxPrice !== undefined) {
      return data.minPrice <= data.maxPrice
    }
    return true
  },
  { message: 'minPrice must be less than or equal to maxPrice' }
)
```

### Create/Update Resources

```typescript
// ✅ Create project
const createProjectSchema = z.object({
  name: z.string()
    .min(1, 'Name is required')
    .max(100, 'Name must not exceed 100 characters')
    .trim(),
  description: z.string()
    .max(1000, 'Description must not exceed 1000 characters')
    .optional(),
  repository: z.string().url('Invalid repository URL').optional(),
  visibility: z.enum(['public', 'private', 'organization']).default('private'),
  tags: z.array(z.string()).max(10).optional(),
  settings: z.object({
    autoArchive: z.boolean().default(false),
    notificationsEnabled: z.boolean().default(true),
  }).optional(),
})

// ✅ Update project (all fields optional)
const updateProjectSchema = createProjectSchema.partial()

// ✅ Patch project (only specific fields)
const patchProjectSchema = z.object({
  name: z.string().min(1).max(100).trim().optional(),
  description: z.string().max(1000).optional(),
  visibility: z.enum(['public', 'private', 'organization']).optional(),
})
```

---

## Database Query Validation

### Query Parameters

```typescript
// ✅ Database ID validation
const dbIdSchema = z.string()
  .uuid('Invalid ID format')
  .or(z.string().regex(/^[a-zA-Z0-9_-]+$/, 'Invalid ID format'))

// ✅ Find by ID
const findByIdSchema = z.object({
  id: dbIdSchema,
})

// ✅ Find many with filters
const findManySchema = z.object({
  where: z.object({
    userId: dbIdSchema.optional(),
    organizationId: dbIdSchema.optional(),
    status: z.enum(['active', 'archived', 'deleted']).optional(),
    createdAfter: z.coerce.date().optional(),
    createdBefore: z.coerce.date().optional(),
  }).optional(),
  orderBy: z.object({
    field: z.enum(['createdAt', 'updatedAt', 'name']),
    direction: z.enum(['asc', 'desc']),
  }).optional(),
  take: z.number().int().positive().max(100).optional(),
  skip: z.number().int().nonnegative().optional(),
})
```

### Bulk Operations

```typescript
// ✅ Bulk create
const bulkCreateSchema = z.object({
  items: z.array(createProjectSchema)
    .min(1, 'At least one item is required')
    .max(100, 'Maximum 100 items allowed'),
})

// ✅ Bulk update
const bulkUpdateSchema = z.object({
  ids: z.array(dbIdSchema)
    .min(1, 'At least one ID is required')
    .max(100, 'Maximum 100 IDs allowed'),
  data: updateProjectSchema,
})

// ✅ Bulk delete
const bulkDeleteSchema = z.object({
  ids: z.array(dbIdSchema)
    .min(1, 'At least one ID is required')
    .max(100, 'Maximum 100 IDs allowed'),
})
```

---

## Custom Validators

### Email Domain Validation

```typescript
// ✅ Allow only specific email domains
const corporateEmailSchema = z.string()
  .email()
  .refine(
    (email) => {
      const domain = email.split('@')[1]
      return ['company.com', 'company.io'].includes(domain)
    },
    { message: 'Only company email addresses are allowed' }
  )
```

### Username Validation

```typescript
// ✅ Username (letters, numbers, underscores, hyphens)
const usernameSchema = z.string()
  .min(3, 'Username must be at least 3 characters')
  .max(20, 'Username must not exceed 20 characters')
  .regex(/^[a-zA-Z0-9_-]+$/, 'Username can only contain letters, numbers, underscores, and hyphens')
  .regex(/^[a-zA-Z]/, 'Username must start with a letter')
  .refine(
    (username) => !['admin', 'root', 'system', 'test'].includes(username.toLowerCase()),
    { message: 'This username is reserved' }
  )
```

### Credit Card Validation

```typescript
// ✅ Credit card number (Luhn algorithm)
function luhnCheck(cardNumber: string): boolean {
  const digits = cardNumber.replace(/\D/g, '')
  let sum = 0
  let isEven = false

  for (let i = digits.length - 1; i >= 0; i--) {
    let digit = parseInt(digits[i], 10)

    if (isEven) {
      digit *= 2
      if (digit > 9) {
        digit -= 9
      }
    }

    sum += digit
    isEven = !isEven
  }

  return sum % 10 === 0
}

const creditCardSchema = z.string()
  .regex(/^\d{13,19}$/, 'Invalid credit card number')
  .refine(luhnCheck, { message: 'Invalid credit card number' })

// ✅ CVV
const cvvSchema = z.string()
  .regex(/^\d{3,4}$/, 'CVV must be 3 or 4 digits')

// ✅ Expiry date (MM/YY)
const expiryDateSchema = z.string()
  .regex(/^(0[1-9]|1[0-2])\/\d{2}$/, 'Expiry date must be in MM/YY format')
  .refine(
    (expiry) => {
      const [month, year] = expiry.split('/').map(Number)
      const now = new Date()
      const currentYear = now.getFullYear() % 100
      const currentMonth = now.getMonth() + 1

      if (year < currentYear) return false
      if (year === currentYear && month < currentMonth) return false

      return true
    },
    { message: 'Card has expired' }
  )
```

### IP Address Validation

```typescript
// ✅ IPv4
const ipv4Schema = z.string()
  .regex(
    /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
    'Invalid IPv4 address'
  )

// ✅ IPv6
const ipv6Schema = z.string()
  .regex(
    /^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$/,
    'Invalid IPv6 address'
  )

// ✅ IP address (v4 or v6)
const ipSchema = z.union([ipv4Schema, ipv6Schema])
```

---

## Async Validation

### Database Uniqueness Check

```typescript
import { db } from '@/lib/db'

// ✅ Check if email is unique
const uniqueEmailSchema = z.string()
  .email()
  .refine(
    async (email) => {
      const existing = await db.user.findUnique({ where: { email } })
      return !existing
    },
    { message: 'Email is already registered' }
  )

// Usage (must use parseAsync)
const result = await uniqueEmailSchema.parseAsync('test@example.com')
```

### External API Validation

```typescript
// ✅ Validate GitHub username exists
const githubUsernameSchema = z.string()
  .min(1)
  .max(39)
  .refine(
    async (username) => {
      const response = await fetch(`https://api.github.com/users/${username}`)
      return response.ok
    },
    { message: 'GitHub username not found' }
  )
```

### Combined Async Validation

```typescript
// ✅ Registration with uniqueness checks
const registerSchemaAsync = z.object({
  email: z.string()
    .email()
    .refine(
      async (email) => {
        const existing = await db.user.findUnique({ where: { email } })
        return !existing
      },
      { message: 'Email is already registered' }
    ),
  username: z.string()
    .min(3)
    .max(20)
    .refine(
      async (username) => {
        const existing = await db.user.findUnique({ where: { username } })
        return !existing
      },
      { message: 'Username is already taken' }
    ),
  password: passwordSchema,
})

// Usage
export async function POST(request: Request) {
  const body = await request.json()

  // Use parseAsync for async validation
  const validated = await registerSchemaAsync.parseAsync(body)

  // Create user...
}
```

---

## Error Handling

### Format Validation Errors

```typescript
// ✅ Flatten errors for easier display
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

const result = schema.safeParse({ email: 'invalid', password: 'short' })

if (!result.success) {
  const errors = result.error.flatten()
  console.log(errors)
  /*
  {
    formErrors: [],
    fieldErrors: {
      email: ['Invalid email'],
      password: ['String must contain at least 8 character(s)']
    }
  }
  */
}
```

### Custom Error Messages

```typescript
// ✅ Custom error map
const customErrorMap: z.ZodErrorMap = (issue, ctx) => {
  if (issue.code === z.ZodIssueCode.invalid_type) {
    if (issue.expected === 'string') {
      return { message: 'This field must be text' }
    }
  }

  if (issue.code === z.ZodIssueCode.too_small) {
    if (issue.type === 'string') {
      return { message: `This field must be at least ${issue.minimum} characters` }
    }
  }

  return { message: ctx.defaultError }
}

z.setErrorMap(customErrorMap)
```

### Form Error Display

```typescript
// ✅ React form with Zod validation
'use client'

import { useState } from 'react'
import { z } from 'zod'

const formSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

export function LoginForm() {
  const [errors, setErrors] = useState<Record<string, string[]>>({})

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()

    const formData = new FormData(e.currentTarget)
    const data = Object.fromEntries(formData)

    const result = formSchema.safeParse(data)

    if (!result.success) {
      // Set field errors
      setErrors(result.error.flatten().fieldErrors)
      return
    }

    // Submit valid data
    setErrors({})
    // ... submit to API
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input type="email" name="email" />
        {errors.email && <p className="error">{errors.email[0]}</p>}
      </div>

      <div>
        <input type="password" name="password" />
        {errors.password && <p className="error">{errors.password[0]}</p>}
      </div>

      <button type="submit">Login</button>
    </form>
  )
}
```

---

## Summary

**Input validation checklist:**

- [ ] All user input validated with Zod
- [ ] Email addresses normalized (toLowerCase)
- [ ] Passwords meet complexity requirements
- [ ] File uploads checked for size and type
- [ ] URLs verified for valid protocol
- [ ] Arrays have min/max length constraints
- [ ] Numbers have range constraints
- [ ] Strings trimmed and length-limited
- [ ] Async validation for uniqueness
- [ ] Custom error messages user-friendly
- [ ] Validation errors displayed per-field
- [ ] No unvalidated data reaches database
