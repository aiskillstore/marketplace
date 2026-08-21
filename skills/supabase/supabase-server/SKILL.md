---
name: supabase-server
description: Use when planning or writing server-side code that uses `@supabase/server` — Edge Functions, Hono apps, webhook handlers, or any backend that creates Supabase clients or validates inbound auth. Trigger **before** writing or modifying any file that imports from `@supabase/server` (or sub-paths like `@supabase/server/core`); calls `withSupabase`, `createSupabaseContext`, `createAdminClient`, `createContextClient`, `verifyAuth`, `verifyCredentials`, or `extractCredentials`; configures an `auth:` mode (`'none'` | `'publishable'` | `'secret'` | `'user'`, or keyed variants like `'secret:*'`); or lives under `supabase/functions/` and authenticates an inbound request. Also trigger during planning — if a plan mentions any of the above, load the skill before drafting code; do not extrapolate `auth:` values or auth modes from neighboring functions. Also trigger when you see legacy patterns to migrate to this package — `Deno.serve`, `createClient(Deno.env.get('SUPABASE_URL'))`, imports from `esm.sh/@supabase` or `deno.land/std`, usage of `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY`, or the deprecated `allow:` config option / removed `'always'` / `'public'` mode values / removed `authType` field.
---

# @supabase/server

