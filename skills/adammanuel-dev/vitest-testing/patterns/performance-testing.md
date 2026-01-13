# Performance Testing Patterns

**Comprehensive patterns for measuring and optimizing performance in tests with Vitest.**

Performance testing ensures your code meets performance requirements and identifies bottlenecks before they reach production. Vitest provides built-in benchmarking capabilities and integrates well with Node.js performance APIs.

---

## 🎯 When to Use Performance Tests

Performance tests are appropriate when you need to:

- **Verify algorithmic complexity** - Ensure O(n), O(log n) behavior
- **Detect memory leaks** - Track heap usage over time
- **Measure throughput** - Requests per second, operations per second
- **Test caching effectiveness** - Verify speed improvements
- **Prevent performance regressions** - Catch slowdowns early
- **Validate optimization** - Prove refactorings improve performance

**Don't use performance tests for:**
- Every function (focus on critical paths)
- Simple CRUD operations
- Code that's not performance-sensitive
- When traditional unit tests suffice

---

## ⚡ Benchmarking with Vitest

Vitest includes built-in bench() API for performance benchmarking with statistical significance.

### Basic Benchmarking

```typescript
import { bench, describe } from 'vitest'

describe('Array operations performance', () => {
  // Baseline: Array.push
  bench('Array.push', () => {
    const arr: number[] = []
    for (let i = 0; i < 1000; i++) {
      arr.push(i)
    }
  })

  // Compare with spread operator
  bench('Array spread', () => {
    let arr: number[] = []
    for (let i = 0; i < 1000; i++) {
      arr = [...arr, i] // Much slower
    }
  })

  // Compare with Array.from
  bench('Array.from', () => {
    const arr = Array.from({ length: 1000 }, (_, i) => i)
  })
})

// Run with: vitest bench
// Output shows ops/sec, mean time, standard deviation
```

### Benchmarking with Setup/Teardown

```typescript
import { bench } from 'vitest'

bench(
  'Map operations',
  () => {
    // This is what gets measured
    const map = task.meta.map as Map<string, number>

    for (let i = 0; i < 1000; i++) {
      map.set(`key${i}`, i)
      map.get(`key${i}`)
      map.delete(`key${i}`)
    }
  },
  {
    // Setup runs before each benchmark iteration (not measured)
    setup(task) {
      task.meta = { map: new Map() }
    },

    // Teardown runs after each iteration (not measured)
    teardown(task) {
      (task.meta.map as Map<string, number>).clear()
    }
  }
)
```

### Comparing Implementations

```typescript
describe('String concatenation performance', () => {
  const iterations = 10000

  bench('String concatenation with +', () => {
    let result = ''
    for (let i = 0; i < iterations; i++) {
      result += `item${i},`
    }
  })

  bench('Array.join', () => {
    const items: string[] = []
    for (let i = 0; i < iterations; i++) {
      items.push(`item${i}`)
    }
    const result = items.join(',')
  })

  bench('Template literals', () => {
    let result = ''
    for (let i = 0; i < iterations; i++) {
      result += `item${i},`
    }
  })
})
```

---

## 💾 Memory Usage Testing

Detect memory leaks and track heap consumption.

### Basic Memory Testing

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest'

