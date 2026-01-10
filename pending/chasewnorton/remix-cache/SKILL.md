---
name: remix-cache
description: A type-safe, Redis-backed caching library for Remix applications with SSE-based real-time invalidation, stale-while-revalidate, pattern matching, and automatic React revalidation. Use when working with Remix caching, Redis, cache invalidation, implementing caching strategies, or real-time data synchronization in Remix apps.
---

# Remix Cache Skill

Expert guidance for using remix-cache, a production-ready caching library for Remix applications.

## When to use this skill

Use this skill when the user asks about:
- Implementing caching in Remix applications
- Redis-backed caching strategies
- Cache invalidation (by key, tag, or pattern)
- Real-time cache synchronization with SSE
- Stale-while-revalidate patterns
- Type-safe cache definitions
- React hooks for automatic revalidation
- Performance optimization with caching
- Server vs serverless caching modes
- Circuit breaker patterns for cache failures

## Quick reference

### Basic setup

```typescript
// app/cache.server.ts
import { createCache } from 'remix-cache/server'

export const cache = createCache({
  redis: { host: process.env.REDIS_HOST, port: 6379 },
  prefix: 'myapp',
})

export const userCache = cache.define({
  name: 'user',
  key: (userId: string) => userId,
  fetch: async (userId: string) => db.user.findUnique({ where: { id: userId } }),
  ttl: 300,
})
```

### Use in loaders

```typescript
export async function loader({ params }: LoaderFunctionArgs) {
  const user = await userCache.get(params.userId)
  return json({ user })
}
```

### Invalidation

```typescript
// By key
await cache.invalidate({ key: 'myapp:user:123' })

// By tag
await cache.invalidateByTag('product')

// By pattern
await cache.invalidateByPattern('user:*')
```

### Real-time React revalidation

```typescript
// app/root.tsx
<CacheProvider endpoint="/api/cache-events">
  <Outlet />
</CacheProvider>

// Component
useCache({ tags: ['user'], debounce: 200 })
```

## Detailed documentation

For comprehensive guidance on specific topics, see:

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Installation, setup, and first cache definition
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation for all methods and options
- **[PATTERNS.md](PATTERNS.md)** - Common caching patterns and best practices
- **[REACT_INTEGRATION.md](REACT_INTEGRATION.md)** - SSE setup and React hooks for real-time invalidation
- **[EXAMPLES.md](EXAMPLES.md)** - Real-world examples (e-commerce, sessions, API caching)
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[TESTING.md](TESTING.md)** - Testing strategies and patterns

## Key capabilities

### 1. Type-safe cache definitions
Perfect TypeScript inference for cache keys and values. See [API_REFERENCE.md](API_REFERENCE.md#cache-definitions).

### 2. Advanced TTL strategies
- **Stale-while-revalidate**: Serve stale data while fetching fresh
- **Sliding window**: Reset TTL on each access
- **Conditional TTL**: Dynamic TTL based on data
See [PATTERNS.md](PATTERNS.md#ttl-strategies).

### 3. Multi-level invalidation
- **By key**: Invalidate specific entries
- **By tag**: Invalidate groups of related entries
- **By pattern**: Invalidate using glob patterns
- **Cascading**: Automatic dependent invalidation
See [API_REFERENCE.md](API_REFERENCE.md#invalidation).

### 4. Real-time synchronization
- **SSE endpoint**: Stream invalidation events to clients
- **React hooks**: Automatic revalidation on cache changes
- **Filtering**: Revalidate only for specific keys/tags/patterns
See [REACT_INTEGRATION.md](REACT_INTEGRATION.md).

### 5. Resilience features
- **Circuit breaker**: Graceful degradation when Redis fails
- **Request deduplication**: Prevent cache stampede
- **Error events**: Monitor and track failures
See [PATTERNS.md](PATTERNS.md#resilience).

### 6. Deployment flexibility
- **Server mode**: Two-tier caching (local LRU + Redis)
- **Serverless mode**: Redis-only with versioned keys
See [API_REFERENCE.md](API_REFERENCE.md#deployment-modes).

## File structure in this repository

The remix-cache library is organized as:

```
src/
├── server/           # Server-side cache implementation
│   ├── cache.ts      # Main cache class
│   ├── definition.ts # Cache definition implementation
│   ├── sse-handler.ts # SSE endpoint generator
│   ├── local-cache.ts # In-memory LRU cache
│   ├── circuit-breaker.ts # Circuit breaker pattern
│   └── deduplicator.ts # Request deduplication
├── react/            # React integration
│   ├── provider.tsx  # CacheProvider component
│   ├── use-cache.ts  # useCache hook
│   └── context.tsx   # React context
├── types/            # TypeScript type definitions
│   ├── cache.ts
│   ├── definition.ts
│   └── events.ts
└── utils/            # Utility functions
    ├── key-builder.ts     # Cache key generation
    ├── pattern-match.ts   # Glob pattern matching
    └── env-detect.ts      # Environment detection
```

## Common workflows

### Setting up a new cache

1. Read [GETTING_STARTED.md](GETTING_STARTED.md) for basic setup
2. Create cache instance in `app/cache.server.ts`
3. Define cache definitions for your data types
4. Use in loaders/actions
5. Set up SSE endpoint for real-time invalidation (see [REACT_INTEGRATION.md](REACT_INTEGRATION.md))
6. Add React hooks to components that need auto-revalidation

### Implementing cache invalidation

1. Identify invalidation strategy (key/tag/pattern)
2. Add tags to cache definitions if needed
3. Call invalidation methods in actions
4. Verify invalidation events are fired
5. Test React components revalidate correctly

### Debugging cache issues

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
2. Enable event listeners to monitor cache behavior
3. Verify Redis connection and configuration
4. Check circuit breaker state
5. Inspect SSE connection in browser DevTools

### Writing tests

See [TESTING.md](TESTING.md) for:
- Unit testing cache definitions
- Integration testing with Redis
- Mocking cache in tests
- Testing invalidation logic
- Testing React components with cache

## Environment variables

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-password
CACHE_PREFIX=myapp
CACHE_DEFAULT_TTL=300
NODE_ENV=production
```

## Implementation notes

When helping users implement remix-cache:

1. **Always ensure type safety**: The library provides perfect TypeScript inference
2. **Consider deployment mode**: Ask if serverless or server-based
3. **Plan invalidation strategy**: Tags are more flexible than keys
4. **Set appropriate TTLs**: Balance freshness with performance
5. **Monitor errors**: Always set up error event listeners
6. **Test thoroughly**: Cache bugs can be subtle, see [TESTING.md](TESTING.md)
7. **Close connections**: Especially important in tests

## Getting help

For specific topics:
- New to the library? → [GETTING_STARTED.md](GETTING_STARTED.md)
- Looking for API details? → [API_REFERENCE.md](API_REFERENCE.md)
- Need implementation patterns? → [PATTERNS.md](PATTERNS.md) and [EXAMPLES.md](EXAMPLES.md)
- Setting up React integration? → [REACT_INTEGRATION.md](REACT_INTEGRATION.md)
- Encountering issues? → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Writing tests? → [TESTING.md](TESTING.md)

## Version

This skill covers remix-cache v0.1.0 with complete implementation of Phases 1-5:
- ✅ Core caching with Redis backend
- ✅ Type-safe cache definitions
- ✅ Stale-while-revalidate
- ✅ Sliding window TTL
- ✅ Pattern & tag-based invalidation
- ✅ Circuit breaker pattern
- ✅ Request deduplication
- ✅ Server/serverless modes
- ✅ SSE real-time invalidation
- ✅ React hooks for auto-revalidation
