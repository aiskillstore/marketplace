# Next.js 15 Data Fetching - Complete Guide

Complete reference for all data fetching patterns in Next.js 15 with App Router.

**Official Docs:** https://nextjs.org/docs/app/building-your-application/data-fetching

---

## Table of Contents

- [Server Component Data Fetching](#server-component-data-fetching)
- [Client Component Data Fetching](#client-component-data-fetching)
- [Parallel Data Fetching](#parallel-data-fetching)
- [Sequential Data Fetching](#sequential-data-fetching)
- [Streaming Data](#streaming-data)
- [Server-Sent Events](#server-sent-events)
- [Data Mutations](#data-mutations)
- [Optimistic Updates](#optimistic-updates)
- [Form Handling](#form-handling)
- [Request Deduplication](#request-deduplication)
- [Preloading Data](#preloading-data)

---

## Server Component Data Fetching

Server Components can fetch data directly with async/await.

### Example 1: Basic Server Component Fetch

```typescript
// app/projects/page.tsx
import { db } from '@/lib/db'

export default async function ProjectsPage() {
  // Fetch data directly in Server Component
  const projects = await db.project.findMany({
    orderBy: { createdAt: 'desc' },
  })

  return (
    <div>
      <h1>Projects ({projects.length})</h1>
      <ProjectList projects={projects} />
    </div>
  )
}
```

### Example 2: Fetch with Cache Control

```typescript
// app/blog/page.tsx

export default async function BlogPage() {
  // Force cache (static generation)
  const posts = await fetch('https://api.example.com/posts', {
    cache: 'force-cache', // Default behavior
  }).then(r => r.json())

  return <PostList posts={posts} />
}
```

### Example 3: No Store (Dynamic Rendering)

```typescript
// app/dashboard/page.tsx

export default async function DashboardPage() {
  // No cache (always fetch fresh)
  const metrics = await fetch('https://api.example.com/metrics', {
    cache: 'no-store', // Equivalent to getServerSideProps
  }).then(r => r.json())

  return <MetricsDashboard data={metrics} />
}
```

### Example 4: Revalidate (ISR)

```typescript
// app/news/page.tsx

export default async function NewsPage() {
  // Revalidate every 60 seconds (ISR)
  const news = await fetch('https://api.example.com/news', {
    next: { revalidate: 60 },
  }).then(r => r.json())

  return <NewsList items={news} />
}
```

### Example 5: Tagged Cache

```typescript
// app/products/page.tsx

export default async function ProductsPage() {
  // Tagged cache (can revalidate by tag)
  const products = await fetch('https://api.example.com/products', {
    next: {
      tags: ['products'],
      revalidate: 3600, // 1 hour
    },
  }).then(r => r.json())

  return <ProductGrid products={products} />
}

// Revalidate in Server Action:
// revalidateTag('products')
```

### Example 6: Direct Database Access

```typescript
// app/users/page.tsx
import { db } from '@/lib/db'

export default async function UsersPage() {
  const users = await db.user.findMany({
    select: {
      id: true,
      email: true,
      name: true,
      _count: {
        select: { projects: true },
      },
    },
  })

  return <UserTable users={users} />
}
```

### Example 7: Multiple Queries in Server Component

```typescript
// app/dashboard/page.tsx
import { db } from '@/lib/db'

export default async function DashboardPage() {
  const [projects, users, metrics] = await Promise.all([
    db.project.findMany({ take: 10 }),
    db.user.findMany({ take: 5 }),
    db.metric.aggregate({
      _count: true,
      _avg: { score: true },
    }),
  ])

  return (
    <div className="dashboard">
      <ProjectsSummary projects={projects} />
      <RecentUsers users={users} />
      <MetricsOverview metrics={metrics} />
    </div>
  )
}
```

---

## Client Component Data Fetching

Client Components use hooks for data fetching.

### Example 8: useEffect with Fetch

```typescript
// components/ProjectsClient.tsx
'use client'

import { useState, useEffect } from 'react'

interface Project {
  id: string
  name: string
}

export function ProjectsClient() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    fetch('/api/projects')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch')
        return res.json()
      })
      .then(data => {
        setProjects(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err)
        setLoading(false)
      })
  }, [])

  if (loading) return <Skeleton />
  if (error) return <Error error={error} />
  return <ProjectList projects={projects} />
}
```

### Example 9: React Query (TanStack Query)

```typescript
// components/ProjectsQuery.tsx
'use client'

import { useQuery } from '@tanstack/react-query'

export function ProjectsQuery() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const res = await fetch('/api/projects')
      if (!res.ok) throw new Error('Failed to fetch projects')
      return res.json()
    },
    staleTime: 60000, // 1 minute
    refetchOnWindowFocus: true,
  })

  if (isLoading) return <Skeleton />
  if (error) return <Error error={error} />
  return <ProjectList projects={data} />
}
```

### Example 10: SWR (Stale-While-Revalidate)

```typescript
// components/ProjectsSWR.tsx
'use client'

import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export function ProjectsSWR() {
  const { data, error, isLoading } = useSWR('/api/projects', fetcher, {
    refreshInterval: 60000, // Refresh every minute
    revalidateOnFocus: true,
    dedupingInterval: 2000,
  })

  if (isLoading) return <Skeleton />
  if (error) return <Error error={error} />
  return <ProjectList projects={data} />
}
```

### Example 11: Infinite Query (React Query)

```typescript
// components/InfiniteProjectList.tsx
'use client'

import { useInfiniteQuery } from '@tanstack/react-query'

export function InfiniteProjectList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['projects', 'infinite'],
    queryFn: async ({ pageParam = 0 }) => {
      const res = await fetch(`/api/projects?offset=${pageParam}&limit=20`)
      return res.json()
    },
    getNextPageParam: (lastPage, pages) => {
      return lastPage.hasMore ? pages.length * 20 : undefined
    },
  })

  return (
    <div>
      {data?.pages.map((page, i) => (
        <div key={i}>
          {page.projects.map((project: any) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      ))}

      {hasNextPage && (
        <button onClick={() => fetchNextPage()} disabled={isFetchingNextPage}>
          {isFetchingNextPage ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  )
}
```

### Example 12: Polling with React Query

```typescript
// components/LiveMetrics.tsx
'use client'

import { useQuery } from '@tanstack/react-query'

export function LiveMetrics() {
  const { data } = useQuery({
    queryKey: ['metrics'],
    queryFn: () => fetch('/api/metrics').then(r => r.json()),
    refetchInterval: 5000, // Poll every 5 seconds
    refetchIntervalInBackground: false, // Stop when tab inactive
  })

  return <MetricsChart data={data} />
}
```

---

## Parallel Data Fetching

Fetch multiple data sources simultaneously.

### Example 13: Promise.all in Server Component

```typescript
// app/dashboard/page.tsx

export default async function DashboardPage() {
  // All fetches happen in parallel
  const [projects, users, analytics] = await Promise.all([
    fetch('https://api.example.com/projects').then(r => r.json()),
    fetch('https://api.example.com/users').then(r => r.json()),
    fetch('https://api.example.com/analytics').then(r => r.json()),
  ])

  return (
    <Dashboard
      projects={projects}
      users={users}
      analytics={analytics}
    />
  )
}
```

### Example 14: Database Parallel Queries

```typescript
// app/reports/page.tsx
import { db } from '@/lib/db'

export default async function ReportsPage() {
  const [
    projectCount,
    userCount,
    recentActivity,
    topProjects,
  ] = await Promise.all([
    db.project.count(),
    db.user.count(),
    db.activity.findMany({ take: 10, orderBy: { createdAt: 'desc' } }),
    db.project.findMany({ take: 5, orderBy: { stars: 'desc' } }),
  ])

  return (
    <div className="reports">
      <Stats projectCount={projectCount} userCount={userCount} />
      <RecentActivity items={recentActivity} />
      <TopProjects projects={topProjects} />
    </div>
  )
}
```

### Example 15: Parallel with Suspense

```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react'

export default function DashboardPage() {
  // Each component fetches in parallel, streams independently
  return (
    <div className="dashboard">
      <Suspense fallback={<ProjectsSkeleton />}>
        <ProjectsAsync />
      </Suspense>

      <Suspense fallback={<UsersSkeleton />}>
        <UsersAsync />
      </Suspense>

      <Suspense fallback={<MetricsSkeleton />}>
        <MetricsAsync />
      </Suspense>
    </div>
  )
}

async function ProjectsAsync() {
  const projects = await fetchProjects()
  return <ProjectList projects={projects} />
}

async function UsersAsync() {
  const users = await fetchUsers()
  return <UserList users={users} />
}

async function MetricsAsync() {
  const metrics = await fetchMetrics()
  return <MetricsChart data={metrics} />
}
```

---

## Sequential Data Fetching

Fetch data that depends on previous fetches.

### Example 16: Sequential Server Component Fetches

```typescript
// app/user/[id]/page.tsx

export default async function UserProfilePage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  // Fetch 1: Get user
  const user = await fetch(`https://api.example.com/users/${id}`)
    .then(r => r.json())

  // Fetch 2: Get user's organization (depends on user)
  const org = await fetch(`https://api.example.com/orgs/${user.orgId}`)
    .then(r => r.json())

  // Fetch 3: Get org's projects (depends on org)
  const projects = await fetch(`https://api.example.com/orgs/${org.id}/projects`)
    .then(r => r.json())

  return (
    <div>
      <UserProfile user={user} />
      <Organization org={org} />
      <ProjectList projects={projects} />
    </div>
  )
}
```

### Example 17: Sequential Database Queries

```typescript
// app/project/[id]/insights/page.tsx
import { db } from '@/lib/db'

export default async function ProjectInsightsPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  // Step 1: Get project
  const project = await db.project.findUniqueOrThrow({
    where: { id },
  })

  // Step 2: Get related data based on project
  const [contributors, commits, issues] = await Promise.all([
    db.contributor.findMany({ where: { projectId: project.id } }),
    db.commit.count({ where: { projectId: project.id } }),
    db.issue.count({ where: { projectId: project.id } }),
  ])

  return (
    <ProjectInsights
      project={project}
      contributors={contributors}
      stats={{ commits, issues }}
    />
  )
}
```

---

## Streaming Data

Stream data as it becomes available.

### Example 18: Async Server Component with Suspense

```typescript
// app/feed/page.tsx
import { Suspense } from 'react'

export default function FeedPage() {
  return (
    <div className="feed">
      <h1>Feed</h1>

      {/* Fast content loads immediately */}
      <Suspense fallback={<HeaderSkeleton />}>
        <HeaderAsync />
      </Suspense>

      {/* Slow content streams in when ready */}
      <Suspense fallback={<PostsSkeleton />}>
        <PostsAsync />
      </Suspense>
    </div>
  )
}

async function HeaderAsync() {
  const user = await fetchUser() // Fast
  return <Header user={user} />
}

async function PostsAsync() {
  const posts = await fetchPosts() // Slow
  return <PostList posts={posts} />
}
```

### Example 19: Streaming with Loading States

```typescript
// app/dashboard/analytics/page.tsx
import { Suspense } from 'react'

export default function AnalyticsPage() {
  return (
    <div className="analytics">
      {/* Static header - renders immediately */}
      <h1>Analytics Dashboard</h1>

      {/* Each section streams independently */}
      <div className="grid">
        <Suspense fallback={<ChartSkeleton />}>
          <RevenueChart />
        </Suspense>

        <Suspense fallback={<ChartSkeleton />}>
          <UsersChart />
        </Suspense>

        <Suspense fallback={<TableSkeleton />}>
          <RecentTransactions />
        </Suspense>
      </div>
    </div>
  )
}

async function RevenueChart() {
  const data = await fetchRevenueData() // 500ms
  return <Chart data={data} />
}

async function UsersChart() {
  const data = await fetchUsersData() // 1000ms
  return <Chart data={data} />
}

async function RecentTransactions() {
  const txns = await fetchTransactions() // 2000ms
  return <Table rows={txns} />
}
```

### Example 20: Nested Suspense Boundaries

```typescript
// app/project/[id]/page.tsx
import { Suspense } from 'react'

export default function ProjectPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  return (
    <div>
      <Suspense fallback={<ProjectHeaderSkeleton />}>
        <ProjectHeader params={params} />
      </Suspense>

      <Suspense fallback={<ProjectDetailsSkeleton />}>
        <ProjectDetails params={params}>
          {/* Nested Suspense for even finer control */}
          <Suspense fallback={<ActivitySkeleton />}>
            <RecentActivity params={params} />
          </Suspense>
        </ProjectDetails>
      </Suspense>
    </div>
  )
}
```

---

## Server-Sent Events

Real-time data streaming for Quetrex voice interface.

### Example 21: SSE Route Handler

```typescript
// app/api/stream/route.ts

export async function GET(request: Request) {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      try {
        // Send initial connection message
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ type: 'connected' })}\n\n`)
        )

        // Stream updates
        for (let i = 0; i < 10; i++) {
          const message = {
            type: 'update',
            data: { count: i, timestamp: Date.now() },
          }
          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify(message)}\n\n`)
          )
          await new Promise(resolve => setTimeout(resolve, 1000))
        }

        // Send completion
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ type: 'done' })}\n\n`)
        )
        controller.close()
      } catch (error) {
        controller.error(error)
      }
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
}
```

### Example 22: SSE Client Component

```typescript
// components/LiveUpdates.tsx
'use client'

import { useEffect, useState } from 'react'

export function LiveUpdates() {
  const [updates, setUpdates] = useState<any[]>([])
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting')

  useEffect(() => {
    const eventSource = new EventSource('/api/stream')

    eventSource.onopen = () => {
      setStatus('connected')
    }

    eventSource.onmessage = (event) => {
      const message = JSON.parse(event.data)

      if (message.type === 'update') {
        setUpdates(prev => [...prev, message.data])
      } else if (message.type === 'done') {
        eventSource.close()
        setStatus('disconnected')
      }
    }

    eventSource.onerror = () => {
      setStatus('disconnected')
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [])

  return (
    <div>
      <p>Status: {status}</p>
      <ul>
        {updates.map((update, i) => (
          <li key={i}>{JSON.stringify(update)}</li>
        ))}
      </ul>
    </div>
  )
}
```

### Example 23: OpenAI Streaming Response

```typescript
// app/api/ai/stream/route.ts
import { OpenAI } from 'openai'

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })

export async function POST(request: Request) {
  const { prompt } = await request.json()

  const stream = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: prompt }],
    stream: true,
  })

  const encoder = new TextEncoder()

  const readableStream = new ReadableStream({
    async start(controller) {
      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content || ''
        if (content) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ content })}\n\n`))
        }
      }
      controller.close()
    },
  })

  return new Response(readableStream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
    },
  })
}
```

---

## Data Mutations

Mutate data with Server Actions and API routes.

### Example 24: Basic Server Action

```typescript
// app/actions.ts
'use server'

