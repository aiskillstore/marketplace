# Metadata

Declarative dump of the backend's configured state: auth provider config, database tables, storage buckets, edge functions, AI models, realtime channels. The primary primitive for **what the project is set up to do** — used to confirm configuration matches expectations, find misconfiguration, and detect drift.

## Command

```bash
npx -y @insforge/cli metadata [--json]
```

`--json` for structured output (preferred when extracting fields for follow-up commands).

## What you see

| Section | Contains |
|---------|----------|
| **Auth** | Configured providers (email/password, OAuth providers, third-party JWT), JWT config, allowed redirect URLs |
| **Database** | Tables with schema (columns, types), indexes, triggers |
| **Storage** | Buckets with `public` flag and size limits |
| **Functions** | Edge functions with slug, `status` (`active` / `inactive`), runtime |
| **AI** | Configured models, OpenRouter key presence |
| **Realtime** | Channel patterns and enabled flag |

## How to read

For "is this thing configured the way I think?":

| Symptom | Section to check | What to look for |
|---------|------------------|------------------|
| OAuth callback errors | Auth | Provider enabled? Redirect URLs match the callback in the request? |
| 401 / token-expired everywhere | Auth | JWT secret rotation, third-party provider integration mismatch |
| 404 on `/api/database/records/<name>` | Database | Table exists in the dump? Spelling? |
| Storage upload silently public | Storage | Bucket `public: true` when it should be `false` |
| Edge function returns 404 | Functions | Function in list with `status: "active"`? |
| `functions deploy` succeeded but invoke fails | Functions | Function `status` — may be inactive |
| Realtime channel "doesn't exist" | Realtime | Channel pattern matches what client subscribes to? `enabled: true`? |

## Boundaries

- **Configuration state, not runtime state.** Tells you what's *declared*, not what's *currently broken*. A function with `status: active` may still be crashing on every invocation — pair with [logs](logs.md) (`function.logs`).
- **Doesn't show RLS policies.** For RLS use [policies](policies.md); metadata only confirms the table exists.
- **Snapshot at query time.** Just-applied migrations or deploys may not yet be reflected — wait a moment and re-query if you suspect staleness.

## Example

User reports: "OAuth login with Google redirects but then errors out."

```bash
# 1. Pull current auth config
npx -y @insforge/cli metadata --json

# 2. In the auth section, confirm:
#    - google provider enabled: true
#    - redirect URLs include the exact callback the app uses
#    (e.g., https://myapp.com/auth/callback — protocol + host + path must match)

# 3. If config looks right, check insforge.logs for the OAuth error
npx -y @insforge/cli logs insforge.logs --limit 50
```

## Frequently paired with

- [logs](logs.md) — metadata says "configured" but logs say "actually broken"; pair to distinguish config drift vs runtime failure
- [policies](policies.md) — metadata confirms the table; policies show the RLS gating it
- [advisor](advisor.md) — security/health issues often name a configured object (bucket, secret, function) for inspection
