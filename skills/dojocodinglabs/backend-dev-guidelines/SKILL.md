---
name: backend-dev-guidelines
description: Comprehensive backend development guide for Supabase Edge Functions + PostgreSQL. Use when working with Supabase (database, auth, storage, realtime), Edge Functions, PostgreSQL, Row-Level Security (RLS), Resend email, Stripe payments, or TypeScript backend patterns. Covers database design, auth flows, Edge Function patterns, RLS policies, email integration, payment processing, and deployment to Supabase.
---

> **📋 OPINIONATED SCAFFOLD**: Modern Supabase + Edge Functions stack
>
> **Default Stack**:
> - **Backend**: Supabase Edge Functions (Deno runtime)
> - **Database**: Supabase PostgreSQL + Row-Level Security
> - **Auth**: Supabase Auth (JWT-based)
> - **Storage**: Supabase Storage
> - **Email**: Resend (transactional emails)
> - **Payments**: Stripe (subscriptions + one-time)
> - **Language**: TypeScript
> - **Deployment**: Git push to Supabase
>
> **To customize**: Run `/customize-scaffold backend` or use the scaffold-customizer agent
> to adapt for Express, NestJS, Fastify, Django, Rails, Go, or other frameworks.

# Backend Development Guidelines

## Purpose

Establish consistency and best practices for Supabase-powered backends using Edge Functions, PostgreSQL with Row-Level Security, and TypeScript. This skill covers database design, authentication flows, API patterns, email integration, and payment processing.

## When to Use This Skill

Automatically activates when working on:
- Creating or modifying Supabase Edge Functions
- Designing PostgreSQL database schemas
- Implementing Row-Level Security (RLS) policies
- Building authentication flows with Supabase Auth
- Integrating Supabase Storage for file uploads
- Sending transactional emails with Resend
- Processing payments with Stripe
- Input validation with Zod
- Testing with Supabase CLI
- Backend deployment and configuration

---

## Quick Start

### New Edge Function Checklist

- [ ] **Function**: Create in `supabase/functions/[name]/index.ts`
- [ ] **Validation**: Zod schema for input
- [ ] **Auth**: JWT verification with Supabase client
- [ ] **Database**: Use Supabase client with RLS
- [ ] **Error handling**: Try/catch with proper responses
- [ ] **CORS**: Configure allowed origins
- [ ] **Tests**: Local testing with Supabase CLI
- [ ] **Deploy**: `supabase functions deploy [name]`

### New Feature Checklist

- [ ] **Database**: Create migration with schema changes
- [ ] **RLS**: Add appropriate security policies
- [ ] **Edge Function**: Implement API endpoint
- [ ] **Frontend Integration**: Update Supabase client calls
- [ ] **Testing**: Test locally before deploy
- [ ] **Monitoring**: Check logs after deployment

---

## Architecture Overview

### Supabase Stack Architecture

```
HTTP Request
    ↓
Edge Function (Deno runtime)
    ↓
Supabase Client (Auth + validation)
    ↓
PostgreSQL Database (with RLS)
    ↓
Response with JSON
```

**Key Principle:** Edge Functions are stateless, RLS enforces data security.

**Integrations:**
- **Supabase Auth** → JWT-based authentication
- **Supabase Storage** → File uploads and CDN
- **Supabase Realtime** → WebSocket subscriptions
- **Resend** → Transactional emails
- **Stripe** → Payment processing

See [architecture-overview.md](resources/architecture-overview.md) for complete details.

---

## Directory Structure

```
project/
├── supabase/
│   ├── functions/           # Edge Functions
│   │   ├── create-user/
│   │   │   └── index.ts
│   │   ├── send-email/
│   │   │   └── index.ts
│   │   └── process-payment/
│   │       └── index.ts
│   ├── migrations/          # Database migrations
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_add_rls.sql
│   │   └── 003_add_indexes.sql
│   ├── seed.sql             # Test data
│   └── config.toml          # Supabase config
├── lib/
│   └── supabase/
│       ├── client.ts        # Supabase client setup
│       ├── auth.ts          # Auth utilities
│       └── types.ts         # Database types
└── types/
    └── database.types.ts    # Generated from schema
```

**Naming Conventions:**
- Edge Functions: `kebab-case` - `create-user`, `send-email`
- Database tables: `snake_case` - `user_profiles`, `subscription_plans`
- RLS policies: `snake_case` - `users_select_own`, `posts_insert_authenticated`
- TypeScript types: `PascalCase` - `UserProfile`, `SubscriptionPlan`

---

## Core Principles (7 Key Rules)

### 1. Edge Functions are Simple and Focused

```typescript
// ❌ NEVER: 500-line Edge Function
Deno.serve(async (req) => {
    // Massive logic...
});

// ✅ ALWAYS: Focused, single-purpose functions
Deno.serve(async (req) => {
    const user = await getUserFromRequest(req);
    const result = await createPost(user.id, req);
    return new Response(JSON.stringify(result), { status: 201 });
});
```

### 2. Always Verify JWT Tokens

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_ANON_KEY')!,
    {
        global: {
            headers: { Authorization: req.headers.get('Authorization')! }
        }
    }
);

