# Async TypeScript Patterns

**Official Documentation:**
- [TypeScript Async/Await](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-1-7.html#async-functions)
- [Promise Documentation](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)
- [TypeScript Promise Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#promises)

Complete guide for typing asynchronous operations in TypeScript.

---

## 1. Basic Promise Typing

```typescript
// ❌ DON'T: Implicit any in Promise
async function fetchData(url: string) {
  const response = await fetch(url)
  return response.json()
}

// ✅ DO: Explicit Promise return type
async function fetchData<T>(url: string): Promise<T> {
  const response = await fetch(url)
  return response.json()
}

// ✅ DO: Non-async Promise
function fetchData<T>(url: string): Promise<T> {
  return fetch(url).then(response => response.json())
}

// Usage
interface User {
  id: string
  name: string
  email: string
}

const user = await fetchData<User>('/api/user')
// user is typed as User
```

---

## 2. Promise.all Typing

```typescript
// ✅ DO: Type tuple results
async function fetchMultiple(): Promise<[User, Post[], Comment[]]> {
  const [user, posts, comments] = await Promise.all([
    fetchData<User>('/api/user'),
    fetchData<Post[]>('/api/posts'),
    fetchData<Comment[]>('/api/comments')
  ])

  return [user, posts, comments]
}

// ✅ DO: Homogeneous array
async function fetchUsers(ids: string[]): Promise<User[]> {
  const promises = ids.map(id => fetchData<User>(`/api/users/${id}`))
  return Promise.all(promises)
}

// ✅ DO: Object with typed results
async function fetchDashboardData() {
  const results = await Promise.all({
    user: fetchData<User>('/api/user'),
    posts: fetchData<Post[]>('/api/posts'),
    stats: fetchData<Stats>('/api/stats')
  })

  return results
}

// ✅ BETTER: Using as const for exact types
async function fetchExactData() {
  const [user, posts] = await Promise.all([
    fetchData<User>('/api/user'),
    fetchData<Post[]>('/api/posts')
  ] as const)

  // user: User
  // posts: Post[]
  return { user, posts }
}
```

---

## 3. Promise.race and Promise.any

```typescript
// ✅ DO: Promise.race with union type
async function fetchWithTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number
): Promise<T> {
  const timeout = new Promise<never>((_, reject) => {
    setTimeout(() => reject(new Error('Timeout')), timeoutMs)
  })

  return Promise.race([promise, timeout])
}

// ✅ DO: Promise.any with same type
async function fetchFromMirrors<T>(urls: string[]): Promise<T> {
  const promises = urls.map(url => fetchData<T>(url))
  return Promise.any(promises)
}

// Usage
const user = await fetchWithTimeout(
  fetchData<User>('/api/user'),
  5000
)
```

---

## 4. Error Handling with Types

```typescript
// ✅ DO: Result type pattern
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E }

async function fetchUser(id: string): Promise<Result<User>> {
  try {
    const response = await fetch(`/api/users/${id}`)

    if (!response.ok) {
      return {
        success: false,
        error: new Error(`HTTP ${response.status}`)
      }
    }

    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error : new Error('Unknown error')
    }
  }
}

// Usage
const result = await fetchUser('1')

if (result.success) {
  console.log(result.data.name)  // Type: User
} else {
  console.error(result.error.message)  // Type: Error
}

// ✅ DO: Option type pattern
type Option<T> = T | null

async function findUser(id: string): Promise<Option<User>> {
  try {
    const response = await fetch(`/api/users/${id}`)
    if (!response.ok) return null
    return response.json()
  } catch {
    return null
  }
}

// ✅ DO: Either type pattern
type Either<L, R> =
  | { type: 'left'; value: L }
  | { type: 'right'; value: R }

async function fetchUserEither(id: string): Promise<Either<Error, User>> {
  try {
    const response = await fetch(`/api/users/${id}`)
    if (!response.ok) {
      return { type: 'left', value: new Error(`HTTP ${response.status}`) }
    }
    const user = await response.json()
    return { type: 'right', value: user }
  } catch (error) {
    return {
      type: 'left',
      value: error instanceof Error ? error : new Error('Unknown error')
    }
  }
}
```

---

## 5. Async Generators

```typescript
// ✅ DO: Type async generator
async function* fetchPaginated<T>(
  baseUrl: string,
  pageSize: number = 10
): AsyncGenerator<T[], void, undefined> {
  let page = 1
  let hasMore = true

  while (hasMore) {
    const response = await fetch(`${baseUrl}?page=${page}&size=${pageSize}`)
    const data: T[] = await response.json()

    if (data.length < pageSize) {
      hasMore = false
    }

    yield data
    page++
  }
}

// Usage
for await (const users of fetchPaginated<User>('/api/users')) {
  console.log('Page of users:', users)
}

// ✅ DO: Async generator with return value
async function* processItems<T, R>(
  items: T[],
  processor: (item: T) => Promise<R>
): AsyncGenerator<R, number, undefined> {
  let processed = 0

  for (const item of items) {
    yield await processor(item)
    processed++
  }

  return processed
}

// Usage
const generator = processItems(items, async item => {
  return await processItem(item)
})

for await (const result of generator) {
  console.log('Processed:', result)
}

const total = await generator.next()  // Gets return value
```

---

## 6. Async Iterators

```typescript
// ✅ DO: Type async iterable
interface AsyncIterable<T> {
  [Symbol.asyncIterator](): AsyncIterator<T>
}

interface AsyncIterator<T> {
  next(): Promise<IteratorResult<T>>
}

class PagedDataSource<T> implements AsyncIterable<T> {
  constructor(
    private fetchPage: (page: number) => Promise<T[]>,
    private pageSize: number = 10
  ) {}

  async *[Symbol.asyncIterator](): AsyncIterator<T> {
    let page = 0
    let hasMore = true

    while (hasMore) {
      const items = await this.fetchPage(page)

      if (items.length < this.pageSize) {
        hasMore = false
      }

      for (const item of items) {
        yield item
      }

      page++
    }
  }
}

// Usage
const users = new PagedDataSource<User>(
  page => fetchData<User[]>(`/api/users?page=${page}`)
)

for await (const user of users) {
  console.log(user.name)
}
```

---

## 7. Deferred / Lazy Promises

```typescript
// ✅ DO: Deferred promise type
interface Deferred<T> {
  promise: Promise<T>
  resolve: (value: T) => void
  reject: (reason?: any) => void
}

function createDeferred<T>(): Deferred<T> {
  let resolve!: (value: T) => void
  let reject!: (reason?: any) => void

  const promise = new Promise<T>((res, rej) => {
    resolve = res
    reject = rej
  })

  return { promise, resolve, reject }
}

// Usage
const deferred = createDeferred<User>()

// Later...
deferred.resolve({ id: '1', name: 'Alice', email: 'alice@example.com' })

const user = await deferred.promise

// ✅ DO: Lazy promise
function lazy<T>(factory: () => Promise<T>): () => Promise<T> {
  let promise: Promise<T> | null = null

  return () => {
    if (!promise) {
      promise = factory()
    }
    return promise
  }
}

// Usage
const getUser = lazy(() => fetchData<User>('/api/user'))

// Not called yet
const user1 = await getUser()  // Calls API
const user2 = await getUser()  // Returns cached promise
```

---

## 8. Retry Logic

```typescript
// ✅ DO: Retry with exponential backoff
async function retry<T>(
  fn: () => Promise<T>,
  options: {
    maxAttempts: number
    delayMs: number
    backoff?: number
  }
): Promise<T> {
  const { maxAttempts, delayMs, backoff = 2 } = options

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn()
    } catch (error) {
      if (attempt === maxAttempts) {
        throw error
      }

      const delay = delayMs * Math.pow(backoff, attempt - 1)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }

  throw new Error('Retry failed')
}

// Usage
const user = await retry(
  () => fetchData<User>('/api/user'),
  {
    maxAttempts: 3,
    delayMs: 1000,
    backoff: 2
  }
)

// ✅ DO: Retry with condition
async function retryIf<T>(
  fn: () => Promise<T>,
  shouldRetry: (error: unknown) => boolean,
  maxAttempts: number = 3
): Promise<T> {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn()
    } catch (error) {
      if (attempt === maxAttempts || !shouldRetry(error)) {
        throw error
      }
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt))
    }
  }

  throw new Error('Retry failed')
}

// Usage
const data = await retryIf(
  () => fetchData<User>('/api/user'),
  error => error instanceof NetworkError,
  3
)
```

---

## 9. Timeout Utilities

```typescript
// ✅ DO: Add timeout to any promise
async function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
  errorMessage?: string
): Promise<T> {
  const timeout = new Promise<never>((_, reject) => {
    setTimeout(
      () => reject(new Error(errorMessage ?? `Timeout after ${timeoutMs}ms`)),
      timeoutMs
    )
  })

  return Promise.race([promise, timeout])
}

// Usage
const user = await withTimeout(
  fetchData<User>('/api/user'),
  5000,
  'Failed to fetch user'
)

// ✅ DO: Timeout with cleanup
async function withTimeoutAndCleanup<T>(
  promise: Promise<T>,
  timeoutMs: number,
  cleanup?: () => void
): Promise<T> {
  let timeoutId: NodeJS.Timeout | null = null

  const timeout = new Promise<never>((_, reject) => {
    timeoutId = setTimeout(() => {
      cleanup?.()
      reject(new Error(`Timeout after ${timeoutMs}ms`))
    }, timeoutMs)
  })

  try {
    const result = await Promise.race([promise, timeout])
    if (timeoutId) clearTimeout(timeoutId)
    return result
  } catch (error) {
    if (timeoutId) clearTimeout(timeoutId)
    throw error
  }
}
```

---

## 10. Parallel Execution with Concurrency Limit

```typescript
// ✅ DO: Limit concurrent promises
async function parallelLimit<T, R>(
  items: T[],
  concurrency: number,
  fn: (item: T) => Promise<R>
): Promise<R[]> {
  const results: R[] = []
  const executing: Promise<void>[] = []

  for (const item of items) {
    const promise = fn(item).then(result => {
      results.push(result)
    })

    executing.push(promise)

    if (executing.length >= concurrency) {
      await Promise.race(executing)
      executing.splice(
        executing.findIndex(p => p === promise),
        1
      )
    }
  }

  await Promise.all(executing)
  return results
}

// Usage
const userIds = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

const users = await parallelLimit(
  userIds,
  3,  // Max 3 concurrent requests
  id => fetchData<User>(`/api/users/${id}`)
)

// ✅ DO: Queue-based concurrency
class AsyncQueue<T, R> {
  private queue: Array<() => Promise<R>> = []
  private running = 0

  constructor(private concurrency: number) {}

  async add(fn: () => Promise<R>): Promise<R> {
    return new Promise((resolve, reject) => {
      this.queue.push(async () => {
        try {
          const result = await fn()
          resolve(result)
        } catch (error) {
          reject(error)
        }
      })

      this.process()
    })
  }

  private async process(): Promise<void> {
    if (this.running >= this.concurrency || this.queue.length === 0) {
      return
    }

    this.running++
    const fn = this.queue.shift()!

    try {
      await fn()
    } finally {
      this.running--
      this.process()
    }
  }
}

// Usage
const queue = new AsyncQueue<User, void>(3)

for (const id of userIds) {
  queue.add(() => fetchData<User>(`/api/users/${id}`))
}
```

---

## 11. Async Caching

```typescript
// ✅ DO: Cached async function
function cached<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  keyFn: (...args: Parameters<T>) => string = (...args) => JSON.stringify(args)
): T {
  const cache = new Map<string, Promise<Awaited<ReturnType<T>>>>()

  return ((...args: Parameters<T>) => {
    const key = keyFn(...args)

    if (cache.has(key)) {
      return cache.get(key)!
    }

    const promise = fn(...args)
    cache.set(key, promise)

    // Remove from cache on error
    promise.catch(() => cache.delete(key))

    return promise
  }) as T
}

// Usage
const cachedFetchUser = cached(
  (id: string) => fetchData<User>(`/api/users/${id}`)
)

const user1 = await cachedFetchUser('1')  // Fetches
const user2 = await cachedFetchUser('1')  // Returns cached

// ✅ DO: TTL cache
class TTLCache<K, V> {
  private cache = new Map<K, { value: Promise<V>; expiry: number }>()

  async get(
    key: K,
    factory: () => Promise<V>,
    ttlMs: number = 60000
  ): Promise<V> {
    const cached = this.cache.get(key)

    if (cached && Date.now() < cached.expiry) {
      return cached.value
    }

    const promise = factory()
    this.cache.set(key, {
      value: promise,
      expiry: Date.now() + ttlMs
    })

    return promise
  }

  clear(): void {
    this.cache.clear()
  }
}

// Usage
const cache = new TTLCache<string, User>()

const user = await cache.get(
  '1',
  () => fetchData<User>('/api/users/1'),
  60000  // 1 minute TTL
)
```

---

## 12. Async Event Emitter

```typescript
// ✅ DO: Type-safe async event emitter
type EventMap = Record<string, any>

class AsyncEventEmitter<Events extends EventMap> {
  private listeners = new Map<keyof Events, Set<(data: any) => Promise<void>>>()

  on<K extends keyof Events>(
    event: K,
    listener: (data: Events[K]) => Promise<void>
  ): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(listener)
  }

  async emit<K extends keyof Events>(event: K, data: Events[K]): Promise<void> {
    const listeners = this.listeners.get(event)
    if (!listeners) return

    await Promise.all(
      Array.from(listeners).map(listener => listener(data))
    )
  }

  off<K extends keyof Events>(
    event: K,
    listener: (data: Events[K]) => Promise<void>
  ): void {
    this.listeners.get(event)?.delete(listener)
  }
}

// Usage
interface AppEvents {
  'user:created': { id: string; name: string }
  'user:updated': { id: string; changes: Partial<User> }
  'user:deleted': { id: string }
}

const emitter = new AsyncEventEmitter<AppEvents>()

emitter.on('user:created', async user => {
  await sendWelcomeEmail(user.id)
})

await emitter.emit('user:created', { id: '1', name: 'Alice' })
```

---

## 13. AbortController Integration

```typescript
// ✅ DO: Cancellable fetch
async function fetchWithAbort<T>(
  url: string,
  signal: AbortSignal
): Promise<T> {
  const response = await fetch(url, { signal })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  return response.json()
}

// Usage
const controller = new AbortController()

setTimeout(() => controller.abort(), 5000)  // Cancel after 5s

try {
  const user = await fetchWithAbort<User>('/api/user', controller.signal)
  console.log(user)
} catch (error) {
  if (error instanceof Error && error.name === 'AbortError') {
    console.log('Request was aborted')
  }
}

// ✅ DO: Cancellable async operation
async function runWithAbort<T>(
  fn: (signal: AbortSignal) => Promise<T>,
  timeoutMs?: number
): Promise<T> {
  const controller = new AbortController()

  if (timeoutMs) {
    setTimeout(() => controller.abort(), timeoutMs)
  }

  try {
    return await fn(controller.signal)
  } finally {
    controller.abort()  // Cleanup
  }
}

// Usage
const result = await runWithAbort(
  async signal => {
    const response = await fetch('/api/data', { signal })
    return response.json()
  },
  5000
)
```

---

## Test Requirements

```typescript
describe('Async Functions', () => {
  describe('fetchUser', () => {
    it('should fetch user successfully', async () => {
      const user = await fetchUser('1')
      expect(user.id).toBe('1')
    })

    it('should handle errors', async () => {
      await expect(fetchUser('invalid')).rejects.toThrow()
    })
  })

  describe('retry', () => {
    it('should retry on failure', async () => {
      let attempts = 0
      const fn = vi.fn(async () => {
        attempts++
        if (attempts < 3) throw new Error('Failed')
        return 'success'
      })

      const result = await retry(fn, { maxAttempts: 3, delayMs: 100 })
      expect(result).toBe('success')
      expect(fn).toHaveBeenCalledTimes(3)
    })
  })

  describe('withTimeout', () => {
    it('should timeout slow promises', async () => {
      const slow = new Promise(resolve => setTimeout(resolve, 1000))
      await expect(withTimeout(slow, 100)).rejects.toThrow('Timeout')
    })
  })
})
```

---

## Quick Reference

| Pattern | Use Case | Example |
|---------|----------|---------|
| `Promise<T>` | Async return | `async (): Promise<User>` |
| `Promise.all` | Parallel execution | Multiple fetches |
| Result type | Error handling | `Result<T, E>` |
| Async generator | Streaming data | Pagination |
| Retry | Transient failures | Network requests |
| Timeout | Slow operations | API calls |
| Concurrency limit | Resource control | Batch processing |
| Cache | Performance | Expensive operations |
| AbortController | Cancellation | User-initiated cancel |
