# Next.js 16 Deep Reference

Source: `NEXTJS_16_COMPLETE_GUIDE.md` (lines 1-1614)

## 1. Installation & Tooling

- **Runtime Requirements**: Node.js 20.9+, TypeScript 5.1+, React 19.2+, modern browsers (Chrome/Edge/Firefox 111+, Safari 16.4+)
- **Bootstrap Commands**:
  - `npx @next/codemod@canary upgrade latest`
  - `npm install next@latest react@latest react-dom@latest`
  - `npx create-next-app@latest my-app`
- **Recommended `create-next-app` Defaults**: TypeScript, ESLint, Tailwind CSS, App Router, Turbopack, alias `@/*`
- **Scripts**:
  ```json
  {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint",
    "lint:fix": "eslint --fix"
  }
  ```
- **Project Skeleton**: `app/` (layout/page/proxy), `public/`, `next.config.ts`, `package.json`, `tsconfig.json`

## 2. Configuration Changes (v15 → v16)

| Feature | v15 | v16 |
|---------|-----|-----|
| Bundler | Webpack default, opt-in Turbopack | Turbopack default, opt-out `--webpack` |
| PPR | `experimental.ppr` | `cacheComponents` |
| Dynamic IO | `experimental.dynamicIO` | `cacheComponents` |
| React Compiler | `experimental.reactCompiler` | `reactCompiler` |
| Middleware | `middleware.ts` (Edge) | `proxy.ts` (Node) |
| Linting | `next lint` command | Use ESLint directly |

**TypeScript Config Example**:
```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,
  reactCompiler: true,
}

export default nextConfig
```

## 3. Old Way vs New Way

- **Routing**: `pages/*` replaced by `app/*`, nested `layout.tsx`, slots, parallel routes.
- **Data Fetching**: `getServerSideProps`/`getStaticProps` replaced by async Server Components with explicit caching via `'use cache'`, `cacheLife`, and fetch options like `{ next: { revalidate: 60 } }`.
- **Async APIs**: `params`, `searchParams`, `cookies()`, `headers()`, `draftMode()` now return Promises; must await.
- **Caching**: `revalidateTag(tag)` now `revalidateTag(tag, profile)`; new `updateTag` for read-your-writes; `cacheTag`, `cacheLife` stable.
- **Proxy vs Middleware**: `proxy.ts` intercepts requests on Node runtime; `middleware.ts` deprecated.

## 4. Migration Steps & Gotchas

1. **Turbopack by Default**
   - Remove webpack config or opt-out via `next build --webpack` or `turbopack` overrides.
2. **Async Request Codemod**
   - `npx @next/codemod@canary async-request-api`
   - Update component signatures to await `params`, `searchParams`.
3. **`middleware.ts` → `proxy.ts`**
   - Rename file, export `proxy`, maintain `config.matcher`.
4. **Image Query Strings**
   - Configure `images.localPatterns` for `/assets/photo?v=1` style imports.
5. **PPR Flag Removal**
   - Replace `experimental.ppr` and route-level flags with `cacheComponents: true`.
6. **Metadata Image Routes**
   - `id` now `Promise<string>`; await inside route handlers.
7. **Deprecations**
   - Remove `serverRuntimeConfig`, `publicRuntimeConfig`, `next lint`, tilde Sass imports.

**Common Pitfalls**
- Missing `<Suspense>` when Cache Components enabled.
- Using `'use cache'` around runtime-only APIs (cookies/headers) without extracting first.
- Calling `revalidateTag('tag')` without profile argument.
- Plugins injecting webpack config unexpectedly on Turbopack builds.

## 5. Core Patterns & Workflows

### 5.1 Server + Client Composition

```tsx
// app/dashboard/page.tsx (Server)
import { Suspense } from 'react'
import DashboardClient from './dashboard-client'

export default async function DashboardPage() {
  const user = await getUser()
  return (
    <div>
      <h1>Welcome, {user.name}</h1>
      <Suspense fallback={<div>Loading stats...</div>}>
        <DashboardClient userId={user.id} />
      </Suspense>
    </div>
  )
}
```

```tsx
// app/dashboard/dashboard-client.tsx (Client)
'use client'
import { useEffect, useState } from 'react'

export default function DashboardClient({ userId }) {
  const [stats, setStats] = useState(null)
  useEffect(() => {
    fetch(`/api/stats/${userId}`).then(res => res.json()).then(setStats)
  }, [userId])
  return stats ? <div>Stats: {stats.count}</div> : null
}
```

### 5.2 Parallel Data Fetching