const { data: { user }, error } = await supabase.auth.getUser();
if (error || !user) {
    return new Response('Unauthorized', { status: 401 });
}
```

### 3. Use RLS for Data Security

```sql
-- Enable RLS on all tables
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Users can only read their own data
CREATE POLICY "users_select_own" ON posts
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own data
CREATE POLICY "posts_insert_own" ON posts
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);
```

### 4. Validate All Input with Zod

```typescript
import { z } from 'zod';

const CreatePostSchema = z.object({
    title: z.string().min(1).max(200),
    content: z.string().min(1),
    tags: z.array(z.string()).optional()
});

const body = await req.json();
const validated = CreatePostSchema.parse(body); // Throws if invalid
```

### 5. Use Environment Variables via Deno.env

```typescript
// ❌ NEVER: Hardcode secrets
const apiKey = 'sk_live_abc123';

// ✅ ALWAYS: Use environment variables
const apiKey = Deno.env.get('STRIPE_API_KEY')!;
const resendKey = Deno.env.get('RESEND_API_KEY')!;
```

### 6. Handle Errors Gracefully

```typescript
try {
    const result = await performOperation();
    return new Response(JSON.stringify({ success: true, data: result }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
    });
} catch (error) {
    console.error('Operation failed:', error);
    return new Response(JSON.stringify({
        success: false,
        error: error.message
    }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
    });
}
```

### 7. Test Locally Before Deploying

```bash
# Start Supabase locally
supabase start

# Test Edge Function locally
supabase functions serve create-user --env-file .env.local

# Run tests
curl -i http://localhost:54321/functions/v1/create-user \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"email":"test@example.com"}'
```

---

## Common Imports

```typescript
// Supabase
import { createClient } from '@supabase/supabase-js';
import type { Database } from '../types/database.types.ts';

// Validation
import { z } from 'zod';

// Email (Resend)
import { Resend } from 'resend';

// Payments (Stripe)
import Stripe from 'stripe';

// CORS helper
import { corsHeaders } from '../_shared/cors.ts';
```

---

## Quick Reference

### HTTP Status Codes

| Code | Use Case |
|------|----------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (DELETE success) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (no/invalid token) |
| 403 | Forbidden (valid token, no permission) |
| 404 | Not Found |
| 500 | Server Error |

### Common Edge Function Patterns

**Auth Check** → Verify JWT, get user
**CRUD Operations** → Create, Read, Update, Delete with RLS
**Email Sending** → Resend integration
**Payment Processing** → Stripe webhooks and charges
**File Upload** → Supabase Storage integration

---

## Anti-Patterns to Avoid

❌ Skipping JWT verification
❌ Querying database without RLS
❌ No input validation
❌ Exposing secrets in code
❌ Missing error handling
❌ Deploying without local testing
❌ Direct database access (bypassing RLS)
❌ console.log for production errors (use proper logging)

---

## Example Resource Files

> **📝 Note**: This is a **scaffold skill** with example resources. The provided resources demonstrate the pattern - you should generate additional resources as needed for your specific project.

### ✅ Provided Examples

**[architecture-overview.md](resources/architecture-overview.md)** - Complete Supabase stack architecture
**[edge-functions-guide.md](resources/edge-functions-guide.md)** - Edge Function patterns and deployment
**[database-and-rls.md](resources/database-and-rls.md)** - Database design and RLS policies

### 📋 Generate On-Demand

When you need guidance on a specific topic, ask Claude to generate a resource file following the same pattern as the examples above. Common topics:

- **Validation patterns** - Zod schemas and error handling
- **Auth patterns** - JWT verification, session management
- **Storage patterns** - File uploads, CDN, signed URLs
- **Email integration** - Resend templates and sending
- **Stripe integration** - Payments, subscriptions, webhooks
- **Testing guide** - Local testing, integration tests
- **Complete examples** - Full working Edge Function examples

**How to request**: "Generate a resource file for [topic] following the pattern in architecture-overview.md"

---

## Customization Instructions

### For Your Tech Stack

**Not using Supabase?** Use the scaffold-customizer agent or manual replacement:

```bash
# Option 1: Automated
# Claude will detect your stack and offer to customize

# Option 2: Manual find-and-replace
Supabase → Your database (Prisma, TypeORM, etc.)
Edge Functions → Your backend (Express, NestJS, etc.)
PostgreSQL → Your database (MySQL, MongoDB, etc.)
RLS → Your auth strategy
```

### For Your Domain

Replace the generic examples with your domain:
- Update "posts" table → your entities
- Update "users" → your user model
- Update business logic examples

### For Your Patterns

Adapt the principles to your architecture:
- Keep security-first approach
- Keep validation patterns
- Keep error handling patterns
- Adjust structure to your needs

---

## Related Skills

- **frontend-dev-guidelines** - Next.js + React patterns for Supabase integration
- **memory-management** - Track architectural decisions
- **skill-developer** - Meta-skill for creating and managing skills

---

**Skill Status**: SCAFFOLD ✅
**Line Count**: < 500 ✅
**Progressive Disclosure**: Example resources + generation instructions ✅
