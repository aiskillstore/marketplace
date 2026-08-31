---
name: insforge
description: >-
  Use this skill when writing app code with InsForge or @insforge/sdk: database CRUD, auth, storage uploads/storage RLS, functions, OpenRouter AI, realtime, emails, Stripe or Razorpay payments, or pointing S3-compatible tooling (aws CLI, AWS SDKs, rclone, Terraform, boto3) at InsForge Storage. Trigger on requests like add auth, fetch data, upload files, make a bucket public, add checkout, sell subscriptions, or send email. For infrastructure, SQL migrations, CLI commands, or payment provider setup, use insforge-cli instead.
license: Apache-2.0
---

# InsForge App Integration Skill

This skill covers **client-side SDK integration** using `@insforge/sdk`. For backend infrastructure operations (creating tables, inspecting schema, deploying functions, secrets, managing storage buckets, configuring payment provider keys/catalog, website deployments, cron job and schedules, logs, etc.), use the **insforge-cli** skill.

## Quick Setup

### 1. Install the SDK

```bash
npm install @insforge/sdk@latest
```

### 2. Set up environment variables

Before using the SDK, create a `.env` file (or `.env.local` for Next.js) in your project root with your InsForge URL and anon key.

#### How to get your URL and anon key

1. **Ensure the project is linked.** Check for `.insforge/project.json` in the project root.
   - Generate it with `npx -y @insforge/cli link` for an existing project or `npx -y @insforge/cli create` for a new project.

2. **Get the anon key** via the CLI:

   ```bash
   npx -y @insforge/cli secrets get ANON_KEY
   ```

3. **Get the URL** from the `oss_host` field in `.insforge/project.json` (e.g., `https://myapp.us-east.insforge.app`).

4. **Write both values** to the `.env` file using the correct framework prefix (see table below).

> **Important:** Use the anon key for user-scoped SDK clients, including SSR. For privileged server-only app code that needs admin/service access, use `createAdminClient({ apiKey })`; the API key is a full-access admin key, equivalent to a service role key on other platforms.

Use the correct environment variable prefix and access pattern for your framework:

| Framework                     | `.env` file  | Variables                                                   | Access Pattern                              |
| ----------------------------- | ------------ | ----------------------------------------------------------- | ------------------------------------------- |
| **Next.js**                   | `.env.local` | `NEXT_PUBLIC_INSFORGE_URL`, `NEXT_PUBLIC_INSFORGE_ANON_KEY` | `process.env.NEXT_PUBLIC_*`                 |
| **Vite** (React, Vue, Svelte) | `.env`       | `VITE_INSFORGE_URL`, `VITE_INSFORGE_ANON_KEY`               | `import.meta.env.VITE_*`                    |
| **Astro**                     | `.env`       | `PUBLIC_INSFORGE_URL`, `PUBLIC_INSFORGE_ANON_KEY`           | `import.meta.env.PUBLIC_*`                  |
| **SvelteKit**                 | `.env`       | `PUBLIC_INSFORGE_URL`, `PUBLIC_INSFORGE_ANON_KEY`           | `import { env } from '$env/dynamic/public'` |
| **Create React App**          | `.env`       | `REACT_APP_INSFORGE_URL`, `REACT_APP_INSFORGE_ANON_KEY`     | `process.env.REACT_APP_*`                   |
| **Node.js / Server**          | `.env`       | `INSFORGE_URL`, `INSFORGE_ANON_KEY`                         | `process.env.*`                             |

Example `.env.local` for Next.js:

```bash
NEXT_PUBLIC_INSFORGE_URL=https://your-appkey.us-east.insforge.app
NEXT_PUBLIC_INSFORGE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
```

> **Important:** Keep `.env` files local. Add `.env`, `.env.local`, and `.env*.local` to your `.gitignore` and keep `.env.example` for documenting required variables.

### 3. Initialize the client

Next.js:

```javascript
import { createClient } from '@insforge/sdk'

const insforge = createClient({
  baseUrl: process.env.NEXT_PUBLIC_INSFORGE_URL,
  anonKey: process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY
})
```

Vite:

```javascript
import { createClient } from '@insforge/sdk'

const insforge = createClient({
  baseUrl: import.meta.env.VITE_INSFORGE_URL,
  anonKey: import.meta.env.VITE_INSFORGE_ANON_KEY
})
```

