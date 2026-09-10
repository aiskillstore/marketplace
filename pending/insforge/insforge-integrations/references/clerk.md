
# InsForge + Clerk Integration Guide (Next.js)

Clerk signs tokens with InsForge's JWT secret directly via a **JWT Template** — no server-side signing needed. The app calls `getToken({ template: 'insforge' })` and forwards the token to the InsForge client via `client.setAccessToken()`.

This guide targets **Next.js (App Router)**. The same pattern works in other React setups, but all examples and env vars assume Next.js.

## Key packages

- `@clerk/nextjs` — Clerk SDK for Next.js (includes `clerkMiddleware`, `ClerkProvider`, hooks, and prebuilt `<SignIn>` / `<SignUp>` components)
- `@insforge/sdk` — InsForge client

## Recommended Workflow

```text
1. Create Clerk application        → Clerk Dashboard (manual)
2. Create/link InsForge project    → npx -y @insforge/cli create or link
3. Create JWT template in Clerk    → Clerk Dashboard (manual)
4. Install deps + configure env    → npm install, .env.local
5. Wire ClerkProvider + middleware → app/layout.tsx + middleware.ts
6. Initialize InsForge client      → createClient + setAccessToken with Clerk token (refresh on interval)
7. Set up InsForge database        → requesting_user_id() + table + RLS
8. Build features                  → CRUD pages using InsForge client
```

## Dashboard setup (manual, cannot be automated)

### Clerk Application
- Create an application in Clerk Dashboard
- Note down **Publishable Key** and **Secret Key**

### Clerk JWT Template
- Create in Clerk Dashboard > Configure > JWT Templates > New template > Blank
- Name: `insforge`
- Signing algorithm: `HS256`
- Signing key: the InsForge JWT Secret
- Claims: `{ "role": "authenticated", "aud": "insforge-api" }`
- Do NOT add `sub` or `iss` — they are reserved and auto-included

### InsForge Project
- Create via `npx -y @insforge/cli create` or link via `npx -y @insforge/cli link --project-id <id>`
- Get the JWT secret via CLI: `npx -y @insforge/cli secrets get JWT_SECRET`
- Note down **URL** and **Anon Key** from InsForge, then use the CLI output as the signing key in Clerk

## Next.js wiring

### `middleware.ts` (project root)

```ts
import { clerkMiddleware } from '@clerk/nextjs/server';

export default clerkMiddleware();

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
};
```

### `app/layout.tsx`

