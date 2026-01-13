# Streaming Patterns - Progressive Rendering Guide

## Table of Contents

- [What is Streaming?](#what-is-streaming)
- [Streaming in Next.js](#streaming-in-nextjs)
- [Progressive Page Loading](#progressive-page-loading)
- [Streaming Server-Rendered Content](#streaming-server-rendered-content)
- [Streaming API Responses](#streaming-api-responses)
- [Streaming with Suspense](#streaming-with-suspense)
- [Streaming Best Practices](#streaming-best-practices)

## What is Streaming?

Streaming allows you to:
- Send HTML to browser progressively
- Show content as it becomes available
- Improve perceived performance
- Keep users engaged with instant feedback
- Reduce Time to First Byte (TTFB)

### Traditional Rendering vs Streaming

```
Traditional (All-or-Nothing):
Server: [████████████████████] (2s)
Client: [                    ] ⟶ [████████████████████]
User sees: Nothing... Nothing... BOOM! Full page

Streaming (Progressive):
Server: [██              ] (0.2s) → [████          ] (0.8s) → [████████      ] (1.5s)
Client: [██              ] ⟶ [████          ] ⟶ [████████      ]
User sees: Shell → Header → Content progressively
```

## Streaming in Next.js

### Automatic Streaming with App Router

Next.js 13+ automatically streams Server Components:

```typescript
// app/page.tsx - Automatically streamed!
export default async function Page() {
  const data = await fetchData()

  return (
    <div>
      <h1>Page Title</h1>
      <Content data={data} />
    </div>
  )
}
```

### Manual Streaming with Suspense

```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react'

export default function DashboardPage() {
  return (
    <div>
      {/* Shell renders immediately */}
      <DashboardHeader />

      {/* Content streams as available */}
      <Suspense fallback={<StatsSkeleton />}>
        <StatsPanel />
      </Suspense>

      <Suspense fallback={<ProjectsSkeleton />}>
        <ProjectsList />
      </Suspense>

      <Suspense fallback={<ActivitySkeleton />}>
        <ActivityFeed />
      </Suspense>
    </div>
  )
}
```

## Progressive Page Loading

### Pattern 1: Shell → Content

```typescript
// app/projects/page.tsx
export default function ProjectsPage() {
  return (
    <div>
      {/* Instant shell */}
      <header>
        <h1>Projects</h1>
        <nav>{/* Navigation */}</nav>
      </header>

      {/* Progressive content */}
      <Suspense fallback={<PageSkeleton />}>
        <ProjectsContent />
      </Suspense>
    </div>
  )
}

async function ProjectsContent() {
  const projects = await fetchProjects()

  return (
    <div>
      {projects.map((project) => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  )
}
```

### Pattern 2: Above-the-Fold First

```typescript
export default function Page() {
  return (
    <div>
      {/* Above-the-fold: Render immediately */}
      <Hero />
      <CallToAction />

      {/* Below-the-fold: Stream progressively */}
      <Suspense fallback={<FeaturesSkeleton />}>
        <Features />
      </Suspense>

      <Suspense fallback={<TestimonialsSkeleton />}>
        <Testimonials />
      </Suspense>

      <Suspense fallback={<FooterSkeleton />}>
        <Footer />
      </Suspense>
    </div>
  )
}
```

### Pattern 3: Priority-Based Streaming

```typescript
export default function Dashboard() {
  return (
    <div>
      {/* High priority: Show first */}
      <Suspense fallback={<UserSkeleton />} priority="high">
        <UserInfo />
      </Suspense>

      {/* Medium priority: Show next */}
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />
      </Suspense>

      {/* Low priority: Show last */}
      <Suspense fallback={<RecommendationsSkeleton />} priority="low">
        <Recommendations />
      </Suspense>
    </div>
  )
}
```

## Streaming Server-Rendered Content

### Parallel Data Fetching

```typescript
// app/project/[id]/page.tsx
export default function ProjectPage({ params }: { params: { id: string } }) {
  return (
    <div>
      {/* These all load in parallel and stream independently */}
      <Suspense fallback={<ProjectHeaderSkeleton />}>
        <ProjectHeader id={params.id} />
      </Suspense>

      <Suspense fallback={<TasksSkeleton />}>
        <TasksList id={params.id} />
      </Suspense>

      <Suspense fallback={<CommentsSkeleton />}>
        <Comments id={params.id} />
      </Suspense>

      <Suspense fallback={<ActivitySkeleton />}>
        <Activity id={params.id} />
      </Suspense>
    </div>
  )
}

// Each component fetches independently
async function ProjectHeader({ id }: { id: string }) {
  const project = await db.project.findUnique({ where: { id } })
  return <header>{project.name}</header>
}

async function TasksList({ id }: { id: string }) {
  const tasks = await db.task.findMany({ where: { projectId: id } })
  return <ul>{/* tasks */}</ul>
}
```

### Sequential Dependencies

```typescript
export default function Page() {
  return (
    <div>
      {/* Parent streams first */}
      <Suspense fallback={<ParentSkeleton />}>
        <ParentContent>
          {/* Child waits for parent, then streams */}
          <Suspense fallback={<ChildSkeleton />}>
            <ChildContent />
          </Suspense>
        </ParentContent>
      </Suspense>
    </div>
  )
}

async function ParentContent({ children }: { children: React.ReactNode }) {
  const parentData = await fetchParentData()

  return (
    <div>
      <h1>{parentData.title}</h1>
      {children}
    </div>
  )
}

async function ChildContent() {
  const childData = await fetchChildData()
  return <div>{childData}</div>
}
```

## Streaming API Responses

### Server-Sent Events (SSE)

```typescript
// app/api/stream/route.ts
export async function GET() {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      // Send data progressively
      for (let i = 0; i < 10; i++) {
        const data = { count: i, timestamp: Date.now() }
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify(data)}\n\n`)
        )
        await new Promise((resolve) => setTimeout(resolve, 1000))
      }

      controller.close()
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    },
  })
}
```

```typescript
// Client-side consumption
'use client'

