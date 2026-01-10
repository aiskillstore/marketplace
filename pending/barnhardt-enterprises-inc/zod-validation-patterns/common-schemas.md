# Common Schemas - Reusable Validation Library

This document provides 15+ production-ready validation schemas that can be imported and used directly in your application.

## Table of Contents

- [Email Schema](#email-schema)
- [Password Schema](#password-schema)
- [Phone Schema](#phone-schema)
- [URL Schema](#url-schema)
- [UUID Schema](#uuid-schema)
- [CUID Schema](#cuid-schema)
- [Date Schema](#date-schema)
- [Currency Schema](#currency-schema)
- [Address Schema](#address-schema)
- [Credit Card Schema](#credit-card-schema)
- [Username Schema](#username-schema)
- [Slug Schema](#slug-schema)
- [Hex Color Schema](#hex-color-schema)
- [IP Address Schema](#ip-address-schema)
- [JSON Schema](#json-schema)
- [File Upload Schema](#file-upload-schema)
- [Pagination Schema](#pagination-schema)
- [Social Media Handles](#social-media-handles)
- [Tax ID Schemas](#tax-id-schemas)
- [Timezone Schema](#timezone-schema)

---

## Email Schema

### Basic Email

```typescript
import { z } from 'zod'

export const emailSchema = z.string()
  .trim()
  .toLowerCase()
  .email('Invalid email address')

// Usage
type Email = z.infer<typeof emailSchema>
```

### Business Email (Company Domain)

```typescript
export function createBusinessEmailSchema(domain: string) {
  return z.string()
    .email()
    .refine(
      email => email.endsWith(`@${domain}`),
      { message: `Email must be from ${domain} domain` }
    )
}

// Usage
const companyEmailSchema = createBusinessEmailSchema('company.com')
```

### Email with Disposable Check

```typescript
const DISPOSABLE_DOMAINS = new Set([
  'tempmail.com',
  '10minutemail.com',
  'guerrillamail.com',
  'mailinator.com',
  'throwaway.email'
])

export const verifiedEmailSchema = z.string()
  .email()
  .refine(
    email => {
      const domain = email.split('@')[1]
      return !DISPOSABLE_DOMAINS.has(domain)
    },
    { message: 'Disposable email addresses are not allowed' }
  )
```

---

## Password Schema

### Strong Password

```typescript
export const passwordSchema = z.string()
  .min(8, 'Password must be at least 8 characters')
  .max(100, 'Password is too long')
  .refine(
    val => /[A-Z]/.test(val),
    { message: 'Password must contain at least one uppercase letter' }
  )
  .refine(
    val => /[a-z]/.test(val),
    { message: 'Password must contain at least one lowercase letter' }
  )
  .refine(
    val => /[0-9]/.test(val),
    { message: 'Password must contain at least one number' }
  )
  .refine(
    val => /[^A-Za-z0-9]/.test(val),
    { message: 'Password must contain at least one special character' }
  )

// Usage
type Password = z.infer<typeof passwordSchema>
```

### Password with Confirmation

```typescript
export const passwordWithConfirmationSchema = z.object({
  password: passwordSchema,
  confirmPassword: z.string()
}).refine(
  data => data.password === data.confirmPassword,
  {
    message: "Passwords don't match",
    path: ['confirmPassword']
  }
)

type PasswordWithConfirmation = z.infer<typeof passwordWithConfirmationSchema>
```

### Password Strength Levels

```typescript
export const weakPasswordSchema = z.string().min(6)

export const mediumPasswordSchema = z.string()
  .min(8)
  .refine(val => /[A-Z]/.test(val) && /[a-z]/.test(val))

export const strongPasswordSchema = passwordSchema // From above
```

---

## Phone Schema

### US Phone Number

```typescript
export const usPhoneSchema = z.string()
  .regex(/^\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$/, 'Invalid US phone number')
  .transform(phone => phone.replace(/\D/g, '')) // Remove non-digits

// Accepts: (555) 123-4567, 555-123-4567, 5551234567, +1 555 123 4567
// Returns: 5551234567
```

### International Phone Number

```typescript
export const internationalPhoneSchema = z.string()
  .regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number format')
  .transform(phone => phone.replace(/\D/g, ''))

// E.164 format: +1234567890
```

### Phone with Country Code

```typescript
export const phoneWithCountrySchema = z.object({
  countryCode: z.string().regex(/^\+\d{1,3}$/),
  number: z.string().regex(/^\d{6,14}$/)
}).transform(data => `${data.countryCode}${data.number}`)

// Usage
type PhoneWithCountry = z.infer<typeof phoneWithCountrySchema>
// Input: { countryCode: '+1', number: '5551234567' }
// Output: '+15551234567'
```

---

## URL Schema

### Basic URL

```typescript
export const urlSchema = z.string()
  .url('Invalid URL format')
  .transform(url => {
    // Ensure https if no protocol
    if (!url.match(/^https?:\/\//i)) {
      return `https://${url}`
    }
    return url
  })
```

### HTTPS Only

```typescript
export const secureUrlSchema = z.string()
  .url()
  .refine(
    url => url.startsWith('https://'),
    { message: 'URL must use HTTPS' }
  )
```

### URL with Path Validation

```typescript
export function createUrlWithPathSchema(allowedPaths: string[]) {
  return z.string()
    .url()
    .refine(
      url => {
        const pathname = new URL(url).pathname
        return allowedPaths.some(path => pathname.startsWith(path))
      },
      { message: 'URL path not allowed' }
    )
}

// Usage
const apiUrlSchema = createUrlWithPathSchema(['/api/v1', '/api/v2'])
```

---

## UUID Schema

### UUID v4

```typescript
export const uuidSchema = z.string().uuid('Invalid UUID format')

type UUID = z.infer<typeof uuidSchema>
```

### Branded UUID

```typescript
export const userIdSchema = z.string().uuid().brand<'UserId'>()
export const postIdSchema = z.string().uuid().brand<'PostId'>()
export const commentIdSchema = z.string().uuid().brand<'CommentId'>()

type UserId = z.infer<typeof userIdSchema>
type PostId = z.infer<typeof postIdSchema>
type CommentId = z.infer<typeof commentIdSchema>

// These types are incompatible with each other
function getUser(id: UserId) { /* ... */ }
getUser(userIdSchema.parse('...')) // ✅ Works
// getUser(postIdSchema.parse('...')) // ❌ Type error
```

---

## CUID Schema

### CUID v2

```typescript
export const cuidSchema = z.string().cuid2('Invalid CUID format')

type CUID = z.infer<typeof cuidSchema>
```

### Branded CUID

```typescript
export const resourceIdSchema = z.string().cuid2().brand<'ResourceId'>()

type ResourceId = z.infer<typeof resourceIdSchema>
```

---

## Date Schema

### ISO Date String

```typescript
export const isoDateSchema = z.string()
  .datetime('Invalid ISO date format')
  .transform(str => new Date(str))

type ISODate = z.infer<typeof isoDateSchema>
```

### Date Range

```typescript
export const dateRangeSchema = z.object({
  startDate: z.date(),
  endDate: z.date()
}).refine(
  data => data.endDate >= data.startDate,
  {
    message: 'End date must be after or equal to start date',
    path: ['endDate']
  }
)

type DateRange = z.infer<typeof dateRangeSchema>
```

### Future Date Only

```typescript
export const futureDateSchema = z.date().min(
  new Date(),
  'Date must be in the future'
)
```

### Past Date Only

```typescript
export const pastDateSchema = z.date().max(
  new Date(),
  'Date must be in the past'
)
```

### Birthdate (18+ validation)

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

export const birthdateSchema = z.date()
  .max(new Date(), 'Birthdate cannot be in the future')
  .refine(
    date => calculateAge(date) >= 18,
    { message: 'You must be at least 18 years old' }
  )

type Birthdate = z.infer<typeof birthdateSchema>
```

---

## Currency Schema

### USD Currency

```typescript
export const usdCurrencySchema = z.number()
  .positive('Amount must be positive')
  .multipleOf(0.01, 'Amount must have at most 2 decimal places')
  .max(999999.99, 'Amount is too large')

type USDAmount = z.infer<typeof usdCurrencySchema>
```

### Multi-Currency

```typescript
export const currencySchema = z.object({
  amount: z.number().positive().multipleOf(0.01),
  currency: z.enum(['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD'])
})

type Currency = z.infer<typeof currencySchema>

// Usage
const price: Currency = { amount: 19.99, currency: 'USD' }
```

### Price Range

```typescript
export function createPriceRangeSchema(min: number, max: number) {
  return z.number()
    .positive()
    .multipleOf(0.01)
    .min(min, `Price must be at least $${min}`)
    .max(max, `Price cannot exceed $${max}`)
}

const productPriceSchema = createPriceRangeSchema(0.01, 9999.99)
```

---

## Address Schema

### US Address

```typescript
export const usAddressSchema = z.object({
  street: z.string().min(1, 'Street address is required'),
  street2: z.string().optional(),
  city: z.string().min(1, 'City is required'),
  state: z.string().length(2, 'State must be 2-letter code').toUpperCase(),
  zipCode: z.string().regex(/^\d{5}(-\d{4})?$/, 'Invalid ZIP code'),
  country: z.literal('US')
})

type USAddress = z.infer<typeof usAddressSchema>
```

### International Address

```typescript
export const internationalAddressSchema = z.object({
  street: z.string().min(1),
  street2: z.string().optional(),
  city: z.string().min(1),
  state: z.string().optional(),
  postalCode: z.string().min(1),
  country: z.string().length(2) // ISO 3166-1 alpha-2
})

type InternationalAddress = z.infer<typeof internationalAddressSchema>
```

### Full Address with Validation

```typescript
export const fullAddressSchema = z.object({
  street: z.string().min(1),
  city: z.string().min(1),
  state: z.string().optional(),
  zipCode: z.string().optional(),
  country: z.string().length(2)
}).refine(
  data => {
    // US addresses require state and zip
    if (data.country === 'US') {
      return !!data.state && !!data.zipCode
    }
    return true
  },
  {
    message: 'US addresses require state and ZIP code',
    path: ['state']
  }
)
```

---

## Credit Card Schema

### Credit Card Number (Luhn Algorithm)

```typescript
function luhnCheck(cardNumber: string): boolean {
  const digits = cardNumber.replace(/\D/g, '')
  let sum = 0
  let isEven = false

  for (let i = digits.length - 1; i >= 0; i--) {
    let digit = parseInt(digits[i], 10)

    if (isEven) {
      digit *= 2
      if (digit > 9) digit -= 9
    }

    sum += digit
    isEven = !isEven
  }

  return sum % 10 === 0
}

export const creditCardNumberSchema = z.string()
  .regex(/^\d{13,19}$/, 'Invalid card number format')
  .refine(luhnCheck, { message: 'Invalid credit card number' })

type CreditCardNumber = z.infer<typeof creditCardNumberSchema>
```

### CVV

```typescript
export const cvvSchema = z.string().regex(/^\d{3,4}$/, 'CVV must be 3 or 4 digits')
```

### Expiry Date

```typescript
export const expiryDateSchema = z.object({
  month: z.number().int().min(1).max(12),
  year: z.number().int()
}).refine(
  data => {
    const now = new Date()
    const currentYear = now.getFullYear()
    const currentMonth = now.getMonth() + 1

    if (data.year < currentYear) return false
    if (data.year === currentYear && data.month < currentMonth) return false
    return true
  },
  {
    message: 'Card has expired',
    path: ['month']
  }
)

type ExpiryDate = z.infer<typeof expiryDateSchema>
```

### Full Credit Card

```typescript
export const fullCreditCardSchema = z.object({
  number: creditCardNumberSchema,
  cvv: cvvSchema,
  expiry: expiryDateSchema,
  holderName: z.string().min(1, 'Cardholder name is required')
})

type FullCreditCard = z.infer<typeof fullCreditCardSchema>
```

---

## Username Schema

### Basic Username

```typescript
export const usernameSchema = z.string()
  .min(3, 'Username must be at least 3 characters')
  .max(20, 'Username must be at most 20 characters')
  .regex(
    /^[a-zA-Z0-9_-]+$/,
    'Username can only contain letters, numbers, underscores, and hyphens'
  )
  .transform(val => val.toLowerCase())

type Username = z.infer<typeof usernameSchema>
```

### Username with Reserved Check

```typescript
const RESERVED_USERNAMES = new Set([
  'admin', 'root', 'system', 'moderator',
  'support', 'help', 'api', 'www'
])

export const validatedUsernameSchema = usernameSchema
  .refine(
    username => !RESERVED_USERNAMES.has(username.toLowerCase()),
    { message: 'This username is reserved' }
  )
```

---

## Slug Schema

### URL-Safe Slug

```typescript
export const slugSchema = z.string()
  .min(1)
  .max(100)
  .regex(
    /^[a-z0-9-]+$/,
    'Slug can only contain lowercase letters, numbers, and hyphens'
  )
  .refine(
    slug => !slug.startsWith('-') && !slug.endsWith('-'),
    { message: 'Slug cannot start or end with a hyphen' }
  )

type Slug = z.infer<typeof slugSchema>
```

### Generate Slug from Title

```typescript
export const titleToSlugSchema = z.string()
  .min(1)
  .transform(title =>
    title
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim()
  )
  .pipe(slugSchema)

// Usage
const slug = titleToSlugSchema.parse('Hello World! 123') // 'hello-world-123'
```

---

## Hex Color Schema

### Hex Color Code

```typescript
export const hexColorSchema = z.string()
  .regex(/^#[0-9A-Fa-f]{6}$/, 'Invalid hex color format')
  .transform(val => val.toUpperCase())

type HexColor = z.infer<typeof hexColorSchema>

// Usage
const color = hexColorSchema.parse('#ff5733') // '#FF5733'
```

### Hex Color with Alpha

```typescript
export const hexColorAlphaSchema = z.string()
  .regex(/^#[0-9A-Fa-f]{8}$/, 'Invalid hex color format with alpha')
  .transform(val => val.toUpperCase())

// Example: #FF5733FF
```

### RGB Color

```typescript
export const rgbColorSchema = z.object({
  r: z.number().int().min(0).max(255),
  g: z.number().int().min(0).max(255),
  b: z.number().int().min(0).max(255)
})

type RGBColor = z.infer<typeof rgbColorSchema>
```

---

## IP Address Schema

### IPv4

```typescript
export const ipv4Schema = z.string().ip({ version: 'v4' })

type IPv4 = z.infer<typeof ipv4Schema>
```

### IPv6

```typescript
export const ipv6Schema = z.string().ip({ version: 'v6' })

type IPv6 = z.infer<typeof ipv6Schema>
```

### IP Address (v4 or v6)

```typescript
export const ipAddressSchema = z.string().ip()

type IPAddress = z.infer<typeof ipAddressSchema>
```

---

## JSON Schema

### Valid JSON String

```typescript
export const jsonStringSchema = z.string().transform((str, ctx) => {
  try {
    return JSON.parse(str)
  } catch {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'Invalid JSON'
    })
    return z.NEVER
  }
})

type JSONString = z.infer<typeof jsonStringSchema>
```

### JSON with Type Validation

```typescript
export function createTypedJsonSchema<T extends z.ZodTypeAny>(schema: T) {
  return z.string()
    .transform((str, ctx) => {
      try {
        return JSON.parse(str)
      } catch {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: 'Invalid JSON'
        })
        return z.NEVER
      }
    })
    .pipe(schema)
}

// Usage
const userJsonSchema = createTypedJsonSchema(z.object({
  name: z.string(),
  email: z.string().email()
}))
```

---

## File Upload Schema

### Image File

```typescript
const MAX_IMAGE_SIZE = 5 * 1024 * 1024 // 5MB
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']

export const imageFileSchema = z.instanceof(File)
  .refine(
    file => file.size <= MAX_IMAGE_SIZE,
    { message: 'Image must be less than 5MB' }
  )
  .refine(
    file => ALLOWED_IMAGE_TYPES.includes(file.type),
    { message: 'Only JPEG, PNG, and WebP images are allowed' }
  )

type ImageFile = z.infer<typeof imageFileSchema>
```

### Document File

```typescript
const MAX_DOC_SIZE = 10 * 1024 * 1024 // 10MB
const ALLOWED_DOC_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

export const documentFileSchema = z.instanceof(File)
  .refine(
    file => file.size <= MAX_DOC_SIZE,
    { message: 'Document must be less than 10MB' }
  )
  .refine(
    file => ALLOWED_DOC_TYPES.includes(file.type),
    { message: 'Only PDF and Word documents are allowed' }
  )
```

### Avatar Upload

```typescript
export const avatarSchema = z.instanceof(File)
  .refine(file => file.size <= 2 * 1024 * 1024, 'Avatar must be less than 2MB')
  .refine(
    file => ['image/jpeg', 'image/png'].includes(file.type),
    'Only JPEG and PNG images allowed'
  )
  .refine(
    async file => {
      // Check dimensions
      const img = await createImageBitmap(file)
      return img.width >= 200 && img.height >= 200
    },
    'Image must be at least 200x200 pixels'
  )
```

---

## Pagination Schema

### Basic Pagination

```typescript
export const paginationSchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20)
})

type Pagination = z.infer<typeof paginationSchema>
```

### Pagination with Sorting

```typescript
export function createPaginationSchema<T extends string>(
  sortFields: readonly [T, ...T[]]
) {
  return z.object({
    page: z.coerce.number().int().positive().default(1),
    limit: z.coerce.number().int().positive().max(100).default(20),
    sortBy: z.enum(sortFields).default(sortFields[0]),
    sortOrder: z.enum(['asc', 'desc']).default('desc')
  })
}

// Usage
const userPaginationSchema = createPaginationSchema([
  'createdAt', 'name', 'email'
] as const)

type UserPagination = z.infer<typeof userPaginationSchema>
```

### Cursor-Based Pagination

```typescript
export const cursorPaginationSchema = z.object({
  cursor: z.string().optional(),
  limit: z.coerce.number().int().positive().max(100).default(20)
})

type CursorPagination = z.infer<typeof cursorPaginationSchema>
```

---

## Social Media Handles

### Twitter Handle

```typescript
export const twitterHandleSchema = z.string()
  .min(1)
  .max(15)
  .regex(/^@?[a-zA-Z0-9_]+$/, 'Invalid Twitter handle')
  .transform(handle => handle.startsWith('@') ? handle.slice(1) : handle)

type TwitterHandle = z.infer<typeof twitterHandleSchema>
```

### Instagram Handle

```typescript
export const instagramHandleSchema = z.string()
  .min(1)
  .max(30)
  .regex(/^@?[a-zA-Z0-9._]+$/, 'Invalid Instagram handle')
  .transform(handle => handle.startsWith('@') ? handle.slice(1) : handle)
```

### GitHub Username

```typescript
export const githubUsernameSchema = z.string()
  .min(1)
  .max(39)
  .regex(/^[a-zA-Z0-9-]+$/, 'Invalid GitHub username')
```

---

## Tax ID Schemas

### US SSN

```typescript
export const ssnSchema = z.string()
  .regex(/^\d{3}-\d{2}-\d{4}$/, 'SSN must be in format XXX-XX-XXXX')
  .refine(
    val => {
      const [area, group, serial] = val.split('-')
      return area !== '000' &&
             area !== '666' &&
             parseInt(area) < 900 &&
             group !== '00' &&
             serial !== '0000'
    },
    { message: 'Invalid SSN number' }
  )

type SSN = z.infer<typeof ssnSchema>
```

### US EIN

```typescript
export const einSchema = z.string()
  .regex(/^\d{2}-\d{7}$/, 'EIN must be in format XX-XXXXXXX')
  .refine(
    val => {
      const prefix = parseInt(val.split('-')[0])
      return prefix >= 1 && prefix <= 99
    },
    { message: 'Invalid EIN number' }
  )

type EIN = z.infer<typeof einSchema>
```

---

## Timezone Schema

### IANA Timezone

```typescript
const COMMON_TIMEZONES = [
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'Europe/London',
  'Europe/Paris',
  'Asia/Tokyo',
  'Australia/Sydney'
] as const

export const timezoneSchema = z.enum(COMMON_TIMEZONES)

type Timezone = z.infer<typeof timezoneSchema>
```

### UTC Offset

```typescript
export const utcOffsetSchema = z.string()
  .regex(/^[+-]\d{2}:\d{2}$/, 'Invalid UTC offset format')

// Examples: +05:30, -08:00
```

---

## Usage Examples

### Import and Use

```typescript
import { emailSchema, passwordSchema, usernameSchema } from '@/lib/schemas'

const registerSchema = z.object({
  username: usernameSchema,
  email: emailSchema,
  password: passwordSchema
})

// Extend existing schemas
const extendedEmailSchema = emailSchema
  .refine(async email => {
    const exists = await checkEmailExists(email)
    return !exists
  }, 'Email already registered')
```

### Combine Schemas

```typescript
import { addressSchema, phoneSchema, emailSchema } from '@/lib/schemas'

const contactInfoSchema = z.object({
  email: emailSchema,
  phone: phoneSchema,
  address: addressSchema
})
```

### Create Schema Library File

```typescript
// src/lib/schemas/index.ts
export * from './email'
export * from './password'
export * from './phone'
export * from './address'
export * from './payment'
export * from './user'
// ... etc
```

---

## Summary

This document provided:
- ✅ 20+ production-ready validation schemas
- ✅ Email, password, phone validation
- ✅ URL, UUID, date schemas
- ✅ Address and payment validation
- ✅ File upload schemas
- ✅ Pagination patterns
- ✅ Social media and tax ID validation
- ✅ All schemas ready to copy and use

**Next Steps:**
- **[API Integration](./api-integration.md)** - Use schemas in Next.js
- **[Schema Patterns](./schema-patterns.md)** - Learn all schema types
- **[Type Inference](./type-inference.md)** - Extract TypeScript types

---

*Last updated: 2025-11-23 | Zod v4.1.12*
