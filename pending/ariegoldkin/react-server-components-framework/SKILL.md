---
name: react-server-components-framework
description: Design and implement React Server Components with Next.js 15 App Router. Master server-first architecture, streaming SSR, Server Actions, and modern data fetching patterns for 2025+ frontend development.
version: 1.0.0
author: AI Agent Hub
tags: [frontend, react, nextjs, server-components, streaming, 2025]
---

# React Server Components Framework

## Overview

React Server Components (RSC) represent a paradigm shift in React architecture, enabling server-first rendering with client-side interactivity. This skill provides comprehensive patterns, templates, and best practices for building modern Next.js 15 applications using the App Router with Server Components, Server Actions, and streaming.

**When to use this skill:**
- Building Next.js 15+ applications with the App Router
- Designing component boundaries (Server vs Client Components)
- Implementing data fetching with caching and revalidation
- Creating mutations with Server Actions
- Optimizing performance with streaming and Suspense
- Implementing Partial Prerendering (PPR)
- Designing advanced routing patterns (parallel, intercepting routes)

---

## Why React Server Components Matter

RSC fundamentally changes how we think about React applications:

- **Server-First Architecture**: Components render on the server by default, reducing client bundle size
- **Zero Client Bundle**: Server Components don't ship JavaScript to the client
- **Direct Backend Access**: Access databases, file systems, and APIs directly from components
- **Automatic Code Splitting**: Only Client Components and their dependencies are bundled
- **Streaming & Suspense**: Progressive rendering for instant perceived performance
- **Type-Safe Data Fetching**: End-to-end TypeScript from database to UI
- **SEO & Performance**: Server rendering improves Core Web Vitals and SEO

---

## Core Concepts

### 1. Server Components vs Client Components

**Server Components** (default):
- Can be `async` and use `await`
- Direct database access
- Cannot use hooks or browser APIs
- Zero client JavaScript

**Client Components** (with `'use client'`):
- Can use hooks (`useState`, `useEffect`, etc.)
- Browser APIs available
- Cannot be `async`
- Ships JavaScript to client

**Key Rule**: Server Components can render Client Components, but Client Components cannot directly import Server Components (use `children` prop instead).

**Detailed Patterns**: See `references/component-patterns.md` for:
- Complete component boundary rules
- Composition patterns
- Props passing strategies
- Common pitfalls and solutions

### 2. Data Fetching

Next.js extends the fetch API with powerful caching and revalidation:

```tsx
// Static (cached indefinitely)
await fetch(url, { cache: 'force-cache' })

// Revalidate every 60 seconds
await fetch(url, { next: { revalidate: 60 } })

// Always fresh
await fetch(url, { cache: 'no-store' })

// Tag-based revalidation
await fetch(url, { next: { tags: ['posts'] } })
```

**Patterns:**
- **Parallel fetching**: `Promise.all([fetch1, fetch2, fetch3])`
- **Sequential fetching**: When data depends on previous results
- **Route segment config**: Control static/dynamic rendering

**Detailed Implementation**: See `references/data-fetching.md` for:
- Complete caching strategies
- Revalidation methods (`revalidatePath`, `revalidateTag`)
- Database queries in Server Components
- generateStaticParams for SSG
- Error handling patterns

### 3. Server Actions

Server Actions enable mutations without API routes:

```tsx
// app/actions.ts
'use server'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  const post = await db.post.create({ data: { title } })

  revalidatePath('/posts')
  redirect(`/posts/${post.id}`)
}
```

**Progressive Enhancement**: Forms work without JavaScript, then enhance with client-side states.

**Detailed Implementation**: See `references/server-actions.md` for:
- Progressive enhancement patterns
- useFormStatus and useFormState hooks
- Optimistic UI with useOptimistic
- Validation with Zod
- Inline vs exported Server Actions

### 4. Streaming with Suspense

Stream components independently for better perceived performance:

```tsx
import { Suspense } from 'react'

export default function Dashboard() {
  return (
    <div>
      <Suspense fallback={<ChartSkeleton />}>
        <RevenueChart />
      </Suspense>

      <Suspense fallback={<InvoicesSkeleton />}>
        <LatestInvoices />
      </Suspense>
    </div>
  )
}
```

**Benefits**:
- Show content as it's ready
- Non-blocking data fetching
- Better Core Web Vitals

**Templates**: Use `templates/ServerComponent.tsx` for streaming patterns

### 5. Advanced Routing

**Parallel Routes**: Render multiple pages simultaneously
```
app/
  @team/page.tsx
  @analytics/page.tsx
  layout.tsx  # Receives both as props
```

**Intercepting Routes**: Show modals while preserving URLs
```
app/
  photos/[id]/page.tsx      # Direct route
  (..)photos/[id]/page.tsx  # Intercepted (modal)
```

**Partial Prerendering (PPR)**: Mix static and dynamic content
```tsx
export const experimental_ppr = true

// Static shell + dynamic Suspense boundaries
```

**Detailed Implementation**: See `references/routing-patterns.md` for:
- Parallel routes layout implementation
- Intercepting routes for modals
- PPR configuration and patterns
- Route groups for organization
- Dynamic, catch-all, and optional catch-all routes

