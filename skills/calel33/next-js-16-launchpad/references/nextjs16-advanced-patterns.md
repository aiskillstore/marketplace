# Next.js 16 Advanced Patterns & Blueprints

Source: `NEXTJS_16_COMPLETE_GUIDE.md` (sections 5-6, 10)

## 1. Cache Components Patterns

### Cache + Tags
```tsx
import { cacheLife, cacheTag } from 'next/cache'

export default async function BlogPage() {
  'use cache'
  cacheLife('hours')
  cacheTag('blog-posts')
  const posts = await db.posts.findMany({ orderBy: { createdAt: 'desc' } })
  return <PostList posts={posts} />
}
```

```ts
'use server'
import { updateTag } from 'next/cache'

export async function createPost(data: PostData) {
  await db.posts.create(data)
  updateTag('blog-posts')
}
```

### Custom Cache Profiles
```ts
const nextConfig: NextConfig = {
  cacheComponents: true,
  cacheLife: {
    'product-catalog': { stale: 3600, revalidate: 7200, expire: 86400 },
  },
}
```

```tsx
export default async function ProductsPage() {
  'use cache'
  cacheLife('product-catalog')
  const products = await db.products.findMany()
  return <ProductGrid products={products} />
}
```

## 2. Streaming & Suspense Composition

```tsx
import { Suspense } from 'react'

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<SkeletonStats />}>
        <Stats />
      </Suspense>
      <Suspense fallback={<SkeletonChart />}>
        <Chart />
      </Suspense>
      <Suspense fallback={<SkeletonActivity />}>
        <RecentActivity />
      </Suspense>
    </div>
  )
}
```

**Guidelines**
- Each `<Suspense>` boundary streams independently.
- Place `cache`-backed sections outside fallback-critical areas to send static shell immediately.

## 3. Parallel Routes & Interception

```
app/
├── layout.tsx            # Renders { children, modal }
├── page.tsx
├── photo/[id]/page.tsx   # Full page
└── @modal/(.)photo/[id]/page.tsx  # Intercepted modal
```

Use for modal overlays, previews, or multi-pane dashboards.

## 4. Proxy & Auth Architecture

```ts
// proxy.ts
import { NextRequest, NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'

export async function proxy(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    const session = await getSession(request)
    if (!session) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }
  return NextResponse.next()
}

export const config = { matcher: ['/dashboard/:path*'] }
```

```ts
// lib/auth.ts
import { cookies } from 'next/headers'
import jwt from 'jsonwebtoken'

export async function getSession(request?: NextRequest) {
  const store = request ? request.cookies : await cookies()
  const token = store.get('auth-token')?.value
  if (!token) return null
  try {
    return jwt.verify(token, process.env.JWT_SECRET!)
  } catch {
    return null
  }
}
```

## 5. Server Actions & Forms

```tsx
// app/blog/new/page.tsx
import { createPost } from '@/app/actions'

export default function NewPostPage() {
  return (
    <form action={createPost} className="space-y-4">
      <input name="title" required />
      <textarea name="content" required />
      <button type="submit">Publish</button>
    </form>
  )
}
```

```ts
// app/actions.ts
'use server'
import { redirect } from 'next/navigation'
import { updateTag } from 'next/cache'

export async function createPost(formData: FormData) {
  const title = formData.get('title')
  const content = formData.get('content')
  const slug = generateSlug(title)
  await db.posts.create({ data: { title, content, slug } })
  updateTag('blog-posts')
  redirect(`/blog/${slug}`)
}
```

## 6. Data Security & React Compiler

- **Taint API**: `experimental_taintObjectReference('message', object)` to prevent leaking sensitive server objects into Client Components.
- **`server-only` package**: Import to assert server-only modules.
- **React Compiler**: Enable via `reactCompiler: true` and install `babel-plugin-react-compiler`; reduces manual memoization.

## 7. Performance Principles

1. **Turbopack Everywhere**: Keep default bundler, leverage incremental compilation and file system cache.
2. **Parallel Fetching**: Kick off independent fetches before `await Promise.all`.
3. **Minimal Client Components**: Prefer server by default; mark `'use client'` only when interactivity needed.
4. **Cache Lifecycle Alignment**: Match `cacheLife` durations with business freshness requirements.
5. **Monitor Build Metrics**: Track `next build` timing to confirm 2-5× improvement; investigate regressions early.

## 8. Real-World Blueprints

### E-commerce Product Page
- Server component loads product shell.
- Cached reviews (`cacheLife('hours')`, `cacheTag('product-:id-reviews')`).
- Client `AddToCartButton` posts to API, calls `router.refresh()`.
- Multiple `<Suspense>` fallbacks keep UX responsive.

### Blog CMS
- Blog index cached with tags; Server Action updates tag + redirects.
- Parallel fetching for metadata & content.
- Proxy protects `/dashboard` author routes.

### SaaS Dashboard
- Proxy enforces auth.
- Layout uses parallel routes for modals.
- Streaming sections deliver stats, charts, and activity in parallel.

Use this file when implementing complex Next.js 16 experiences that go beyond basic bootstrapping.
