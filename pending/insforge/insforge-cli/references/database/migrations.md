# npx -y @insforge/cli db migrations

Manage developer database migration files for an InsForge project.

## Commands

```bash
npx -y @insforge/cli db migrations list
npx -y @insforge/cli db migrations fetch
npx -y @insforge/cli db migrations new <migration-name>
npx -y @insforge/cli db migrations up <migration-file-name-or-version>
npx -y @insforge/cli db migrations up --to <migration-file-name-or-version>
npx -y @insforge/cli db migrations up --all
```

## What Each Command Does

| Command | Description |
|--------|-------------|
| `list` | Show applied remote migrations (version, name, created date) |
| `fetch` | Download remote applied migrations into `migrations/` |
| `new <migration-name>` | Create the next local migration file with the next timestamp version |
| `up <filename\\|version>` | Apply exactly one explicit local migration file |
| `up --to <filename\\|version>` | Apply pending local migrations up to a chosen target |
| `up --all` | Apply every pending local migration file |

## Filename Format

Migration files must be named exactly:

```text
<migration_version>_<migration-name>.sql
```

Examples:

- valid: `20260418091500_create-users.sql`
- valid: `20260418103045_add-post-index.sql`
- invalid: `20260418_create-users.sql`
- invalid: `20260418091500_create_users.sql`
- invalid: `20260418091500_CreateUsers.sql`
- invalid: `20260418091500 create-users.sql`

### Migration Name Rules

The `<migration-name>` portion must use:

- lowercase letters
- numbers
- hyphens

No spaces, underscores, uppercase letters, or other special characters.

## Local Directory

Migration files live under:

```text
migrations/
```

## Examples

```bash
# View remote migration history
npx -y @insforge/cli db migrations list

# Fetch remote migration files into migrations/
npx -y @insforge/cli db migrations fetch

# Create the next migration file
npx -y @insforge/cli db migrations new create-posts

# Apply by exact filename
npx -y @insforge/cli db migrations up 20260418091500_create-posts.sql

# Apply by version
npx -y @insforge/cli db migrations up 20260418091500

# Apply all pending migrations through a target
npx -y @insforge/cli db migrations up --to 20260418110000

# Apply all pending migrations
npx -y @insforge/cli db migrations up --all

# JSON output
npx -y @insforge/cli db migrations list --json
```

## Output

- `list` prints a table with version, name, and created date
- `fetch` reports how many files were created and skipped
- `new` prints the created filename
- `up` prints the applied filename(s) on success

## Command Behavior

### `list`

- Reads the current remote migration history from the project backend
- Shows only applied remote migrations

### `fetch`

- Ensures `migrations/` exists
- Writes one local `.sql` file per applied remote migration
- Skips existing file paths without overwriting them, even if the contents differ

### `new <migration-name>`

- Validates the migration name
- Looks at the latest remote migration version
- Validates local filenames before choosing the next timestamp version
- Uses the greater of current UTC time or the latest known local/remote version, bumping by one second when needed
- Fails if local migration filenames are malformed or duplicated

### `up <filename|version>`

- Resolves exactly one local file target
- Applies exactly one migration file
- The target must be the next pending local migration after the latest remote version
- Fails if the target is ambiguous, missing, empty, invalidly named, or already applied
- Unrelated invalid files elsewhere in `migrations/` do not block an explicit valid target

### `up --to <filename|version>`

- Strictly validates every local migration filename first
- Applies pending local migrations in ascending version order
- Stops after the chosen target migration is applied
- Fails if the target is missing, already applied, ambiguous, or not present in the pending set

### `up --all`

- Strictly validates every local migration filename first
- Applies every pending local migration in ascending version order
- Stops on the first failure

## Best Practices