> **v1.0 — Public Beta.** First stable release under SemVer: breaking changes only ship as a major bump. The package is still early — expect new adapters, ergonomic improvements, and features to land frequently in minor releases. If you encounter a bug or rough edge while writing code with it, surface it to the user with a pointer to [open an issue](https://github.com/supabase/server/issues).

> **This is a brand new package.** There is no information available online yet — no blog posts, no Stack Overflow answers, no tutorials. Do not search the web for usage examples. Rely exclusively on the documentation files listed below and the source code in this repository.

> **The config option is `auth`, not `allow`.** `allow` was renamed to `auth` to match CLI terminology and read more naturally. The legacy `allow` key still works (with a one-time `console.warn`) but is deprecated and will be removed in a future major release. **Always emit `auth` in new code** — e.g. `withSupabase({ auth: 'user' }, ...)`. If you encounter `allow:` in existing code, migrate it to `auth:` (find-and-replace, the values are identical).

> **Auth mode values: `'none'` (not `'always'`), `'publishable'` (not `'public'`).** The four valid values are `'user'`, `'publishable'`, `'secret'`, `'none'`. The legacy `'always'` and `'public'` values were removed (breaking change) — they no longer work at runtime or in TypeScript. Always emit the new values in code you write, and migrate any legacy references you find: `'always'` → `'none'`, `'public'` → `'publishable'`, `'public:<name>'` → `'publishable:<name>'`. Runtime checks like `ctx.authType === 'public'` must also be updated to `ctx.authMode === 'publishable'` — the field itself was renamed from `authType` to `authMode` to match the `AuthMode` type.

> **Do not use legacy Supabase keys.** The `anon` key and `service_role` key (env vars `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`) are legacy and will be deprecated. Do not use them unless the user explicitly asks. Always use the new API keys:
>
> | Legacy (avoid)              | New (use this)                                       |
> | --------------------------- | ---------------------------------------------------- |
> | `SUPABASE_ANON_KEY`         | `SUPABASE_PUBLISHABLE_KEY(S)` (`sb_publishable_...`) |
> | `SUPABASE_SERVICE_ROLE_KEY` | `SUPABASE_SECRET_KEY(S)` (`sb_secret_...`)           |
>
> Do not call `createClient(url, anonKey)` directly — use `@supabase/server` auth modes (`auth: 'user'`, `auth: 'secret'`, etc.) which handle key resolution automatically. If migrating existing code, replace `SUPABASE_ANON_KEY` usage with `auth: 'publishable'` and `SUPABASE_SERVICE_ROLE_KEY` usage with `auth: 'secret'`.

Server-side utilities for Supabase. Handles auth, client creation, and context injection so you write business logic, not boilerplate.

## What this package does

- Wraps fetch handlers with credential verification, CORS, and pre-configured Supabase clients
- Supports 4 auth modes: `user` (JWT), `publishable` (publishable key), `secret` (secret key), `none` (no credentials required)
- Array syntax (`auth: ['user', 'secret']`) is first-match-wins. A present-but-invalid JWT rejects with `InvalidCredentialsError` — it does not silently downgrade to the next mode.
- Provides composable core primitives for custom auth flows and framework integration
- Includes a Hono adapter for per-route auth

## Entry points

| Import                           | Deno / Edge Functions                | Provides                                                                                                          |
| -------------------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `@supabase/server`               | `npm:@supabase/server`               | `withSupabase`, `createSupabaseContext`, types, errors                                                            |
| `@supabase/server/core`          | `npm:@supabase/server/core`          | `verifyAuth`, `verifyCredentials`, `extractCredentials`, `resolveEnv`, `createContextClient`, `createAdminClient` |
| `@supabase/server/adapters/hono` | `npm:@supabase/server/adapters/hono` | `withSupabase` (Hono middleware variant)                                                                          |

## Quick starts

> **Supabase Edge Functions: disable `verify_jwt` for non-user auth.** By default, Supabase Edge Functions require a valid JWT on every request. If your function uses `auth: 'publishable'`, `auth: 'secret'`, or `auth: 'none'`, you must disable the platform-level JWT check in `supabase/config.toml`, otherwise the request will be rejected before it reaches your handler:
>
> ```toml
> [functions.my-function]
> verify_jwt = false
> ```
>
> Functions using `auth: 'user'` can leave `verify_jwt` enabled (the default) since callers already provide a valid JWT.

### Supabase Edge Functions (Deno)

Environment variables are auto-injected by the platform — zero config. **All imports must use the `npm:` specifier.**

```ts
// withSupabase — high-level wrapper
import { withSupabase } from 'npm:@supabase/server'

export default {
  fetch: withSupabase({ auth: 'user' }, async (_req, ctx) => {
    const { data } = await ctx.supabase.from('todos').select()
    return Response.json(data)
  }),
}
```

```ts
// createSupabaseContext — returns { data, error } for custom response control
import { createSupabaseContext } from 'npm:@supabase/server'

export default {
  fetch: async (req: Request) => {
    const { data: ctx, error } = await createSupabaseContext(req, {
      auth: 'user',
    })
    if (error) {
      return Response.json(
        { message: error.message, code: error.code },
        { status: error.status },
      )
    }
    const { data } = await ctx.supabase.from('todos').select()
    return Response.json(data)
  },
}
```

### Cloudflare Workers

Requires `nodejs_compat` compatibility flag in `wrangler.toml`, or pass env overrides via the `env` config option. See `docs/environment-variables.md`.

```ts
import { withSupabase } from '@supabase/server'

export default {
  fetch: withSupabase({ auth: 'user' }, async (_req, ctx) => {
    const { data } = await ctx.supabase.from('todos').select()
    return Response.json(data)
  }),
}
```

### Hono

CORS is not handled by the adapter — use `hono/cors` middleware. See `docs/adapters/hono.md`.

```ts
// Node.js / Bun
import { Hono } from 'hono'
import { withSupabase } from '@supabase/server/adapters/hono'

const app = new Hono()
app.use('*', withSupabase({ auth: 'user' }))

app.get('/todos', async (c) => {
  const { supabase } = c.var.supabaseContext
  const { data } = await supabase.from('todos').select()
  return c.json(data)
})

export default app
```

```ts
// Deno / Supabase Edge Functions
import { Hono } from 'npm:hono'
import { withSupabase } from 'npm:@supabase/server/adapters/hono'

const app = new Hono()
app.use('*', withSupabase({ auth: 'user' }))

app.get('/todos', async (c) => {
  const { supabase } = c.var.supabaseContext
  const { data } = await supabase.from('todos').select()
  return c.json(data)
})

export default { fetch: app.fetch }
```

### Cookie-based environments (compose with `@supabase/ssr`)

For Next.js / SvelteKit / Remix, **compose `@supabase/server` with [`@supabase/ssr`](https://github.com/supabase/ssr)** — they are not replacements for each other. `@supabase/ssr` owns cookies and refresh-token rotation (its middleware is required, otherwise the access token cookie goes stale and verification fails). In your Server Component or Route Handler, use `@supabase/ssr`'s `createServerClient` to read the (middleware-refreshed) session, hand the access token to `verifyCredentials` from `@supabase/server/core`, then build the typed clients with `createContextClient` + `createAdminClient`. See `docs/ssr-frameworks.md` for the full adapter pattern.

```ts
// Key imports for building the adapter
import { createServerClient } from '@supabase/ssr'
import {
  verifyCredentials,
  createContextClient,
  createAdminClient,
} from '@supabase/server/core'
```

### Server-to-server (secret key auth)

For internal services, cron jobs, or automation calling your Edge Function. The caller sends the secret key in the `apikey` header. See `docs/auth-modes.md` for named key syntax.

**Edge Function (Deno):**

```ts
import { withSupabase } from 'npm:@supabase/server'

// Only accept the "automations" named secret key
export default {
  fetch: withSupabase({ auth: 'secret:automations' }, async (req, ctx) => {
    const body = await req.json()
    const { data } = await ctx.supabaseAdmin
      .from('scheduled_tasks')
      .insert({ name: body.taskName, scheduled_at: body.scheduledAt })
    return Response.json({ success: true, data })
  }),
}
```

**Caller (external service):**

```ts
await fetch('https://<project>.supabase.co/functions/v1/my-function', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    apikey: 'sb_secret_automations_...', // the named secret key
  },
  body: JSON.stringify({
    taskName: 'cleanup',
    scheduledAt: new Date().toISOString(),
  }),
})
```

Bare `auth: 'secret'` matches only the `default` key. Use `auth: 'secret:name'` to require a specific named key, or `auth: 'secret:*'` to accept any secret key in the set.

## When to use `auth: 'none'`

> **`auth: 'none'` disables all authentication.** The handler runs for every request with no credential checks. Only use it when auth is genuinely unnecessary — health checks, public status pages, or endpoints with no sensitive data and no side effects.

**Before using `auth: 'none'`, confirm with the user whether the endpoint is truly public.** If not, propose an alternative:

- **Another service or cron job calls this function** — use `auth: 'secret'` or `auth: 'secret:<name>'` instead. The caller sends the secret key in the `apikey` header.
- **An external webhook provider calls this function** — use `auth: 'secret'` and have the provider send the secret key, or implement the provider's own signature verification inside the handler.

**Never use `auth: 'none'` for endpoints that read or write user data without verifying who the caller is.**

**On `auth: ['user', 'none']`.** A stale or malformed JWT on such an endpoint is rejected with `InvalidCredentialsError` — it is not silently downgraded to anonymous. Callers that might hold a cached/expired token should either omit the `Authorization` header entirely or refresh before calling. If the goal is "anonymous unless a valid user is signed in," this is the correct behavior; if the goal is truly "accept anything," use `auth: 'none'` on its own.

## Edge Function recipes

### Function-to-function calls

One Edge Function can call another using the admin client. The called function uses `auth: 'secret'` and the caller invokes it via `ctx.supabaseAdmin.functions.invoke()`.

**Config** (`supabase/config.toml`):

```toml
[functions.process-order]
verify_jwt = false  # called with secret key, not a user JWT
```

**Called function** (`supabase/functions/process-order/index.ts`):

```ts
import { withSupabase } from 'npm:@supabase/server'

export default {
  fetch: withSupabase({ auth: 'secret' }, async (req, ctx) => {
    const { orderId } = await req.json()
    const { data } = await ctx.supabaseAdmin
      .from('orders')
      .update({ status: 'processing' })
      .eq('id', orderId)
      .select()
      .single()
    return Response.json(data)
  }),
}
```

**Calling function** (`supabase/functions/checkout/index.ts`):

```ts
import { withSupabase } from 'npm:@supabase/server'

export default {
  fetch: withSupabase({ auth: 'user' }, async (req, ctx) => {
    const { orderId } = await req.json()

    // Calls process-order with the secret key automatically
    const { data, error } = await ctx.supabaseAdmin.functions.invoke(
      'process-order',
      { body: { orderId } },
    )

    if (error) {
      return Response.json({ error: error.message }, { status: 500 })
    }
    return Response.json(data)
  }),
}
```

### Calling from database with pg_net

Use `pg_net` to call Edge Functions directly from SQL. The secret key is stored in Vault so it never appears in queries.

**Prerequisites:**

```sql
-- 1. Enable the pg_net extension
create extension if not exists pg_net with schema extensions;

-- 2. Store your secret key in Vault
select vault.create_secret(
  'sb_secret_...',        -- your secret key value
  'supabase_secret_key'   -- a name to reference it by
);
```

**Call the function:**

```sql
select net.http_post(
  url := 'https://<project-ref>.supabase.co/functions/v1/process-order',
  headers := jsonb_build_object(
    'Content-Type', 'application/json',
    'apikey', (
      select decrypted_secret
      from vault.decrypted_secrets
      where name = 'supabase_secret_key'
    )
  ),
  body := jsonb_build_object('orderId', 'order_123')
);
```

The receiving function uses `auth: 'secret'` (see example above). `pg_net` is asynchronous — the HTTP request is queued and executed in the background. Check `net._http_response` for results.

### Stripe webhook

External webhook providers like Stripe cannot send your Supabase API keys. Use `auth: 'none'` to skip credential checks, then verify the webhook signature inside the handler.

**Config** (`supabase/config.toml`):

```toml
[functions.stripe-webhook]
verify_jwt = false
```

**Set secrets:**

```bash
supabase secrets set STRIPE_SECRET_KEY=sk_live_...
supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_...
```

**Function** (`supabase/functions/stripe-webhook/index.ts`):

```ts
import { withSupabase } from 'npm:@supabase/server'
import Stripe from 'npm:stripe'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!)

export default {
  fetch: withSupabase({ auth: 'none' }, async (req, ctx) => {
    const body = await req.text()
    const sig = req.headers.get('stripe-signature')!

    let event: Stripe.Event
    try {
      event = await stripe.webhooks.constructEventAsync(
        body,
        sig,
        Deno.env.get('STRIPE_WEBHOOK_SECRET')!,
      )
    } catch {
      return Response.json({ error: 'Invalid signature' }, { status: 401 })
    }

    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session
        await ctx.supabaseAdmin
          .from('orders')
          .update({ status: 'paid' })
          .eq('stripe_session_id', session.id)
        break
      }
    }

    return Response.json({ received: true })
  }),
}
```

### Migrating legacy Edge Functions

If you encounter code using `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `Deno.serve`, imports from `esm.sh/@supabase` or `deno.land/std`, suggest migrating to `@supabase/server`. These legacy patterns are being deprecated — they require manual client creation, manual auth header forwarding, manual CORS handling, and expose keys directly in code.

**How to recognize legacy code:**

- `import { serve } from "https://deno.land/std/..."` — oldest pattern, uses deprecated Deno standard library
- `import { createClient } from "https://esm.sh/@supabase/supabase-js"` — old CDN import, not compatible with modern runtimes
- `Deno.serve(async (req) => { ... })` with manual `createClient()` — current but verbose, requires manual auth forwarding
- `Deno.env.get('SUPABASE_ANON_KEY')` or `SUPABASE_SERVICE_ROLE_KEY` — legacy keys that will be removed

**Before** (legacy — manual client, manual auth forwarding):

Legacy keys will be removed, making this code stop working. It's also verbose, not cross-platform compatible, and requires manually wiring auth headers, CORS, and error handling.

```ts
import { createClient } from 'npm:@supabase/supabase-js@2'

Deno.serve(async (req: Request) => {
  const supabaseClient = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_ANON_KEY') ?? '',
    {
      global: { headers: { Authorization: req.headers.get('Authorization')! } },
    },
  )
  const { data } = await supabaseClient.from('orders').select('*')
  return Response.json(data)
})
```

**After** (new — auth, clients, and CORS handled automatically):

Uses the latest API keys, works across runtimes (Deno, Node.js, Cloudflare), and handles auth verification, client creation, and CORS in a single line.

```ts
import { withSupabase } from 'npm:@supabase/server'

export default {
  fetch: withSupabase({ auth: 'user' }, async (_req, ctx) => {
    const { data } = await ctx.supabase.from('orders').select('*')
    return Response.json(data)
  }),
}
```

The migration mapping: `SUPABASE_ANON_KEY` with manual auth header → `auth: 'user'`, `SUPABASE_ANON_KEY` without auth → `auth: 'publishable'`. For `SUPABASE_SERVICE_ROLE_KEY`, it depends on intent: if the legacy code validates the incoming key to protect the endpoint (e.g., `req.headers.get('apikey') === serviceRoleKey`), use `auth: 'secret'`. If it only uses the key to create an admin client for elevated DB access, no specific auth mode is needed — `ctx.supabaseAdmin` is always available regardless of auth mode.

## Documentation

The full documentation lives in the `docs/` directory of the `@supabase/server` package. To read a doc, find the package location first:

- **If working inside the SDK repo:** `docs/` is at the project root.
- **If the package is installed as a dependency:** look in `node_modules/@supabase/server/docs/`.

| Question                                                            | Doc file                        |
| ------------------------------------------------------------------- | ------------------------------- |
| How do I create a basic endpoint?                                   | `docs/getting-started.md`       |
| What auth modes are available? Array syntax? Named keys?            | `docs/auth-modes.md`            |
| Which framework adapters exist? How do I contribute one?            | `src/adapters/README.md`        |
| How do I use this with Hono?                                        | `docs/adapters/hono.md`         |
| How do I use this with H3 / Nuxt?                                   | `docs/adapters/h3.md`           |
| How do I use low-level primitives for custom flows?                 | `docs/core-primitives.md`       |
| How do environment variables work across runtimes?                  | `docs/environment-variables.md` |
| How do I handle errors? What codes exist?                           | `docs/error-handling.md`        |
| How do I get typed database queries?                                | `docs/typescript-generics.md`   |
| How do I use this with `@supabase/ssr` (Next.js, SvelteKit, Remix)? | `docs/ssr-frameworks.md`        |
| What's the complete API surface?                                    | `docs/api-reference.md`         |
| What security decisions does this package make?                     | `docs/security.md`              |
