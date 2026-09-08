# npx -y @insforge/cli branch merge

Merge a branch's schema, config, and data-level changes back into the parent.

## Syntax

```bash
npx -y @insforge/cli branch merge <name> [options]
```

## Options

| Option              | Default | Description                                                                   |
| ------------------- | ------- | ----------------------------------------------------------------------------- |
| `--dry-run`         | off     | Compute the diff and print rendered SQL; do not apply.                        |
| `-y, --yes`         | off     | Skip the "are you sure" confirmation when applying.                           |
| `--save-sql <path>` | —       | Write the rendered SQL preview to a file (works with or without `--dry-run`). |

Inherits `--json` and `--api-url`.

## Always run `--dry-run` first

The dry run prints a migration-style SQL preview, organized by section:

```sql
-- Generated 2026-04-29T12:00:00Z
BEGIN;

-- ===== MIGRATION =====
-- [MIGRATION] migration system.060 (add)
-- Migration 060: add_visibility_to_posts
ALTER TABLE public.posts ADD COLUMN visibility TEXT NOT NULL DEFAULT 'private';
INSERT INTO "system"."custom_migrations" ("version", "name", "statements", "created_at") VALUES (...)
  ON CONFLICT ("version") DO UPDATE SET ...;

-- ===== DATA =====
-- [DATA] config_row email.templates (modify)
INSERT INTO "email"."templates" ("template_type", "subject", ...) VALUES (...)
  ON CONFLICT ("template_type") DO UPDATE SET "subject" = EXCLUDED."subject", ...;

COMMIT;
```

Read it. If anything looks wrong, do **not** run merge without `--dry-run`.

## Merge order (matters)

The cloud-backend orders the SQL such that:

1. **Migrations** (DDL via `system.custom_migrations.statements[]`) run first, so any newly added tables/columns exist when data lands.
2. **Config rows** (UPSERTs into the 13 mergeable matrix tables) and **edge functions** (UPSERTs into `functions.definitions`) run second.

The whole script is wrapped in `BEGIN; … COMMIT;` — any failure rolls the parent's PG back to the pre-merge state, and `branch_state` flips from `merging` back to `ready`.

## Conflicts

If the cloud-backend reports `branch.merge_conflict` (HTTP 409), the
preview SQL is prefixed with:

```sql
-- ⚠️ MERGE BLOCKED: 1 conflict(s) detected. Resolve before applying.
--
-- [CONFLICT] table public.users
--   parent_t0_hash:  <hash>
--   parent_now_hash: <different hash>
--   branch_now_hash: <different hash>
--   hint: Both parent and branch modified this object after branch creation. Resolve manually.
```

The CLI exits with code **2** (distinct from the generic error exit 1).

### Resolution steps

1. Inspect parent's current state and branch's current state for the conflicted object (e.g. `npx -y @insforge/cli db tables` / `db policies`).
2. Decide which version to keep:
   - **Keep parent**: revert the branch's change (drop the column on branch, etc.) and run `branch merge --dry-run` again.
   - **Keep branch**: forcibly apply the branch's version on parent (manually), then merge — auto-merge will see no conflict because parent_now will match branch_now.
   - **Hand-merge**: write a manual migration that combines both intents, apply it on the branch, then merge.
3. Re-run `branch merge <name> --dry-run` to confirm zero conflicts, then run without `--dry-run`.

## What gets auto-applied

The full v1 matrix, by `(diff type, action)`. The user-schema DDL paths (`table` / `policy` / `function`) replay introspected SQL — you don't have to wrap every change in a `system.custom_migrations` entry, though doing so is still the safest option for complex changes.

