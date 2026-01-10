# Async Validation - Asynchronous Validation Patterns

This document covers all asynchronous validation patterns in Zod for database checks, API calls, and other async operations.

## Table of Contents

- [Async Refinement](#async-refinement)
- [Async Schema](#async-schema)
- [Email Existence Validation](#email-existence-validation)
- [URL Reachability Check](#url-reachability-check)
- [Async Dependent Validation](#async-dependent-validation)
- [Error Handling](#error-handling)
- [Timeout Handling](#timeout-handling)
- [Concurrent Async Validations](#concurrent-async-validations)
- [Caching Async Results](#caching-async-results)

---

## Async Refinement

### Basic Async Refinement

```typescript
import { z } from 'zod'

// Async database check
const emailSchema = z.string()
  .email()
  .refine(
    async (email) => {
      const user = await db.user.findUnique({ where: { email } })
      return !user // Return false if user exists
    },
    { message: 'Email is already registered' }
  )

// Usage
const result = await emailSchema.parseAsync('user@example.com')
// Or with safeParse
const safeResult = await emailSchema.safeParseAsync('user@example.com')
```

### Async with Custom Error

```typescript
const usernameSchema = z.string()
  .min(3)
  .max(20)
  .refine(
    async (username) => {
      const existing = await db.user.findUnique({ where: { username } })
      return !existing
    },
    async (username) => ({
      message: `Username "${username}" is already taken`
    })
  )
```

### Multiple Async Refinements

```typescript
const userSchema = z.object({
  email: z.string().email(),
  username: z.string()
})
  .refine(
    async (data) => {
      const emailExists = await db.user.findUnique({ where: { email: data.email } })
      return !emailExists
    },
    { message: 'Email already registered', path: ['email'] }
  )
  .refine(
    async (data) => {
      const usernameExists = await db.user.findUnique({ where: { username: data.username } })
      return !usernameExists
    },
    { message: 'Username already taken', path: ['username'] }
  )

// Usage - must use parseAsync
const result = await userSchema.parseAsync({
  email: 'user@example.com',
  username: 'johndoe'
})
```

---

## Async Schema

### Promise Schema

```typescript
// Validate a promise that resolves to a value
const promiseSchema = z.promise(z.string())

// Example
const myPromise = Promise.resolve('hello')
const result = await promiseSchema.parse(myPromise) // 'hello'
```

### Async Function Return Type

```typescript
async function fetchUser(id: string): Promise<{ name: string; email: string }> {
  // Fetch from database
  return await db.user.findUnique({ where: { id } })
}

const userSchema = z.object({
  name: z.string(),
  email: z.string().email()
})

const userPromiseSchema = z.promise(userSchema)

// Validate async function result
const user = await fetchUser('123')
const validated = userSchema.parse(user)
```

---

## Email Existence Validation

### Check Email Domain

```typescript
import dns from 'dns/promises'

const emailWithDomainCheckSchema = z.string()
  .email()
  .refine(
    async (email) => {
      const domain = email.split('@')[1]
      try {
        const records = await dns.resolveMx(domain)
        return records.length > 0
      } catch {
        return false
      }
    },
    { message: 'Email domain does not exist' }
  )
```

### Check Email via API

```typescript
async function verifyEmail(email: string): Promise<boolean> {
  try {
    const response = await fetch(`https://api.emailverification.com/verify?email=${email}`)
    const data = await response.json()
    return data.valid
  } catch {
    return false
  }
}

const verifiedEmailSchema = z.string()
  .email()
  .refine(
    verifyEmail,
    { message: 'Email address could not be verified' }
  )
```

### Check Disposable Email

```typescript
const DISPOSABLE_DOMAINS = new Set([
  'tempmail.com',
  '10minutemail.com',
  // ... more
])

async function isDisposableEmail(email: string): Promise<boolean> {
  const domain = email.split('@')[1]

  // Check local blacklist
  if (DISPOSABLE_DOMAINS.has(domain)) {
    return true
  }

  // Check external API
  try {
    const response = await fetch(`https://api.disposable-email.com/check/${domain}`)
    const data = await response.json()
    return data.disposable
  } catch {
    return false
  }
}

const nonDisposableEmailSchema = z.string()
  .email()
  .refine(
    async (email) => !(await isDisposableEmail(email)),
    { message: 'Disposable email addresses are not allowed' }
  )
```

---

## URL Reachability Check

### Check URL Exists

```typescript
async function isUrlReachable(url: string): Promise<boolean> {
  try {
    const response = await fetch(url, { method: 'HEAD', signal: AbortSignal.timeout(5000) })
    return response.ok
  } catch {
    return false
  }
}

const reachableUrlSchema = z.string()
  .url()
  .refine(
    isUrlReachable,
    { message: 'URL is not reachable' }
  )
```

### Check Image URL

```typescript
async function isValidImageUrl(url: string): Promise<boolean> {
  try {
    const response = await fetch(url, { method: 'HEAD', signal: AbortSignal.timeout(5000) })
    const contentType = response.headers.get('content-type')
    return contentType?.startsWith('image/') ?? false
  } catch {
    return false
  }
}

const imageUrlSchema = z.string()
  .url()
  .refine(
    isValidImageUrl,
    { message: 'URL must point to a valid image' }
  )
```

### Check API Endpoint

```typescript
async function isValidApiEndpoint(url: string): Promise<boolean> {
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(5000) })
    return response.status < 500 // Accept any non-server error
  } catch {
    return false
  }
}

const apiEndpointSchema = z.string()
  .url()
  .refine(
    isValidApiEndpoint,
    { message: 'API endpoint is not available' }
  )
```

---

## Async Dependent Validation

### Cross-Table Validation

```typescript
const orderSchema = z.object({
  userId: z.string(),
  productId: z.string(),
  quantity: z.number().positive()
})
  .refine(
    async (data) => {
      // Check if user exists
      const user = await db.user.findUnique({ where: { id: data.userId } })
      return !!user
    },
    { message: 'User not found', path: ['userId'] }
  )
  .refine(
    async (data) => {
      // Check if product exists
      const product = await db.product.findUnique({ where: { id: data.productId } })
      return !!product
    },
    { message: 'Product not found', path: ['productId'] }
  )
  .refine(
    async (data) => {
      // Check if enough stock
      const product = await db.product.findUnique({ where: { id: data.productId } })
      return product && product.stock >= data.quantity
    },
    { message: 'Insufficient stock', path: ['quantity'] }
  )
```

### Permission Validation

```typescript
const actionSchema = z.object({
  userId: z.string(),
  resourceId: z.string(),
  action: z.enum(['read', 'write', 'delete'])
})
  .refine(
    async (data) => {
      const user = await db.user.findUnique({
        where: { id: data.userId },
        include: { permissions: true }
      })

      if (!user) return false

      const resource = await db.resource.findUnique({
        where: { id: data.resourceId }
      })

      if (!resource) return false

      // Check permission
      return user.permissions.some(p =>
        p.resourceId === data.resourceId &&
        p.action === data.action
      )
    },
    { message: 'Permission denied' }
  )
```

### Rate Limit Validation

```typescript
async function checkRateLimit(userId: string): Promise<boolean> {
  const key = `rate_limit:${userId}`
  const count = await redis.get(key)

  if (!count) {
    await redis.setex(key, 60, '1') // 1 request in 60 seconds
    return true
  }

  const requests = parseInt(count)
  if (requests >= 10) {
    return false
  }

  await redis.incr(key)
  return true
}

const rateLimitedSchema = z.object({
  userId: z.string(),
  // ... other fields
})
  .refine(
    async (data) => await checkRateLimit(data.userId),
    { message: 'Rate limit exceeded. Please try again later.' }
  )
```

---

## Error Handling

### Try-Catch in Refinement

```typescript
const safeAsyncSchema = z.string()
  .refine(
    async (value) => {
      try {
        const result = await externalApiCall(value)
        return result.valid
      } catch (error) {
        console.error('Validation error:', error)
        return false // Treat errors as validation failure
      }
    },
    { message: 'Validation failed' }
  )
```

### Fallback on Error

```typescript
const resilientSchema = z.string()
  .refine(
    async (value) => {
      try {
        return await primaryValidation(value)
      } catch {
        try {
          return await fallbackValidation(value)
        } catch {
          return false
        }
      }
    },
    { message: 'All validation methods failed' }
  )
```

### Detailed Error Messages

```typescript
const detailedErrorSchema = z.string()
  .refine(
    async (value) => {
      try {
        const result = await validateWithApi(value)
        return result.valid
      } catch (error) {
        throw new Error(`Validation service error: ${error.message}`)
      }
    },
    { message: 'External validation failed' }
  )
```

---

## Timeout Handling

### With AbortController

```typescript
async function validateWithTimeout(value: string, timeoutMs: number): Promise<boolean> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch(`https://api.example.com/validate?value=${value}`, {
      signal: controller.signal
    })
    clearTimeout(timeout)
    return response.ok
  } catch (error) {
    clearTimeout(timeout)
    if (error.name === 'AbortError') {
      console.log('Validation timeout')
      return false
    }
    throw error
  }
}

const timeoutSchema = z.string()
  .refine(
    async (value) => await validateWithTimeout(value, 5000),
    { message: 'Validation timeout or failed' }
  )
```

### With Promise.race

```typescript
async function timeoutPromise<T>(promise: Promise<T>, ms: number): Promise<T> {
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error('Timeout')), ms)
  )
  return Promise.race([promise, timeout])
}

