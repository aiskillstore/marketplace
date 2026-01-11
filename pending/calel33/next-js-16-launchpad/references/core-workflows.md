# Next.js 16 Core Workflows

Detailed workflows for Next.js 16 setup, configuration, and data patterns.

## Workflow 1: Install and Bootstrap

### Step-by-Step

1. **Verify Requirements**
   ```bash
   node --version  # Should be 20.9.0+
   npx tsc --version  # Should be 5.1.0+
   ```

2. **Install Next.js**
   
   **For new projects:**
   ```bash
   npx create-next-app@latest my-app
   ```
   
   **For upgrades:**
   ```bash
   npx @next/codemod@canary upgrade latest
   npm install next@latest react@latest react-dom@latest
   ```

3. **Configure package.json scripts**
   ```json
   {
     "scripts": {
       "dev": "next dev --turbopack",
       "build": "next build",
       "start": "next start",
       "lint": "eslint .",
       "lint:fix": "eslint . --fix"
     }
   }
   ```

4. **Scaffold Core Files**
   
   Create baseline structure:
   ```
   my-app/
   ├── app/
   │   ├── layout.tsx
   │   ├── page.tsx
   │   ├── proxy.ts
   │   ├── error.tsx
   │   └── loading.tsx
   ├── public/
   ├── next.config.ts
   ├── package.json
   └── tsconfig.json
   ```

5. **Add Styling System**
   
   Tailwind (recommended):
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```

### Minimal Files

```tsx
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

```tsx
// app/page.tsx
export default function Page() {
  return <h1>Hello, Next.js 16!</h1>
}
```

```tsx
// app/error.tsx
'use client'

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

```tsx
// app/loading.tsx
export default function Loading() {
  return <div>Loading...</div>
}
```

---

## Workflow 2: Configuration Modernization

### TypeScript Config

```ts
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Cache Components
  cacheComponents: true,
  
  // React Compiler
  reactCompiler: true,
  
  // Custom cache lifecycles
  cacheLife: {
    'product-catalog': {
      stale: 3600,      // 1 hour
      revalidate: 7200, // 2 hours
      expire: 86400     // 24 hours
    },
  },
  
  // Image configuration
  images: {
    localPatterns: [
      {
        pathname: '/assets/**',
        search: '',
      },
    ],
  },
  
  // Custom Turbopack aliases (if needed)
  turbopack: {
    resolveAlias: {
      '@components': './components',
      '@lib': './lib',
    },
  },
}

export default nextConfig
```

### Migration Table: v15 → v16

| Feature | v15 | v16 | Action |
|---------|-----|-----|--------|
| **Bundler** | `experimental.turbopack` | Default | Remove flag |
| **PPR** | `experimental.ppr` | `cacheComponents` | Rename |
| **Dynamic IO** | `experimental.dynamicIO` | `cacheComponents` | Merge into cacheComponents |
| **Middleware** | `middleware.ts` (Edge) | `proxy.ts` (Node) | Rename & update |
| **React Compiler** | `experimental.reactCompiler` | `reactCompiler` | Remove experimental prefix |
| **Runtime Config** | `serverRuntimeConfig` | Env variables | Remove entirely |
| **Lint in Build** | `next lint` in build | External ESLint | Run separately |
| **Sass Imports** | `~bootstrap/` | `bootstrap/` | Remove tilde |

### Step-by-Step Migration

1. **Remove experimental flags**
   ```ts
   // ❌ Old
   experimental: {
     turbopack: true,
     ppr: true,
     reactCompiler: true
   }
   
   // ✅ New
   cacheComponents: true,
   reactCompiler: true
   ```

2. **Update middleware → proxy**
   ```bash
   mv middleware.ts app/proxy.ts
   ```
   
   ```ts
   // Update exports
   // ❌ Old: export default function middleware()
   // ✅ New: export function proxy()
   ```

3. **Remove deprecated configs**
   ```ts
   // Remove these entirely
   delete config.serverRuntimeConfig
   delete config.publicRuntimeConfig
   ```

4. **Update ESLint**
   ```json
   // package.json - remove from build
   {
     "scripts": {
       "build": "next build",  // No longer runs lint
       "lint": "eslint ."      // Run separately
     }
   }
   ```

5. **Fix Turbopack-incompatible imports**
   ```ts
   // ❌ Old: import 'bootstrap/scss/bootstrap.scss'
   // ✅ New: import 'bootstrap/scss/bootstrap.scss' (remove tilde if using ~)
   ```

---

## Workflow 3: Execution & Data Patterns

### Pattern 1: Basic Server Component

```tsx
// app/blog/page.tsx
export default async function BlogPage() {
  // Fetch runs on server
  const res = await fetch('https://api.example.com/posts')
  const posts = await res.json()
  
  return (
    <div>
      <h1>Blog Posts</h1>
      {posts.map(post => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
        </article>
      ))}
    </div>
  )
}
```

**Benefits:**
- Zero client JavaScript
- SEO-friendly
- Direct database access possible
- Automatic streaming

### Pattern 2: Cache Components

```tsx
import { cacheLife, cacheTag } from 'next/cache'

