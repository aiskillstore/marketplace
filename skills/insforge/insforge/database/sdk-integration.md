# Database SDK Integration

Use InsForge SDK to perform CRUD operations in your frontend application.

## Setup

First, ensure your `.env` file is configured with your InsForge URL and anon key. Get the anon key with `npx -y @insforge/cli secrets get ANON_KEY`. See the main [SKILL.md](../SKILL.md) for framework-specific variable names and full setup steps.

```javascript
import { createClient } from '@insforge/sdk'

const insforge = createClient({
  baseUrl: process.env.NEXT_PUBLIC_INSFORGE_URL,       // adjust prefix for your framework
  anonKey: process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY   // adjust prefix for your framework
})
```

For trusted server-only database work that needs project-admin access:

```javascript
import { createAdminClient } from '@insforge/sdk'

const admin = createAdminClient({
  baseUrl: process.env.INSFORGE_URL,
  apiKey: process.env.INSFORGE_API_KEY
})
```

## CRUD Operations

### Select

```javascript
// Specific columns (default choice — smaller responses, less bandwidth)
const { data, error } = await insforge.database.from('posts').select('id, title')

// All columns — reserve for single-record detail views; bound list reads with .limit()
const { data } = await insforge.database
  .from('posts')
  .select()
  .order('created_at', { ascending: false })
  .order('id', { ascending: false })   // tie-breaker keeps page membership stable
  .limit(50)

// With relationships
const { data } = await insforge.database.from('posts').select('*, comments(id, content)')
```

Default to naming columns and bounding list reads. An unbounded `select()` re-downloads the whole table on every call — see [Bandwidth-efficient reads](#bandwidth-efficient-reads).

### Insert

```javascript
// Single record (MUST use array format)
const { data, error } = await insforge.database
  .from('posts')
  .insert([{ title: 'Hello', content: 'World' }])
  .select()

// Bulk insert
const { data } = await insforge.database
  .from('posts')
  .insert([{ title: 'A' }, { title: 'B' }])
  .select()
```

When a table has RLS enabled, `.insert(...).select()` behaves like
`INSERT ... RETURNING`: the new row must pass both the `INSERT` policy and the
`SELECT` policy. If `WITH CHECK` looks correct but the call still fails with
`new row violates row-level security policy`, make sure the returned row is
also visible to the caller.

### Update

```javascript
const { data, error } = await insforge.database
  .from('posts')
  .update({ title: 'Updated' })
  .eq('id', postId)
  .select()
```

### Delete

```javascript
const { error } = await insforge.database
  .from('posts')
  .delete()
  .eq('id', postId)
```

### RPC (Stored Procedures)

```javascript
const { data, error } = await insforge.database.rpc('get_user_stats', { user_id: '123' })
```

## Selecting a Schema

Queries target the `public` schema by default — reach for `.schema()` only when you need a different one. The table name stays bare; `.schema()` maps to PostgREST's `Accept-Profile` (reads) / `Content-Profile` (writes) headers and chains in front of `from()` and `rpc()`:

```javascript
const { data, error } = await insforge.database
  .schema('analytics')
  .from('events')
  .select('id, name, occurred_at')

// Writes chain the same way
const { error: insertError } = await insforge.database
  .schema('analytics')
  .from('events')
  .insert([{ name: 'signup' }])

const { data: rollup, error: rpcError } = await insforge.database
  .schema('analytics')
  .rpc('rollup', { day: '2026-01-01' })
```

To make every query use one schema, set the default when you create the client (omit it to stay on `public`):

```javascript
const insforge = createClient({
  baseUrl: process.env.NEXT_PUBLIC_INSFORGE_URL,
  anonKey: process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY,
  db: { schema: 'analytics' },
})
```

**You must grant access yourself.** On v2.2.3+ backends every non-internal schema you create is automatically reachable over the data API, but a new schema's tables stay **unreadable to `anon`/`authenticated` until you grant them** — exposure is not access. Grant in the same migration that creates the table, then RLS filters rows exactly as in `public`:

```sql
GRANT USAGE ON SCHEMA analytics TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA analytics TO anon, authenticated;
```

**Don't target InsForge-internal schemas.** Platform schemas (`auth`, `storage`, `system`, `payments`, …) are never exposed over the data API — keep app data in `public` or your own schemas so you never collide with them. Pointing `.schema()` at an internal schema (or any schema an older backend doesn't expose) fails with PostgREST `PGRST106` ("The schema must be one of the following: ...") rather than silently falling back to `public`.

