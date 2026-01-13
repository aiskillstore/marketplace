# Test Doubles (Mocks, Stubs, Spies, Fakes)

**Advanced patterns for isolating code under test using test doubles in Vitest.**

Test doubles are objects that replace real dependencies in tests, allowing you to isolate the code under test and control its environment. Understanding when and how to use each type is crucial for writing effective, maintainable tests.

---

## 🎯 Decision Matrix: Choosing the Right Test Double

| Scenario | Use | Vitest Tool | Example |
|----------|-----|-------------|---------|
| **Verify function was called** | Spy | `vi.spyOn()` | Logging, analytics tracking |
| **Replace external API** | Mock | `vi.mock()` | HTTP requests, database calls |
| **Return specific values** | Stub | `vi.fn().mockReturnValue()` | Configuration, feature flags |
| **Lightweight replacement** | Fake | In-memory implementation | In-memory database, file system |
| **Control time** | Fake Timers | `vi.useFakeTimers()` | Timeouts, intervals, Date.now() |

---

## 📚 Types of Test Doubles

### 1. Mock
**Purpose:** Verify interactions (function calls, arguments, call count)

```typescript
import { vi } from 'vitest'

// Mock entire module
vi.mock('./email-service', () => ({
  sendEmail: vi.fn().mockResolvedValue({ success: true })
}))

import { sendEmail } from './email-service'

it('sends welcome email on registration', async () => {
  await userService.register({ email: 'test@example.com' })

  // Verify the interaction
  expect(sendEmail).toHaveBeenCalledWith(
    expect.objectContaining({
      to: 'test@example.com',
      template: 'welcome'
    })
  )
  expect(sendEmail).toHaveBeenCalledTimes(1)
})
```

### 2. Stub
**Purpose:** Provide predetermined responses

```typescript
it('handles API response', async () => {
  const stubApi = {
    fetchUser: vi.fn().mockResolvedValue({
      id: '123',
      name: 'John Doe'
    })
  }

  const service = new UserService(stubApi)
  const user = await service.getUser('123')

  expect(user.name).toBe('John Doe')
  // Don't care about how many times it was called
})
```

### 3. Spy
**Purpose:** Observe real object while tracking calls

```typescript
it('calls logger with correct message', () => {
  const logger = {
    log: (message: string) => console.log(message)
  }

  const spy = vi.spyOn(logger, 'log')

  service.processOrder(order, logger)

  expect(spy).toHaveBeenCalledWith('Order processed: order-123')
  spy.mockRestore() // Restore original implementation
})
```

### 4. Fake
**Purpose:** Working implementation with shortcuts

```typescript
class FakeDatabase {
  private data = new Map<string, any>()

  async save(key: string, value: any) {
    this.data.set(key, value)
    return value
  }

  async find(key: string) {
    return this.data.get(key)
  }

  async delete(key: string) {
    this.data.delete(key)
  }
}

it('saves user to database', async () => {
  const db = new FakeDatabase()
  const service = new UserService(db)

  await service.createUser({ name: 'Alice' })

  const saved = await db.find('user-1')
  expect(saved.name).toBe('Alice')
})
```

---

## 🏭 Factory Pattern for Mocks

Create reusable mock factories for consistent test data:

```typescript
// mockFactories.ts
import { vi } from 'vitest'

export const createMockUser = (overrides = {}) => ({
  id: '123',
  name: 'Test User',
  email: 'test@example.com',
  roles: ['user'],
  createdAt: new Date('2024-01-01'),
  ...overrides
})

export const createMockApiClient = () => ({
  get: vi.fn().mockResolvedValue({ data: [] }),
  post: vi.fn().mockResolvedValue({ data: { success: true } }),
  put: vi.fn().mockResolvedValue({ data: { updated: true } }),
  delete: vi.fn().mockResolvedValue({ data: { deleted: true } })
})

export const createMockDatabase = () => {
  const data = new Map()

  return {
    query: vi.fn((id) => data.get(id)),
    save: vi.fn((id, value) => {
      data.set(id, value)
      return value
    }),
    delete: vi.fn((id) => data.delete(id)),
    clear: () => data.clear(),
    _getData: () => data // For test inspection
  }
}

// Usage in tests
describe('User service', () => {
  it('processes user with admin role', () => {
    const admin = createMockUser({ roles: ['admin'] })
    const apiClient = createMockApiClient()

    const service = new UserService(apiClient)
    service.processUser(admin)

    expect(apiClient.post).toHaveBeenCalledWith('/admin-actions', admin)
  })
})
```

