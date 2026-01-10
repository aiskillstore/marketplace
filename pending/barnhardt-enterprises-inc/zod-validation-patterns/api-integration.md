# API Integration - Next.js Patterns

This document covers all patterns for integrating Zod validation with Next.js 15 App Router, API routes, Server Actions, and forms.

## Table of Contents

- [API Route Validation](#api-route-validation)
- [Server Actions Validation](#server-actions-validation)
- [Middleware Validation](#middleware-validation)
- [Request Body Validation](#request-body-validation)
- [Query Parameter Validation](#query-parameter-validation)
- [Path Parameter Validation](#path-parameter-validation)
- [Form Data Validation](#form-data-validation)
- [File Upload Validation](#file-upload-validation)
- [Error Response Formatting](#error-response-formatting)
- [Try-Catch Patterns](#try-catch-patterns)

---

## API Route Validation

### Basic API Route

```typescript
// src/app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

const createUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  age: z.number().int().positive()
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validate
    const result = createUserSchema.safeParse(body)
    if (!result.success) {
      return NextResponse.json(
        {
          error: 'Validation failed',
          details: result.error.format()
        },
        { status: 400 }
      )
    }

    // Process validated data
    const user = await db.user.create({ data: result.data })

    return NextResponse.json({ user }, { status: 201 })
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

### GET with Query Params

```typescript
// src/app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

const getUsersQuerySchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(10),
  sort: z.enum(['name', 'email', 'createdAt']).default('createdAt'),
  order: z.enum(['asc', 'desc']).default('desc')
})

export async function GET(request: NextRequest) {
  const searchParams = Object.fromEntries(request.nextUrl.searchParams)

  const result = getUsersQuerySchema.safeParse(searchParams)
  if (!result.success) {
    return NextResponse.json(
      { error: result.error.format() },
      { status: 400 }
    )
  }

  const { page, limit, sort, order } = result.data

  const users = await db.user.findMany({
    skip: (page - 1) * limit,
    take: limit,
    orderBy: { [sort]: order }
  })

  return NextResponse.json({ users, page, limit })
}
```

### Dynamic Route with Path Params

```typescript
// src/app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

const userIdSchema = z.string().uuid()

const updateUserSchema = z.object({
  name: z.string().min(1).optional(),
  email: z.string().email().optional(),
  age: z.number().int().positive().optional()
}).refine(
  data => Object.keys(data).length > 0,
  { message: 'At least one field must be provided' }
)

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  // Validate path param
  const idResult = userIdSchema.safeParse(params.id)
  if (!idResult.success) {
    return NextResponse.json(
      { error: 'Invalid user ID' },
      { status: 400 }
    )
  }

  // Validate body
  const body = await request.json()
  const bodyResult = updateUserSchema.safeParse(body)
  if (!bodyResult.success) {
    return NextResponse.json(
      { error: bodyResult.error.format() },
      { status: 400 }
    )
  }

  const user = await db.user.update({
    where: { id: idResult.data },
    data: bodyResult.data
  })

  return NextResponse.json({ user })
}
```

---

## Server Actions Validation

### Basic Server Action

```typescript
// src/app/actions/users.ts
'use server'

import { z } from 'zod'
import { revalidatePath } from 'next/cache'

const createUserSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters')
})

export async function createUser(formData: FormData) {
  const result = createUserSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
    password: formData.get('password')
  })

  if (!result.success) {
    return {
      success: false,
      errors: result.error.flatten().fieldErrors
    }
  }

  try {
    const user = await db.user.create({ data: result.data })

    revalidatePath('/users')

    return { success: true, data: user }
  } catch (error) {
    return {
      success: false,
      errors: { _form: ['Failed to create user'] }
    }
  }
}
```

### Server Action with Object Input

```typescript
'use server'

import { z } from 'zod'

const updateProfileSchema = z.object({
  userId: z.string().uuid(),
  name: z.string().min(1).optional(),
  bio: z.string().max(500).optional(),
  website: z.string().url().optional()
})

export async function updateProfile(data: unknown) {
  const result = updateProfileSchema.safeParse(data)

  if (!result.success) {
    return {
      success: false,
      errors: result.error.flatten().fieldErrors
    }
  }

  const { userId, ...updates } = result.data

  await db.user.update({
    where: { id: userId },
    data: updates
  })

  revalidatePath(`/users/${userId}`)

  return { success: true }
}
```

### Server Action with File Upload

```typescript
'use server'

import { z } from 'zod'

const uploadAvatarSchema = z.object({
  userId: z.string().uuid(),
  file: z.instanceof(File)
    .refine(file => file.size <= 5 * 1024 * 1024, 'File must be less than 5MB')
    .refine(
      file => ['image/jpeg', 'image/png', 'image/webp'].includes(file.type),
      'Only JPEG, PNG, and WebP images are allowed'
    )
})

export async function uploadAvatar(formData: FormData) {
  const result = uploadAvatarSchema.safeParse({
    userId: formData.get('userId'),
    file: formData.get('file')
  })

  if (!result.success) {
    return {
      success: false,
      errors: result.error.flatten().fieldErrors
    }
  }

  const { userId, file } = result.data

  // Upload to storage
  const url = await uploadToS3(file)

  // Update database
  await db.user.update({
    where: { id: userId },
    data: { avatar: url }
  })

  return { success: true, url }
}
```

---

## Middleware Validation

### Authentication Middleware

```typescript
// src/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { z } from 'zod'

const authTokenSchema = z.string().regex(/^Bearer .+$/)

export function middleware(request: NextRequest) {
  const authorization = request.headers.get('authorization')

  const result = authTokenSchema.safeParse(authorization)
  if (!result.success) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }

  // Verify token
  const token = result.data.replace('Bearer ', '')
  // ... verify token logic

  return NextResponse.next()
}

export const config = {
  matcher: '/api/:path*'
}
```

### Rate Limiting Middleware

```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { z } from 'zod'

const rateLimitHeaderSchema = z.object({
  'x-user-id': z.string().uuid()
})

export async function middleware(request: NextRequest) {
  const headers = {
    'x-user-id': request.headers.get('x-user-id')
  }

  const result = rateLimitHeaderSchema.safeParse(headers)
  if (!result.success) {
    return NextResponse.json(
      { error: 'Missing user ID header' },
      { status: 400 }
    )
  }

  const userId = result.data['x-user-id']

  // Check rate limit
  const allowed = await checkRateLimit(userId)
  if (!allowed) {
    return NextResponse.json(
      { error: 'Rate limit exceeded' },
      { status: 429 }
    )
  }

  return NextResponse.next()
}
```

---

## Request Body Validation

### JSON Body

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

const postSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  tags: z.array(z.string()).max(10).optional(),
  published: z.boolean().default(false)
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const validated = postSchema.parse(body)

    const post = await db.post.create({ data: validated })

    return NextResponse.json({ post }, { status: 201 })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: error.format() },
        { status: 400 }
      )
    }
    throw error
  }
}
```

### Nested Objects

```typescript
const createOrderSchema = z.object({
  customer: z.object({
    name: z.string(),
    email: z.string().email(),
    phone: z.string().optional()
  }),
  items: z.array(z.object({
    productId: z.string().uuid(),
    quantity: z.number().int().positive(),
    price: z.number().positive()
  })).min(1),
  shippingAddress: z.object({
    street: z.string(),
    city: z.string(),
    state: z.string(),
    zipCode: z.string().regex(/^\d{5}$/),
    country: z.string()
  })
})

export async function POST(request: NextRequest) {
  const body = await request.json()
  const result = createOrderSchema.safeParse(body)

  if (!result.success) {
    return NextResponse.json(
      { error: result.error.format() },
      { status: 400 }
    )
  }

  // All nested data is validated
  const order = await createOrder(result.data)

  return NextResponse.json({ order }, { status: 201 })
}
```

---

## Query Parameter Validation

### Simple Query Params

```typescript
const searchSchema = z.object({
  q: z.string().min(1),
  category: z.string().optional(),
  minPrice: z.coerce.number().positive().optional(),
  maxPrice: z.coerce.number().positive().optional()
})

export async function GET(request: NextRequest) {
  const searchParams = Object.fromEntries(request.nextUrl.searchParams)

  const result = searchSchema.safeParse(searchParams)
  if (!result.success) {
    return NextResponse.json(
      { error: result.error.format() },
      { status: 400 }
    )
  }

  const products = await searchProducts(result.data)

  return NextResponse.json({ products })
}
```

### Pagination and Sorting

```typescript
const paginationSchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20),
  sortBy: z.enum(['createdAt', 'updatedAt', 'name']).default('createdAt'),
  sortOrder: z.enum(['asc', 'desc']).default('desc')
})

export async function GET(request: NextRequest) {
  const params = Object.fromEntries(request.nextUrl.searchParams)

  const validated = paginationSchema.parse(params)

  const items = await db.item.findMany({
    skip: (validated.page - 1) * validated.limit,
    take: validated.limit,
    orderBy: { [validated.sortBy]: validated.sortOrder }
  })

  return NextResponse.json({ items })
}
```

### Filters

```typescript
const filterSchema = z.object({
  status: z.enum(['active', 'inactive', 'pending']).optional(),
  startDate: z.coerce.date().optional(),
  endDate: z.coerce.date().optional(),
  tags: z.string().transform(val => val.split(',')).optional()
})

export async function GET(request: NextRequest) {
  const params = Object.fromEntries(request.nextUrl.searchParams)

  const filters = filterSchema.parse(params)

  const where: any = {}
  if (filters.status) where.status = filters.status
  if (filters.startDate) where.createdAt = { gte: filters.startDate }
  if (filters.endDate) where.createdAt = { ...where.createdAt, lte: filters.endDate }
  if (filters.tags) where.tags = { hasSome: filters.tags }

  const items = await db.item.findMany({ where })

  return NextResponse.json({ items })
}
```

---

## Path Parameter Validation

### UUID Parameter

```typescript
// src/app/api/posts/[id]/route.ts
const postIdSchema = z.string().uuid()

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const result = postIdSchema.safeParse(params.id)
  if (!result.success) {
    return NextResponse.json(
      { error: 'Invalid post ID format' },
      { status: 400 }
    )
  }

  const post = await db.post.findUnique({ where: { id: result.data } })

  if (!post) {
    return NextResponse.json(
      { error: 'Post not found' },
      { status: 404 }
    )
  }

  return NextResponse.json({ post })
}
```

### Slug Parameter

```typescript
// src/app/api/posts/slug/[slug]/route.ts
const slugSchema = z.string().regex(/^[a-z0-9-]+$/)

export async function GET(
  request: NextRequest,
  { params }: { params: { slug: string } }
) {
  const validated = slugSchema.parse(params.slug)

  const post = await db.post.findUnique({ where: { slug: validated } })

  if (!post) {
    return NextResponse.json(
      { error: 'Post not found' },
      { status: 404 }
    )
  }

  return NextResponse.json({ post })
}
```

### Multiple Parameters

```typescript
// src/app/api/users/[userId]/posts/[postId]/route.ts
const paramsSchema = z.object({
  userId: z.string().uuid(),
  postId: z.string().uuid()
})

export async function GET(
  request: NextRequest,
  { params }: { params: { userId: string; postId: string } }
) {
  const validated = paramsSchema.parse(params)

  const post = await db.post.findFirst({
    where: {
      id: validated.postId,
      authorId: validated.userId
    }
  })

  if (!post) {
    return NextResponse.json(
      { error: 'Post not found' },
      { status: 404 }
    )
  }

  return NextResponse.json({ post })
}
```

---

## Form Data Validation

### Basic Form Data

```typescript
'use server'

const contactFormSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
  message: z.string().min(10, 'Message must be at least 10 characters')
})

export async function submitContactForm(formData: FormData) {
  const result = contactFormSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
    message: formData.get('message')
  })

  if (!result.success) {
    return {
      success: false,
      errors: result.error.flatten().fieldErrors
    }
  }

  await sendEmail(result.data)

  return { success: true }
}
```

### Form with Checkboxes

```typescript
const preferencesSchema = z.object({
  newsletter: z.string().transform(val => val === 'on').default('false'),
  notifications: z.string().transform(val => val === 'on').default('false'),
  marketing: z.string().transform(val => val === 'on').default('false')
})

export async function updatePreferences(formData: FormData) {
  const result = preferencesSchema.safeParse({
    newsletter: formData.get('newsletter'),
    notifications: formData.get('notifications'),
    marketing: formData.get('marketing')
  })

  if (!result.success) {
    return { success: false, errors: result.error.format() }
  }

  await db.user.update({
    where: { id: userId },
    data: result.data
  })

  return { success: true }
}
```

### Form with Array Fields

```typescript
const multipleFilesSchema = z.object({
  files: z.array(z.instanceof(File)).min(1).max(10)
})

export async function uploadFiles(formData: FormData) {
  const files = formData.getAll('files')

  const result = multipleFilesSchema.safeParse({ files })

  if (!result.success) {
    return { success: false, errors: result.error.format() }
  }

  const uploadedUrls = await Promise.all(
    result.data.files.map(file => uploadToS3(file))
  )

  return { success: true, urls: uploadedUrls }
}
```

---

## File Upload Validation

### Single File Upload

```typescript
'use server'

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

const fileUploadSchema = z.object({
  file: z.instanceof(File)
    .refine(file => file.size <= MAX_FILE_SIZE, 'File must be less than 5MB')
    .refine(
      file => ALLOWED_TYPES.includes(file.type),
      'Only JPEG, PNG, and WebP images allowed'
    )
})

export async function uploadFile(formData: FormData) {
  const result = fileUploadSchema.safeParse({
    file: formData.get('file')
  })

  if (!result.success) {
    return { success: false, errors: result.error.format() }
  }

  const url = await uploadToS3(result.data.file)

  return { success: true, url }
}
```

### Multiple Files with Validation

```typescript
const multipleImagesSchema = z.object({
  images: z.array(z.instanceof(File))
    .min(1, 'At least one image is required')
    .max(10, 'Maximum 10 images allowed')
    .refine(
      files => files.every(file => file.size <= MAX_FILE_SIZE),
      'Each file must be less than 5MB'
    )
    .refine(
      files => files.every(file => ALLOWED_TYPES.includes(file.type)),
      'All files must be JPEG, PNG, or WebP images'
    )
})

export async function uploadGallery(formData: FormData) {
  const images = formData.getAll('images')

  const result = multipleImagesSchema.safeParse({ images })

  if (!result.success) {
    return { success: false, errors: result.error.format() }
  }

  const urls = await Promise.all(
    result.data.images.map(uploadToS3)
  )

  return { success: true, urls }
}
```

---

## Error Response Formatting

### Standard Error Format

```typescript
type ErrorResponse = {
  error: string
  details?: Record<string, string[]>
  code?: string
}

function formatZodError(error: z.ZodError): ErrorResponse {
  return {
    error: 'Validation failed',
    details: error.flatten().fieldErrors,
    code: 'VALIDATION_ERROR'
  }
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const result = schema.safeParse(body)

  if (!result.success) {
    return NextResponse.json(
      formatZodError(result.error),
      { status: 400 }
    )
  }

  // Process
}
```

### Detailed Error Format

```typescript
function formatDetailedErrors(error: z.ZodError) {
  return {
    success: false,
    errors: error.errors.map(err => ({
      path: err.path.join('.'),
      message: err.message,
      code: err.code
    }))
  }
}
```

### User-Friendly Errors

```typescript
function formatUserFriendlyErrors(error: z.ZodError) {
  const fieldErrors: Record<string, string> = {}

  error.errors.forEach(err => {
    const field = err.path.join('.')
    if (!fieldErrors[field]) {
      fieldErrors[field] = err.message
    }
  })

  return {
    success: false,
    message: 'Please check the form for errors',
    fields: fieldErrors
  }
}
```

---

## Try-Catch Patterns

### API Route Error Handling

```typescript
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validate
    const validated = schema.parse(body)

    // Process
    const result = await processData(validated)

    return NextResponse.json({ result }, { status: 201 })

  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: error.format() },
        { status: 400 }
      )
    }

    if (error instanceof DatabaseError) {
      return NextResponse.json(
        { error: 'Database error' },
        { status: 500 }
      )
    }

    console.error('Unexpected error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

### Server Action Error Handling

```typescript
'use server'

export async function createPost(formData: FormData) {
  try {
    const validated = postSchema.parse({
      title: formData.get('title'),
      content: formData.get('content')
    })

    const post = await db.post.create({ data: validated })

    revalidatePath('/posts')

    return { success: true, data: post }

  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        errors: error.flatten().fieldErrors
      }
    }

    return {
      success: false,
      errors: { _form: ['Failed to create post'] }
    }
  }
}
```

---

## Summary

This document covered:
- ✅ API route validation (GET, POST, PATCH, DELETE)
- ✅ Server Actions with FormData and objects
- ✅ Middleware validation
- ✅ Request body, query params, and path params
- ✅ Form data and file upload validation
- ✅ Error response formatting
- ✅ Try-catch patterns for robust error handling

**Next Steps:**
- **[Common Schemas](./common-schemas.md)** - Ready-to-use validation schemas
- **[Error Handling](./error-handling.md)** - Advanced error patterns
- **[Schema Patterns](./schema-patterns.md)** - All schema types

---

*Last updated: 2025-11-23 | Zod v4.1.12*
