# Supabase Auth Integration

This application uses **Supabase Auth** for authentication. This document explains how Supabase auth integrates with the API client pattern.

## Supabase Client Files

All Supabase clients live in `src/lib/supabase/`:

```
src/lib/supabase/
├── client.ts      # Browser-side client for Client Components
├── server.ts      # Server-side client for RSC and Server Actions
└── middleware.ts  # Middleware helper for auth session refresh
```

### client.ts (Browser-Side)
```typescript
import { createBrowserClient } from '@supabase/ssr';

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!
  );
}
```

**Usage:** Import in Client Components (`'use client'`)

### server.ts (Server-Side)
```typescript
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function createClient() {
  const cookieStore = await cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          } catch {
            // Ignore if called from Server Component
          }
        }
      }
    }
  );
}
```

**Usage:** Import in Server Components, Server Actions, Route Handlers

### middleware.ts (Auth Refresh)
```typescript
import { NextResponse, type NextRequest } from 'next/server';
import { createServerClient } from '@supabase/ssr';

export async function updateSession(request: NextRequest) {
  const response = NextResponse.next();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            request.cookies.set({ name, value, ...options });
            response.cookies.set({ name, value, ...options });
          });
        }
      }
    }
  );

  // Refresh auth session
  await supabase.auth.getUser();
  return response;
}
```

**Usage:** Called from `src/middleware.ts` on every request

## Middleware Setup

Root middleware file (`src/middleware.ts`):

```typescript
import type { NextRequest } from 'next/server';
import { updateSession } from '@/lib/supabase/middleware';

export async function middleware(request: NextRequest) {
  return updateSession(request);
}

export const config = {
  matcher: [
    // Skip static files, include everything else
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'
  ]
};
```

This ensures auth session is refreshed on every request.

## API Client Integration

### getAuthHeaders Implementation

In `src/lib/api/api-client.ts`:

```typescript
'use server';

import { createClient } from '@/lib/supabase/server';

/**
 * Get authentication headers for API requests
 */
export async function getAuthHeaders(): Promise<Record<string, string>> {
  const supabase = await createClient();
  const { data: { session } } = await supabase.auth.getSession();

  if (!session?.access_token) {
    throw new Error('Unauthorized: No access token available');
  }

  return {
    Authorization: `Bearer ${session.access_token}`
  };
}
```

**How It Works:**
1. Creates Supabase server client
2. Gets current auth session from cookies
3. Extracts access token from session
4. Returns Authorization header with Bearer token
5. Throws error if no session exists

### Admin Role Checking

In `src/lib/api/admin-api-client.ts`:

```typescript
'use server';

import { createClient } from '@/lib/supabase/server';

/**
 * Validate if current user has admin access
 */
export async function validateAdminAccess(): Promise<boolean> {
  const supabase = await createClient();

  // Get current user from session
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return false;
  }

  // Query users table for role
  const { data: userData } = await supabase
    .from('users')
    .select('role')
    .eq('id', user.id)
    .single();

  return userData?.role === 'admin';
}

/**
 * Check admin permission and throw if not authorized
 */
export async function checkAdminPermission(): Promise<void> {
  const hasAccess = await validateAdminAccess();
  if (!hasAccess) {
    throw new AdminAuthError('Admin access required');
  }
}
```

**How It Works:**
1. Creates Supabase server client
2. Gets current authenticated user
3. Queries `users` table for user's role
4. Returns true if role is 'admin'
5. Throws `AdminAuthError` if not admin

## Multi-Tenant Architecture

### Family-Based Access Control

All users belong to a `family` (household):
- `users.family_id` links user to family
- RLS policies enforce family-level isolation
- First user in family gets 'admin' role

### Row Level Security (RLS)

Example RLS policy for family-scoped data:

```sql
-- Enable RLS
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;

-- Family isolation policy
CREATE POLICY "family_isolation_accounts" ON accounts
  FOR ALL
  USING (
    family_id IN (
      SELECT family_id FROM users WHERE id = auth.uid()
    )
  );
```

