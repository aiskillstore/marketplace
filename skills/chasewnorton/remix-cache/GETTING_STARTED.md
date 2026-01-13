# Getting Started with remix-cache

Complete guide to installing and setting up remix-cache in your Remix application.

## Installation

```bash
npm install remix-cache

# Peer dependencies (usually already in Remix projects)
npm install redis @remix-run/react remix-utils
```

## Prerequisites

- Remix application (v2+)
- Redis server (v6+)
- Node.js 18+
- TypeScript (recommended)

## Step 1: Set up Redis

### Local development

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Using Homebrew (macOS)
brew install redis
brew services start redis

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### Production

Use a managed Redis service:
- **AWS**: ElastiCache
- **GCP**: Cloud Memorystore
- **Azure**: Azure Cache for Redis
- **Vercel**: Upstash Redis
- **Self-hosted**: Redis Cluster or Sentinel

## Step 2: Configure environment variables

Create or update `.env`:

```bash
# Required
REDIS_HOST=localhost
REDIS_PORT=6379

# Optional but recommended
REDIS_PASSWORD=your-secure-password
CACHE_PREFIX=myapp
CACHE_DEFAULT_TTL=300

# Environment
NODE_ENV=development
```

## Step 3: Create cache instance

Create `app/cache.server.ts`:

```typescript
import { createCache } from 'remix-cache/server'

// Basic setup
export const cache = createCache({
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379'),
    password: process.env.REDIS_PASSWORD,
  },
  prefix: process.env.CACHE_PREFIX || 'myapp',
})

// Server mode (default) - with local cache
export const cache = createCache({
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379'),
  },
  prefix: 'myapp',
  local: {
    max: 1000,    // Max items in memory
    ttl: 60,      // Local cache TTL in seconds
  },
})

// Serverless mode - Redis only
export const cache = createCache({
  redis: {
    host: process.env.REDIS_HOST!,
    port: parseInt(process.env.REDIS_PORT || '6379'),
  },
  prefix: 'myapp',
  serverless: true, // Disable local cache
})
```

### Full configuration options

```typescript
export const cache = createCache({
  // Required: Redis connection
  redis: {
    host: string
    port: number
    password?: string
    db?: number                    // Redis database number (0-15)
    family?: 4 | 6                 // IPv4 or IPv6
    connectTimeout?: number        // Connection timeout in ms
    maxRetriesPerRequest?: number  // Retry attempts
    enableOfflineQueue?: boolean   // Queue commands when offline
  },

  // Namespace for all cache keys
  prefix: string

  // Optional: Local cache (server mode only)
  local?: {
    max: number      // Max items in memory
    ttl: number      // Default TTL in seconds
  }

  // Optional: Serverless mode
  serverless?: boolean  // Default: false

  // Optional: Circuit breaker
  circuitBreaker?: {
    threshold: number        // Failures before opening circuit
    timeout: number          // ms before trying half-open
    halfOpenRequests: number // Test requests in half-open state
  }

  // Optional: Serialization
  serializer?: {
    serialize: (value: any) => string
    deserialize: <T>(value: string) => T
  }
})
```

## Step 4: Define your first cache

Add to `app/cache.server.ts`:

```typescript
// Simple cache definition
export const userCache = cache.define({
  name: 'user',
  key: (userId: string) => userId,
  fetch: async (userId: string) => {
    return db.user.findUnique({ where: { id: userId } })
  },
  ttl: 300, // 5 minutes
})
```

### Cache definition options

```typescript
const myCache = cache.define({
  // Required: Unique name for this cache
  name: string

  // Required: Generate cache key from arguments
  key: (...args: TArgs) => string

  // Optional: Fetch function for cache misses
  fetch?: (...args: TArgs) => Promise<TData>

  // Optional: TTL in seconds (number or function)
  ttl?: number | ((...args: TArgs, data: TData) => number)

  // Optional: Stale-while-revalidate period in seconds
  staleWhileRevalidate?: number

  // Optional: Enable sliding window TTL
  slidingWindow?: boolean

  // Optional: Generate tags for invalidation
  tags?: (...args: TArgs, data: TData) => string[]

  // Optional: Cascade invalidation to other keys
  invalidate?: (...args: TArgs, data: TData) => string[]

  // Optional: Enable request deduplication
  dedupe?: boolean  // Default: true
})
```

## Step 5: Use in loaders

```typescript
// app/routes/users.$userId.tsx
import { json, type LoaderFunctionArgs } from '@remix-run/node'
import { userCache } from '~/cache.server'

export async function loader({ params }: LoaderFunctionArgs) {
  // Automatically fetches from cache or database
  const user = await userCache.get(params.userId)

  if (!user) {
    throw new Response('Not Found', { status: 404 })
  }

  return json({ user })
}
```

## Step 6: Invalidate in actions

```typescript
// app/routes/users.$userId.edit.tsx
import { json, type ActionFunctionArgs } from '@remix-run/node'
import { cache, userCache } from '~/cache.server'

export async function action({ request, params }: ActionFunctionArgs) {
  const formData = await request.formData()

  // Update database
  const user = await db.user.update({
    where: { id: params.userId },
    data: Object.fromEntries(formData),
  })

  // Invalidate cache
  await cache.invalidate({ key: `myapp:user:${params.userId}` })
  // Or using cache definition
  await userCache.delete(params.userId)

  return json({ user })
}
```

