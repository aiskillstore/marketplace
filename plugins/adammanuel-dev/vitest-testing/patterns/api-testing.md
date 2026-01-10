# API Testing Patterns

**Comprehensive patterns for testing HTTP APIs, REST endpoints, and API clients.**

API testing focuses on verifying contracts, error handling, and integration with external services. These patterns ensure your API layer is reliable and maintainable.

---

## 🎯 What to Test in APIs

### HTTP Contract
- ✅ Request/response structure
- ✅ HTTP status codes
- ✅ Headers and content types
- ✅ Query parameters and path variables
- ✅ Request/response body validation

### Error Handling
- ✅ 4xx client errors (400, 401, 404, etc.)
- ✅ 5xx server errors (500, 503, etc.)
- ✅ Network failures
- ✅ Timeout handling
- ✅ Retry logic

### Edge Cases
- ✅ Empty responses
- ✅ Large payloads
- ✅ Rate limiting
- ✅ Authentication/authorization
- ✅ Concurrent requests

---

## 🌐 Testing API Clients

### Basic GET Request

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('UserAPIClient', () => {
  let mockFetch: ReturnType<typeof vi.fn>

  beforeEach(() => {
    mockFetch = vi.fn()
    global.fetch = mockFetch
  })

  it('fetches user by ID', async () => {
    const mockUser = { id: '123', name: 'John Doe', email: 'john@example.com' }

    mockFetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockUser
    } as Response)

    const apiClient = new UserAPIClient()
    const user = await apiClient.getUser('123')

    expect(mockFetch).toHaveBeenCalledWith('/api/users/123', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    expect(user).toEqual(mockUser)
  })

  it('handles 404 not found', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found'
    } as Response)

    const apiClient = new UserAPIClient()

    await expect(apiClient.getUser('999'))
      .rejects.toThrow('User not found')
  })

  it('handles network errors', async () => {
    mockFetch.mockRejectedValue(new Error('Network error'))

    const apiClient = new UserAPIClient()

    await expect(apiClient.getUser('123'))
      .rejects.toThrow('Network error')
  })
})
```

### POST Request with Body

```typescript
describe('UserAPIClient.createUser', () => {
  it('creates user with POST request', async () => {
    const userData = {
      name: 'Jane Doe',
      email: 'jane@example.com'
    }

    const mockResponse = {
      id: '456',
      ...userData,
      createdAt: '2024-01-15T10:00:00Z'
    }

    mockFetch.mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => mockResponse
    } as Response)

    const apiClient = new UserAPIClient()
    const user = await apiClient.createUser(userData)

    expect(mockFetch).toHaveBeenCalledWith('/api/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    })
    expect(user).toEqual(mockResponse)
  })

  it('handles validation errors (400)', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({
        errors: ['Invalid email format']
      })
    } as Response)

    const apiClient = new UserAPIClient()

    await expect(apiClient.createUser({ email: 'invalid' }))
      .rejects.toThrow('Invalid email format')
  })
})
```

---

## 🔐 Testing Authentication

### Bearer Token Authentication

```typescript
describe('Authenticated API calls', () => {
  it('includes auth token in headers', async () => {
    const token = 'Bearer abc123xyz'

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ data: 'protected' })
    } as Response)

    const apiClient = new APIClient({ token })
    await apiClient.getProtectedResource()

    expect(mockFetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': token
        })
      })
    )
  })

  it('handles 401 unauthorized', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 401,
      statusText: 'Unauthorized'
    } as Response)

    const apiClient = new APIClient({ token: 'invalid' })

    await expect(apiClient.getProtectedResource())
      .rejects.toThrow('Unauthorized')
  })

  it('refreshes token on 401 and retries', async () => {
    const mockRefreshToken = vi.fn().mockResolvedValue('new-token')

    mockFetch
      .mockResolvedValueOnce({
        ok: false,
        status: 401
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'success' })
      } as Response)

    const apiClient = new APIClient({
      token: 'old-token',
      refreshToken: mockRefreshToken
    })

    const result = await apiClient.getProtectedResource()

    expect(mockRefreshToken).toHaveBeenCalled()
    expect(mockFetch).toHaveBeenCalledTimes(2)
    expect(result.data).toBe('success')
  })
})
```

---

## 🔄 Testing Retry Logic

```typescript
describe('API retry logic', () => {
  it('retries on 5xx errors', async () => {
    mockFetch
      .mockResolvedValueOnce({ ok: false, status: 503 } as Response)
      .mockResolvedValueOnce({ ok: false, status: 503 } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'success' })
      } as Response)

    const apiClient = new APIClient({ maxRetries: 3 })
    const result = await apiClient.getData()

    expect(mockFetch).toHaveBeenCalledTimes(3)
    expect(result.data).toBe('success')
  })

  it('fails after max retries', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 503,
      statusText: 'Service Unavailable'
    } as Response)

    const apiClient = new APIClient({ maxRetries: 3 })

    await expect(apiClient.getData())
      .rejects.toThrow('Service Unavailable')

    expect(mockFetch).toHaveBeenCalledTimes(3)
  })

  it('uses exponential backoff', async () => {
    vi.useFakeTimers()

    const delays: number[] = []
    mockFetch.mockImplementation(async () => {
      delays.push(Date.now())
      return { ok: false, status: 503 } as Response
    })

    const apiClient = new APIClient({ maxRetries: 3 })
    const promise = apiClient.getData().catch(() => {})

    // Advance through retries
    await vi.advanceTimersByTimeAsync(1000)  // 1st retry
    await vi.advanceTimersByTimeAsync(2000)  // 2nd retry (2x)
    await vi.advanceTimersByTimeAsync(4000)  // 3rd retry (4x)

    await promise

    // Verify exponential backoff
    expect(delays).toHaveLength(3)

    vi.useRealTimers()
  })
})
```

---

## 📊 Testing Query Parameters

```typescript
describe('Query parameters', () => {
  it('builds query string correctly', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ([])
    } as Response)

    const apiClient = new APIClient()
    await apiClient.searchUsers({
      name: 'John',
      age: 25,
      active: true
    })

    expect(mockFetch).toHaveBeenCalledWith(
      '/api/users?name=John&age=25&active=true',
      expect.any(Object)
    )
  })

  it('handles array query parameters', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ([])
    } as Response)

    const apiClient = new APIClient()
    await apiClient.searchUsers({
      roles: ['admin', 'moderator']
    })

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('roles=admin&roles=moderator'),
      expect.any(Object)
    )
  })
})
```

---

## 🎭 Using MSW for Realistic API Mocking

```typescript
import { rest } from 'msw'
import { setupServer } from 'msw/node'

