---
name: edge-computing-patterns
description: Deploy to edge runtimes (Cloudflare Workers, Vercel Edge, Deno Deploy) for globally distributed, low-latency applications. Master edge middleware, streaming, and runtime constraints for 2025+ edge computing.
version: 1.0.0
author: AI Agent Hub
tags: [edge, cloudflare, vercel, deno, serverless, 2025]
---

# Edge Computing Patterns

## Overview

Edge computing runs code closer to users worldwide, reducing latency from seconds to milliseconds. This skill covers Cloudflare Workers, Vercel Edge Functions, and Deno Deploy patterns for building globally distributed applications.

**When to use this skill:**
- Global applications requiring <50ms latency
- Authentication/authorization at the edge
- A/B testing and feature flags
- Geo-routing and localization
- API rate limiting and DDoS protection
- Transforming responses (image optimization, HTML rewriting)

## Platform Comparison

| Feature | Cloudflare Workers | Vercel Edge | Deno Deploy |
|---------|-------------------|-------------|-------------|
| Cold Start | <1ms | <10ms | <10ms |
| Locations | 300+ | 100+ | 35+ |
| Runtime | V8 Isolates | V8 Isolates | Deno |
| Max Duration | 30s (paid: unlimited) | 25s | 50ms-5min |
| Free Tier | 100k req/day | 100k req/month | 100k req/month |

## Cloudflare Workers

```typescript
// worker.ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url)

    // Geo-routing
    const country = request.cf?.country || 'US'

    if (url.pathname === '/api/hello') {
      return new Response(JSON.stringify({
        message: `Hello from ${country}!`
      }), {
        headers: { 'Content-Type': 'application/json' }
      })
    }

    // Cache API
    const cache = caches.default
    let response = await cache.match(request)

    if (!response) {
      response = await fetch(request)
      // Cache for 1 hour
      response = new Response(response.body, response)
      response.headers.set('Cache-Control', 'max-age=3600')
      await cache.put(request, response.clone())
    }

    return response
  }
}

// Durable Objects for stateful edge
export class Counter {
  private state: DurableObjectState
  private count = 0

  constructor(state: DurableObjectState) {
    this.state = state
  }

  async fetch(request: Request) {
    const url = new URL(request.url)

    if (url.pathname === '/increment') {
      this.count++
      await this.state.storage.put('count', this.count)
    }

    return new Response(JSON.stringify({ count: this.count }))
  }
}
```

## Vercel Edge Functions

```typescript
// middleware.ts (Edge Middleware)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // A/B testing
  const bucket = Math.random() < 0.5 ? 'a' : 'b'
  const url = request.nextUrl.clone()
  url.searchParams.set('bucket', bucket)

  // Geo-location
  const country = request.geo?.country || 'US'

  const response = NextResponse.rewrite(url)
  response.cookies.set('bucket', bucket)
  response.headers.set('X-Country', country)

  return response
}

export const config = {
  matcher: '/experiment/:path*'
}

// Edge API Route
export const runtime = 'edge'

export async function GET(request: Request) {
  return new Response(JSON.stringify({
    timestamp: Date.now(),
    region: process.env.VERCEL_REGION
  }))
}
```

## Edge Runtime Constraints

**✅ Available**:
- `fetch`, `Request`, `Response`, `Headers`
- `URL`, `URLSearchParams`
- `TextEncoder`, `TextDecoder`
- `ReadableStream`, `WritableStream`
- `crypto`, `SubtleCrypto`
- Web APIs (atob, btoa, setTimeout, etc.)

**❌ Not Available**:
- Node.js APIs (`fs`, `path`, `child_process`)
- Native modules
- Some npm packages
- File system access

## Common Patterns

### Authentication at Edge
```typescript
import { verify } from '@tsndr/cloudflare-worker-jwt'

export default {
  async fetch(request: Request, env: Env) {
    const token = request.headers.get('Authorization')?.replace('Bearer ', '')

    if (!token) {
      return new Response('Unauthorized', { status: 401 })
    }

    const isValid = await verify(token, env.JWT_SECRET)
    if (!isValid) {
      return new Response('Invalid token', { status: 403 })
    }

    // Proceed with authenticated request
    return fetch(request)
  }
}
```

### Rate Limiting
```typescript
export default {
  async fetch(request: Request, env: Env) {
    const ip = request.headers.get('CF-Connecting-IP')
    const key = `ratelimit:${ip}`

    // Use KV for rate limiting
    const count = await env.KV.get(key)
    const currentCount = count ? parseInt(count) : 0

    if (currentCount >= 100) {
      return new Response('Rate limit exceeded', { status: 429 })
    }

    await env.KV.put(key, (currentCount + 1).toString(), {
      expirationTtl: 60 // 1 minute
    })

    return fetch(request)
  }
}
```

### Edge Caching
```typescript
async function handleRequest(request: Request) {
  const cache = caches.default
  const cacheKey = new Request(request.url, request)

  // Try cache first
  let response = await cache.match(cacheKey)

  if (!response) {
    // Fetch from origin
    response = await fetch(request)

    // Cache successful responses
    if (response.status === 200) {
      response = new Response(response.body, response)
      response.headers.set('Cache-Control', 'max-age=3600')
      await cache.put(cacheKey, response.clone())
    }
  }

  return response
}
```

## Best Practices

- ✅ Keep bundles small (<1MB)
- ✅ Use streaming for large responses
- ✅ Leverage edge caching (KV, Durable Objects)
- ✅ Handle errors gracefully (edge errors can't be recovered)
- ✅ Test cold starts and warm starts
- ✅ Monitor edge function performance
- ✅ Use environment variables for secrets
- ✅ Implement proper CORS headers

## Resources

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Vercel Edge Functions](https://vercel.com/docs/functions/edge-functions)
- [Deno Deploy](https://deno.com/deploy/docs)