---

## 🔀 Partial Mocking

Mock only specific parts while keeping the rest real:

```typescript
import { vi } from 'vitest'

// Partial mock: Replace only specific exports
vi.mock('./database', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./database')>()
  return {
    ...actual,
    // Only mock specific functions
    saveUser: vi.fn().mockResolvedValue({ id: '123' }),
    // Keep original implementation for others
    validateUser: actual.validateUser,
    hashPassword: actual.hashPassword
  }
})

// Partial mock of Node.js modules
vi.mock('fs/promises', async () => {
  const actual = await vi.importActual<typeof import('fs/promises')>('fs/promises')
  return {
    ...actual,
    readFile: vi.fn().mockResolvedValue('mocked content'),
    // All other fs methods use real implementation
  }
})
```

---

## 🎨 Conditional Mocking

Different behavior based on input parameters:

```typescript
const mockFetch = vi.fn((url: string) => {
  // Different responses based on URL
  if (url.includes('/users')) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve([{ id: 1, name: 'User' }])
    })
  }

  if (url.includes('/error')) {
    return Promise.reject(new Error('Network error'))
  }

  if (url.includes('/posts')) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve([{ id: 1, title: 'Post' }])
    })
  }

  // Default response
  return Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ default: true })
  })
})

global.fetch = mockFetch

it('handles different endpoints', async () => {
  const users = await fetchUsers()
  expect(users).toHaveLength(1)

  const posts = await fetchPosts()
  expect(posts[0].title).toBe('Post')

  await expect(fetchError()).rejects.toThrow('Network error')
})
```

---

## ⛓️ Mock Chaining

Build complex mock behaviors through chaining:

```typescript
class MockQueryBuilder {
  private conditions: any[] = []
  private orderField?: string
  private limitValue?: number

  where(field: string, value: any) {
    this.conditions.push({ field, value })
    return this
  }

  orderBy(field: string) {
    this.orderField = field
    return this
  }

  limit(n: number) {
    this.limitValue = n
    return this
  }

  async execute() {
    // Return mock data based on conditions
    const results = []

    if (this.conditions.some(c => c.field === 'status' && c.value === 'active')) {
      results.push({ id: 1, status: 'active', name: 'Active User' })
    }

    if (this.conditions.some(c => c.field === 'role' && c.value === 'admin')) {
      results.push({ id: 2, status: 'active', name: 'Admin', role: 'admin' })
    }

    // Apply limit if set
    return this.limitValue ? results.slice(0, this.limitValue) : results
  }
}

// Mock database with chainable API
vi.mock('./database', () => ({
  query: () => new MockQueryBuilder()
}))

it('builds complex queries', async () => {
  const results = await db.query()
    .where('status', 'active')
    .where('role', 'admin')
    .orderBy('createdAt')
    .limit(10)
    .execute()

  expect(results).toHaveLength(1)
  expect(results[0].role).toBe('admin')
})
```

---

## 💾 Stateful Mocks

Mocks that maintain state across calls:

```typescript
const createStatefulMock = () => {
  let callCount = 0
  const data: any[] = []

  return {
    add: vi.fn((item) => {
      callCount++
      data.push(item)
      return item
    }),

    getAll: vi.fn(() => [...data]),

    remove: vi.fn((id) => {
      callCount++
      const index = data.findIndex(item => item.id === id)
      if (index >= 0) {
        data.splice(index, 1)
        return true
      }
      return false
    }),

    getCallCount: () => callCount,

    reset: () => {
      callCount = 0
      data.length = 0
    },

    _inspect: () => ({ callCount, data: [...data] })
  }
}

describe('Stateful mock', () => {
  let mockStore: ReturnType<typeof createStatefulMock>

  beforeEach(() => {
    mockStore = createStatefulMock()
  })

  it('maintains state across operations', () => {
    mockStore.add({ id: 1, name: 'Item 1' })
    mockStore.add({ id: 2, name: 'Item 2' })

    expect(mockStore.getAll()).toHaveLength(2)

    mockStore.remove(1)

    expect(mockStore.getAll()).toHaveLength(1)
    expect(mockStore.getCallCount()).toBe(3) // 2 adds + 1 remove
  })
})
```