describe('Memory usage patterns', () => {
  let initialMemory: number

  beforeEach(() => {
    // Force garbage collection if available (run with --expose-gc)
    if (global.gc) {
      global.gc()
    }
    initialMemory = process.memoryUsage().heapUsed
  })

  afterEach(() => {
    if (global.gc) {
      global.gc()
    }
  })

  it('does not leak memory in cache implementation', () => {
    const cache = new Map()
    const dataSize = 10000

    // Fill cache with data
    for (let i = 0; i < dataSize; i++) {
      cache.set(`key${i}`, {
        id: i,
        data: new Array(100).fill(`value${i}`),
        timestamp: Date.now()
      })
    }

    expect(cache.size).toBe(dataSize)

    // Clear cache
    cache.clear()

    // Force garbage collection
    if (global.gc) {
      global.gc()
    }

    // Check memory was released
    const finalMemory = process.memoryUsage().heapUsed
    const memoryGrowth = finalMemory - initialMemory

    // Memory growth should be minimal after clearing
    expect(memoryGrowth).toBeLessThan(1024 * 1024) // Less than 1MB growth
  })
})
```

### Testing for Memory Leaks

```typescript
it('does not leak event listeners', () => {
  class EventEmitter {
    private listeners = new Map<string, Set<Function>>()

    on(event: string, handler: Function) {
      if (!this.listeners.has(event)) {
        this.listeners.set(event, new Set())
      }
      this.listeners.get(event)!.add(handler)
    }

    removeAllListeners() {
      this.listeners.clear()
    }

    getListenerCount(): number {
      let count = 0
      for (const handlers of this.listeners.values()) {
        count += handlers.size
      }
      return count
    }
  }

  const emitter = new EventEmitter()

  // Add many listeners
  const listenerCount = 10000
  for (let i = 0; i < listenerCount; i++) {
    emitter.on(`event${i % 100}`, () => console.log(i))
  }

  expect(emitter.getListenerCount()).toBe(listenerCount)

  // Cleanup
  const memoryBefore = process.memoryUsage().heapUsed
  emitter.removeAllListeners()

  if (global.gc) global.gc()

  const memoryAfter = process.memoryUsage().heapUsed

  expect(emitter.getListenerCount()).toBe(0)
  // Memory should be released
  expect(memoryAfter).toBeLessThan(memoryBefore + 1024 * 1024)
})
```

### Large Dataset Handling

```typescript
it('handles large datasets efficiently', () => {
  const processLargeDataset = (size: number) => {
    const results = []

    // Process in chunks to avoid memory spikes
    const chunkSize = 1000
    for (let i = 0; i < size; i += chunkSize) {
      const chunk = []
      for (let j = i; j < Math.min(i + chunkSize, size); j++) {
        chunk.push({ index: j, value: Math.random() })
      }

      // Process chunk and only keep summary
      results.push({
        start: i,
        end: Math.min(i + chunkSize, size),
        average: chunk.reduce((sum, item) => sum + item.value, 0) / chunk.length
      })
    }

    return results
  }

  const memoryBefore = process.memoryUsage().heapUsed
  const results = processLargeDataset(100000)
  const memoryAfter = process.memoryUsage().heapUsed

  const memoryUsed = (memoryAfter - memoryBefore) / 1024 / 1024

  expect(results).toHaveLength(100)
  expect(memoryUsed).toBeLessThan(10) // Should use less than 10MB
})
```

---

## 📊 Time Complexity Verification

Verify algorithms perform within expected complexity bounds.

### O(n) Linear Complexity

```typescript
import { describe, it, expect } from 'vitest'

