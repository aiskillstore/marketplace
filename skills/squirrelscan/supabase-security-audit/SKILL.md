---
name: supabase-security-audit
description: "Audit a Supabase app with squirrelscan (the squirrel CLI or hosted squirrelscan MCP server) in Claude Code, GitHub Copilot, Codex, Cursor, and other coding agents to see if the public anon key can read tables with Row Level Security off or if a secret key shipped to the browser. After reading the repo and confirming project ownership, it runs audit rules that count rows with HEAD requests without reading data, then writes RLS SQL fixes. Use when asked \"is my Supabase app leaking data\", \"audit my Supabase RLS\", or \"check if my secret key is exposed\"."
license: See LICENSE file in repository root
compatibility: Requires the squirrel CLI installed and accessible in PATH, or the hosted squirrelscan MCP server connected
metadata:
  author: squirrelscan
  version: "0.1.3"
allowed-tools: Bash(squirrel:*) Read Edit Grep Glob
---

# Supabase Security Audit

Check whether a Supabase app lets the public anon key read tables it should not, and whether any secret key reached the browser.

A Supabase app ships its project URL and anon (publishable) key to every visitor on purpose. That is safe only when every table in an exposed schema has Row Level Security (RLS) turned on with policies that grant just what each role needs. Supabase's own docs warn that a table in an exposed schema without RLS is readable and writable by any role with a grant on it, and that a secret (service role) key bypasses RLS and must never leave your control.

## Before the first audit

Run `squirrel --version`. If it fails, install the CLI from [squirrelscan.com/download](https://squirrelscan.com/download) (the `squirrelscan` skill has `references/install.md`). Then run `squirrel auth status`:

- **Signed out, or `--offline`**: the audit runs on this machine, is free, and nothing is published.
- **Signed in**: the audit is billed in credits (50 plus 2 per audited page, plus 1 per distinct external link the cloud verifies), adds the site to the user's dashboard, can turn on recurring audits and publishes an unlisted report. Tell the user the cost (`squirrel credits`) and get a yes. Offer `--offline` or `--no-publish`. For a site the user does not own, add `--ephemeral`: nothing is added to the dashboard, scheduled or published.

Every flag below is checked against the squirrel CLI docs (https://docs.squirrelscan.com/cli/audit). Rule docs: `https://docs.squirrelscan.com/rules/{category}/{rule_id}`.

## Confirm ownership first

The probe sends the site's public anon key to the site's Supabase project, from the user's machine. Ask: "Is this your Supabase project, or are you authorized to test it?" If not, stop: do not run the probe. You can still read the code and report `leaked-secrets` passively.

## Step 1: read the code (no network)

If the repo is available, search it before auditing:

- Secret keys in client code: `service_role`, `sb_secret_`, `SUPABASE_SERVICE_ROLE_KEY` used in a file that ships to the browser (`NEXT_PUBLIC_*`, Vite `VITE_*`, `PUBLIC_*`, anything under `src/` of an SPA). A secret key in the browser is an incident: rotate it first.
- Every table the client queries: `.from("<table>")`, `/rest/v1/<table>`. This is the list the audit will probe.
- Migrations: `alter table ... enable row level security` for each of those tables, and `create policy` statements.

## Step 2: run the probe

```bash
squirrel audit https://app.example.com --level surface --aggressive --probe-budget 1m \
  --rule-include security/supabase-rls,security/leaked-secrets --format json -o supabase.json
```

How the rule works (https://docs.squirrelscan.com/rules/security/supabase-rls):

- It finds the project URL and anon key in the scripts the crawl fetched, and probes only tables the site's own code names, up to 30 per project and 40 per audit, with one `HEAD /rest/v1/<table>` each and `Prefer: count=exact`. It never reads a row; it reads only the status and the `Content-Range` total.
- It runs only at `--aggressive`, only online (not `--offline`, external link checking on) and inside the probe budget. A hosted audit of an unverified site stays passive and skips it.
- A secret key is never used for probing. `security/leaked-secrets` reports those if they are in the scripts.

## Step 3: read the answer

| Result | Meaning | Action |
|--------|---------|--------|
| Fail, table listed with a row count | The anon key can see that many rows: RLS is off, or a policy lets anyone read | Fix below, or waive if the table is public by design |
| Pass | Every table the code names got a definite answer and none reported rows | Not proof for tables the code never names, views or RPC functions |
| Skipped `probe-incomplete` | Some tables were throttled, capped or unanswered | Not clean. Say how many were unchecked and re-run narrower or later |
| Skipped `probing-not-aggressive`, `probing-passive`, `external-requests-off`, `no-tables-in-code`, `not-applicable` | Nothing was sent | Explain which, do not report it as clean |

A count of zero cannot tell RLS hiding every row from an empty table. An empty table with RLS off becomes exposed when rows arrive, so check the migration, not only the result.

## Step 4: fix

Turn on RLS for every table in an exposed schema, then add policies:

```sql
alter table public.profiles enable row level security;

create policy "Users read their own profile"
  on public.profiles for select
  using (auth.uid() = id);
```

With RLS on and no policy, the anon key reads nothing. Check each exposed table in Supabase's dashboard Security Advisor for others. Then:

- Treat exposed rows as already read: rotate anything sensitive they held and tell the user which tables were exposed and how many rows.
- Move any secret key out of client code to a server, Edge Function or CI secret, then rotate it.
- Check views and RPC functions by hand: the rule does not probe them.
- A table that is meant to be public (a `posts` table) still fails, because a count cannot tell a deliberate policy from RLS left off. Confirm with the user, then waive it:

```toml
[[ignore]]
rule   = "security/supabase-rls"
items  = ["posts"]
reason = "posts is public by design"
```

## Where the fix lives

Supabase SQL editor or the repo's `supabase/migrations/` folder (a fix applied only in the dashboard is lost on the next migration reset, so commit it), the Auth and API settings pages for keys, framework env files (Next.js `.env*`, Vite `.env`) for what ships to the browser, and AI app builders' generated code (Lovable, Bolt and similar), which often creates tables with no RLS.

## Stop condition

Stop when a re-run shows `security/supabase-rls` passing or skipped only for reasons you explained, no secret key in any shipped script (`security/leaked-secrets` clean), exposed keys rotated (ask the user to confirm), and every waived table has a reason.

## Hand off

Everything else on the site (headers, exposed files, cookies): `security-audit`. Non-security findings: `audit-website`.