import { useEffect, useState } from 'react'

export function StreamingData() {
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    const eventSource = new EventSource('/api/stream')

    eventSource.onmessage = (event) => {
      const newData = JSON.parse(event.data)
      setData((prev) => [...prev, newData])
    }

    return () => eventSource.close()
  }, [])

  return (
    <ul>
      {data.map((item, i) => (
        <li key={i}>
          Count: {item.count}, Time: {item.timestamp}
        </li>
      ))}
    </ul>
  )
}
```

### Streaming JSON

```typescript
// app/api/projects/stream/route.ts
import { db } from '@/lib/db'

export async function GET() {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      controller.enqueue(encoder.encode('['))

      const projects = await db.project.findMany()

      projects.forEach((project, i) => {
        const data = JSON.stringify(project)
        const chunk = i === 0 ? data : `,${data}`
        controller.enqueue(encoder.encode(chunk))
      })

      controller.enqueue(encoder.encode(']'))
      controller.close()
    },
  })

  return new Response(stream, {
    headers: { 'Content-Type': 'application/json' },
  })
}
```

### Chunked Transfer

```typescript
// app/api/large-data/route.ts
export async function GET() {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      const chunkSize = 1000

      for (let i = 0; i < 10000; i += chunkSize) {
        const chunk = await fetchDataChunk(i, chunkSize)
        controller.enqueue(encoder.encode(JSON.stringify(chunk)))

        // Allow browser to process
        await new Promise((resolve) => setTimeout(resolve, 100))
      }

      controller.close()
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'application/json',
      'Transfer-Encoding': 'chunked',
    },
  })
}
```

## Streaming with Suspense

### Nested Boundaries

```typescript
export default function Page() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* Outer boundary: Page layout */}
      <Suspense fallback={<PageSkeleton />}>
        <PageLayout>
          {/* Inner boundary: Section content */}
          <Suspense fallback={<SectionSkeleton />}>
            <Section1 />
          </Suspense>

          <Suspense fallback={<SectionSkeleton />}>
            <Section2 />
          </Suspense>
        </PageLayout>
      </Suspense>
    </div>
  )
}
```

### Conditional Streaming

```typescript
interface PageProps {
  searchParams: { fast?: string }
}

export default function Page({ searchParams }: PageProps) {
  const useFastMode = searchParams.fast === 'true'

  return (
    <div>
      <h1>Content</h1>

      {useFastMode ? (
        // Fast mode: Show cached data immediately
        <CachedContent />
      ) : (
        // Normal mode: Stream fresh data
        <Suspense fallback={<ContentSkeleton />}>
          <FreshContent />
        </Suspense>
      )}
    </div>
  )
}
```

### Streaming with Loading States

```typescript
// app/projects/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
      <div className="grid grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-32 bg-gray-200 rounded"></div>
        ))}
      </div>
    </div>
  )
}