import { db } from '@/lib/db'
import { revalidatePath } from 'next/cache'

export async function createProject(formData: FormData) {
  const name = formData.get('name') as string
  const description = formData.get('description') as string

  const project = await db.project.create({
    data: { name, description },
  })

  revalidatePath('/projects')
  return { success: true, project }
}
```

### Example 25: Server Action with Validation

```typescript
// app/actions.ts
'use server'

import { z } from 'zod'
import { db } from '@/lib/db'

const createProjectSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
})

export async function createProject(formData: FormData) {
  // Validate input
  const validated = createProjectSchema.parse({
    name: formData.get('name'),
    description: formData.get('description'),
  })

  // Create project
  const project = await db.project.create({
    data: validated,
  })

  revalidatePath('/projects')
  return { success: true, project }
}
```

### Example 26: Mutation API Route

```typescript
// app/api/projects/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { db } from '@/lib/db'

const createProjectSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional(),
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validate
    const validated = createProjectSchema.parse(body)

    // Create
    const project = await db.project.create({
      data: validated,
    })

    return NextResponse.json(project, { status: 201 })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: error.errors },
        { status: 400 }
      )
    }
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

---

## Optimistic Updates

Update UI immediately before server confirmation.

### Example 27: useOptimistic Hook

```typescript
// components/TodoList.tsx
'use client'

import { useOptimistic } from 'react'
import { deleteTodo } from '@/app/actions'

interface Todo {
  id: string
  text: string
}

export function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, deletedId: string) => state.filter(t => t.id !== deletedId)
  )

  const handleDelete = async (id: string) => {
    // Update UI immediately
    addOptimisticTodo(id)

    // Send to server
    await deleteTodo(id)
  }

  return (
    <ul>
      {optimisticTodos.map(todo => (
        <li key={todo.id}>
          {todo.text}
          <button onClick={() => handleDelete(todo.id)}>Delete</button>
        </li>
      ))}
    </ul>
  )
}
```