```tsx
const artist = fetch(`https://api.example.com/artist/${username}`)
const albums = fetch(`https://api.example.com/artist/${username}/albums`)
const [artistData, albumsData] = await Promise.all([
  artist.then(r => r.json()),
  albums.then(r => r.json()),
])
```

### 5.3 Server Actions + Revalidation

```ts
// app/actions.ts
'use server'
import { updateTag } from 'next/cache'
import { redirect } from 'next/navigation'

export async function createPost(formData: FormData) {
  const title = formData.get('title')
  const content = formData.get('content')
  const slug = generateSlug(title)
  await db.posts.create({ data: { title, content, slug } })
  updateTag('blog-posts')
  redirect(`/blog/${slug}`)
}
```

### 5.4 Proxy Guarded Routes

```ts
// proxy.ts
import { NextRequest, NextResponse } from 'next/server'

export async function proxy(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    const token = request.cookies.get('auth-token')
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }
  return NextResponse.next()
}

export const config = { matcher: ['/dashboard/:path*'] }
```

## 6. Advanced Topics

### 6.1 Cache Components

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
// app/actions.ts
'use server'
import { updateTag } from 'next/cache'

export async function createPost(data: PostData) {
  await db.posts.create(data)
  updateTag('blog-posts')
}
```

### 6.2 Custom `cacheLife` Profiles

```ts
const nextConfig: NextConfig = {
  cacheComponents: true,
  cacheLife: {
    'product-catalog': {
      stale: 3600,
      revalidate: 7200,
      expire: 86400,
    },
  },
}
```

### 6.3 Parallel Routes & Intercepting Modals

```
app/
├── @modal/(.)photo/[id]/page.tsx
├── photo/[id]/page.tsx
├── layout.tsx (renders { children, modal })
└── page.tsx
```

### 6.4 Streaming Dashboard Example

```tsx
<Suspense fallback={<SkeletonStats />}>
  <Stats />
</Suspense>
<Suspense fallback={<SkeletonChart />}>
  <Chart />
</Suspense>
<Suspense fallback={<SkeletonActivity />}>
  <RecentActivity />
</Suspense>
```

### 6.5 React Compiler

- Enable via `reactCompiler: true` in `next.config.ts`
- Install `babel-plugin-react-compiler`
- Reduces manual memoization; trade-off is slower builds due to Babel pass

### 6.6 Taint API for Sensitive Data

```ts
import { experimental_taintObjectReference } from 'react'

export async function getUser(id: string) {
  const user = await db.users.findUnique({ where: { id } })
  experimental_taintObjectReference('Server-only user object', user)
  return user
}
```

## 7. Deployment & Ops

- **Vercel**: First-class support; zero-config for `next build` + `next start`
- **Standalone Output**: Use `output: 'standalone'` for Docker/Node deployments
- **Monitoring**: Track `next build` times to ensure Turbopack retains 2-5× speedup
- **CDN Strategy**: Serve `/public` assets via CDN, align Cache Component TTL with CDN cache headers
- **Turbopack File System Cache**: (Beta) `experimental.turbopackFileSystemCacheForDev = true` for large repos

## 8. Checklists

### Setup Checklist
- [ ] Upgrade Node.js to 20.9+
- [ ] Run `npx @next/codemod@canary upgrade latest`
- [ ] Use App Router + TypeScript defaults
- [ ] Keep Turbopack default (opt-out only if blocker)
- [ ] Configure ESLint scripts (`eslint`, `eslint --fix`)

### Migration Checklist
- [ ] Rename `middleware.ts` → `proxy.ts`
- [ ] Await `params`, `searchParams`, `cookies()`, `headers()`
- [ ] Replace `experimental.*` flags with stable config keys
- [ ] Update `revalidateTag` calls to include profile or use `updateTag`
- [ ] Configure `images.localPatterns` for query-string assets
- [ ] Remove `serverRuntimeConfig`/`publicRuntimeConfig`
- [ ] Replace tilde Sass imports

### Anti-Patterns to Avoid
- [ ] ❌ Using `'use cache'` with runtime request data
- [ ] ❌ Forgetting `<Suspense>` when Cache Components enabled
- [ ] ❌ Leaving webpack-specific plugins without opt-out
- [ ] ❌ Attempting to run `proxy.ts` on Edge runtime
- [ ] ❌ Relying on `next lint` command (removed)

## 9. Version Timeline

| Version | Date | Notes |
|---------|------|-------|
| 16.0.10 | Dec 2025 | Current stable |
| 16.0.0 | Oct 2025 | Turbopack default, Cache Components, `proxy.ts` |
| 15.5.0 | — | Async params typegen |
| 15.0.0 | — | Async Request APIs introduced |

Use this table to confirm behavior when diagnosing historical issues.