Astro:

```javascript
import { createClient } from '@insforge/sdk'

const insforge = createClient({
  baseUrl: import.meta.env.PUBLIC_INSFORGE_URL,
  anonKey: import.meta.env.PUBLIC_INSFORGE_ANON_KEY
})
```

For trusted server-only code that needs project-admin access:

```javascript
import { createAdminClient } from "@insforge/sdk";

const admin = createAdminClient({
  baseUrl: process.env.INSFORGE_URL,
  apiKey: process.env.INSFORGE_API_KEY,
});
```

## Module Reference

| Module        | Integration Guide                                            |
| ------------- | ------------------------------------------------------------ |
| **Database**  | [database/sdk-integration.md](database/sdk-integration.md)   |
| **Auth**      | [auth/sdk-integration.md](auth/sdk-integration.md)           |
| **Storage**   | [storage/sdk-integration.md](storage/sdk-integration.md)     |
| **Functions** | [functions/sdk-integration.md](functions/sdk-integration.md) |
| **AI**        | [ai/overview.md](ai/overview.md)                             |
| **Real-time** | [realtime/sdk-integration.md](realtime/sdk-integration.md)   |
| **Email**     | [email/sdk-integration.md](email/sdk-integration.md)         |
| **Payments: Stripe** | [payments/stripe.md](payments/stripe.md)             |
| **Payments: Razorpay** | [payments/razorpay.md](payments/razorpay.md)       |

### What Each Module Covers

| Module        | Content                                                                                                       |
| ------------- | ------------------------------------------------------------------------------------------------------------- |
| **Database**  | CRUD operations, filters, pagination, RPC calls                                                               |
| **Auth**      | Sign up/in, OAuth, sessions, profiles, password reset                                                         |
| **Storage**   | Upload, download, delete files; S3-compatible gateway for CI / backup tooling; write RLS policies for buckets |
| **Functions** | Invoke edge functions                                                                                         |
| **AI**        | OpenRouter AI calls for chat, images, video, audio, embeddings, and model discovery                           |
| **Email**     | Send custom transactional HTML emails (welcome, newsletter, notifications)                                    |
| **Payments: Stripe** | Stripe Checkout Sessions, subscriptions, and Billing Portal redirects                                  |
| **Payments: Razorpay** | Razorpay Orders, Subscriptions, Checkout.js, and subscription management                               |
| **Real-time** | Connect, subscribe, publish events, and track presence snapshots plus join/leave deltas                       |

### Guides

| Guide                                                                                                          | When to Use                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [../insforge-cli/references/database/access-control.md](../insforge-cli/references/database/access-control.md) | Backend setup for application-table access control — covers RLS, infinite recursion prevention, `SECURITY DEFINER` patterns, performance tips, and common InsForge patterns                                                                                                                                                                                                                            |
| [storage/s3-gateway.md](storage/s3-gateway.md)                                                                 | Fallback path when the consumer is existing S3 tooling (aws CLI, AWS SDKs, rclone, Terraform, boto3) and adopting `@insforge/sdk` is impractical — covers endpoint/region setup, access-key management, path-style addressing, and supported vs. not-supported S3 operations. **Requires InsForge 2.0.9+.** **Prefer the SDK** ([storage/sdk-integration.md](storage/sdk-integration.md)) for app code |
| [storage/postgres-rls.md](storage/postgres-rls.md)                                                             | Writing RLS policies for `storage.objects` — owner-only, public-read, path-scoped, team-shared, and the `NULL uploaded_by` caveat for mixed REST + S3 buckets                                                                                                                                                                                                                                          |
| [../insforge-cli/references/database/vector.md](../insforge-cli/references/database/vector.md)                 | Backend setup for semantic search, recommendations, or RAG — covers the `vector` extension, schema/dimensions, distance operators, HNSW/IVFFlat indexes, and RPC similarity search                                                                                                                                                                                                                     |
| [ai/chat-completions.md](ai/chat-completions.md)                                                               | Text generation, structured answers, and streaming chat through OpenRouter                                                                                                                                                                                                                                                                                                                             |
| [ai/image-generation.md](ai/image-generation.md)                                                               | Image generation/editing through OpenRouter, then durable storage in InsForge Storage                                                                                                                                                                                                                                                                                                                  |
| [ai/video-generation.md](ai/video-generation.md)                                                               | Async OpenRouter video jobs, status polling, and storing generated media                                                                                                                                                                                                                                                                                                                               |
| [ai/audio.md](ai/audio.md)                                                                                     | Speech-to-text, text-to-speech, and storing audio assets/transcripts with InsForge                                                                                                                                                                                                                                                                                                                     |
| [ai/embeddings-and-rag.md](ai/embeddings-and-rag.md)                                                           | Generating embeddings through OpenRouter, storing them in pgvector, and wiring up a basic RAG pipeline                                                                                                                                                                                                                                                                                                 |
| [ai/models-list.md](ai/models-list.md)                                                                         | Discovering OpenRouter model IDs, modalities, parameters, pricing, and embedding dimensions                                                                                                                                                                                                                                                                                                            |
| [payments](../insforge-cli/references/payments/overview.md)                                                    | Configuring Stripe/Razorpay keys, syncing provider catalog, setting up webhooks, and writing payment RLS before app integration                                                                                                                                                                                                                                                                        |

