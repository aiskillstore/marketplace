# Supabase security audit skill for Claude Code, GitHub Copilot, Codex and Cursor

`supabase-security-audit` is an Agent Skills `SKILL.md` from squirrelscan: a Supabase RLS checker and exposed-key audit for coding agents. It uses the squirrel CLI or the hosted squirrelscan MCP server in Claude Code, GitHub Copilot, Codex, Cursor and other agents to see whether the public anon key can read tables with Row Level Security off, or whether a secret key shipped to the browser. It then writes the RLS SQL fixes.

## What it does

- Reads the repo first, with no network: secret keys in client code, every table the client queries and the migrations that enable RLS.
- Confirms ownership before probing: "Is this your Supabase project, or are you authorized to test it?" If not, it stops.
- Runs the `security/supabase-rls` audit rule, which sends one `HEAD` request per table with `Prefer: count=exact`. It never reads a row.
- Probes only tables the site's own code names, and never uses a secret key to probe.
- Reports skipped probes as not checked, not clean, and says that a count of zero cannot tell RLS hiding every row from an empty table.
- Writes `alter table ... enable row level security` and `create policy` SQL, and puts it in `supabase/migrations/`.
- Treats exposed rows as already read, and tells you to rotate anything sensitive and any exposed secret key.
- Waives a table that is public by design with an `[[ignore]]` entry and a reason.

## Questions it answers

- Is my Supabase app leaking data?
- Audit my Supabase RLS
- Check if my secret key is exposed
- Is Row Level Security turned on for every table?
- Can the anon key read my tables?
- Did my service role key end up in the browser bundle?
- Does my Lovable or Bolt app have tables with no RLS?
- What RLS policy should I write for a profiles table?

## Install

With any Agent Skills tool (Claude Code, GitHub Copilot, Codex, Cursor, Gemini CLI, Amp and others):

```bash
npx skills add squirrelscan/skills --skill supabase-security-audit
```

- **Claude Code plugin** (installs all the skills plus the hosted squirrelscan MCP server):

  ```
  /plugin marketplace add squirrelscan/skills
  ```

  ```
  /plugin install squirrelscan@squirrelscan
  ```

- **Codex**: `npx skills add` lands the skill in `.agents/skills/`. To add the MCP server too, configure it in `~/.codex/config.toml` ([Codex docs](https://docs.squirrelscan.com/developers/agents/codex)).
- **GitHub Copilot**: `npx skills add squirrelscan/skills --skill supabase-security-audit -a github-copilot` (project `.agents/skills/`, or `~/.copilot/skills/` with `-g`). Add the hosted MCP server too, see the [GitHub Copilot docs](https://docs.squirrelscan.com/developers/agents/copilot).
- **Cursor**: use the Cursor plugin in this repo, or the [one-click MCP link](cursor://anysphere.cursor-deeplink/mcp/install?name=squirrelscan&config=eyJ1cmwiOiJodHRwczovL21jcC5zcXVpcnJlbHNjYW4uY29tL21jcCJ9) plus the skill.
- **Gemini CLI, Amp and other Agent Skills tools**: `npx skills add` plus the MCP server ([docs](https://docs.squirrelscan.com/developers/agents)).

**Requirements:** the squirrel CLI installed and in PATH ([squirrelscan.com/download](https://squirrelscan.com/download), check with `squirrel --version`), or the hosted squirrelscan MCP server connected (`https://mcp.squirrelscan.com/mcp`).

Install the CLI on macOS or Linux:

```bash
curl -fsSL https://install.squirrelscan.com | bash
```

## Use it in Claude Code, GitHub Copilot, Codex or Cursor

```text
Is my Supabase app leaking data? Audit https://app.example.com
```

```text
Audit my Supabase RLS and write the migration to fix it
```

```text
Check if my service role key is exposed in the frontend code
```

The agent searches the repo, asks about ownership, runs the probe, reads each table's result and writes the SQL and key-rotation steps.

## How it works

1. Confirm you own the Supabase project, or stop.
2. Read the code: secret keys, queried tables and RLS in migrations.
3. Run `squirrel audit` with `--aggressive --probe-budget 1m` and the `security/supabase-rls` and `security/leaked-secrets` rules.
4. Read the answer per table: fail, pass or skipped, with the reason for any skip.
5. Enable RLS, add policies, move secret keys to a server and rotate them. Stop when a re-run passes, or skips only for reasons you explained.

## Related skills

- [`security-audit`](../security-audit/): headers, exposed files, cookies and the rest of the site.
- [`security-headers`](../security-headers/): CSP and header config.
- [`audit-website`](../audit-website/): non-security findings.

## Links

- [squirrelscan.com](https://squirrelscan.com)
- [docs.squirrelscan.com](https://docs.squirrelscan.com)
- [Repo README](../../README.md)
- [`SKILL.md`](./SKILL.md) for this skill
- MIT licensed
