---
name: architecture-patterns
description: Organizational coding standards and architectural patterns. References comprehensive skills for detailed patterns. Use when making architecture decisions or implementing features.
allowed-tools: Read, Grep
---

# Architecture Patterns (Pattern Index)

## When to Use
- Making architecture decisions
- Implementing new features
- Reviewing code for pattern compliance
- Choosing between multiple approaches
- Learning established patterns

## Overview

This skill is a **pattern index** that references comprehensive skills for details. Use this to understand which pattern to use, then reference the specific skill for implementation details.

## Pattern Categories

### 1. Next.js Patterns
→ See: [nextjs-15-specialist skill](../nextjs-15-specialist/SKILL.md)

**Quick Reference:**
- **Server Components** (default): Data fetching, database access, backend APIs
- **Client Components** ('use client'): Interactivity, hooks, browser APIs
- **Server Actions** ('use server'): Form submissions, mutations
- **Route Handlers** (app/api/): REST API endpoints
- **Streaming**: Suspense boundaries for progressive loading

**Decision Tree:**
```
Need interactivity (onClick, onChange)?
├─ YES → Client Component
└─ NO → Server Component

Need React hooks (useState, useEffect)?
├─ YES → Client Component
└─ NO → Server Component

Need to fetch data?
└─ Prefer Server Component (better performance)
```

**Details:** [nextjs-patterns.md](./nextjs-patterns.md)

---

### 2. TypeScript Conventions
→ See: [typescript-strict-guard skill](../typescript-strict-guard/SKILL.md)

**Quick Reference:**
- **No `any`** - Use explicit types or `unknown` with type guards
- **No `@ts-ignore`** - Fix underlying type error
- **No `!` assertions** - Use optional chaining or type guards
- **Explicit types** - All function parameters and return types
- **Type guards** - Runtime validation for `unknown` types

**Decision Tree:**
```
Type is unknown at compile time?
├─ Use `unknown` with type guard
└─ Define explicit interface/type

Need optional property?
├─ Use `type?.property`
└─ Or `type ?? defaultValue`

Need to narrow union type?
└─ Use discriminated union or type guard
```

**Details:** [typescript-conventions.md](./typescript-conventions.md)

---

### 3. Database Patterns
→ See: [drizzle-orm-patterns skill](../drizzle-orm-patterns/SKILL.md)

**Quick Reference:**
- **Drizzle ORM** (not Prisma) - Edge runtime compatible
- **Parameterized queries** - SQL injection prevention
- **Transactions** - Atomic operations for multi-step changes
- **Relations** - Join queries with `.with()` syntax
- **Migrations** - Version-controlled schema changes

**Decision Tree:**
```
Need to query database?
├─ Simple query → db.select().from(table)
├─ Relations → .with() syntax
└─ Complex → Use joins explicitly

Need to modify data?
├─ Single record → db.insert/update/delete
└─ Multiple operations → Use transaction
```

**Details:** [database-patterns.md](./database-patterns.md)

---

### 4. State Management Patterns
**Quick Reference:**
- **Server state** → React Query (useQuery, useMutation)
- **Local UI state** → useState
- **Shared UI state** → Context API
- **URL state** → Next.js useSearchParams
- **Form state** → React Hook Form + Zod

**Decision Tree:**
```
What kind of state?
├─ Server data (API, database) → React Query
├─ Local UI (toggle, input) → useState
├─ Shared across components → Context
├─ URL parameters → useSearchParams
└─ Form data → React Hook Form
```

**Details:** [state-management-patterns.md](./state-management-patterns.md)

---

### 5. API Patterns
→ See: [zod-validation-patterns skill](../zod-validation-patterns/SKILL.md)

**Quick Reference:**
- **Input validation** → Zod schemas (MANDATORY)
- **Error handling** → try/catch with informative messages
- **Response format** → Consistent JSON structure
- **Status codes** → Proper HTTP semantics
- **Authentication** → Check before processing
- **Authorization** → Verify resource ownership

**Decision Tree:**
```
Implementing API route?
1. Define Zod schema for input validation
2. Check authentication (if protected)
3. Validate input with schema.parse()
4. Check authorization (resource ownership)
5. Execute business logic
6. Return appropriate status code
```

**Details:** [api-patterns.md](./api-patterns.md)

---

### 6. React 19 Patterns
→ See: [react-19-patterns skill](../react-19-patterns/SKILL.md)

**Quick Reference:**
- **use() hook** - Read resources (Promises, Context) in components
- **useOptimistic** - Optimistic UI updates
- **useFormStatus** - Form submission state
- **useActionState** - Server action state management
- **Actions** - Server/client actions for mutations

