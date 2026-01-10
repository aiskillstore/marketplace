# Async Testing Patterns

**Comprehensive patterns for testing asynchronous code with Vitest.**

Async code is everywhere in modern JavaScript - API calls, database queries, file operations, timers. Testing async code requires understanding promises, async/await, and timing control.

---

## 🎯 Core Principles

### Rules for Async Tests
1. **Always use `async/await`** in test functions
2. **Always `await` async assertions**
3. **Don't mix callbacks and promises** - use one pattern
4. **Control timing** with fake timers when needed
5. **Test loading states** and error states

---

## ⏳ Testing Promises

### Basic Promise Testing

```typescript
import { describe, it, expect } from 'vitest'

describe('Promise testing', () => {
  it('tests resolved promise', async () => {
    const promise = Promise.resolve(42)

    await expect(promise).resolves.toBe(42)
  })

  it('tests rejected promise', async () => {
    const promise = Promise.reject(new Error('Failed'))

    await expect(promise).rejects.toThrow('Failed')
  })

  it('tests async function', async () => {
    async function fetchData() {
      return { data: 'test' }
    }

    const result = await fetchData()
    expect(result.data).toBe('test')
  })
})
```

### Testing Multiple Promises

```typescript
describe('Multiple promises', () => {
  it('waits for all promises', async () => {
    const promises = [
      Promise.resolve(1),
      Promise.resolve(2),
      Promise.resolve(3)
    ]

    const results = await Promise.all(promises)

    expect(results).toEqual([1, 2, 3])
  })

  it('handles Promise.race', async () => {
    const slow = new Promise(resolve => setTimeout(() => resolve('slow'), 100))
    const fast = Promise.resolve('fast')

    const result = await Promise.race([slow, fast])

    expect(result).toBe('fast')
  })
})
```

---

## 🌐 Testing API Calls

### Mocking fetch

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('API client', () => {
  beforeEach(() => {
    global.fetch = vi.fn()
  })

  it('fetches user data', async () => {
    const mockUser = { id: '1', name: 'John' }

    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => mockUser
    } as Response)

    const user = await fetchUser('1')

    expect(fetch).toHaveBeenCalledWith('/api/users/1')
    expect(user).toEqual(mockUser)
  })

  it('handles 404 error', async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found'
    } as Response)

    await expect(fetchUser('999')).rejects.toThrow('User not found')
  })

  it('handles network errors', async () => {
    vi.mocked(global.fetch).mockRejectedValue(new Error('Network error'))

    await expect(fetchUser('1')).rejects.toThrow('Network error')
  })
})
```

### Using MSW (Mock Service Worker)

```typescript
import { rest } from 'msw'
import { setupServer } from 'msw/node'
import { beforeAll, afterEach, afterAll } from 'vitest'

// Setup MSW server
const server = setupServer(
  rest.get('/api/users/:id', (req, res, ctx) => {
    return res(ctx.json({ id: req.params.id, name: 'John' }))
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('API with MSW', () => {
  it('fetches user', async () => {
    const user = await fetchUser('123')

    expect(user).toEqual({ id: '123', name: 'John' })
  })

  it('handles custom response for specific test', async () => {
    server.use(
      rest.get('/api/users/:id', (req, res, ctx) => {
        return res(ctx.status(500))
      })
    )

    await expect(fetchUser('123')).rejects.toThrow()
  })
})
```

---

## ⏰ Testing with Timers

### Fake Timers

```typescript
import { vi, beforeEach, afterEach } from 'vitest'

describe('Timer testing', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('executes setTimeout callback', () => {
    const callback = vi.fn()

    setTimeout(callback, 1000)

    expect(callback).not.toHaveBeenCalled()

    // Advance time
    vi.advanceTimersByTime(1000)

    expect(callback).toHaveBeenCalledTimes(1)
  })

  it('executes setInterval callback multiple times', () => {
    const callback = vi.fn()

    setInterval(callback, 1000)

    vi.advanceTimersByTime(3000)

    expect(callback).toHaveBeenCalledTimes(3)
  })

  it('runs all pending timers', () => {
    const callback1 = vi.fn()
    const callback2 = vi.fn()

    setTimeout(callback1, 1000)
    setTimeout(callback2, 2000)

    vi.runAllTimers()

    expect(callback1).toHaveBeenCalled()
    expect(callback2).toHaveBeenCalled()
  })
})
```

### Async Timer Control

```typescript
describe('Async timer testing', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('handles async operations with timers', async () => {
    const callback = vi.fn()

    setTimeout(callback, 1000)

    // Advance timers asynchronously
    await vi.advanceTimersByTimeAsync(1000)

    expect(callback).toHaveBeenCalled()
  })

  it('waits for all async timers', async () => {
    const callback = vi.fn()

    setTimeout(callback, 1000)

    await vi.runAllTimersAsync()

    expect(callback).toHaveBeenCalled()
  })
})
```

### Controlling Date.now()

```typescript
describe('Date testing', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  it('controls current time', () => {
    const fixedTime = new Date('2024-01-15T10:00:00Z')
    vi.setSystemTime(fixedTime)

    expect(Date.now()).toBe(fixedTime.getTime())
    expect(new Date().toISOString()).toBe('2024-01-15T10:00:00.000Z')
  })

  it('advances time for time-dependent logic', () => {
    vi.setSystemTime(new Date('2024-01-15T10:00:00Z'))

    const createdAt = Date.now()

    // Advance 1 hour
    vi.advanceTimersByTime(3600000)

    const expiresAt = Date.now()

    expect(expiresAt - createdAt).toBe(3600000)
  })
})
```

---

## 🔄 Testing Async/Await Functions

### Basic Async Testing

```typescript
describe('Async functions', () => {
  it('tests async function with await', async () => {
    async function getData() {
      return { value: 42 }
    }

    const result = await getData()

    expect(result.value).toBe(42)
  })

  it('tests async error handling', async () => {
    async function failingFunction() {
      throw new Error('Operation failed')
    }

    await expect(failingFunction()).rejects.toThrow('Operation failed')
  })
})
```

### Testing Sequential Async Operations

```typescript
it('processes items sequentially', async () => {
  const results: number[] = []

  async function processItem(item: number) {
    await new Promise(resolve => setTimeout(resolve, 10))
    results.push(item * 2)
  }

  for (const item of [1, 2, 3]) {
    await processItem(item)
  }

  expect(results).toEqual([2, 4, 6])
})
```

### Testing Parallel Async Operations

```typescript
it('processes items in parallel', async () => {
  const mockApi = {
    fetch: vi.fn().mockResolvedValue({ data: 'success' })
  }

  const promises = [
    mockApi.fetch('/endpoint1'),
    mockApi.fetch('/endpoint2'),
    mockApi.fetch('/endpoint3')
  ]

  const results = await Promise.all(promises)

  expect(results).toHaveLength(3)
  expect(mockApi.fetch).toHaveBeenCalledTimes(3)
  expect(results.every(r => r.data === 'success')).toBe(true)
})
```

---

## 🎭 Testing Loading States

### React Component Loading

```typescript
import { render, screen, waitFor } from '@testing-library/react'