1. **Use migrations for schema changes**
   - Migration SQL runs as `project_admin`.
   - `project_admin` can manage and own objects in `public`, but access to InsForge-managed schemas is restricted.
   - For generic application database work, create and evolve app-owned objects through migration files in `public`: tables, views, indexes, policies, triggers, helper functions, and grants.
   - Do not create custom schemas or write to InsForge-managed/system schemas such as `auth`, `storage`, `realtime`, `payments`, `graphql`, `extensions`, `pg_catalog`, `information_schema`, or `system`, unless you are working on that specific feature module and its docs explicitly allow the operation.
   - It is allowed to reference built-in objects such as `auth.users(id)` and `auth.uid()` from public tables or public RLS policies; do not modify those built-in objects.
   - Group related schema changes into one migration when practical.
   - Reserve `db query` for row-level data fixes, backfills, and targeted inspection.
   - Migration apply reloads the PostgREST schema cache automatically.
   - Migration SQL runs against `public`; schema-qualify references such as `public.posts` and `auth.uid()`.

2. **Normalize large JSONB payloads into columns or child tables**
   - Avoid designing tables where app code reads/writes large JSONB blobs through PostgREST; large JSONB rows can drive excessive PostgREST memory use.
   - Use typed columns for fields used in filters, sorting, list views, RLS policies, or partial updates.
   - Use child tables for repeated nested objects, with foreign keys and indexes on ownership/lookup columns.
   - Keep JSONB for small, rarely queried metadata/config where whole-object reads and writes are acceptable.

3. **Compare remote and local migration history**
   - Use `list` to see applied remote migrations.
   - Use `fetch` to sync applied remote migration files into `migrations/`.

4. **Use `new` instead of naming files by hand**
   - Let the CLI assign the next timestamp version safely.

5. **Use explicit single-target apply for focused changes**
   - `up <filename>` or `up <version>` is ideal when you want one specific migration.

6. **Use batch apply for CI or bootstrap**
   - `up --to <target>` or `up --all` is safer than hand-looping files in shell scripts because the CLI keeps ordering and fail-fast behavior consistent.

7. **Treat fetched files as history**
   - Once a migration is applied remotely, avoid editing its local file.

8. **Do not include transaction statements in migration files**
   - The backend executes each migration inside its own transaction.
   - Do not add `BEGIN`, `COMMIT`, or `ROLLBACK` to the migration SQL.

## Common Mistakes

| Mistake | Solution |
|---------|----------|
| Naming files manually with underscores or spaces | Use `npx -y @insforge/cli db migrations new <migration-name>` |
| Reaching for `db query` to create or alter schema | Use migration files for schema changes; reserve `db query` for row changes |
| Trying to alter InsForge-managed tables like app-owned tables | Keep generic schema, RLS, trigger, function, and grant changes on `public` application objects; use feature-specific docs for managed module hooks or RLS |
| Storing large app state or repeated nested objects in one JSONB column | Normalize into typed columns and child tables before exposing the table through SDK/PostgREST CRUD |
| Applying a file out of order | Apply the next pending local migration, or fix/delete the earlier local file that is blocking it |
| Keeping a local file older than the current remote head | Rename it with a newer timestamp or delete it locally if it is stale |
| Adding `BEGIN` / `COMMIT` / `ROLLBACK` to migration SQL | Remove them; the backend already wraps the migration in its own transaction |
| Editing already-fetched remote history casually | Treat fetched files as applied history, not drafts |
| Assuming `fetch` overwrites local files | `fetch` skips existing file paths instead of replacing them |

## Recommended Workflow

```text
1. Check remote history             → npx -y @insforge/cli db migrations list
2. Sync applied files when useful   → npx -y @insforge/cli db migrations fetch
3. Create the next migration file   → npx -y @insforge/cli db migrations new <migration-name>
4. Edit the SQL file                → migrations/<version>_<migration-name>.sql
5. Apply the migration              → npx -y @insforge/cli db migrations up <filename> or --all
6. If apply fails, read the error, fix the migration, and retry the migration.
```
