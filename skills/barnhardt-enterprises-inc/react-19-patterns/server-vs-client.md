# Server vs Client Components - Complete Decision Guide

## Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│           Creating a New React Component                     │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │ Does it need interactivity?           │
    │ (onClick, onChange, onSubmit, etc.)   │
    └───────────┬───────────────────────────┘
                │
        ┌───────┴───────┐
        │               │
       YES             NO
        │               │
        ▼               ▼
    CLIENT          ┌───────────────────────────┐
    COMPONENT       │ Does it need React hooks? │
                    │ (useState, useEffect...)  │
                    └───────┬───────────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
                   YES             NO
                    │               │
                    ▼               ▼
                CLIENT          ┌───────────────────────────┐
                COMPONENT       │ Does it use browser APIs? │
                                │ (window, localStorage...) │
                                └───────┬───────────────────┘
                                        │
                                ┌───────┴───────┐
                                │               │
                               YES             NO
                                │               │
                                ▼               ▼
                            CLIENT          ┌─────────────────────┐
                            COMPONENT       │ Does it fetch data? │
                                            └───────┬─────────────┘
                                                    │
                                            ┌───────┴───────┐
                                            │               │
                                           YES             NO
                                            │               │
                                            ▼               ▼
                                        SERVER          SERVER
                                        COMPONENT       COMPONENT
                                        (preferred)     (default)
```

## Server Components

### What Are Server Components?

Server Components run **only on the server**. They:
- Execute during the build (static) or on each request (dynamic)
- Never send JavaScript to the client
- Can directly access backend resources
- Support async/await for data fetching
- Are the **default** in Next.js App Router

### Benefits

1. **Zero Bundle Size**
   - No JavaScript sent to client
   - Smaller bundle = faster load time
   - Better performance on low-end devices

2. **Direct Backend Access**
   - Query databases directly
   - Access file system
   - Use server-only libraries
   - Read environment variables (without NEXT_PUBLIC_)

3. **Better Security**
   - Keep secrets on server
   - API keys never exposed
   - No client-side code to inspect

4. **SEO Friendly**
   - Fully rendered HTML sent to browser
   - Search engines can index content
   - No hydration delay

5. **Automatic Code Splitting**
   - Only needed code sent to client
   - Reduces initial bundle
   - Faster page loads

### Limitations

**Cannot use:**
- React hooks (useState, useEffect, useContext, etc.)
  - Exception: `use()` hook in React 19
- Event handlers (onClick, onChange, etc.)
- Browser APIs (window, document, localStorage, etc.)
- Lifecycle methods
- React Context (must use Client Components)

**Can use:**
- `async`/`await`
- Node.js APIs (fs, path, etc.)
- Server-only libraries (database clients, etc.)
- Environment variables (all of them)

### When to Use Server Components

✅ **USE for:**
- Data fetching from databases
- Rendering static content
- SEO-critical pages
- Heavy computations (do on server)
- Accessing backend resources
- Reading files
- Server-side only operations

### Examples

#### Example 1: Database Query
```typescript
// app/projects/page.tsx
import { db } from '@/lib/db'

// ✅ Server Component (default)
export default async function ProjectsPage() {
  // Direct database access
  const projects = await db.project.findMany({
    where: { status: 'active' },
    include: { owner: true },
    orderBy: { createdAt: 'desc' },
  })

  return (
    <div>
      <h1>Projects</h1>
      <ProjectList projects={projects} />
    </div>
  )
}
```

#### Example 2: Environment Variables
```typescript
// app/api-status/page.tsx

// ✅ Server Component - access ALL env vars
export default async function ApiStatusPage() {
  const apiKey = process.env.OPENAI_API_KEY // No NEXT_PUBLIC_ needed
  const hasKey = !!apiKey

  const status = await fetch('https://api.openai.com/v1/models', {
    headers: { Authorization: `Bearer ${apiKey}` },
  })

  return (
    <div>
      <h1>API Status</h1>
      <p>API Key Configured: {hasKey ? 'Yes' : 'No'}</p>
      <p>Status: {status.ok ? 'Connected' : 'Error'}</p>
    </div>
  )
}
```

#### Example 3: File System Access
```typescript
// app/docs/[slug]/page.tsx
import fs from 'fs/promises'
import path from 'path'
import { remark } from 'remark'
import html from 'remark-html'

