
# InsForge + WorkOS Integration Guide

WorkOS AuthKit handles authentication via middleware. On the server, `withAuth()` retrieves the authenticated user, and a JWT is signed with InsForge's secret containing the user's ID. The token is passed to InsForge as `accessToken` (deprecated alias: `edgeFunctionToken`).

## Key packages

- `@workos-inc/authkit-nextjs` — WorkOS AuthKit for Next.js
- `@insforge/sdk` — InsForge client
- `jsonwebtoken` + `@types/jsonwebtoken` — for server-side JWT signing

## Recommended Workflow

```text
1. Create WorkOS application       → WorkOS Dashboard (manual)
2. Configure JWT template          → WorkOS Dashboard (manual)
3. Create/link InsForge project    → npx -y @insforge/cli create or link
4. Install deps + configure env    → npm install, .env.local
5. Set up callback + login routes  → app/callback/route.ts, app/login/route.ts
6. Set up middleware + layout      → middleware.ts, app/layout.tsx
7. Create InsForge client utility  → lib/insforge.ts (server-side JWT signing)
8. Set up InsForge database        → requesting_user_id() + table + RLS
9. Build features                  → CRUD pages using InsForge client
```

## Dashboard setup (manual, cannot be automated)

### WorkOS Application
- Note down **API Key** and **Client ID** from WorkOS Dashboard > API Keys
- Add `http://localhost:3000/callback` under Redirects
- Enable desired auth methods (email/password, social login, SSO, etc.)

### WorkOS JWT Template
- In WorkOS Dashboard > Authentication > Sessions > Configure JWT Template
- Claims: `role: "authenticated"`, `aud: "insforge-api"`, `user_email: {{ user.email }}`
- `sub` is reserved — auto-included, do not add manually

### InsForge Project
- Create via `npx -y @insforge/cli create` or link via `npx -y @insforge/cli link --project-id <id>`
- Get the JWT secret via CLI: `npx -y @insforge/cli secrets get JWT_SECRET`
- Note down **URL** and **Anon Key** from InsForge, then export the CLI value as `INSFORGE_JWT_SECRET`

## App structure

- **Callback route**: `app/callback/route.ts` — export `handleAuth()` from `@workos-inc/authkit-nextjs`
- **Layout**: wrap with `AuthKitProvider` from `@workos-inc/authkit-nextjs/components` in `app/layout.tsx`
- **Middleware**: `middleware.ts` — export `authkitMiddleware()`, match `['/', '/api/:path*']`
- **Login route**: `app/login/route.ts` — get sign-in URL via `getSignInUrl()` and `redirect()`

**Next.js 16 limitation**: `withAuth({ ensureSignedIn: true })` can cause **cookie errors** in server components. Use `redirect('/login')` in the page instead.

```typescript
// app/callback/route.ts
import { handleAuth } from '@workos-inc/authkit-nextjs';
export const GET = handleAuth();
```

```typescript
// middleware.ts
import { authkitMiddleware } from '@workos-inc/authkit-nextjs';
export default authkitMiddleware();
export const config = { matcher: ['/', '/api/:path*'] };
```

```typescript
// app/login/route.ts
import { getSignInUrl } from '@workos-inc/authkit-nextjs';
import { redirect } from 'next/navigation';
export async function GET() {
  const signInUrl = await getSignInUrl();
  redirect(signInUrl);
}
```

## InsForge client

- Create a server-side utility at `lib/insforge.ts`
- Use `withAuth()` to get the WorkOS user
- Sign a JWT with `jsonwebtoken` using `INSFORGE_JWT_SECRET`
- Required claims: `sub` (from `user.id`), `role: "authenticated"`, `aud: "insforge-api"`
- Set expiration to 1 hour
- Pass the signed token as `accessToken` to `createClient`

```typescript
// lib/insforge.ts
import { createClient } from '@insforge/sdk';
import { withAuth } from '@workos-inc/authkit-nextjs';
import jwt from 'jsonwebtoken';

export async function createInsForgeClient() {
  const { user } = await withAuth();
  if (!user) return null;

  const insforgeToken = jwt.sign(
    {
      sub: user.id,
      role: 'authenticated',
      aud: 'insforge-api',
      exp: Math.floor(Date.now() / 1000) + 60 * 60,
    },
    process.env.INSFORGE_JWT_SECRET!
  );

  return createClient({
    baseUrl: process.env.NEXT_PUBLIC_INSFORGE_URL!,
    accessToken: insforgeToken,
  });
}
```

## Database setup

- WorkOS user IDs are strings (e.g. `user_01H...`), not UUIDs — use `TEXT` columns for `user_id`
- Create a `requesting_user_id()` SQL function that extracts the `sub` claim from `auth.jwt()` as text
- Set `user_id` column default to `requesting_user_id()` so it auto-populates on insert
- Enable RLS and create policies that compare `user_id = requesting_user_id()`

```sql
create or replace function public.requesting_user_id()
returns text
language sql stable
as $$
  select nullif(auth.jwt() ->> 'sub', '')::text
$$;
```

## Environment variables

| Variable | Source |
|----------|--------|
| `WORKOS_API_KEY` | WorkOS Dashboard |
| `WORKOS_CLIENT_ID` | WorkOS Dashboard |
| `WORKOS_COOKIE_PASSWORD` | Generate with `openssl rand -hex 32` |
| `NEXT_PUBLIC_WORKOS_REDIRECT_URI` | `http://localhost:3000/callback` |
| `NEXT_PUBLIC_INSFORGE_URL` | InsForge Dashboard |
| `NEXT_PUBLIC_INSFORGE_ANON_KEY` | InsForge Dashboard |
| `INSFORGE_JWT_SECRET` | InsForge CLI (`npx -y @insforge/cli secrets get JWT_SECRET`) |

## Common Mistakes

| Mistake | Solution |
|---------|----------|
| ❌ Using `withAuth({ ensureSignedIn: true })` in server components | ✅ Causes cookie errors on Next.js 16 — use `redirect('/login')` instead |
| ❌ Forgetting `WORKOS_COOKIE_PASSWORD` | ✅ Session encryption fails silently without it |
| ❌ Using `auth.uid()` for RLS policies | ✅ Use `requesting_user_id()` — WorkOS IDs are strings, not UUIDs |
