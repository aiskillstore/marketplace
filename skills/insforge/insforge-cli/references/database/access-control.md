# Database Access Control for InsForge

## Overview

Row Level Security (RLS) provides defense-in-depth for data isolation. When implemented correctly, it prevents data leaks even if application code misses a filter. When implemented incorrectly, it creates false security confidence while data bleeds between users or tenants.

**Core principle:** RLS is your last line of defense, not your only one. Get it wrong and you have a data breach.

---

## InsForge RLS Basics

InsForge uses three built-in PostgreSQL roles:

| Role | Description | When active |
|------|-------------|-------------|
| `anon` | Unauthenticated users | No valid session token |
| `authenticated` | Logged-in users | Valid session token present |
| `project_admin` | Project admin | CLI `db query`, migrations, API-key/admin tasks |

The current user's ID is available via `auth.uid()`. All user foreign keys should reference `auth.users(id)`.

Raw SQL from `db query` and migration files runs as `project_admin`. This role can manage and own objects in `public`; access to InsForge-managed schemas is restricted.

### Schema Scope and Managed Modules

For generic application database work, create and modify app-owned objects in the `public` schema.

- Create, alter, drop, grant, revoke, index, trigger, function, view, and policy changes on `public` application objects.
- Do not create custom schemas or write to InsForge-managed/system schemas such as `auth`, `storage`, `realtime`, `payments`, `graphql`, `extensions`, `pg_catalog`, `information_schema`, or `system`, unless you are working on that specific feature module and its docs explicitly allow the operation.
- It is allowed to reference built-in objects such as `auth.users(id)` and `auth.uid()` from public tables or public RLS policies; do not modify those built-in objects.
- Put RLS helper functions in `public`, schema-qualify references such as `public.team_members` and `auth.uid()`, and pin `SECURITY DEFINER` helpers to `SET search_path = pg_catalog, public, pg_temp`.
- InsForge migrations already run against `public`; schema-qualified references keep helper functions explicit.

Managed table RLS belongs to the corresponding storage, realtime, or payments feature context. Use those feature docs when the task is specifically about those modules.

### Minimal RLS Setup

```sql
-- 1. Create table
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 3. Create policies
CREATE POLICY "anyone can read" ON posts
  FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "owners can insert" ON posts
  FOR INSERT TO authenticated
  WITH CHECK (user_id = (SELECT auth.uid()));

CREATE POLICY "owners can update" ON posts
  FOR UPDATE TO authenticated
  USING (user_id = (SELECT auth.uid()))
  WITH CHECK (user_id = (SELECT auth.uid()));

CREATE POLICY "owners can delete" ON posts
  FOR DELETE TO authenticated
  USING (user_id = (SELECT auth.uid()));

-- 4. Grant SQL privileges to the roles that should pass through the policies
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON posts TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON posts TO authenticated;

-- 5. Auto-update updated_at
CREATE TRIGGER posts_updated_at
  BEFORE UPDATE ON posts
  FOR EACH ROW
  EXECUTE FUNCTION system.update_updated_at();
```

Policies decide which rows a role may access after PostgreSQL has allowed the SQL operation. They do not grant `SELECT`, `INSERT`, `UPDATE`, or `DELETE` privileges.

InsForge grants broad DML privileges on `public` tables to `anon` and
`authenticated` by default so RLS policies can decide row-level access. When the
goal is narrower than the default operation or column surface, explicitly revoke
the broad privilege before granting the exact access you want:

```sql
REVOKE UPDATE ON public.posts FROM anon, authenticated;
GRANT UPDATE (title) ON public.posts TO authenticated;
```

If you revoke a privilege, a matching policy is no longer enough by itself; the
role still needs the operation or column grant to reach the policy.

### Design the Operation Surface First

Before writing policies, decide what each runtime role may do at the SQL
operation level. RLS answers "which rows"; privileges and guards answer "which
operations and columns".

For each table, list:

