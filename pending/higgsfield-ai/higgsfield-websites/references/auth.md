# Skill: Auth Boundary

Use this when a website needs signed-in user state, login, logout, account-gated
pages, or profile loading. This template does not implement its own identity
provider. The platform owns auth and exposes a small contract to the website.

## Contract

- Browser code must call app-local endpoints only.
- Server code may call `https://fnf.internal/*`.
- Do not send auth headers to `fnf.internal`; identity is attached by the
  platform/runtime automatically.
- Do not call `https://fnf.internal/*` from the browser. It is not reachable
  there and would be a security bug even if it were.

Endpoints:

| Purpose | Endpoint | Caller |
|---|---|---|
| Current user profile | `GET https://fnf.internal/user` | server only |
| Browser-safe user proxy | `GET /api/user` | frontend/browser |
| Start login | `GET /__auth/login?return=<path>` | browser navigation |
| Start logout | `GET /__auth/logout?return=<path>` | browser navigation |

`GET https://fnf.internal/user` returns the current user's profile JSON and
returns `401` when the visitor is not signed in.

`GET /api/user` must call `https://fnf.internal/user` server-side and return the
same status code and JSON body unchanged. This endpoint is the only user-profile
endpoint browser components should fetch.

## Choose The Correct Auth Mode

There are two different auth concepts. Pick intentionally:

| Website need | Auth mode | Required behavior |
|---|---|---|
| Higgsfield SDK/model generation, media upload, profile, workspace, credits, feed/history | Higgsfield platform auth | Use `/api/user`, `/__auth/login`, `/__auth/logout`, and server-side `https://fnf.internal` guards |
| The generated website's own product accounts, for example todos, notes, CRM records, dashboards, memberships | In-app auth | Build app-local auth/session/storage. Do not call `fnf.internal/user` unless the website also uses Higgsfield SDK features |
| Both generation and product accounts | Both, kept separate | Gate SDK routes with Higgsfield auth and product data with in-app auth. Label UI clearly and never mix identities |

If the prompt mentions Higgsfield, SDK, model generation, Nano Banana, Seedance,
image/video generation, media upload, credits, workspaces, or generation history,
Higgsfield auth is implicit even if the user did not say "add sign in."

If the prompt only asks for "sign in" for a normal generated product and does not
use Higgsfield generation/profile/credits, default to in-app sign in. Do not use
`/__auth/login` as the product's account system unless the prompt specifically
asks for Higgsfield account sign-in.

## Required `/api/user` Route

Create a TanStack Start server route, not a separate Hono/Express API:

```ts
// app/src/routes/api/user.ts
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/api/user')({
  server: {
    handlers: {
      GET: async () => {
        const upstream = await fetch('https://fnf.internal/user')
        const body = await upstream.text()

        return new Response(body, {
          status: upstream.status,
          headers: {
            'content-type': upstream.headers.get('content-type') ?? 'application/json',
            'cache-control': 'no-store',
          },
        })
      },
    },
  },
})
```

Notes:

- Preserve upstream status. A `401` from `fnf.internal/user` must remain `401`
  at `/api/user`.
- Preserve upstream JSON body unchanged. Do not reshape fields in the proxy.
- Add `cache-control: no-store`; user identity is per request.
- Do not add `Authorization`, cookies, service secrets, `hf-user-id`, or
  marketplace headers. The platform injects identity on server egress.
- Do not expose raw fnf internal URLs to the UI.

## Frontend User Loader Pattern

Use `/api/user` from loaders, queries, or components:

```ts
export async function fetchCurrentUser() {
  const response = await fetch('/api/user', { credentials: 'include' })
  if (response.status === 401)
    return null
  if (!response.ok)
    throw new Error('Failed to load user')
  return response.json()
}
```

For route loaders, return `null` for signed-out users rather than crashing the
page. For account-required pages, redirect or render a sign-in action.

## Login

Login is browser navigation, not an SDK call:

```ts
function login(returnPath = window.location.pathname + window.location.search) {
  window.location.href = `/__auth/login?return=${encodeURIComponent(returnPath)}`
}
```

Rules:

- Use the current path as `return` by default.
- Encode the return path.
- Keep the return path app-local. Do not pass full external URLs.
- After login completes, the platform redirects back to `return`; then
  `/api/user` should succeed.

## Logout

Logout is also browser navigation:

```ts
function logout(returnPath = '/') {
  window.location.href = `/__auth/logout?return=${encodeURIComponent(returnPath)}`
}
```

Rules:

- Use `/` or the current public route as the default `return`.
- Clear client-side query/cache state after navigation if the website stores user,
  workspace, feed, or credits data in TanStack Query.
- Do not try to delete platform cookies manually from website code.
- Do not call `fnf.internal` for logout.

## Auth UI Rules

- Signed-out state should show a clear sign-in action using the website's normal
  Quanta button style.
- Do not build email/password forms unless the task explicitly asks for a custom
  identity UI and the platform supports it. The default is `/__auth/login`.
- Do not show fake profile data while loading. Use skeletons or neutral loading
  states.