const racingSchema = z.string()
  .refine(
    async (value) => {
      try {
        await timeoutPromise(externalValidation(value), 3000)
        return true
      } catch {
        return false
      }
    },
    { message: 'Validation timeout' }
  )
```

---

## Concurrent Async Validations

### Parallel Validations

```typescript
const parallelSchema = z.object({
  email: z.string().email(),
  username: z.string(),
  slug: z.string()
})
  .refine(
    async (data) => {
      // Run all checks in parallel
      const [emailExists, usernameExists, slugExists] = await Promise.all([
        db.user.findUnique({ where: { email: data.email } }),
        db.user.findUnique({ where: { username: data.username } }),
        db.post.findUnique({ where: { slug: data.slug } })
      ])

      return !emailExists && !usernameExists && !slugExists
    },
    { message: 'One or more fields already exist' }
  )
```

### Parallel with Individual Errors

```typescript
const parallelErrorsSchema = z.object({
  email: z.string().email(),
  username: z.string()
})
  .refine(
    async (data) => {
      const emailExists = await db.user.findUnique({ where: { email: data.email } })
      return !emailExists
    },
    { message: 'Email already registered', path: ['email'] }
  )
  .refine(
    async (data) => {
      const usernameExists = await db.user.findUnique({ where: { username: data.username } })
      return !usernameExists
    },
    { message: 'Username already taken', path: ['username'] }
  )