### Building Payments for a New App

First choose the provider. There is no generic app payments guide:

- For Stripe Checkout, subscriptions, and Billing Portal, load [payments/stripe.md](payments/stripe.md).
- For Razorpay Orders, Subscriptions, Checkout.js, and cancel/pause/resume flows, load [payments/razorpay.md](payments/razorpay.md).

Before writing app code, check provider setup with the **insforge-cli** payments references:

```bash
npx -y @insforge/cli payments stripe status
npx -y @insforge/cli payments razorpay status
```

If the chosen provider is unconfigured, ask the developer/admin to configure that provider first.

### Real-time Backend Setup

The real-time SDK is for frontend event handling and messaging. Configure channel patterns, database triggers, and channel/message RLS with the **insforge-cli** skill; see [realtime](../insforge-cli/references/realtime.md).

### Backend Configuration

Supported project config knobs are managed via the CLI — use
`npx -y @insforge/cli config export/plan/apply` for auth redirect URLs,
verification flags, password policy, auth SMTP settings, storage upload size,
realtime/schedule retention, and cloud deployment subdomain. OAuth providers,
external app setup, storage buckets, functions, secrets, and deployment env vars
still use their dedicated dashboard or CLI flows. See the **insforge-cli**
skill's Configuration section.

### Risky backend changes? Use a branch first

When a code change in this skill depends on a **schema migration**, **new RLS policy**, **OAuth provider config change**, or any other backend change that affects prod behavior, create a backend branch first. Branches share `JWT_SECRET` (existing user JWTs keep working) but get a fresh database + EC2 + `API_KEY` / `ANON_KEY`, so you can test the SDK + backend change end-to-end in isolation.

The full branching workflow lives in the **insforge-cli** skill — see [branch](../insforge-cli/references/branch/overview.md) for the decision guide and lifecycle commands. Typical loop:

```bash
npx -y @insforge/cli branch create feat-x --mode schema-only
# ... apply migrations / change auth config / update RLS on the branch ...
# ... test the SDK against the branch backend ...
npx -y @insforge/cli branch merge feat-x --dry-run     # review SQL
npx -y @insforge/cli branch merge feat-x               # apply to parent
```

> ⚠ **After `branch create` or `branch switch`**, update the app's InsForge URL and anon-key env values, then **restart your dev server** (or re-source `.env`) so the SDK talks to the selected branch backend.

## SDK Quick Reference

All SDK methods return `{ data, error }`.

| Module               | Methods                                                                                              |
| -------------------- | ---------------------------------------------------------------------------------------------------- |
| `insforge.database`  | `.from().select()`, `.insert()`, `.update()`, `.delete()`, `.rpc()`                                  |
| `insforge.auth`      | `.signUp()`, `.signInWithPassword()`, `.signInWithOtp()` / `.verifyOtp()`, `.signInWithOAuth()`, `.signOut()`, `.getCurrentUser()`        |
| `insforge.storage`   | `.from().upload()`, `.uploadAuto()`, `.download()`, `.remove()`                                      |
| `insforge.functions` | `.invoke()`                                                                                          |
| `insforge.ai`        | Deprecated fallback only: `.chat.completions.create()`, `.images.generate()`, `.embeddings.create()` |
| `insforge.realtime`  | `.connect()`, `.subscribe()`, `.publish()`, `.on()`, `.disconnect()`                                 |
| `insforge.emails`    | `.send({ to, subject, html, cc?, bcc?, from?, replyTo? })`                                           |
| `insforge.payments.stripe` | `.createCheckoutSession()`, `.createCustomerPortalSession()` |
| `insforge.payments.razorpay` | `.createOrder()`, `.verifyOrder()`, `.createSubscription()`, `.verifySubscription()`, `.cancelSubscription()`, `.pauseSubscription()`, `.resumeSubscription()` |