| Operation | Typical access-control question |
|-----------|---------------------------------|
| `SELECT` | Who may see full rows, and who only sees a projection? |
| `INSERT` | Which user identity or tenant must new rows belong to? |
| `UPDATE` | Which rows may be edited, and which fields must remain immutable? |
| `DELETE` | Is deletion allowed, or should lifecycle state/soft delete be modeled? |

If an operation or field is narrower than InsForge's broad public-table runtime
privileges, revoke the broad privilege first, then grant back the exact surface.

### Guard Protected Fields Outside RLS Predicates

RLS policies filter candidate rows and validate the final row with `WITH CHECK`.
They do not compare old and new column values. PostgreSQL policy expressions do
not have `OLD` or `NEW`.

For protected fields such as `owner_id`, `tenant_id`, role columns, immutable
foreign keys, billing fields, or status fields, use column privileges and/or a
`BEFORE UPDATE` trigger guard. This keeps invariants true even if a future policy
or grant becomes broader.

```sql
REVOKE UPDATE ON public.documents FROM anon, authenticated;
GRANT UPDATE (title, body) ON public.documents TO authenticated;

CREATE OR REPLACE FUNCTION public.prevent_document_owner_change()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.owner_id IS DISTINCT FROM OLD.owner_id THEN
    RAISE EXCEPTION 'owner_id cannot be changed';
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER prevent_document_owner_change
BEFORE UPDATE ON public.documents
FOR EACH ROW EXECUTE FUNCTION public.prevent_document_owner_change();
```

For field-level update masks such as "members may edit content, managers may
edit status, finance may edit billing code", use a `BEFORE UPDATE` trigger to
compare `OLD` and `NEW`; use RLS to decide whether the caller can reach the row.

### Model ACLs as Positive Capabilities

For owner/editor/viewer/member sharing systems, avoid one broad `FOR ALL`
policy. Write separate policies for each operation and express the positive
capability needed for that operation.

- `SELECT`: owner or active read/edit share.
- `UPDATE`: owner or active edit share, with protected owner/tenant fields
  guarded separately.
- `DELETE`: usually owner/admin only.
- Share mutation: usually owner/admin only; viewers and editors should not
  reshare, revoke, or escalate themselves unless that is explicitly intended.

Cross-table ACL lookups commonly touch RLS-enabled tables. Put those lookups in
`SECURITY DEFINER` helpers, pin their `search_path`, and schema-qualify
referenced objects.

### Separate Private Base Tables from Public Projections

When a table contains private JSON, billing fields, internal notes, or other
sensitive columns, keep full-row base-table access narrow. Expose public data
through a view or function that projects only safe fields.

Do not make the base table readable by everyone just to make a public view work.
That exposes the full row through direct table reads. If callers need a public
projection, design the projection explicitly and grant access to the projection,
not the private base table.

`WITH (security_invoker = true)` makes a PostgreSQL 15+ view respect the caller's
RLS on the base tables. Use it when the base-table RLS already allows the rows
the view should expose. If the public projection intentionally exposes a subset
of fields from rows whose full base rows are private, use a carefully projected
view/function and keep direct base-table privileges and policies narrow.

---

## Critical Vulnerabilities

### 1. Infinite Recursive RLS (CRITICAL — Causes OOM Crash)

**This is the most dangerous RLS bug.** When RLS policies on table A call a function that queries table B, and table B's RLS calls a function that queries table A (or itself), PostgreSQL enters infinite recursion until the server runs out of memory and is killed by the OS.

**Real-world example:**

```
companies → is_company_member() → queries company_memberships
                                     → RLS on company_memberships
                                     → is_company_consultant_or_admin()
                                     → company_role()
                                     → queries company_memberships (LOOP!)
                                     → OOM → SIGKILL
```

**How to detect:**
- Database connection hangs, then the server crashes
- PostgreSQL logs show `SIGKILL` or out-of-memory errors
- `EXPLAIN` on the query runs forever

**The fix — use SECURITY DEFINER:**