### Example 28: React Query Optimistic Update

```typescript
// components/ProjectCard.tsx
'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'

export function ProjectCard({ project }: { project: Project }) {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: async (starred: boolean) => {
      const res = await fetch(`/api/projects/${project.id}/star`, {
        method: 'PATCH',
        body: JSON.stringify({ starred }),
      })
      return res.json()
    },
    onMutate: async (starred) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['projects'] })

      // Snapshot previous value
      const previous = queryClient.getQueryData(['projects'])

      // Optimistically update
      queryClient.setQueryData(['projects'], (old: any) =>
        old.map((p: any) =>
          p.id === project.id ? { ...p, starred } : p
        )
      )

      return { previous }
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.previous) {
        queryClient.setQueryData(['projects'], context.previous)
      }
    },
    onSettled: () => {
      // Refetch after mutation
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
  })

  return (
    <div>
      <h3>{project.name}</h3>
      <button onClick={() => mutation.mutate(!project.starred)}>
        {project.starred ? '⭐' : '☆'}
      </button>
    </div>
  )
}
```

---

## Form Handling

Handle forms with Server Actions and hooks.

### Example 29: Basic Form with Server Action

```typescript
// app/projects/new/page.tsx
import { createProject } from '@/app/actions'

export default function NewProjectPage() {
  return (
    <form action={createProject}>
      <input name="name" placeholder="Project name" required />
      <textarea name="description" placeholder="Description" />
      <button type="submit">Create Project</button>
    </form>
  )
}
```

