# Storage Row Level Security (RLS) for InsForge

## Overview

InsForge governs `storage.objects` with PostgreSQL Row Level Security, not with app-side `WHERE uploaded_by = $1` filters. A signed-in caller runs as `authenticated` with their JWT `sub` available via `auth.jwt() ->> 'sub'`. Admin/API-key callers bypass RLS for admin workflows.

**Core principle:** Policies are the contract. The user API does the cheapest possible thing on top of them — it does not re-implement authorization.

---

## InsForge Storage RLS Basics

| Role | Description | When active |
|------|-------------|-------------|
| `anon` | Unauthenticated callers | No valid session token |
| `authenticated` | Logged-in end users | Valid session token in the request |

The `auth.jwt()` helper returns the caller's full claims as `jsonb`. Most policies use `auth.jwt() ->> 'sub'` for ownership checks, but you can read any claim — `->> 'role'`, `->> 'org_id'`, custom claims from third-party providers (Better Auth, Clerk, Auth0, WorkOS, Stytch, Kinde).

### What ships by default

- **Fresh installs**: zero policies on `storage.objects` and RLS **disabled** (since migration 047). Policies you create stay dormant until RLS is enabled — always include `ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;` in your policy migration, or the table grants let any authenticated user read every row.
- **Existing projects** (any rows in `storage.buckets` at migration time): the owner-only set below is auto-installed so the upgrade does not silently break end-user uploads and reads.

### Managed Storage RLS

Allowed managed storage policy tables:

- `storage.objects`

Put `storage.objects` policy changes in a custom migration. This managed storage table can be managed with RLS.

### Path helpers shipped with InsForge

```sql
storage.foldername(name)   -- text[] of folders, e.g. {alice, photos}
storage.filename(name)     -- last segment, e.g. 'cat.jpg'
storage.extension(name)    -- 'jpg' from 'alice/photos/cat.jpg'
```

### Inspecting current policies

```sql
SELECT polname, polcmd,
       pg_get_expr(polqual,     polrelid) AS using_clause,
       pg_get_expr(polwithcheck, polrelid) AS check_clause
FROM pg_policy
WHERE polrelid = 'storage.objects'::regclass;
```

Check whether RLS is actually enabled — policies are dormant while this is `false`:

```sql
SELECT relrowsecurity FROM pg_class WHERE oid = 'storage.objects'::regclass;
```

### Removing the auto-installed defaults

When you want a different shape on a bucket the defaults don't fit:

```sql
DROP POLICY IF EXISTS storage_objects_owner_select ON storage.objects;
DROP POLICY IF EXISTS storage_objects_owner_insert ON storage.objects;
DROP POLICY IF EXISTS storage_objects_owner_update ON storage.objects;
DROP POLICY IF EXISTS storage_objects_owner_delete ON storage.objects;
```

---

## Pattern: Owner-only Bucket

**Use when:** Each user only sees, modifies, or deletes their own files. This is the default that ships auto-installed for existing projects.

| Caller | SELECT | INSERT | UPDATE | DELETE |
|--------|--------|--------|--------|--------|
| Owner of the row | ✓ | ✓ (must set `uploaded_by = sub`) | ✓ | ✓ |
| Other authenticated user | ✗ (404) | ✓ for own rows | ✗ | ✗ |
| Anonymous (`anon`) | ✗ | ✗ | ✗ | ✗ |
| Admin | ✓ bypass | ✓ bypass | ✓ bypass | ✓ bypass |