```sql
-- DANGEROUS: This function runs as the calling role, so RLS is enforced
-- on every table it touches — creating recursion risk
CREATE OR REPLACE FUNCTION is_company_member(company_uuid UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM company_memberships
    WHERE company_id = company_uuid AND user_id = auth.uid()
  );
$$ LANGUAGE sql STABLE;

-- SAFE: SECURITY DEFINER runs as the function owner (postgres),
-- bypassing RLS on queried tables and breaking the recursion
CREATE OR REPLACE FUNCTION is_company_member(company_uuid UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.company_memberships
    WHERE company_id = company_uuid AND user_id = auth.uid()
  );
$$ LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = pg_catalog, public, pg_temp;
```

**Rule: Any helper function called from an RLS policy should be `SECURITY DEFINER`** when it queries RLS-enabled tables. This includes same-table lookups, parent/ancestor lookups, membership tables, ACL/share tables, and helper chains that would otherwise re-enter RLS. Keep helpers in `public`, use explicit schema-qualified references, and pin the function `search_path` to `pg_catalog, public, pg_temp`.

**Checklist:**
- [ ] Map all RLS policy → function → table dependencies
- [ ] Every policy helper that queries RLS-enabled tables, including same-table lookups, is `SECURITY DEFINER`
- [ ] Every `SECURITY DEFINER` helper sets `search_path` to `pg_catalog, public, pg_temp`
- [ ] Helper functions and policies schema-qualify app tables/functions with `public.` and built-ins with their managed schema, such as `auth.uid()`
- [ ] No circular chains: table A RLS → table B RLS → table A RLS
- [ ] If recursion or bad plans are suspected, use targeted `EXPLAIN`

### 2. Missing USING or WITH CHECK (HIGH)

`USING` filters reads; `WITH CHECK` validates writes. Missing `WITH CHECK` allows inserting rows you can't read back.

```sql
-- INCOMPLETE: User can INSERT rows for other users
CREATE POLICY "owner access" ON posts
  FOR ALL USING (user_id = auth.uid());

-- COMPLETE: Both read and write protected
CREATE POLICY "owner access" ON posts
  FOR ALL
  USING (user_id = (SELECT auth.uid()))
  WITH CHECK (user_id = (SELECT auth.uid()));
```

**Checklist:**
- [ ] INSERT/UPDATE policies always include `WITH CHECK`
- [ ] `FOR ALL` policies include both `USING` and `WITH CHECK`

### 3. Overly Permissive Policies (HIGH)

Multiple policies on the same table are combined with OR. One overly broad policy defeats all others.

```sql
-- DANGEROUS: This single policy overrides all restrictions
CREATE POLICY "allow all reads" ON orders
  FOR SELECT USING (true);

CREATE POLICY "tenant isolation" ON orders
  FOR SELECT USING (tenant_id = (SELECT auth.uid()));
-- ^ This is useless — the first policy already allows everything
```

**Checklist:**
- [ ] Audit all policies per table — they combine with OR
- [ ] No `USING (true)` on sensitive tables unless intentional (e.g., public blog posts)

### 4. View Bypass (MEDIUM)

Views run with the creator's privileges by default.

```sql
-- DANGEROUS: View owned by superuser bypasses RLS
CREATE VIEW all_orders AS SELECT * FROM orders;

-- SAFE (PostgreSQL 15+): Respects caller's RLS
CREATE VIEW user_orders
WITH (security_invoker = true)
AS SELECT * FROM orders;
```

---

## Performance Considerations

### Index Policy Columns

Every column referenced in an RLS policy should be indexed:

```sql
CREATE INDEX idx_posts_user_id ON posts(user_id);
```

### Wrap Functions in Subqueries

Functions called per-row are expensive. Wrap in a subquery for single evaluation:

```sql
-- SLOW: auth.uid() called per row
CREATE POLICY "owner access" ON posts
  USING (user_id = auth.uid());

-- FASTER: Evaluated once
CREATE POLICY "owner access" ON posts
  USING (user_id = (SELECT auth.uid()));
```

