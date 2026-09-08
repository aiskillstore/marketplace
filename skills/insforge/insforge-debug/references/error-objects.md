# Error objects

The error envelope returned by SDK calls and HTTP responses. The **entry-point primitive** — almost every reactive debug starts by reading the error and routing to the right log source / primitive.

This primitive isn't a command; it's the protocol for reading what the client got back, plus the routing tables that turn an error into "look here next."

## SDK error envelope

```ts
const { data, error } = await client.database.from('posts').select('*')
// error: { code: string, message: string, details?: string }
```

Read all three fields. `code` routes to the right log source; `message` and `details` provide context.

## Error code → log source

| Code prefix | Source | Look in |
|-------------|--------|---------|
| `PGRST*` (PostgREST errors: `PGRST204`, `PGRST301`, etc.) | PostgREST API layer | [logs](logs.md) `postgREST.logs` |
| SQL state codes (`23505` unique violation, `42P01` undefined table, etc.) | Postgres | [logs](logs.md) `postgres.logs` |
| `AUTH_*` / OAuth errors | Backend auth | [logs](logs.md) `insforge.logs` |
| Generic 500 / no code | Server error in backend | [logs](logs.md) — start with `diagnose logs` aggregate, then drill |

## HTTP status routing

| Status | What it means | Where to look |
|--------|---------------|---------------|
| **400** | Request payload/params malformed | [logs](logs.md) `postgREST.logs` for validation error |
| **401** | Auth token missing / invalid / expired | [logs](logs.md) `insforge.logs` + [metadata](metadata.md) auth config |
| **403** | RLS policy or permission denied | [logs](logs.md) `postgREST.logs` + [policies](policies.md) + [metadata](metadata.md) |
| **404** | Endpoint or resource doesn't exist | [metadata](metadata.md) — verify the table/function/bucket exists |
| **429** | Rate limit hit | **No logs** — see 429 note below |
| **500** | Server-side error | [logs](logs.md) `diagnose logs` (aggregate) → drill into specific source |
| **502 / 503 / 504** | Gateway / upstream timeout | Route by URL subsystem — see 5xx gateway note |

## 429 — special case

429 responses are **not logged** in any source and the backend does **not return** `Retry-After` or `X-RateLimit-*` headers. Checking logs is useless.

What to do:

1. Read the client code that issued the request. Look for: loops without throttling, missing debounce, retry-on-failure without exponential backoff, parallel calls that could be batched.
2. Check [metrics](metrics.md) for overall backend load context — is the system being slammed?
3. **The fix is always client-side**: reduce frequency, add backoff/debounce, batch operations.

## 5xx gateway timeout (502 / 503 / 504) — route by URL subsystem

The status alone doesn't tell you which subsystem timed out. Route by the URL path:

| URL pattern | Subsystem | Look in |
|-------------|-----------|---------|
| `/api/database/records/...` or `/api/database/...` | PostgREST → Postgres | [logs](logs.md) `postgREST.logs` then `postgres.logs`; [db-health](db-health.md) `locks`, `slow-queries` |
| `/functions/<slug>` | Edge function | [logs](logs.md) `function.logs`; check function isn't crash-looping |
| `/api/auth/...` | Auth backend | [logs](logs.md) `insforge.logs` |
| `/api/storage/...` | Storage | [logs](logs.md) `insforge.logs` |
| Any path during a system-wide spike | EC2 saturation | [metrics](metrics.md) `--range 1h` |
| Intermittent, across *unrelated* paths, small instance | Likely OOM | `diagnose incident` (cloud-side verdict, works while the box is down; Platform login required — unavailable on older CLI/backend or `--api-key` link mode); fallback: the gateway-timeout recipe's OOM branch — crash-recovery aftermath in `postgres.logs`, then upgrade the instance |
| Instance entirely unreachable (logs/metrics dead) | Box down | `diagnose incident` — built from platform-side sources, so it answers when every per-project endpoint is dead (same availability caveat; without it, escalate to support) |

## Example

User pastes: `POST /api/database/records/posts returned { code: "PGRST204", message: "Column not found" }`.

1. Read code: `PGRST*` → PostgREST source. `PGRST204` specifically means **column not found** — a `select` / `columns` / `order` / filter parameter references a column that doesn't exist on the table.
2. Read `message` / `details` to identify the offending column name. Verify the table schema with `npx -y @insforge/cli db tables` or `npx -y @insforge/cli metadata --json`.
3. Drop into `postgREST.logs` for the full error context if `details` is empty:

```bash
npx -y @insforge/cli logs postgREST.logs --limit 50
```

## Frequently paired with

- [logs](logs.md) — every code routes to a log source for the actual error context
- [policies](policies.md) — 403 always needs policy inspection
- [metadata](metadata.md) — 404 / config-related codes need metadata to confirm the configured state
- [ai-assisted](ai-assisted.md) — when the code is unfamiliar or the error spans subsystems, hand it to `diagnose --ai`
