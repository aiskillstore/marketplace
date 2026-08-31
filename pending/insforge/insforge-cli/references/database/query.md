# npx -y @insforge/cli db query

Execute a raw SQL query against the project database for targeted inspection and row-level data changes.

## Syntax

```bash
npx -y @insforge/cli db query <sql> [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--json` | Return rows as JSON for scripting |

## Examples

```bash
# Basic query
npx -y @insforge/cli db query "SELECT * FROM posts LIMIT 10"

# Update rows
npx -y @insforge/cli db query "UPDATE posts SET status = 'published' WHERE id = 'post_123'"

# Insert rows
npx -y @insforge/cli db query "INSERT INTO posts (title, status) VALUES ('Hello', 'draft')"

# Delete rows
npx -y @insforge/cli db query "DELETE FROM posts WHERE archived = true"

# Inspect Postgres system catalog
npx -y @insforge/cli db query "SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = 'public'"

# Inspect InsForge-managed schema data
npx -y @insforge/cli db query "SELECT * FROM auth.users LIMIT 10"

# JSON output for scripting
npx -y @insforge/cli db query "SELECT count(*) FROM posts" --json
```

## Output

- **Human:** Formatted table
- **JSON:** `{ "rows": [...] }`

## Restrictions

- Do not include transaction control statements in the SQL.
- `db query` rejects `BEGIN`, `COMMIT`, `ROLLBACK`, and `SAVEPOINT` with the error `Transaction control statements are not allowed.`
- Each `db query` call already runs as a single statement in its own transaction, so an explicit `BEGIN ... ROLLBACK` block is not needed for atomicity.

### Rollback Rehearsal (Dry Run) Pattern

To rehearse a guarded data change without committing it, run one `DO` block that performs the mutation, validates the result, and ends with `RAISE EXCEPTION` so PostgreSQL rolls the whole statement back:

```bash
npx -y @insforge/cli db query "DO \$\$
DECLARE
  updated_count integer;
BEGIN
  UPDATE posts SET status = 'draft' WHERE status IS NULL;
  GET DIAGNOSTICS updated_count = ROW_COUNT;
  IF updated_count > 100 THEN
    RAISE EXCEPTION 'guard failed: % rows matched, expected at most 100', updated_count;
  END IF;
  -- Validation passed; raise anyway so the statement rolls back
  RAISE EXCEPTION 'rehearsal ok: % rows would be updated (rolled back)', updated_count;
END
\$\$"
```

The `BEGIN` inside the `DO` block is the PL/pgSQL block keyword, not a transaction statement, so it is allowed.

**A rehearsal always ends as a failed command.** Rolling back means raising, so the command writes to stderr and exits non-zero (`1`) on both the pass and the fail path — that is the expected outcome, not a broken query. Read the message to tell them apart:

| Output on stderr | Meaning |
|------------------|---------|
| `Error: rehearsal ok: 42 rows would be updated (rolled back)` | Validation passed; safe to apply |
| `Error: guard failed: 250 rows matched, expected at most 100` | Validation failed; do not apply |

Under `--json` the same text arrives on stderr as `{"error": "rehearsal ok: ...", "code": "INTERNAL_ERROR"}`. Do not treat the non-zero exit code as a reason to retry.

Once the rehearsal reports `rehearsal ok:`, rerun the mutation as a plain `db query` statement to apply it.

## Permission Model and Schema Changes

`db query` runs as `project_admin`.

- `public`: full access for normal data changes and schema work.
- Postgres system catalogs such as `pg_catalog` and `information_schema`: read-only inspection is allowed.
- InsForge-managed/system schemas such as `auth`, `storage`, `realtime`, `payments`, `graphql`, `extensions`, `pg_catalog`, `information_schema`, or `system`: do not write or run DDL unless you are working on that specific feature module and its docs explicitly allow the operation.

Use `npx -y @insforge/cli db migrations new ...` and `npx -y @insforge/cli db migrations up ...` for schema changes on `public` application objects.

Use `db query` for:

- reading app data and inspecting managed-schema data
- inspecting Postgres system catalogs such as `pg_catalog` and `information_schema`
- backfilling or correcting rows in `public`
- one-off row updates in `public`

For schema, RLS, grants, triggers, functions, indexes, and extensions, create a
migration and apply it.

## InsForge SQL References

When writing SQL for InsForge, use these built-in references:

| Reference | Description |
|-----------|-------------|
| `auth.uid()` | Returns current authenticated user's UUID (use in RLS policies) |
| `auth.users(id)` | Built-in users table — use for foreign keys, not a custom table |
| `system.update_updated_at()` | Built-in trigger function that auto-updates `updated_at` columns |

### Complete Example: Row-Level Data Fix

```bash
# Inspect the current rows
npx -y @insforge/cli db query "SELECT id, status FROM posts WHERE status IS NULL"

# Backfill missing row values
npx -y @insforge/cli db query "UPDATE posts SET status = 'draft' WHERE status IS NULL"
```

## Notes

- For schema changes and RLS policy changes, use the migrations workflow in [migrations.md](migrations.md).
- For advanced access-control patterns (RLS recursion prevention, SECURITY DEFINER, performance), see [access-control.md](access-control.md).