const server = setupServer(
  rest.get('/api/users/:id', (req, res, ctx) => {
    const { id } = req.params

    if (id === 'invalid') {
      return res(ctx.status(404), ctx.json({ error: 'User not found' }))
    }

    return res(ctx.json({ id, name: 'John Doe' }))
  }),

  rest.post('/api/users', async (req, res, ctx) => {
    const body = await req.json()

    if (!body.email) {
      return res(ctx.status(400), ctx.json({ error: 'Email required' }))
    }

    return res(
      ctx.status(201),
      ctx.json({ id: '123', ...body })
    )
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('API with MSW', () => {
  it('fetches user successfully', async () => {
    const user = await apiClient.getUser('1')

    expect(user).toEqual({ id: '1', name: 'John Doe' })
  })

  it('handles 404 errors', async () => {
    await expect(apiClient.getUser('invalid'))
      .rejects.toThrow('User not found')
  })

  it('creates user', async () => {
    const newUser = { email: 'new@example.com', name: 'New User' }
    const created = await apiClient.createUser(newUser)

    expect(created.id).toBe('123')
    expect(created.email).toBe('new@example.com')
  })
})
```

---

## 📋 Best Practices

### ✅ Do

- **Mock HTTP layer** - Don't make real API calls
- **Test error scenarios** - 4xx, 5xx, network errors
- **Verify request structure** - method, headers, body
- **Test retry logic** - transient failures
- **Use MSW** for realistic mocking
- **Test authentication** flows

### ❌ Don't

- **Make real API calls** in unit tests
- **Test external APIs** - test your client code
- **Ignore error handling** - critical for APIs
- **Skip timeout tests** - APIs can be slow
- **Forget rate limiting** tests
- **Test only happy paths**

---

## 🔗 Related Patterns

- **[Async Testing](async-testing.md)** - Promises and async/await
- **[Error Testing](error-testing.md)** - HTTP error scenarios
- **[Test Doubles](test-doubles.md)** - Mocking fetch

---

**Next Steps:**
- Install [MSW](https://mswjs.io/) for realistic API mocking
- Review [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- Explore [Testing Library](https://testing-library.com/) for component integration
