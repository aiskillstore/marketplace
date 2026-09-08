# Database Integrity

Use this reference when a migration must enforce database invariants: counters,
balances, latest pointers, append-only history, lifecycle states, quotas,
protected deletes, immutable ownership fields, or trigger-maintained columns.

DDL belongs in a migration. Use SQL constraints for row-local invariants, unique
indexes for uniqueness, foreign keys for references, and triggers only when the
rule depends on transitions, related rows, or server-maintained derived state.

## Choose the Smallest Database Primitive

| Need | Prefer |
|------|--------|
| Required field or valid range | `NOT NULL` / `CHECK` |
| Unique active value | partial unique index |
| Parent-child reference | foreign key plus index on the referencing column |
| Immutable owner or tenant | `BEFORE UPDATE` guard trigger |
| Append-only history | revoke client `UPDATE`/`DELETE`, plus optional guard trigger |
| Counter, balance, latest pointer, current status | trusted trigger-maintained derived field |
| Cross-row state transition | trigger or SQL function with clear transition checks |

## Server-Maintained Derived Fields

Derived fields include `comment_count`, `balance_cents`, `latest_revision_id`,
`current_status`, `last_event_at`, and similar values maintained by database
logic. Design them so normal client writes still work, but direct client edits
to the derived value do not.

Required shape:

1. A legal client can create the parent row with defaults, `NULL`, or zero for
   server-maintained fields.
2. A legal client can create the child/event row that should update the parent.
3. The trigger updates the derived parent field.
4. A client cannot directly update the derived field.
5. Guard triggers must not block the trusted maintenance path.

### Bad: Guard Blocks Its Own Maintenance Trigger

```sql
CREATE OR REPLACE FUNCTION public.protect_post_fields()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.comment_count IS DISTINCT FROM OLD.comment_count THEN
    RAISE EXCEPTION 'comment_count is server maintained';
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER protect_post_fields
BEFORE UPDATE ON public.posts
FOR EACH ROW EXECUTE FUNCTION public.protect_post_fields();

CREATE OR REPLACE FUNCTION public.bump_comment_count()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE public.posts
  SET comment_count = comment_count + 1
  WHERE id = NEW.post_id;
  RETURN NEW;
END;
$$;
```

The child insert fires `bump_comment_count`, which updates `posts`, which fires
`protect_post_fields`, which rejects the legitimate maintenance update.

### Good: Restrict Client Update Surface, Let Trigger Maintain

```sql
CREATE TABLE public.posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  comment_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID NOT NULL REFERENCES public.posts(id) ON DELETE CASCADE,
  author_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  body TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "owners can create posts"
ON public.posts FOR INSERT TO authenticated
WITH CHECK (owner_id = (SELECT auth.uid()));

CREATE POLICY "owners can edit post title"
ON public.posts FOR UPDATE TO authenticated
USING (owner_id = (SELECT auth.uid()))
WITH CHECK (owner_id = (SELECT auth.uid()));

GRANT SELECT, INSERT ON public.posts TO authenticated;
REVOKE UPDATE ON public.posts FROM authenticated;
GRANT UPDATE (title) ON public.posts TO authenticated;

CREATE OR REPLACE FUNCTION public.bump_comment_count()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, pg_temp
AS $$
BEGIN
  UPDATE public.posts
  SET comment_count = comment_count + 1
  WHERE id = NEW.post_id;
  RETURN NEW;
END;
$$;

CREATE TRIGGER comments_bump_post_count
AFTER INSERT ON public.comments
FOR EACH ROW EXECUTE FUNCTION public.bump_comment_count();
```

Here the client has no column privilege to update `comment_count` directly, but
the trusted trigger function can maintain it.

## Legal Insert Payloads

InsForge gives runtime roles broad default DML privileges on `public` tables so
RLS can decide row access. For integrity rules that narrow writes, explicitly
`REVOKE` broad privileges before adding column-level or operation-specific
`GRANT`s.

Column-level grants can accidentally block legitimate API payloads. Before using
column-level `INSERT` grants, list every column a normal SDK/REST caller may send.

Avoid this when callers may send `balance_cents: 0`:

```sql
GRANT INSERT (id, owner_id, name) ON public.accounts TO authenticated;
```

Prefer allowing the legal create payload and protecting later mutation:

```sql
GRANT SELECT, INSERT ON public.accounts TO authenticated;
REVOKE UPDATE ON public.accounts FROM authenticated;
GRANT UPDATE (name) ON public.accounts TO authenticated;
```

The same rule applies to `latest_revision_id = NULL`, `comment_count = 0`,
`current_status = 'draft'`, and other server-maintained initial values.

## Immutable Fields and Append-Only Tables

Guard fields that must never change after creation: `owner_id`, `tenant_id`,
business identifiers, immutable slugs, or ledger account IDs.

```sql
CREATE OR REPLACE FUNCTION public.prevent_owner_change()
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

CREATE TRIGGER prevent_owner_change
BEFORE UPDATE ON public.documents
FOR EACH ROW EXECUTE FUNCTION public.prevent_owner_change();
```

For append-only rows such as revisions, ledger entries, audit events, and claims:

```sql
REVOKE UPDATE, DELETE ON public.ledger_entries FROM authenticated;
GRANT SELECT, INSERT ON public.ledger_entries TO authenticated;
```

Add trigger guards only if privileged or future grants might otherwise mutate
history.

## Latest Pointer and History Pattern

For document revisions or status history, keep history append-only and maintain a
latest pointer on the parent.

```sql
CREATE OR REPLACE FUNCTION public.set_latest_revision()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, pg_temp
AS $$
BEGIN
  UPDATE public.documents
  SET latest_revision_id = NEW.id
  WHERE id = NEW.document_id;
  RETURN NEW;
END;
$$;

CREATE TRIGGER revisions_set_latest
AFTER INSERT ON public.document_revisions
FOR EACH ROW EXECUTE FUNCTION public.set_latest_revision();
```

Do not add a parent guard that rejects every `latest_revision_id` change unless
it also allows this trusted transition. The simpler pattern is to prevent client
updates to that column with privileges and let the trigger maintain it.

## Self-Check Before Finishing

- Can a legal parent insert pass with default, `NULL`, or zero derived values?
- Can a legal child/event insert pass?
- Does the child/event insert update the parent derived field?
- Is direct client mutation of derived fields blocked?
- Are immutable owner, tenant, and business identity fields protected?
- Are append-only child/history rows protected from update and delete?
- Do trigger functions that must bypass runtime privileges use `SECURITY DEFINER`
  with `SET search_path = pg_catalog, public, pg_temp` and schema-qualify
  references such as `public.documents`?
- Do RLS helpers that query RLS-enabled tables use `SECURITY DEFINER` and
  `SET search_path = pg_catalog, public, pg_temp`, then schema-qualify references
  such as `public.team_members` and `auth.uid()`?
- Are foreign keys and columns used by guards, RLS, and lookups indexed where
  the table can grow?