**Details:** [react-19-patterns.md](./react-19-patterns.md)

---

## Pattern Selection Guide

### Data Fetching

**Scenario:** Need to display data from database

**Options:**
1. **Server Component** (PREFERRED)
   - ✅ Best performance
   - ✅ No client bundle
   - ✅ Direct database access
   - ❌ No interactivity

2. **React Query in Client Component**
   - ✅ Caching, refetching, optimistic updates
   - ✅ Client-side interactivity
   - ❌ Larger bundle
   - ❌ Requires API route

3. **Server-Sent Events (SSE)**
   - ✅ Real-time updates
   - ✅ Automatic reconnection
   - ❌ More complex setup
   - ❌ Requires SSE endpoint

**Decision:**
```
Is data static or rarely changes?
└─ Use Server Component

Need real-time updates?
└─ Use SSE pattern

Need client-side caching/refetching?
└─ Use React Query
```

---

### Form Handling

**Scenario:** Need to handle form submission

**Options:**
1. **Server Actions** (PREFERRED)
   - ✅ Progressive enhancement
   - ✅ Works without JavaScript
   - ✅ Simple implementation
   - ❌ Limited client-side control

2. **Client Component + API Route**
   - ✅ Full client-side control
   - ✅ Complex validation
   - ✅ Multi-step forms
   - ❌ More code

**Decision:**
```
Simple form (create, update)?
└─ Use Server Action

Complex validation or multi-step?
└─ Use Client Component + API Route

Need optimistic UI updates?
└─ Use Client Component with useOptimistic
```

---

### Authentication

**Scenario:** Need to protect routes/resources

**Pattern:**
```typescript
// 1. Check authentication
const user = await getAuthUser(request)
if (!user) {
  return new Response('Unauthorized', { status: 401 })
}

// 2. Check authorization (resource ownership)
const resource = await db.resource.findUnique({ where: { id } })
if (!resource) {
  return new Response('Not found', { status: 404 })
}
if (resource.userId !== user.id) {
  return new Response('Forbidden', { status: 403 })
}

// 3. Proceed with operation
```

**See:** [../security-sentinel/SKILL.md](../security-sentinel/SKILL.md)

---

## Progressive Disclosure

This skill uses progressive disclosure:

1. **SKILL.md** (this file) - Pattern index and decision trees
2. **Pattern files** - Reference comprehensive skills
3. **Comprehensive skills** - Full implementation details

**Example workflow:**
1. Read SKILL.md to understand pattern categories
2. Use decision tree to select pattern
3. Reference specific pattern file for overview
4. Deep dive into comprehensive skill for details

---

## Integration with Other Skills

Architecture patterns aggregate knowledge from:
- **nextjs-15-specialist** - Next.js 15 complete patterns
- **typescript-strict-guard** - TypeScript strict mode
- **drizzle-orm-patterns** - Database operations
- **react-19-patterns** - React 19 features
- **zod-validation-patterns** - Input validation
- **security-sentinel** - Security best practices

---

## Common Patterns Quick Reference

### Create a new page with data
```typescript
// app/projects/page.tsx (Server Component)
export default async function ProjectsPage() {
  const projects = await db.select().from(projectsTable)
  return <ProjectList projects={projects} />
}
```

### Create an API endpoint
```typescript
// app/api/projects/route.ts
import { z } from 'zod'

const createSchema = z.object({
  name: z.string().min(1).max(100),
})

export async function POST(request: Request) {
  // 1. Validate input
  const body = await request.json()
  const validated = createSchema.parse(body)

  // 2. Check auth
  const user = await getAuthUser(request)
  if (!user) return new Response('Unauthorized', { status: 401 })

  // 3. Execute
  const project = await db.insert(projectsTable).values({
    ...validated,
    userId: user.id,
  })

  return Response.json(project, { status: 201 })
}
```

### Add interactivity to a component
```typescript
// components/ProjectCard.tsx (Client Component)
'use client'

import { useState } from 'react'

export function ProjectCard({ project }: Props) {
  const [loading, setLoading] = useState(false)

  const handleDelete = async () => {
    setLoading(true)
    await deleteProject(project.id)
    setLoading(false)
  }

  return (
    <div>
      <h2>{project.name}</h2>
      <button onClick={handleDelete} disabled={loading}>
        Delete
      </button>
    </div>
  )
}
```

---

## See Also

- nextjs-patterns.md - Next.js pattern details
- typescript-conventions.md - TypeScript standards
- database-patterns.md - Database operation patterns
- state-management-patterns.md - State management guide
- api-patterns.md - API design patterns
- react-19-patterns.md - React 19 features
