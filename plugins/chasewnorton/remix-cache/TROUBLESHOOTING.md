# Troubleshooting Guide

Common issues and solutions when using remix-cache.

## Table of Contents

- [Connection Issues](#connection-issues)
- [Cache Not Working](#cache-not-working)
- [Invalidation Issues](#invalidation-issues)
- [SSE / Real-Time Issues](#sse--real-time-issues)
- [Performance Issues](#performance-issues)
- [Memory Issues](#memory-issues)
- [Testing Issues](#testing-issues)
- [Type Errors](#type-errors)

---

## Connection Issues

### Redis Connection Refused

**Symptoms**: Error: `connect ECONNREFUSED 127.0.0.1:6379`

**Causes**:
- Redis server not running
- Wrong host/port configuration
- Firewall blocking connection
- Redis listening on different interface

**Solutions**:

1. **Verify Redis is running**:
   ```bash
   # Test connection
   redis-cli ping
   # Should return: PONG

   # Check if Redis process is running
   ps aux | grep redis

   # Start Redis (Docker)
   docker run -d -p 6379:6379 redis:7-alpine

   # Start Redis (Homebrew)
   brew services start redis
   ```

2. **Check configuration**:
   ```typescript
   // Verify env variables are loaded
   console.log('REDIS_HOST:', process.env.REDIS_HOST)
   console.log('REDIS_PORT:', process.env.REDIS_PORT)

   // Check Redis connection
   const cache = createCache({
     redis: {
       host: process.env.REDIS_HOST || 'localhost',
       port: parseInt(process.env.REDIS_PORT || '6379'),
     },
     prefix: 'myapp',
   })
   ```

3. **Test Redis directly**:
   ```bash
   redis-cli -h localhost -p 6379
   > ping
   PONG
   > set test "hello"
   OK
   > get test
   "hello"
   ```

---

### Redis Authentication Failed

**Symptoms**: `Error: NOAUTH Authentication required`

**Cause**: Redis requires password but none provided

**Solution**:
```typescript
const cache = createCache({
  redis: {
    host: process.env.REDIS_HOST!,
    port: parseInt(process.env.REDIS_PORT!),
    password: process.env.REDIS_PASSWORD, // Add password
  },
  prefix: 'myapp',
})
```

---

### Connection Timeout

**Symptoms**: `Error: Connection timeout`

**Causes**:
- Redis server slow to respond
- Network latency
- Redis under heavy load

**Solutions**:

1. **Increase timeout**:
   ```typescript
   const cache = createCache({
     redis: {
       host: process.env.REDIS_HOST!,
       port: 6379,
       connectTimeout: 10000, // 10 seconds
     },
     prefix: 'myapp',
   })
   ```

2. **Check Redis performance**:
   ```bash
   redis-cli --latency
   redis-cli info stats
   ```

3. **Enable circuit breaker** (graceful degradation):
   ```typescript
   const cache = createCache({
     redis: { /* ... */ },
     circuitBreaker: {
       threshold: 5,
       timeout: 30000,
       halfOpenRequests: 3,
     },
   })
   ```

---

## Cache Not Working

### Cache Always Misses

**Symptoms**: `fetch` function called every time, no cache hits

**Diagnosis**:

1. **Check if values are being stored**:
   ```bash
   redis-cli keys "myapp:*"
   redis-cli get "myapp:user:123"
   ```

2. **Enable event logging**:
   ```typescript
   cache.on('hit', (event) => console.log('HIT:', event))
   cache.on('miss', (event) => console.log('MISS:', event))
   cache.on('set', (event) => console.log('SET:', event))
   ```

**Common Causes**:

1. **TTL is 0 or too short**:
   ```typescript
   // Bad - TTL is 0
   const myCache = cache.define({
     ttl: 0, // Expires immediately!
   })

   // Good
   const myCache = cache.define({
     ttl: 300, // 5 minutes
   })
   ```

2. **Cache key changes every request**:
   ```typescript
   // Bad - includes timestamp
   key: (id: string) => `${id}:${Date.now()}`

   // Good - stable key
   key: (id: string) => id
   ```

3. **Serverless mode without proper setup**:
   ```typescript
   // In serverless, local cache is disabled
   const cache = createCache({
     redis: { /* ... */ },
     serverless: true, // No local cache
   })
   ```

4. **Serialization error**:
   ```typescript
   cache.on('error', (event) => {
     console.error('Cache error:', event.error)
   })
   ```

---

### Cache Returns Stale Data

**Symptoms**: Old data returned even after updates

**Causes**:
- Forgot to invalidate after update
- Wrong invalidation key/tag
- Local cache not invalidated

**Solutions**:

1. **Always invalidate after updates**:
   ```typescript
   export async function action({ params }: ActionFunctionArgs) {
     // Update database
     await db.user.update({ where: { id: params.userId }, data: {...} })

     // IMPORTANT: Invalidate cache
     await userCache.delete(params.userId)

     return json({ success: true })
   }
   ```

2. **Verify invalidation key matches cache key**:
   ```typescript
   // Cache definition
   const userCache = cache.define({
     name: 'user',
     key: (userId: string) => userId, // Key is just userId
   })

   // Invalidation must match
   await cache.invalidate({ key: 'myapp:user:123' }) // Full key!
   // Or use cache definition
   await userCache.delete('123') // Just userId
   ```

3. **Check local cache in server mode**:
   ```typescript
   // Local cache has separate TTL
   const cache = createCache({
     redis: { /* ... */ },
     local: {
       max: 1000,
       ttl: 60, // Local cache TTL
     },
   })

   // When you invalidate, both local and Redis are cleared
   await userCache.delete('123')
   ```

---

## Invalidation Issues

### Invalidation Not Working

**Symptoms**: Cache not cleared after invalidation

**Debug Steps**:

1. **Log invalidation events**:
   ```typescript
   cache.on('invalidate', (event) => {
     console.log('INVALIDATE:', {
       key: event.key,
       tag: event.tag,
       pattern: event.pattern,
     })
   })
   ```

2. **Check Redis directly**:
   ```bash
   # Before invalidation
   redis-cli get "myapp:user:123"

   # After invalidation (should be null)
   redis-cli get "myapp:user:123"
   ```

3. **Verify tag/pattern tracking**:
   ```bash
   # Check tags set
   redis-cli smembers "myapp:tags:user"

   # Check pattern set
   redis-cli smembers "myapp:patterns:user:*"
   ```

**Common Issues**:

1. **Tag not defined in cache definition**:
   ```typescript
   // Bad - no tags
   const userCache = cache.define({
     name: 'user',
     key: (id) => id,
     // No tags!
   })

   // This won't work!
   await cache.invalidateByTag('user')

   // Good - with tags
   const userCache = cache.define({
     name: 'user',
     key: (id) => id,
     tags: (id, user) => ['user', `user:${id}`],
   })

   // Now this works
   await cache.invalidateByTag('user')
   ```

2. **Pattern doesn't match**:
   ```typescript
   // Pattern only matches within cache name
   await cache.invalidateByPattern('user:*')
   // Matches: myapp:user:123, myapp:user:456
   // Does NOT match: myapp:session:user:123 (wrong cache name)
   ```

---

### Cascading Invalidation Not Working

**Symptoms**: Dependent caches not invalidated

**Solution**:

```typescript
// Make sure invalidate function is defined
const postCache = cache.define({
  name: 'post',
  key: (id) => id,
  tags: (id, post) => ['post', `post:${id}`],
  invalidate: (id, post) => [
    // Return FULL cache keys (prefix:name:key)
    `myapp:user:${post.authorId}:posts`, // Wrong if user cache key is just userId
    // Or use cache definition name
    `user:${post.authorId}:posts`, // Correct format
  ],
})

// Test cascading
await postCache.delete('123')
// Check if user posts cache was invalidated
redis-cli get "myapp:user:456:posts"
```

---

## SSE / Real-Time Issues

### SSE Connection Not Established

**Symptoms**: No EventSource connection in Network tab

**Debug Steps**:

1. **Check CacheProvider is in root**:
   ```typescript
   // app/root.tsx
   export default function App() {
     return (
       <CacheProvider endpoint="/api/cache-events"> {/* Must wrap Outlet */}
         <Outlet />
       </CacheProvider>
     )
   }
   ```

2. **Verify SSE endpoint exists**:
   ```bash
   curl -N http://localhost:3000/api/cache-events
   # Should keep connection open
   ```

3. **Check browser DevTools**:
   - Network tab → Filter by "EventStream"
   - Should see `cache-events` connection
   - Status should be 200
   - Type should be "eventsource"

**Common Issues**:

1. **Wrong endpoint path**:
   ```typescript
   // Must match route file name
   // File: app/routes/api.cache-events.tsx
   <CacheProvider endpoint="/api/cache-events" /> // ✓ Correct

   // File: app/routes/cache.events.tsx
   <CacheProvider endpoint="/api/cache-events" /> // ✗ Wrong path
   ```

2. **Missing SSE loader**:
   ```typescript
   // app/routes/api.cache-events.tsx
   import { createSSEHandler } from 'remix-cache/server'
   import { cache } from '~/cache.server'

   // MUST export loader
   export const loader = createSSEHandler(cache)
   ```

---

### Events Not Received

**Symptoms**: SSE connected but no events received

**Debug Steps**:

1. **Test with curl**:
   ```bash
   # In one terminal, watch events
   curl -N http://localhost:3000/api/cache-events

   # In another terminal, trigger invalidation
   curl -X POST http://localhost:3000/some-action
   ```

2. **Check event format**:
   ```typescript
   cache.on('invalidate', (event) => {
     console.log('Event emitted:', event)
   })
   ```

**Common Issues**:

1. **Invalidation not emitting events**:
   ```typescript
   // These methods emit events
   await cache.invalidate({ key: '...' })
   await cache.invalidateByTag('...')
   await cache.invalidateByPattern('...')
   await cacheDefinition.delete(...)

   // Direct Redis operations DO NOT emit events
   await redis.del('myapp:user:123') // ✗ No event!
   ```

2. **Browser caching EventSource**:
   ```typescript
   // Add cache-busting query param
   <CacheProvider endpoint="/api/cache-events?nocache=true" />
   ```

---

### Revalidation Not Triggering

**Symptoms**: Events received but component doesn't revalidate

**Debug Steps**:

1. **Check useCache filters match events**:
   ```typescript
   // Event emitted
   { tag: 'product', timestamp: ... }

   // Component filter
   useCache({ tags: ['user'] }) // ✗ Doesn't match!

   // Fixed
   useCache({ tags: ['product'] }) // ✓ Matches
   ```

2. **Check revalidator state**:
   ```typescript
   import { useRevalidator } from '@remix-run/react'

   export default function MyComponent() {
     const revalidator = useRevalidator()

     useEffect(() => {
       console.log('Revalidator state:', revalidator.state)
     }, [revalidator.state])

     useCache({ tags: ['user'] })
   }
   ```

**Common Issues**:

1. **Filters too strict**:
   ```typescript
   // Only matches this exact key
   useCache({ keys: ['myapp:user:123'] })

   // More flexible - matches all user tags
   useCache({ tags: ['user'] })
   ```

2. **Debounce too long**:
   ```typescript
   // Revalidation delayed by 10 seconds
   useCache({ tags: ['user'], debounce: 10000 })

   // More responsive
   useCache({ tags: ['user'], debounce: 200 })
   ```

---

## Performance Issues

### Slow Cache Operations

**Symptoms**: Cache operations taking too long

**Diagnosis**:

1. **Measure latency**:
   ```typescript
   cache.on('hit', (event) => {
     console.log(`Cache hit latency: ${event.latency}ms`)
   })

   cache.on('miss', (event) => {
     console.log(`Cache miss latency: ${event.latency}ms`)
   })
   ```

2. **Check Redis performance**:
   ```bash
   redis-cli --latency
   redis-cli --latency-history
   redis-cli slowlog get 10
   ```

**Solutions**:

1. **Enable local cache**:
   ```typescript
   const cache = createCache({
     redis: { /* ... */ },
     local: {
       max: 1000,
       ttl: 60, // Hot data served from memory
     },
   })
   ```

2. **Use batch operations**:
   ```typescript
   // Slow - sequential
   for (const id of ids) {
     await userCache.get(id)
   }

   // Fast - batched
   const users = await userCache.getMany(ids.map(id => [id]))
   ```

3. **Optimize serialization**:
   ```typescript
   // Large objects are slow to serialize
   // Consider caching only what you need
   const userCache = cache.define({
     fetch: async (id) => {
       const user = await db.user.findUnique({ where: { id } })
       // Return only necessary fields
       return {
         id: user.id,
         name: user.name,
         email: user.email,
         // Don't cache large fields
       }
     },
   })
   ```

---

### High Redis Memory Usage

**Symptoms**: Redis using too much memory

**Diagnosis**:
```bash
redis-cli info memory
redis-cli --bigkeys
```

**Solutions**:

1. **Set appropriate TTLs**:
   ```typescript
   // Don't cache forever
   const cache = cache.define({
     ttl: 3600, // Expire after 1 hour
   })
   ```

2. **Use patterns for bulk invalidation**:
   ```bash
   # Periodically clean old data
   redis-cli --scan --pattern "myapp:*:2023-*" | xargs redis-cli del
   ```

3. **Limit local cache size**:
   ```typescript
   const cache = createCache({
     local: {
       max: 500, // Limit to 500 items
       ttl: 60,
     },
   })
   ```

---

## Memory Issues

### Memory Leaks in Tests

**Symptoms**: Tests slow down over time, memory usage grows

**Cause**: Redis connections not closed

**Solution**:
```typescript
import { afterEach } from 'vitest'

afterEach(async () => {
  await cache.close() // IMPORTANT!
})
```

---

### Memory Leaks in Production

**Symptoms**: Application memory grows over time

**Causes**:
- Event listeners not cleaned up
- Local cache growing unbounded

**Solutions**:

1. **Limit local cache**:
   ```typescript
   const cache = createCache({
     local: {
       max: 1000, // Prevent unbounded growth
       ttl: 60,
     },
   })
   ```

2. **Clean up event listeners**:
   ```typescript
   const handler = (event) => { /* ... */ }
   cache.on('hit', handler)

   // When done
   cache.off('hit', handler)
   ```

---

## Testing Issues

### Tests Failing with "Connection Refused"

**Solution**: Ensure Redis is running

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    globalSetup: './test/setup.ts',
  },
})

// test/setup.ts
export async function setup() {
  // Start Redis or check it's running
  const redis = new Redis()
  await redis.ping()
  await redis.quit()
}
```

---

### Tests Interfering with Each Other

**Symptoms**: Tests pass individually but fail together

**Cause**: Shared Redis state

**Solutions**:

1. **Use unique prefixes per test**:
   ```typescript
   let cache: Cache

   beforeEach(() => {
     cache = createCache({
       redis: { host: 'localhost', port: 6379 },
       prefix: `test-${Math.random().toString(36)}`, // Unique prefix
     })
   })

   afterEach(async () => {
     await cache.close()
   })
   ```

2. **Flush Redis between tests**:
   ```typescript
   afterEach(async () => {
     await redis.flushdb() // Clear test database
     await cache.close()
   })
   ```

See [TESTING.md](TESTING.md) for complete testing guide.

---

## Type Errors

### Generic Type Inference Issues

**Symptom**: TypeScript can't infer types correctly

**Solution**: Explicitly type the cache definition

```typescript
interface User {
  id: string
  name: string
  email: string
}

const userCache = cache.define<[string], User>({
  name: 'user',
  key: (userId: string) => userId,
  fetch: async (userId: string): Promise<User> => {
    return db.user.findUnique({ where: { id: userId } })
  },
})
```

---

## Getting More Help

If your issue isn't covered here:

1. Check [API_REFERENCE.md](API_REFERENCE.md) for detailed API documentation
2. Review [PATTERNS.md](PATTERNS.md) for best practices
3. See [TESTING.md](TESTING.md) for testing strategies
4. Check the test files in `src/**/__tests__/` for working examples
5. Enable debug logging to understand what's happening

**Debug logging**:
```typescript
cache.on('hit', (e) => console.log('HIT:', e))
cache.on('miss', (e) => console.log('MISS:', e))
cache.on('set', (e) => console.log('SET:', e))
cache.on('invalidate', (e) => console.log('INVALIDATE:', e))
cache.on('error', (e) => console.error('ERROR:', e))
```