**How It Works:**
1. `auth.uid()` returns current Supabase user ID
2. Looks up user's family_id from users table
3. Only returns rows where family_id matches
4. Enforced at database level (PostgreSQL)

## Environment Variables

Required in `.env.local`:

```bash
# Supabase Auth
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=your-anon-key

# External API (if using)
INSTANCE_API_URL=https://api.example.com

# Site URL (optional)
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

## Auth Flow Diagram

```
1. User logs in → Supabase Auth
   ↓
2. Supabase stores session in httpOnly cookies
   ↓
3. Every request → Middleware refreshes session
   ↓
4. Server Component/Action needs data
   ↓
5. Calls protected endpoint: api.resources.list()
   ↓
6. api-client calls getAuthHeaders()
   ↓
7. getAuthHeaders uses createClient() from server.ts
   ↓
8. Fetches session from cookies
   ↓
9. Extracts access_token from session
   ↓
10. Returns { Authorization: "Bearer <token>" }
   ↓
11. API request sent with auth header
```

## Common Patterns

### Server Component
```typescript
import { api } from '@/lib/api/protected-endpoints';

export default async function Page() {
  // Auth automatic from Supabase session
  const data = await api.resources.list();

  return <div>{/* render data */}</div>;
}
```

### Server Action
```typescript
'use server';

import { api } from '@/lib/api/protected-endpoints';

export async function createResource(formData: FormData) {
  const name = formData.get('name') as string;

  // Auth automatic from Supabase session
  const resource = await api.resources.create({ name });

  return { success: true, resource };
}
```

### Client Component with Server Action
```typescript
'use client';

import { createResource } from './actions';

export function ResourceForm() {
  async function handleSubmit(formData: FormData) {
    await createResource(formData);
  }

  return (
    <form action={handleSubmit}>
      <input name="name" />
      <button>Create</button>
    </form>
  );
}
```

### Admin-Protected Endpoint
```typescript
'use server';

import { checkAdminPermission } from '@/lib/api/admin-api-client';
import { api } from '@/lib/api/protected-endpoints';

export async function deleteAllResources() {
  // Verify admin role first
  await checkAdminPermission();

  // Then proceed with admin operation
  await api.admin.deleteAll();

  return { success: true };
}
```

## Database Schema Integration

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,          -- Links to auth.users.id
  family_id UUID NOT NULL REFERENCES families(id),
  email VARCHAR NOT NULL,
  first_name VARCHAR,
  last_name VARCHAR,
  role VARCHAR NOT NULL DEFAULT 'member', -- 'admin' or 'member'
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Families Table
```sql
CREATE TABLE families (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR NOT NULL,
  currency VARCHAR DEFAULT 'USD',
  country VARCHAR DEFAULT 'US',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## Best Practices

1. **Always use server.ts in server code** - Never use client.ts in Server Components/Actions
2. **Middleware refreshes sessions** - Don't manually refresh
3. **RLS enforces security** - Database-level protection
4. **Admin checks first** - Call checkAdminPermission() before admin operations
5. **Trust auth.uid()** - Supabase JWT is verified by PostgreSQL
6. **Family isolation** - All sensitive data scoped to family_id
7. **httpOnly cookies** - Supabase sessions stored securely
8. **Access tokens auto-refresh** - Middleware handles this

## Troubleshooting

### "Unauthorized: No access token available"
- User not logged in
- Session expired
- Check middleware is running
- Verify environment variables

### "Admin access required"
- User role is not 'admin'
- Check users table for correct role
- Verify family_id is correct

### RLS blocking queries
- Check RLS policies are correct
- Verify auth.uid() returns user ID
- Check user's family_id matches data

### Session not persisting
- Verify middleware is configured correctly
- Check cookie settings
- Ensure NEXT_PUBLIC_SUPABASE_URL is set
