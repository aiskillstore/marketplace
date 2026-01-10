# API Reference

Complete reference for all remix-cache APIs.

## Table of Contents

- [Cache Creation](#cache-creation)
- [Cache Definitions](#cache-definitions)
- [Cache Operations](#cache-operations)
- [Invalidation](#invalidation)
- [Events](#events)
- [React Integration](#react-integration)
- [Type Definitions](#type-definitions)

---

## Cache Creation

### `createCache(config)`

Creates a new cache instance.

```typescript
import { createCache } from 'remix-cache/server'

const cache = createCache(config)
```

#### Parameters

```typescript
interface CacheConfig {
  redis: RedisOptions
  prefix: string
  local?: LocalCacheOptions
  serverless?: boolean
  circuitBreaker?: CircuitBreakerOptions
  serializer?: Serializer
}
```

**`redis`** (required): Redis connection configuration
```typescript
interface RedisOptions {
  host: string                   // Redis server host
  port: number                   // Redis server port
  password?: string              // Authentication password
  db?: number                    // Database number (0-15)
  family?: 4 | 6                 // IPv4 or IPv6
  connectTimeout?: number        // Connection timeout (ms)
  maxRetriesPerRequest?: number  // Max retry attempts
  enableOfflineQueue?: boolean   // Queue commands when offline
}
```

**`prefix`** (required): Namespace for all cache keys
- Type: `string`
- Example: `'myapp'`
- Keys will be formatted as: `prefix:cacheName:key`

**`local`** (optional): Local in-memory cache configuration (server mode only)
```typescript
interface LocalCacheOptions {
  max: number  // Maximum number of items
  ttl: number  // Default TTL in seconds
}
```

**`serverless`** (optional): Enable serverless mode
- Type: `boolean`
- Default: `false`
- When `true`, disables local cache and uses versioned Redis keys

**`circuitBreaker`** (optional): Circuit breaker configuration
```typescript
interface CircuitBreakerOptions {
  threshold: number        // Failures before opening circuit
  timeout: number          // ms before attempting half-open
  halfOpenRequests: number // Test requests in half-open state
}
```
- Default: `{ threshold: 5, timeout: 30000, halfOpenRequests: 3 }`

**`serializer`** (optional): Custom serialization
```typescript
interface Serializer {
  serialize: (value: any) => string
  deserialize: <T>(value: string) => T
}
```
- Default: JSON serialization

#### Returns

`Cache` instance with methods for defining caches and performing operations.

#### Example

```typescript
// Basic setup
const cache = createCache({
  redis: { host: 'localhost', port: 6379 },
  prefix: 'myapp',
})

// Server mode with local cache
const cache = createCache({
  redis: { host: 'localhost', port: 6379 },
  prefix: 'myapp',
  local: { max: 1000, ttl: 60 },
})

// Serverless mode
const cache = createCache({
  redis: { host: process.env.REDIS_HOST!, port: 6379 },
  prefix: 'myapp',
  serverless: true,
})
```

---

## Cache Definitions

### `cache.define(definition)`

Creates a type-safe cache definition with automatic key generation.

```typescript
const myCache = cache.define(definition)
```

#### Parameters

```typescript
interface CacheDefinition<TArgs, TData> {
  name: string
  key: (...args: TArgs) => string
  fetch?: (...args: TArgs) => Promise<TData>
  ttl?: number | ((...args: TArgs, data: TData) => number)
  staleWhileRevalidate?: number
  slidingWindow?: boolean
  tags?: (...args: TArgs, data: TData) => string[]
  invalidate?: (...args: TArgs, data: TData) => string[]
  dedupe?: boolean
}
```

**`name`** (required): Unique identifier for this cache
- Type: `string`
- Must be unique across all cache definitions
- Used in key generation: `prefix:name:key`

**`key`** (required): Function to generate cache key from arguments
- Type: `(...args: TArgs) => string`
- Receives same arguments as `get()`, `set()`, etc.
- Should return a stable, unique string for the cache entry

**`fetch`** (optional): Function to fetch data on cache miss
- Type: `(...args: TArgs) => Promise<TData>`
- Called automatically when cache misses
- Also used for background revalidation (stale-while-revalidate)
- If not provided, `get()` returns `null` on miss

**`ttl`** (optional): Time-to-live in seconds
- Type: `number | ((...args: TArgs, data: TData) => number)`
- Can be static number or dynamic function
- Function receives fetch arguments and fetched data
- Default: No expiration (cache forever)

**`staleWhileRevalidate`** (optional): Serve stale data while revalidating
- Type: `number` (seconds)
- After TTL expires, serve stale data for this duration
- Triggers background revalidation
- Requires `fetch` to be defined

**`slidingWindow`** (optional): Reset TTL on each access
- Type: `boolean`
- Default: `false`
- When `true`, each `get()` resets the TTL
- Useful for session-like caches

**`tags`** (optional): Generate tags for group invalidation
- Type: `(...args: TArgs, data: TData) => string[]`
- Returns array of tags to associate with this cache entry
- Used with `cache.invalidateByTag()`

**`invalidate`** (optional): Cascade invalidation to other keys
- Type: `(...args: TArgs, data: TData) => string[]`
- Returns array of additional keys to invalidate
- Called when this cache entry is invalidated

**`dedupe`** (optional): Enable request deduplication
- Type: `boolean`
- Default: `true`
- Deduplicates concurrent requests for the same cache key
- Prevents cache stampede

#### Returns

`CacheDefinitionInstance<TArgs, TData>` with methods:
- `get(...args)`: Get value
- `set(...args, value)`: Set value
- `delete(...args)`: Delete value
- `getMany(argsArray)`: Get multiple values
- `setMany(entries)`: Set multiple values
- `deleteMany(argsArray)`: Delete multiple values
- `seed(entries)`: Seed cache with initial values

#### Examples

```typescript
// Simple cache
const userCache = cache.define({
  name: 'user',
  key: (userId: string) => userId,
  fetch: async (userId: string) => db.user.findUnique({ where: { id: userId } }),
  ttl: 300,
})

// Multi-argument key
const productCache = cache.define({
  name: 'product',
  key: (productId: string, locale: string = 'en') => `${productId}:${locale}`,
  fetch: async (productId: string, locale = 'en') => {
    return db.product.findUnique({ where: { id: productId } })
  },
  ttl: 3600,
})

// With tags and cascading
const postCache = cache.define({
  name: 'post',
  key: (postId: string) => postId,
  fetch: fetchPost,
  ttl: 600,
  tags: (postId, post) => ['post', `post:${postId}`, `author:${post.authorId}`],
  invalidate: (postId, post) => [`user:${post.authorId}:posts`],
})

// Stale-while-revalidate
const apiCache = cache.define({
  name: 'api',
  key: (endpoint: string) => endpoint,
  fetch: async (endpoint) => (await fetch(endpoint)).json(),
  ttl: 300,
  staleWhileRevalidate: 600,
})

// Sliding window session
const sessionCache = cache.define({
  name: 'session',
  key: (sessionId: string) => sessionId,
  fetch: fetchSession,
  ttl: 1800,
  slidingWindow: true,
})

// Conditional TTL
const dataCache = cache.define({
  name: 'data',
  key: (id: string) => id,
  fetch: fetchData,
  ttl: (id, data) => data.isPremium ? 3600 : 300,
})
```

---

## Cache Operations

### `cacheDefinition.get(...args)`

Retrieves a value from cache or fetches it if missing.

```typescript
const value = await myCache.get(...args)
```

#### Behavior

1. Check local cache (if server mode)
2. Check Redis cache
3. If miss and `fetch` defined, call fetch function
4. Store fetched value in cache
5. Return value or `null`

#### Returns

- `Promise<TData | null>`
- Returns cached/fetched data or `null` if not found

#### Example

```typescript
const user = await userCache.get('user-123')
const product = await productCache.get('prod-456', 'es')
```

---

### `cacheDefinition.set(...args, value)`

Stores a value in the cache.

```typescript
await myCache.set(...args, value)
```

#### Parameters

- `...args`: Cache key arguments (same as `key()` function)
- `value`: Data to cache

#### Behavior

1. Generate cache key from args
2. Serialize value
3. Store in local cache (if server mode)
4. Store in Redis with TTL
5. Track tags/patterns if configured
6. Emit `set` event

#### Returns

- `Promise<void>`

#### Example

```typescript
await userCache.set('user-123', { id: '123', name: 'Alice' })
await productCache.set('prod-456', 'es', productData)
```

---

### `cacheDefinition.delete(...args)`

Removes a value from the cache.

```typescript
await myCache.delete(...args)
```

#### Parameters

- `...args`: Cache key arguments

#### Behavior

1. Generate cache key from args
2. Remove from local cache (if server mode)
3. Remove from Redis
4. Remove from pattern/tag tracking
5. Trigger cascading invalidation if configured
6. Emit `invalidate` event
7. Publish invalidation event (for SSE)

#### Returns

- `Promise<void>`

#### Example

```typescript
await userCache.delete('user-123')
await productCache.delete('prod-456', 'es')
```

---

### `cacheDefinition.getMany(argsArray)`

Retrieves multiple values at once.

```typescript
const values = await myCache.getMany(argsArray)
```

#### Parameters

```typescript
argsArray: TArgs[]
```

Array of argument tuples, where each tuple is the arguments for one cache entry.

#### Returns

```typescript
Promise<(TData | null)[]>
```

Array of values in the same order as input. `null` for missing entries.

#### Example

```typescript
const users = await userCache.getMany([['1'], ['2'], ['3']])
// Returns: [user1, user2, null] if user 3 doesn't exist

const products = await productCache.getMany([
  ['prod-1', 'en'],
  ['prod-2', 'es'],
])
```

---

### `cacheDefinition.setMany(entries)`

Stores multiple values at once.

```typescript
await myCache.setMany(entries)
```

#### Parameters

```typescript
interface CacheEntry<TArgs, TData> {
  args: TArgs
  value: TData
}

entries: CacheEntry<TArgs, TData>[]
```

#### Behavior

Same as `set()` but batched:
1. Stores all values in local cache
2. Uses Redis pipeline for atomic batch write
3. Tracks all tags/patterns
4. Emits single `set` event with all keys

#### Returns

- `Promise<void>`

#### Example

```typescript
await userCache.setMany([
  { args: ['1'], value: user1 },
  { args: ['2'], value: user2 },
  { args: ['3'], value: user3 },
])

await productCache.setMany([
  { args: ['prod-1', 'en'], value: product1En },
  { args: ['prod-1', 'es'], value: product1Es },
])
```

---

### `cacheDefinition.deleteMany(argsArray)`

Removes multiple values at once.

```typescript
await myCache.deleteMany(argsArray)
```

#### Parameters

```typescript
argsArray: TArgs[]
```

#### Behavior

Same as `delete()` but batched using Redis pipeline.

#### Returns

- `Promise<void>`

#### Example

```typescript
await userCache.deleteMany([['1'], ['2'], ['3']])
await productCache.deleteMany([['prod-1', 'en'], ['prod-1', 'es']])
```

---

### `cacheDefinition.seed(entries)`

Pre-populates cache with initial values. Alias for `setMany()`.

```typescript
await myCache.seed(entries)
```

Useful for warming cache on application startup.

#### Example

```typescript
// Warm cache on startup
const popularProducts = await db.product.findMany({
  where: { featured: true }
})

await productCache.seed(
  popularProducts.map(p => ({
    args: [p.id, 'en'],
    value: p
  }))
)
```

---

## Invalidation

### `cache.invalidate(options)`

Invalidates a specific cache entry by key.

```typescript
await cache.invalidate({ key: 'myapp:user:123' })
```

#### Parameters

```typescript
interface InvalidateOptions {
  key: string  // Full cache key (prefix:name:key)
}
```

#### Behavior

1. Remove from local cache
2. Remove from Redis
3. Remove from pattern/tag tracking
4. Trigger cascading invalidation
5. Emit `invalidate` event
6. Publish SSE invalidation event

#### Returns

- `Promise<void>`

---

### `cache.invalidateByTag(tag)`

Invalidates all cache entries with a specific tag.

```typescript
await cache.invalidateByTag('product')
```

#### Parameters

- `tag`: Tag string to match

#### Behavior

1. Find all keys with this tag
2. Invalidate each key (same as `invalidate()`)
3. Publish SSE event with tag

#### Returns

- `Promise<void>`

#### Example

```typescript
// Invalidate all products
await cache.invalidateByTag('product')

// Invalidate all caches for a user
await cache.invalidateByTag(`user:${userId}`)
```

---

### `cache.invalidateByPattern(pattern)`

Invalidates all cache entries matching a glob pattern.

```typescript
await cache.invalidateByPattern('user:*')
```

#### Parameters

- `pattern`: Glob pattern to match (supports `*` and `?`)

#### Behavior

1. Find all keys matching pattern in the cache name namespace
2. Invalidate each matched key
3. Publish SSE event with pattern

#### Returns

- `Promise<void>`

#### Pattern syntax

- `*`: Matches any characters except `:`
- `?`: Matches single character
- Patterns match within the cache name, not the full key

#### Example

```typescript
// Invalidate all users
await cache.invalidateByPattern('user:*')

// Invalidate specific pattern
await cache.invalidateByPattern('user:admin-*')
await cache.invalidateByPattern('session:2024-??-??')
```

---

### `cache.close()`

Closes all connections and cleans up resources.

```typescript
await cache.close()
```

#### Behavior

1. Closes Redis connection
2. Clears local cache
3. Removes all event listeners

**Important**: Always call in test `afterEach()` hooks.

#### Returns

- `Promise<void>`

#### Example

```typescript
// In tests
afterEach(async () => {
  await cache.close()
})

// On application shutdown
process.on('SIGTERM', async () => {
  await cache.close()
  process.exit(0)
})
```

---

## Events

The cache instance is an EventEmitter that emits various events for monitoring.

### Event Types

```typescript
type CacheEvent =
  | 'hit'        // Cache hit
  | 'miss'       // Cache miss
  | 'set'        // Value set
  | 'invalidate' // Value invalidated
  | 'error'      // Error occurred
```

### `cache.on(event, handler)`

Subscribe to cache events.

```typescript
cache.on('hit', (event) => {
  console.log('Cache hit:', event)
})
```

### Event Payloads

#### `hit` event

```typescript
interface CacheHitEvent {
  key: string
  latency: number        // ms
  source: 'local' | 'redis'
  timestamp: number
}
```

#### `miss` event

```typescript
interface CacheMissEvent {
  key: string
  latency: number  // ms
  timestamp: number
}
```

#### `set` event

```typescript
interface CacheSetEvent {
  key?: string       // Single key
  keys?: string[]    // Multiple keys (bulk operation)
  timestamp: number
}
```

#### `invalidate` event

```typescript
interface CacheInvalidateEvent {
  key?: string
  keys?: string[]
  tag?: string
  tags?: string[]
  pattern?: string
  timestamp: number
}
```

#### `error` event

```typescript
interface CacheErrorEvent {
  error: Error
  key?: string
  timestamp: number
}
```

### Example: Monitoring

```typescript
// Track hit rate
let hits = 0
let misses = 0

cache.on('hit', () => hits++)
cache.on('miss', () => misses++)

setInterval(() => {
  const total = hits + misses
  const hitRate = total > 0 ? (hits / total) * 100 : 0
  console.log(`Cache hit rate: ${hitRate.toFixed(2)}%`)
}, 60000)

// Track errors
cache.on('error', (event) => {
  console.error('Cache error:', event.error)
  sendToSentry(event.error)
})

// Track invalidations
cache.on('invalidate', (event) => {
  console.log('Invalidated:', {
    key: event.key,
    tag: event.tag,
    pattern: event.pattern,
  })
})
```

---

## React Integration

### `<CacheProvider>`

React context provider that connects to SSE endpoint.

```typescript
import { CacheProvider } from 'remix-cache/react'

<CacheProvider endpoint="/api/cache-events">
  {children}
</CacheProvider>
```

#### Props

```typescript
interface CacheProviderProps {
  children: ReactNode
  endpoint?: string  // Default: '/api/cache-events'
}
```

---

### `useCache(options)`

React hook for automatic revalidation on cache invalidation.

```typescript
import { useCache } from 'remix-cache/react'

useCache(options)
```

#### Parameters

```typescript
interface UseCacheOptions {
  keys?: string[]      // Specific cache keys to watch
  tags?: string[]      // Tags to watch
  patterns?: string[]  // Patterns to watch
  debounce?: number    // Debounce ms (default: 100)
}
```

All filters use OR logic: revalidates if ANY filter matches.

If no filters provided, revalidates on all invalidations.

#### Behavior

1. Listens to invalidation events from CacheProvider
2. Filters events based on options
3. Debounces revalidation requests
4. Calls `revalidator.revalidate()` from Remix

#### Example

```typescript
// Revalidate on specific tags
useCache({ tags: ['user', 'profile'] })

// Revalidate on specific keys
useCache({ keys: ['myapp:user:123'] })

// Revalidate on patterns
useCache({ patterns: ['user:*', 'session:*'] })

// Combined (OR logic)
useCache({
  tags: ['user'],
  keys: ['myapp:user:123'],
  debounce: 300
})

// Revalidate on all invalidations
useCache()
```

---

### `useCacheContext()`

Access raw cache context (advanced usage).

```typescript
import { useCacheContext } from 'remix-cache/react'

const { invalidations } = useCacheContext()
```

#### Returns

```typescript
interface CacheContextValue {
  invalidations: InvalidationEvent[]
}
```

---

### `createSSEHandler(cache)`

Creates an SSE endpoint handler for Remix.

```typescript
import { createSSEHandler } from 'remix-cache/server'

export const loader = createSSEHandler(cache)
```

#### Parameters

- `cache`: Cache instance

#### Returns

- Remix loader function that handles SSE connections

#### Example

```typescript
// app/routes/api.cache-events.tsx
import { createSSEHandler } from 'remix-cache/server'
import { cache } from '~/cache.server'

export const loader = createSSEHandler(cache)
```

---

## Type Definitions

### Core Types

```typescript
// Cache instance
interface Cache {
  define<TArgs extends any[], TData>(
    definition: CacheDefinition<TArgs, TData>
  ): CacheDefinitionInstance<TArgs, TData>

  invalidate(options: { key: string }): Promise<void>
  invalidateByTag(tag: string): Promise<void>
  invalidateByPattern(pattern: string): Promise<void>
  close(): Promise<void>

  on(event: 'hit', handler: (event: CacheHitEvent) => void): void
  on(event: 'miss', handler: (event: CacheMissEvent) => void): void
  on(event: 'set', handler: (event: CacheSetEvent) => void): void
  on(event: 'invalidate', handler: (event: CacheInvalidateEvent) => void): void
  on(event: 'error', handler: (event: CacheErrorEvent) => void): void

  off(event: string, handler: Function): void
}

// Cache definition instance
interface CacheDefinitionInstance<TArgs extends any[], TData> {
  get(...args: TArgs): Promise<TData | null>
  set(...args: [...TArgs, TData]): Promise<void>
  delete(...args: TArgs): Promise<void>
  getMany(argsArray: TArgs[]): Promise<(TData | null)[]>
  setMany(entries: CacheEntry<TArgs, TData>[]): Promise<void>
  deleteMany(argsArray: TArgs[]): Promise<void>
  seed(entries: CacheEntry<TArgs, TData>[]): Promise<void>
}
```

### Location in codebase

Type definitions are in `src/types/`:
- `cache.ts`: Core cache types
- `definition.ts`: Cache definition types
- `events.ts`: Event types
