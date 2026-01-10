# Edge Functions Guide

Comprehensive guide to creating, deploying, and managing Supabase Edge Functions.

## Table of Contents

- [Creating Edge Functions](#creating-edge-functions)
- [Request and Response Handling](#request-and-response-handling)
- [CORS Configuration](#cors-configuration)
- [Error Handling](#error-handling)
- [Testing Edge Functions](#testing-edge-functions)
- [Deployment](#deployment)
- [Common Patterns](#common-patterns)

---

## Creating Edge Functions

### Generate New Function

```bash
# Create new Edge Function
supabase functions new my-function

# Creates:
# supabase/functions/my-function/
#   └── index.ts
```

### Basic Template

```typescript
// supabase/functions/my-function/index.ts

import { createClient } from '@supabase/supabase-js'
import { corsHeaders } from '../_shared/cors.ts'

Deno.serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Your logic here
    return new Response(
      JSON.stringify({ success: true }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400
      }
    )
  }
})
```

---

## Request and Response Handling

### Reading Request Data

```typescript
// Query parameters
const url = new URL(req.url)
const id = url.searchParams.get('id')

// Request headers
const authHeader = req.headers.get('Authorization')
const contentType = req.headers.get('Content-Type')

// Request body (JSON)
const body = await req.json()

// Request body (FormData)
const formData = await req.formData()
const file = formData.get('file')

// Request body (text)
const text = await req.text()
```

### Creating Responses

```typescript
// JSON response
return new Response(
  JSON.stringify({ data: result }),
  {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  }
)

// Text response
return new Response('Success', { status: 200 })

// Redirect
return new Response(null, {
  status: 302,
  headers: { 'Location': 'https://example.com' }
})

// Stream response
const stream = new ReadableStream({
  start(controller) {
    controller.enqueue('chunk 1')
    controller.enqueue('chunk 2')
    controller.close()
  }
})
return new Response(stream)
```

---

## CORS Configuration

### Shared CORS Helper

```typescript
// supabase/functions/_shared/cors.ts

export const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}
```

### Production CORS (Restricted Origins)

```typescript
// supabase/functions/_shared/cors.ts

const allowedOrigins = [
  'https://yourdomain.com',
  'https://app.yourdomain.com'
]

export function getCorsHeaders(origin: string | null) {
  if (origin && allowedOrigins.includes(origin)) {
    return {
      'Access-Control-Allow-Origin': origin,
      'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
      'Access-Control-Allow-Credentials': 'true'
    }
  }
  return {
    'Access-Control-Allow-Origin': allowedOrigins[0],
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  }
}

// Usage in function:
const origin = req.headers.get('Origin')
const corsHeaders = getCorsHeaders(origin)
```

### Handling OPTIONS Requests

```typescript
Deno.serve(async (req) => {
  // Always handle OPTIONS first
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  // Your function logic...
})
```

---

## Error Handling

### Structured Error Responses

```typescript
interface ErrorResponse {
  success: false
  error: {
    message: string
    code?: string
    details?: unknown
  }
}

function errorResponse(message: string, status: number, code?: string): Response {
  return new Response(
    JSON.stringify({
      success: false,
      error: { message, code }
    }),
    {
      status,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    }
  )
}

// Usage:
if (!user) {
  return errorResponse('Unauthorized', 401, 'AUTH_REQUIRED')
}
```

### Error Categories

```typescript
// Authentication errors (401)
return errorResponse('Invalid or missing token', 401, 'INVALID_TOKEN')

// Authorization errors (403)
return errorResponse('Insufficient permissions', 403, 'FORBIDDEN')

// Validation errors (400)
return errorResponse('Invalid input', 400, 'VALIDATION_ERROR')

// Not found (404)
return errorResponse('Resource not found', 404, 'NOT_FOUND')

// Server errors (500)
return errorResponse('Internal server error', 500, 'INTERNAL_ERROR')
```

### Zod Validation Errors

```typescript
import { z } from 'zod'

try {
  const validated = schema.parse(body)
} catch (error) {
  if (error instanceof z.ZodError) {
    return new Response(
      JSON.stringify({
        success: false,
        error: {
          message: 'Validation failed',
          code: 'VALIDATION_ERROR',
          details: error.errors
        }
      }),
      {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
  throw error
}
```

---

## Testing Edge Functions

### Local Testing

```bash
# Start Supabase locally
supabase start

# Serve function (auto-reloads on changes)
supabase functions serve my-function --env-file .env.local

# Function available at:
# http://localhost:54321/functions/v1/my-function
```

### Test with curl

```bash
# GET request
curl http://localhost:54321/functions/v1/my-function

# POST with JSON
curl -X POST http://localhost:54321/functions/v1/my-function \
  -H "Content-Type: application/json" \
  -d '{"key":"value"}'

# With authorization
curl http://localhost:54321/functions/v1/my-function \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test with Deno Test

```typescript
// supabase/functions/my-function/index.test.ts

import { assert, assertEquals } from 'https://deno.land/std@0.192.0/testing/asserts.ts'

Deno.test('My function returns success', async () => {
  const req = new Request('http://localhost/test', {
    method: 'POST',
    body: JSON.stringify({ test: true })
  })

  const response = await handler(req) // Your function
  const data = await response.json()

  assertEquals(response.status, 200)
  assert(data.success)
})
```

---

## Deployment

### Deploy Single Function

```bash
# Deploy to production
supabase functions deploy my-function

# Deploy with environment variables
supabase secrets set API_KEY=abc123
supabase functions deploy my-function
```

### Deploy All Functions

```bash
# Deploy all functions at once
supabase functions deploy
```

### Environment Variables

```bash
# Set secrets (encrypted, not visible in dashboard)
supabase secrets set STRIPE_SECRET_KEY=sk_live_...
supabase secrets set RESEND_API_KEY=re_...

# List secrets (shows names only, not values)
supabase secrets list

# Remove secret
supabase secrets unset API_KEY
```

### Invoke Deployed Function

```bash
# Invoke function from CLI
supabase functions invoke my-function \
  --body '{"key":"value"}' \
  --headers '{"Authorization":"Bearer TOKEN"}'
```

---

## Common Patterns

### Authenticated Endpoint

```typescript
import { createClient } from '@supabase/supabase-js'

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  // Create authenticated client
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_ANON_KEY')!,
    {
      global: {
        headers: { Authorization: req.headers.get('Authorization')! }
      }
    }
  )

  // Verify auth
  const { data: { user }, error } = await supabase.auth.getUser()
  if (error || !user) {
    return errorResponse('Unauthorized', 401)
  }

  // User is authenticated, proceed...
  return new Response(
    JSON.stringify({ user_id: user.id }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
})
```

### CRUD Endpoint

```typescript
Deno.serve(async (req) => {
  const url = new URL(req.url)
  const method = req.method

  // Auth check...
  const supabase = createClient(/* ... */)
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return errorResponse('Unauthorized', 401)

  // Route based on method
  switch (method) {
    case 'GET': {
      const id = url.searchParams.get('id')
      const { data, error } = await supabase
        .from('posts')
        .select('*')
        .eq('id', id)
        .single()

      if (error) return errorResponse('Not found', 404)
      return jsonResponse(data)
    }

    case 'POST': {
      const body = await req.json()
      const { data, error } = await supabase
        .from('posts')
        .insert({ ...body, user_id: user.id })
        .select()
        .single()

      if (error) return errorResponse(error.message, 400)
      return jsonResponse(data, 201)
    }

    case 'PUT': {
      const id = url.searchParams.get('id')
      const body = await req.json()
      const { data, error } = await supabase
        .from('posts')
        .update(body)
        .eq('id', id)
        .select()
        .single()

      if (error) return errorResponse(error.message, 400)
      return jsonResponse(data)
    }

    case 'DELETE': {
      const id = url.searchParams.get('id')
      const { error } = await supabase
        .from('posts')
        .delete()
        .eq('id', id)

      if (error) return errorResponse(error.message, 400)
      return new Response(null, { status: 204 })
    }

    default:
      return errorResponse('Method not allowed', 405)
  }
})
```

### Webhook Handler

```typescript
import Stripe from 'stripe'

Deno.serve(async (req) => {
  const signature = req.headers.get('stripe-signature')
  const body = await req.text()

  const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!, {
    httpClient: Stripe.createFetchHttpClient()
  })

  try {
    // Verify webhook signature
    const event = stripe.webhooks.constructEvent(
      body,
      signature!,
      Deno.env.get('STRIPE_WEBHOOK_SECRET')!
    )

    // Handle event
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutComplete(event.data.object)
        break
      case 'customer.subscription.created':
        await handleSubscriptionCreated(event.data.object)
        break
      // ... other events
    }

    return new Response(JSON.stringify({ received: true }), { status: 200 })
  } catch (error) {
    console.error('Webhook error:', error)
    return errorResponse('Webhook signature verification failed', 400)
  }
})
```

### Background Job

```typescript
// Triggered via cron or manual invocation
Deno.serve(async (req) => {
  // Verify request is from Supabase (check secret header)
  const secret = req.headers.get('x-supabase-secret')
  if (secret !== Deno.env.get('SUPABASE_FUNCTION_SECRET')) {
    return errorResponse('Unauthorized', 401)
  }

  // Perform background task
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')! // Service role for admin access
  )

  // Process batch of items
  const { data: items } = await supabase
    .from('queue')
    .select('*')
    .limit(100)

  for (const item of items) {
    await processItem(item)
  }

  return jsonResponse({ processed: items.length })
})
```

### File Upload Handler

```typescript
Deno.serve(async (req) => {
  const formData = await req.formData()
  const file = formData.get('file') as File

  if (!file) {
    return errorResponse('No file provided', 400)
  }

  // Auth check...
  const supabase = createClient(/* ... */)
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return errorResponse('Unauthorized', 401)

  // Upload to Supabase Storage
  const fileName = `${user.id}/${crypto.randomUUID()}-${file.name}`
  const { data, error } = await supabase.storage
    .from('uploads')
    .upload(fileName, file, {
      contentType: file.type,
      cacheControl: '3600'
    })

  if (error) return errorResponse(error.message, 500)

  // Get public URL
  const { data: { publicUrl } } = supabase.storage
    .from('uploads')
    .getPublicUrl(fileName)

  return jsonResponse({ url: publicUrl })
})
```

---

## Performance Tips

1. **Minimize cold starts**
   - Keep functions small (< 1MB bundled)
   - Import only what you need
   - Use dynamic imports for large dependencies

2. **Optimize queries**
   - Select only needed columns
   - Use indexes
   - Limit result sets

3. **Cache responses**
   - Set Cache-Control headers for static data
   - Use Supabase Realtime for frequently changing data

4. **Parallel operations**
```typescript
// ❌ Sequential (slow)
const user = await getUser(id)
const posts = await getPosts(user.id)
const comments = await getComments(user.id)

// ✅ Parallel (fast)
const [user, posts, comments] = await Promise.all([
  getUser(id),
  getPosts(id),
  getComments(id)
])
```

---

## Debugging

### View Logs

```bash
# Real-time logs
supabase functions logs my-function --tail

# Recent logs
supabase functions logs my-function --limit 100
```

### Console Logging

```typescript
// Logs appear in Supabase dashboard and CLI
console.log('Info message')
console.error('Error message')
console.warn('Warning message')

// Structured logging
console.log(JSON.stringify({
  level: 'info',
  message: 'User action',
  user_id: user.id,
  action: 'create_post'
}))
```

---

**Related Resources:**
- [architecture-overview.md](architecture-overview.md) - Complete stack architecture
- [database-and-rls.md](database-and-rls.md) - Database patterns
- [validation-patterns.md](validation-patterns.md) - Input validation
- [complete-examples.md](complete-examples.md) - Full examples
