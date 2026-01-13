# API Patterns

For complete validation patterns, see: [zod-validation-patterns skill](../zod-validation-patterns/SKILL.md)

## API Route Template

```typescript
// app/api/projects/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { db } from '@/lib/db'
import { projectsTable } from '@/lib/db/schema'
import { getAuthUser } from '@/lib/auth'

// 1. Define Zod schema for input validation
const createProjectSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
})

export async function GET(request: NextRequest) {
  try {
    // 2. Check authentication
    const user = await getAuthUser(request)
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // 3. Fetch data
    const projects = await db
      .select()
      .from(projectsTable)
      .where(eq(projectsTable.userId, user.id))

    // 4. Return response
    return NextResponse.json(projects)
  } catch (error) {
    console.error('GET /api/projects failed:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    // 1. Check authentication
    const user = await getAuthUser(request)
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // 2. Parse and validate input
    const body = await request.json()
    const validated = createProjectSchema.parse(body)

    // 3. Execute business logic
    const project = await db
      .insert(projectsTable)
      .values({
        ...validated,
        userId: user.id,
      })
      .returning()

    // 4. Return response
    return NextResponse.json(project[0], { status: 201 })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid input', details: error.errors },
        { status: 400 }
      )
    }

    console.error('POST /api/projects failed:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // 1. Check authentication
    const user = await getAuthUser(request)
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // 2. Check resource exists
    const project = await db
      .select()
      .from(projectsTable)
      .where(eq(projectsTable.id, params.id))
      .limit(1)

    if (!project[0]) {
      return NextResponse.json(
        { error: 'Project not found' },
        { status: 404 }
      )
    }

    // 3. Check authorization (ownership)
    if (project[0].userId !== user.id) {
      return NextResponse.json(
        { error: 'Forbidden' },
        { status: 403 }
      )
    }

    // 4. Execute operation
    await db
      .delete(projectsTable)
      .where(eq(projectsTable.id, params.id))

    // 5. Return response
    return NextResponse.json(null, { status: 204 })
  } catch (error) {
    console.error('DELETE /api/projects failed:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

---

## Input Validation (Zod)

→ [Full Details](../zod-validation-patterns/SKILL.md)

**Every API route MUST validate input:**

```typescript
const createUserSchema = z.object({
  email: z.string().email().max(255),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .max(128)
    .regex(/[A-Z]/, 'Password must contain uppercase letter')
    .regex(/[a-z]/, 'Password must contain lowercase letter')
    .regex(/[0-9]/, 'Password must contain number')
    .regex(/[^A-Za-z0-9]/, 'Password must contain special character'),
  name: z.string().min(1).max(100).optional(),
})

export async function POST(request: NextRequest) {
  const body = await request.json()
  const validated = createUserSchema.parse(body) // Throws ZodError if invalid
  // ... use validated data
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (new resource) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input (validation error) |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Unexpected server error |

### Error Response Format

```typescript
// Validation error (400)
{
  "error": "Invalid input",
  "details": [
    {
      "path": ["email"],
      "message": "Invalid email format"
    }
  ]
}

// Authentication error (401)
{
  "error": "Unauthorized"
}

// Authorization error (403)
{
  "error": "Forbidden"
}

// Not found error (404)
{
  "error": "Project not found"
}

// Internal error (500)
{
  "error": "Internal server error"
}
```

---

## Authentication Pattern

```typescript
import { cookies } from 'next/headers'
import jwt from 'jsonwebtoken'

export async function getAuthUser(request: NextRequest) {
  const cookieStore = cookies()
  const token = cookieStore.get('session')?.value

  if (!token) {
    return null
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!)
    const user = await db
      .select()
      .from(usersTable)
      .where(eq(usersTable.id, decoded.userId))
      .limit(1)

    return user[0] || null
  } catch (error) {
    return null
  }
}
```

---

## Authorization Pattern

**Check resource ownership:**

```typescript
// 1. Get authenticated user
const user = await getAuthUser(request)
if (!user) {
  return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
}

// 2. Fetch resource
const project = await db
  .select()
  .from(projectsTable)
  .where(eq(projectsTable.id, params.id))
  .limit(1)

if (!project[0]) {
  return NextResponse.json({ error: 'Not found' }, { status: 404 })
}

// 3. Check ownership
if (project[0].userId !== user.id) {
  return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
}

// 4. Proceed with operation
```

---

## Response Format

### Success Response

```typescript
// Single resource
{
  "id": "123",
  "name": "Project Name",
  "createdAt": "2025-01-01T00:00:00Z"
}

// Multiple resources
[
  {
    "id": "123",
    "name": "Project 1"
  },
  {
    "id": "456",
    "name": "Project 2"
  }
]

// With pagination
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

---

## Common Patterns

### Pagination

```typescript
const paginationSchema = z.object({
  page: z.coerce.number().min(1).default(1),
  pageSize: z.coerce.number().min(1).max(100).default(20),
})

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const { page, pageSize } = paginationSchema.parse({
    page: searchParams.get('page'),
    pageSize: searchParams.get('pageSize'),
  })

  const offset = (page - 1) * pageSize

  const [data, total] = await Promise.all([
    db
      .select()
      .from(projectsTable)
      .limit(pageSize)
      .offset(offset),
    db
      .select({ count: count() })
      .from(projectsTable),
  ])

  return NextResponse.json({
    data,
    pagination: {
      page,
      pageSize,
      total: total[0].count,
      totalPages: Math.ceil(total[0].count / pageSize),
    },
  })
}
```

### Filtering

```typescript
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const status = searchParams.get('status')

  let query = db.select().from(projectsTable)

  if (status) {
    query = query.where(eq(projectsTable.status, status))
  }

  const projects = await query

  return NextResponse.json(projects)
}
```

### Sorting

```typescript
const sortSchema = z.object({
  sortBy: z.enum(['name', 'createdAt']).default('createdAt'),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
})

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const { sortBy, sortOrder } = sortSchema.parse({
    sortBy: searchParams.get('sortBy'),
    sortOrder: searchParams.get('sortOrder'),
  })

  const projects = await db
    .select()
    .from(projectsTable)
    .orderBy(
      sortOrder === 'asc'
        ? asc(projectsTable[sortBy])
        : desc(projectsTable[sortBy])
    )

  return NextResponse.json(projects)
}
```

---

## See Also

- [../zod-validation-patterns/SKILL.md](../zod-validation-patterns/SKILL.md) - Complete validation patterns
- [../security-sentinel/SKILL.md](../security-sentinel/SKILL.md) - Security best practices
- [database-patterns.md](./database-patterns.md) - Database operations
