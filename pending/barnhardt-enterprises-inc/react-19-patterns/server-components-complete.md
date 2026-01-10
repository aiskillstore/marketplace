# Server Components - Complete Guide

## Table of Contents

- [Server Components Overview](#server-components-overview)
- [Basic Async Server Components](#basic-async-server-components)
- [Data Fetching Patterns](#data-fetching-patterns)
- [Database Queries](#database-queries)
- [API Calls](#api-calls)
- [Parallel Data Fetching](#parallel-data-fetching)
- [Sequential Data Fetching](#sequential-data-fetching)
- [Caching Strategies](#caching-strategies)
- [Revalidation Patterns](#revalidation-patterns)
- [Composition Patterns](#composition-patterns)
- [Props to Client Components](#props-to-client-components)
- [Children Pattern](#children-pattern)
- [Context Limitations](#context-limitations)

## Server Components Overview

Server Components execute **only on the server**:
- During build time (static generation)
- On each request (dynamic rendering)
- Never send JavaScript to client
- Can access backend resources directly

### Benefits

1. **Zero Client Bundle** - No JS shipped for Server Components
2. **Direct Data Access** - Query databases, read files
3. **Security** - Keep secrets on server
4. **SEO** - Fully rendered HTML
5. **Performance** - Heavy work on server

### Limitations

**Cannot use:**
- React hooks (useState, useEffect, etc.)
  - Exception: `use()` in React 19
- Event handlers (onClick, onChange, etc.)
- Browser APIs (window, localStorage, etc.)
- React Context (as provider or consumer)

**Can use:**
- `async`/`await` functions
- Node.js APIs (fs, path, crypto, etc.)
- Server-only libraries
- All environment variables
- Database clients

## Basic Async Server Components

### Simple Async Component

```typescript
// ✅ Server Component - async by default
export default async function ProjectsPage() {
  const projects = await fetchProjects()

  return (
    <div>
      <h1>Projects</h1>
      <ul>
        {projects.map((project) => (
          <li key={project.id}>{project.name}</li>
        ))}
      </ul>
    </div>
  )
}
```

### With TypeScript Types

```typescript
interface Project {
  id: string
  name: string
  description: string
  createdAt: Date
}

async function fetchProjects(): Promise<Project[]> {
  const response = await fetch('https://api.example.com/projects')
  return response.json()
}

export default async function ProjectsPage() {
  const projects: Project[] = await fetchProjects()

  return (
    <ul>
      {projects.map((project: Project) => (
        <li key={project.id}>
          <h2>{project.name}</h2>
          <p>{project.description}</p>
        </li>
      ))}
    </ul>
  )
}
```

### Error Handling

```typescript
export default async function ProjectsPage() {
  try {
    const projects = await fetchProjects()

    return (
      <ul>
        {projects.map((project) => (
          <li key={project.id}>{project.name}</li>
        ))}
      </ul>
    )
  } catch (error) {
    return (
      <div className="error">
        <h2>Failed to load projects</h2>
        <p>{error instanceof Error ? error.message : 'Unknown error'}</p>
      </div>
    )
  }
}
```

## Data Fetching Patterns

### Pattern 1: Direct Fetch

```typescript
async function fetchUser(id: string) {
  const response = await fetch(`https://api.example.com/users/${id}`, {
    next: { revalidate: 3600 }, // Cache for 1 hour
  })

  if (!response.ok) {
    throw new Error('Failed to fetch user')
  }

  return response.json()
}

export default async function UserProfile({ params }: { params: { id: string } }) {
  const user = await fetchUser(params.id)

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  )
}
```

### Pattern 2: With Loading State (Suspense)

```typescript
// app/projects/page.tsx
import { Suspense } from 'react'

export default function ProjectsPage() {
  return (
    <div>
      <h1>Projects</h1>
      <Suspense fallback={<ProjectsSkeleton />}>
        <ProjectsList />
      </Suspense>
    </div>
  )
}

async function ProjectsList() {
  const projects = await fetchProjects()

  return (
    <ul>
      {projects.map((project) => (
        <li key={project.id}>{project.name}</li>
      ))}
    </ul>
  )
}

function ProjectsSkeleton() {
  return (
    <div className="animate-pulse">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="h-16 bg-gray-200 rounded mb-2"></div>
      ))}
    </div>
  )
}
```

### Pattern 3: Nested Data Loading

```typescript
export default async function ProjectPage({ params }: { params: { id: string } }) {
  const project = await fetchProject(params.id)

  return (
    <div>
      <h1>{project.name}</h1>

      <Suspense fallback={<CommentsSkeleton />}>
        <Comments projectId={project.id} />
      </Suspense>
    </div>
  )
}

async function Comments({ projectId }: { projectId: string }) {
  const comments = await fetchComments(projectId)

  return (
    <ul>
      {comments.map((comment) => (
        <li key={comment.id}>{comment.text}</li>
      ))}
    </ul>
  )
}
```

## Database Queries

### With Drizzle ORM

```typescript
// lib/db.ts
import { drizzle } from 'drizzle-orm/postgres-js'
import postgres from 'postgres'

const connectionString = process.env.DATABASE_URL!
const client = postgres(connectionString)
export const db = drizzle(client)

// schema.ts
import { pgTable, text, timestamp, uuid } from 'drizzle-orm/pg-core'

export const projects = pgTable('projects', {
  id: uuid('id').defaultRandom().primaryKey(),
  name: text('name').notNull(),
  description: text('description'),
  createdAt: timestamp('created_at').defaultNow(),
})
```

```typescript
// app/projects/page.tsx
import { db } from '@/lib/db'
import { projects } from '@/lib/schema'
import { desc } from 'drizzle-orm'

export default async function ProjectsPage() {
  const allProjects = await db
    .select()
    .from(projects)
    .orderBy(desc(projects.createdAt))

  return (
    <ul>
      {allProjects.map((project) => (
        <li key={project.id}>{project.name}</li>
      ))}
    </ul>
  )
}
```

### Complex Queries

```typescript
import { db } from '@/lib/db'
import { projects, users, tasks } from '@/lib/schema'
import { eq, and, gte } from 'drizzle-orm'

export default async function Dashboard() {
  // Join query
  const projectsWithOwners = await db
    .select({
      projectId: projects.id,
      projectName: projects.name,
      ownerName: users.name,
    })
    .from(projects)
    .leftJoin(users, eq(projects.ownerId, users.id))

  // Filtered query
  const recentProjects = await db
    .select()
    .from(projects)
    .where(
      and(
        eq(projects.status, 'active'),
        gte(projects.createdAt, new Date('2024-01-01'))
      )
    )

  return (
    <div>
      <ProjectsList projects={projectsWithOwners} />
      <RecentProjects projects={recentProjects} />
    </div>
  )
}
```

### Transactions

```typescript
export default async function CreateProjectPage() {
  async function createProjectWithTasks(formData: FormData) {
    'use server'

    const name = formData.get('name') as string
    const taskNames = formData.getAll('tasks') as string[]

    await db.transaction(async (tx) => {
      // Create project
      const [project] = await tx
        .insert(projects)
        .values({ name })
        .returning()

      // Create tasks
      await tx.insert(tasks).values(
        taskNames.map((taskName) => ({
          projectId: project.id,
          name: taskName,
        }))
      )
    })

    revalidatePath('/projects')
  }

  return (
    <form action={createProjectWithTasks}>
      <input name="name" required />
      <input name="tasks" />
      <input name="tasks" />
      <button type="submit">Create</button>
    </form>
  )
}
```

## API Calls

### Basic API Call

```typescript
async function fetchGitHubUser(username: string) {
  const response = await fetch(`https://api.github.com/users/${username}`, {
    headers: {
      Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
    },
    next: { revalidate: 3600 }, // Cache for 1 hour
  })

  if (!response.ok) {
    throw new Error('Failed to fetch user')
  }

  return response.json()
}

export default async function GitHubProfile({ username }: { username: string }) {
  const user = await fetchGitHubUser(username)

  return (
    <div>
      <img src={user.avatar_url} alt={user.name} />
      <h1>{user.name}</h1>
      <p>{user.bio}</p>
    </div>
  )
}
```

### With Request Headers

```typescript
export default async function WeatherPage() {
  const response = await fetch('https://api.weather.com/current', {
    headers: {
      'X-API-Key': process.env.WEATHER_API_KEY!,
      'Content-Type': 'application/json',
    },
  })

  const weather = await response.json()

  return (
    <div>
      <h1>Current Weather</h1>
      <p>Temperature: {weather.temp}°F</p>
    </div>
  )
}
```

### POST Requests

```typescript
async function createProject(data: { name: string; description: string }) {
  const response = await fetch('https://api.example.com/projects', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.API_TOKEN}`,
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error('Failed to create project')
  }

  return response.json()
}
```

## Parallel Data Fetching

### Promise.all Pattern

```typescript
export default async function Dashboard() {
  // ✅ GOOD: Parallel fetching
  const [projects, users, stats] = await Promise.all([
    fetchProjects(),
    fetchUsers(),
    fetchStats(),
  ])

  return (
    <div>
      <h1>Dashboard</h1>
      <ProjectsSection projects={projects} />
      <UsersSection users={users} />
      <StatsSection stats={stats} />
    </div>
  )
}
```

### Suspense Boundaries for Independent Loading

```typescript
export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* Each section loads independently (parallel) */}
      <Suspense fallback={<ProjectsSkeleton />}>
        <ProjectsSection />
      </Suspense>

      <Suspense fallback={<UsersSkeleton />}>
        <UsersSection />
      </Suspense>

      <Suspense fallback={<StatsSkeleton />}>
        <StatsSection />
      </Suspense>
    </div>
  )
}

async function ProjectsSection() {
  const projects = await fetchProjects()
  return <div>{/* render projects */}</div>
}

async function UsersSection() {
  const users = await fetchUsers()
  return <div>{/* render users */}</div>
}

async function StatsSection() {
  const stats = await fetchStats()
  return <div>{/* render stats */}</div>
}
```

## Sequential Data Fetching

### When Data Depends on Previous Data

```typescript
export default async function ProjectDetails({ params }: { params: { id: string } }) {
  // Step 1: Fetch project
  const project = await fetchProject(params.id)

  // Step 2: Fetch related data (depends on project)
  const [owner, tasks] = await Promise.all([
    fetchUser(project.ownerId),
    fetchTasks(project.id),
  ])

  return (
    <div>
      <h1>{project.name}</h1>
      <p>Owner: {owner.name}</p>
      <TasksList tasks={tasks} />
    </div>
  )
}
```

### Waterfall (Avoid When Possible)

```typescript
// ❌ BAD: Sequential waterfall (slow)
export default async function BadDashboard() {
  const projects = await fetchProjects() // Wait 1s
  const users = await fetchUsers() // Wait 1s
  const stats = await fetchStats() // Wait 1s
  // Total: 3 seconds

  return <div>{/* ... */}</div>
}

// ✅ GOOD: Parallel loading (fast)
export default async function GoodDashboard() {
  const [projects, users, stats] = await Promise.all([
    fetchProjects(),
    fetchUsers(),
    fetchStats(),
  ])
  // Total: 1 second (all parallel)

  return <div>{/* ... */}</div>
}
```

## Caching Strategies

### Next.js Fetch Caching

```typescript
// Cache forever (until revalidate or rebuild)
fetch('https://api.example.com/data', {
  cache: 'force-cache', // Default
})

// Never cache
fetch('https://api.example.com/data', {
  cache: 'no-store',
})

// Revalidate after 60 seconds
fetch('https://api.example.com/data', {
  next: { revalidate: 60 },
})

// Tag-based revalidation
fetch('https://api.example.com/data', {
  next: { tags: ['projects'] },
})
```

### Route Segment Config

```typescript
// app/projects/page.tsx

// Revalidate page every 60 seconds
export const revalidate = 60

// Never cache (always dynamic)
export const dynamic = 'force-dynamic'

// Static generation (cache forever)
export const dynamic = 'force-static'

export default async function ProjectsPage() {
  const projects = await fetchProjects()
  return <div>{/* ... */}</div>
}
```

### generateStaticParams for Dynamic Routes

```typescript
// app/projects/[id]/page.tsx

export async function generateStaticParams() {
  const projects = await fetchProjects()

  return projects.map((project) => ({
    id: project.id,
  }))
}

export default async function ProjectPage({ params }: { params: { id: string } }) {
  const project = await fetchProject(params.id)
  return <div>{project.name}</div>
}
```

## Revalidation Patterns

### Time-Based Revalidation

```typescript
// Revalidate every 60 seconds
export const revalidate = 60

export default async function NewsPage() {
  const news = await fetchNews()
  return <div>{/* ... */}</div>
}
```

### On-Demand Revalidation

```typescript
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const { path, tag } = await request.json()

  if (path) {
    revalidatePath(path)
  }

  if (tag) {
    revalidateTag(tag)
  }

  return NextResponse.json({ revalidated: true })
}
```

```typescript
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'

export async function createProject(formData: FormData) {
  const name = formData.get('name') as string

  await db.insert(projects).values({ name })

  // Revalidate projects page
  revalidatePath('/projects')
}
```

### Tag-Based Revalidation

```typescript
// Fetch with tags
async function fetchProjects() {
  const response = await fetch('https://api.example.com/projects', {
    next: { tags: ['projects'] },
  })
  return response.json()
}

// Revalidate by tag
'use server'

import { revalidateTag } from 'next/cache'

export async function createProject(formData: FormData) {
  // Create project...

  // Revalidate all fetches tagged with 'projects'
  revalidateTag('projects')
}
```

## Composition Patterns

### Server Component with Client Child

```typescript
// app/projects/page.tsx (Server Component)
import { ProjectList } from '@/components/ProjectList'

export default async function ProjectsPage() {
  const projects = await fetchProjects()

  return (
    <div>
      <h1>Projects</h1>
      {/* Pass data to Client Component */}
      <ProjectList projects={projects} />
    </div>
  )
}
```

```typescript
// components/ProjectList.tsx (Client Component)
'use client'

import { useState } from 'react'

export function ProjectList({ projects }: { projects: Project[] }) {
  const [filter, setFilter] = useState('')

  const filtered = projects.filter((p) =>
    p.name.toLowerCase().includes(filter.toLowerCase())
  )

  return (
    <div>
      <input
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter..."
      />
      <ul>
        {filtered.map((project) => (
          <li key={project.id}>{project.name}</li>
        ))}
      </ul>
    </div>
  )
}
```

### Multiple Levels of Composition

```typescript
// Page (Server Component)
export default async function Page() {
  const data = await fetchData()

  return (
    <div>
      <ServerHeader data={data} />
      <ClientInteractive data={data}>
        <ServerContent data={data} />
      </ClientInteractive>
    </div>
  )
}

// Server Component
async function ServerHeader({ data }: Props) {
  return <header>{data.title}</header>
}

// Client Component (can have Server Component children!)
'use client'

function ClientInteractive({ data, children }: Props) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div>
      <button onClick={() => setExpanded(!expanded)}>Toggle</button>
      {expanded && children}
    </div>
  )
}

// Server Component
async function ServerContent({ data }: Props) {
  return <div>{data.content}</div>
}
```

## Props to Client Components

### Serializable Props Only

```typescript
// ✅ GOOD: Serializable props
<ClientComponent
  string="hello"
  number={42}
  boolean={true}
  array={[1, 2, 3]}
  object={{ id: 1, name: 'Alice' }}
  date={new Date()} // Serialized to string
/>

// ❌ BAD: Non-serializable props
<ClientComponent
  onClick={() => {}} // ERROR: Function not serializable
  user={new User()} // ERROR: Class instance not serializable
/>
```

### Complex Data Structures

```typescript
interface Project {
  id: string
  name: string
  owner: {
    id: string
    name: string
  }
  tasks: Array<{
    id: string
    title: string
    completed: boolean
  }>
}

export default async function ProjectPage({ params }: { params: { id: string } }) {
  const project: Project = await fetchProject(params.id)

  // ✅ All serializable
  return <ProjectDetails project={project} />
}
```

## Children Pattern

### Passing Server Components as Children

```typescript
// ClientWrapper.tsx (Client Component)
'use client'

import { ReactNode } from 'react'

export function ClientWrapper({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(true)

  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>Toggle</button>
      {isOpen && children}
    </div>
  )
}

// Page.tsx (Server Component)
export default async function Page() {
  const data = await fetchData()

  return (
    <ClientWrapper>
      {/* This is still a Server Component! */}
      <ServerContent data={data} />
    </ClientWrapper>
  )
}

async function ServerContent({ data }: Props) {
  // Can do async operations, database queries, etc.
  return <div>{data}</div>
}
```

### Slots Pattern

```typescript
// Layout.tsx (Client Component)
'use client'

interface LayoutProps {
  header: ReactNode
  sidebar: ReactNode
  main: ReactNode
}

export function Layout({ header, sidebar, main }: LayoutProps) {
  return (
    <div className="grid">
      <header>{header}</header>
      <aside>{sidebar}</aside>
      <main>{main}</main>
    </div>
  )
}

// Page.tsx (Server Component)
export default async function Page() {
  const [headerData, sidebarData, mainData] = await Promise.all([
    fetchHeader(),
    fetchSidebar(),
    fetchMain(),
  ])

  return (
    <Layout
      header={<Header data={headerData} />}
      sidebar={<Sidebar data={sidebarData} />}
      main={<Main data={mainData} />}
    />
  )
}
```

## Context Limitations

### Cannot Provide Context in Server Components

```typescript
// ❌ BAD: Context Provider in Server Component
export default async function Layout({ children }: Props) {
  return (
    <ThemeContext.Provider value="dark">
      {children}
    </ThemeContext.Provider>
  )
}
// ERROR: Context not available in Server Components
```

### Workaround: Wrap with Client Component

```typescript
// providers.tsx (Client Component)
'use client'

import { ReactNode } from 'react'

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeContext.Provider value="dark">
      {children}
    </ThemeContext.Provider>
  )
}

// layout.tsx (Server Component)
import { Providers } from './providers'

export default async function RootLayout({ children }: Props) {
  return (
    <html>
      <body>
        <Providers>
          {/* Children can still be Server Components */}
          {children}
        </Providers>
      </body>
    </html>
  )
}
```

---

**Next**: Read [client-components-complete.md](./client-components-complete.md) for Client Component patterns.
