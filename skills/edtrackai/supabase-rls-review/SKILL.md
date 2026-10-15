---
name: supabase-rls-review
description: Review Supabase SQL migrations for row level security gaps and missing or blanket Data API grants (tables without RLS, using (true) write policies, anon write policies, security definer functions without search_path, public tables with no explicit GRANT (Supabase's changelog schedules a grants change for 30 Oct 2026), blanket grants to anon/authenticated). Use when the user asks to review RLS, Supabase policies, grants, a 42501 error, or database security before launch.
allowed-tools: Read Grep Glob
---

# supabase-rls-review

Read-only review. Don't edit files unless the user asks for the fixes afterwards.

## Scope
Read every `.sql` file under `supabase/migrations/` (and any other `.sql` files the user points to), in filename order, so later migrations can fix earlier ones. Policies created in the Supabase dashboard aren't in these files: say so in the report instead of guessing.

## Checks
For each finding, give file:line, the check id, severity, and the fix.

| Id | Severity | Look for | Fix |
|---|---|---|---|
| R1 | critical | `create table` in `public` with no later `alter table ... enable row level security` | Enable RLS, then add policies scoped to `auth.uid()`. |
| R2 | critical | An `insert`/`update`/`delete`/`all` policy with `using (true)` or `with check (true)` | Scope it to the owner: `using (auth.uid() = user_id) with check (auth.uid() = user_id)`. |
| R3 | high | A write policy that applies to `anon` (`to anon`, or `to public` with no auth check) | Write policies go to `authenticated` only, scoped to `auth.uid()`. |
| R4 | high | `security definer` function with no `set search_path` | Add `set search_path = ''` and schema-qualify names, or use `security invoker`. |
| R5 | medium | A `public` table with no explicit per-table `grant` to the roles that use it | Supabase's changelog schedules a change for 30 Oct 2026 after which new `public` tables on existing projects get no automatic grants to `anon`/`authenticated`/`service_role`, so a table with no explicit `grant` returns `42501` from the Data API ([Supabase changelog](https://supabase.com/changelog/45329-breaking-change-tables-not-exposed-to-data-and-graphql-api-automatically)). Explicit grants are good practice either way. In the migration that creates the table, grant only what each role needs, e.g. `grant select on public.t to anon; grant select, insert, update, delete on public.t to authenticated, service_role;`, next to `enable row level security` and the policies. |
| R6 | high | `grant ... on all tables in schema public to anon/authenticated`, or `alter default privileges ... grant ... to anon/authenticated` | Replace with per-table grants. A blanket grant also exposes every table where RLS is off or policies are loose. Don't "fix" R5 this way. |

Per the changelog, tables that already exist keep their grants; R5 matters most for new tables. R5 is order-aware: a table counts as granted if a per-table grant, or an earlier blanket grant or default privilege, covers it. Report R6 for the blanket grant itself.

## Report
1. One line: how many migration files you read, and findings by severity.
2. A table: severity, id, file:line, what you saw, fix.
3. Anything you couldn't verify (dashboard policies, tables created outside migrations).

These are heuristics: each finding is a prompt to review, not proof of a vulnerability, and a clean result isn't proof the database is secure.
