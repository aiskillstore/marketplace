# Authentication Security Best Practices

## Token Validation

### ✅ DO
- Always use `supabase.auth.getUser()` to validate tokens
- getUser() makes a request to Supabase Auth server to revalidate the token
- Safe to use in middleware, Server Components, Server Actions, Route Handlers

### ❌ DON'T
- Never trust `supabase.auth.getSession()` in server code
- getSession() doesn't revalidate tokens and can be spoofed
- Session data can be manipulated on client side

## Server-Side Authorization

### ✅ DO
- Use `requireAuthRedirect()` in page layouts and Server Components
- Use `requireAuth()` in Server Actions that need authentication
- Store all auth logic server-side (never in Client Components)
- Use React `cache()` for request-level caching of auth checks
- Validate user's family access with `requireFamilyAccess()` for multi-tenant data

### ❌ DON'T
- Never add `'use server'` directive to server-auth.ts (breaks class exports)
- Never skip authentication checks in protected routes
- Never trust client-side role/permission checks for authorization
- Never expose sensitive auth helpers to Client Components

## Environment Security

### Required Variables
```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=eyJxxx...
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### ⚠️ Important
- Never commit `.env` to version control
- Use environment-specific values for production
- Rotate keys if exposed

## Middleware Best Practices

### Token Refresh
- Middleware refreshes tokens automatically on every request
- Uses `updateSession()` from `src/lib/supabase/middleware.ts`
- Passes refreshed tokens to both request and response
- Server Components receive refreshed auth state

### Matcher Configuration
- Exclude static files, images, and assets
- Prevents unnecessary middleware runs
- Current matcher: `/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)`

## Server Actions Security

### POST Request Handling
- Next.js middleware redirects don't work with Server Actions (POST requests)
- Server Actions return 307 but user won't be redirected
- **Solution**: Skip POST requests in middleware, validate in each Server Action

### Pattern
```typescript
'use server';
import { requireAuth } from '@/lib/auth/server-auth';

export async function myAction() {
  const user = await requireAuth(); // Throws if not authenticated
  // Proceed with action
}
```

## Multi-Tenant Data Isolation

### Family-Based Access Control
- Every user belongs to a family (household)
- Use `requireFamilyAccess(familyId)` before accessing family data
- Prevents cross-family data access
- Critical for maintaining data privacy

### Example
```typescript
export async function getFamilyData(familyId: string) {
  await requireFamilyAccess(familyId); // Throws if user doesn't belong to family
  // User guaranteed to have access here
  return fetchData(familyId);
}
```

## Role-Based Access Control

### Admin vs Member
- First user in family is automatically 'admin'
- Additional users are 'member' by default
- Use `requireAdminRedirect()` for admin-only pages
- Use `requireAdmin()` for admin-only Server Actions

### Pattern
```typescript
export async function AdminPage() {
  await requireAdminRedirect(); // Redirects non-admins
  // User guaranteed to be admin
  return <AdminPanel />;
}
```

## Migration Notes

### From AWS Amplify
- Removed all Amplify client-side initialization
- Replaced with Supabase SSR (server-side) auth
- httpOnly cookies instead of localStorage tokens
- More secure: tokens never exposed to JavaScript

### Key Changes
- No client-side auth initialization needed
- All auth checks happen server-side
- Middleware handles token refresh automatically
- Server Components can directly access auth state