export default async function BlogPage() {
  'use cache'
  cacheLife('hours')
  cacheTag('blog-posts')
  
  const res = await fetch('https://api.example.com/posts')
  const posts = await res.json()
  
  return <PostList posts={posts} />
}
```

**Cache Lifecycle Profiles:**
```ts
// Built-in profiles
cacheLife('seconds')  // 1 second
cacheLife('minutes')  // 1 minute
cacheLife('hours')    // 1 hour
cacheLife('days')     // 1 day
cacheLife('weeks')    // 1 week
cacheLife('max')      // 1 year

// Custom profiles (define in next.config.ts)
cacheLife('product-catalog')
```

### Pattern 3: Client Components

```tsx
'use client'
import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  )
}
```

**When to use `'use client'`:**
- Need React hooks (`useState`, `useEffect`, etc.)
- Browser APIs (localStorage, window, etc.)
- Event handlers
- Third-party libraries requiring client-side

**Keep server-side when:**
- No interactivity needed
- SEO important
- Reduce bundle size
- Direct data fetching

### Pattern 4: Streaming with Suspense

```tsx
import { Suspense } from 'react'

export default function DashboardPage() {
  return (
    <div className="dashboard">
      <h1>Analytics Dashboard</h1>
      
      <div className="grid">
        <Suspense fallback={<CardSkeleton />}>
          <RevenueCard />
        </Suspense>
        
        <Suspense fallback={<CardSkeleton />}>
          <UsersCard />
        </Suspense>
        
        <Suspense fallback={<CardSkeleton />}>
          <ActivityCard />
        </Suspense>
      </div>
    </div>
  )
}

async function RevenueCard() {
  const revenue = await db.analytics.getRevenue()
  return (
    <div className="card">
      <h2>Revenue</h2>
      <p>${revenue}</p>
    </div>
  )
}

async function UsersCard() {
  const users = await db.analytics.getActiveUsers()
  return (
    <div className="card">
      <h2>Active Users</h2>
      <p>{users}</p>
    </div>
  )
}

async function ActivityCard() {
  const activity = await db.analytics.getRecentActivity()
  return (
    <div className="card">
      <h2>Recent Activity</h2>
      <ul>
        {activity.map(item => (
          <li key={item.id}>{item.description}</li>
        ))}
      </ul>
    </div>
  )
}

