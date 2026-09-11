
# InsForge + Auth0 Integration Guide

Auth0 signs an InsForge-compatible JWT inside a **Post Login Action**, embeds it as a custom claim on the ID token, and the Next.js app extracts it to pass to the InsForge client as `accessToken` (deprecated alias: `edgeFunctionToken`). InsForge validates the token and uses the `sub` claim for Row Level Security.

## Key packages

- `@auth0/nextjs-auth0` — Auth0 SDK for Next.js (use v4+)
- `@insforge/sdk` — InsForge client

## Recommended Workflow

```text
1. Create Auth0 application       → Auth0 Dashboard (manual)
2. Create/link InsForge project   → npx -y @insforge/cli create or link
3. Create Post Login Action       → Auth0 Dashboard (manual, paste code below)
4. Install deps + configure env   → npm install, .env.local
5. Set up Auth0 client            → lib/auth0.ts with beforeSessionSaved
6. Set up middleware + layout      → middleware.ts, app/layout.tsx
7. Create InsForge client utility → lib/insforge.ts
8. Set up InsForge database        → requesting_user_id() + table + RLS
9. Build features                  → CRUD pages using InsForge client
```

## Dashboard setup (manual, cannot be automated)

### Auth0 Application
- Create a **Regular Web Application** in Auth0 Dashboard > Applications
- Set **Allowed Callback URLs** to `http://localhost:3000/auth/callback`
- Set **Allowed Logout URLs** to `http://localhost:3000`
- Note down **Domain**, **Client ID**, **Client Secret**

### Auth0 Post Login Action
- Create in Auth0 Dashboard > Actions > Library > Build Custom
- Name: `Generate InsForge Token`, trigger: **Post Login**
- Add `jsonwebtoken` as a dependency in the action editor
- Add `INSFORGE_JWT_SECRET` in the action's **Secrets** tab
- Deploy the action and drag it into the **post-login** trigger flow

### InsForge Project
- Create via `npx -y @insforge/cli create` or link via `npx -y @insforge/cli link --project-id <id>`
- Get the JWT secret via CLI: `npx -y @insforge/cli secrets get JWT_SECRET`
- Note down **URL** and **Anon Key** from InsForge, then store the CLI value in Auth0 as `INSFORGE_JWT_SECRET`

## Auth0 Post Login Action

This code runs in Auth0's environment (not your app). The action must sign a JWT with the InsForge secret and attach it as a namespaced custom claim on the ID token.

```javascript
const jwt = require('jsonwebtoken');

exports.onExecutePostLogin = async (event, api) => {
  const insforgeToken = jwt.sign(
    {
      sub: event.user.user_id,
      role: 'authenticated',
      aud: 'insforge-api',
      email: event.user.email,
    },
    event.secrets.INSFORGE_JWT_SECRET,
    { expiresIn: '1h' }
  );

  api.idToken.setCustomClaim('https://insforge.dev/insforge_token', insforgeToken);
};
```

## Auth0 v4 SDK — `beforeSessionSaved`

Auth0 v4 SDK **filters out custom claims** from the ID token by default. You **must** configure `beforeSessionSaved` on `Auth0Client` to extract the InsForge token into the session. Without this, `getSession().user` will not contain the token.

**The `idToken` parameter is a raw JWT string**, not a decoded object — you must split and base64url-decode it:

```typescript
// lib/auth0.ts
beforeSessionSaved: async (session, idToken) => {
  if (idToken) {
    const parts = idToken.split(".");
    const payload = JSON.parse(Buffer.from(parts[1], "base64url").toString());
    const insforgeToken = payload["https://insforge.dev/insforge_token"];
    if (insforgeToken) {
      (session.user ??= {})["https://insforge.dev/insforge_token"] = insforgeToken;
    }
  }
  return session;
}
```

## Middleware

- Auth0 v4 uses `auth0.middleware()` exported directly from `middleware.ts` as `export const middleware = auth0.middleware()`
- No `app/api/auth/[auth0]/route.js` needed in v4
- Match paths: `/auth/:path*` and any protected routes

```typescript
// middleware.ts
import { auth0 } from "@/lib/auth0";

export const middleware = auth0.middleware();

export const config = {
  matcher: ["/auth/:path*", "/protected/:path*"],
};
```

## Layout

- Wrap the app with `Auth0Provider` from `@auth0/nextjs-auth0/client` in `app/layout.tsx`

```typescript
import { Auth0Provider } from '@auth0/nextjs-auth0/client';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Auth0Provider>{children}</Auth0Provider>
      </body>
    </html>
  );
}
```

## InsForge client

- Create a utility at `lib/insforge.ts` that calls `auth0.getSession()`, reads the token from `session.user["https://insforge.dev/insforge_token"]`, and passes it as `accessToken` to `createClient`

```typescript
// lib/insforge.ts
import { createClient } from '@insforge/sdk';
import { auth0 } from '@/lib/auth0';

export async function createInsForgeClient() {
  const session = await auth0.getSession();
  const insforgeToken = session?.user?.["https://insforge.dev/insforge_token"];

  return createClient({
    baseUrl: process.env.NEXT_PUBLIC_INSFORGE_URL,
    accessToken: insforgeToken,
  });
}
```

## Database setup

- Auth0 user IDs are strings (e.g. `auth0|64a...`), not UUIDs — use `TEXT` columns for `user_id`
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
| `AUTH0_SECRET` | Generate with `openssl rand -hex 32` |
| `APP_BASE_URL` | `http://localhost:3000` |
| `AUTH0_DOMAIN` | Auth0 Dashboard |
| `AUTH0_CLIENT_ID` | Auth0 Dashboard |
| `AUTH0_CLIENT_SECRET` | Auth0 Dashboard |
| `NEXT_PUBLIC_INSFORGE_URL` | InsForge Dashboard |
| `NEXT_PUBLIC_INSFORGE_ANON_KEY` | InsForge Dashboard |
| `INSFORGE_JWT_SECRET` | InsForge CLI (`npx -y @insforge/cli secrets get JWT_SECRET`) |

## Common Mistakes

| Mistake | Solution |
|---------|----------|
| ❌ Forgetting `beforeSessionSaved` | ✅ Always configure it — without it the InsForge token is silently dropped |
| ❌ Treating `idToken` as a decoded object | ✅ It's a raw JWT string — split and base64url-decode the payload |
| ❌ Using `auth.uid()` for RLS policies | ✅ Use `requesting_user_id()` — Auth0 IDs are strings, not UUIDs |
| ❌ Creating `app/api/auth/[auth0]/route.js` | ✅ Not needed in v4 — `auth0.middleware()` handles it |