## Important Notes

- **Database inserts require array format**: `insert([{...}])`
- **Bandwidth-efficient reads**: Name columns and `.limit()` list reads; never poll unbounded `select()` on an interval — subscribe with realtime (paired with a `realtime.publish` trigger) or poll a cheap ordered probe instead. Wasteful query shapes are the top cause of projects exhausting their monthly egress allowance. Probe snippet and full rules: [database/sdk-integration.md](database/sdk-integration.md#bandwidth-efficient-reads).
- **Next.js / SSR auth**: Use `@insforge/sdk/ssr` helpers (`createBrowserClient`, `createServerClient`, `createAuthActions`, `createRefreshAuthRouter`) and import `updateSession` from `@insforge/sdk/ssr/middleware` in Proxy/Middleware. Keep the refresh token httpOnly, run auth mutations through `createAuthActions()` on the server, return only safe app data from Server Actions, and let the browser read the short-lived access token for Storage/Realtime. See [auth/ssr-integration.md](auth/ssr-integration.md)
- **Storage**: Save both `url` AND `key` to database for download/delete operations
- **Functions invoke URL**: Prefer `insforge.functions.invoke(slug)` — the SDK owns route construction. For raw HTTP: the project base URL serves the compat path `/functions/{slug}`, while the functions deployment host (e.g. `*.function2.insforge.app`) serves the slug at root `/{slug}`
- **Email delivery**: Auth emails (signup verification, password reset, magic links, invites) ship on **every plan**. Custom email via `insforge.emails.send()` ships on **every paid plan**. Use the platform-managed delivery path; custom sender domain is dashboard config. See [email/sdk-integration.md](email/sdk-integration.md).
- **Payments**: Configure provider keys/catalog with `npx -y @insforge/cli payments <provider> ...` first; frontend code uses provider-scoped SDK modules.
- **Payment RLS**: Before payment UI, add app-specific RLS on provider runtime tables. Stripe uses `payments.stripe_checkout_sessions` and `payments.stripe_customer_portal_sessions`; Razorpay uses `payments.razorpay_orders` and `payments.razorpay_subscriptions`. Durable fulfillment triggers go on `payments.webhook_events`, not success URLs, Checkout callbacks, or `payments.transactions`.
- **Use Tailwind CSS v3.4**
- **Always local build before deploy**: Prevents wasted build resources and faster debugging
- **SDK package**: Use `@insforge/sdk` directly for all features including authentication.
- **Deployment**: Include a `vercel.json` in the project root for SPA routing (React, React Router apps). The `download-template` tool includes this automatically.
- **Branching for risky backend changes**: If your SDK code depends on a new schema, RLS policy, or auth config change, create a branch via `npx -y @insforge/cli branch create` first — see the **insforge-cli** skill's [branch](../insforge-cli/references/branch/overview.md) reference. After `branch create` / `branch switch`, update the app's InsForge URL and anon-key env values, then **restart the dev server**.
- **Hit an InsForge-side hurdle?** When the SDK, backend, docs, or a skill misbehaves — an API that should work but errors (`--type bug`), a capability you need that isn't supported (`--type feature-request`), docs that contradict actual behavior (`--type bug --component docs` with `--doc`/`--expected`) — report it and continue with a workaround: `npx -y @insforge/cli feedback --json --type <bug|feature-request|friction> --component <backend|sdk|cli|skills|docs> --title "..." --detail "..."`, adding `--language <lang>` for SDK issues (no login required; PII is redacted locally). See the **insforge-cli** skill's Feedback section for the full flag set and situation→type mapping. Never file feedback for problems in the app code you are writing.