---

## ✅ Mock Validation

Validate mock usage patterns:

```typescript
const createValidatedMock = (name: string, validations: {
  minArgs?: number
  argTypes?: string[]
  returnValue: any
}) => {
  return vi.fn((...args) => {
    // Validate argument count
    if (validations.minArgs && args.length < validations.minArgs) {
      throw new Error(
        `${name} requires at least ${validations.minArgs} arguments, got ${args.length}`
      )
    }

    // Validate argument types
    if (validations.argTypes) {
      args.forEach((arg, i) => {
        const expectedType = validations.argTypes![i]
        if (expectedType && typeof arg !== expectedType) {
          throw new Error(
            `${name} argument ${i} must be ${expectedType}, got ${typeof arg}`
          )
        }
      })
    }

    return validations.returnValue
  })
}

// Usage
const mockApi = createValidatedMock('api.call', {
  minArgs: 2,
  argTypes: ['string', 'object'],
  returnValue: { success: true }
})

it('validates mock arguments', () => {
  // This works
  expect(mockApi('endpoint', { data: 'test' })).toEqual({ success: true })

  // This throws
  expect(() => mockApi('endpoint')).toThrow('requires at least 2 arguments')
  expect(() => mockApi(123, {})).toThrow('argument 0 must be string')
})
```

---

## 🌍 Environment-Specific Mocking

Mock differently based on test environment:

```typescript
const createEnvironmentMock = () => {
  const env = process.env.TEST_ENV || 'unit'

  if (env === 'integration') {
    // More realistic mocks for integration tests
    return {
      database: createRealDatabaseMock(),
      api: createRealApiMock(),
      cache: createRedisLikeMock()
    }
  }

  // Simple mocks for unit tests
  return {
    database: { query: vi.fn() },
    api: { call: vi.fn() },
    cache: { get: vi.fn(), set: vi.fn() }
  }
}

describe('Service tests', () => {
  const mocks = createEnvironmentMock()

  it('uses appropriate mocks for environment', () => {
    const service = new Service(mocks.database, mocks.api)

    // Test behavior adapts to mock complexity
    service.process()

    expect(mocks.database.query).toHaveBeenCalled()
  })
})
```

---

## 🔄 Mock Reset Strategies

Different strategies for resetting mocks between tests:

```typescript
import { vi, beforeEach, afterEach, describe, it } from 'vitest'

describe('Mock reset strategies', () => {
  // Strategy 1: Reset all mocks globally
  afterEach(() => {
    vi.clearAllMocks()   // Clear call history
    vi.resetAllMocks()   // Reset implementation
    vi.restoreAllMocks() // Restore original implementation
  })

  // Strategy 2: Selective reset
  const mocks = {
    api: vi.fn(),
    database: vi.fn(),
    cache: vi.fn()
  }

  afterEach(() => {
    // Only reset specific mocks
    mocks.api.mockClear()
    mocks.database.mockReset()
    // Keep cache mock state between tests
  })

  // Strategy 3: Scoped mocking
  describe('Feature tests', () => {
    const localMock = vi.fn()

    afterEach(() => {
      localMock.mockClear()
    })

    it('test 1', () => {
      localMock('call 1')
      expect(localMock).toHaveBeenCalledWith('call 1')
    })

    it('test 2', () => {
      // localMock is cleared, starts fresh
      expect(localMock).not.toHaveBeenCalled()
    })
  })
})

// Understanding the differences:
// - mockClear()   -> Clears call history (mock.calls, mock.results)
// - mockReset()   -> Clears history + removes implementation
// - mockRestore() -> Restores original implementation (for spies)
```