// ✅ Server Component - file system access
export default async function DocPage({ params }: { params: { slug: string } }) {
  const filePath = path.join(process.cwd(), 'docs', `${params.slug}.md`)
  const content = await fs.readFile(filePath, 'utf-8')

  const processedContent = await remark()
    .use(html)
    .process(content)

  return (
    <article dangerouslySetInnerHTML={{ __html: processedContent.toString() }} />
  )
}
```

#### Example 4: Parallel Data Fetching
```typescript
// app/dashboard/page.tsx

// ✅ Server Component - parallel fetching
export default async function DashboardPage() {
  // Fetch multiple data sources in parallel
  const [projects, users, stats] = await Promise.all([
    db.project.findMany(),
    db.user.findMany(),
    db.stats.aggregate(),
  ])

  return (
    <div>
      <h1>Dashboard</h1>
      <StatsPanel stats={stats} />
      <ProjectsGrid projects={projects} />
      <UsersTable users={users} />
    </div>
  )
}
```

## Client Components

### What Are Client Components?

Client Components run **in the browser**. They:
- Hydrate after initial HTML load
- Enable interactivity
- Support React hooks
- Can use browser APIs
- Must use `'use client'` directive

### Benefits

1. **Interactivity**
   - Event handlers (onClick, onChange, etc.)
   - Form interactions
   - Real-time updates

2. **React Hooks**
   - useState, useEffect, useContext
   - Custom hooks
   - React ecosystem libraries

3. **Browser APIs**
   - localStorage, sessionStorage
   - window, document
   - Web APIs (Geolocation, etc.)

4. **Client-Side Libraries**
   - Animation libraries
   - Chart libraries
   - Third-party UI components

### Limitations

**Cannot use:**
- `async` component functions
- Direct database access
- File system access
- Server-only libraries
- Environment variables (without NEXT_PUBLIC_)

**Can use:**
- All React hooks
- Event handlers
- Browser APIs
- Client-side libraries
- useState, useEffect, etc.

### When to Use Client Components

✅ **USE for:**
- Interactive UI elements (buttons, forms, modals)
- State management (useState, useReducer)
- Event handlers (onClick, onChange)
- Browser APIs (localStorage, window)
- Effects (useEffect, useLayoutEffect)
- React Context consumers
- Animations and transitions
- Third-party client libraries

### Examples

#### Example 1: Interactive Form
```typescript
// components/CreateProjectForm.tsx
'use client'

import { useState } from 'react'
import { createProject } from '@/app/actions'

export function CreateProjectForm() {
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      await createProject({ name })
      setName('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Project name"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Project'}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  )
}
```

#### Example 2: Local Storage
```typescript
// components/ThemeToggle.tsx
'use client'

import { useState, useEffect } from 'react'

export function ThemeToggle() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  // Read from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('theme') as 'light' | 'dark' | null
    if (saved) setTheme(saved)
  }, [])

  // Save to localStorage on change
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <button onClick={toggleTheme}>
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  )
}
```

#### Example 3: Real-Time Updates
```typescript
// components/LiveProjectStatus.tsx
'use client'

import { useState, useEffect } from 'react'

interface Project {
  id: string
  status: 'idle' | 'running' | 'completed'
}

export function LiveProjectStatus({ projectId }: { projectId: string }) {
  const [project, setProject] = useState<Project | null>(null)

  useEffect(() => {
    // Poll for updates every 2 seconds
    const interval = setInterval(async () => {
      const response = await fetch(`/api/projects/${projectId}`)
      const data = await response.json()
      setProject(data)
    }, 2000)

    return () => clearInterval(interval)
  }, [projectId])

  if (!project) return <div>Loading...</div>

  return (
    <div className={`status-${project.status}`}>
      Status: {project.status}
    </div>
  )
}
```

#### Example 4: Animation
```typescript
// components/AnimatedModal.tsx
'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export function AnimatedModal() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button onClick={() => setIsOpen(true)}>
        Open Modal
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="modal"
          >
            <h2>Modal Content</h2>
            <button onClick={() => setIsOpen(false)}>Close</button>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