// Both refinements run in parallel automatically
```

### Optimized Parallel Validation

```typescript
async function validateUserData(data: { email: string; username: string; phone: string }) {
  const [emailExists, usernameExists, phoneExists] = await Promise.all([
    db.user.findUnique({ where: { email: data.email } }),
    db.user.findUnique({ where: { username: data.username } }),
    db.user.findUnique({ where: { phone: data.phone } })
  ])

  const errors: Array<{ path: string[]; message: string }> = []

  if (emailExists) errors.push({ path: ['email'], message: 'Email already registered' })
  if (usernameExists) errors.push({ path: ['username'], message: 'Username taken' })
  if (phoneExists) errors.push({ path: ['phone'], message: 'Phone number registered' })

  return { valid: errors.length === 0, errors }
}

const optimizedSchema = z.object({
  email: z.string().email(),
  username: z.string(),
  phone: z.string()
})
  .refine(
    async (data) => {
      const result = await validateUserData(data)
      return result.valid
    },
    { message: 'Validation failed' }
  )
```

---

## Caching Async Results

### Simple Cache

```typescript
const cache = new Map<string, boolean>()

const cachedSchema = z.string()
  .refine(
    async (value) => {
      // Check cache first
      if (cache.has(value)) {
        return cache.get(value)!
      }

      // Perform validation
      const result = await expensiveValidation(value)

      // Cache result
      cache.set(value, result)

      return result
    },
    { message: 'Validation failed' }
  )
```

### TTL Cache

```typescript
interface CacheEntry {
  value: boolean
  expires: number
}

const ttlCache = new Map<string, CacheEntry>()

async function cachedValidation(value: string, ttlMs: number): Promise<boolean> {
  const now = Date.now()
  const cached = ttlCache.get(value)

  if (cached && cached.expires > now) {
    return cached.value
  }

  const result = await expensiveValidation(value)

  ttlCache.set(value, {
    value: result,
    expires: now + ttlMs
  })

  return result
}

const ttlCachedSchema = z.string()
  .refine(
    async (value) => await cachedValidation(value, 60000), // 1 minute TTL
    { message: 'Validation failed' }
  )