## Filters

| Filter | Example |
|--------|---------|
| `.eq(col, val)` | `.eq('status', 'active')` |
| `.neq(col, val)` | `.neq('status', 'deleted')` |
| `.gt(col, val)` | `.gt('age', 18)` |
| `.gte(col, val)` | `.gte('price', 100)` |
| `.lt(col, val)` | `.lt('stock', 10)` |
| `.lte(col, val)` | `.lte('score', 50)` |
| `.like(col, pattern)` | `.like('name', '%Widget%')` |
| `.ilike(col, pattern)` | `.ilike('email', '%@gmail.com')` |
| `.in(col, array)` | `.in('status', ['pending', 'active'])` |
| `.is(col, val)` | `.is('deleted_at', null)` |

## Modifiers

| Modifier | Example |
|----------|---------|
| `.order(col, opts)` | `.order('created_at', { ascending: false })` |
| `.limit(n)` | `.limit(10)` |
| `.range(from, to)` | `.range(0, 9)` |
| `.single()` | Returns object, throws if multiple |
| `.maybeSingle()` | Returns object or null |

## Pagination

```javascript
const page = 1, pageSize = 10
const from = (page - 1) * pageSize
const to = from + pageSize - 1

const { data, count } = await insforge.database
  .from('posts')
  .select('id, title, created_at', { count: 'exact' })
  .range(from, to)
  .order('created_at', { ascending: false })
```

## Bandwidth-efficient reads

Every byte a query returns counts against the project's monthly egress allowance. The most common way projects exhaust it is not traffic volume — it is a small number of wasteful query shapes, usually written once and left running:

