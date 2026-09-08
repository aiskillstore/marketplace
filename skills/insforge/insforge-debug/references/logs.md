# Logs

Time-stream of events emitted by each backend service. The primary primitive for finding **when** something failed and **what the backend was doing at that moment**.

## Command

```bash
npx -y @insforge/cli logs <source> [--limit <n>]
```

Default limit: 20. Source names are **case-insensitive** (`postgrest.logs` works the same as `postgREST.logs`).

## Sources

| Source | What it contains | Reach for when |
|--------|------------------|----------------|
| `insforge.logs` | Main backend (auth, API gateway, realtime, edge function dispatcher, deploy controller) | Auth/OAuth errors, realtime WS errors, generic 5xx, signup/login failures |
| `postgREST.logs` | PostgREST API layer (REST/CRUD over the database) | 400 (payload), 403 (RLS denied), PGRST* error codes |
| `postgres.logs` | PostgreSQL itself | SQL errors, query warnings, slow query log, deadlock, constraint violations |
| `function.logs` | Edge function **execution** (per-invocation runtime) | Function threw / timed out / unhandled rejection |
| `function-deploy.logs` | Edge function **deploy** (build + push) | `functions deploy` failed; function isn't in `functions list` |

## Cross-source aggregate

```bash
npx -y @insforge/cli diagnose logs [--source <name>] [--limit <n>]
```

Aggregates **error-level only** rows across all sources. Use first when you don't know which source the error lives in.

## How to read

Each line has timestamp + source + level + message. When chasing a known-time symptom:

1. Get the approximate timestamp from the user (when did the request fail?)
2. Increase `--limit` until the window covers it (start 50, bump to 200 if needed)
3. Look for the level (`ERROR` / `WARN`) and message — the message usually names the failing component

For request-correlated symptoms (single failing URL), look for the request line in `postgREST.logs` (REST calls) or `insforge.logs` (auth/realtime/function dispatch) — both include the URL path.

## Boundaries

- **Logs are streamed, not retained forever.** If the user reports something from days ago, you may not find it. State this explicitly instead of guessing.
- **429 responses are NOT logged.** Rate limit hits don't appear in any source — confirm via [error-objects](error-objects.md) status code and check [metrics](metrics.md) for backend load context.
- **`diagnose logs` filters to errors only.** For warnings or info-level activity, query the specific source directly.

## Example

User reports: `POST /api/database/records/posts returned 500 around 14:32`.

```bash
# Aggregate first to see if the error surfaces anywhere
npx -y @insforge/cli diagnose logs --limit 100

# If it's a CRUD path, postgREST is the likely source
npx -y @insforge/cli logs postgREST.logs --limit 100

# If postgREST log shows "SQL error", drop into postgres
npx -y @insforge/cli logs postgres.logs --limit 100
```

## Frequently paired with

- [error-objects](error-objects.md) — start there to pick the right source from the error code/HTTP status
- [db-health](db-health.md) — when postgres.logs shows slow/locked queries, confirm with `pg_stat_*`
- [policies](policies.md) — when postgREST.logs shows RLS denial, inspect which policy fired
- [metadata](metadata.md) — when logs show auth/function/channel errors, verify the configured state