```

### LRU Cache

```typescript
class LRUCache<K, V> {
  private cache = new Map<K, V>()

  constructor(private maxSize: number) {}

  get(key: K): V | undefined {
    const value = this.cache.get(key)
    if (value !== undefined) {
      // Move to end (most recently used)
      this.cache.delete(key)
      this.cache.set(key, value)
    }
    return value
  }

  set(key: K, value: V): void {
    this.cache.delete(key)
    this.cache.set(key, value)

    if (this.cache.size > this.maxSize) {
      // Remove oldest (first) entry
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }
  }
}

const lruCache = new LRUCache<string, boolean>(100)

const lruCachedSchema = z.string()
  .refine(
    async (value) => {
      const cached = lruCache.get(value)
      if (cached !== undefined) {
        return cached
      }

      const result = await expensiveValidation(value)
      lruCache.set(value, result)
      return result
    },
    { message: 'Validation failed' }
  )
```

### Redis Cache

```typescript
import { Redis } from 'ioredis'

const redis = new Redis()

async function redisCachedValidation(value: string): Promise<boolean> {
  const cacheKey = `validation:${value}`

  // Check cache
  const cached = await redis.get(cacheKey)
  if (cached !== null) {
    return cached === 'true'
  }

  // Perform validation
  const result = await expensiveValidation(value)

  // Cache for 1 hour
  await redis.setex(cacheKey, 3600, result.toString())

  return result
}

const redisCachedSchema = z.string()
  .refine(
    redisCachedValidation,
    { message: 'Validation failed' }
  )
```

---

## Advanced Async Patterns

### Debounced Validation

```typescript
function debounce<T extends (...args: any[]) => any>(
  func: T,
  waitMs: number
): (...args: Parameters<T>) => Promise<ReturnType<T>> {
  let timeout: NodeJS.Timeout | null = null

  return (...args: Parameters<T>): Promise<ReturnType<T>> => {
    return new Promise((resolve) => {
      if (timeout) clearTimeout(timeout)
      timeout = setTimeout(() => resolve(func(...args)), waitMs)
    })
  }
}

const debouncedCheck = debounce(expensiveValidation, 500)

const debouncedSchema = z.string()
  .refine(
    async (value) => await debouncedCheck(value),
    { message: 'Validation failed' }
  )
```

### Batched Validation

```typescript
let batchQueue: string[] = []
let batchTimeout: NodeJS.Timeout | null = null

async function batchValidation(values: string[]): Promise<Map<string, boolean>> {
  // Validate all values in single API call
  const response = await fetch('https://api.example.com/validate/batch', {
    method: 'POST',
    body: JSON.stringify({ values })
  })
  const results = await response.json()
  return new Map(results)
}

async function queuedValidation(value: string): Promise<boolean> {
  return new Promise((resolve) => {
    batchQueue.push(value)

    if (batchTimeout) clearTimeout(batchTimeout)

    batchTimeout = setTimeout(async () => {
      const queue = [...batchQueue]
      batchQueue = []

      const results = await batchValidation(queue)
      resolve(results.get(value) ?? false)
    }, 100) // Batch every 100ms
  })
}
```

### Retry on Failure

```typescript
async function retryValidation(
  value: string,
  maxRetries: number = 3
): Promise<boolean> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await externalValidation(value)
    } catch (error) {
      if (i === maxRetries - 1) throw error
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1))) // Exponential backoff
    }
  }
  return false
}

const retrySchema = z.string()
  .refine(
    async (value) => await retryValidation(value),
    { message: 'Validation failed after retries' }
  )
```

---

## Summary

This document covered:
- ✅ Async refinements for database checks
- ✅ Promise schema validation
- ✅ Email existence and domain validation
- ✅ URL reachability checks
- ✅ Cross-table and permission validation
- ✅ Error and timeout handling
- ✅ Concurrent validations for performance
- ✅ Caching strategies (TTL, LRU, Redis)
- ✅ Advanced patterns (debounce, batch, retry)

**Next Steps:**
- **[Type Inference](./type-inference.md)** - TypeScript types
- **[API Integration](./api-integration.md)** - Use in Next.js
- **[Common Schemas](./common-schemas.md)** - Ready-to-use patterns

---

*Last updated: 2025-11-23 | Zod v4.1.12*