function CardSkeleton() {
  return <div className="card skeleton animate-pulse" />
}
```

**Benefits:**
- Sections load independently
- Fast initial paint
- No loading waterfalls
- Progressive enhancement

### Pattern 5: Parallel Data Fetching

```tsx
export default async function ArtistPage({ params }) {
  const { id } = await params
  
  // Start fetches in parallel
  const artistPromise = fetch(`/api/artists/${id}`).then(r => r.json())
  const albumsPromise = fetch(`/api/artists/${id}/albums`).then(r => r.json())
  const toursPromise = fetch(`/api/artists/${id}/tours`).then(r => r.json())
  
  // Wait for all
  const [artist, albums, tours] = await Promise.all([
    artistPromise,
    albumsPromise,
    toursPromise
  ])
  
  return (
    <div>
      <h1>{artist.name}</h1>
      <AlbumList albums={albums} />
      <TourDates tours={tours} />
    </div>
  )
}
```

### Pattern 6: Route States

```tsx
// app/blog/error.tsx
'use client'

export default function BlogError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="error-container">
      <h2>Failed to load blog posts</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

```tsx
// app/blog/loading.tsx
export default function BlogLoading() {
  return (
    <div className="skeleton">
      <div className="skeleton-title" />
      <div className="skeleton-text" />
      <div className="skeleton-text" />
    </div>
  )
}
```

```tsx
// app/blog/not-found.tsx
export default function BlogNotFound() {
  return (
    <div>
      <h2>Blog post not found</h2>
      <a href="/blog">Return to blog</a>
    </div>
  )
}
```

---

## Advanced Patterns

### Cache Components with Custom Lifecycle

```ts
// next.config.ts
const nextConfig: NextConfig = {
  cacheComponents: true,
  cacheLife: {
    'product-catalog': {
      stale: 3600,      // Serve stale for 1 hour
      revalidate: 7200, // Revalidate in background after 2 hours
      expire: 86400     // Hard expire after 24 hours
    },
  },
}
```

```tsx
// app/products/page.tsx
import { cacheLife } from 'next/cache'

export default async function ProductsPage() {
  'use cache'
  cacheLife('product-catalog')
  
  const products = await db.products.findMany()
  return <ProductGrid products={products} />
}
```

### Cache Tags with Server Actions

```tsx
// app/blog/page.tsx
import { cacheLife, cacheTag } from 'next/cache'

export default async function BlogList() {
  'use cache'
  cacheLife('hours')
  cacheTag('blog-posts')
  
  const posts = await db.posts.findMany()
  return <PostList posts={posts} />
}
```

```ts
// app/actions.ts
'use server'
import { updateTag } from 'next/cache'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  const content = formData.get('content') as string
  
  await db.posts.create({ title, content })
  
  // Immediately invalidate cache
  updateTag('blog-posts')
  
  redirect(`/blog/${newPost.slug}`)
}
```

### Proxy with Authentication

```ts
// app/proxy.ts
import { NextRequest, NextResponse } from 'next/server'

export function proxy(request: NextRequest) {
  const session = request.cookies.get('session')
  const { pathname } = request.nextUrl
  
  // Protect dashboard routes
  if (pathname.startsWith('/dashboard')) {
    if (!session) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }
  
  // Redirect logged-in users away from auth pages
  if (pathname.startsWith('/login') && session) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/login']
}
```

---

## Common Patterns Summary

| Pattern | Use When | Example |
|---------|----------|---------|
| **Server Component** | Default, SEO, zero JS | Blog posts, product listings |
| **Client Component** | Interactivity needed | Forms, modals, interactive widgets |
| **Cache Component** | Semi-static data | Product catalogs, blog archives |
| **Suspense Streaming** | Multiple data sources | Dashboards, analytics pages |
| **Proxy** | Auth, redirects | Login checks, route guards |
| **Server Actions** | Form submissions | Create/update/delete operations |

---

## Decision Tree

```
Need interactivity? 
├─ Yes → Client Component ('use client')
└─ No → Server Component
    │
    ├─ Data rarely changes?
    │  └─ Yes → Cache Component ('use cache')
    │
    ├─ Multiple data sources?
    │  └─ Yes → Suspense boundaries
    │
    └─ Need auth check?
       └─ Yes → Add proxy.ts
```