### Example 30: Form with useFormStatus

```typescript
// components/SubmitButton.tsx
'use client'

import { useFormStatus } from 'react-dom'

export function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Creating...' : 'Create Project'}
    </button>
  )
}

// app/projects/new/page.tsx
import { createProject } from '@/app/actions'
import { SubmitButton } from '@/components/SubmitButton'

export default function NewProjectPage() {
  return (
    <form action={createProject}>
      <input name="name" required />
      <SubmitButton />
    </form>
  )
}
```

### Example 31: Form with useActionState

```typescript
// components/CreateProjectForm.tsx
'use client'

import { useActionState } from 'react'
import { createProject } from '@/app/actions'

export function CreateProjectForm() {
  const [state, formAction] = useActionState(createProject, {
    error: null,
    success: false,
  })

  return (
    <form action={formAction}>
      <input name="name" required />
      <textarea name="description" />

      {state.error && (
        <div className="error">{state.error}</div>
      )}

      {state.success && (
        <div className="success">Project created!</div>
      )}

      <button type="submit">Create</button>
    </form>
  )
}
```

---

## Request Deduplication

Next.js automatically deduplicates fetch requests.

### Example 32: Automatic Deduplication

```typescript
// app/project/[id]/page.tsx

async function getProject(id: string) {
  // This fetch is deduplicated across components
  return fetch(`https://api.example.com/projects/${id}`, {
    cache: 'force-cache',
  }).then(r => r.json())
}

