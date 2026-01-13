---
name: nextjs-15-specialist
description: Use when working with Next.js 15 features, App Router, Server Components, Server Actions, or data fetching patterns. Ensures correct usage of Server vs Client Components and modern Next.js patterns.
allowed-tools: Read, Grep, Glob, WebFetch
---

# Next.js 15 + App Router Specialist

**Complete Next.js 15 reference for Quetrex development.**

This skill provides comprehensive guidance on all Next.js 15 App Router patterns, ensuring agents implement modern Next.js correctly the first time.

---

## CRITICAL RULES (NEVER VIOLATE)

These rules are NON-NEGOTIABLE. Violations will break builds.

### 1. ALWAYS use `<Image>` from `next/image` - NEVER use `<img>`

```typescript
// ✅ ALWAYS DO THIS
import Image from 'next/image'

<Image src="/logo.png" alt="Logo" width={200} height={100} />
<Image src={user.avatar} alt={user.name} width={40} height={40} />

// ❌ NEVER DO THIS - BUILD WILL FAIL
<img src="/logo.png" alt="Logo" />
<img src={user.avatar} alt={user.name} />
```

**Why:** Next.js Image component provides automatic optimization, lazy loading, and prevents layout shift. ESLint is configured to fail builds on `<img>` usage.

### 2. Server Components are DEFAULT - only add 'use client' when needed

### 3. Never make async Client Components

### 4. Always specify cache strategy for fetch()

---

## When to Use This Skill

Use this skill when working with:
- Creating new routes or pages
- Implementing data fetching (Server Components vs Client Components)
- Server vs Client Component decisions
- Server Actions and form handling
- Streaming and Suspense
- Metadata and SEO
- Route handlers (API routes)
- Caching strategies
- Performance optimization

---

## Complete Documentation

This skill includes comprehensive guides covering every Next.js 15 pattern:

### 📁 [App Router Complete Guide](./app-router-complete.md)
**45+ examples covering:**
- File-based routing (page.tsx, layout.tsx, route.ts)
- Dynamic routes ([id], [...slug], [[...slug]])
- Route groups ((group))
- Private folders (_folder)
- Route handlers (API routes)
- Layouts and templates
- Loading UI (loading.tsx)
- Error boundaries (error.tsx, global-error.tsx)
- Not found pages (not-found.tsx)
- Parallel routes (@folder)
- Intercepting routes ((.)folder)
- Route segment config (dynamic, revalidate, runtime)

### 🔄 [Data Fetching Complete Guide](./data-fetching-complete.md)
**35+ examples covering:**
- Server Component data fetching (async/await)
- Client Component data fetching (useEffect, React Query, SWR)
- Parallel data fetching (Promise.all)
- Sequential data fetching (waterfall prevention)
- Streaming data (Suspense boundaries)
- Server-Sent Events (SSE for Quetrex voice)
- Data mutations (Server Actions)
- Optimistic updates (useOptimistic)
- Form handling (useFormStatus, useActionState)
- Request deduplication
- Preloading data

### 💾 [Caching Strategies Guide](./caching-strategies.md)
**35+ examples covering:**
- Request memoization (automatic deduplication)
- Data Cache (fetch cache behavior)
- Full Route Cache (static vs dynamic)
- Router Cache (client-side cache)
- Cache configuration (force-cache, no-store, revalidate)
- Cache tags (revalidateTag, revalidatePath)
- On-demand revalidation
- Time-based revalidation (ISR)
- Cache debugging techniques
- Opting out of caching

### ⚡ [Server Actions Complete Guide](./server-actions-complete.md)
**31+ examples covering:**
- Basic Server Action patterns
- Form actions (progressive enhancement)
- Button actions (programmatic calls)
- useFormStatus hook (loading states)
- useActionState hook (state management)
- useOptimistic hook (optimistic UI)
- Error handling in actions
- Validation with Zod
- Returning JSON vs redirect
- Security (authentication, CSRF)
- Rate limiting
- Database transactions

### 🎯 [Metadata API Guide](./metadata-api.md)
**26+ examples covering:**
- Static metadata (exported object)
- Dynamic metadata (generateMetadata)
- File-based metadata (icon.png, opengraph-image.png)
- Open Graph metadata
- Twitter Cards
- JSON-LD structured data
- Viewport configuration
- PWA manifest
- Robots.txt
- Sitemap generation

### ✅ [Pattern Validator](./validate-patterns.py)
**Executable Python script that checks:**
- Server Components don't use client-only APIs
- Client Components have 'use client' directive
- Data fetching uses proper cache strategy
- Server Actions are marked with 'use server'
- Metadata API used correctly
- Image optimization (<Image> not <img>)
- Dynamic imports for heavy components

Run with: `python validate-patterns.py /path/to/src`

---

## Quick Reference

### Server vs Client Components Decision Tree

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

### Common Patterns

#### 1. Server Component Data Fetching

```typescript
// app/projects/page.tsx
export default async function ProjectsPage() {
  const projects = await db.project.findMany()
  return <ProjectList projects={projects} />
}
```

#### 2. Client Component with Interactivity

```typescript
// components/ProjectCard.tsx
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

#### 3. Server Action with Form

```typescript
// app/actions.ts
'use server'

export async function createProject(formData: FormData) {
  const name = formData.get('name') as string
  const project = await db.project.create({ data: { name } })
  revalidatePath('/projects')
  return { success: true, project }
}

// app/projects/new/page.tsx
import { createProject } from '@/app/actions'

export default function NewProjectPage() {
  return (
    <form action={createProject}>
      <input name="name" required />
      <button type="submit">Create</button>
    </form>
  )
}
```

#### 4. Streaming with Suspense

```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react'

