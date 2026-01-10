# Next.js 15 App Router - Complete Guide

Complete reference for all Next.js 15 App Router patterns and conventions.

**Official Docs:** https://nextjs.org/docs/app

---

## Table of Contents

- [File-Based Routing](#file-based-routing)
- [Dynamic Routes](#dynamic-routes)
- [Route Groups](#route-groups)
- [Private Folders](#private-folders)
- [Route Handlers](#route-handlers)
- [Layouts and Templates](#layouts-and-templates)
- [Loading UI](#loading-ui)
- [Error Boundaries](#error-boundaries)
- [Not Found Pages](#not-found-pages)
- [Parallel Routes](#parallel-routes)
- [Intercepting Routes](#intercepting-routes)
- [Route Segment Config](#route-segment-config)

---

## File-Based Routing

Next.js uses file-system based routing where folders define routes.

### Example 1: Basic Page

```
app/
├── page.tsx          # / route
├── about/
│   └── page.tsx      # /about route
└── blog/
    └── page.tsx      # /blog route
```

```typescript
// app/page.tsx
export default function HomePage() {
  return <h1>Home Page</h1>
}

// app/about/page.tsx
export default function AboutPage() {
  return <h1>About Page</h1>
}
```

### Example 2: Nested Routes

```
app/
└── dashboard/
    ├── page.tsx              # /dashboard
    └── projects/
        ├── page.tsx          # /dashboard/projects
        └── [id]/
            └── page.tsx      # /dashboard/projects/123
```

```typescript
// app/dashboard/page.tsx
export default function DashboardPage() {
  return <h1>Dashboard</h1>
}

// app/dashboard/projects/page.tsx
export default async function ProjectsPage() {
  const projects = await fetchProjects()
  return <ProjectList projects={projects} />
}
```

### Example 3: Route Precedence

Order of precedence (highest to lowest):
1. Static routes
2. Dynamic routes with single segment
3. Dynamic routes with catch-all
4. Dynamic routes with optional catch-all

```
app/
├── blog/
│   ├── page.tsx           # /blog (highest)
│   ├── [slug]/
│   │   └── page.tsx       # /blog/hello
│   ├── [...slug]/
│   │   └── page.tsx       # /blog/a/b/c
│   └── [[...slug]]/
│       └── page.tsx       # /blog OR /blog/a/b/c (lowest)
```

---

## Dynamic Routes

Dynamic routes use square brackets in folder names.

### Example 4: Single Dynamic Segment

```typescript
// app/blog/[slug]/page.tsx
interface PageProps {
  params: Promise<{ slug: string }>
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}

export default async function BlogPostPage({ params }: PageProps) {
  const { slug } = await params
  const post = await fetchPost(slug)

  return (
    <article>
      <h1>{post.title}</h1>
      <div>{post.content}</div>
    </article>
  )
}

// Generate static params at build time
export async function generateStaticParams() {
  const posts = await fetchAllPosts()

  return posts.map((post) => ({
    slug: post.slug,
  }))
}
```

### Example 5: Multiple Dynamic Segments

```typescript
// app/shop/[category]/[product]/page.tsx
interface PageProps {
  params: Promise<{ category: string; product: string }>
}

export default async function ProductPage({ params }: PageProps) {
  const { category, product } = await params
  const item = await fetchProduct(category, product)

  return (
    <div>
      <h1>{item.name}</h1>
      <p>Category: {category}</p>
    </div>
  )
}

export async function generateStaticParams() {
  const products = await fetchAllProducts()

  return products.map((product) => ({
    category: product.category,
    product: product.slug,
  }))
}
```

### Example 6: Catch-All Segments

```typescript
// app/docs/[...slug]/page.tsx
interface PageProps {
  params: Promise<{ slug: string[] }>
}

export default async function DocsPage({ params }: PageProps) {
  const { slug } = await params
  // /docs/a/b/c → slug = ['a', 'b', 'c']

  const doc = await fetchDoc(slug.join('/'))

  return (
    <div>
      <h1>{doc.title}</h1>
      <Breadcrumbs path={slug} />
      <div>{doc.content}</div>
    </div>
  )
}

export async function generateStaticParams() {
  const docs = await fetchAllDocs()

  return docs.map((doc) => ({
    slug: doc.path.split('/'),
  }))
}
```

### Example 7: Optional Catch-All Segments

```typescript
// app/shop/[[...slug]]/page.tsx
interface PageProps {
  params: Promise<{ slug?: string[] }>
}

export default async function ShopPage({ params }: PageProps) {
  const { slug } = await params

  // /shop → slug = undefined
  // /shop/clothing → slug = ['clothing']
  // /shop/clothing/shirts → slug = ['clothing', 'shirts']

  if (!slug || slug.length === 0) {
    return <AllCategories />
  }

  const [category, ...subcategories] = slug
  return <CategoryPage category={category} subcategories={subcategories} />
}
```

---

## Route Groups

Route groups organize routes without affecting URL structure.

### Example 8: Basic Route Group

```
app/
├── (marketing)/
│   ├── about/
│   │   └── page.tsx       # /about (not /marketing/about)
│   └── contact/
│       └── page.tsx       # /contact
└── (shop)/
    ├── products/
    │   └── page.tsx       # /products
    └── cart/
        └── page.tsx       # /cart
```

```typescript
// app/(marketing)/about/page.tsx
export default function AboutPage() {
  return <h1>About Us</h1>
}
// URL: /about (parentheses are omitted)
```

### Example 9: Multiple Root Layouts

```
app/
├── (marketing)/
│   ├── layout.tsx         # Marketing layout
│   └── page.tsx           # /
└── (app)/
    ├── layout.tsx         # App layout
    └── dashboard/
        └── page.tsx       # /dashboard
```

```typescript
// app/(marketing)/layout.tsx
export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="marketing-layout">
      <MarketingNav />
      <main>{children}</main>
      <MarketingFooter />
    </div>
  )
}

// app/(app)/layout.tsx
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-layout">
      <AppSidebar />
      <main>{children}</main>
    </div>
  )
}
```

### Example 10: Organizing by Feature

```
app/
├── (auth)/
│   ├── login/
│   │   └── page.tsx       # /login
│   ├── register/
│   │   └── page.tsx       # /register
│   └── layout.tsx         # Auth layout (centered card)
└── (dashboard)/
    ├── projects/
    │   └── page.tsx       # /projects
    ├── settings/
    │   └── page.tsx       # /settings
    └── layout.tsx         # Dashboard layout (sidebar)
```

---

## Private Folders

Prefix folders with underscore to exclude from routing.

### Example 11: Private Components Folder

```
app/
└── dashboard/
    ├── _components/       # NOT a route
    │   ├── Header.tsx
    │   └── Sidebar.tsx
    ├── _lib/              # NOT a route
    │   └── utils.ts
    └── page.tsx           # /dashboard
```

```typescript
// app/dashboard/_components/Header.tsx
export function DashboardHeader() {
  return <header>Dashboard</header>
}

// app/dashboard/page.tsx
import { DashboardHeader } from './_components/Header'

export default function DashboardPage() {
  return (
    <div>
      <DashboardHeader />
      <main>Content</main>
    </div>
  )
}
```

### Example 12: Private Utilities

```
app/
└── api/
    ├── _middleware/       # NOT a route
    │   ├── auth.ts
    │   └── validation.ts
    ├── _schemas/          # NOT a route
    │   └── project.ts
    └── projects/
        └── route.ts       # /api/projects
```

```typescript
// app/api/_middleware/auth.ts
export function requireAuth(request: Request) {
  const token = request.headers.get('authorization')
  if (!token) throw new Error('Unauthorized')
  return verifyToken(token)
}

// app/api/projects/route.ts
import { requireAuth } from '../_middleware/auth'

export async function GET(request: Request) {
  const user = requireAuth(request)
  const projects = await fetchProjects(user.id)
  return Response.json(projects)
}
```

---

## Route Handlers

API routes using route.ts files.

### Example 13: Basic Route Handler

```typescript
// app/api/hello/route.ts
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  return NextResponse.json({ message: 'Hello World' })
}

export async function POST(request: Request) {
  const body = await request.json()
  return NextResponse.json({ received: body }, { status: 201 })
}
```

### Example 14: Dynamic Route Handler

```typescript
// app/api/projects/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server'

interface RouteContext {
  params: Promise<{ id: string }>
}

export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  const { id } = await context.params
  const project = await fetchProject(id)

  if (!project) {
    return NextResponse.json(
      { error: 'Project not found' },
      { status: 404 }
    )
  }

  return NextResponse.json(project)
}

export async function PATCH(
  request: NextRequest,
  context: RouteContext
) {
  const { id } = await context.params
  const updates = await request.json()

  const project = await updateProject(id, updates)
  return NextResponse.json(project)
}

export async function DELETE(
  request: NextRequest,
  context: RouteContext
) {
  const { id } = await context.params
  await deleteProject(id)

  return NextResponse.json(null, { status: 204 })
}
```

### Example 15: Search Params in Route Handler

```typescript
// app/api/search/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const query = searchParams.get('q')
  const limit = searchParams.get('limit') || '10'
  const offset = searchParams.get('offset') || '0'

  const results = await search(query, {
    limit: parseInt(limit),
    offset: parseInt(offset),
  })

  return NextResponse.json({
    results,
    pagination: {
      limit: parseInt(limit),
      offset: parseInt(offset),
      total: results.length,
    },
  })
}
```

### Example 16: Headers and Cookies

```typescript
// app/api/auth/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function POST(request: NextRequest) {
  const { email, password } = await request.json()

  // Authenticate user
  const user = await authenticate(email, password)
  const token = generateToken(user)

  // Set cookie
  const cookieStore = await cookies()
  cookieStore.set('auth-token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7, // 7 days
  })

  // Set custom headers
  const response = NextResponse.json({ user })
  response.headers.set('X-Custom-Header', 'value')

  return response
}

export async function DELETE(request: NextRequest) {
  // Clear cookie
  const cookieStore = await cookies()
  cookieStore.delete('auth-token')

  return NextResponse.json({ success: true })
}
```

### Example 17: Streaming Response

```typescript
// app/api/stream/route.ts
export async function GET() {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 0; i < 10; i++) {
        const message = `Event ${i}\n\n`
        controller.enqueue(encoder.encode(message))
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
      controller.close()
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

---

## Layouts and Templates

Layouts and templates share UI across routes.

### Example 18: Root Layout

```typescript
// app/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Quetrex - AI Development Platform',
  description: 'Voice-first AI assistant for developers',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
```

### Example 19: Nested Layouts

```typescript
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="dashboard-layout">
      <DashboardSidebar />
      <main className="dashboard-main">
        {children}
      </main>
    </div>
  )
}

// app/dashboard/projects/layout.tsx
export default function ProjectsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="projects-layout">
      <ProjectsHeader />
      <div className="projects-content">
        {children}
      </div>
    </div>
  )
}
```

### Example 20: Template (Resets State)

```typescript
// app/template.tsx
'use client'

import { useEffect } from 'react'

// Templates create NEW instance on navigation (layouts persist)
export default function Template({
  children,
}: {
  children: React.ReactNode
}) {
  useEffect(() => {
    console.log('Template mounted - runs on every navigation')
  }, [])

  return <div className="template-wrapper">{children}</div>
}
```

### Example 21: Layout with Parallel Routes

```typescript
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  return (
    <div className="dashboard">
      <div className="main">{children}</div>
      <div className="sidebar">
        <section>{analytics}</section>
        <section>{team}</section>
      </div>
    </div>
  )
}
```

---

## Loading UI

Loading states with loading.tsx.

### Example 22: Basic Loading State

```typescript
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="loading-container">
      <Spinner />
      <p>Loading dashboard...</p>
    </div>
  )
}

// app/dashboard/page.tsx
export default async function DashboardPage() {
  // This delay triggers loading.tsx
  const data = await fetchDashboardData()
  return <Dashboard data={data} />
}
```

### Example 23: Skeleton Loading UI

```typescript
// app/projects/loading.tsx
export default function ProjectsLoading() {
  return (
    <div className="projects-grid">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="project-card-skeleton">
          <div className="skeleton-title" />
          <div className="skeleton-description" />
          <div className="skeleton-footer" />
        </div>
      ))}
    </div>
  )
}
```

### Example 24: Nested Loading States

```
app/
└── dashboard/
    ├── loading.tsx           # Loading for /dashboard
    ├── page.tsx              # /dashboard
    └── projects/
        ├── loading.tsx       # Loading for /dashboard/projects
        └── page.tsx          # /dashboard/projects
```

```typescript
// app/dashboard/loading.tsx
export default function DashboardLoading() {
  return <DashboardSkeleton />
}

// app/dashboard/projects/loading.tsx
export default function ProjectsLoading() {
  return <ProjectsListSkeleton />
}
```

---

## Error Boundaries

Error handling with error.tsx.

### Example 25: Basic Error Boundary

```typescript
// app/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="error-container">
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

### Example 26: Nested Error Boundaries

```typescript
// app/dashboard/error.tsx
'use client'

import { useEffect } from 'react'

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log to error reporting service
    console.error('Dashboard error:', error)
  }, [error])

  return (
    <div className="dashboard-error">
      <h2>Dashboard Error</h2>
      <details>
        <summary>Error details</summary>
        <pre>{error.message}</pre>
      </details>
      <button onClick={reset}>Reload Dashboard</button>
    </div>
  )
}
```

### Example 27: Global Error Handler

```typescript
// app/global-error.tsx
'use client'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>
      <body>
        <div className="global-error">
          <h1>Critical Error</h1>
          <p>The application encountered a critical error.</p>
          <button onClick={reset}>Reload Application</button>
        </div>
      </body>
    </html>
  )
}
```

---

## Not Found Pages

Custom 404 pages with not-found.tsx.

### Example 28: Root Not Found

```typescript
// app/not-found.tsx
import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="not-found">
      <h1>404 - Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
      <Link href="/">Go back home</Link>
    </div>
  )
}
```

### Example 29: Dynamic Not Found

```typescript
// app/blog/[slug]/page.tsx
import { notFound } from 'next/navigation'

export default async function BlogPost({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = await fetchPost(slug)

  if (!post) {
    notFound() // Triggers closest not-found.tsx
  }

  return <article>{post.content}</article>
}

// app/blog/not-found.tsx
export default function BlogNotFound() {
  return (
    <div>
      <h1>Blog Post Not Found</h1>
      <p>This blog post doesn't exist.</p>
    </div>
  )
}
```

### Example 30: Nested Not Found Pages

```
app/
├── not-found.tsx              # Global 404
└── dashboard/
    ├── not-found.tsx          # Dashboard 404
    └── projects/
        └── [id]/
            ├── not-found.tsx  # Project 404
            └── page.tsx
```

```typescript
// app/dashboard/projects/[id]/not-found.tsx
export default function ProjectNotFound() {
  return (
    <div className="project-not-found">
      <h2>Project Not Found</h2>
      <p>This project doesn't exist or you don't have access.</p>
      <Link href="/dashboard/projects">View all projects</Link>
    </div>
  )
}
```

---

## Parallel Routes

Render multiple pages in the same layout using @folder convention.

### Example 31: Dashboard with Parallel Routes

```
app/
└── dashboard/
    ├── layout.tsx
    ├── page.tsx
    ├── @analytics/
    │   └── page.tsx       # Parallel slot
    └── @team/
        └── page.tsx       # Parallel slot
```

```typescript
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  return (
    <div className="dashboard-layout">
      <main>{children}</main>
      <aside>
        <section>{analytics}</section>
        <section>{team}</section>
      </aside>
    </div>
  )
}

// app/dashboard/@analytics/page.tsx
export default async function AnalyticsSlot() {
  const metrics = await fetchMetrics()
  return <AnalyticsChart metrics={metrics} />
}

// app/dashboard/@team/page.tsx
export default async function TeamSlot() {
  const team = await fetchTeam()
  return <TeamList members={team} />
}
```

### Example 32: Conditional Parallel Routes

```typescript
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  const showAnalytics = true // Could be from user settings

  return (
    <div className="dashboard-layout">
      <main>{children}</main>
      <aside>
        {showAnalytics && <section>{analytics}</section>}
        <section>{team}</section>
      </aside>
    </div>
  )
}
```

### Example 33: Default Parallel Route Fallback

```
app/
└── dashboard/
    ├── layout.tsx
    ├── @analytics/
    │   ├── default.tsx    # Fallback when no match
    │   └── page.tsx
    └── settings/
        └── page.tsx       # @analytics not defined here
```

```typescript
// app/dashboard/@analytics/default.tsx
export default function AnalyticsDefault() {
  return null // Don't show analytics by default
}
```

---

## Intercepting Routes

Intercept routes for modals and overlays.

### Example 34: Photo Modal (Instagram-style)

```
app/
└── photos/
    ├── page.tsx              # /photos (grid)
    ├── [id]/
    │   └── page.tsx          # /photos/123 (full page)
    └── (.)[id]/
        └── page.tsx          # Intercept /photos/123 (modal)
```

```typescript
// app/photos/page.tsx
import Link from 'next/link'

export default function PhotosPage() {
  return (
    <div className="photo-grid">
      {photos.map(photo => (
        <Link key={photo.id} href={`/photos/${photo.id}`}>
          <img src={photo.url} alt={photo.title} />
        </Link>
      ))}
    </div>
  )
}

// app/photos/(.)[id]/page.tsx (Modal)
import Modal from '@/components/Modal'

export default async function PhotoModal({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const photo = await fetchPhoto(id)

  return (
    <Modal>
      <img src={photo.url} alt={photo.title} />
    </Modal>
  )
}

// app/photos/[id]/page.tsx (Full page - same content, different layout)
export default async function PhotoPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const photo = await fetchPhoto(id)

  return (
    <div className="photo-page">
      <img src={photo.url} alt={photo.title} />
      <PhotoDetails photo={photo} />
    </div>
  )
}
```

### Example 35: Login Modal Intercept

```
app/
├── login/
│   └── page.tsx          # /login (full page)
└── @auth/
    └── (.)login/
        └── page.tsx      # Intercept /login (modal)
```

```typescript
// app/login/page.tsx
export default function LoginPage() {
  return (
    <div className="login-page">
      <LoginForm />
    </div>
  )
}

// app/@auth/(.)login/page.tsx
export default function LoginModal() {
  return (
    <Modal>
      <LoginForm />
    </Modal>
  )
}
```

### Example 36: Intercepting Route Markers

```
// (.) - Same level
app/feed/(.)photo/[id]

// (..) - One level up
app/feed/(..)photo/[id]

// (..)(..) - Two levels up
app/feed/(..)(...)photo/[id]

// (...) - Root app directory
app/feed/(...)photo/[id]
```

---

## Route Segment Config

Configure route behavior with exported constants.

### Example 37: Dynamic Routes Configuration

```typescript
// app/blog/[slug]/page.tsx

// Force static generation (default)
export const dynamic = 'auto'

// Force dynamic rendering (no static generation)
export const dynamic = 'force-dynamic'

// Force static rendering (throw error if dynamic)
export const dynamic = 'force-static'

// Error if any dynamic functions are used
export const dynamic = 'error'

export default async function BlogPost({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = await fetchPost(slug)
  return <article>{post.content}</article>
}
```

### Example 38: Revalidation Configuration

```typescript
// app/blog/page.tsx

// Revalidate every 60 seconds (ISR)
export const revalidate = 60

// Never revalidate (static)
export const revalidate = false

// Always revalidate (dynamic)
export const revalidate = 0

export default async function BlogPage() {
  const posts = await fetchPosts()
  return <PostList posts={posts} />
}
```

### Example 39: Fetch Cache Configuration

```typescript
// app/dashboard/page.tsx

// Default fetch cache behavior
export const fetchCache = 'auto'

// Store all fetches in cache
export const fetchCache = 'default-cache'

// Never use cache
export const fetchCache = 'force-no-store'

// Always use cache
export const fetchCache = 'force-cache'

// Only use cache for GET requests
export const fetchCache = 'only-cache'

export default async function DashboardPage() {
  const data = await fetch('https://api.example.com/data')
  return <Dashboard data={data} />
}
```

### Example 40: Runtime Configuration

```typescript
// app/api/route.ts

// Use Node.js runtime (default)
export const runtime = 'nodejs'

// Use Edge runtime (lighter, faster)
export const runtime = 'edge'

export async function GET() {
  return Response.json({ message: 'Hello' })
}
```

### Example 41: Preferred Region

```typescript
// app/api/users/route.ts

// Deploy to specific regions
export const preferredRegion = 'iad1' // US East

// Deploy to multiple regions
export const preferredRegion = ['iad1', 'sfo1']

// Deploy to all regions
export const preferredRegion = 'auto'

export async function GET() {
  const users = await fetchUsers()
  return Response.json(users)
}
```

### Example 42: Maximum Duration

```typescript
// app/api/long-task/route.ts

// Set max execution time (seconds)
export const maxDuration = 300 // 5 minutes

export async function POST(request: Request) {
  const result = await longRunningTask()
  return Response.json(result)
}
```

### Example 43: Combined Configuration

```typescript
// app/products/[id]/page.tsx

// Combine multiple configs
export const dynamic = 'force-dynamic'
export const revalidate = 0
export const runtime = 'edge'
export const preferredRegion = 'iad1'

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const product = await fetchProduct(id)
  return <Product data={product} />
}
```

---

## Advanced Patterns

### Example 44: Shared Layouts with Route Groups

```
app/
├── (app)/
│   ├── layout.tsx        # App layout
│   ├── dashboard/
│   │   └── page.tsx      # /dashboard
│   └── settings/
│       └── page.tsx      # /settings
└── (marketing)/
    ├── layout.tsx        # Marketing layout
    ├── page.tsx          # /
    └── about/
        └── page.tsx      # /about
```

### Example 45: Private and Public API Routes

```
app/
└── api/
    ├── public/
    │   └── status/
    │       └── route.ts  # /api/public/status
    └── private/
        └── users/
            └── route.ts  # /api/private/users (auth required)
```

```typescript
// app/api/private/users/route.ts
import { requireAuth } from '@/lib/auth'

export async function GET(request: Request) {
  await requireAuth(request)
  const users = await fetchUsers()
  return Response.json(users)
}
```

---

## Summary

**File Conventions:**
- `page.tsx` - Page component
- `layout.tsx` - Layout component (persists across navigation)
- `template.tsx` - Template component (re-renders on navigation)
- `loading.tsx` - Loading UI
- `error.tsx` - Error boundary
- `not-found.tsx` - 404 page
- `route.ts` - API route handler

**Folder Conventions:**
- `[folder]` - Dynamic route segment
- `[...folder]` - Catch-all segment
- `[[...folder]]` - Optional catch-all
- `(folder)` - Route group (omitted from URL)
- `_folder` - Private folder (excluded from routing)
- `@folder` - Parallel route slot

**Best Practices:**
1. Use Server Components by default
2. Add `'use client'` only when needed
3. Organize with route groups
4. Use private folders for utilities
5. Provide loading and error states
6. Configure routes appropriately
7. Use parallel routes for complex layouts
8. Use intercepting routes for modals

**Official Docs:**
- App Router: https://nextjs.org/docs/app/building-your-application/routing
- Route Handlers: https://nextjs.org/docs/app/building-your-application/routing/route-handlers
- Route Segment Config: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config