export default async function ProjectPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const project = await getProject(id)

  return (
    <div>
      <ProjectHeader project={project} />
      <ProjectDetails project={project} />
      <ProjectMetrics project={project} />
    </div>
  )
}

async function ProjectHeader({ project }: { project: Project }) {
  // Same fetch - deduplicated (only one request)
  const data = await getProject(project.id)
  return <h1>{data.name}</h1>
}

async function ProjectDetails({ project }: { project: Project }) {
  // Same fetch - deduplicated
  const data = await getProject(project.id)
  return <div>{data.description}</div>
}
```

### Example 33: React Cache for Functions

```typescript
// lib/data.ts
import { cache } from 'react'

export const getProject = cache(async (id: string) => {
  console.log('Fetching project:', id)

  const project = await db.project.findUnique({
    where: { id },
    include: {
      owner: true,
      collaborators: true,
    },
  })

  return project
})

// app/project/[id]/page.tsx
// Multiple calls to getProject(id) are deduplicated
```

---

## Preloading Data

Preload data to avoid waterfalls.

### Example 34: Preload Pattern

```typescript
// lib/data.ts
import { cache } from 'react'

export const getProject = cache(async (id: string) => {
  return db.project.findUnique({ where: { id } })
})

export const preloadProject = (id: string) => {
  void getProject(id) // Trigger fetch without awaiting
}

// app/project/[id]/page.tsx
import { getProject, preloadProject } from '@/lib/data'

export default async function ProjectPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  // Preload related data
  preloadProject(id)

  const project = await getProject(id)

  return <ProjectView project={project} />
}
```

### Example 35: Link Prefetch

```typescript
// components/ProjectLink.tsx
import Link from 'next/link'

export function ProjectLink({ id }: { id: string }) {
  return (
    <Link
      href={`/projects/${id}`}
      prefetch={true} // Prefetch on hover (default)
    >
      View Project
    </Link>
  )
}
```

---

## Summary

**Server Component Patterns:**
- Direct database access
- Fetch with cache control
- Parallel fetching with Promise.all
- Sequential fetching when dependent

**Client Component Patterns:**
- useEffect for simple fetches
- React Query for advanced caching
- SWR for revalidation
- Infinite queries for pagination

**Streaming:**
- Suspense boundaries for progressive loading
- SSE for real-time updates
- OpenAI streaming responses

**Mutations:**
- Server Actions for forms
- API routes for programmatic mutations
- useOptimistic for instant UI updates

**Best Practices:**
1. Prefer Server Components for data fetching
2. Use Client Components only when needed
3. Implement proper loading states
4. Handle errors gracefully
5. Use Suspense for streaming
6. Cache appropriately
7. Deduplicate requests automatically

**Official Docs:**
- Data Fetching: https://nextjs.org/docs/app/building-your-application/data-fetching
- Server Actions: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations
- Caching: https://nextjs.org/docs/app/building-your-application/caching
