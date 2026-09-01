# Policies

Active RLS (Row-Level Security) rules pulled from Postgres's `pg_policies` system view. The primary primitive for **what RLS is currently allowing or denying** — distinct from "what config we *meant* to deploy" (that lives in [metadata](metadata.md) / migration history).

## Command

```bash
npx -y @insforge/cli db policies
```

Returns every policy: table, schema, policy name, command (`SELECT` / `INSERT` / `UPDATE` / `DELETE` / `ALL`), target role, `USING` expression, `WITH CHECK` expression.

Only specific InsForge-managed tables allow developer RLS changes. Check the relevant module skill or CLI reference before writing policy SQL for a managed table. If that table is listed as allowing RLS changes, normal RLS operations are allowed and should go in migrations.

## Policy anatomy

| Field | Meaning |
|-------|---------|
| `tablename` | Which table the policy applies to |
| `cmd` | Which operation it gates (read/write/all) |
| `roles` | Which DB roles the policy applies to (typically `authenticated`, `anon`, `public`) |
| `qual` (USING) | Filter expression: **which existing rows the role can see/modify**. Applied to `SELECT`, `UPDATE`, `DELETE`. |
| `with_check` | Validation expression: **which new/modified rows are allowed**. Applied to `INSERT`, `UPDATE`. |
| `permissive` / `restrictive` | Permissive policies OR together; restrictive AND. Most InsForge projects use permissive. |

## How to read

For "why was this request denied?":

1. Identify the table from the request URL (`/api/database/records/<table>`).
2. List policies for that table — note `cmd` and `roles`.
3. Walk the `USING` / `WITH CHECK` expressions against the actual request:
   - **No policy for that role+cmd combo** → denied by default. Need to add a policy.
   - **`USING` evaluates false for this row** → row is invisible / not modifiable. Confirm the helper (e.g., `auth.uid()` returns the expected user_id).
   - **`WITH CHECK` evaluates false on insert** → the new row's columns violate the policy. The insert payload is wrong, or the policy is too strict.

## Common RLS bug shapes

| Symptom | Likely cause |
|---------|-------------|
| All authenticated users see all rows (no isolation) | Policy is `USING (true)` — too permissive; restrict by `user_id` column |
| Authenticated user gets empty result on own data | Wrong helper function (`auth.uid()` returns UUID; if `user_id` column is TEXT from third-party auth, use `requesting_user_id()` instead) |
| Insert fails for owner with "new row violates RLS policy" | Missing `WITH CHECK` matching the `USING`, or `WITH CHECK` references columns not in payload |
| Third-party auth (Clerk/Auth0/etc.) users get blanket deny | Wrong helper (`auth.uid()` expects InsForge-issued JWT; third-party providers need `requesting_user_id()` with the right claim extraction) |
| Anonymous user can read sensitive table | RLS not enabled on the table (forgot `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`), or a policy applies to `public` / `anon` role without filter, or the connection is using a role with `BYPASSRLS` |

## Boundaries

- **Lists active policies, doesn't simulate.** Doesn't tell you "this specific request would be allowed" — combine with [logs](logs.md) (`postgREST.logs`) to see the actual denial event.
- **Doesn't include the helper function bodies.** `auth.uid()` / `requesting_user_id()` are SQL functions; inspect via `db query` if you need to verify they return what you expect.
- **Only listed managed tables allow RLS changes.** Check the relevant module skill or CLI reference before changing RLS on a managed table. If the table is listed, put normal RLS operations in [migrations](../../insforge-cli/references/database/migrations.md); keep normal schema changes in `public`.

## Example

User reports: "logged-in user gets 403 trying to `GET /api/database/records/posts`".

```bash
# 1. See the denial event
npx -y @insforge/cli logs postgREST.logs --limit 50

# 2. List policies on the posts table
npx -y @insforge/cli db policies

# 3. If the project uses third-party auth, verify the helper
npx -y @insforge/cli db query "SELECT requesting_user_id()"

# 4. Confirm the user's JWT contains the expected claim (auth config in metadata)
npx -y @insforge/cli metadata --json
```

## Frequently paired with

- [logs](logs.md) — `postgREST.logs` shows the actual RLS denial events; pair with policies to identify which rule fired
- [metadata](metadata.md) — auth config determines which claim feeds `auth.uid()` / `requesting_user_id()`
- [advisor](advisor.md) — security category often flags missing/overly-permissive RLS policies
