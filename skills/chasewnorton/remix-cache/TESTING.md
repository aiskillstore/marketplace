# Testing Guide

Comprehensive guide to testing applications using remix-cache.

## Table of Contents

- [Test Setup](#test-setup)
- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [Testing Invalidation](#testing-invalidation)
- [Testing React Components](#testing-react-components)
- [Mocking Strategies](#mocking-strategies)
- [Testing Patterns](#testing-patterns)
- [Common Test Issues](#common-test-issues)

---

## Test Setup

### Basic Vitest Setup

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: true, // Prevent parallel execution issues
      },
    },
    fileParallelism: false, // Run test files sequentially
    setupFiles: ['./test/setup.ts'],
  },
})
```

### Test Setup File

```typescript
// test/setup.ts
import { afterEach, beforeAll } from 'vitest'
import Redis from 'ioredis'

// Verify Redis is available
beforeAll(async () => {
  const redis = new Redis({
    host: 'localhost',
    port: 6379,
  })

  try {
    await redis.ping()
    console.log('✓ Redis is available for testing')
  } catch (error) {
    console.error('✗ Redis is not available')
    throw error
  } finally {
    await redis.quit()
  }
})
```

### Per-Test Cache Setup

```typescript
// test/cache-test-utils.ts
import { createCache, type Cache } from 'remix-cache/server'
import { afterEach } from 'vitest'

let cacheInstances: Cache[] = []

export function createTestCache(prefix?: string) {
  const cache = createCache({
    redis: {
      host: 'localhost',
      port: 6379,
    },
    prefix: prefix || `test-${Math.random().toString(36).substring(7)}`,
  })

  cacheInstances.push(cache)
  return cache
}

// Cleanup all cache instances after each test
afterEach(async () => {
  await Promise.all(cacheInstances.map(cache => cache.close()))
  cacheInstances = []
})
```

---

## Unit Testing

### Testing Cache Definitions

```typescript
// app/cache.server.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { createTestCache } from '~/test/cache-test-utils'

describe('userCache', () => {
  let cache: Cache

  beforeEach(() => {
    cache = createTestCache()
  })

  it('should cache user data', async () => {
    const userCache = cache.define({
      name: 'user',
      key: (userId: string) => userId,
      fetch: async (userId: string) => ({
        id: userId,
        name: `User ${userId}`,
        email: `user${userId}@example.com`,
      }),
      ttl: 300,
    })

    // First call - cache miss
    const user1 = await userCache.get('123')
    expect(user1).toEqual({
      id: '123',
      name: 'User 123',
      email: 'user123@example.com',
    })

    // Second call - cache hit (same object)
    const user2 = await userCache.get('123')
    expect(user2).toEqual(user1)
  })

  it('should respect TTL', async () => {
    vi.useFakeTimers()

    const userCache = cache.define({
      name: 'user',
      key: (userId: string) => userId,
      fetch: vi.fn(async (userId: string) => ({
        id: userId,
        timestamp: Date.now(),
      })),
      ttl: 2, // 2 seconds
    })

    // First fetch
    await userCache.get('123')
    expect(userCache.config.fetch).toHaveBeenCalledTimes(1)

    // Within TTL - cache hit
    vi.advanceTimersByTime(1000)
    await userCache.get('123')
    expect(userCache.config.fetch).toHaveBeenCalledTimes(1)

    // After TTL - cache miss
    vi.advanceTimersByTime(2000)
    await userCache.get('123')
    expect(userCache.config.fetch).toHaveBeenCalledTimes(2)

    vi.useRealTimers()
  })

  it('should handle multi-argument keys', async () => {
    const productCache = cache.define({
      name: 'product',
      key: (productId: string, locale: string) => `${productId}:${locale}`,
      fetch: async (productId: string, locale: string) => ({
        id: productId,
        name: locale === 'es' ? 'Producto' : 'Product',
      }),
      ttl: 300,
    })

    const productEn = await productCache.get('123', 'en')
    const productEs = await productCache.get('123', 'es')

    expect(productEn.name).toBe('Product')
    expect(productEs.name).toBe('Producto')
  })

  it('should handle cache miss without fetch', async () => {
    const cache = cache.define({
      name: 'test',
      key: (id: string) => id,
      // No fetch function
    })

    const result = await cache.get('missing')
    expect(result).toBeNull()
  })

  it('should store values with set', async () => {
    const userCache = cache.define({
      name: 'user',
      key: (id: string) => id,
      ttl: 300,
    })

    await userCache.set('123', { id: '123', name: 'Alice' })

    const user = await userCache.get('123')
    expect(user).toEqual({ id: '123', name: 'Alice' })
  })

  it('should delete values', async () => {
    const userCache = cache.define({
      name: 'user',
      key: (id: string) => id,
      fetch: async (id: string) => ({ id, name: 'User' }),
      ttl: 300,
    })

    // Populate cache
    await userCache.get('123')

    // Delete
    await userCache.delete('123')

    // Should be null (not refetched without fetch function)
    const user = await userCache.get('123')
    expect(user).toBeNull()
  })
})
```

### Testing Bulk Operations

```typescript
describe('Bulk operations', () => {
  let cache: Cache
  let userCache: CacheDefinitionInstance<[string], User>

  beforeEach(() => {
    cache = createTestCache()
    userCache = cache.define({
      name: 'user',
      key: (id: string) => id,
      fetch: async (id: string) => ({
        id,
        name: `User ${id}`,
      }),
      ttl: 300,
    })
  })

  it('should get multiple values', async () => {
    await userCache.setMany([
      { args: ['1'], value: { id: '1', name: 'Alice' } },
      { args: ['2'], value: { id: '2', name: 'Bob' } },
      { args: ['3'], value: { id: '3', name: 'Charlie' } },
    ])

    const users = await userCache.getMany([['1'], ['2'], ['3']])

    expect(users).toEqual([
      { id: '1', name: 'Alice' },
      { id: '2', name: 'Bob' },
      { id: '3', name: 'Charlie' },
    ])
  })

  it('should handle missing values in getMany', async () => {
    await userCache.set('1', { id: '1', name: 'Alice' })

    const users = await userCache.getMany([['1'], ['2'], ['3']])

    expect(users[0]).toEqual({ id: '1', name: 'Alice' })
    expect(users[1]).toBeNull() // Missing
    expect(users[2]).toBeNull() // Missing
  })

  it('should delete multiple values', async () => {
    await userCache.setMany([
      { args: ['1'], value: { id: '1', name: 'Alice' } },
      { args: ['2'], value: { id: '2', name: 'Bob' } },
    ])

    await userCache.deleteMany([['1'], ['2']])

    const users = await userCache.getMany([['1'], ['2']])
    expect(users).toEqual([null, null])
  })
})
```

---

## Integration Testing

### Testing with Database

```typescript
// app/routes/users.$userId.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { createTestCache } from '~/test/cache-test-utils'
import { db } from '~/db.server'

describe('User routes with cache', () => {
  let cache: Cache

  beforeEach(async () => {
    cache = createTestCache()

    // Clean test data
    await db.user.deleteMany()
  })

  it('should cache user from database', async () => {
    // Create test user in database
    const testUser = await db.user.create({
      data: {
        id: '123',
        name: 'Test User',
        email: 'test@example.com',
      },
    })

    const userCache = cache.define({
      name: 'user',
      key: (id: string) => id,
      fetch: async (id: string) => {
        return db.user.findUnique({ where: { id } })
      },
      ttl: 300,
    })

    // First call - fetches from DB
    const user1 = await userCache.get('123')
    expect(user1).toEqual(testUser)

    // Update database directly
    await db.user.update({
      where: { id: '123' },
      data: { name: 'Updated Name' },
    })

    // Second call - returns cached (old) value
    const user2 = await userCache.get('123')
    expect(user2?.name).toBe('Test User') // Still old name

    // Invalidate cache
    await userCache.delete('123')

    // Third call - fetches updated value
    const user3 = await userCache.get('123')
    expect(user3?.name).toBe('Updated Name')
  })

  it('should handle database errors gracefully', async () => {
    const userCache = cache.define({
      name: 'user',
      key: (id: string) => id,
      fetch: async (id: string) => {
        // Simulate database error
        throw new Error('Database connection failed')
      },
      ttl: 300,
    })

    await expect(userCache.get('123')).rejects.toThrow(
      'Database connection failed'
    )
  })
})
```

### Testing Loaders and Actions

```typescript
// app/routes/products.$productId.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { loader, action } from './products.$productId'

describe('Product routes', () => {
  beforeEach(() => {
    // Setup test cache and database
  })

  it('should load product from cache', async () => {
    const request = new Request('http://localhost/products/123')
    const params = { productId: '123' }

    const response = await loader({ request, params, context: {} })
    const data = await response.json()

    expect(data.product).toBeDefined()
    expect(data.product.id).toBe('123')
  })

  it('should invalidate cache on update', async () => {
    const formData = new FormData()
    formData.set('name', 'Updated Product')
    formData.set('price', '99.99')

    const request = new Request('http://localhost/products/123', {
      method: 'POST',
      body: formData,
    })

    const response = await action({ request, params: { productId: '123' }, context: {} })
    const data = await response.json()

    expect(data.product.name).toBe('Updated Product')

    // Verify cache was invalidated (next loader call fetches fresh data)
  })
})
```

---

## Testing Invalidation

### Testing Tag-Based Invalidation

```typescript
describe('Tag-based invalidation', () => {
  let cache: Cache

  beforeEach(() => {
    cache = createTestCache()
  })

  it('should invalidate all entries with tag', async () => {
    const productCache = cache.define({
      name: 'product',
      key: (id: string) => id,
      fetch: vi.fn(async (id: string) => ({
        id,
        name: `Product ${id}`,
      })),
      ttl: 300,
      tags: (id) => ['product', `product:${id}`],
    })

    // Populate cache with 3 products
    await productCache.get('1')
    await productCache.get('2')
    await productCache.get('3')
    expect(productCache.config.fetch).toHaveBeenCalledTimes(3)

    // Invalidate all products by tag
    await cache.invalidateByTag('product')

    // Next calls should refetch
    await productCache.get('1')
    await productCache.get('2')
    await productCache.get('3')
    expect(productCache.config.fetch).toHaveBeenCalledTimes(6) // 3 initial + 3 after invalidation
  })

  it('should invalidate specific product by tag', async () => {
    const productCache = cache.define({
      name: 'product',
      key: (id: string) => id,
      fetch: vi.fn(async (id: string) => ({ id, name: `Product ${id}` })),
      ttl: 300,
      tags: (id) => ['product', `product:${id}`],
    })

    await productCache.get('1')
    await productCache.get('2')
    expect(productCache.config.fetch).toHaveBeenCalledTimes(2)

    // Invalidate only product:1
    await cache.invalidateByTag('product:1')

    await productCache.get('1') // Refetched
    await productCache.get('2') // Still cached
    expect(productCache.config.fetch).toHaveBeenCalledTimes(3) // Only 1 refetch
  })
})
```

### Testing Pattern-Based Invalidation

```typescript
describe('Pattern-based invalidation', () => {
  let cache: Cache

  beforeEach(() => {
    cache = createTestCache()
  })

  it('should invalidate entries matching pattern', async () => {
    const userCache = cache.define({
      name: 'user',
      key: (id: string) => id,
      fetch: vi.fn(async (id: string) => ({ id, name: `User ${id}` })),
      ttl: 300,
    })

    // Populate cache
    await userCache.get('admin-1')
    await userCache.get('admin-2')
    await userCache.get('user-1')
    expect(userCache.config.fetch).toHaveBeenCalledTimes(3)

    // Invalidate only admin users
    await cache.invalidateByPattern('admin-*')

    await userCache.get('admin-1') // Refetched
    await userCache.get('admin-2') // Refetched
    await userCache.get('user-1')   // Still cached
    expect(userCache.config.fetch).toHaveBeenCalledTimes(5) // 2 refetches
  })
})
```

### Testing Cascading Invalidation

```typescript
describe('Cascading invalidation', () => {
  let cache: Cache

  beforeEach(() => {
    cache = createTestCache()
  })

  it('should cascade invalidation to dependent keys', async () => {
    const postCache = cache.define({
      name: 'post',
      key: (id: string) => id,
      fetch: async (id: string) => ({
        id,
        title: 'Post',
        authorId: 'author-1',
      }),
      ttl: 300,
      tags: (id, post) => ['post', `post:${id}`],
      invalidate: (id, post) => [
        `author:${post.authorId}:posts`, // Cascade to author's posts
      ],
    })

    const authorPostsCache = cache.define({
      name: 'author-posts',
      key: (authorId: string) => `${authorId}:posts`,
      fetch: vi.fn(async (authorId: string) => []),
      ttl: 300,
    })

    // Populate caches
    await postCache.get('1')
    await authorPostsCache.get('author-1')

    // Invalidate post - should cascade to author posts
    await postCache.delete('1')

    // Author posts should be refetched
    await authorPostsCache.get('author-1')
    expect(authorPostsCache.config.fetch).toHaveBeenCalledTimes(2)
  })
})
```

---

## Testing React Components

### Testing with CacheProvider

```typescript
// app/routes/users.$userId.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { CacheProvider } from 'remix-cache/react'
import UserProfile from './users.$userId'

// Mock useEventSource
vi.mock('remix-utils/sse/react', () => ({
  useEventSource: vi.fn(() => null),
}))

describe('UserProfile component', () => {
  it('should revalidate on cache invalidation', async () => {
    const { useEventSource } = await import('remix-utils/sse/react')

    // Mock initial state
    vi.mocked(useEventSource).mockReturnValueOnce(null)

    const { rerender } = render(
      <CacheProvider>
        <UserProfile />
      </CacheProvider>
    )

    expect(screen.getByText('John Doe')).toBeInTheDocument()

    // Simulate invalidation event
    const invalidationEvent = JSON.stringify({
      tag: 'user',
      timestamp: Date.now(),
    })

    vi.mocked(useEventSource).mockReturnValueOnce(invalidationEvent)

    rerender(
      <CacheProvider>
        <UserProfile />
      </CacheProvider>
    )

    // Component should trigger revalidation
    await waitFor(() => {
      // Verify revalidation happened
      expect(screen.getByText('Updated Name')).toBeInTheDocument()
    })
  })
})
```

### Testing useCache Hook

```typescript
// test/use-cache.test.ts
import { describe, it, expect, vi } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useCache } from 'remix-cache/react'
import { CacheProvider } from 'remix-cache/react'

