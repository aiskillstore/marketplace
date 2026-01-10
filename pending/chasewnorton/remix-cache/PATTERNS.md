# Caching Patterns and Best Practices

Common patterns, strategies, and best practices for using remix-cache effectively.

## Table of Contents

- [Caching Strategies](#caching-strategies)
- [TTL Strategies](#ttl-strategies)
- [Invalidation Patterns](#invalidation-patterns)
- [Key Design](#key-design)
- [Tag Strategy](#tag-strategy)
- [Resilience](#resilience)
- [Performance Optimization](#performance-optimization)
- [Security Considerations](#security-considerations)

---

## Caching Strategies

### 1. Cache-Aside (Lazy Loading)

Most common pattern: check cache first, fetch on miss, then cache the result.

```typescript
const userCache = cache.define({
  name: 'user',
  key: (userId: string) => userId,
  fetch: async (userId: string) => {
    return db.user.findUnique({ where: { id: userId } })
  },
  ttl: 300,
})

export async function loader({ params }: LoaderFunctionArgs) {
  // Automatically does cache-aside
  const user = await userCache.get(params.userId)
  return json({ user })
}
```

**When to use**: Default choice for most read-heavy operations.

**Pros**:
- Simple
- Only caches what's actually requested
- Handles cache failures gracefully

**Cons**:
- Initial request is slow (cache miss)
- Potential for cache stampede

---

### 2. Write-Through

Update cache immediately when data changes.

```typescript
export async function action({ request, params }: ActionFunctionArgs) {
  const formData = await request.formData()

  // Update database
  const user = await db.user.update({
    where: { id: params.userId },
    data: Object.fromEntries(formData),
  })

  // Update cache immediately
  await userCache.set(params.userId, user)

  return json({ user })
}
```

**When to use**: When you want cache to always be fresh after updates.

**Pros**:
- Cache is always consistent with database
- Next read is fast (cache hit)

**Cons**:
- Write latency increased
- Wastes cache space if data not read again

---

### 3. Write-Behind (Invalidate on Write)

Invalidate cache when data changes, fetch fresh on next read.

```typescript
export async function action({ request, params }: ActionFunctionArgs) {
  const formData = await request.formData()

  // Update database
  const user = await db.user.update({
    where: { id: params.userId },
    data: Object.fromEntries(formData),
  })

  // Invalidate cache - next read will fetch fresh
  await userCache.delete(params.userId)

  return json({ user })
}
```

**When to use**: When writes are more frequent than reads, or cache TTL is short.

**Pros**:
- Fast writes
- No stale data after invalidation
- Simpler than write-through

**Cons**:
- Next read is slow (cache miss)

---

### 4. Read-Through with Warming

Pre-populate cache with frequently accessed data.

```typescript
// On application startup
async function warmCache() {
  const popularProducts = await db.product.findMany({
    where: { featured: true },
    take: 100,
  })

  await productCache.seed(
    popularProducts.map(p => ({
      args: [p.id],
      value: p,
    }))
  )
}

// Call on startup
warmCache().catch(console.error)
```

**When to use**: When you know which data will be accessed frequently.

**Pros**:
- Fast initial requests
- Prevents cache stampede on popular items

**Cons**:
- Wastes cache space on unpopular items
- Requires knowing access patterns

---

### 5. Stale-While-Revalidate

Serve stale data immediately while fetching fresh data in background.

```typescript
const productCache = cache.define({
  name: 'product',
  key: (id: string) => id,
  fetch: fetchProduct,
  ttl: 300,                    // Fresh for 5 minutes
  staleWhileRevalidate: 1800,  // Serve stale for 30 minutes
})

// First request: fetches from DB (slow)
await productCache.get('123')

// After 5 minutes: returns stale immediately, fetches in background
await productCache.get('123')  // Fast! Returns stale data

// Next request: returns fresh data
await productCache.get('123')  // Fast! Returns updated data
```

**When to use**: When freshness is important but response time is critical.

**Pros**:
- Fast responses (no waiting for fetch)
- Eventually consistent
- Graceful degradation

**Cons**:
- Users may see slightly stale data
- Background fetch still consumes resources

---

## TTL Strategies

### Static TTL

Fixed expiration time for all entries.

```typescript
const userCache = cache.define({
  name: 'user',
  key: (id: string) => id,
  fetch: fetchUser,
  ttl: 300, // 5 minutes for everyone
})
```

**Guidelines**:
- Static content: 1 hour - 24 hours
- User data: 5-15 minutes
- Product catalog: 15-60 minutes
- API responses: 1-5 minutes
- Configuration: 1-24 hours

---

### Conditional TTL

Dynamic TTL based on data characteristics.

```typescript
const apiCache = cache.define({
  name: 'api',
  key: (endpoint: string) => endpoint,
  fetch: fetchFromAPI,
  ttl: (endpoint, data) => {
    // Cache errors for shorter time
    if (data.error) return 60

    // Cache successful responses longer
    if (data.cached_until) {
      const secondsUntil = (data.cached_until - Date.now()) / 1000
      return Math.max(60, secondsUntil)
    }

    return 300
  },
})
```

**When to use**: When different data has different freshness requirements.

---

### Sliding Window TTL

Reset TTL on each access (session-like behavior).

```typescript
const sessionCache = cache.define({
  name: 'session',
  key: (sessionId: string) => sessionId,
  fetch: fetchSession,
  ttl: 1800,           // 30 minutes
  slidingWindow: true,  // Reset TTL on each access
})

// User active: TTL keeps resetting
await sessionCache.get('session-123')  // TTL reset to 30 min

// User inactive: TTL expires after 30 min of no access
```

**When to use**: Sessions, temporary tokens, rate limiting.

**Warning**: High-traffic keys will never expire. Consider max lifetime.

---

### No TTL (Manual Expiration)

Cache forever, invalidate manually.

```typescript
const configCache = cache.define({
  name: 'config',
  key: () => 'global',
  fetch: fetchConfig,
  // No TTL - cache forever
})

// Invalidate when config changes
export async function updateConfig(newConfig: Config) {
  await db.config.update({ data: newConfig })
  await configCache.delete() // Manual invalidation
}
```

**When to use**: Data that rarely changes and is expensive to fetch.

---

## Invalidation Patterns

### 1. Direct Key Invalidation

Invalidate specific cache entry.

```typescript
// After updating user
await cache.invalidate({ key: 'myapp:user:123' })

// Or using cache definition
await userCache.delete('123')
```

**When to use**: When you know exactly which cache entry changed.

---

### 2. Tag-Based Invalidation

Group related cache entries for coordinated invalidation.

```typescript
const productCache = cache.define({
  name: 'product',
  key: (id: string) => id,
  fetch: fetchProduct,
  tags: (id, product) => [
    'product',
    `product:${id}`,
    `category:${product.categoryId}`,
    `brand:${product.brandId}`,
  ],
})

// Invalidate all products
await cache.invalidateByTag('product')

// Invalidate all products in a category
await cache.invalidateByTag(`category:${categoryId}`)

// Invalidate all products from a brand
await cache.invalidateByTag(`brand:${brandId}`)
```

**When to use**: When changes affect multiple related cache entries.

---

### 3. Pattern-Based Invalidation

Invalidate using glob patterns.

```typescript
// Invalidate all users
await cache.invalidateByPattern('user:*')

// Invalidate admin users
await cache.invalidateByPattern('user:admin-*')

// Invalidate by date
await cache.invalidateByPattern('session:2024-01-*')
```

**When to use**: When you need to invalidate by naming convention.

---

### 4. Cascading Invalidation

Automatically invalidate dependent cache entries.

```typescript
const postCache = cache.define({
  name: 'post',
  key: (id: string) => id,
  fetch: fetchPost,
  invalidate: (id, post) => [
    `user:${post.authorId}:posts`,  // Invalidate author's post list
    `category:${post.categoryId}`,  // Invalidate category page
  ],
})

// Invalidating a post also invalidates related caches
await postCache.delete('post-123')
```

**When to use**: When data has clear dependencies.

---

### 5. Time-Based Invalidation

Invalidate at specific times (combine with external scheduler).

```typescript
// In a cron job or scheduled function
export async function invalidateOldData() {
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)

  // Invalidate old analytics
  await cache.invalidateByPattern(`analytics:${yesterday.toISOString().split('T')[0]}:*`)
}
```

**When to use**: Daily aggregations, scheduled content updates.

---

## Key Design

### Hierarchical Keys

Use `:` separators for hierarchy.

```typescript
// Good - hierarchical structure
'user:123'
'user:123:profile'
'user:123:posts'
'user:123:posts:456'

// Allows pattern invalidation
await cache.invalidateByPattern('user:123:*')
```

---

### Stable Keys

Ensure keys don't change unless semantics change.

```typescript
// Good - stable
key: (userId: string) => userId

// Bad - changes every request
key: (userId: string) => `${userId}:${Date.now()}`

// Good - locale included in key
key: (productId: string, locale: string) => `${productId}:${locale}`
```

---

### Normalized Keys

Normalize input before generating keys.

```typescript
// Good - normalized
key: (email: string) => email.toLowerCase().trim()

// Good - sorted arrays
key: (tags: string[]) => tags.sort().join(',')

// Good - JSON for complex keys
key: (filters: Filter) => JSON.stringify(filters, Object.keys(filters).sort())
```

---

### Avoid Sensitive Data in Keys

Keys are logged and visible in monitoring.

```typescript
// Bad - password in key
key: (username: string, password: string) => `${username}:${password}`

// Good - use hash
key: (username: string, passwordHash: string) => `${username}:${passwordHash.slice(0, 8)}`

// Better - don't include password at all
key: (sessionId: string) => sessionId
```

---

## Tag Strategy

### Hierarchical Tags

Use tags at multiple levels of granularity.

```typescript
tags: (productId, product) => [
  'product',                      // All products
  `product:${productId}`,         // Specific product
  `category:${product.categoryId}`, // Category
  `brand:${product.brandId}`,     // Brand
  `price:${product.priceRange}`,  // Price range
]

// Invalidate at any level
await cache.invalidateByTag('product')           // All products
await cache.invalidateByTag('category:electronics') // Category
await cache.invalidateByTag('brand:apple')       // Brand
```

---

### Relationship Tags

Tag cache entries by their relationships.

```typescript
// User cache
const userCache = cache.define({
  name: 'user',
  key: (id: string) => id,
  tags: (id, user) => [
    'user',
    `user:${id}`,
    `org:${user.organizationId}`,  // Org relationship
    `role:${user.role}`,           // Role relationship
  ],
})

// When org changes, invalidate all users in org
await cache.invalidateByTag(`org:${orgId}`)
```

---

### State-Based Tags

Tag by data state.

```typescript
tags: (orderId, order) => [
  'order',
  `order:${orderId}`,
  `order:status:${order.status}`,  // Status tag
  `order:user:${order.userId}`,
]

// Invalidate all pending orders
await cache.invalidateByTag('order:status:pending')
```

---

## Resilience

### Circuit Breaker

Automatically handle Redis failures.

```typescript
const cache = createCache({
  redis: { host: 'localhost', port: 6379 },
  circuitBreaker: {
    threshold: 5,        // Open after 5 failures
    timeout: 30000,      // Try again after 30s
    halfOpenRequests: 3, // Test with 3 requests
  },
})

// Circuit states:
// CLOSED: Normal operation (uses Redis)
// OPEN: Redis is down (falls back to fetch)
// HALF_OPEN: Testing if Redis recovered
```

---

### Graceful Degradation

Always provide fetch function.

```typescript
// Good - graceful degradation
const userCache = cache.define({
  name: 'user',
  key: (id: string) => id,
  fetch: async (id: string) => db.user.findUnique({ where: { id } }),
  ttl: 300,
})

// If Redis fails, falls back to database
const user = await userCache.get('123') // Always works
```

---

### Request Deduplication

Prevent cache stampede.

```typescript
const expensiveCache = cache.define({
  name: 'expensive',
  key: (id: string) => id,
  fetch: expensiveDatabaseQuery,
  dedupe: true, // Default
  ttl: 300,
})

// Multiple concurrent requests only execute fetch once
await Promise.all([
  expensiveCache.get('123'), // Executes fetch
  expensiveCache.get('123'), // Waits for first
  expensiveCache.get('123'), // Waits for first
])
```

---

### Error Monitoring

Track cache errors.

```typescript
cache.on('error', (event) => {
  console.error('Cache error:', event.error)

  // Send to monitoring
  if (process.env.NODE_ENV === 'production') {
    sentry.captureException(event.error, {
      tags: { key: event.key },
    })
  }
})
```

---

## Performance Optimization

### Batch Operations

Use bulk methods when possible.

```typescript
// Bad - sequential gets
const users = []
for (const id of userIds) {
  users.push(await userCache.get(id))
}

// Good - batch get
const users = await userCache.getMany(userIds.map(id => [id]))
```

---

### Local Cache (Server Mode)

Enable local cache for frequently accessed data.

```typescript
const cache = createCache({
  redis: { host: 'localhost', port: 6379 },
  local: {
    max: 1000,  // Cache 1000 items locally
    ttl: 60,    // Local cache TTL: 60 seconds
  },
})

// Hot data is served from memory (microseconds)
// Reduces Redis round trips
```

---

### TTL Optimization

Balance freshness with performance.

```typescript
// High-traffic, slow-changing data: longer TTL
const categoryCache = cache.define({
  name: 'category',
  ttl: 3600, // 1 hour
})

// Low-traffic, fast-changing data: shorter TTL
const userOnlineCache = cache.define({
  name: 'user-online',
  ttl: 60, // 1 minute
})
```

---

### Stale-While-Revalidate for Hot Paths

Serve stale data on critical paths.

```typescript
const productDetailCache = cache.define({
  name: 'product-detail',
  key: (id: string) => id,
  fetch: fetchProductWithRelations, // Expensive
  ttl: 300,
  staleWhileRevalidate: 1800, // Serve stale for 30 min
})

// Product page loads instantly even after TTL
```

---

### Selective Caching

Don't cache everything.

```typescript
// Cache expensive queries
const analyticsCache = cache.define({
  name: 'analytics',
  ttl: 300,
})

// Don't cache cheap queries
async function getUser(id: string) {
  // Simple query - don't cache
  return db.user.findUnique({ where: { id } })
}
```

---

## Security Considerations

### Validate Cache Keys

Prevent cache key injection.

```typescript
// Bad - no validation
key: (userId: string) => userId

// Good - validate input
key: (userId: string) => {
  if (!/^[a-zA-Z0-9-]+$/.test(userId)) {
    throw new Error('Invalid user ID')
  }
  return userId
}
```

---

### Sanitize Cached Data

Don't cache sensitive data unnecessarily.

```typescript
const userCache = cache.define({
  name: 'user',
  key: (id: string) => id,
  fetch: async (id: string) => {
    const user = await db.user.findUnique({ where: { id } })

    // Remove sensitive fields before caching
    const { password, ssn, ...safeUser } = user
    return safeUser
  },
})
```

---

### Cache Timing Attacks

Be aware of timing side channels.

```typescript
// If checking existence reveals secret information
const secretDocCache = cache.define({
  name: 'secret-doc',
  key: (id: string) => id,
  fetch: async (id: string) => {
    // Always take same time regardless of existence
    const [doc] = await Promise.all([
      db.doc.findUnique({ where: { id } }),
      sleep(100), // Constant time
    ])
    return doc
  },
})
```

---

### Access Control

Don't bypass authorization with cache.

```typescript
const documentCache = cache.define({
  name: 'document',
  key: (docId: string, userId: string) => `${docId}:${userId}`,
  fetch: async (docId: string, userId: string) => {
    // Always check authorization
    const doc = await db.document.findFirst({
      where: {
        id: docId,
        OR: [
          { ownerId: userId },
          { sharedWith: { some: { userId } } }
        ]
      }
    })

    if (!doc) {
      throw new Error('Not found or unauthorized')
    }

    return doc
  },
})
```

---

### Rate Limiting

Prevent cache exhaustion attacks.

```typescript
// Track cache operations per user
const userCacheOps = new Map<string, number>()

function checkRateLimit(userId: string) {
  const count = userCacheOps.get(userId) || 0
  if (count > 1000) {
    throw new Error('Rate limit exceeded')
  }
  userCacheOps.set(userId, count + 1)

  // Reset every minute
  setTimeout(() => userCacheOps.delete(userId), 60000)
}

export async function loader({ request }: LoaderFunctionArgs) {
  const userId = await requireUserId(request)
  checkRateLimit(userId)

  const data = await cache.get(...)
  return json({ data })
}
```

---

## Anti-Patterns

### ❌ Caching User-Specific Data with Shared Keys

```typescript
// Bad - different users get same key
const profileCache = cache.define({
  name: 'profile',
  key: () => 'current-user', // Same for everyone!
  fetch: getCurrentUserProfile,
})
```

**Fix**: Include user ID in key:
```typescript
key: (userId: string) => userId
```

---

### ❌ Not Invalidating After Updates

```typescript
// Bad - stale data after update
export async function action({ request }: ActionFunctionArgs) {
  await db.user.update({ ... })
  // Forgot to invalidate!
  return redirect('/users')
}
```

**Fix**: Always invalidate:
```typescript
await db.user.update({ ... })
await userCache.delete(userId)
```

---

### ❌ Over-Caching

```typescript
// Bad - caching everything
const everyQueryCache = cache.define({
  name: 'query',
  key: (sql: string) => hash(sql),
  ttl: 3600,
})
```

**Fix**: Cache selectively. Simple queries don't need caching.

---

### ❌ Forgetting to Close Connections in Tests

```typescript
// Bad - connection leak
it('should cache user', async () => {
  const user = await userCache.get('123')
  expect(user).toBeDefined()
  // Connection still open!
})
```

**Fix**: Use afterEach:
```typescript
afterEach(async () => {
  await cache.close()
})
```