```

## Composition Patterns

### Pattern 1: Server Wrapping Client

The most common pattern - Server Component fetches data and passes to Client Component.

```typescript
// app/projects/page.tsx (Server Component)
import { db } from '@/lib/db'
import { ProjectList } from '@/components/ProjectList'

// ✅ Server Component fetches data
export default async function ProjectsPage() {
  const projects = await db.project.findMany()

  // Pass data as props to Client Component
  return (
    <div>
      <h1>Projects</h1>
      <ProjectList projects={projects} />
    </div>
  )
}

// components/ProjectList.tsx (Client Component)
'use client'

import { useState } from 'react'

interface Project {
  id: string
  name: string
}

// ✅ Client Component handles interactivity
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
        placeholder="Filter projects..."
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

### Pattern 2: Client with Server Children

Client Component can render Server Components as children.

```typescript
// components/ClientWrapper.tsx (Client Component)
'use client'

import { useState, ReactNode } from 'react'

export function ClientWrapper({ children }: { children: ReactNode }) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div>
      <button onClick={() => setIsExpanded(!isExpanded)}>
        {isExpanded ? 'Collapse' : 'Expand'}
      </button>
      {isExpanded && children}
    </div>
  )
}

// app/page.tsx (Server Component)
import { ClientWrapper } from '@/components/ClientWrapper'

export default async function Page() {
  const data = await fetchData()

  return (
    <ClientWrapper>
      {/* This is a Server Component rendered inside Client Component */}
      <ServerDataDisplay data={data} />
    </ClientWrapper>
  )
}

async function ServerDataDisplay({ data }: { data: any }) {
  // This is still a Server Component!
  // It can do async operations, database queries, etc.
  return <div>{JSON.stringify(data)}</div>
}
```

### Pattern 3: Shared Components

Some components work as both Server and Client Components.

```typescript
// components/Button.tsx
// ✅ No 'use client' - works in both!

interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary'
}

export function Button({ children, variant = 'primary' }: ButtonProps) {
  // Purely presentational - no hooks, no events
  return (
    <button className={`btn btn-${variant}`}>
      {children}
    </button>
  )
}

// Can be used in Server Component:
export default async function ServerPage() {
  return <Button>Click Me</Button>
}

// Can be used in Client Component:
'use client'
export function ClientPage() {
  return <Button onClick={() => alert('Hi')}>Click Me</Button>
}
```

### Pattern 4: Context Providers

Context must be in Client Component, but can wrap Server Components.

```typescript
// components/Providers.tsx (Client Component)
'use client'

import { createContext, useState, ReactNode } from 'react'

export const ThemeContext = createContext<{
  theme: 'light' | 'dark'
  setTheme: (theme: 'light' | 'dark') => void
}>({ theme: 'light', setTheme: () => {} })

export function Providers({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

// app/layout.tsx (Server Component)
import { Providers } from '@/components/Providers'

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>
        <Providers>
          {/* Children can be Server Components */}
          {children}
        </Providers>
      </body>
    </html>
  )
}
```

## Props Passing Rules

### Serialization Requirements

Props passed from Server to Client Components **must be serializable**.

#### ✅ Serializable (Allowed)

```typescript
// Primitives
<ClientComponent
  string="hello"
  number={42}
  boolean={true}
  null={null}
  undefined={undefined}
/>

// Arrays
<ClientComponent array={[1, 2, 3]} />

// Plain objects
<ClientComponent user={{ id: 1, name: 'Alice' }} />

// Dates (converted to strings)
<ClientComponent date={new Date()} />
```

#### ❌ Non-Serializable (Not Allowed)

```typescript
// ❌ Functions
<ClientComponent onClick={() => {}} /> // ERROR!

// ❌ Class instances
<ClientComponent user={new User()} /> // ERROR!

// ❌ Symbols
<ClientComponent sym={Symbol('id')} /> // ERROR!

// ❌ BigInt
<ClientComponent big={BigInt(9007199254740991)} /> // ERROR!

// ❌ undefined in objects (becomes null)
<ClientComponent user={{ name: undefined }} /> // Changed to null!
```

### Workarounds

#### Workaround 1: Server Actions

Instead of passing functions, use Server Actions.