```sql
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

CREATE POLICY storage_objects_owner_select ON storage.objects
  FOR SELECT TO authenticated
  USING (uploaded_by = (SELECT auth.jwt() ->> 'sub'));

CREATE POLICY storage_objects_owner_insert ON storage.objects
  FOR INSERT TO authenticated
  WITH CHECK (uploaded_by = (SELECT auth.jwt() ->> 'sub'));

CREATE POLICY storage_objects_owner_update ON storage.objects
  FOR UPDATE TO authenticated
  USING      (uploaded_by = (SELECT auth.jwt() ->> 'sub'))
  WITH CHECK (uploaded_by = (SELECT auth.jwt() ->> 'sub'));

CREATE POLICY storage_objects_owner_delete ON storage.objects
  FOR DELETE TO authenticated
  USING (uploaded_by = (SELECT auth.jwt() ->> 'sub'));

GRANT SELECT, INSERT, UPDATE, DELETE ON storage.objects TO authenticated;
GRANT USAGE ON SCHEMA storage TO authenticated;
```

---

## Pattern: Public-read Bucket

**Use when:** Anyone (signed in or anonymous) should read files in the bucket, but only the owner can write or delete. Photo galleries, public assets, marketing content, user avatars served to everyone.

| Caller | SELECT | INSERT | UPDATE | DELETE |
|--------|--------|--------|--------|--------|
| Owner of the row | ✓ | ✓ | ✓ | ✓ |
| Other authenticated user | ✓ | ✗ | ✗ | ✗ |
| Anonymous (`anon`) | ✓ | ✗ | ✗ | ✗ |

```sql
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS storage_objects_owner_select ON storage.objects;

CREATE POLICY storage_objects_public_read ON storage.objects
  FOR SELECT TO authenticated, anon
  USING (bucket = 'photos');

-- Writes / mutations stay owner-only (same as the owner-only pattern)

GRANT SELECT ON storage.objects TO anon;
GRANT USAGE ON SCHEMA storage TO anon;
```

Marking the bucket `public` does more than fast-path routing: direct object GETs on a public bucket are served with root access and **bypass `storage.objects` RLS entirely** — an anon SELECT policy does not gate those downloads. RLS still scopes list and metadata queries made through the user API, but it cannot restrict who fetches an object URL from a public bucket. Only mark a bucket `public` when every object in it may be world-readable. If visibility is conditional (e.g. files attached to draft content that becomes readable on publish), keep the bucket private and mint signed URLs after an RLS-scoped check — see Caveats below.

---

## Pattern: Path-scoped Bucket

**Use when:** Each user owns a folder named after their `sub`, and the first path segment encodes ownership. Slack-style file URLs (`<user_id>/2024/photo.png`), per-user document trees.

```sql
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS storage_objects_owner_select ON storage.objects;
DROP POLICY IF EXISTS storage_objects_owner_insert ON storage.objects;
DROP POLICY IF EXISTS storage_objects_owner_update ON storage.objects;
DROP POLICY IF EXISTS storage_objects_owner_delete ON storage.objects;

CREATE POLICY storage_objects_path_select ON storage.objects
  FOR SELECT TO authenticated
  USING (
    bucket = 'user-files'
    AND (storage.foldername(key))[1] = (SELECT auth.jwt() ->> 'sub')
  );

CREATE POLICY storage_objects_path_insert ON storage.objects
  FOR INSERT TO authenticated
  WITH CHECK (
    bucket = 'user-files'
    AND (storage.foldername(key))[1] = (SELECT auth.jwt() ->> 'sub')
  );

CREATE POLICY storage_objects_path_update ON storage.objects
  FOR UPDATE TO authenticated
  USING      (bucket = 'user-files' AND (storage.foldername(key))[1] = (SELECT auth.jwt() ->> 'sub'))
  WITH CHECK (bucket = 'user-files' AND (storage.foldername(key))[1] = (SELECT auth.jwt() ->> 'sub'));

CREATE POLICY storage_objects_path_delete ON storage.objects
  FOR DELETE TO authenticated
  USING (
    bucket = 'user-files'
    AND (storage.foldername(key))[1] = (SELECT auth.jwt() ->> 'sub')
  );
```

A key with no `/` returns an empty array from `storage.foldername`, so `[1]` is NULL and the row is invisible to everyone except admin. If you want bucket-root files allowed, add `OR (storage.foldername(key))[1] IS NULL` to the relevant clause.