vi.mock('remix-utils/sse/react', () => ({
  useEventSource: vi.fn(() => null),
}))

vi.mock('@remix-run/react', () => ({
  useRevalidator: () => ({
    revalidate: vi.fn(),
    state: 'idle',
  }),
}))

describe('useCache hook', () => {
  it('should call revalidator when event matches filter', async () => {
    const { useEventSource } = await import('remix-utils/sse/react')
    const { useRevalidator } = await import('@remix-run/react')

    const revalidate = vi.fn()
    vi.mocked(useRevalidator).mockReturnValue({
      revalidate,
      state: 'idle',
    })

    const wrapper = ({ children }) => (
      <CacheProvider>{children}</CacheProvider>
    )

    renderHook(() => useCache({ tags: ['user'] }), { wrapper })

    // Emit invalidation event
    const event = JSON.stringify({ tag: 'user', timestamp: Date.now() })
    vi.mocked(useEventSource).mockReturnValue(event)

    // Wait for debounce
    await new Promise(resolve => setTimeout(resolve, 150))

    expect(revalidate).toHaveBeenCalled()
  })
})
```

---

## Mocking Strategies

### Mock Entire Cache

```typescript
// test/mocks/cache.ts
import { vi } from 'vitest'

export function createMockCache() {
  const mockCache = {
    define: vi.fn(() => ({
      get: vi.fn(),
      set: vi.fn(),
      delete: vi.fn(),
      getMany: vi.fn(),
      setMany: vi.fn(),
      deleteMany: vi.fn(),
      seed: vi.fn(),
    })),
    invalidate: vi.fn(),
    invalidateByTag: vi.fn(),
    invalidateByPattern: vi.fn(),
    close: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
  }

  return mockCache
}