```typescript
// app/actions.ts
'use server'

export async function deleteProject(id: string) {
  await db.project.delete({ where: { id } })
}

// app/page.tsx (Server Component)
import { deleteProject } from './actions'

export default async function Page() {
  const projects = await db.project.findMany()

  return <ProjectList projects={projects} deleteAction={deleteProject} />
}

// components/ProjectList.tsx (Client Component)
'use client'

export function ProjectList({ projects, deleteAction }: Props) {
  return (
    <ul>
      {projects.map((p) => (
        <li key={p.id}>
          {p.name}
          <form action={deleteAction}>
            <input type="hidden" name="id" value={p.id} />
            <button type="submit">Delete</button>
          </form>
        </li>
      ))}
    </ul>
  )
}
```

#### Workaround 2: Event Handlers in Client Component

Define event handlers in Client Component, not Server Component.

```typescript
// ❌ DON'T: Pass handler from Server Component
export default async function ServerPage() {
  const handleClick = () => {} // Can't serialize!
  return <ClientButton onClick={handleClick} /> // ERROR!
}

// ✅ DO: Define handler in Client Component
'use client'
export function ClientButton() {
  const handleClick = () => {
    // Handle click here
  }
  return <button onClick={handleClick}>Click</button>
}
```

## Common Mistakes

### Mistake 1: Async Client Component

```typescript
// ❌ DON'T: Async Client Component
'use client'

export default async function BadComponent() {
  const data = await fetch('/api/data')
  return <div>{data}</div>
}
// Error: Client Components cannot be async
```

```typescript
// ✅ DO: Use Server Component
export default async function GoodComponent() {
  const data = await fetch('/api/data')
  return <div>{data}</div>
}

// ✅ OR: Use useEffect in Client Component
'use client'

export default function GoodComponent() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('/api/data')
      .then((res) => res.json())
      .then(setData)
  }, [])

  return <div>{data}</div>
}
```

### Mistake 2: Browser APIs in Server Component

```typescript
// ❌ DON'T: Use browser APIs in Server Component
export default function BadComponent() {
  const theme = localStorage.getItem('theme') // ERROR!
  return <div>Theme: {theme}</div>
}
```

```typescript
// ✅ DO: Use Client Component
'use client'

export default function GoodComponent() {
  const [theme, setTheme] = useState<string | null>(null)

  useEffect(() => {
    setTheme(localStorage.getItem('theme'))
  }, [])

  return <div>Theme: {theme}</div>
}
```

### Mistake 3: Hooks in Server Component

```typescript
// ❌ DON'T: Use hooks in Server Component
export default async function BadComponent() {
  const [count, setCount] = useState(0) // ERROR!
  const data = await fetch('/api/data')
  return <div>{count}</div>
}
```

```typescript
// ✅ DO: Use Client Component for hooks
'use client'

export function GoodComponent() {
  const [count, setCount] = useState(0)
  return <div>{count}</div>
}
```

### Mistake 4: Passing Functions as Props

```typescript
// ❌ DON'T: Pass functions from Server to Client
export default async function ServerPage() {
  const handleClick = () => console.log('hi') // Not serializable!
  return <ClientButton onClick={handleClick} /> // ERROR!
}
```

```typescript
// ✅ DO: Use Server Actions or define in Client
'use server'

async function handleClick() {
  console.log('hi')
}

export default async function ServerPage() {
  return <ClientButton action={handleClick} /> // ✅ Server Action
}

// OR define in Client Component
'use client'
export function ClientButton() {
  const handleClick = () => console.log('hi')
  return <button onClick={handleClick}>Click</button>
}
```

## Quick Reference Checklist

### When to Use Server Component

- [ ] Fetching data from database
- [ ] Fetching data from API
- [ ] Reading files
- [ ] Using Node.js APIs
- [ ] Accessing environment variables
- [ ] Static/SEO content
- [ ] No interactivity needed

### When to Use Client Component

- [ ] Event handlers (onClick, etc.)
- [ ] React hooks (useState, etc.)
- [ ] Browser APIs (localStorage, etc.)
- [ ] Animations
- [ ] Form inputs with state
- [ ] Real-time updates
- [ ] Third-party client libraries

### Props Checklist

- [ ] Props are serializable (JSON-compatible)
- [ ] No functions (use Server Actions)
- [ ] No class instances
- [ ] No symbols or BigInt

---

**Next**: Read [hooks-complete.md](./hooks-complete.md) for all React hooks reference.