describe('AsyncComponent', () => {
  it('shows loading state initially', () => {
    vi.mocked(fetchData).mockImplementation(() => new Promise(() => {}))

    render(<AsyncComponent />)

    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })

  it('shows data when loaded', async () => {
    vi.mocked(fetchData).mockResolvedValue({ name: 'John' })

    render(<AsyncComponent />)

    await waitFor(() => {
      expect(screen.getByText('John')).toBeInTheDocument()
    })

    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
  })

  it('shows error state on failure', async () => {
    vi.mocked(fetchData).mockRejectedValue(new Error('Failed'))

    render(<AsyncComponent />)

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument()
    })
  })
})
```

---

## 🔁 Testing Retry Logic

```typescript
describe('Retry logic', () => {
  it('retries on failure', async () => {
    const mockApi = vi.fn()
      .mockRejectedValueOnce(new Error('Fail 1'))
      .mockRejectedValueOnce(new Error('Fail 2'))
      .mockResolvedValueOnce({ data: 'success' })

    async function fetchWithRetry(maxRetries = 3) {
      for (let i = 0; i < maxRetries; i++) {
        try {
          return await mockApi()
        } catch (error) {
          if (i === maxRetries - 1) throw error
        }
      }
    }

    const result = await fetchWithRetry(3)

    expect(mockApi).toHaveBeenCalledTimes(3)
    expect(result.data).toBe('success')
  })

  it('throws after max retries', async () => {
    const mockApi = vi.fn().mockRejectedValue(new Error('Always fails'))

    async function fetchWithRetry(maxRetries = 3) {
      for (let i = 0; i < maxRetries; i++) {
        try {
          return await mockApi()
        } catch (error) {
          if (i === maxRetries - 1) throw error
        }
      }
    }

    await expect(fetchWithRetry(3)).rejects.toThrow('Always fails')
    expect(mockApi).toHaveBeenCalledTimes(3)
  })
})
```

---

## 🎯 Testing Race Conditions

```typescript
describe('Race conditions', () => {
  it('handles concurrent updates correctly', async () => {
    let value = 0
    const lock = { locked: false }

    async function incrementWithLock() {
      // Wait for lock
      while (lock.locked) {
        await new Promise(resolve => setTimeout(resolve, 1))
      }

      lock.locked = true
      const current = value
      await new Promise(resolve => setTimeout(resolve, 5))
      value = current + 1
      lock.locked = false
    }

    // Run concurrent increments
    await Promise.all([
      incrementWithLock(),
      incrementWithLock(),
      incrementWithLock()
    ])

    expect(value).toBe(3) // Should be 3, not random
  })
})
```

---

## 📋 Best Practices

### ✅ Do

- **Always use `async/await`** in test functions
- **Always `await`** async matchers (`resolves`, `rejects`)
- **Use fake timers** for time-dependent code
- **Test all states** - loading, success, error
- **Mock external APIs** - don't make real network calls
- **Test retry logic** and timeout handling

### ❌ Don't

- **Forget `await`** - common source of flaky tests
- **Use real timers** for time-dependent tests
- **Make real API calls** in tests
- **Ignore error states** - always test failures
- **Mix callback and promise** patterns
- **Use `done` callback** - prefer async/await

---

## 🔗 Related Patterns

- **[Component Testing](component-testing.md)** - Async component loading
- **[Test Doubles](test-doubles.md)** - Mock async APIs
- **[API Testing](api-testing.md)** - HTTP client testing
- **[F.I.R.S.T Principles](../principles/first-principles.md#repeatable)** - Repeatable async tests

---

**Next Steps:**
- Review [Vitest Async API](https://vitest.dev/guide/features.html#async-tests)
- Explore [MSW for API Mocking](https://mswjs.io/)
- Practice [Error Handling Patterns](error-testing.md)