describe('Algorithm time complexity', () => {
  const measureTime = (fn: () => void): number => {
    const start = performance.now()
    fn()
    return performance.now() - start
  }

  it('has O(n) complexity for linear search', () => {
    const linearSearch = (arr: number[], target: number): number => {
      for (let i = 0; i < arr.length; i++) {
        if (arr[i] === target) return i
      }
      return -1
    }

    // Test with different sizes
    const sizes = [1000, 2000, 4000, 8000]
    const times: number[] = []

    for (const size of sizes) {
      const arr = Array.from({ length: size }, (_, i) => i)
      const time = measureTime(() => {
        // Worst case: search for last element
        linearSearch(arr, size - 1)
      })
      times.push(time)
    }

    // Verify linear growth
    // Time should approximately double when size doubles
    for (let i = 1; i < times.length; i++) {
      const ratio = times[i] / times[i - 1]
      // Allow variance but should be roughly 2x
      expect(ratio).toBeGreaterThan(1.5)
      expect(ratio).toBeLessThan(2.5)
    }
  })
})
```

### O(log n) Logarithmic Complexity

```typescript
it('has O(log n) complexity for binary search', () => {
  const binarySearch = (arr: number[], target: number): number => {
    let left = 0
    let right = arr.length - 1

    while (left <= right) {
      const mid = Math.floor((left + right) / 2)
      if (arr[mid] === target) return mid
      if (arr[mid] < target) left = mid + 1
      else right = mid - 1
    }

    return -1
  }

  const sizes = [1000, 10000, 100000, 1000000]
  const times: number[] = []

  for (const size of sizes) {
    const arr = Array.from({ length: size }, (_, i) => i)

    // Run multiple iterations for stable measurement
    const iterations = 10000
    const time = measureTime(() => {
      for (let i = 0; i < iterations; i++) {
        binarySearch(arr, Math.floor(Math.random() * size))
      }
    })

    times.push(time / iterations)
  }

  // For O(log n), when size increases by 10x, time should increase much less
  for (let i = 1; i < times.length; i++) {
    const ratio = times[i] / times[i - 1]
    // Should be much less than 10x increase
    expect(ratio).toBeLessThan(3)
  }
})
```

---

## 🔄 Load Testing

Test system behavior under load.

### Concurrent Requests

```typescript
describe('Load testing', () => {
  it('handles concurrent requests', async () => {
    const processRequest = async (id: number): Promise<{ id: number; result: string }> => {
      // Simulate async processing
      await new Promise(resolve => setTimeout(resolve, Math.random() * 10))
      return { id, result: `processed-${id}` }
    }

    const concurrentRequests = 100
    const start = performance.now()

    // Launch all requests concurrently
    const promises = Array.from(
      { length: concurrentRequests },
      (_, i) => processRequest(i)
    )

    const results = await Promise.all(promises)
    const duration = performance.now() - start

    expect(results).toHaveLength(concurrentRequests)
    expect(results.every(r => r.result.startsWith('processed-'))).toBe(true)

    // Should complete all requests within reasonable time
    expect(duration).toBeLessThan(1000) // Less than 1 second

    // Calculate throughput
    const throughput = (concurrentRequests / duration) * 1000 // req/sec
    expect(throughput).toBeGreaterThan(100) // At least 100 req/s
  })
})
```

### Rate Limiting

```typescript
it('throttles requests appropriately', async () => {
  const rateLimiter = {
    tokens: 10,
    refillRate: 5, // tokens per second
    lastRefill: Date.now(),

    async acquire(): Promise<boolean> {
      const now = Date.now()
      const timePassed = (now - this.lastRefill) / 1000
      const tokensToAdd = Math.floor(timePassed * this.refillRate)

      if (tokensToAdd > 0) {
        this.tokens = Math.min(10, this.tokens + tokensToAdd)
        this.lastRefill = now
      }

      if (this.tokens > 0) {
        this.tokens--
        return true
      }

      return false
    }
  }

  const makeRequest = async (): Promise<boolean> => {
    const allowed = await rateLimiter.acquire()
    if (!allowed) return false

    // Simulate request processing
    await new Promise(resolve => setTimeout(resolve, 10))
    return true
  }

  // Try to make many requests rapidly
  const attempts = 50
  const results = await Promise.all(
    Array.from({ length: attempts }, () => makeRequest())
  )

  const successful = results.filter(r => r === true).length
  const rejected = results.filter(r => r === false).length

  // Should allow initial burst plus refilled tokens
  expect(successful).toBeGreaterThan(0)
  expect(successful).toBeLessThanOrEqual(15) // Initial 10 + some refilled
  expect(rejected).toBeGreaterThan(0) // Some should be rate limited
})
```

---

## 🧹 Resource Cleanup Performance

Test that cleanup operations are efficient.

### Connection Pool Cleanup

```typescript
it('cleans up connection pool efficiently', async () => {
  class ConnectionPool {
    private connections: any[] = []
    private available: any[] = []
    private maxSize = 10
    private createCount = 0
    private destroyCount = 0

    async acquire() {
      if (this.available.length > 0) {
        return this.available.pop()
      }

      if (this.connections.length < this.maxSize) {
        const conn = await this.createConnection()
        this.connections.push(conn)
        return conn
      }

      // Wait for available connection
      await new Promise(resolve => setTimeout(resolve, 10))
      return this.acquire()
    }

    release(conn: any) {
      this.available.push(conn)
    }

    async createConnection() {
      this.createCount++
      await new Promise(resolve => setTimeout(resolve, 1))
      return { id: this.createCount, createdAt: Date.now() }
    }

    async destroy() {
      const start = performance.now()

      await Promise.all(
        this.connections.map(async conn => {
          await new Promise(resolve => setTimeout(resolve, 1))
          this.destroyCount++
        })
      )

      this.connections = []
      this.available = []

      return performance.now() - start
    }

    getStats() {
      return {
        created: this.createCount,
        destroyed: this.destroyCount,
        total: this.connections.length,
        available: this.available.length
      }
    }
  }

  const pool = new ConnectionPool()

  // Simulate concurrent usage
  const operations = Array.from({ length: 50 }, async () => {
    const conn = await pool.acquire()
    await new Promise(resolve => setTimeout(resolve, Math.random() * 5))
    pool.release(conn)
  })

  await Promise.all(operations)

  const stats = pool.getStats()
  expect(stats.created).toBeLessThanOrEqual(10) // Should reuse connections

  // Cleanup should be fast (parallel)
  const destroyTime = await pool.destroy()
  expect(destroyTime).toBeLessThan(50) // Parallel cleanup

  const finalStats = pool.getStats()
  expect(finalStats.destroyed).toBe(stats.created)
  expect(finalStats.total).toBe(0)
})
```

---

## 🗄️ Caching Performance

Test cache effectiveness.

### Cache Hit Ratio

```typescript
describe('Cache performance', () => {
  it('demonstrates cache effectiveness', async () => {
    const expensiveOperation = vi.fn(async (key: string) => {
      // Simulate expensive computation
      await new Promise(resolve => setTimeout(resolve, 100))
      return `result-${key}`
    })

    class Cache {
      private store = new Map<string, { value: any; timestamp: number }>()
      private ttl = 1000 // 1 second TTL

      async get(key: string, factory: () => Promise<any>) {
        const cached = this.store.get(key)

        if (cached && Date.now() - cached.timestamp < this.ttl) {
          return cached.value
        }

        const value = await factory()
        this.store.set(key, { value, timestamp: Date.now() })
        return value
      }
    }

    const cache = new Cache()

    // First call - cache miss
    const start1 = performance.now()
    const result1 = await cache.get('key1', () => expensiveOperation('key1'))
    const time1 = performance.now() - start1

    expect(result1).toBe('result-key1')
    expect(expensiveOperation).toHaveBeenCalledTimes(1)
    expect(time1).toBeGreaterThan(90) // Should take ~100ms

    // Second call - cache hit
    const start2 = performance.now()
    const result2 = await cache.get('key1', () => expensiveOperation('key1'))
    const time2 = performance.now() - start2

    expect(result2).toBe('result-key1')
    expect(expensiveOperation).toHaveBeenCalledTimes(1) // Not called again
    expect(time2).toBeLessThan(10) // Should be instant

    // Performance improvement ratio
    const speedup = time1 / time2
    expect(speedup).toBeGreaterThan(10) // At least 10x faster
  })
})
```

### LRU Cache Performance

```typescript
it('handles LRU eviction efficiently', () => {
  class LRUCache {
    private cache = new Map<string, any>()
    private maxSize: number

    constructor(maxSize: number) {
      this.maxSize = maxSize
    }

    get(key: string): any {
      if (!this.cache.has(key)) return undefined

      // Move to end (most recent)
      const value = this.cache.get(key)
      this.cache.delete(key)
      this.cache.set(key, value)
      return value
    }

    set(key: string, value: any): void {
      // Remove if exists to update position
      if (this.cache.has(key)) {
        this.cache.delete(key)
      }

      // Evict oldest if at capacity
      if (this.cache.size >= this.maxSize) {
        const firstKey = this.cache.keys().next().value
        this.cache.delete(firstKey)
      }

      this.cache.set(key, value)
    }

    getSize(): number {
      return this.cache.size
    }
  }

  const cache = new LRUCache(3)
  const operations = 10000

  const start = performance.now()

  for (let i = 0; i < operations; i++) {
    const key = `key${i % 10}` // 10 unique keys
    cache.set(key, i)

    // Occasionally read to test reordering
    if (i % 3 === 0) {
      cache.get(`key${(i - 1) % 10}`)
    }
  }

  const duration = performance.now() - start

  expect(cache.getSize()).toBe(3) // Should maintain max size
  expect(duration).toBeLessThan(100) // Should complete quickly

  // Operations per millisecond
  const opsPerMs = operations / duration
  expect(opsPerMs).toBeGreaterThan(100) // At least 100 ops/ms
})
```

---

## 📋 Best Practices

### ✅ Do

- **Focus on critical paths** - Performance test hot code paths
- **Establish baselines** - Know current performance before optimizing
- **Test different scales** - Small, medium, large datasets
- **Use realistic data** - Representative of production
- **Run multiple iterations** - Reduce noise, get statistical significance
- **Test cleanup** - Ensure resources are released efficiently
- **Document expectations** - Add comments explaining thresholds

### ❌ Don't

- **Performance test everything** - Only test performance-critical code
- **Ignore variance** - Account for statistical noise
- **Test in isolation only** - Consider integration performance
- **Optimize prematurely** - Profile first, then optimize
- **Forget about memory** - Track heap usage alongside speed
- **Use arbitrary thresholds** - Base limits on requirements

---

## 🔗 Related Patterns

- **[F.I.R.S.T Principles](../principles/first-principles.md#fast)** - Fast test execution
- **[Test Data](test-data.md)** - Generate large datasets for load testing
- **[Test Doubles](test-doubles.md)** - Mock slow dependencies

---

**Next Steps:**
- Review [Vitest Bench API](https://vitest.dev/api/#bench)
- Explore [Node.js Performance Hooks](https://nodejs.org/api/perf_hooks.html)
- Profile with [Chrome DevTools](https://developer.chrome.com/docs/devtools/performance/)
