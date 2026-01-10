# Error Handling - Comprehensive Guide

This document covers every error handling pattern in Zod for robust validation error management.

## Table of Contents

- [Default Error Messages](#default-error-messages)
- [Custom Error Messages](#custom-error-messages)
- [Error Map Customization](#error-map-customization)
- [Internationalization (i18n)](#internationalization-i18n)
- [Error Formatting for UI](#error-formatting-for-ui)
- [Error Flattening](#error-flattening)
- [Parsing Errors](#parsing-errors)
- [Safe Parsing](#safe-parsing)
- [Try-Catch Patterns](#try-catch-patterns)
- [Error Recovery](#error-recovery)

---

## Default Error Messages

### Built-in Error Messages

```typescript
import { z } from 'zod'

const userSchema = z.object({
  email: z.string().email(),
  age: z.number().min(18)
})

try {
  userSchema.parse({
    email: 'invalid',
    age: 15
  })
} catch (error) {
  if (error instanceof z.ZodError) {
    console.log(error.errors)
    // [
    //   {
    //     code: 'invalid_string',
    //     validation: 'email',
    //     message: 'Invalid email',
    //     path: ['email']
    //   },
    //   {
    //     code: 'too_small',
    //     minimum: 18,
    //     type: 'number',
    //     inclusive: true,
    //     message: 'Number must be greater than or equal to 18',
    //     path: ['age']
    //   }
    // ]
  }
}
```

### Error Codes Reference

```typescript
// String validation errors
z.string().email() // code: 'invalid_string', validation: 'email'
z.string().url() // code: 'invalid_string', validation: 'url'
z.string().uuid() // code: 'invalid_string', validation: 'uuid'
z.string().regex(/.../) // code: 'invalid_string', validation: 'regex'

// Number validation errors
z.number().min(5) // code: 'too_small', type: 'number'
z.number().max(100) // code: 'too_big', type: 'number'
z.number().int() // code: 'invalid_type', expected: 'integer'

// Array validation errors
z.array(z.string()).min(1) // code: 'too_small', type: 'array'
z.array(z.string()).max(10) // code: 'too_big', type: 'array'

// Required field errors
z.string() // code: 'invalid_type', expected: 'string', received: 'undefined'

// Type mismatch
z.number() // code: 'invalid_type', expected: 'number', received: 'string'
```

---

## Custom Error Messages

### Per-Field Custom Messages

```typescript
// String validation with custom message
const emailSchema = z.string().email('Please enter a valid email address')

const urlSchema = z.string().url('Please enter a valid URL')

const passwordSchema = z.string()
  .min(8, 'Password must be at least 8 characters long')
  .max(100, 'Password is too long')
```

### Number Validation Messages

```typescript
const ageSchema = z.number()
  .min(18, 'You must be at least 18 years old')
  .max(120, 'Please enter a valid age')

const priceSchema = z.number()
  .positive('Price must be positive')
  .multipleOf(0.01, 'Price must have at most 2 decimal places')
```

### Array Validation Messages

```typescript
const tagsSchema = z.array(z.string())
  .min(1, 'Please add at least one tag')
  .max(10, 'You can add up to 10 tags')
  .nonempty('Tags cannot be empty')
```

### Schema-Level Custom Messages

```typescript
const userSchema = z.object({
  email: z.string({
    required_error: 'Email is required',
    invalid_type_error: 'Email must be a string'
  }).email('Invalid email format'),

  age: z.number({
    required_error: 'Age is required',
    invalid_type_error: 'Age must be a number'
  }).min(18, 'Must be 18 or older'),

  acceptTerms: z.boolean({
    required_error: 'You must accept the terms',
    invalid_type_error: 'Invalid value'
  })
})
```

---

## Error Map Customization

### Global Error Map

```typescript
import { z } from 'zod'

// Custom error map for all schemas
z.setErrorMap((issue, ctx) => {
  if (issue.code === z.ZodIssueCode.invalid_type) {
    if (issue.expected === 'string') {
      return { message: 'This field must be text' }
    }
  }

  if (issue.code === z.ZodIssueCode.too_small) {
    if (issue.type === 'string') {
      return { message: `Minimum ${issue.minimum} characters required` }
    }
  }

  // Use default message
  return { message: ctx.defaultError }
})
```

### Schema-Specific Error Map

```typescript
const customErrorMap: z.ZodErrorMap = (issue, ctx) => {
  switch (issue.code) {
    case z.ZodIssueCode.invalid_type:
      return { message: `Expected ${issue.expected}, got ${issue.received}` }

    case z.ZodIssueCode.invalid_string:
      if (issue.validation === 'email') {
        return { message: 'Please provide a valid email address' }
      }
      if (issue.validation === 'url') {
        return { message: 'Please provide a valid URL' }
      }
      break

    case z.ZodIssueCode.too_small:
      if (issue.type === 'string') {
        return { message: `Must be at least ${issue.minimum} characters` }
      }
      if (issue.type === 'number') {
        return { message: `Must be at least ${issue.minimum}` }
      }
      if (issue.type === 'array') {
        return { message: `Must contain at least ${issue.minimum} items` }
      }
      break

    case z.ZodIssueCode.too_big:
      if (issue.type === 'string') {
        return { message: `Must be at most ${issue.maximum} characters` }
      }
      if (issue.type === 'number') {
        return { message: `Must be at most ${issue.maximum}` }
      }
      if (issue.type === 'array') {
        return { message: `Must contain at most ${issue.maximum} items` }
      }
      break

    case z.ZodIssueCode.invalid_enum_value:
      return {
        message: `Must be one of: ${issue.options.join(', ')}`
      }

    case z.ZodIssueCode.custom:
      return { message: issue.message || 'Invalid value' }
  }

  return { message: ctx.defaultError }
}

// Use with specific schema
const userSchema = z.object({
  email: z.string().email(),
  age: z.number().min(18)
}, { errorMap: customErrorMap })
```

### Error Map with Context

```typescript
const contextualErrorMap: z.ZodErrorMap = (issue, ctx) => {
  // Access path for field-specific messages
  const fieldName = issue.path.join('.')

  if (issue.code === z.ZodIssueCode.invalid_type) {
    return {
      message: `The field "${fieldName}" must be a ${issue.expected}`
    }
  }

  if (issue.code === z.ZodIssueCode.too_small && issue.type === 'string') {
    return {
      message: `"${fieldName}" must be at least ${issue.minimum} characters`
    }
  }

  return { message: ctx.defaultError }
}
```

---

## Internationalization (i18n)

### Multi-Language Error Messages

```typescript
type Language = 'en' | 'es' | 'fr'

const translations = {
  en: {
    required: 'This field is required',
    email: 'Invalid email address',
    minLength: (min: number) => `Must be at least ${min} characters`,
    maxLength: (max: number) => `Must be at most ${max} characters`,
    minValue: (min: number) => `Must be at least ${min}`,
    maxValue: (max: number) => `Must be at most ${max}`
  },
  es: {
    required: 'Este campo es obligatorio',
    email: 'Correo electrónico inválido',
    minLength: (min: number) => `Debe tener al menos ${min} caracteres`,
    maxLength: (max: number) => `Debe tener como máximo ${max} caracteres`,
    minValue: (min: number) => `Debe ser al menos ${min}`,
    maxValue: (max: number) => `Debe ser como máximo ${max}`
  },
  fr: {
    required: 'Ce champ est requis',
    email: 'Adresse e-mail invalide',
    minLength: (min: number) => `Doit contenir au moins ${min} caractères`,
    maxLength: (max: number) => `Doit contenir au plus ${max} caractères`,
    minValue: (min: number) => `Doit être au moins ${min}`,
    maxValue: (max: number) => `Doit être au plus ${max}`
  }
}

function createI18nErrorMap(lang: Language): z.ZodErrorMap {
  const t = translations[lang]

  return (issue, ctx) => {
    switch (issue.code) {
      case z.ZodIssueCode.invalid_type:
        if (issue.received === 'undefined') {
          return { message: t.required }
        }
        break

      case z.ZodIssueCode.invalid_string:
        if (issue.validation === 'email') {
          return { message: t.email }
        }
        break

      case z.ZodIssueCode.too_small:
        if (issue.type === 'string') {
          return { message: t.minLength(issue.minimum as number) }
        }
        if (issue.type === 'number') {
          return { message: t.minValue(issue.minimum as number) }
        }
        break

      case z.ZodIssueCode.too_big:
        if (issue.type === 'string') {
          return { message: t.maxLength(issue.maximum as number) }
        }
        if (issue.type === 'number') {
          return { message: t.maxValue(issue.maximum as number) }
        }
        break
    }

    return { message: ctx.defaultError }
  }
}

// Usage
const spanishErrorMap = createI18nErrorMap('es')
const userSchema = z.object({
  email: z.string().email(),
  age: z.number().min(18)
}, { errorMap: spanishErrorMap })
```

### i18n with Library Integration

```typescript
// Example with i18next
import i18next from 'i18next'

const i18nErrorMap: z.ZodErrorMap = (issue, ctx) => {
  if (issue.code === z.ZodIssueCode.invalid_string) {
    if (issue.validation === 'email') {
      return { message: i18next.t('validation.email') }
    }
  }

  if (issue.code === z.ZodIssueCode.too_small && issue.type === 'string') {
    return {
      message: i18next.t('validation.minLength', { min: issue.minimum })
    }
  }

  return { message: ctx.defaultError }
}

// Set globally
z.setErrorMap(i18nErrorMap)
```

---

## Error Formatting for UI

### Format for Form Display

```typescript
import { z } from 'zod'

const userSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  confirmPassword: z.string()
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword']
})

// Parse and format errors
function validateUser(data: unknown) {
  const result = userSchema.safeParse(data)

  if (!result.success) {
    // Format errors for UI
    const fieldErrors: Record<string, string> = {}

    result.error.errors.forEach(err => {
      const path = err.path.join('.')
      if (!fieldErrors[path]) {
        fieldErrors[path] = err.message
      }
    })

    return { success: false, errors: fieldErrors }
  }

  return { success: true, data: result.data }
}

// Usage in React component
function UserForm() {
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleSubmit = (data: unknown) => {
    const result = validateUser(data)
    if (!result.success) {
      setErrors(result.errors)
      return
    }
    // Process result.data
  }

  return (
    <form>
      <input name="email" />
      {errors.email && <span className="error">{errors.email}</span>}

      <input name="password" type="password" />
      {errors.password && <span className="error">{errors.password}</span>}
    </form>
  )
}
```

### Format for API Response

```typescript
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const body = await request.json()
  const result = userSchema.safeParse(body)

  if (!result.success) {
    // Format errors for API response
    return NextResponse.json(
      {
        error: 'Validation failed',
        details: result.error.format()
      },
      { status: 400 }
    )
  }

  // Process valid data
  return NextResponse.json({ success: true })
}
```

### Format with Nested Objects

```typescript
const addressSchema = z.object({
  street: z.string().min(1),
  city: z.string().min(1),
  zipCode: z.string().regex(/^\d{5}$/)
})

const userWithAddressSchema = z.object({
  name: z.string(),
  address: addressSchema
})

function formatErrors(error: z.ZodError) {
  const formatted: Record<string, string> = {}

  error.errors.forEach(err => {
    const path = err.path.join('.')
    formatted[path] = err.message
  })

  return formatted
}

// Example output:
// {
//   "name": "Name is required",
//   "address.street": "Street is required",
//   "address.zipCode": "Invalid zip code format"
// }
```

---

## Error Flattening

### Flatten Nested Errors

```typescript
const complexSchema = z.object({
  user: z.object({
    profile: z.object({
      name: z.string(),
      email: z.string().email()
    }),
    settings: z.object({
      theme: z.enum(['light', 'dark'])
    })
  })
})

try {
  complexSchema.parse({
    user: {
      profile: { name: '', email: 'invalid' },
      settings: { theme: 'invalid' }
    }
  })
} catch (error) {
  if (error instanceof z.ZodError) {
    // Flatten errors
    const flattened = error.flatten()
    console.log(flattened)
    // {
    //   formErrors: [],
    //   fieldErrors: {
    //     'user.profile.name': ['String must contain at least 1 character(s)'],
    //     'user.profile.email': ['Invalid email'],
    //     'user.settings.theme': ['Invalid enum value...']
    //   }
    // }
  }
}
```

### Field Errors vs Form Errors

```typescript
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
}).refine(data => {
  // Form-level validation
  return someGlobalCheck(data)
}, {
  message: 'Form validation failed'
  // No path = form-level error
})

const result = schema.safeParse(data)
if (!result.success) {
  const { fieldErrors, formErrors } = result.error.flatten()

  // fieldErrors: { email: [...], password: [...] }
  // formErrors: ['Form validation failed']
}
```

### Custom Flattening

```typescript
function flattenErrors(error: z.ZodError): Record<string, string[]> {
  const errors: Record<string, string[]> = {}

  error.errors.forEach(err => {
    const path = err.path.join('.') || '_form'
    if (!errors[path]) {
      errors[path] = []
    }
    errors[path].push(err.message)
  })

  return errors
}

// Usage
try {
  schema.parse(data)
} catch (error) {
  if (error instanceof z.ZodError) {
    const flattened = flattenErrors(error)
    // { "email": ["Invalid email"], "age": ["Must be 18+"] }
  }
}
```

---

## Parsing Errors

### ZodError Structure

```typescript
import { z } from 'zod'

try {
  const schema = z.string().email()
  schema.parse('invalid')
} catch (error) {
  if (error instanceof z.ZodError) {
    console.log(error.issues) // Array of issues
    console.log(error.errors) // Same as issues
    console.log(error.message) // Formatted error message
    console.log(error.format()) // Nested error object
    console.log(error.flatten()) // Flattened errors
  }
}
```

### Individual Issue Structure

```typescript
const issue = {
  code: 'invalid_string', // Error code
  validation: 'email', // Validation type
  message: 'Invalid email', // Error message
  path: ['email'], // Path to field
  // Additional fields depending on error type
}
```

### Accessing Error Details

```typescript
const userSchema = z.object({
  email: z.string().email(),
  age: z.number().min(18).max(120)
})

try {
  userSchema.parse({ email: 'invalid', age: 15 })
} catch (error) {
  if (error instanceof z.ZodError) {
    // Iterate through all errors
    error.errors.forEach(err => {
      console.log(`Field: ${err.path.join('.')}`)
      console.log(`Message: ${err.message}`)
      console.log(`Code: ${err.code}`)

      // Type-specific details
      if (err.code === 'too_small') {
        console.log(`Minimum: ${err.minimum}`)
      }
    })
  }
}
```

---

## Safe Parsing

### safeParse() vs parse()

```typescript
const schema = z.string().email()

// parse() - throws on error
try {
  const result = schema.parse('invalid')
  console.log(result)
} catch (error) {
  console.error(error)
}

// safeParse() - returns result object
const result = schema.safeParse('invalid')
if (result.success) {
  console.log(result.data)
} else {
  console.error(result.error)
}
```

### Safe Parse in API Routes

```typescript
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const body = await request.json()

  const result = userSchema.safeParse(body)

  if (!result.success) {
    // Handle validation error
    return NextResponse.json(
      { error: result.error.format() },
      { status: 400 }
    )
  }

  // Process valid data
  const validData = result.data
  // ...
}
```

### Safe Parse in Server Actions

```typescript
'use server'

export async function createUser(formData: FormData) {
  const result = userSchema.safeParse({
    email: formData.get('email'),
    password: formData.get('password')
  })

  if (!result.success) {
    // Return errors to client
    return {
      success: false,
      errors: result.error.flatten().fieldErrors
    }
  }

  // Process valid data
  return { success: true, data: result.data }
}
```

### Type Guards with Safe Parse

```typescript
function isValidUser(data: unknown): data is User {
  return userSchema.safeParse(data).success
}

// Usage
if (isValidUser(unknownData)) {
  // TypeScript knows this is User
  console.log(unknownData.email)
}
```

---

## Try-Catch Patterns

### Basic Try-Catch

```typescript
function validateAndProcess(data: unknown) {
  try {
    const validated = userSchema.parse(data)
    // Process validated data
    return { success: true, data: validated }
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { success: false, errors: error.errors }
    }
    // Handle unexpected errors
    throw error
  }
}
```

### Try-Catch with Specific Error Handling

```typescript
async function createUser(data: unknown) {
  try {
    const validated = userSchema.parse(data)

    // Attempt to create user
    const user = await db.user.create({ data: validated })
    return { success: true, user }

  } catch (error) {
    if (error instanceof z.ZodError) {
      // Validation error
      return {
        success: false,
        type: 'validation',
        errors: error.format()
      }
    }

    // Database error, network error, etc.
    return {
      success: false,
      type: 'unknown',
      message: error instanceof Error ? error.message : 'Unknown error'
    }
  }
}
```

### Nested Try-Catch for Multi-Step Validation

```typescript
async function processOrder(orderData: unknown, paymentData: unknown) {
  try {
    // Step 1: Validate order
    const order = orderSchema.parse(orderData)

    try {
      // Step 2: Validate payment
      const payment = paymentSchema.parse(paymentData)

      // Process both
      return await createOrder(order, payment)

    } catch (error) {
      if (error instanceof z.ZodError) {
        return { error: 'Invalid payment data', details: error.errors }
      }
      throw error
    }

  } catch (error) {
    if (error instanceof z.ZodError) {
      return { error: 'Invalid order data', details: error.errors }
    }
    throw error
  }
}
```

---

## Error Recovery

### Fallback Values with catch()

```typescript
// Provide default value on parse error
const safeNumberSchema = z.number().catch(0)

safeNumberSchema.parse(123) // 123
safeNumberSchema.parse('invalid') // 0

// Computed fallback
const timestampSchema = z.date().catch(() => new Date())

// Context-aware fallback
const userIdSchema = z.string().uuid().catch((ctx) => {
  console.log('Invalid input:', ctx.input)
  return crypto.randomUUID()
})
```

### Partial Validation

```typescript
// Allow partial object validation
const userSchema = z.object({
  email: z.string().email(),
  age: z.number(),
  name: z.string()
})

const partialUserSchema = userSchema.partial()

// All fields optional
const result = partialUserSchema.parse({
  email: 'user@example.com'
  // age and name can be missing
})
```

### Best-Effort Parsing

```typescript
function bestEffortParse<T>(
  schema: z.ZodType<T>,
  data: unknown
): { data: Partial<T>; errors: z.ZodError | null } {
  const result = schema.safeParse(data)

  if (result.success) {
    return { data: result.data, errors: null }
  }

  // Try to salvage what we can
  const partial: any = {}
  const originalData = data as Record<string, unknown>

  for (const key in originalData) {
    try {
      // Try to validate individual fields
      const fieldSchema = (schema as any).shape?.[key]
      if (fieldSchema) {
        partial[key] = fieldSchema.parse(originalData[key])
      }
    } catch {
      // Skip invalid fields
    }
  }

  return { data: partial, errors: result.error }
}
```

### Graceful Degradation

```typescript
async function loadUserProfile(userId: string) {
  try {
    const data = await fetchUserProfile(userId)
    const validated = userProfileSchema.parse(data)
    return { type: 'full', data: validated }
  } catch (error) {
    if (error instanceof z.ZodError) {
      // Try with minimal schema
      const minimalSchema = userProfileSchema.pick({
        id: true,
        name: true
      })

      try {
        const minimal = minimalSchema.parse(data)
        return { type: 'minimal', data: minimal }
      } catch {
        // Can't even get minimal data
        return { type: 'error', error }
      }
    }
    throw error
  }
}
```

### Error Logging and Monitoring

```typescript
function parseWithLogging<T>(
  schema: z.ZodType<T>,
  data: unknown,
  context: string
) {
  const result = schema.safeParse(data)

  if (!result.success) {
    // Log validation failures
    logger.warn('Validation failed', {
      context,
      errors: result.error.errors,
      data: JSON.stringify(data)
    })

    // Send to monitoring service
    monitoringService.recordValidationError({
      schema: schema.constructor.name,
      context,
      errorCount: result.error.errors.length
    })
  }

  return result
}

// Usage
const result = parseWithLogging(
  userSchema,
  requestBody,
  'POST /api/users'
)
```

---

## Summary

This document covered:
- ✅ Default and custom error messages
- ✅ Error map customization (global and schema-specific)
- ✅ Internationalization patterns
- ✅ Error formatting for UI and API responses
- ✅ Error flattening for nested objects
- ✅ Safe parsing vs throwing
- ✅ Try-catch patterns for error handling
- ✅ Error recovery strategies

**Next Steps:**
- **[Refinements](./refinements.md)** - Custom validation logic
- **[API Integration](./api-integration.md)** - Use in Next.js routes
- **[Common Schemas](./common-schemas.md)** - Ready-to-use schemas

---

*Last updated: 2025-11-23 | Zod v4.1.12*