---

## Pattern: Team-shared Bucket

**Use when:** Files belong to teams / workspaces / organizations rather than individual users. Members of a team can read and write files attributed to that team; non-members can't see them.

The team-id is encoded as the first path segment (`<team_id>/<file>`). A membership table maps users to teams.

```sql
CREATE TABLE IF NOT EXISTS team_members (
  team_id UUID NOT NULL,
  user_id TEXT NOT NULL,            -- TEXT so third-party auth subs work
  role    TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner','admin','member')),
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (team_id, user_id)
);

CREATE INDEX IF NOT EXISTS team_members_user_idx ON team_members (user_id);

ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS storage_objects_owner_select ON storage.objects;
-- (drop the rest of the owner-only set too)

CREATE POLICY storage_objects_team_select ON storage.objects
  FOR SELECT TO authenticated
  USING (
    bucket = 'team-files'
    AND EXISTS (
      SELECT 1 FROM team_members
      WHERE team_members.team_id::text = (storage.foldername(key))[1]
        AND team_members.user_id      = (SELECT auth.jwt() ->> 'sub')
    )
  );

CREATE POLICY storage_objects_team_insert ON storage.objects
  FOR INSERT TO authenticated
  WITH CHECK (
    bucket = 'team-files'
    AND uploaded_by = (SELECT auth.jwt() ->> 'sub')
    AND EXISTS (
      SELECT 1 FROM team_members
      WHERE team_members.team_id::text = (storage.foldername(key))[1]
        AND team_members.user_id      = (SELECT auth.jwt() ->> 'sub')
    )
  );

-- UPDATE/DELETE: only the original uploader. Loosen for team admins as needed.
CREATE POLICY storage_objects_team_update ON storage.objects
  FOR UPDATE TO authenticated
  USING      (uploaded_by = (SELECT auth.jwt() ->> 'sub'))
  WITH CHECK (uploaded_by = (SELECT auth.jwt() ->> 'sub'));

CREATE POLICY storage_objects_team_delete ON storage.objects
  FOR DELETE TO authenticated
  USING (uploaded_by = (SELECT auth.jwt() ->> 'sub'));
```

For "admins can delete anything in their team" semantics, replace the DELETE policy's `uploaded_by =` check with a membership lookup that requires `role IN ('owner','admin')`.

---

## Pattern: Mixed REST + S3 Surfaces

InsForge exposes two write surfaces against the same `storage.objects` table:

| Surface | Who calls it | `uploaded_by` set to |
|---------|--------------|----------------------|
| `/api/storage/...` REST | A signed-in end user, JWT in the request | The caller's `sub` |
| `/storage/v1/s3/...` S3 protocol | An AWS-SDK / `aws-cli` client with an InsForge S3 access key | `NULL` |

Under the default owner-only SELECT policy, `NULL = '<sub>'` is never true (SQL three-valued logic), so **end users cannot see S3-uploaded rows through the user API**. Admin/API-key callers bypass RLS and see everything. The S3 surface itself doesn't run RLS — it uses admin credentials by design.

When the S3 gateway overwrites a key that a REST user previously owned, the platform preserves `uploaded_by` — it does not clobber to NULL. That part is automatic.

If end users need to see S3-uploaded rows, expose them explicitly:

```sql
DROP POLICY IF EXISTS storage_objects_owner_select ON storage.objects;

CREATE POLICY storage_objects_visible_select ON storage.objects
  FOR SELECT TO authenticated
  USING (
    bucket = 'shared-content'
    AND (
      uploaded_by IS NULL                                 -- S3-uploaded rows
      OR uploaded_by = (SELECT auth.jwt() ->> 'sub')      -- caller's own rows
    )
  );
```

If your S3 ingester needs to attribute ownership instead, run an admin-side `UPDATE storage.objects SET uploaded_by = $sub WHERE bucket = $1 AND key = $2 AND uploaded_by IS NULL;` after the upload — admin bypasses RLS so the UPDATE just works.