---

## 🔍 Testing Mock Interactions

Verify complex mock interactions:

```typescript
describe('Service coordination', () => {
  it('calls services in correct order', async () => {
    const mockAuth = vi.fn().mockResolvedValue({ userId: '123' })
    const mockFetch = vi.fn().mockResolvedValue({ data: [] })
    const mockLog = vi.fn()

    await coordinateServices(mockAuth, mockFetch, mockLog)

    // Verify call order
    const callOrder = [
      mockAuth.mock.invocationCallOrder[0],
      mockFetch.mock.invocationCallOrder[0],
      mockLog.mock.invocationCallOrder[0]
    ]

    expect(callOrder[0]).toBeLessThan(callOrder[1])
    expect(callOrder[1]).toBeLessThan(callOrder[2])
  })

  it('passes results between mocks', async () => {
    const mockAuth = vi.fn().mockResolvedValue({ userId: '123', token: 'abc' })
    const mockFetch = vi.fn().mockResolvedValue({ data: [] })

    await fetchWithAuth(mockAuth, mockFetch)

    // Verify mockFetch was called with mockAuth result
    expect(mockFetch).toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer abc'
        })
      })
    )
  })

  it('handles conditional mock calling', async () => {
    const mockCheck = vi.fn().mockReturnValue(true)
    const mockAction = vi.fn()

    await conditionalAction(mockCheck, mockAction)

    // Verify mockAction only called if mockCheck returned true
    if (mockCheck.mock.results[0].value) {
      expect(mockAction).toHaveBeenCalled()
    } else {
      expect(mockAction).not.toHaveBeenCalled()
    }
  })
})
```

---

## ⏰ Timer Mocking

Control time in tests:

```typescript
import { vi, beforeEach, afterEach } from 'vitest'

describe('Timer mocking', () => {
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

    vi.advanceTimersByTime(1000)

    expect(callback).toHaveBeenCalledTimes(1)
  })

  it('controls Date.now()', () => {
    const fixedTime = new Date('2024-01-15T10:00:00Z')
    vi.setSystemTime(fixedTime)

    expect(Date.now()).toBe(fixedTime.getTime())
    expect(new Date().toISOString()).toBe('2024-01-15T10:00:00.000Z')
  })

  it('runs all timers', () => {
    const callback1 = vi.fn()
    const callback2 = vi.fn()

    setTimeout(callback1, 1000)
    setTimeout(callback2, 2000)

    vi.runAllTimers()

    expect(callback1).toHaveBeenCalled()
    expect(callback2).toHaveBeenCalled()
  })

  it('handles async timers', async () => {
    const callback = vi.fn()

    setTimeout(callback, 1000)

    await vi.advanceTimersByTimeAsync(1000)

    expect(callback).toHaveBeenCalled()
  })
})
```

---

## 📋 Best Practices

### ✅ Do

- **Use factories** for consistent mock creation
- **Reset mocks** between tests to avoid interference
- **Mock at boundaries** (APIs, databases, not internal functions)
- **Verify interactions** that matter (important side effects)
- **Use descriptive names** for mock functions
- **Keep mocks simple** - complex mocks suggest design issues

### ❌ Don't

- **Mock everything** - test real code when possible
- **Mock what you don't own** - wrap third-party code instead
- **Over-specify** mock interactions - makes tests brittle
- **Share mocks** across unrelated tests
- **Mock trivial code** - pure functions don't need mocks
- **Test mock implementations** - test real behavior

---

## 🔗 Related Patterns

- **[F.I.R.S.T Principles](../principles/first-principles.md#isolated)** - Isolation through test doubles
- **[Component Testing](component-testing.md)** - Mocking child components
- **[Test Data](test-data.md)** - Mock factories and test data
- **[Async Testing](async-testing.md)** - Mocking promises and async functions

---

**Next Steps:**
- Review [Vitest Mocking API](https://vitest.dev/api/vi.html)
- Explore [Test Doubles Patterns](https://martinfowler.com/bliki/TestDouble.html)
- Practice with [Complete Examples](../examples/)
