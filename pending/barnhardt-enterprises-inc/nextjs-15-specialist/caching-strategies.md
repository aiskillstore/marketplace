# Next.js 15 Caching Strategies - Complete Guide

Complete reference for all caching mechanisms in Next.js 15 App Router.

**Official Docs:** https://nextjs.org/docs/app/building-your-application/caching

---

## Table of Contents

- [Caching Overview](#caching-overview)
- [Request Memoization](#request-memoization)
- [Data Cache](#data-cache)
- [Full Route Cache](#full-route-cache)
- [Router Cache](#router-cache)
- [Cache Tags](#cache-tags)
- [Revalidation](#revalidation)
- [Cache Debugging](#cache-debugging)
- [Opting Out](#opting-out)

---

## Caching Overview

Next.js has 4 caching mechanisms:

1. **Request Memoization** - Deduplicates requests in single render
2. **Data Cache** - Persists fetch results across requests
3. **Full Route Cache** - Caches rendered routes at build time
4. **Router Cache** - Client-side cache of visited routes

---

## Request Memoization

Automatic deduplication of identical fetch requests during a single render.

### Example 1: Automatic Deduplication

```typescript
// lib/data.ts
export async function getUser(id: string) {
  // This fetch is memoized per request
  const res = await fetch(`https://api.example.com/users/${id}`)
  return res.json()
}

// app/user/[id]/page.tsx
export default async function UserPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  // All three calls are deduplicated - only ONE request sent
  const user1 = await getUser(id)
  const user2 = await getUser(id)
  const user3 = await getUser(id)

  return <UserProfile user={user1} />
}
```

### Example 2: React cache() Function

```typescript
// lib/data.ts
import { cache } from 'react'

// cache() memoizes function calls (not just fetch)
export const getProject = cache(async (id: string) => {
  console.log('Database query for:', id) // Only logs once per request

  return await db.project.findUnique({
    where: { id },
    include: {
      owner: true,
      collaborators: true,
    },
  })
})

// Multiple calls to getProject(id) are deduplicated
```

### Example 3: Cross-Component Deduplication

```typescript
// app/project/[id]/page.tsx

async function ProjectHeader({ id }: { id: string }) {
  const project = await getProject(id) // Call 1
  return <h1>{project.name}</h1>
}

async function ProjectDetails({ id }: { id: string }) {
  const project = await getProject(id) // Call 2 - deduplicated
  return <p>{project.description}</p>
}

async function ProjectStats({ id }: { id: string }) {
  const project = await getProject(id) // Call 3 - deduplicated
  return <div>Stars: {project.stars}</div>
}

export default async function ProjectPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  // All three components call getProject(id)
  // Only ONE database query is executed
  return (
    <div>
      <ProjectHeader id={id} />
      <ProjectDetails id={id} />
      <ProjectStats id={id} />
    </div>
  )
}
```

---

## Data Cache

Persistent cache for fetch results across requests and deployments.

### Example 4: Force Cache (Default)

```typescript
// Data is cached indefinitely (static generation)
export default async function BlogPage() {
  const posts = await fetch('https://api.example.com/posts', {
    cache: 'force-cache', // Default
  }).then(r => r.json())

  return <PostList posts={posts} />
}

// Same as:
export default async function BlogPage() {
  const posts = await fetch('https://api.example.com/posts')
    .then(r => r.json())

  return <PostList posts={posts} />
}
```

### Example 5: No Store (Dynamic)

```typescript
// Always fetch fresh data (no caching)
export default async function DashboardPage() {
  const metrics = await fetch('https://api.example.com/metrics', {
    cache: 'no-store', // Never cache
  }).then(r => r.json())

  return <MetricsDashboard data={metrics} />
}
```

### Example 6: Time-Based Revalidation

```typescript
// Cache for 60 seconds, then revalidate
export default async function NewsPage() {
  const news = await fetch('https://api.example.com/news', {
    next: { revalidate: 60 }, // Revalidate every 60 seconds
  }).then(r => r.json())

  return <NewsList items={news} />
}
```

### Example 7: Multiple Fetch Strategies

```typescript
export default async function MixedPage() {
  // Static (cached forever)
  const categories = await fetch('https://api.example.com/categories', {
    cache: 'force-cache',
  }).then(r => r.json())

  // ISR (revalidate every hour)
  const products = await fetch('https://api.example.com/products', {
    next: { revalidate: 3600 },
  }).then(r => r.json())

  // Dynamic (no cache)
  const user = await fetch('https://api.example.com/user', {
    cache: 'no-store',
  }).then(r => r.json())

  return <Page categories={categories} products={products} user={user} />
}
```

---

## Full Route Cache

Caches rendered HTML and RSC payload at build time.

### Example 8: Static Route (Fully Cached)

```typescript
// app/about/page.tsx

// Route is fully static (cached at build time)
export default function AboutPage() {
  return (
    <div>
      <h1>About Us</h1>
      <p>Static content cached at build time.</p>
    </div>
  )
}
```

### Example 9: Dynamic Route with Static Generation

```typescript
// app/blog/[slug]/page.tsx

// Generate static pages at build time
export async function generateStaticParams() {
  const posts = await fetch('https://api.example.com/posts')
    .then(r => r.json())

  return posts.map((post: any) => ({
    slug: post.slug,
  }))
}

// Each page is cached at build time
export default async function BlogPost({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = await fetch(`https://api.example.com/posts/${slug}`, {
    cache: 'force-cache',
  }).then(r => r.json())

  return <Article post={post} />
}
```

### Example 10: Force Dynamic Rendering

```typescript
// app/dashboard/page.tsx

// Opt out of Full Route Cache
export const dynamic = 'force-dynamic'

export default async function DashboardPage() {
  // Page is rendered on every request (not cached)
  const data = await fetchDashboardData()
  return <Dashboard data={data} />
}
```

### Example 11: Static with Dynamic Segments

```typescript
// app/products/[category]/page.tsx

// Make route static despite dynamic segment
export const dynamicParams = false // Only allow pre-generated params

export async function generateStaticParams() {
  return [
    { category: 'electronics' },
    { category: 'clothing' },
    { category: 'books' },
  ]
}

export default async function CategoryPage({
  params,
}: {
  params: Promise<{ category: string }>
}) {
  const { category } = await params
  const products = await fetchProducts(category)
  return <ProductGrid products={products} />
}
```

---

## Router Cache

Client-side cache of visited routes (browser only).

### Example 12: Link Prefetching

```typescript
// components/Navigation.tsx
import Link from 'next/link'

export function Navigation() {
  return (
    <nav>
      {/* Prefetches on hover (default) */}
      <Link href="/about" prefetch={true}>
        About
      </Link>

      {/* No prefetch */}
      <Link href="/admin" prefetch={false}>
        Admin
      </Link>

      {/* Prefetch only in production */}
      <Link href="/dashboard">
        Dashboard
      </Link>
    </nav>
  )
}
```

### Example 13: Programmatic Prefetch

```typescript
// components/ProjectCard.tsx
'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export function ProjectCard({ id }: { id: string }) {
  const router = useRouter()

  useEffect(() => {
    // Prefetch route programmatically
    router.prefetch(`/projects/${id}`)
  }, [id, router])

  return (
    <div onClick={() => router.push(`/projects/${id}`)}>
      Project {id}
    </div>
  )
}
```

### Example 14: Router Cache Duration

```typescript
// Default cache durations:
// - Static routes: 5 minutes
// - Dynamic routes: 30 seconds

// Clear router cache by refreshing
'use client'

import { useRouter } from 'next/navigation'

export function RefreshButton() {
  const router = useRouter()

  return (
    <button onClick={() => router.refresh()}>
      Refresh
    </button>
  )
}
```

---

## Cache Tags

Tag caches for granular revalidation.

### Example 15: Basic Cache Tags

```typescript
// app/projects/page.tsx

export default async function ProjectsPage() {
  const projects = await fetch('https://api.example.com/projects', {
    next: {
      tags: ['projects'], // Tag this cache entry
      revalidate: 3600,
    },
  }).then(r => r.json())

  return <ProjectList projects={projects} />
}

// Revalidate by tag in Server Action:
// revalidateTag('projects')
```

### Example 16: Multiple Tags

```typescript
// app/user/[id]/projects/page.tsx

export default async function UserProjectsPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  const projects = await fetch(
    `https://api.example.com/users/${id}/projects`,
    {
      next: {
        tags: ['projects', `user-${id}`], // Multiple tags
        revalidate: 3600,
      },
    }
  ).then(r => r.json())

  return <ProjectList projects={projects} />
}

// Revalidate all projects:
// revalidateTag('projects')

// Revalidate specific user's projects:
// revalidateTag('user-123')
```

### Example 17: Revalidate Tag in Server Action

```typescript
// app/actions.ts
'use server'

import { revalidateTag } from 'next/cache'

export async function createProject(formData: FormData) {
  const project = await db.project.create({
    data: {
      name: formData.get('name') as string,
    },
  })

  // Revalidate all caches tagged with 'projects'
  revalidateTag('projects')

  return { success: true, project }
}
```

### Example 18: Hierarchical Tags

```typescript
// lib/data.ts

export async function getProjects(orgId: string) {
  return fetch(`https://api.example.com/orgs/${orgId}/projects`, {
    next: {
      tags: [
        'projects',           // All projects
        `org-${orgId}`,       // Organization projects
        `org-${orgId}-projects`, // Specific tag
      ],
    },
  })
}

// Revalidate strategies:
// revalidateTag('projects')        → All projects
// revalidateTag('org-123')         → All org-123 data
// revalidateTag('org-123-projects') → Only org-123 projects
```

---

## Revalidation

Revalidate cached data on-demand or time-based.

### Example 19: Time-Based Revalidation (ISR)

```typescript
// app/blog/page.tsx

// Revalidate every 60 seconds
export const revalidate = 60

export default async function BlogPage() {
  const posts = await fetchPosts()
  return <PostList posts={posts} />
}
```

### Example 20: On-Demand Path Revalidation

```typescript
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'

export async function updateProject(id: string, data: any) {
  await db.project.update({
    where: { id },
    data,
  })

  // Revalidate specific path
  revalidatePath('/projects')
  revalidatePath(`/projects/${id}`)

  return { success: true }
}
```

### Example 21: Revalidate Layout and Children

```typescript
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'

export async function updateSettings() {
  await db.settings.update({ /* ... */ })

  // Revalidate layout and all nested pages
  revalidatePath('/dashboard', 'layout')

  // Revalidate specific page only (default)
  revalidatePath('/dashboard', 'page')

  return { success: true }
}
```

### Example 22: Webhook Revalidation

```typescript
// app/api/revalidate/route.ts
import { revalidateTag, revalidatePath } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const secret = request.nextUrl.searchParams.get('secret')

  // Validate secret
  if (secret !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ error: 'Invalid secret' }, { status: 401 })
  }

  const { tag, path } = await request.json()

  if (tag) {
    revalidateTag(tag)
  }

  if (path) {
    revalidatePath(path)
  }

  return NextResponse.json({ revalidated: true })
}

// Usage:
// POST /api/revalidate?secret=xxx
// { "tag": "projects" }
```

### Example 23: Batch Revalidation

```typescript
// app/actions.ts
'use server'

import { revalidateTag, revalidatePath } from 'next/cache'

export async function publishPost(id: string) {
  await db.post.update({
    where: { id },
    data: { published: true },
  })

  // Revalidate multiple caches
  revalidateTag('posts')
  revalidateTag('blog')
  revalidatePath('/blog')
  revalidatePath(`/blog/${id}`)

  return { success: true }
}
```

---

## Cache Debugging

Debug caching behavior in development and production.

### Example 24: Cache Headers Inspection

```typescript
// app/api/debug/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  const response = NextResponse.json({ message: 'Debug' })

  // Inspect cache headers
  response.headers.set('Cache-Control', 's-maxage=3600, stale-while-revalidate')

  return response
}
```

### Example 25: Development Cache Logging

```typescript
// lib/data.ts

export async function getProject(id: string) {
  console.log('[CACHE] Fetching project:', id, new Date().toISOString())

  const project = await fetch(`https://api.example.com/projects/${id}`, {
    next: { revalidate: 60, tags: ['projects'] },
  }).then(r => r.json())

  console.log('[CACHE] Project fetched:', id)

  return project
}
```

### Example 26: Cache Status Component

```typescript
// components/CacheStatus.tsx
'use client'

import { useEffect, useState } from 'react'

export function CacheStatus() {
  const [cacheTime, setCacheTime] = useState<string>('')

  useEffect(() => {
    setCacheTime(new Date().toISOString())
  }, [])

  return (
    <div className="cache-status">
      <small>Rendered at: {cacheTime}</small>
    </div>
  )
}
```

---

## Opting Out

Disable caching when needed.

### Example 27: Opt Out of Data Cache

```typescript
// app/dashboard/page.tsx

export default async function DashboardPage() {
  // Don't cache this fetch
  const data = await fetch('https://api.example.com/live-data', {
    cache: 'no-store',
  }).then(r => r.json())

  return <Dashboard data={data} />
}
```

### Example 28: Opt Out of Full Route Cache

```typescript
// app/profile/page.tsx

// Force dynamic rendering (no route cache)
export const dynamic = 'force-dynamic'

export default async function ProfilePage() {
  const user = await getCurrentUser()
  return <Profile user={user} />
}
```

### Example 29: Disable Request Memoization

```typescript
// lib/data.ts

// Disable memoization by adding cache-busting param
export async function getLiveData() {
  const cacheBuster = Date.now()

  return fetch(`https://api.example.com/live?t=${cacheBuster}`, {
    cache: 'no-store',
  }).then(r => r.json())
}
```

### Example 30: Mixed Caching Strategy

```typescript
// app/page.tsx

export default async function HomePage() {
  // Cached (static)
  const categories = await fetch('https://api.example.com/categories', {
    cache: 'force-cache',
  }).then(r => r.json())

  // Not cached (dynamic)
  const user = await fetch('https://api.example.com/me', {
    cache: 'no-store',
  }).then(r => r.json())

  // Page is dynamic due to 'no-store' fetch
  return <Home categories={categories} user={user} />
}
```

---

## Advanced Patterns

### Example 31: Stale-While-Revalidate

```typescript
// app/products/page.tsx

export default async function ProductsPage() {
  const products = await fetch('https://api.example.com/products', {
    next: {
      revalidate: 3600, // Revalidate every hour
      tags: ['products'],
    },
  }).then(r => r.json())

  // Serves stale content immediately
  // Revalidates in background
  return <ProductGrid products={products} />
}
```

### Example 32: Per-Request Cache Control

```typescript
// app/api/data/route.ts
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const data = await fetchData()

  const response = NextResponse.json(data)

  // Custom cache control per request
  const url = new URL(request.url)
  const skipCache = url.searchParams.get('skipCache') === 'true'

  if (skipCache) {
    response.headers.set('Cache-Control', 'no-cache, no-store')
  } else {
    response.headers.set('Cache-Control', 's-maxage=3600, stale-while-revalidate')
  }

  return response
}
```

### Example 33: Conditional Revalidation

```typescript
// app/actions.ts
'use server'