## Step 7: Set up real-time invalidation (optional)

### 7.1: Create SSE endpoint

Create `app/routes/api.cache-events.tsx`:

```typescript
import { createSSEHandler } from 'remix-cache/server'
import { cache } from '~/cache.server'

export const loader = createSSEHandler(cache)
```

### 7.2: Wrap app with CacheProvider

Update `app/root.tsx`:

```typescript
import { CacheProvider } from 'remix-cache/react'
import { Outlet } from '@remix-run/react'

export default function App() {
  return (
    <html lang="en">
      <head>
        <Meta />
        <Links />
      </head>
      <body>
        <CacheProvider endpoint="/api/cache-events">
          <Outlet />
        </CacheProvider>
        <Scripts />
      </body>
    </html>
  )
}
```

### 7.3: Use useCache hook

```typescript
// app/routes/users.$userId.tsx
import { useCache } from 'remix-cache/react'
import { useLoaderData } from '@remix-run/react'

export default function UserProfile() {
  const { user } = useLoaderData<typeof loader>()

  // Auto-revalidate when user cache is invalidated
  useCache({ tags: ['user'] })

  return <div>{user.name}</div>
}
```

## Step 8: Monitor cache behavior (optional)

Add event listeners in `app/cache.server.ts`:

```typescript
// Log cache hits and misses
cache.on('hit', (event) => {
  console.log(`Cache hit: ${event.key} (${event.source}) - ${event.latency}ms`)
})

cache.on('miss', (event) => {
  console.log(`Cache miss: ${event.key} - ${event.latency}ms`)
})

// Track errors
cache.on('error', (event) => {
  console.error('Cache error:', event.error)
  // Send to monitoring service
  if (process.env.NODE_ENV === 'production') {
    // sendToSentry(event.error)
  }
})

// Track invalidations
cache.on('invalidate', (event) => {
  console.log('Cache invalidated:', {
    key: event.key,
    tag: event.tag,
    pattern: event.pattern,
  })
})
```

## Verification checklist

- [ ] Redis is running and accessible
- [ ] Environment variables are set
- [ ] Cache instance created successfully
- [ ] At least one cache definition exists
- [ ] Cache is used in a loader
- [ ] Cache invalidation works in an action
- [ ] SSE endpoint returns events (optional)
- [ ] React components revalidate (optional)
- [ ] Event listeners are set up (optional)

## Testing your setup

Create a simple test route `app/routes/test-cache.tsx`:

```typescript
import { json, type ActionFunctionArgs, type LoaderFunctionArgs } from '@remix-run/node'
import { Form, useLoaderData } from '@remix-run/react'
import { cache } from '~/cache.server'

const testCache = cache.define({
  name: 'test',
  key: (key: string) => key,
  fetch: async (key: string) => ({
    key,
    timestamp: Date.now(),
    random: Math.random(),
  }),
  ttl: 60,
})

export async function loader({ request }: LoaderFunctionArgs) {
  const value = await testCache.get('demo')
  return json({ value })
}

export async function action({ request }: ActionFunctionArgs) {
  await testCache.delete('demo')
  return json({ success: true })
}

export default function TestCache() {
  const { value } = useLoaderData<typeof loader>()

  return (
    <div>
      <h1>Cache Test</h1>
      <pre>{JSON.stringify(value, null, 2)}</pre>
      <Form method="post">
        <button type="submit">Invalidate Cache</button>
      </Form>
      <p>
        Refresh the page to see cached value (same timestamp).
        Click "Invalidate Cache" then refresh to see new value.
      </p>
    </div>
  )
}
```

Visit `/test-cache`:
1. Note the timestamp
2. Refresh - timestamp should be the same (cached)
3. Click "Invalidate Cache"
4. Refresh - timestamp should be new (cache was cleared)

## Next steps

- **[API_REFERENCE.md](API_REFERENCE.md)** - Learn all available methods and options
- **[PATTERNS.md](PATTERNS.md)** - Discover common caching patterns
- **[REACT_INTEGRATION.md](REACT_INTEGRATION.md)** - Deep dive into SSE and React hooks
- **[EXAMPLES.md](EXAMPLES.md)** - See real-world examples
- **[TESTING.md](TESTING.md)** - Learn how to test your cache

## Common setup issues

### Redis connection refused

```bash
# Verify Redis is running
redis-cli ping

# Check logs
docker logs <redis-container-id>

# Verify port is open
lsof -i :6379
```

### TypeScript errors

Ensure you have proper types:

```bash
npm install --save-dev @types/node
```

Add to `tsconfig.json`:

```json
{
  "compilerOptions": {
    "types": ["node"]
  }
}
```

### Import errors

Ensure you're importing from the correct path:

```typescript
// Server-side
import { createCache } from 'remix-cache/server'

// Client-side
import { CacheProvider, useCache } from 'remix-cache/react'
```

### Environment variables not loading

In Remix, ensure you're loading them correctly:

```typescript
// For server-side only
process.env.REDIS_HOST

// For client-side, use loader data
export async function loader() {
  return json({
    publicVar: process.env.PUBLIC_VAR
  })
}
```
