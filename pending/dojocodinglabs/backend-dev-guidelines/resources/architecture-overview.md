# Architecture Overview - Supabase Backend

Complete guide to building backends with Supabase Edge Functions, PostgreSQL, and Row-Level Security.

## Table of Contents

- [Supabase Stack Overview](#supabase-stack-overview)
- [Edge Functions Architecture](#edge-functions-architecture)
- [Request Lifecycle](#request-lifecycle)
- [Database Layer (PostgreSQL + RLS)](#database-layer-postgresql--rls)
- [Authentication Flow](#authentication-flow)
- [Directory Structure Rationale](#directory-structure-rationale)
- [Integration Points](#integration-points)

---

## Supabase Stack Overview

### The Complete Stack

```
┌─────────────────────────────────────────┐
│         Frontend (Next.js)              │
│    @supabase/supabase-js client         │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│      Supabase Edge Functions            │
│      (Deno runtime, TypeScript)         │
│  - Stateless serverless functions       │
│  - JWT verification                     │
│  - Business logic                       │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│     Supabase PostgreSQL Database        │
│  - Row-Level Security (RLS)             │
│  - Real-time subscriptions              │
│  - Full-text search                     │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│     Supporting Services                 │
│  - Supabase Auth (JWT)                  │
│  - Supabase Storage (files)             │
│  - Supabase Realtime (WebSocket)        │
│  - Resend (email)                       │
│  - Stripe (payments)                    │
└─────────────────────────────────────────┘
```

### Key Components

**Edge Functions (Deno)**
- Run on Deno runtime (not Node.js)
- Deploy to edge locations globally
- Auto-scale based on demand
- Cold start < 100ms

**PostgreSQL Database**
- Managed by Supabase
- Built-in connection pooling
- Automatic backups
- Extensions (pgvector, pg_cron, etc.)

**Row-Level Security (RLS)**
- Database-level authorization
- Enforced on every query
- Cannot be bypassed
- Uses JWT claims

**Supabase Auth**
- JWT-based authentication
- Multiple providers (email, OAuth, magic links)
- Session management
- Role-based access

---

## Edge Functions Architecture

### Anatomy of an Edge Function

```typescript
// supabase/functions/create-post/index.ts

import { createClient } from '@supabase/supabase-js'
import { corsHeaders } from '../_shared/cors.ts'
import { z } from 'zod'

// Schema validation
const CreatePostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  tags: z.array(z.string()).optional()
})

Deno.serve(async (req) => {
  // CORS handling
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // 1. Create authenticated Supabase client
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_ANON_KEY')!,
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! }
        }
      }
    )

    // 2. Verify JWT and get user
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    if (authError || !user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // 3. Parse and validate input
    const body = await req.json()
    const validated = CreatePostSchema.parse(body)

    // 4. Database operation (RLS enforced)
    const { data: post, error: dbError } = await supabase
      .from('posts')
      .insert({
        user_id: user.id,
        title: validated.title,
        content: validated.content,
        tags: validated.tags || []
      })
      .select()
      .single()

    if (dbError) throw dbError

    // 5. Return success response
    return new Response(
      JSON.stringify({ success: true, data: post }),
      {
        status: 201,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )

  } catch (error) {
    console.error('Error creating post:', error)
    return new Response(
      JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})
```

### Edge Function Principles

**1. Stateless**
- No in-memory state between requests
- Use database or external services for state
- Each invocation is independent

**2. Single Responsibility**
- One function = one API endpoint
- Clear, focused purpose
- Easy to understand and maintain

**3. Security First**
- Always verify JWT
- Let RLS handle authorization
- Validate all input
- Never trust client data

**4. Performance Optimized**
- Minimize cold start time
- Use efficient queries
- Cache when appropriate
- Return only needed data

---

## Request Lifecycle

### Complete Flow Example

```
1. Frontend makes request
   ↓
   fetch('https://PROJECT.supabase.co/functions/v1/create-post', {
     headers: {
       'Authorization': `Bearer ${session.access_token}`,
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({ title: 'Hello', content: 'World' })
   })

2. Request hits Edge Function
   ↓
   - Deno runtime receives request
   - CORS headers checked (if OPTIONS, return immediately)
   - Function code executes

3. JWT Verification
   ↓
   - Extract Authorization header
   - Pass to Supabase client
   - supabase.auth.getUser() verifies JWT
   - Returns user object if valid

4. Input Validation
   ↓
   - Parse request body
   - Zod schema validation
   - Throws error if invalid

5. Database Operation
   ↓
   - Supabase client makes query
   - RLS policies automatically checked:
     * Check if auth.uid() = user_id (from JWT)
     * Allow/deny based on policy
   - Query executes if allowed

6. Response
   ↓
   - Format response (JSON)
   - Add CORS headers
   - Return Response object
   - Deno runtime sends to client

7. Frontend receives response
   ↓
   - Parse JSON
   - Update UI
   - Handle errors if any
```

### Error Flow

```
Error occurs at any step
    ↓
Catch block executes
    ↓
Log error with console.error()
    ↓
Return Response with:
  - status: 400/401/403/500
  - body: { success: false, error: message }
  - headers: corsHeaders + Content-Type
```

---

## Database Layer (PostgreSQL + RLS)

### Schema Design

```sql
-- Example: Blog posts with RLS

-- 1. Create table
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  tags TEXT[] DEFAULT '{}',
  published BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create indexes
CREATE INDEX posts_user_id_idx ON posts(user_id);
CREATE INDEX posts_published_idx ON posts(published) WHERE published = true;
CREATE INDEX posts_created_at_idx ON posts(created_at DESC);

-- 3. Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 4. Create policies
-- Allow users to read their own posts
CREATE POLICY "users_read_own_posts" ON posts
  FOR SELECT
  USING (auth.uid() = user_id);

-- Allow everyone to read published posts
CREATE POLICY "everyone_read_published" ON posts
  FOR SELECT
  USING (published = true);

-- Allow users to insert their own posts
CREATE POLICY "users_insert_own_posts" ON posts
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Allow users to update their own posts
CREATE POLICY "users_update_own_posts" ON posts
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Allow users to delete their own posts
CREATE POLICY "users_delete_own_posts" ON posts
  FOR DELETE
  USING (auth.uid() = user_id);
```

### RLS Best Practices

**DO ✅**
- Enable RLS on ALL tables with user data
- Create specific policies for each operation (SELECT, INSERT, UPDATE, DELETE)
- Use `auth.uid()` to reference the authenticated user
- Test policies thoroughly with different user roles
- Create indexes on columns used in policies

**DON'T ❌**
- Disable RLS in production
- Create overly complex policies (split into multiple if needed)
- Use `USING (true)` unless table is truly public
- Forget to add policies after enabling RLS (table becomes inaccessible)
- Query database bypassing RLS (always use Supabase client)

---

## Authentication Flow

### JWT-Based Authentication

```typescript
// 1. User signs in (frontend)
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password123'
})
// Returns: { session: { access_token, refresh_token, user } }

// 2. Frontend includes JWT in Edge Function calls
fetch('https://PROJECT.supabase.co/functions/v1/endpoint', {
  headers: {
    'Authorization': `Bearer ${session.access_token}`
  }
})

// 3. Edge Function verifies JWT
const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_ANON_KEY')!,
  {
    global: {
      headers: { Authorization: req.headers.get('Authorization')! }
    }
  }
)

const { data: { user }, error } = await supabase.auth.getUser()
// JWT is verified, user object returned

// 4. RLS uses JWT claims
-- In RLS policy: auth.uid() reads from JWT
-- Supabase automatically includes JWT in database queries
```

### Auth Patterns

**Protected Endpoint**
```typescript
// Require authentication
const { data: { user }, error } = await supabase.auth.getUser()
if (error || !user) {
  return new Response('Unauthorized', { status: 401 })
}
// Continue with user.id, user.email, etc.
```

**Role-Based Access**
```typescript
// Check user role (custom claim)
const { data: { user }, error } = await supabase.auth.getUser()
if (!user || user.user_metadata.role !== 'admin') {
  return new Response('Forbidden', { status: 403 })
}
```

**Optional Auth**
```typescript
// Auth optional, but change behavior if authenticated
const { data: { user } } = await supabase.auth.getUser()
// If user exists, show personalized data
// If not, show public data
```

---

## Directory Structure Rationale

### Project Organization

```
project/
├── supabase/
│   ├── functions/              # Edge Functions
│   │   ├── _shared/            # Shared utilities
│   │   │   ├── cors.ts         # CORS headers
│   │   │   ├── schemas.ts      # Zod schemas
│   │   │   └── utils.ts        # Helper functions
│   │   ├── create-post/
│   │   │   └── index.ts
│   │   ├── send-email/
│   │   │   └── index.ts
│   │   └── webhook-stripe/
│   │       └── index.ts
│   ├── migrations/             # Database schema
│   │   ├── 001_initial.sql
│   │   ├── 002_add_rls.sql
│   │   └── 003_add_features.sql
│   ├── seed.sql                # Test data
│   └── config.toml             # Supabase config
├── lib/
│   └── supabase/
│       ├── client.ts           # Client setup (frontend)
│       ├── server.ts           # Server client (SSR)
│       └── types.ts            # Type helpers
└── types/
    └── database.types.ts       # Generated from schema
```

### Why This Structure?

**_shared/ directory**
- Reusable code across functions
- Import with `../shared/cors.ts`
- Avoids duplication

**One function per directory**
- Clear organization
- Independent deployment
- Easy to locate code

**Migrations in order**
- Sequential numbering (001, 002, etc.)
- Each migration is atomic
- Easy rollback

**Generated types**
```bash
supabase gen types typescript --local > types/database.types.ts
```
- Type-safe database access
- Autocomplete in IDE
- Catch errors early

---

## Integration Points

### Resend (Email)

```typescript
import { Resend } from 'resend'

const resend = new Resend(Deno.env.get('RESEND_API_KEY'))

await resend.emails.send({
  from: 'noreply@example.com',
  to: user.email,
  subject: 'Welcome!',
  html: '<h1>Welcome to our app</h1>'
})
```

### Stripe (Payments)

```typescript
import Stripe from 'stripe'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!, {
  httpClient: Stripe.createFetchHttpClient()
})

const session = await stripe.checkout.sessions.create({
  customer_email: user.email,
  line_items: [{ price: 'price_123', quantity: 1 }],
  mode: 'payment',
  success_url: 'https://example.com/success',
  cancel_url: 'https://example.com/cancel'
})
```

### Supabase Storage

```typescript
// Upload file
const { data, error } = await supabase.storage
  .from('avatars')
  .upload(`${user.id}/avatar.png`, file)

// Get public URL
const { data: { publicUrl } } = supabase.storage
  .from('avatars')
  .getPublicUrl(`${user.id}/avatar.png`)
```

### Supabase Realtime

```typescript
// Subscribe to changes (frontend)
const channel = supabase
  .channel('posts')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'posts'
  }, (payload) => {
    console.log('Change received!', payload)
  })
  .subscribe()
```

---

## Performance Considerations

### Edge Function Optimization

**Minimize Cold Starts**
```typescript
// ❌ SLOW: Large imports
import _ from 'lodash'

// ✅ FAST: Import only what you need
import { pick } from 'lodash/pick'
```

**Efficient Queries**
```typescript
// ❌ SLOW: Fetch all columns
const { data } = await supabase.from('posts').select('*')

// ✅ FAST: Select only needed columns
const { data } = await supabase.from('posts').select('id, title, created_at')
```

**Use Indexes**
```sql
-- Add indexes for frequently queried columns
CREATE INDEX posts_user_id_idx ON posts(user_id);
CREATE INDEX posts_created_at_idx ON posts(created_at DESC);
```

### Caching Strategies

**Database-level caching**
- PostgreSQL query cache (automatic)
- Use prepared statements when possible

**CDN caching**
- Supabase Storage includes CDN
- Edge Functions can set Cache-Control headers

**Application-level caching**
- Use Supabase Realtime for live data
- Cache static data in frontend state

---

## Security Best Practices

1. **Always verify JWT** - Never trust Authorization header without verification
2. **Use RLS religiously** - Enable on ALL tables, create specific policies
3. **Validate input** - Use Zod or similar for all user input
4. **Environment variables** - Never hardcode secrets
5. **HTTPS only** - Supabase enforces this automatically
6. **Rate limiting** - Configure in Supabase dashboard
7. **CORS properly** - Only allow trusted origins
8. **Audit logs** - Track sensitive operations

---

## Deployment

### Local Development

```bash
# Start Supabase locally
supabase start

# Serve function locally
supabase functions serve create-post --env-file .env.local

# Test with curl
curl http://localhost:54321/functions/v1/create-post
```

### Production Deployment

```bash
# Deploy single function
supabase functions deploy create-post

# Deploy all functions
supabase functions deploy

# Set secrets
supabase secrets set RESEND_API_KEY=re_abc123
supabase secrets set STRIPE_SECRET_KEY=sk_live_abc123
```

### Monitoring

- **Logs**: Supabase Dashboard → Edge Functions → Logs
- **Metrics**: Function invocations, errors, duration
- **Alerts**: Configure in dashboard for error thresholds

---

**Related Resources:**
- [edge-functions-guide.md](edge-functions-guide.md) - Detailed Edge Function patterns
- [database-and-rls.md](database-and-rls.md) - Database design and RLS
- [auth-patterns.md](auth-patterns.md) - Authentication flows
- [complete-examples.md](complete-examples.md) - Full working examples
