# Next.js Patterns

For complete Next.js patterns, see: [nextjs-15-specialist skill](../nextjs-15-specialist/SKILL.md)

## Quick Reference

### Server Components
→ [Full Details](../nextjs-15-specialist/SKILL.md#server-components-default)

Default in Next.js App Router. Use for:
- Data fetching from database
- Backend API access
- Static content rendering
- SEO optimization

**Example:**
```typescript
export default async function ProjectsPage() {
  const projects = await db.select().from(projectsTable)
  return <ProjectList projects={projects} />
}
```

---

### Client Components
→ [Full Details](../nextjs-15-specialist/SKILL.md#client-components)

Add `'use client'` for:
- Interactivity (onClick, onChange)
- React hooks (useState, useEffect)
- Browser APIs (window, localStorage)
- Event handlers

**Example:**
```typescript
'use client'

import { useState } from 'react'

export function ProjectCard({ project }: Props) {
  const [loading, setLoading] = useState(false)
  // ...
}
```

---

### Data Fetching
→ [Full Details](../nextjs-15-specialist/SKILL.md#data-fetching-patterns)

**Server Component (Recommended):**
```typescript
export default async function Page() {
  const data = await fetchData() // Direct fetch
  return <Display data={data} />
}
```

**Client Component (When needed):**
```typescript
'use client'

import { useQuery } from '@tanstack/react-query'

export function Component() {
  const { data } = useQuery({
    queryKey: ['data'],
    queryFn: () => fetch('/api/data').then(r => r.json()),
  })
  return <Display data={data} />
}
```

---

### Server Actions
→ [Full Details](../nextjs-15-specialist/SKILL.md#server-actions)

**Use for:** Form submissions, mutations

```typescript
'use server'

export async function createProject(formData: FormData) {
  const validated = schema.parse({
    name: formData.get('name'),
  })

  await db.insert(projectsTable).values(validated)
  revalidatePath('/projects')
}
```

---

### Route Handlers (API Routes)
→ [Full Details](../nextjs-15-specialist/SKILL.md#route-handlers-api-routes)

**Use for:** REST API endpoints, webhooks

```typescript
// app/api/projects/route.ts
export async function GET(request: Request) {
  const projects = await db.select().from(projectsTable)
  return Response.json(projects)
}

export async function POST(request: Request) {
  const body = await request.json()
  const validated = schema.parse(body)
  const project = await db.insert(projectsTable).values(validated)
  return Response.json(project, { status: 201 })
}
```

---

### Streaming and Suspense
→ [Full Details](../nextjs-15-specialist/SKILL.md#streaming-and-suspense)

**Use for:** Progressive loading, slow data

```typescript
export default function Page() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<ProjectsSkeleton />}>
        <ProjectsList />
      </Suspense>
      <Suspense fallback={<UsersSkeleton />}>
        <UsersList />
      </Suspense>
    </div>
  )
}
```

---

## Decision Tree: Server vs Client Component

```
Do you need interactivity (onClick, onChange, etc.)?
├─ YES → Client Component ('use client')
└─ NO → Server Component (default)

Do you need React hooks (useState, useEffect)?
├─ YES → Client Component
└─ NO → Server Component

Do you need browser APIs (window, localStorage)?
├─ YES → Client Component
└─ NO → Server Component

Do you need to fetch data?
├─ Use Server Component (preferred)
└─ Only use Client Component if data must be client-side

Is the component purely presentational?
└─ Server Component (better performance)
```

---

## Common Mistakes

### ❌ Async Client Component
```typescript
'use client'

export default async function BadComponent() {
  const data = await fetch('/api/data') // ERROR!
  return <div>{data}</div>
}
```

**Fix:** Remove `'use client'` or use useEffect

---

### ❌ Using useState in Server Component
```typescript
export default function BadComponent() {
  const [state, setState] = useState(0) // ERROR!
  return <div>{state}</div>
}
```

**Fix:** Add `'use client'` directive

---

### ❌ Fetching in useEffect when Server Component works
```typescript
'use client'

export default function SuboptimalComponent() {
  const [data, setData] = useState(null)
  useEffect(() => {
    fetch('/api/data').then(r => r.json()).then(setData)
  }, [])
  return <div>{data}</div>
}
```

**Fix:** Use Server Component:
```typescript
export default async function OptimalComponent() {
  const data = await fetch('/api/data').then(r => r.json())
  return <div>{data}</div>
}
```

---

## Pattern Selection

| Use Case | Pattern | Why |
|----------|---------|-----|
| Display database data | Server Component | Direct access, no bundle |
| Interactive button | Client Component | Needs onClick handler |
| Form with validation | Server Action | Progressive enhancement |
| REST API endpoint | Route Handler | Standard API |
| Real-time updates | SSE/Client Component | Live data |
| Static content | Server Component | SEO, performance |

---

## See Also

- [nextjs-15-specialist/SKILL.md](../nextjs-15-specialist/SKILL.md) - Complete patterns
- [../typescript-strict-guard/SKILL.md](../typescript-strict-guard/SKILL.md) - Type safety
- [state-management-patterns.md](./state-management-patterns.md) - State decisions
