# Refinements - Custom Validation Logic

This document covers all refinement patterns in Zod for implementing custom validation logic beyond built-in validators.

## Table of Contents

- [Basic Refinement](#basic-refinement)
- [Multiple Refinements](#multiple-refinements)
- [Custom Error Messages](#custom-error-messages)
- [Cross-Field Validation](#cross-field-validation)
- [Conditional Validation](#conditional-validation)
- [Business Logic Validation](#business-logic-validation)
- [File Upload Validation](#file-upload-validation)
- [Date Range Validation](#date-range-validation)
- [Uniqueness Validation](#uniqueness-validation)
- [Complex Validation Patterns](#complex-validation-patterns)

---

## Basic Refinement

### Simple Refinement

```typescript
import { z } from 'zod'

// Basic refinement with boolean return
const evenNumberSchema = z.number().refine(
  val => val % 2 === 0,
  { message: 'Number must be even' }
)

// Without custom message (uses default)
const positiveSchema = z.number().refine(val => val > 0)

// Multiple conditions
const strongPasswordSchema = z.string().refine(
  val => {
    return val.length >= 8 &&
           /[A-Z]/.test(val) &&
           /[a-z]/.test(val) &&
           /[0-9]/.test(val)
  },
  { message: 'Password must be at least 8 characters with uppercase, lowercase, and numbers' }
)
```

### Refinement with Path

```typescript
// Specify which field the error belongs to
const userSchema = z.object({
  username: z.string(),
  email: z.string()
}).refine(
  data => data.username !== data.email,
  {
    message: 'Username and email cannot be the same',
    path: ['username'] // Error will appear on username field
  }
)
```

### Refinement with Function Message

```typescript
const rangeSchema = z.number().refine(
  val => val >= 0 && val <= 100,
  val => ({
    message: `Value ${val} is out of range (0-100)`
  })
)
```

---

## Multiple Refinements

### Chaining Refinements

```typescript
const passwordSchema = z.string()
  .refine(val => val.length >= 8, {
    message: 'Password must be at least 8 characters'
  })
  .refine(val => /[A-Z]/.test(val), {
    message: 'Password must contain at least one uppercase letter'
  })
  .refine(val => /[a-z]/.test(val), {
    message: 'Password must contain at least one lowercase letter'
  })
  .refine(val => /[0-9]/.test(val), {
    message: 'Password must contain at least one number'
  })
  .refine(val => /[^A-Za-z0-9]/.test(val), {
    message: 'Password must contain at least one special character'
  })

// All refinements are checked, all errors returned
```

### Ordered Refinements

```typescript
// Refinements run in order
const schema = z.string()
  .refine(val => val.length > 0, 'Required')
  .refine(val => val.length <= 100, 'Too long')
  .refine(val => /^[a-zA-Z]+$/.test(val), 'Only letters allowed')

// If first fails, subsequent refinements may not run
```

### Combined Refinements

```typescript
const userSchema = z.object({
  email: z.string().email(),
  username: z.string().min(3).max(20)
})
  // First refinement
  .refine(
    data => data.username !== 'admin',
    { message: 'Username "admin" is reserved', path: ['username'] }
  )
  // Second refinement
  .refine(
    data => !data.email.includes(data.username),
    { message: 'Email should not contain username', path: ['email'] }
  )
```

---

## Custom Error Messages

### Dynamic Error Messages

```typescript
const ageSchema = z.number().refine(
  val => val >= 18,
  val => ({ message: `You are ${val} years old. Must be at least 18.` })
)

const usernameSchema = z.string().refine(
  val => val.length >= 3,
  val => ({ message: `Username "${val}" is too short (minimum 3 characters)` })
)
```

### Contextual Error Messages

```typescript
function createMinLengthSchema(minLength: number, fieldName: string) {
  return z.string().refine(
    val => val.length >= minLength,
    { message: `${fieldName} must be at least ${minLength} characters` }
  )
}

const usernameSchema = createMinLengthSchema(3, 'Username')
const bioSchema = createMinLengthSchema(10, 'Bio')
```

### Multiple Error Paths

```typescript
const schema = z.object({
  password: z.string(),
  confirmPassword: z.string()
}).refine(
  data => data.password === data.confirmPassword,
  {
    message: "Passwords don't match",
    path: ['confirmPassword'] // Error shown on confirmPassword field
  }
)

// Can also show error on multiple fields
const multiPathSchema = z.object({
  startDate: z.date(),
  endDate: z.date()
}).refine(
  data => data.endDate > data.startDate,
  {
    message: 'End date must be after start date',
    path: ['endDate'] // Could also be ['startDate', 'endDate']
  }
)
```

---

## Cross-Field Validation

### Password Confirmation

```typescript
const signupSchema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string()
}).refine(
  data => data.password === data.confirmPassword,
  {
    message: "Passwords don't match",
    path: ['confirmPassword']
  }
)
```

### Date Range Validation

```typescript
const eventSchema = z.object({
  startDate: z.date(),
  endDate: z.date()
}).refine(
  data => data.endDate > data.startDate,
  {
    message: 'End date must be after start date',
    path: ['endDate']
  }
)
```

### Dependent Fields

```typescript
const addressSchema = z.object({
  country: z.string(),
  state: z.string().optional(),
  province: z.string().optional()
}).refine(
  data => {
    if (data.country === 'US') {
      return !!data.state
    }
    if (data.country === 'CA') {
      return !!data.province
    }
    return true
  },
  {
    message: 'State is required for US addresses',
    path: ['state']
  }
)
```

### Mutual Exclusivity

```typescript
const contactSchema = z.object({
  email: z.string().email().optional(),
  phone: z.string().optional()
}).refine(
  data => data.email || data.phone,
  {
    message: 'Either email or phone is required',
    path: ['email']
  }
)

// Exactly one must be provided
const exclusiveSchema = z.object({
  email: z.string().email().optional(),
  phone: z.string().optional()
}).refine(
  data => !!(data.email) !== !!(data.phone), // XOR
  {
    message: 'Provide either email or phone, not both',
    path: ['email']
  }
)
```

### Field Comparison

```typescript
const priceSchema = z.object({
  minPrice: z.number(),
  maxPrice: z.number()
}).refine(
  data => data.maxPrice >= data.minPrice,
  {
    message: 'Maximum price must be greater than or equal to minimum price',
    path: ['maxPrice']
  }
)

const bidSchema = z.object({
  currentBid: z.number(),
  yourBid: z.number()
}).refine(
  data => data.yourBid > data.currentBid,
  {
    message: 'Your bid must be higher than the current bid',
    path: ['yourBid']
  }
)
```

---

## Conditional Validation

### If-Then Validation

```typescript
const shippingSchema = z.object({
  requiresShipping: z.boolean(),
  shippingAddress: z.string().optional()
}).refine(
  data => {
    if (data.requiresShipping) {
      return !!data.shippingAddress && data.shippingAddress.length > 0
    }
    return true
  },
  {
    message: 'Shipping address is required when shipping is needed',
    path: ['shippingAddress']
  }
)
```

### Role-Based Validation

```typescript
const userSchema = z.object({
  role: z.enum(['admin', 'user', 'guest']),
  permissions: z.array(z.string()).optional(),
  department: z.string().optional()
}).refine(
  data => {
    if (data.role === 'admin') {
      return !!data.permissions && data.permissions.length > 0
    }
    return true
  },
  {
    message: 'Admins must have at least one permission',
    path: ['permissions']
  }
).refine(
  data => {
    if (data.role === 'user') {
      return !!data.department
    }
    return true
  },
  {
    message: 'Users must belong to a department',
    path: ['department']
  }
)
```

### Payment Method Validation

```typescript
const paymentSchema = z.object({
  method: z.enum(['card', 'paypal', 'bank_transfer']),
  cardNumber: z.string().optional(),
  paypalEmail: z.string().email().optional(),
  accountNumber: z.string().optional()
}).refine(
  data => {
    if (data.method === 'card') return !!data.cardNumber
    if (data.method === 'paypal') return !!data.paypalEmail
    if (data.method === 'bank_transfer') return !!data.accountNumber
    return false
  },
  data => ({
    message: `${data.method} details are required`,
    path: [
      data.method === 'card' ? 'cardNumber' :
      data.method === 'paypal' ? 'paypalEmail' :
      'accountNumber'
    ]
  })
)
```

### Conditional Required Fields

```typescript
const employmentSchema = z.object({
  employed: z.boolean(),
  employer: z.string().optional(),
  position: z.string().optional(),
  unemployed: z.boolean(),
  unemploymentReason: z.string().optional()
}).refine(
  data => {
    if (data.employed) {
      return !!data.employer && !!data.position
    }
    if (data.unemployed) {
      return !!data.unemploymentReason
    }
    return true
  },
  data => {
    if (data.employed && !data.employer) {
      return { message: 'Employer is required', path: ['employer'] }
    }
    if (data.employed && !data.position) {
      return { message: 'Position is required', path: ['position'] }
    }
    if (data.unemployed && !data.unemploymentReason) {
      return { message: 'Reason is required', path: ['unemploymentReason'] }
    }
    return { message: 'Invalid state' }
  }
)
```

---

## Business Logic Validation

### Credit Card Luhn Algorithm

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

const creditCardSchema = z.string()
  .regex(/^\d{13,19}$/, 'Invalid card number format')
  .refine(luhnCheck, { message: 'Invalid credit card number' })
```

### Tax ID Validation

```typescript
// US SSN validation (XXX-XX-XXXX)
const ssnSchema = z.string()
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

// EIN validation (XX-XXXXXXX)
const einSchema = z.string()
  .regex(/^\d{2}-\d{7}$/, 'EIN must be in format XX-XXXXXXX')
  .refine(
    val => {
      const prefix = parseInt(val.split('-')[0])
      return prefix >= 1 && prefix <= 99
    },
    { message: 'Invalid EIN number' }
  )
```

### Business Hours Validation

```typescript
const appointmentSchema = z.object({
  dateTime: z.date()
}).refine(
  data => {
    const hour = data.dateTime.getHours()
    const day = data.dateTime.getDay()
    // Monday-Friday, 9 AM - 5 PM
    return day >= 1 && day <= 5 && hour >= 9 && hour < 17
  },
  {
    message: 'Appointments must be scheduled during business hours (Mon-Fri, 9 AM - 5 PM)',
    path: ['dateTime']
  }
)
```

### Age Restriction

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
  birthdate: z.date()
}).refine(
  data => calculateAge(data.birthdate) >= 18,
  {
    message: 'You must be at least 18 years old',
    path: ['birthdate']
  }
)

// Age range
const seniorDiscountSchema = z.object({
  birthdate: z.date()
}).refine(
  data => {
    const age = calculateAge(data.birthdate)
    return age >= 65
  },
  {
    message: 'Senior discount available for ages 65+',
    path: ['birthdate']
  }
)
```

### Inventory Check

```typescript
const orderItemSchema = z.object({
  productId: z.string(),
  quantity: z.number().int().positive()
}).refine(
  async data => {
    const product = await getProduct(data.productId)
    return product.stock >= data.quantity
  },
  data => ({
    message: `Only ${data.quantity} units available`,
    path: ['quantity']
  })
)
```

---

## File Upload Validation

### File Size Validation

```typescript
const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB

const fileSchema = z.instanceof(File).refine(
  file => file.size <= MAX_FILE_SIZE,
  { message: 'File size must be less than 5MB' }
)
```

### File Type Validation

```typescript
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']

const imageSchema = z.instanceof(File).refine(
  file => ALLOWED_IMAGE_TYPES.includes(file.type),
  { message: 'Only JPEG, PNG, and WebP images are allowed' }
)

// Multiple checks
const uploadSchema = z.instanceof(File)
  .refine(
    file => file.size <= MAX_FILE_SIZE,
    { message: 'File must be less than 5MB' }
  )
  .refine(
    file => ALLOWED_IMAGE_TYPES.includes(file.type),
    { message: 'Only JPEG, PNG, and WebP images are allowed' }
  )
```

### Image Dimensions Validation

```typescript
async function getImageDimensions(file: File): Promise<{ width: number; height: number }> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve({ width: img.width, height: img.height })
    img.onerror = reject
    img.src = URL.createObjectURL(file)
  })
}

const profilePictureSchema = z.instanceof(File)
  .refine(
    file => ALLOWED_IMAGE_TYPES.includes(file.type),
    { message: 'Invalid file type' }
  )
  .refine(
    async file => {
      const { width, height } = await getImageDimensions(file)
      return width >= 200 && height >= 200
    },
    { message: 'Image must be at least 200x200 pixels' }
  )
  .refine(
    async file => {
      const { width, height } = await getImageDimensions(file)
      return width <= 4000 && height <= 4000
    },
    { message: 'Image must be at most 4000x4000 pixels' }
  )
```

### File Name Validation

```typescript
const documentSchema = z.instanceof(File).refine(
  file => {
    const extension = file.name.split('.').pop()?.toLowerCase()
    return ['pdf', 'doc', 'docx'].includes(extension || '')
  },
  { message: 'Only PDF and Word documents are allowed' }
).refine(
  file => !file.name.includes('..'),
  { message: 'Invalid file name' }
)
```

### Multiple Files Validation

```typescript
const multipleFilesSchema = z.array(z.instanceof(File))
  .min(1, 'At least one file is required')
  .max(10, 'Maximum 10 files allowed')
  .refine(
    files => files.every(file => file.size <= MAX_FILE_SIZE),
    { message: 'Each file must be less than 5MB' }
  )
  .refine(
    files => files.every(file => ALLOWED_IMAGE_TYPES.includes(file.type)),
    { message: 'All files must be images (JPEG, PNG, or WebP)' }
  )
  .refine(
    files => {
      const totalSize = files.reduce((sum, file) => sum + file.size, 0)
      return totalSize <= 50 * 1024 * 1024 // 50MB total
    },
    { message: 'Total upload size must be less than 50MB' }
  )
```

---

## Date Range Validation

### Event Scheduling

```typescript
const eventSchema = z.object({
  startDate: z.date(),
  endDate: z.date()
})
  .refine(
    data => data.endDate > data.startDate,
    {
      message: 'End date must be after start date',
      path: ['endDate']
    }
  )
  .refine(
    data => {
      const duration = data.endDate.getTime() - data.startDate.getTime()
      const maxDuration = 7 * 24 * 60 * 60 * 1000 // 7 days
      return duration <= maxDuration
    },
    {
      message: 'Event cannot be longer than 7 days',
      path: ['endDate']
    }
  )
```

### Booking Window

```typescript
const bookingSchema = z.object({
  checkIn: z.date(),
  checkOut: z.date()
})
  .refine(
    data => data.checkOut > data.checkIn,
    {
      message: 'Check-out must be after check-in',
      path: ['checkOut']
    }
  )
  .refine(
    data => {
      const now = new Date()
      const minAdvance = new Date(now.getTime() + 24 * 60 * 60 * 1000) // 24 hours
      return data.checkIn >= minAdvance
    },
    {
      message: 'Bookings must be made at least 24 hours in advance',
      path: ['checkIn']
    }
  )
  .refine(
    data => {
      const nights = Math.ceil(
        (data.checkOut.getTime() - data.checkIn.getTime()) / (1000 * 60 * 60 * 24)
      )
      return nights >= 1 && nights <= 30
    },
    {
      message: 'Booking must be between 1 and 30 nights',
      path: ['checkOut']
    }
  )
```

### Expiration Date

```typescript
const cardSchema = z.object({
  expiryMonth: z.number().min(1).max(12),
  expiryYear: z.number()
}).refine(
  data => {
    const now = new Date()
    const currentYear = now.getFullYear()
    const currentMonth = now.getMonth() + 1

    if (data.expiryYear < currentYear) return false
    if (data.expiryYear === currentYear && data.expiryMonth < currentMonth) return false
    return true
  },
  {
    message: 'Card has expired',
    path: ['expiryMonth']
  }
)
```

---

## Uniqueness Validation

### Database Uniqueness (Async)

```typescript
// Check if email is unique
const emailSchema = z.string()
  .email()
  .refine(
    async email => {
      const existing = await db.user.findUnique({ where: { email } })
      return !existing
    },
    { message: 'Email is already registered' }
  )

// Check if username is unique
const usernameSchema = z.string()
  .min(3)
  .max(20)
  .regex(/^[a-zA-Z0-9_-]+$/)
  .refine(
    async username => {
      const existing = await db.user.findUnique({ where: { username } })
      return !existing
    },
    { message: 'Username is already taken' }
  )
```

### Array Uniqueness

```typescript
// Unique emails in array
const emailListSchema = z.array(z.string().email()).refine(
  emails => new Set(emails).size === emails.length,
  { message: 'Emails must be unique' }
)

// Unique IDs
const idListSchema = z.array(z.string().uuid()).refine(
  ids => new Set(ids).size === ids.length,
  { message: 'IDs must be unique' }
)

// Complex object uniqueness
const usersSchema = z.array(
  z.object({
    id: z.string(),
    email: z.string().email()
  })
).refine(
  users => {
    const emails = users.map(u => u.email)
    return new Set(emails).size === emails.length
  },
  { message: 'User emails must be unique' }
)
```

### Slug Uniqueness

```typescript
const slugSchema = z.string()
  .regex(/^[a-z0-9-]+$/, 'Slug can only contain lowercase letters, numbers, and hyphens')
  .refine(
    async slug => {
      const existing = await db.post.findUnique({ where: { slug } })
      return !existing
    },
    { message: 'This slug is already in use' }
  )
```

---

## Complex Validation Patterns

### Nested Object Validation

```typescript
const orderSchema = z.object({
  items: z.array(
    z.object({
      productId: z.string(),
      quantity: z.number().positive()
    })
  ),
  total: z.number()
}).refine(
  data => {
    // Validate that total matches sum of item prices
    const calculatedTotal = data.items.reduce((sum, item) => {
      // This would normally fetch price from database
      return sum + (item.quantity * 10) // Example calculation
    }, 0)
    return Math.abs(data.total - calculatedTotal) < 0.01 // Account for floating point
  },
  {
    message: 'Total does not match item prices',
    path: ['total']
  }
)
```

### Multi-Step Validation

```typescript
const registrationSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  confirmPassword: z.string(),
  termsAccepted: z.boolean()
})
  // Step 1: Password confirmation
  .refine(
    data => data.password === data.confirmPassword,
    { message: "Passwords don't match", path: ['confirmPassword'] }
  )
  // Step 2: Terms must be accepted
  .refine(
    data => data.termsAccepted === true,
    { message: 'You must accept the terms', path: ['termsAccepted'] }
  )
  // Step 3: Check email uniqueness (async)
  .refine(
    async data => {
      const existing = await db.user.findUnique({ where: { email: data.email } })
      return !existing
    },
    { message: 'Email already registered', path: ['email'] }
  )
```

### Polymorphic Validation

```typescript
const mediaSchema = z.object({
  type: z.enum(['image', 'video', 'audio']),
  url: z.string().url(),
  duration: z.number().optional(),
  width: z.number().optional(),
  height: z.number().optional()
}).refine(
  data => {
    if (data.type === 'video' || data.type === 'audio') {
      return !!data.duration
    }
    if (data.type === 'image') {
      return !!data.width && !!data.height
    }
    return true
  },
  data => {
    if (data.type === 'video' || data.type === 'audio') {
      return { message: 'Duration required for video/audio', path: ['duration'] }
    }
    return { message: 'Dimensions required for images', path: ['width'] }
  }
)
```

---

## Summary

This document covered:
- ✅ Basic and chained refinements
- ✅ Custom error messages with dynamic content
- ✅ Cross-field validation (password confirmation, date ranges)
- ✅ Conditional validation (if-then logic)
- ✅ Business logic (Luhn, SSN, age calculation)
- ✅ File upload validation (size, type, dimensions)
- ✅ Date range and booking validation
- ✅ Uniqueness checks (database, array)
- ✅ Complex nested and multi-step validation

**Next Steps:**
- **[Transforms](./transforms.md)** - Data transformation
- **[Async Validation](./async-validation.md)** - Database/API checks
- **[Common Schemas](./common-schemas.md)** - Ready-to-use patterns

---

*Last updated: 2025-11-23 | Zod v4.1.12*