The cleanest answer is often to put REST-served and S3-served files in separate buckets so the `NULL = sub` foot-gun never comes up.

---

## Performance Best Practices

### Hoist `auth.jwt()` into a subquery

Without the `(SELECT ...)` wrap, `auth.jwt()` re-evaluates per row and list queries get slow:

```sql
-- SLOW: auth.jwt() called per row
USING (uploaded_by = auth.jwt() ->> 'sub')

-- FASTER: evaluated once per query
USING (uploaded_by = (SELECT auth.jwt() ->> 'sub'))
```

### Index the columns RLS reads

`storage.objects` already has indexes on `(bucket, key)` and `uploaded_by`. If you write path-based policies, a functional index on `(storage.foldername(key))[1]` helps for buckets with millions of objects. For team-shared buckets, the `team_members(user_id)` index from the schema is the one that gates request latency.

### Don't write app-side filters on top of RLS

Adding `WHERE uploaded_by = $1` in your service code on top of the RLS policy duplicates work and often hides bugs. Trust the policy; let RLS handle authorization.

---

## Caveats

- **Per-operation policies are independent.** A permissive SELECT does NOT grant DELETE. The reverse is also true. Audit each of the four operations separately.
- **Permissive vs restrictive policies.** Multiple matching policies OR together by default. If you want AND behavior, use `AS RESTRICTIVE`. Most storage policies are permissive (default).
- **Public buckets bypass RLS on downloads.** When `storage.buckets.public` is true, the object-visibility check runs with root access: anonymous GETs of object URLs succeed even if a SELECT policy would deny the row. RLS on `storage.objects` still scopes list/metadata queries through the user API, but it never gates direct downloads from a public bucket. Conditionally-visible files (drafts, gated content) belong in a private bucket with signed URLs issued only after your RLS or app-level check passes.
- **Out-of-band URLs bypass RLS.** Presigned S3 URLs and signed download links are redeemed against the storage backend directly — RLS does not fire on those redemptions. The platform code does an explicit RLS-scoped existence check before issuing the URL; if you build your own signed-URL flow, do the same.
- **Admin always sees everything.** RLS only applies to `authenticated` and `anon`. API-key callers and dashboard inspectors bypass policies regardless of which pattern you pick.

---

## Checklist

Before shipping a storage RLS configuration, apply `storage.objects` policy changes with a custom migration.

- [ ] `ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY` is in your policy migration — fresh installs ship with RLS disabled (since migration 047), and the statement is idempotent, so always include it. Verify with `SELECT relrowsecurity FROM pg_class WHERE oid = 'storage.objects'::regclass;`
- [ ] Policies target `storage.objects`
- [ ] All four operations (SELECT, INSERT, UPDATE, DELETE) have policies — or you've consciously decided to deny one
- [ ] `auth.jwt() ->> 'sub'` is wrapped in `(SELECT ...)` for performance
- [ ] `GRANT SELECT, INSERT, UPDATE, DELETE ON storage.objects TO authenticated` (and `anon` if your pattern allows it)
- [ ] `GRANT USAGE ON SCHEMA storage TO authenticated` (and `anon` if applicable)
- [ ] Buckets marked `public` contain only world-readable objects — direct GETs on a public bucket skip RLS, so conditionally-visible files live in a private bucket with signed URLs
- [ ] Mixed REST + S3 buckets either (a) live in separate buckets, (b) include `uploaded_by IS NULL OR ...` in the SELECT policy, or (c) attribute ownership in an admin-side UPDATE after S3 ingest
- [ ] Tested as `authenticated`, not as superuser/admin — `psql` by default connects with elevated rights

## References

- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Database access-control CLI reference](../../insforge-cli/references/database/access-control.md) — patterns for application tables, helper-function tricks, infinite-recursion gotchas