// Usage in tests
vi.mock('~/cache.server', () => ({
  cache: createMockCache(),
}))
```

### Mock Specific Cache Definition

```typescript
it('should use mocked user cache', async () => {
  const mockUserCache = {
    get: vi.fn().mockResolvedValue({ id: '123', name: 'Mock User' }),
    set: vi.fn(),
    delete: vi.fn(),
  }

  // Use mock in test
  const user = await mockUserCache.get('123')
  expect(user.name).toBe('Mock User')
})
```

---

## Testing Patterns

### Testing with Fake Timers

```typescript
it('should expire cache after TTL', async () => {
  vi.useFakeTimers({ toFake: ['Date', 'setTimeout', 'setInterval'] })

  const cache = cache.define({
    name: 'test',
    key: (id: string) => id,
    fetch: vi.fn(async (id: string) => ({ id, timestamp: Date.now() })),
    ttl: 10, // 10 seconds
  })

  // Initial fetch
  await cache.get('123')
  expect(cache.config.fetch).toHaveBeenCalledTimes(1)

  // Advance time within TTL
  vi.advanceTimersByTime(5000)
  await cache.get('123')
  expect(cache.config.fetch).toHaveBeenCalledTimes(1) // Still cached

  // Advance time past TTL
  vi.advanceTimersByTime(6000)
  await cache.get('123')
  expect(cache.config.fetch).toHaveBeenCalledTimes(2) // Refetched

  vi.useRealTimers()
})
```

### Testing Error Scenarios

```typescript
it('should handle fetch errors', async () => {
  const cache = cache.define({
    name: 'test',
    key: (id: string) => id,
    fetch: async (id: string) => {
      throw new Error('Fetch failed')
    },
  })

  await expect(cache.get('123')).rejects.toThrow('Fetch failed')
})

