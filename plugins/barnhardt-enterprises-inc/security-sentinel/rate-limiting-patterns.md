# Rate Limiting Patterns

Comprehensive rate limiting implementation for Next.js 15 API routes and Server Actions.

---

## Table of Contents

1. [Why Rate Limiting](#why-rate-limiting)
2. [In-Memory Rate Limiting](#in-memory-rate-limiting)
3. [Redis-Based Rate Limiting](#redis-based-rate-limiting)
4. [API Route Protection](#api-route-protection)
5. [Server Action Protection](#server-action-protection)
6. [IP-Based Rate Limiting](#ip-based-rate-limiting)
7. [User-Based Rate Limiting](#user-based-rate-limiting)
8. [Sliding Window Algorithm](#sliding-window-algorithm)
9. [Token Bucket Algorithm](#token-bucket-algorithm)

---

## Why Rate Limiting

**Protects against:**
- Brute force attacks (login, password reset)
- Denial of Service (DoS) attacks
- API abuse and resource exhaustion
- Scraping and data harvesting
- Spam and automated submissions

**Common limits:**
- Login: 5 attempts per 15 minutes
- Password reset: 3 attempts per hour
- API: 100 requests per minute
- Registration: 3 accounts per hour per IP
- File upload: 10 files per hour

---

## In-Memory Rate Limiting

### Simple Rate Limiter

```typescript
// src/lib/rate-limit/memory.ts
interface RateLimitEntry {
  count: number
  resetAt: number
}

class InMemoryRateLimiter {
  private store = new Map<string, RateLimitEntry>()

  constructor(
    private maxRequests: number,
    private windowMs: number
  ) {}

  async check(key: string): Promise<{
    success: boolean
    remaining: number
    resetAt: number
  }> {
    const now = Date.now()
    const entry = this.store.get(key)

    // Clean up expired entries
    this.cleanup(now)

    if (!entry || entry.resetAt <= now) {
      // First request or window expired
      this.store.set(key, {
        count: 1,
        resetAt: now + this.windowMs,
      })

      return {
        success: true,
        remaining: this.maxRequests - 1,
        resetAt: now + this.windowMs,
      }
    }

    if (entry.count >= this.maxRequests) {
      // Rate limit exceeded
      return {
        success: false,
        remaining: 0,
        resetAt: entry.resetAt,
      }
    }

    // Increment count
    entry.count++

    return {
      success: true,
      remaining: this.maxRequests - entry.count,
      resetAt: entry.resetAt,
    }
  }

  private cleanup(now: number) {
    for (const [key, entry] of this.store.entries()) {
      if (entry.resetAt <= now) {
        this.store.delete(key)
      }
    }
  }

  reset(key: string) {
    this.store.delete(key)
  }

  resetAll() {
    this.store.clear()
  }
}

// Create rate limiters for different endpoints
export const loginRateLimiter = new InMemoryRateLimiter(
  5,  // 5 attempts
  15 * 60 * 1000  // 15 minutes
)

export const apiRateLimiter = new InMemoryRateLimiter(
  100,  // 100 requests
  60 * 1000  // 1 minute
)

export const passwordResetRateLimiter = new InMemoryRateLimiter(
  3,  // 3 attempts
  60 * 60 * 1000  // 1 hour
)
```

### Usage in API Route

```typescript
// src/app/api/auth/login/route.ts
import { loginRateLimiter } from '@/lib/rate-limit/memory'

export async function POST(request: Request) {
  // Get client IP
  const ip = request.headers.get('x-forwarded-for') ||
             request.headers.get('x-real-ip') ||
             'unknown'

  // Check rate limit
  const { success, remaining, resetAt } = await loginRateLimiter.check(ip)

  if (!success) {
    const retryAfter = Math.ceil((resetAt - Date.now()) / 1000)

    return Response.json(
      {
        error: 'Too many login attempts. Please try again later.',
        retryAfter,
      },
      {
        status: 429,
        headers: {
          'Retry-After': String(retryAfter),
          'X-RateLimit-Limit': '5',
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': String(Math.floor(resetAt / 1000)),
        },
      }
    )
  }

  // Set rate limit headers
  const headers = {
    'X-RateLimit-Limit': '5',
    'X-RateLimit-Remaining': String(remaining),
    'X-RateLimit-Reset': String(Math.floor(resetAt / 1000)),
  }

  // ... rest of login logic

  return Response.json({ success: true }, { headers })
}
```

---

## Redis-Based Rate Limiting

### Redis Rate Limiter

```typescript
// src/lib/rate-limit/redis.ts
import { Redis } from 'ioredis'

const redis = new Redis(process.env.REDIS_URL!)

export class RedisRateLimiter {
  constructor(
    private maxRequests: number,
    private windowMs: number
  ) {}

  async check(key: string): Promise<{
    success: boolean
    remaining: number
    resetAt: number
  }> {
    const now = Date.now()
    const resetAt = now + this.windowMs
    const windowKey = `ratelimit:${key}:${Math.floor(now / this.windowMs)}`

    // Increment counter
    const count = await redis.incr(windowKey)

    // Set expiration on first request
    if (count === 1) {
      await redis.pexpire(windowKey, this.windowMs)
    }

    const remaining = Math.max(0, this.maxRequests - count)

    return {
      success: count <= this.maxRequests,
      remaining,
      resetAt,
    }
  }

  async reset(key: string) {
    const pattern = `ratelimit:${key}:*`
    const keys = await redis.keys(pattern)

    if (keys.length > 0) {
      await redis.del(...keys)
    }
  }
}

// Create rate limiters
export const loginRateLimiter = new RedisRateLimiter(
  5,
  15 * 60 * 1000
)

export const apiRateLimiter = new RedisRateLimiter(
  100,
  60 * 1000
)
```

### Sliding Window Redis

```typescript
// src/lib/rate-limit/redis-sliding.ts
export class RedisSlidingWindowRateLimiter {
  constructor(
    private maxRequests: number,
    private windowMs: number
  ) {}

  async check(key: string): Promise<{
    success: boolean
    remaining: number
    resetAt: number
  }> {
    const now = Date.now()
    const windowKey = `ratelimit:sliding:${key}`
    const windowStart = now - this.windowMs

    // Use Redis sorted set with timestamps as scores
    const pipeline = redis.pipeline()

    // Remove old entries
    pipeline.zremrangebyscore(windowKey, 0, windowStart)

    // Count current entries
    pipeline.zcard(windowKey)

    // Add current request
    pipeline.zadd(windowKey, now, `${now}:${Math.random()}`)

    // Set expiration
    pipeline.pexpire(windowKey, this.windowMs)

    const results = await pipeline.exec()

    const count = (results![1][1] as number) + 1  // Count after removal + current request
    const remaining = Math.max(0, this.maxRequests - count)

    return {
      success: count <= this.maxRequests,
      remaining,
      resetAt: now + this.windowMs,
    }
  }
}
```

---

## API Route Protection

### Rate Limit Middleware

```typescript
// src/lib/rate-limit/middleware.ts
import { NextRequest, NextResponse } from 'next/server'
import { RedisRateLimiter } from './redis'

export function withRateLimit(
  rateLimiter: RedisRateLimiter,
  getKey: (request: NextRequest) => string = (req) =>
    req.headers.get('x-forwarded-for') || 'unknown'
) {
  return async (
    request: NextRequest,
    handler: (request: NextRequest) => Promise<NextResponse>
  ) => {
    const key = getKey(request)
    const { success, remaining, resetAt } = await rateLimiter.check(key)

    if (!success) {
      const retryAfter = Math.ceil((resetAt - Date.now()) / 1000)

      return NextResponse.json(
        {
          error: 'Rate limit exceeded',
          retryAfter,
        },
        {
          status: 429,
          headers: {
            'Retry-After': String(retryAfter),
            'X-RateLimit-Limit': String(rateLimiter['maxRequests']),
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': String(Math.floor(resetAt / 1000)),
          },
        }
      )
    }

    const response = await handler(request)

    // Add rate limit headers to response
    response.headers.set('X-RateLimit-Limit', String(rateLimiter['maxRequests']))
    response.headers.set('X-RateLimit-Remaining', String(remaining))
    response.headers.set('X-RateLimit-Reset', String(Math.floor(resetAt / 1000)))

    return response
  }
}
```

### Usage with Middleware

```typescript
// src/app/api/data/route.ts
import { withRateLimit } from '@/lib/rate-limit/middleware'
import { apiRateLimiter } from '@/lib/rate-limit/redis'

export const GET = withRateLimit(
  apiRateLimiter,
  (req) => req.headers.get('x-forwarded-for') || 'unknown'
)(async (request) => {
  const data = await fetchData()
  return NextResponse.json({ data })
})
```

---

## Server Action Protection

### Rate Limited Server Action

```typescript
// src/lib/rate-limit/server-action.ts
'use server'

import { headers } from 'next/headers'
import { RedisRateLimiter } from './redis'

export async function withRateLimitAction<T extends any[], R>(
  rateLimiter: RedisRateLimiter,
  action: (...args: T) => Promise<R>
) {
  return async (...args: T): Promise<R> => {
    const headersList = await headers()
    const ip = headersList.get('x-forwarded-for') || 'unknown'

    const { success, resetAt } = await rateLimiter.check(ip)

    if (!success) {
      const retryAfter = Math.ceil((resetAt - Date.now()) / 1000)
      throw new Error(`Rate limit exceeded. Try again in ${retryAfter} seconds.`)
    }

    return action(...args)
  }
}
```

### Usage in Server Action

```typescript
// src/app/actions/create-project.ts
'use server'

import { withRateLimitAction } from '@/lib/rate-limit/server-action'
import { RedisRateLimiter } from '@/lib/rate-limit/redis'
import { db } from '@/lib/db'

const createProjectRateLimiter = new RedisRateLimiter(
  10,  // 10 projects
  60 * 60 * 1000  // per hour
)

async function createProjectImpl(name: string, description: string) {
  const project = await db.project.create({
    data: { name, description },
  })

  return project
}

export const createProject = withRateLimitAction(
  createProjectRateLimiter,
  createProjectImpl
)
```

---

## IP-Based Rate Limiting

### Get Client IP

```typescript
// src/lib/rate-limit/get-ip.ts
import { NextRequest } from 'next/server'

export function getClientIP(request: NextRequest | Request): string {
  // Check X-Forwarded-For (most common)
  const forwarded = request.headers.get('x-forwarded-for')
  if (forwarded) {
    // X-Forwarded-For can contain multiple IPs (comma-separated)
    return forwarded.split(',')[0].trim()
  }

  // Check X-Real-IP
  const realIp = request.headers.get('x-real-ip')
  if (realIp) {
    return realIp
  }

  // Check CF-Connecting-IP (Cloudflare)
  const cfIp = request.headers.get('cf-connecting-ip')
  if (cfIp) {
    return cfIp
  }

  return 'unknown'
}
```

### IP-Based Rate Limiter

```typescript
// src/lib/rate-limit/ip-based.ts
import { getClientIP } from './get-ip'

export async function checkIPRateLimit(
  request: Request,
  rateLimiter: RedisRateLimiter
) {
  const ip = getClientIP(request)
  return rateLimiter.check(`ip:${ip}`)
}

// Usage
export async function POST(request: Request) {
  const { success } = await checkIPRateLimit(request, loginRateLimiter)

  if (!success) {
    return Response.json(
      { error: 'Too many requests from this IP' },
      { status: 429 }
    )
  }

  // ... rest of handler
}
```

---

## User-Based Rate Limiting

### User-Specific Limits

```typescript
// src/lib/rate-limit/user-based.ts
import { getCurrentUser } from '@/lib/auth/jwt'
import { RedisRateLimiter } from './redis'

export async function checkUserRateLimit(
  rateLimiter: RedisRateLimiter
): Promise<{
  success: boolean
  remaining: number
  resetAt: number
}> {
  const user = await getCurrentUser()

  if (!user) {
    throw new Error('Unauthorized')
  }

  return rateLimiter.check(`user:${user.userId}`)
}

// Usage
export async function POST(request: Request) {
  const { success, remaining } = await checkUserRateLimit(apiRateLimiter)

  if (!success) {
    return Response.json(
      { error: 'You have exceeded your API quota' },
      { status: 429 }
    )
  }

  // ... rest of handler
}
```

### Tiered Rate Limits

```typescript
// src/lib/rate-limit/tiered.ts
interface RateLimitTier {
  maxRequests: number
  windowMs: number
}

const RATE_LIMIT_TIERS: Record<string, RateLimitTier> = {
  FREE: {
    maxRequests: 100,
    windowMs: 60 * 60 * 1000,  // 100 per hour
  },
  PRO: {
    maxRequests: 1000,
    windowMs: 60 * 60 * 1000,  // 1000 per hour
  },
  ENTERPRISE: {
    maxRequests: 10000,
    windowMs: 60 * 60 * 1000,  // 10000 per hour
  },
}

export async function checkTieredRateLimit() {
  const user = await getCurrentUser()

  if (!user) {
    // Use strictest limit for unauthenticated
    const tier = RATE_LIMIT_TIERS.FREE
    const limiter = new RedisRateLimiter(tier.maxRequests, tier.windowMs)
    return limiter.check('anonymous')
  }

  // Get user's plan
  const userPlan = await db.user.findUnique({
    where: { id: user.userId },
    select: { plan: true },
  })

  const tier = RATE_LIMIT_TIERS[userPlan?.plan || 'FREE']
  const limiter = new RedisRateLimiter(tier.maxRequests, tier.windowMs)

  return limiter.check(`user:${user.userId}`)
}
```

---

## Sliding Window Algorithm

### Sliding Window Implementation

```typescript
// src/lib/rate-limit/sliding-window.ts
export class SlidingWindowRateLimiter {
  private store = new Map<string, number[]>()

  constructor(
    private maxRequests: number,
    private windowMs: number
  ) {}

  check(key: string): {
    success: boolean
    remaining: number
    resetAt: number
  } {
    const now = Date.now()
    const windowStart = now - this.windowMs

    // Get timestamps for this key
    let timestamps = this.store.get(key) || []

    // Remove timestamps outside window
    timestamps = timestamps.filter((ts) => ts > windowStart)

    // Check if limit exceeded
    if (timestamps.length >= this.maxRequests) {
      const oldestTimestamp = timestamps[0]
      const resetAt = oldestTimestamp + this.windowMs

      return {
        success: false,
        remaining: 0,
        resetAt,
      }
    }

    // Add current timestamp
    timestamps.push(now)
    this.store.set(key, timestamps)

    return {
      success: true,
      remaining: this.maxRequests - timestamps.length,
      resetAt: now + this.windowMs,
    }
  }

  cleanup() {
    const now = Date.now()

    for (const [key, timestamps] of this.store.entries()) {
      const windowStart = now - this.windowMs
      const filtered = timestamps.filter((ts) => ts > windowStart)

      if (filtered.length === 0) {
        this.store.delete(key)
      } else {
        this.store.set(key, filtered)
      }
    }
  }
}

// Cleanup old entries periodically
setInterval(() => {
  limiter.cleanup()
}, 60 * 1000)  // Every minute
```

---

## Token Bucket Algorithm

### Token Bucket Implementation

```typescript
// src/lib/rate-limit/token-bucket.ts
interface Bucket {
  tokens: number
  lastRefill: number
}

export class TokenBucketRateLimiter {
  private store = new Map<string, Bucket>()

  constructor(
    private capacity: number,      // Maximum tokens
    private refillRate: number,    // Tokens added per second
    private refillInterval: number = 1000  // Refill every 1 second
  ) {}

  check(key: string): {
    success: boolean
    remaining: number
  } {
    const now = Date.now()
    let bucket = this.store.get(key)

    if (!bucket) {
      // Create new bucket
      bucket = {
        tokens: this.capacity - 1,  // Take 1 token
        lastRefill: now,
      }
      this.store.set(key, bucket)

      return {
        success: true,
        remaining: bucket.tokens,
      }
    }

    // Calculate tokens to add based on time elapsed
    const timePassed = now - bucket.lastRefill
    const tokensToAdd = Math.floor(timePassed / this.refillInterval) * this.refillRate

    if (tokensToAdd > 0) {
      bucket.tokens = Math.min(this.capacity, bucket.tokens + tokensToAdd)
      bucket.lastRefill = now
    }

    if (bucket.tokens < 1) {
      return {
        success: false,
        remaining: 0,
      }
    }

    // Take 1 token
    bucket.tokens--

    return {
      success: true,
      remaining: bucket.tokens,
    }
  }
}

// Example: 100 tokens, refill 10 tokens per second
const apiTokenBucket = new TokenBucketRateLimiter(
  100,  // capacity
  10,   // refill 10 tokens/second
  1000  // refill interval (1 second)
)
```

---

## Complete Rate Limiting Middleware

### Global Middleware

```typescript
// src/middleware.ts
import { NextRequest, NextResponse } from 'next/server'
import { RedisRateLimiter } from '@/lib/rate-limit/redis'
import { getClientIP } from '@/lib/rate-limit/get-ip'

const globalRateLimiter = new RedisRateLimiter(
  1000,  // 1000 requests
  60 * 1000  // per minute
)

const authRateLimiter = new RedisRateLimiter(
  5,  // 5 attempts
  15 * 60 * 1000  // per 15 minutes
)

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Choose rate limiter based on path
  let rateLimiter: RedisRateLimiter
  let key: string

  if (pathname.startsWith('/api/auth/')) {
    rateLimiter = authRateLimiter
    key = `auth:${getClientIP(request)}`
  } else {
    rateLimiter = globalRateLimiter
    key = `global:${getClientIP(request)}`
  }

  const { success, remaining, resetAt } = await rateLimiter.check(key)

  if (!success) {
    const retryAfter = Math.ceil((resetAt - Date.now()) / 1000)

    return NextResponse.json(
      {
        error: 'Rate limit exceeded',
        retryAfter,
      },
      {
        status: 429,
        headers: {
          'Retry-After': String(retryAfter),
          'X-RateLimit-Limit': String(rateLimiter['maxRequests']),
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': String(Math.floor(resetAt / 1000)),
        },
      }
    )
  }

  const response = NextResponse.next()

  // Add rate limit headers
  response.headers.set('X-RateLimit-Limit', String(rateLimiter['maxRequests']))
  response.headers.set('X-RateLimit-Remaining', String(remaining))
  response.headers.set('X-RateLimit-Reset', String(Math.floor(resetAt / 1000)))

  return response
}

export const config = {
  matcher: '/api/:path*',
}
```

---

## Summary

**Rate limiting checklist:**

- [ ] Rate limiting enabled on authentication endpoints (login, register, password reset)
- [ ] API endpoints have appropriate rate limits (100-1000 req/min)
- [ ] File upload endpoints rate limited (10-20 files/hour)
- [ ] IP-based rate limiting for anonymous users
- [ ] User-based rate limiting for authenticated users
- [ ] Tiered rate limits based on user plan
- [ ] 429 status code returned on rate limit exceeded
- [ ] Retry-After header included in 429 responses
- [ ] X-RateLimit headers included in all responses
- [ ] Redis used for distributed rate limiting (production)
- [ ] Rate limits documented in API documentation
- [ ] Rate limit exceeded events logged for monitoring