| Type                                      | `add`                                                                                                                                                 | `modify`                                                                                                                                                                                 | `drop`                                                                                                                       |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `config_row` (13 mergeable tables)        | ✅ UPSERT keyed on the matrix conflict column, respecting `excludeColumns` / `excludeKeys` (e.g. OAuth `client_secret` is filtered out)               | ✅ same as `add` — UPSERT replaces the row                                                                                                                                               | ❌ **skip** — never auto-`DELETE` from parent. Drop it manually if intended.                                                 |
| `edge_function` (`functions.definitions`) | ✅ UPSERT keyed on `slug`                                                                                                                             | ✅ same as `add`                                                                                                                                                                         | ❌ **skip** — delete the function on parent via dashboard or `cli functions delete`                                          |
| `migration` (`system.custom_migrations`)  | ✅ replays `statements[]` verbatim, then UPSERTs the migration row                                                                                    | —                                                                                                                                                                                        | ❌ **skip** — append-only by design                                                                                          |
| `table` (user schemas only)               | ✅ replays the introspected `CREATE TABLE IF NOT EXISTS …` (columns + inline constraints) plus `CREATE INDEX` for any captured indexes                | ❌ **skip** — column-level diff isn't implemented in v1. Workaround: write an `ALTER TABLE` in a `system.custom_migrations` entry on the branch — it lands via the `migration:add` path. | ✅ `DROP TABLE IF EXISTS schema.table CASCADE`                                                                               |
| `policy` (user-defined RLS)               | ✅ `DROP POLICY IF EXISTS … ; CREATE POLICY …` (the leading drop keeps it idempotent against the OSS `create_policies_on_table_create` event trigger) | ✅ same as `add` — rebuilds to the branch's current spec                                                                                                                                 | ✅ `DROP POLICY IF EXISTS …`                                                                                                 |
| `function` (user-defined PG functions)    | ✅ replays `pg_get_functiondef` (`CREATE OR REPLACE FUNCTION …`) — idempotent for both add and modify                                                 | ✅ same as `add`                                                                                                                                                                         | ✅ `DROP FUNCTION IF EXISTS schema.fn(arg-types)` — uses `pg_get_function_identity_arguments` so overloads resolve precisely |

**Row data on user tables is never auto-merged** — branches are not the source of truth for parent's user data. If you seeded rows into `public.*` tables on the branch and want them on parent, copy them manually after the merge (e.g. via `db query` or a one-off `db import`).

**All auto-apply SQL is idempotent** (`IF EXISTS` / `CREATE OR REPLACE` / UPSERT). This matters because OSS event triggers like `create_policies_on_table_create` will rebuild policies after the table:add step lands — the subsequent `policy:add` step then overwrites them with the branch's exact spec. You should not see drift after merge, but if you do, re-running merge is safe.

**Schemas covered by the DDL paths:** `public` and any user-defined schema. System schemas (`auth`, `storage`, `functions`, `email`, `ai`, `realtime`, `schedules`, `system`, `deployments`, `cron`) are gated by the mergeable matrix — DDL on them propagates only via `system.custom_migrations` append, never via `table` / `policy` / `function` diffs.

Skipped items are recorded in the `unsupported` line on the apply response.

## After the merge

The branch enters `merged` state — dormant, not destroyed. To layer further changes onto the same branch slot, [`branch reset`](reset.md) rewinds it to T0 and flips state back to `ready`.

**The merge does not redeploy code.** Re-run `functions deploy`, `deployments deploy`, and `compute update` for anything outside the database that depends on the new schema.

## Example

```bash
$ npx -y @insforge/cli branch merge feat-rls-fix --dry-run --save-sql /tmp/diff.sql
BEGIN;
…
COMMIT;
2 added, 1 modified, 0 conflict(s).

$ cat /tmp/diff.sql   # review the SQL with a human eye

$ npx -y @insforge/cli branch merge feat-rls-fix
2 added, 1 modified, 0 conflict(s).
? Apply this merge to parent project 'my-app'? › yes
✓ Merged. Branch 'feat-rls-fix' is now in 'merged' state.
⚠ Reminder: redeploy edge functions, website, and compute as needed.
```

## See also

- [branch overview](overview.md) — lifecycle commands and decision guide
- [branch reset](reset.md) — rewinding a branch to T0