---

## Searching References

Use grep to find specific patterns in references:

```bash
# Find component patterns
grep -r "Server Component" references/

# Search for data fetching strategies
grep -A 10 "Caching Strategies" references/data-fetching.md

# Find Server Actions examples
grep -B 5 "Progressive Enhancement" references/server-actions.md

# Locate routing patterns
grep -n "Parallel Routes" references/routing-patterns.md

# Search migration guide
grep -i "pages router\|getServerSideProps" references/migration-guide.md
```

---

## Best Practices

### Component Boundary Design

- ✅ Keep Client Components at the edges (leaves) of the component tree
- ✅ Use Server Components by default
- ✅ Extract minimal interactive parts to Client Components
- ✅ Pass Server Components as `children` to Client Components
- ❌ Avoid making entire pages Client Components

### Data Fetching

- ✅ Fetch data in Server Components close to where it's used
- ✅ Use parallel fetching for independent data
- ✅ Set appropriate cache and revalidate options
- ✅ Use `generateStaticParams` for static routes
- ❌ Don't fetch data in Client Components with useEffect (use Server Components)

### Performance

- ✅ Use Suspense boundaries for streaming
- ✅ Implement loading.tsx for instant loading states
- ✅ Enable PPR for static/dynamic mix
- ✅ Optimize images with next/image
- ✅ Use route segment config to control rendering mode

### Error Handling

- ✅ Implement error.tsx for error boundaries
- ✅ Use not-found.tsx for 404 pages
- ✅ Handle fetch errors gracefully
- ✅ Validate Server Action inputs

---

## Templates

Use provided templates for common patterns:

- **`templates/ServerComponent.tsx`** - Basic async Server Component with data fetching
- **`templates/ClientComponent.tsx`** - Interactive Client Component with hooks
- **`templates/ServerAction.tsx`** - Server Action with validation and revalidation

---

## Examples

### Complete Blog App

See `examples/blog-app/` for a full implementation:
- Server Components for post listing and details
- Client Components for comments and likes
- Server Actions for creating/editing posts
- Streaming with Suspense
- Parallel routes for dashboard

---

## Checklists

### RSC Implementation Checklist

See `checklists/rsc-implementation.md` for comprehensive validation covering:
- [ ] Component boundaries properly defined (Server vs Client)
- [ ] Data fetching with appropriate caching strategy
- [ ] Server Actions for mutations
- [ ] Streaming with Suspense for slow components
- [ ] Error handling (error.tsx, not-found.tsx)
- [ ] Loading states (loading.tsx)
- [ ] Metadata API for SEO
- [ ] Route segment config optimized

---

## Common Patterns

### Search with URL State

```tsx
// app/search/page.tsx
export default async function SearchPage({
  searchParams,
}: {
  searchParams: { q?: string }
}) {
  const query = searchParams.q || ''
  const results = query ? await searchProducts(query) : []

  return (
    <div>
      <SearchForm initialQuery={query} />
      <SearchResults results={results} />
    </div>
  )
}
```

### Authentication

```tsx
import { cookies } from 'next/headers'

export default async function DashboardPage() {
  const token = cookies().get('token')?.value
  const user = await verifyToken(token)

  if (!user) {
    redirect('/login')
  }

  return <Dashboard user={user} />
}
```

### Optimistic UI

```tsx
'use client'

import { useOptimistic } from 'react'

export function TodoList({ todos }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo) => [...state, newTodo]
  )

  return <ul>{/* render optimisticTodos */}</ul>
}
```

---

## Migration from Pages Router

**Incremental Adoption**: Both `pages/` and `app/` can coexist

**Key Changes**:
- `getServerSideProps` → async Server Component
- `getStaticProps` → async Server Component with caching
- API routes → Server Actions
- `_app.tsx` → `layout.tsx`
- `<Head>` → `generateMetadata` function

**Detailed Migration**: See `references/migration-guide.md` for:
- Step-by-step migration guide
- Before/after code examples
- Common migration pitfalls
- Layout and metadata migration patterns

---

## Troubleshooting

**Error: "You're importing a component that needs useState"**
- **Fix**: Add `'use client'` directive to the component

**Error: "async/await is not valid in non-async Server Components"**
- **Fix**: Add `async` to function declaration

**Error: "Cannot use Server Component inside Client Component"**
- **Fix**: Pass Server Component as `children` prop instead of importing

**Error: "Hydration mismatch"**
- **Fix**: Use `'use client'` for components using `Date.now()`, `Math.random()`, or browser APIs

---

## Resources

- [Next.js 15 Documentation](https://nextjs.org/docs)
- [React Server Components RFC](https://github.com/reactjs/rfcs/blob/main/text/0188-server-components.md)
- [App Router Migration Guide](https://nextjs.org/docs/app/building-your-application/upgrading/app-router-migration)
- [Server Actions Documentation](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)

---

## Next Steps

After mastering React Server Components:
1. Explore **Streaming API Patterns** skill for real-time data
2. Use **Type Safety & Validation** skill for tRPC integration
3. Apply **Edge Computing Patterns** skill for global deployment
4. Reference **Performance Optimization** skill for Core Web Vitals