Wrap the app in `<ClerkProvider>` (it's a server component — no `'use client'` needed).

```tsx
import { ClerkProvider } from '@clerk/nextjs';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

### Sign-in / sign-up routes

Use Clerk's optional catch-all routes so Clerk's internal redirects work:

```text
app/sign-in/[[...sign-in]]/page.tsx
app/sign-up/[[...sign-up]]/page.tsx
```

```tsx
// app/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from '@clerk/nextjs';

export default function Page() {
  return <SignIn path="/sign-in" signUpUrl="/sign-up" forceRedirectUrl="/" />;
}
```

## InsForge client

- Create the client once with `createClient({ baseUrl, anonKey })`
- Use Clerk's `useAuth()` to get `getToken`
- In a `useEffect` keyed on `isSignedIn` and Clerk `userId`, call `getToken({ template: 'insforge' })` and pipe the result into `client.setAccessToken(token, event)` (see the next bullet for choosing `event`)
- Clerk JWT templates default to **60-second expiry** — refresh the token on a ~50-second interval while the user is signed in; clear the token on sign-out
- For the initial token or a changed Clerk user, use the default `SIGNED_IN` behavior; for periodic same-user token rotation, pass `AuthChangeEvent.TOKEN_REFRESHED` so Realtime keeps the existing socket and uses the fresh JWT on the next handshake
- The template name `'insforge'` must match the Clerk dashboard exactly
- `@insforge/sdk`'s `accessToken` config field (deprecated alias: `edgeFunctionToken`) is a **static string**, not a function — it cannot auto-refresh on its own, which is why we use `client.setAccessToken()` imperatively
- This hook uses Clerk hooks, so the file must start with `'use client'`

```tsx
// lib/insforge.ts
'use client';

import { AuthChangeEvent, createClient, type InsForgeClient } from '@insforge/sdk';
import { useAuth } from '@clerk/nextjs';
import { useEffect, useMemo, useRef, useState } from 'react';

const TOKEN_REFRESH_MS = 50_000; // Clerk template tokens expire in 60s by default

export function useInsforgeClient(): { client: InsForgeClient; isReady: boolean } {
  const { getToken, isSignedIn, userId } = useAuth();
  const [isReady, setIsReady] = useState(false);
  const currentUserIdRef = useRef<string | null>(null);

  const client = useMemo(
    () =>
      createClient({
        baseUrl: process.env.NEXT_PUBLIC_INSFORGE_BASE_URL!,
        anonKey: process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY!,
      }),
    [],
  );

  useEffect(() => {
    if (!isSignedIn || !userId) {
      client.setAccessToken(null);
      currentUserIdRef.current = null;
      setIsReady(false);
      return;
    }

    // User switched (A → B) without signing out first: drop the previous user's
    // token and mark not-ready before the async fetch, so no request goes out
    // authenticated as the old user while the new token is in flight.
    if (currentUserIdRef.current !== null && currentUserIdRef.current !== userId) {
      client.setAccessToken(null);
      setIsReady(false);
    }

    let cancelled = false;
    const refresh = async () => {
      try {
        const token = await getToken({ template: 'insforge' });
        if (cancelled) return;
        if (!token) {
          client.setAccessToken(null);
          currentUserIdRef.current = null;
          setIsReady(false);
          return;
        }
        const event =
          currentUserIdRef.current === userId
            ? AuthChangeEvent.TOKEN_REFRESHED
            : AuthChangeEvent.SIGNED_IN;
        client.setAccessToken(token, event);
        currentUserIdRef.current = userId;
        setIsReady(true);
      } catch (err) {
        if (cancelled) return;
        client.setAccessToken(null);
        currentUserIdRef.current = null;
        setIsReady(false);
        console.error('Failed to refresh Clerk token for InsForge client', err);
      }
    };

    void refresh();
    const id = setInterval(() => void refresh(), TOKEN_REFRESH_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [client, getToken, isSignedIn, userId]);

  return { client, isReady };
}
```

> **SDK version note.** The two-arg `client.setAccessToken(token, event)` and the `AuthChangeEvent` import require SDK **≥ 1.4.4**. On SDK **1.3.x**, drop the second argument (and the `AuthChangeEvent` import) and call `client.setAccessToken(token)` — it still updates both HTTP and realtime auth, but a same-user refresh may reconnect the socket. On SDK **< 1.3.0** the public method doesn't exist; use the `setBridgeToken` legacy fallback shown in the Better Auth reference.

## Database setup

- Clerk user IDs are strings (e.g. `user_2xPnG8KxVQr`), not UUIDs — use `TEXT` columns for `user_id`
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

| Variable | Source | Notes |
|----------|--------|-------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk Dashboard | Exposed to the browser |
| `CLERK_SECRET_KEY` | Clerk Dashboard | Server-only; required by `clerkMiddleware()` |
| `NEXT_PUBLIC_INSFORGE_BASE_URL` | InsForge Dashboard | Exposed to the browser |
| `NEXT_PUBLIC_INSFORGE_ANON_KEY` | InsForge Dashboard | Exposed to the browser |

## Common Mistakes

| Mistake | Solution |
|---------|----------|
| ❌ Passing an async function as `accessToken` | ✅ SDK accepts only a static string there — use `client.setAccessToken()` instead |
| ❌ Setting the token only once on mount | ✅ Refresh on a ~50s interval — Clerk JWT templates expire in 60s by default |
| ❌ Adding `sub` or `iss` to the JWT template | ✅ These are reserved claims, auto-included by Clerk |
| ❌ Using `auth.uid()` for RLS policies | ✅ Use `requesting_user_id()` — Clerk IDs are strings, not UUIDs |
| ❌ Omitting `CLERK_SECRET_KEY` in `.env.local` | ✅ `clerkMiddleware()` reads it at runtime — add it alongside the publishable key |
| ❌ Forgetting `'use client'` on `lib/insforge.ts` | ✅ The hook uses React + Clerk hooks; the file must be a client module |