import { revalidateTag } from 'next/cache'

export async function updateProject(id: string, data: any) {
  const project = await db.project.update({
    where: { id },
    data,
  })

  // Only revalidate if published
  if (project.published) {
    revalidateTag('projects')
    revalidateTag('public-projects')
  }

  return { success: true, project }
}
```

### Example 34: Cache Warming

```typescript
// scripts/warm-cache.ts

async function warmCache() {
  const routes = [
    '/products',
    '/blog',
    '/about',
  ]

  for (const route of routes) {
    await fetch(`https://example.com${route}`)
    console.log(`Warmed: ${route}`)
  }
}

warmCache()
```

### Example 35: Multi-Region Caching

```typescript
// app/api/global/route.ts

export const runtime = 'edge'
export const preferredRegion = 'auto' // All regions

export async function GET() {
  const data = await fetch('https://api.example.com/global', {
    next: {
      revalidate: 60,
      tags: ['global'],
    },
  }).then(r => r.json())

  return Response.json(data, {
    headers: {
      'Cache-Control': 's-maxage=60, stale-while-revalidate=86400',
    },
  })
}
```

---

## Summary

**4 Caching Mechanisms:**

1. **Request Memoization**
   - Automatic fetch deduplication
   - Per-request lifecycle
   - Use `cache()` for non-fetch functions

2. **Data Cache**
   - Persistent across requests
   - Controlled by `cache` and `next` options
   - Revalidate with tags or time

3. **Full Route Cache**
   - Static generation at build time
   - Opt out with `dynamic = 'force-dynamic'`
   - Controlled by route segment config

4. **Router Cache**
   - Client-side cache
   - 5 minutes (static) / 30 seconds (dynamic)
   - Cleared by `router.refresh()`

**Cache Configuration:**

```typescript
// Static (cached forever)
cache: 'force-cache'

// Dynamic (no cache)
cache: 'no-store'

// ISR (time-based revalidation)
next: { revalidate: 60 }

// Tag-based revalidation
next: { tags: ['projects'] }
```

**Revalidation:**

```typescript
// By tag
revalidateTag('projects')

// By path
revalidatePath('/projects')

// By path and type
revalidatePath('/dashboard', 'layout')
```

**Best Practices:**
1. Use cache tags for granular control
2. Implement on-demand revalidation
3. Use ISR for semi-static content
4. Opt out only when necessary
5. Monitor cache performance
6. Debug with logging in development

**Official Docs:**
- Caching: https://nextjs.org/docs/app/building-your-application/caching
- Revalidating: https://nextjs.org/docs/app/building-your-application/data-fetching/fetching-caching-and-revalidating