export default function DashboardPage() {
  return (
    <div>
      <Suspense fallback={<ProjectsSkeleton />}>
        <ProjectsAsync />
      </Suspense>
      <Suspense fallback={<UsersSkeleton />}>
        <UsersAsync />
      </Suspense>
    </div>
  )
}

async function ProjectsAsync() {
  const projects = await fetchProjects() // Slow query
  return <ProjectList projects={projects} />
}
```

#### 5. Dynamic Metadata

```typescript
// app/blog/[slug]/page.tsx
import type { Metadata } from 'next'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const post = await fetchPost(slug)

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage],
    },
  }
}
```

---

## Best Practices for Quetrex

### 1. Default to Server Components

```typescript
// ✅ DO: Server Component (default)
export default async function ProjectsPage() {
  const projects = await fetchProjects()
  return <ProjectList projects={projects} />
}

// ❌ DON'T: Client Component when not needed
'use client'
export default function ProjectsPage() {
  const [projects, setProjects] = useState([])
  useEffect(() => {
    fetchProjects().then(setProjects)
  }, [])
  return <ProjectList projects={projects} />
}
```

### 2. Use Proper Cache Strategy

```typescript
// Static content (cached forever)
const categories = await fetch('https://api.example.com/categories', {
  cache: 'force-cache',
}).then(r => r.json())

// Dynamic content (no cache)
const user = await fetch('https://api.example.com/me', {
  cache: 'no-store',
}).then(r => r.json())

// ISR (revalidate every hour)
const products = await fetch('https://api.example.com/products', {
  next: { revalidate: 3600 },
}).then(r => r.json())
```

### 3. Implement Proper Error Boundaries

```typescript
// app/dashboard/error.tsx
'use client'

export default function DashboardError({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

### 4. Use Loading States

```typescript
// app/dashboard/loading.tsx
export default function DashboardLoading() {
  return <DashboardSkeleton />
}
```

### 5. Optimize Images

```typescript
// ✅ DO: Use next/image
import Image from 'next/image'

export function ProjectCard({ project }) {
  return (
    <Image
      src={project.image}
      alt={project.name}
      width={400}
      height={300}
    />
  )
}

// ❌ DON'T: Use <img> tag
export function ProjectCard({ project }) {
  return <img src={project.image} alt={project.name} />
}
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Async Client Component

```typescript
// ❌ DON'T: This is a syntax error
'use client'

export default async function BadComponent() {
  const data = await fetch('/api/data')
  return <div>{data}</div>
}

// ✅ DO: Use Server Component or useEffect
export default async function GoodComponent() {
  const data = await fetch('/api/data')
  return <div>{data}</div>
}
```

### ❌ Mistake 2: Client APIs in Server Component

```typescript
// ❌ DON'T: Server Components can't use browser APIs
export default function BadComponent() {
  const [state, setState] = useState(false) // Error!
  return <div>{state}</div>
}

// ✅ DO: Add 'use client' directive
'use client'

export default function GoodComponent() {
  const [state, setState] = useState(false)
  return <div>{state}</div>
}
```

### ❌ Mistake 3: Missing Cache Strategy

```typescript
// ❌ DON'T: Unclear caching behavior
const data = await fetch('/api/data')

// ✅ DO: Explicit cache strategy
const data = await fetch('/api/data', {
  cache: 'no-store', // or 'force-cache', or { next: { revalidate: 60 } }
})
```

### ❌ Mistake 4: Not Using <Image>

```typescript
// ❌ DON'T: Unoptimized images
<img src="/logo.png" alt="Logo" />

// ✅ DO: Use Next.js Image optimization
<Image src="/logo.png" alt="Logo" width={200} height={100} />
```

---

## Troubleshooting

### Error: "You're importing a component that needs useState..."

**Solution:** Add `'use client'` to the component file.

### Error: "async/await is not valid in Client Components"

**Solution:** Remove `'use client'` or use `useEffect` instead of async component.

### Error: "process is not defined"

**Solution:** Environment variables in Client Components need `NEXT_PUBLIC_` prefix.

### Error: "Headers already sent"

**Solution:** Don't use `headers()` or `cookies()` after sending response. Call them before any streaming.

---

## Official Documentation

- **Next.js 15.5 Docs**: https://nextjs.org/docs
- **App Router**: https://nextjs.org/docs/app
- **Data Fetching**: https://nextjs.org/docs/app/building-your-application/data-fetching
- **Server Actions**: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations
- **Caching**: https://nextjs.org/docs/app/building-your-application/caching
- **Metadata**: https://nextjs.org/docs/app/building-your-application/optimizing/metadata
- **Examples**: https://github.com/vercel/next.js/tree/canary/examples

---

## Validation

Run the pattern validator to check your code:

```bash
python .claude/skills/nextjs-15-specialist/validate-patterns.py src/
```

The validator checks for:
- ✅ Async Client Components (forbidden)
- ✅ Client APIs in Server Components
- ✅ 'use client' directive placement
- ✅ Server Action async functions
- ✅ Image optimization
- ✅ Metadata in dynamic routes
- ✅ Dynamic imports for heavy components
- ✅ Fetch cache strategies
- ✅ Route segment config

---

## Summary

**This skill ensures you:**
1. Choose correct component type (Server vs Client)
2. Implement proper data fetching patterns
3. Use appropriate caching strategies
4. Handle Server Actions correctly
5. Optimize metadata and SEO
6. Avoid common Next.js mistakes
7. Follow Quetrex's architecture guidelines

**When in doubt:**
- Read the specific guide (links above)
- Run the validator
- Check official Next.js 15 docs
- Default to Server Components

---

*Last updated: 2025-11-23*
*Next.js Version: 15.5*
*Total Examples: 150+*
*Total Lines: 4,000+*