it('should emit error events', async () => {
  const errorHandler = vi.fn()
  cache.on('error', errorHandler)

  const failingCache = cache.define({
    name: 'test',
    key: (id: string) => id,
    fetch: async () => {
      throw new Error('Test error')
    },
  })

  await failingCache.get('123').catch(() => {})

  expect(errorHandler).toHaveBeenCalled()
})
```

---

## Common Test Issues

### Issue: Tests Pass Individually But Fail Together

**Cause**: Shared Redis state or connections

**Solution**: Use unique prefixes and proper cleanup

```typescript
let cache: Cache

beforeEach(() => {
  cache = createCache({
    prefix: `test-${Math.random().toString(36).substring(7)}`,
    redis: { host: 'localhost', port: 6379 },
  })
})

afterEach(async () => {
  await cache.close() // CRITICAL
})
```

### Issue: Fake Timers Not Working

**Cause**: Not mocking Date.now()

**Solution**: Use toFake option

```typescript
vi.useFakeTimers({
  toFake: ['Date', 'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval']
})
```

### Issue: React Tests Failing

**Cause**: Wrong environment

**Solution**: Use happy-dom or jsdom

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    environment: 'happy-dom', // For React tests
  },
})
```

---

## Complete Test Example

```typescript
// app/cache.server.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createTestCache } from '~/test/cache-test-utils'
import type { Cache } from 'remix-cache/server'

describe('Product Cache', () => {
  let cache: Cache

  beforeEach(() => {
    cache = createTestCache('product-tests')
  })

  describe('Basic operations', () => {
    it('should cache and retrieve products', async () => {
      const productCache = cache.define({
        name: 'product',
        key: (id: string) => id,
        fetch: async (id: string) => ({
          id,
          name: `Product ${id}`,
          price: 99.99,
        }),
        ttl: 300,
      })

      const product = await productCache.get('123')

      expect(product).toEqual({
        id: '123',
        name: 'Product 123',
        price: 99.99,
      })
    })

    it('should handle bulk operations', async () => {
      const productCache = cache.define({
        name: 'product',
        key: (id: string) => id,
        ttl: 300,
      })

      await productCache.setMany([
        { args: ['1'], value: { id: '1', name: 'Product 1' } },
        { args: ['2'], value: { id: '2', name: 'Product 2' } },
      ])

      const products = await productCache.getMany([['1'], ['2']])

      expect(products).toHaveLength(2)
      expect(products[0]?.name).toBe('Product 1')
    })
  })

  describe('Invalidation', () => {
    it('should invalidate by tag', async () => {
      const productCache = cache.define({
        name: 'product',
        key: (id: string) => id,
        fetch: vi.fn(async (id) => ({ id, name: `Product ${id}` })),
        ttl: 300,
        tags: (id) => ['product', `product:${id}`],
      })

      await productCache.get('1')
      await productCache.get('2')

      await cache.invalidateByTag('product')

      await productCache.get('1')
      await productCache.get('2')

      expect(productCache.config.fetch).toHaveBeenCalledTimes(4)
    })
  })
})
```

---

For more testing examples, see the test files in:
- `src/server/__tests__/` - Server-side cache tests
- `src/react/__tests__/` - React integration tests
- `src/utils/__tests__/` - Utility function tests