- **Never poll with unbounded selects.** A dashboard or hook that re-runs `select()` (all columns, no limit) on an interval re-downloads the entire table every cycle. A table with a few hundred rows of JSONB polled every 30 seconds costs ~1 GB/day with a single viewer. To watch for changes, subscribe with [realtime](../realtime/sdk-integration.md) instead of polling — realtime is channel pub/sub, so pair the subscription with a database trigger that calls `realtime.publish(...)` on writes (backend setup: [insforge-cli realtime reference](../../insforge-cli/references/realtime.md)); table changes do not stream automatically. If you must poll, poll something cheap — `select('updated_at', { count: 'exact' }).order('updated_at', { ascending: false }).limit(1)` — and fetch full rows only when the count or newest `updated_at` moves: the count catches inserts and deletes, the timestamp catches edits (keep a `system.update_updated_at()` trigger on the table so edits advance it).
- **Bound every list read.** Always chain `.limit(n)` or `.range(from, to)` on queries that can return multiple rows. Render lists with [pagination](#pagination).
- **Name your columns.** `select('id, title')` instead of `select()` whenever the table has text/JSONB columns the view doesn't render. Fetch heavy columns (`draft_data`-style JSONB blobs, long text) only on the detail screen that needs them.
- **Pause refresh loops when idle.** If the UI auto-refreshes, stop the timer when the tab is hidden (`document.visibilityState`) — an admin page left open overnight is the classic silent egress burner.
- **Let storage objects cache.** Serve files with stable URLs so browsers and the CDN cache them, rather than re-downloading per render (cache-busting query params on every request defeat this).

## Important Notes

- **Insert requires array format**: Always use `insert([{...}])` not `insert({...})`
- **Avoid large JSON/JSONB payloads in SDK reads/writes**: PostgREST can consume excessive memory when rows contain multi-megabyte JSONB payloads. As a rule of thumb, treat JSONB around 1 MB or larger per row as a caution point for hot SDK paths, and normalize multi-megabyte or frequently accessed JSON into typed columns or child tables.
- **Select only the columns you need**: If a table has any large text/JSONB columns, avoid `select('*')` in list views. Fetch lightweight columns first, then lazy-load fields over ~1 MB on a detail screen or through a purpose-built RPC.
- All methods return `{ data, error }` - always check for errors

---

## InsForge SQL References

When creating tables via `insforge db query` (CLI), use these built-in references:

| Reference | Description |
|-----------|-------------|
| `auth.uid()` | Returns current authenticated user's UUID |
| `auth.users(id)` | Reference to the built-in users table for foreign keys |
| `auth.users.profile` | JSONB profile metadata; use `profile->>'name'` / `profile->>'avatar_url'` in auth triggers |
| `system.update_updated_at()` | Built-in trigger function that auto-updates `updated_at` columns |

### Complete Example: Table with RLS and Triggers

```sql
-- Create table with user ownership
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Policies (see the insforge-cli database access-control reference for advanced patterns)
CREATE POLICY "users_can_insert_own_posts" ON posts
  FOR INSERT TO authenticated
  WITH CHECK (user_id = auth.uid());

-- Needed when app code uses .insert(...).select()
CREATE POLICY "users_can_read_own_posts" ON posts
  FOR SELECT TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "users_can_update_own_posts" ON posts
  FOR UPDATE TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "users_can_delete_own_posts" ON posts
  FOR DELETE TO authenticated
  USING (user_id = auth.uid());

-- Allow authenticated SDK callers to reach the table; RLS still filters rows
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON posts TO authenticated;

-- Auto-update updated_at on every UPDATE
CREATE TRIGGER posts_updated_at
  BEFORE UPDATE ON posts
  FOR EACH ROW
  EXECUTE FUNCTION system.update_updated_at();
```

> For access-control best practices (RLS, infinite recursion prevention, SECURITY DEFINER, performance), see the **insforge-cli** skill's [database/access-control.md](../../insforge-cli/references/database/access-control.md) reference.

### Bulk Upsert (HTTP API)

Import CSV or JSON files directly into a table. No CLI equivalent yet — use the HTTP API.

```http
POST /api/database/advance/bulk-upsert
Authorization: Bearer {admin-token-or-api-key}
Content-Type: multipart/form-data

Fields:
- file: CSV or JSON file (required)
- table: Target table name (required)
- upsertKey: Column for conflict resolution (optional)
```

| Parameter | Effect |
|-----------|--------|
| Without `upsertKey` | INSERT all records |
| With `upsertKey` | UPSERT — update existing rows on conflict, insert new ones |

---

## Best Practices

1. **Generate TypeScript interfaces for every table schema**
   - Use `insforge db tables` and `insforge db query` (CLI) to inspect the table schema
   - Create a corresponding TypeScript interface/type for type safety
   - This helps catch errors at compile time and improves developer experience

2. **Normalize large JSONB data before building CRUD flows**
   - Do not store large app state, document bodies, analytics payloads, or arrays of nested objects in a single JSONB column that the app reads/writes through PostgREST.
   - Prefer real columns for fields you filter, sort, display in lists, or update independently.
   - Move repeated nested objects into child tables with foreign keys and indexes.
   - Measure suspicious payloads with `pg_column_size(jsonb_column)` and enforce limits or warnings during ingestion.

### Example: Generate Interface from Schema

```typescript
// After checking table schema via `insforge db tables`
// Create a typed interface:

interface Post {
  id: string
  user_id: string
  title: string
  content: string | null
  created_at: string
  updated_at: string
}

// Cast data to the interface after select
const { data, error } = await insforge.database
  .from('posts')
  .select()

const posts = data as Post[]
```

## Recommended Workflow

```
1. Check table schema     → insforge db tables / insforge db query
2. Check for large JSONB fields and normalize them if needed
3. Generate TypeScript interface for the table
4. Cast query results to the interface for type safety
5. Handle errors appropriately
```
