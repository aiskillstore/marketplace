# React Integration Guide

Complete guide to real-time cache invalidation with SSE and React hooks.

## Table of Contents

- [Overview](#overview)
- [Server Setup](#server-setup)
- [Client Setup](#client-setup)
- [useCache Hook](#usecache-hook)
- [Filtering Strategies](#filtering-strategies)
- [Advanced Patterns](#advanced-patterns)
- [Debugging](#debugging)
- [Performance Considerations](#performance-considerations)

---

## Overview

remix-cache provides real-time cache invalidation using Server-Sent Events (SSE). When you invalidate a cache entry on the server, connected clients automatically revalidate their data.

### Architecture

```
Server (Action)           SSE Endpoint              Client (React)
─────────────────        ──────────────           ─────────────────
    │                          │                         │
    │ 1. Update data           │                         │
    │ 2. Invalidate cache      │                         │
    ├─────────────────────────>│                         │
    │                          │ 3. Broadcast event      │
    │                          ├────────────────────────>│
    │                          │                         │ 4. useCache receives
    │                          │                         │ 5. Calls revalidate()
    │                          │                         │ 6. Loader re-runs
    │<────────────────────────────────────────────────────┤
    │ 7. Returns fresh data    │                         │
```

### Benefits

- **Real-time updates**: Changes reflect immediately across all clients
- **Automatic revalidation**: No manual polling or refresh needed
- **Selective updates**: Filter which components revalidate
- **Debouncing**: Coalesce rapid invalidations
- **Type-safe**: Full TypeScript support

---

## Server Setup

### Step 1: Create SSE endpoint

Create `app/routes/api.cache-events.tsx`:

```typescript
import { createSSEHandler } from 'remix-cache/server'
import { cache } from '~/cache.server'

// This exports a loader that streams invalidation events
export const loader = createSSEHandler(cache)
```

This creates a Remix resource route that:
1. Accepts SSE connections
2. Subscribes to cache invalidation events
3. Streams events to connected clients
4. Cleans up on disconnect

### Step 2: Emit invalidation events

Invalidation events are automatically emitted when you use any invalidation method:

```typescript
// app/routes/users.$userId.edit.tsx
export async function action({ request, params }: ActionFunctionArgs) {
  const formData = await request.formData()

  // Update database
  const user = await db.user.update({
    where: { id: params.userId },
    data: Object.fromEntries(formData),
  })

  // This automatically emits an SSE event
  await cache.invalidateByTag('user')

  return json({ user })
}
```

All invalidation methods emit events:
- `cache.invalidate({ key })` - Emits key invalidation
- `cache.invalidateByTag(tag)` - Emits tag invalidation
- `cache.invalidateByPattern(pattern)` - Emits pattern invalidation
- `cacheDefinition.delete(...)` - Emits key invalidation

### Step 3: Verify endpoint

Test your SSE endpoint manually:

```bash
curl -N http://localhost:3000/api/cache-events
```

You should see an open connection. When you invalidate a cache entry (in another terminal or browser), you'll see events like:

```
event: invalidate
data: {"tag":"user","timestamp":1234567890}
```

---

## Client Setup

### Step 1: Wrap app with CacheProvider

Update `app/root.tsx`:

```typescript
import { CacheProvider } from 'remix-cache/react'
import {
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from '@remix-run/react'

export default function App() {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        <CacheProvider endpoint="/api/cache-events">
          <Outlet />
        </CacheProvider>
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  )
}
```

### CacheProvider Props

```typescript
interface CacheProviderProps {
  children: ReactNode
  endpoint?: string  // Default: '/api/cache-events'
}
```

**endpoint**: URL of your SSE endpoint
- Default: `/api/cache-events`
- Can be absolute or relative
- Must match your SSE route path

### Step 2: Use the useCache hook

In any component that should revalidate on cache changes:

```typescript
import { useCache } from 'remix-cache/react'
import { useLoaderData } from '@remix-run/react'
import type { loader } from './route'

export default function UserProfile() {
  const { user } = useLoaderData<typeof loader>()

  // Revalidate when 'user' tag is invalidated
  useCache({ tags: ['user'] })

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  )
}
```

---

## useCache Hook

### Basic Usage

```typescript
import { useCache } from 'remix-cache/react'

// Revalidate on any invalidation
useCache()

// Revalidate on specific tags
useCache({ tags: ['user', 'profile'] })

// Revalidate on specific keys
useCache({ keys: ['myapp:user:123'] })

// Revalidate on patterns
useCache({ patterns: ['user:*'] })

// With custom debounce
useCache({ tags: ['product'], debounce: 300 })
```

### Options

```typescript
interface UseCacheOptions {
  keys?: string[]      // Specific cache keys to watch
  tags?: string[]      // Tags to watch
  patterns?: string[]  // Patterns to watch
  debounce?: number    // Debounce delay in ms (default: 100)
}
```

### Behavior

1. **Listens** to invalidation events from CacheProvider
2. **Filters** events based on your options (OR logic)
3. **Debounces** revalidation requests
4. **Calls** `revalidator.revalidate()` to re-run the loader
5. **Cleans up** timeout on unmount

### Filter Logic

Filters use **OR logic**: the component revalidates if ANY filter matches.

```typescript
useCache({
  tags: ['user'],
  keys: ['myapp:product:123'],
})

// Revalidates when:
// - Any invalidation event has tag 'user', OR
// - Any invalidation event has key 'myapp:product:123'
```

### No Filters

If no filters are provided, revalidates on **all** invalidations:

```typescript
useCache() // Revalidates on every cache invalidation
```

---

## Filtering Strategies

### By Tag (Most Common)

Revalidate when specific tags are invalidated.

```typescript
// Server: Define tags
const productCache = cache.define({
  name: 'product',
  key: (id: string) => id,
  fetch: fetchProduct,
  tags: (id, product) => ['product', `product:${id}`],
})

// Server: Invalidate by tag
await cache.invalidateByTag('product')

// Client: Listen for tag
useCache({ tags: ['product'] })
```

**When to use**: Most common pattern. Tag-based invalidation is flexible and semantic.

---

### By Key (Specific)

Revalidate when a specific cache entry is invalidated.

```typescript
// Server: Invalidate specific key
await cache.invalidate({ key: 'myapp:user:123' })

// Client: Listen for this specific key
useCache({ keys: ['myapp:user:123'] })
```

**When to use**: When component depends on one specific cache entry.

---

### By Pattern (Flexible)

Revalidate when keys matching a pattern are invalidated.

```typescript
// Server: Invalidate pattern
await cache.invalidateByPattern('user:*')

// Client: Listen for pattern
useCache({ patterns: ['user:*'] })
```

**When to use**: When you need flexible matching beyond tags.

---

### Multiple Filters (OR Logic)

Combine filters to revalidate on multiple conditions.

```typescript
useCache({
  tags: ['user', 'profile'],
  keys: ['myapp:session:current'],
  patterns: ['notification:*'],
})

// Revalidates when ANY of these match
```

**When to use**: Component depends on multiple unrelated cache entries.

---

### User-Specific Filtering

Filter invalidations to specific user's data.

```typescript
// app/routes/dashboard.tsx
export default function Dashboard() {
  const { user, stats } = useLoaderData<typeof loader>()

  // Only revalidate for this user's data
  useCache({
    tags: [`user:${user.id}`, 'stats'],
  })

  return <div>...</div>
}
```

---

### Route-Specific Filtering

Different components filter for different data.

```typescript
// app/routes/products.$productId.tsx
export default function ProductDetail() {
  const { product } = useLoaderData<typeof loader>()

  useCache({
    tags: [`product:${product.id}`],
    debounce: 200,
  })

  return <ProductView product={product} />
}

// app/routes/products._index.tsx
export default function ProductList() {
  const { products } = useLoaderData<typeof loader>()

  useCache({
    tags: ['product'], // All products
    debounce: 300,
  })

  return <ProductGrid products={products} />
}
```

---

## Advanced Patterns

### Conditional Revalidation

Only revalidate based on runtime conditions.

```typescript
export default function UserProfile() {
  const { user } = useLoaderData<typeof loader>()
  const isCurrentUser = useIsCurrentUser()

  // Only revalidate if viewing your own profile
  useCache({
    tags: isCurrentUser ? ['user', `user:${user.id}`] : [],
  })

  return <div>...</div>
}
```

---

### Debounced Revalidation

Adjust debounce based on update frequency.

```typescript
// High-frequency updates: longer debounce
useCache({
  tags: ['realtime-metrics'],
  debounce: 500, // Wait 500ms
})

// Low-frequency updates: shorter debounce
useCache({
  tags: ['user-settings'],
  debounce: 100, // Default
})
```

---

### Manual Revalidation

Combine automatic and manual revalidation.

```typescript
import { useRevalidator } from '@remix-run/react'

export default function ProductDetail() {
  const { product } = useLoaderData<typeof loader>()
  const revalidator = useRevalidator()

  // Automatic revalidation
  useCache({ tags: [`product:${product.id}`] })

  // Manual revalidation
  const handleRefresh = () => {
    revalidator.revalidate()
  }

  return (
    <div>
      <ProductView product={product} />
      <button onClick={handleRefresh}>Refresh</button>
    </div>
  )
}
```

---

### Optimistic Updates with Revalidation

Combine optimistic UI with cache revalidation.

```typescript
import { useFetcher } from '@remix-run/react'

export default function ProductList() {
  const { products } = useLoaderData<typeof loader>()
  const fetcher = useFetcher()

  // Revalidate when products change
  useCache({ tags: ['product'] })

  const handleDelete = (productId: string) => {
    // Optimistic update
    fetcher.submit(
      { intent: 'delete', productId },
      { method: 'post' }
    )
  }

  // Show optimistic state
  const displayProducts = fetcher.formData
    ? products.filter(p => p.id !== fetcher.formData.get('productId'))
    : products

  return (
    <div>
      {displayProducts.map(p => (
        <ProductCard
          key={p.id}
          product={p}
          onDelete={handleDelete}
        />
      ))}
    </div>
  )
}
```

---

### Nested Routes with Shared Data

Parent and child routes revalidating together.

```typescript
// app/routes/users.$userId.tsx (Parent)
export default function UserLayout() {
  const { user } = useLoaderData<typeof loader>()

  // Revalidate user data
  useCache({ tags: [`user:${user.id}`] })

  return (
    <div>
      <UserHeader user={user} />
      <Outlet />
    </div>
  )
}

// app/routes/users.$userId.posts.tsx (Child)
export default function UserPosts() {
  const { user } = useLoaderData<typeof loader>()
  const { posts } = useLoaderData<typeof loader>()

  // Revalidate posts when user changes
  useCache({ tags: [`user:${user.id}:posts`] })

  return <PostList posts={posts} />
}
```

---

## Debugging

### Check SSE Connection

1. Open browser DevTools
2. Go to Network tab
3. Filter by "EventStream" or "cache-events"
4. Check connection status

You should see:
- Status: 200
- Type: eventsource
- Initiator: useEventSource

### View SSE Events

In Network tab, click on the cache-events request:
- Messages tab shows all events
- Each event has `event: invalidate` and data

### Debug useCache

Log when revalidation happens:

```typescript
export default function MyComponent() {
  const revalidator = useRevalidator()

  useCache({ tags: ['user'] })

  useEffect(() => {
    if (revalidator.state === 'loading') {
      console.log('Revalidating due to cache invalidation')
    }
  }, [revalidator.state])

  return <div>...</div>
}
```

### Common Issues

**SSE connection not established**:
- Check CacheProvider is in root
- Verify endpoint path matches route
- Check for CORS issues (if API is separate domain)

**Events not received**:
- Verify invalidation is actually happening on server
- Check event is being emitted (use curl to test endpoint)
- Inspect Network tab for actual events

**Revalidation not triggering**:
- Check useCache filters match invalidation tags/keys
- Verify revalidator is working (try manual revalidation)
- Check for JavaScript errors in console

**Too many revalidations**:
- Increase debounce delay
- Tighten filters (be more specific)
- Check for invalidation loops

---

## Performance Considerations

### Debouncing

Adjust debounce based on update frequency:

```typescript
// Frequent updates: higher debounce
useCache({ tags: ['live-data'], debounce: 500 })

// Infrequent updates: lower debounce
useCache({ tags: ['settings'], debounce: 100 })
```

### Filter Specificity

More specific filters = less revalidation:

```typescript
// Less specific - revalidates often
useCache({ tags: ['product'] })

// More specific - revalidates only for this product
useCache({ tags: [`product:${productId}`] })
```

### SSE Connection Limit

Browsers limit concurrent SSE connections (typically 6 per domain).

**Solutions**:
- Use single CacheProvider for whole app (recommended)
- Don't create multiple EventSource connections
- Share connection across tabs (SharedWorker - advanced)

### Revalidation Cost

Each revalidation re-runs the loader:

```typescript
// Expensive loader - use longer debounce
export async function loader({ params }: LoaderFunctionArgs) {
  const [user, posts, comments] = await Promise.all([
    fetchUser(params.userId),
    fetchPosts(params.userId),
    fetchComments(params.userId),
  ])
  return json({ user, posts, comments })
}

// Use longer debounce for expensive loaders
useCache({ tags: ['user'], debounce: 300 })
```

### Memory Considerations

CacheProvider accumulates invalidation events in memory.

**Note**: Current implementation accumulates all events. For production, consider adding a max size:

```typescript
// Potential enhancement (not currently implemented)
<CacheProvider
  endpoint="/api/cache-events"
  maxEvents={100}  // Keep only last 100 events
/>
```

---

## Advanced: Custom Cache Context

Access raw invalidation events (advanced usage):

```typescript
import { useCacheContext } from 'remix-cache/react'

export default function CustomCacheMonitor() {
  const { invalidations } = useCacheContext()

  return (
    <div>
      <h2>Recent Invalidations</h2>
      <ul>
        {invalidations.slice(-10).map((inv, i) => (
          <li key={i}>
            {inv.key || inv.tag || inv.pattern} - {new Date(inv.timestamp).toLocaleTimeString()}
          </li>
        ))}
      </ul>
    </div>
  )
}
```

---

## Complete Example

Full example of real-time cache invalidation:

```typescript
// app/cache.server.ts
import { createCache } from 'remix-cache/server'

export const cache = createCache({
  redis: { host: 'localhost', port: 6379 },
  prefix: 'myapp',
})

export const productCache = cache.define({
  name: 'product',
  key: (id: string) => id,
  fetch: async (id: string) => db.product.findUnique({ where: { id } }),
  ttl: 300,
  tags: (id, product) => ['product', `product:${id}`, `category:${product.categoryId}`],
})

// app/routes/api.cache-events.tsx
import { createSSEHandler } from 'remix-cache/server'
import { cache } from '~/cache.server'

export const loader = createSSEHandler(cache)

// app/root.tsx
import { CacheProvider } from 'remix-cache/react'

export default function App() {
  return (
    <html>
      <body>
        <CacheProvider endpoint="/api/cache-events">
          <Outlet />
        </CacheProvider>
      </body>
    </html>
  )
}

// app/routes/products.$productId.tsx
import { useCache } from 'remix-cache/react'

export async function loader({ params }: LoaderFunctionArgs) {
  const product = await productCache.get(params.productId)
  return json({ product })
}

export async function action({ request, params }: ActionFunctionArgs) {
  const formData = await request.formData()

  // Update product
  const product = await db.product.update({
    where: { id: params.productId },
    data: Object.fromEntries(formData),
  })

  // Invalidate cache - triggers SSE event
  await productCache.delete(params.productId)

  return json({ product })
}

export default function ProductDetail() {
  const { product } = useLoaderData<typeof loader>()

  // Auto-revalidate when this product changes
  useCache({
    tags: [`product:${product.id}`],
    debounce: 200,
  })

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <p>${product.price}</p>
    </div>
  )
}
```

When the action runs:
1. Product is updated in database
2. Cache is invalidated (`productCache.delete()`)
3. SSE event is emitted to all connected clients
4. `useCache` hook receives event
5. Filters match (`product:${id}` tag)
6. After 200ms debounce, calls `revalidator.revalidate()`
7. Loader re-runs
8. Component shows updated product