### Use SECURITY DEFINER for Cross-Table Checks

Avoid RLS-on-RLS chains (see Infinite Recursive RLS above). Wrap cross-table lookups in `SECURITY DEFINER` functions:

```sql
CREATE OR REPLACE FUNCTION user_accessible_document_ids(uid UUID)
RETURNS SETOF UUID AS $$
  SELECT document_id FROM public.permissions WHERE user_id = uid;
$$ LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = pg_catalog, public, pg_temp;

CREATE POLICY "access check" ON documents
  USING (id IN (SELECT * FROM user_accessible_document_ids((SELECT auth.uid()))));
```

### Denormalize for Performance

Store `user_id` or `tenant_id` directly on every table instead of relying on joins:

```sql
-- SLOW: Must join to resolve ownership
CREATE POLICY "item access" ON order_items
  USING (order_id IN (
    SELECT id FROM orders WHERE user_id = auth.uid()
  ));

-- FAST: Direct column check
ALTER TABLE order_items ADD COLUMN user_id UUID REFERENCES auth.users(id);
CREATE POLICY "item access" ON order_items
  USING (user_id = (SELECT auth.uid()));
```

---

## Common InsForge RLS Patterns

### Public Read, Owner Write

```sql
CREATE POLICY "public read" ON posts
  FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "owner write" ON posts
  FOR INSERT TO authenticated
  WITH CHECK (user_id = (SELECT auth.uid()));

CREATE POLICY "owner update" ON posts
  FOR UPDATE TO authenticated
  USING (user_id = (SELECT auth.uid()))
  WITH CHECK (user_id = (SELECT auth.uid()));

CREATE POLICY "owner delete" ON posts
  FOR DELETE TO authenticated
  USING (user_id = (SELECT auth.uid()));

GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON posts TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON posts TO authenticated;
```

### Role-Based Access with Helper Function

```sql
CREATE OR REPLACE FUNCTION is_org_member(org_uuid UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.org_members
    WHERE org_id = org_uuid AND user_id = auth.uid()
  );
$$ LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = pg_catalog, public, pg_temp;  -- prevents recursive RLS and pins name resolution

CREATE POLICY "org members access" ON projects
  FOR ALL TO authenticated
  USING (is_org_member(org_id))
  WITH CHECK (is_org_member(org_id));

GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON projects TO authenticated;
```

### Authenticated-Only Access

```sql
CREATE POLICY "authenticated users only" ON profiles
  FOR SELECT TO authenticated
  USING ((SELECT auth.uid()) IS NOT NULL);

GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT ON profiles TO authenticated;
```

---

## Checklist

Before completing an RLS implementation:

- [ ] All tables with user data have `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`
- [ ] Matching SQL privileges are granted to `anon`/`authenticated` (`GRANT USAGE ON SCHEMA ...`, `GRANT SELECT/INSERT/UPDATE/DELETE ON ...`)
- [ ] All policies have both `USING` and `WITH CHECK` where applicable
- [ ] Protected owner, tenant, role, and identity fields are guarded with column privileges or triggers, not only RLS predicates
- [ ] No circular RLS dependencies between tables (infinite recursion risk)
- [ ] All policy helpers that query RLS-enabled tables are `SECURITY DEFINER`
- [ ] Helper functions pin `search_path` to `pg_catalog, public, pg_temp`
- [ ] Helper functions and policies use explicit `public.` and managed-schema references instead of relying on `search_path`
- [ ] Broad default table privileges are revoked before narrower operation or column grants
- [ ] Policy columns (`user_id`, `tenant_id`, etc.) are indexed
- [ ] `(SELECT auth.uid())` used in subquery form for performance
- [ ] Public projections do not expose private base-table rows; view/function grants are separated from full table access
- [ ] No overly permissive `USING (true)` on sensitive tables
- [ ] Runtime behavior is not inferred from `project_admin`-only queries

## References

- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [SECURITY DEFINER Functions](https://www.postgresql.org/docs/current/sql-createfunction.html)