// app/projects/page.tsx
export default async function ProjectsPage() {
  const projects = await fetchProjects()

  return (
    <div>
      <h1>Projects</h1>
      <ProjectGrid projects={projects} />
    </div>
  )
}
```

## Streaming Best Practices

### 1. Strategic Suspense Boundaries

```typescript
// ✅ GOOD: Boundary per major section
export default function Page() {
  return (
    <div>
      <Suspense fallback={<HeaderSkeleton />}>
        <Header />
      </Suspense>

      <Suspense fallback={<MainSkeleton />}>
        <MainContent />
      </Suspense>

      <Suspense fallback={<SidebarSkeleton />}>
        <Sidebar />
      </Suspense>
    </div>
  )
}

// ❌ BAD: Too many boundaries
export default function Page() {
  return (
    <div>
      <Suspense fallback={<Spinner />}>
        <Title />
      </Suspense>
      <Suspense fallback={<Spinner />}>
        <Subtitle />
      </Suspense>
      {/* Too granular! */}
    </div>
  )
}
```

### 2. Match Skeleton to Content

```typescript
// ✅ GOOD: Skeleton matches layout
function ProjectCardSkeleton() {
  return (
    <div className="border rounded-lg p-4">
      <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
      <div className="flex gap-2">
        <div className="h-8 bg-gray-200 rounded w-20"></div>
        <div className="h-8 bg-gray-200 rounded w-20"></div>
      </div>
    </div>
  )
}
```

### 3. Avoid Waterfall Loading

```typescript
// ❌ BAD: Sequential waterfall
async function BadComponent() {
  const user = await fetchUser() // Wait 1s
  const projects = await fetchProjects(user.id) // Wait 1s
  const tasks = await fetchTasks(projects[0].id) // Wait 1s
  // Total: 3 seconds
}

// ✅ GOOD: Parallel with independent boundaries
export default function GoodPage() {
  return (
    <div>
      <Suspense fallback={<UserSkeleton />}>
        <UserInfo />
      </Suspense>

      <Suspense fallback={<ProjectsSkeleton />}>
        <ProjectsList />
      </Suspense>

      <Suspense fallback={<TasksSkeleton />}>
        <TasksList />
      </Suspense>
    </div>
  )
}
// Total: 1 second (all parallel)
```

### 4. Cache Streamed Data

```typescript
// Cache with Next.js fetch
async function StreamedContent() {
  const data = await fetch('https://api.example.com/data', {
    next: { revalidate: 3600 }, // Cache for 1 hour
  })

  return <div>{JSON.stringify(data)}</div>
}

export default function Page() {
  return (
    <Suspense fallback={<Skeleton />}>
      <StreamedContent />
    </Suspense>
  )
}
```

### 5. Progressive Enhancement

```typescript
export default function Page() {
  return (
    <div>
      {/* Critical: Render immediately */}
      <CriticalContent />

      {/* Important: Stream next */}
      <Suspense fallback={<ImportantSkeleton />}>
        <ImportantContent />
      </Suspense>

      {/* Nice-to-have: Stream last */}
      <Suspense fallback={<OptionalSkeleton />}>
        <OptionalContent />
      </Suspense>
    </div>
  )
}
```

### 6. Error Boundaries

```typescript
import { ErrorBoundary } from './ErrorBoundary'

export default function Page() {
  return (
    <div>
      <ErrorBoundary fallback={<ErrorUI />}>
        <Suspense fallback={<Skeleton />}>
          <AsyncContent />
        </Suspense>
      </ErrorBoundary>
    </div>
  )
}
```

### 7. Metrics and Monitoring

```typescript
// Track streaming performance
async function MonitoredContent() {
  const start = Date.now()

  const data = await fetchData()

  const duration = Date.now() - start

  // Log metrics
  console.log(`Content loaded in ${duration}ms`)

  return <div>{data}</div>
}

export default function Page() {
  return (
    <Suspense fallback={<Skeleton />}>
      <MonitoredContent />
    </Suspense>
  )
}
```

---

**Next**: Read [migration-guide.md](./migration-guide.md) for React 18 → 19 migration.
