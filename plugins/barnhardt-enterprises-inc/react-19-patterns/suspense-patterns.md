# Suspense Patterns - Complete Guide

## Table of Contents

- [What is Suspense?](#what-is-suspense)
- [Basic Suspense Usage](#basic-suspense-usage)
- [Suspense Boundaries](#suspense-boundaries)
- [Fallback UI Design](#fallback-ui-design)
- [Nested Suspense](#nested-suspense)
- [Suspense with Server Components](#suspense-with-server-components)
- [Suspense with Client Components](#suspense-with-client-components)
- [Error Boundaries with Suspense](#error-boundaries-with-suspense)
- [Streaming with Suspense](#streaming-with-suspense)
- [Parallel Data Loading](#parallel-data-loading)
- [Waterfall Prevention](#waterfall-prevention)
- [Best Practices](#best-practices)

## What is Suspense?

Suspense lets components "wait" for something before rendering. It:
- Shows fallback UI while loading
- Enables progressive rendering (streaming)
- Prevents waterfalls with parallel loading
- Works seamlessly with Server Components
- Improves perceived performance

## Basic Suspense Usage

### Simple Example

```typescript
import { Suspense } from 'react'

export default function Page() {
  return (
    <div>
      <h1>My Page</h1>
      <Suspense fallback={<div>Loading...</div>}>
        <AsyncComponent />
      </Suspense>
    </div>
  )
}

async function AsyncComponent() {
  const data = await fetchData()
  return <div>{data}</div>
}
```

### Multiple Suspense Boundaries

```typescript
export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>

      <Suspense fallback={<Skeleton />}>
        <UserProfile />
      </Suspense>

      <Suspense fallback={<Skeleton />}>
        <ProjectsList />
      </Suspense>

      <Suspense fallback={<Skeleton />}>
        <ActivityFeed />
      </Suspense>
    </div>
  )
}
```

## Suspense Boundaries

### Where to Place Boundaries

✅ **DO place boundaries:**
- Around async components
- At route level for page content
- Around slow components
- Where you want loading states

❌ **DON'T place boundaries:**
- Around every single component
- Inside components that need to render together
- Too granular (creates visual jank)

### Example: Strategic Placement

```typescript
export default function ProjectPage({ params }: { params: { id: string } }) {
  return (
    <div>
      {/* Navbar renders immediately */}
      <Navbar />

      {/* Main content suspended */}
      <Suspense fallback={<ProjectSkeleton />}>
        <ProjectDetails id={params.id} />
      </Suspense>

      {/* Sidebar renders in parallel */}
      <Suspense fallback={<SidebarSkeleton />}>
        <ProjectSidebar id={params.id} />
      </Suspense>
    </div>
  )
}
```

### Boundary Granularity

```typescript
// ❌ TOO GRANULAR: Too many small boundaries
function BadDashboard() {
  return (
    <div>
      <Suspense fallback={<Spinner />}>
        <Title />
      </Suspense>
      <Suspense fallback={<Spinner />}>
        <Subtitle />
      </Suspense>
      <Suspense fallback={<Spinner />}>
        <Description />
      </Suspense>
    </div>
  )
}

// ✅ GOOD: Single boundary for related content
function GoodDashboard() {
  return (
    <div>
      <Suspense fallback={<HeaderSkeleton />}>
        <Header />
      </Suspense>
    </div>
  )
}

async function Header() {
  const data = await fetchHeaderData()
  return (
    <div>
      <Title data={data} />
      <Subtitle data={data} />
      <Description data={data} />
    </div>
  )
}
```

## Fallback UI Design

### Loading Skeletons

```typescript
function ProjectSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
      <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
    </div>
  )
}

function ProjectCard() {
  return (
    <Suspense fallback={<ProjectSkeleton />}>
      <ProjectContent />
    </Suspense>
  )
}
```

### Spinner Pattern

```typescript
function Spinner() {
  return (
    <div className="flex items-center justify-center p-4">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>
  )
}

function Component() {
  return (
    <Suspense fallback={<Spinner />}>
      <AsyncContent />
    </Suspense>
  )
}
```

### Placeholder Content

```typescript
function TableSkeleton() {
  return (
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Status</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        {[...Array(5)].map((_, i) => (
          <tr key={i}>
            <td><div className="h-4 bg-gray-200 rounded w-24"></div></td>
            <td><div className="h-4 bg-gray-200 rounded w-16"></div></td>
            <td><div className="h-4 bg-gray-200 rounded w-20"></div></td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
```

## Nested Suspense

### Independent Loading States

```typescript
export default function Page() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* Top section loads independently */}
      <Suspense fallback={<StatsSkeleton />}>
        <StatsPanel />
      </Suspense>

      {/* Bottom section loads independently */}
      <Suspense fallback={<ContentSkeleton />}>
        <MainContent />

        {/* Nested: Details load after MainContent */}
        <Suspense fallback={<DetailsSkeleton />}>
          <Details />
        </Suspense>
      </Suspense>
    </div>
  )
}
```

### Progressive Disclosure

```typescript
function ProjectDetails({ id }: { id: string }) {
  return (
    <div>
      {/* Show basic info immediately */}
      <Suspense fallback={<BasicInfoSkeleton />}>
        <BasicInfo id={id} />
      </Suspense>

      {/* Load detailed data progressively */}
      <Suspense fallback={<ChartsSkeleton />}>
        <Charts id={id} />
      </Suspense>

      {/* Load activity feed last */}
      <Suspense fallback={<ActivitySkeleton />}>
        <ActivityFeed id={id} />
      </Suspense>
    </div>
  )
}
```

## Suspense with Server Components

### Async Server Components

```typescript
// ✅ Server Component - naturally async
async function Projects() {
  const projects = await db.project.findMany()

  return (
    <ul>
      {projects.map((project) => (
        <li key={project.id}>{project.name}</li>
      ))}
    </ul>
  )
}

// Page wraps with Suspense
export default function ProjectsPage() {
  return (
    <Suspense fallback={<ProjectsSkeleton />}>
      <Projects />
    </Suspense>
  )
}
```

### Parallel Fetching in Server Components

```typescript
export default function Dashboard() {
  return (
    <div>
      {/* These load in parallel */}
      <Suspense fallback={<UserSkeleton />}>
        <UserInfo />
      </Suspense>

      <Suspense fallback={<ProjectsSkeleton />}>
        <ProjectsList />
      </Suspense>

      <Suspense fallback={<StatsSkeleton />}>
        <Stats />
      </Suspense>
    </div>
  )
}

// Each component fetches independently
async function UserInfo() {
  const user = await db.user.findFirst()
  return <div>{user.name}</div>
}

async function ProjectsList() {
  const projects = await db.project.findMany()
  return <ul>{/* ... */}</ul>
}

async function Stats() {
  const stats = await db.stats.aggregate()
  return <div>{/* ... */}</div>
}
```

### Streaming Server-Rendered Content

```typescript
// app/projects/[id]/page.tsx
export default function ProjectPage({ params }: { params: { id: string } }) {
  return (
    <div>
      {/* Instant shell */}
      <ProjectHeader id={params.id} />

      {/* Stream content as it loads */}
      <Suspense fallback={<ContentSkeleton />}>
        <ProjectContent id={params.id} />
      </Suspense>

      {/* Stream comments independently */}
      <Suspense fallback={<CommentsSkeleton />}>
        <Comments projectId={params.id} />
      </Suspense>
    </div>
  )
}
```

## Suspense with Client Components

### Using `use()` Hook (React 19)

```typescript
'use client'

import { use } from 'react'

interface User {
  id: string
  name: string
}

function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  // use() unwraps promise, suspends until ready
  const user = use(userPromise)

  return <div>{user.name}</div>
}

export default function Page() {
  const userPromise = fetchUser('1')

  return (
    <Suspense fallback={<div>Loading user...</div>}>
      <UserProfile userPromise={userPromise} />
    </Suspense>
  )
}
```

### Lazy Loading Components

```typescript
'use client'

import { lazy, Suspense } from 'react'

// Lazy load heavy component
const HeavyChart = lazy(() => import('./HeavyChart'))

export function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<ChartSkeleton />}>
        <HeavyChart />
      </Suspense>
    </div>
  )
}
```

### Data Fetching in Client Components

```typescript
'use client'

import { Suspense } from 'react'
import { use } from 'react'

function fetchProjects(): Promise<Project[]> {
  return fetch('/api/projects').then((r) => r.json())
}

function ProjectList() {
  // use() suspends until promise resolves
  const projects = use(fetchProjects())

  return (
    <ul>
      {projects.map((p) => (
        <li key={p.id}>{p.name}</li>
      ))}
    </ul>
  )
}

export function ProjectsPage() {
  return (
    <Suspense fallback={<ProjectsSkeleton />}>
      <ProjectList />
    </Suspense>
  )
}
```

## Error Boundaries with Suspense

### Basic Error Boundary

```typescript
'use client'

import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('ErrorBoundary caught:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div>Something went wrong</div>
    }

    return this.props.children
  }
}

export default ErrorBoundary
```

### Combined with Suspense

```typescript
export default function Page() {
  return (
    <ErrorBoundary fallback={<ErrorMessage />}>
      <Suspense fallback={<LoadingSkeleton />}>
        <AsyncContent />
      </Suspense>
    </ErrorBoundary>
  )
}

function ErrorMessage() {
  return (
    <div className="error">
      <h2>Failed to load content</h2>
      <button onClick={() => window.location.reload()}>Retry</button>
    </div>
  )
}
```

### Per-Component Error Handling

```typescript
export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* Projects section with error handling */}
      <ErrorBoundary fallback={<ProjectsError />}>
        <Suspense fallback={<ProjectsSkeleton />}>
          <ProjectsList />
        </Suspense>
      </ErrorBoundary>

      {/* Stats section with error handling */}
      <ErrorBoundary fallback={<StatsError />}>
        <Suspense fallback={<StatsSkeleton />}>
          <Stats />
        </Suspense>
      </ErrorBoundary>
    </div>
  )
}
```

### Next.js error.tsx

```typescript
// app/projects/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="error">
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

## Streaming with Suspense

### Progressive Page Load

```typescript
// app/dashboard/page.tsx
export default function DashboardPage() {
  return (
    <div>
      {/* Renders immediately */}
      <DashboardHeader />

      {/* Streams in order */}
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

### Streaming JSON Responses

```typescript
// app/api/stream/route.ts
export async function GET() {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      // Send data progressively
      controller.enqueue(encoder.encode('data: {"count": 1}\n\n'))
      await delay(1000)
      controller.enqueue(encoder.encode('data: {"count": 2}\n\n'))
      await delay(1000)
      controller.enqueue(encoder.encode('data: {"count": 3}\n\n'))
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

## Parallel Data Loading

### Anti-Pattern: Waterfall

```typescript
// ❌ BAD: Sequential loading (waterfall)
async function BadDashboard() {
  const user = await fetchUser() // Wait
  const projects = await fetchProjects() // Then wait
  const stats = await fetchStats() // Then wait

  return (
    <div>
      <UserInfo user={user} />
      <ProjectsList projects={projects} />
      <Stats stats={stats} />
    </div>
  )
}
```

### Pattern: Parallel Loading

```typescript
// ✅ GOOD: Parallel loading with Suspense
export default function GoodDashboard() {
  return (
    <div>
      <Suspense fallback={<UserSkeleton />}>
        <UserInfo />
      </Suspense>

      <Suspense fallback={<ProjectsSkeleton />}>
        <ProjectsList />
      </Suspense>

      <Suspense fallback={<StatsSkeleton />}>
        <Stats />
      </Suspense>
    </div>
  )
}

// Each component fetches independently (parallel)
async function UserInfo() {
  const user = await fetchUser()
  return <div>{user.name}</div>
}

async function ProjectsList() {
  const projects = await fetchProjects()
  return <ul>{/* ... */}</ul>
}

async function Stats() {
  const stats = await fetchStats()
  return <div>{/* ... */}</div>
}
```

### Promise.all for Related Data

```typescript
async function ProjectDetails({ id }: { id: string }) {
  // Fetch related data in parallel
  const [project, comments, activity] = await Promise.all([
    fetchProject(id),
    fetchComments(id),
    fetchActivity(id),
  ])

  return (
    <div>
      <ProjectInfo project={project} />
      <CommentsList comments={comments} />
      <ActivityFeed activity={activity} />
    </div>
  )
}
```

## Waterfall Prevention

### Problem: Nested Async Components

```typescript
// ❌ BAD: Creates waterfall
async function ParentComponent() {
  const data = await fetchParentData() // Wait 1 second
  return (
    <div>
      <ChildComponent parentData={data} />
    </div>
  )
}

async function ChildComponent({ parentData }: Props) {
  const childData = await fetchChildData(parentData) // Wait another 1 second
  return <div>{childData}</div>
}
// Total: 2 seconds sequential
```

### Solution: Separate Suspense Boundaries

```typescript
// ✅ GOOD: Parallel loading
export default function Page() {
  return (
    <div>
      <Suspense fallback={<ParentSkeleton />}>
        <ParentComponent />
      </Suspense>

      <Suspense fallback={<ChildSkeleton />}>
        <ChildComponent />
      </Suspense>
    </div>
  )
}

async function ParentComponent() {
  const data = await fetchParentData() // Loads in parallel
  return <div>{data}</div>
}

async function ChildComponent() {
  const data = await fetchChildData() // Loads in parallel
  return <div>{data}</div>
}
// Total: 1 second parallel
```

### Solution: Preload Data

```typescript
export default function Page() {
  // Start loading immediately
  const parentPromise = fetchParentData()
  const childPromise = fetchChildData()

  return (
    <div>
      <Suspense fallback={<ParentSkeleton />}>
        <ParentComponent dataPromise={parentPromise} />
      </Suspense>

      <Suspense fallback={<ChildSkeleton />}>
        <ChildComponent dataPromise={childPromise} />
      </Suspense>
    </div>
  )
}

function ParentComponent({ dataPromise }: Props) {
  const data = use(dataPromise) // Already loading!
  return <div>{data}</div>
}
```

## Best Practices

### 1. Strategic Boundary Placement

```typescript
// ✅ GOOD: One boundary per major section
export default function Page() {
  return (
    <div>
      <Suspense fallback={<HeaderSkeleton />}>
        <Header />
      </Suspense>

      <Suspense fallback={<ContentSkeleton />}>
        <MainContent />
      </Suspense>

      <Suspense fallback={<SidebarSkeleton />}>
        <Sidebar />
      </Suspense>
    </div>
  )
}
```

### 2. Match Loading States to Content

```typescript
// ✅ GOOD: Skeleton matches final layout
function ProductCardSkeleton() {
  return (
    <div className="product-card">
      <div className="h-48 bg-gray-200 rounded"></div> {/* Image */}
      <div className="h-6 bg-gray-200 rounded w-3/4 mt-2"></div> {/* Title */}
      <div className="h-4 bg-gray-200 rounded w-1/2 mt-1"></div> {/* Price */}
    </div>
  )
}
```

### 3. Avoid Too Many Boundaries

```typescript
// ❌ BAD: Too many small boundaries
function BadList({ items }: Props) {
  return (
    <ul>
      {items.map((item) => (
        <Suspense key={item.id} fallback={<Spinner />}>
          <ListItem item={item} />
        </Suspense>
      ))}
    </ul>
  )
}

// ✅ GOOD: One boundary for entire list
function GoodList({ items }: Props) {
  return (
    <Suspense fallback={<ListSkeleton />}>
      <ListContent items={items} />
    </Suspense>
  )
}
```

### 4. Error Boundaries for Resilience

```typescript
// ✅ GOOD: Error boundary + Suspense
export default function ResilientPage() {
  return (
    <ErrorBoundary fallback={<ErrorUI />}>
      <Suspense fallback={<LoadingUI />}>
        <AsyncContent />
      </Suspense>
    </ErrorBoundary>
  )
}
```

### 5. Server Components for Data Fetching

```typescript
// ✅ GOOD: Server Component with Suspense
export default function Page() {
  return (
    <Suspense fallback={<Skeleton />}>
      <ServerDataComponent />
    </Suspense>
  )
}

async function ServerDataComponent() {
  // Direct database access
  const data = await db.query()
  return <div>{data}</div>
}
```

---

**Next**: Read [streaming-patterns.md](./streaming-patterns.md) for progressive rendering patterns.