- Never render emails, names, workspace names, tokens, or raw profile payloads
  into observability events.

## FNF SDK Interaction

For generated websites using the fnf SDK, create SDK adapters server-side with
`baseUrl: 'https://fnf.internal'`. The auth boundary above is for website UI
identity. SDK calls should still use server functions or server-only modules and
must not be made directly from browser components.

## Required Auth For SDK Features

Any website that uses SDK-backed generation must be authenticated. This includes:

- generation submit, poll, cancel, feed/history, and cost preview
- media upload, media resolve, and media reads
- profile, workspace switch, wallet, and credits
- any UI that exposes model settings or writes paid/user-owned outputs

When the user asks for a Higgsfield generation website, model form, image/video
generator, Nano Banana/Seedance/etc. website, or anything that uses the SDK, auth is
implicit even if the user does not say "add sign in." Add sign-in/logout,
`/api/user`, server-side auth guards, profile/credits/workspace UI, and a
feed/history surface automatically.

The only exception is an offline/mock demo the user EXPLICITLY asked for — memory
adapters only, never calling fnf.internal, apps-marketplace, media upload, or
profile endpoints. Never choose a mock as the default: a real SDK app is
end-to-end, with a real backend and D1 persistence (see references/app-flow.md rule 3a).

Required flow:

1. Implement `/api/user`.
2. Browser loads `/api/user` before rendering SDK-backed controls.
3. If `/api/user` returns `401`, show a signed-out state and a Quanta sign-in
   button that navigates to `/__auth/login?return=<current path>`.
4. Disable or hide submit/upload/cost/profile controls while signed out.
5. Every server function or server route that performs an SDK operation must
   call `https://fnf.internal/user` first and stop on `401`.

The UI gate is for experience; the server-side auth check is the actual safety
boundary. Do not rely on "button hidden when signed out" as protection.

If a page needs both user state and generation data:

1. Browser calls `/api/user` for display/auth gate.
2. Server function submits/reads jobs through the selected SDK adapter.
3. Browser receives only safe website data: user-safe fields, generation ids,
   statuses, display credits, and sanitized errors.

## Server Auth Guard Pattern

Use a small server-only helper for SDK server functions:

```ts
// app/src/lib/auth.server.ts
export async function requireCurrentUser() {
  const response = await fetch('https://fnf.internal/user')
  const body = await response.json().catch(() => null)

  if (response.status === 401) {
    return {
      ok: false as const,
      status: 401,
      body,
    }
  }

  if (!response.ok) {
    return {
      ok: false as const,
      status: response.status,
      body,
    }
  }

  return {
    ok: true as const,
    user: body,
  }
}
```

Then guard SDK operations:

```ts
const auth = await requireCurrentUser()
if (!auth.ok) {
  return new Response(JSON.stringify(auth.body), {
    status: auth.status,
    headers: { 'content-type': 'application/json' },
  })
}

// Safe to create SDK adapter/client and submit/read user-owned data here.
```

For `createServerFn`, return a typed `{ ok: false, code: 'unauthorized' }`
result or throw/redirect according to the website's route behavior, but still check
auth before the SDK call.

## Signed-Out UI Pattern

Use this Quanta pattern for **app-shaped** generation/tool UIs. Marketing
waitlists and landing pages should use custom sign-in chrome per
`references/design-taste-frontend.md` instead of Quanta buttons.

```tsx
import { Button } from '@higgsfield/quanta/button'

function SignInRequired() {
  return (
    <div className="grid min-h-72 place-items-center rounded-lg border border-q-border-subtle bg-q-background-secondary p-6 text-center">
      <div className="grid max-w-sm gap-3">
        <h2 className="text-q-title-md-semi-bold">Sign in to generate</h2>
        <p className="text-q-body-sm-regular text-q-text-secondary">
          Generation, uploads, credits, and history are connected to your account.
        </p>
        <div>
          <Button
            onClick={() => {
              const returnPath = window.location.pathname + window.location.search
              window.location.href = `/__auth/login?return=${encodeURIComponent(returnPath)}`
            }}
          >
            Sign in
          </Button>
        </div>
      </div>
    </div>
  )
}
```

Do not render active prompt fields, upload controls, generate buttons, cost
buttons, workspace switchers, or job feeds as usable controls while signed out.

## Anti-Patterns

```ts
await fetch('https://fnf.internal/user') // bad in browser code
await fetch('/api/user')                 // good in browser code
```

```ts
fetch('https://fnf.internal/user', {
  headers: { Authorization: `Bearer ${token}` },
}) // bad; platform attaches identity automatically
```

```ts
window.location.href = '/login' // bad; not the platform auth route
window.location.href = '/__auth/login?return=%2Fdashboard' // good
```

```ts
// bad: anonymous generation surface
await jobs.submit(input)

// good: server-side auth gate first
const auth = await requireCurrentUser()
if (!auth.ok) {
  return new Response(JSON.stringify(auth.body), {
    status: auth.status,
    headers: { 'content-type': 'application/json' },
  })
}
await jobs.submit(input)
```
