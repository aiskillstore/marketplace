# Security audit skill for Claude Code, GitHub Copilot, Codex and Cursor

`security-audit` is an Agent Skills `SKILL.md` from squirrelscan: a Claude Code security audit and leaked secrets scanner for websites. It runs squirrelscan's security and integrity audit rules through the squirrel CLI or the hosted squirrelscan MCP server in Claude Code, GitHub Copilot, Codex, Cursor and other coding agents. It is not a penetration test: a clean run means these checks found nothing, not that the site is secure.

## What it does

- Finds leaked secrets, exposed files and endpoints, weak headers and cookies, mixed content and signs of compromise.
- Asks "Do you own this site, or are you authorized to test it?" before any probing beyond the crawl.
- Defaults to `--passive --ephemeral` for a site that is not yours, and never adds `--aggressive` or `--pentest` on its own.
- Reads skipped probe rules as not checked, never as clean, and says which checks did not run.
- Fixes in an order that limits damage: `integrity/*` findings first, then leaked secrets, exposed files and endpoints, Supabase tables, transport, headers, cookies and third parties.
- Tells you before changing anything when `integrity` findings suggest the site is compromised, and does not just delete files.
- Rotates leaked keys at the provider before removing them from code, and never pastes a secret into chat, a commit or a PR.
- Waives intentional findings with an `[[ignore]]` entry that has a reason, not by disabling the rule.

## Questions it answers

- Check my site's security
- Find leaked secrets
- Is there an API key in my site's JavaScript bundle?
- Are there exposed files or endpoints on my site?
- Is my site compromised or serving injected pages?
- Is my site using HTTPS correctly, with no mixed content?
- Are my cookie flags and security headers set?
- Is it safe to audit a site I do not own?

## Install

With any Agent Skills tool (Claude Code, GitHub Copilot, Codex, Cursor, Gemini CLI, Amp and others):

```bash
npx skills add squirrelscan/skills --skill security-audit
```

- **Claude Code plugin** (installs all the skills plus the hosted squirrelscan MCP server):

  ```
  /plugin marketplace add squirrelscan/skills
  ```

  ```
  /plugin install squirrelscan@squirrelscan
  ```

- **Codex**: `npx skills add` lands the skill in `.agents/skills/`. To add the MCP server too, configure it in `~/.codex/config.toml` ([Codex docs](https://docs.squirrelscan.com/developers/agents/codex)).
- **GitHub Copilot**: `npx skills add squirrelscan/skills --skill security-audit -a github-copilot` (project `.agents/skills/`, or `~/.copilot/skills/` with `-g`). Add the hosted MCP server too, see the [GitHub Copilot docs](https://docs.squirrelscan.com/developers/agents/copilot).
- **Cursor**: use the Cursor plugin in this repo, or the [one-click MCP link](cursor://anysphere.cursor-deeplink/mcp/install?name=squirrelscan&config=eyJ1cmwiOiJodHRwczovL21jcC5zcXVpcnJlbHNjYW4uY29tL21jcCJ9) plus the skill.
- **Gemini CLI, Amp and other Agent Skills tools**: `npx skills add` plus the MCP server ([docs](https://docs.squirrelscan.com/developers/agents)).

**Requirements:** the squirrel CLI installed and in PATH ([squirrelscan.com/download](https://squirrelscan.com/download), check with `squirrel --version`), or the hosted squirrelscan MCP server connected (`https://mcp.squirrelscan.com/mcp`).

Install the CLI on macOS or Linux:

```bash
curl -fsSL https://install.squirrelscan.com | bash
```

## Use it in Claude Code, GitHub Copilot, Codex or Cursor

```text
Check my site's security: https://example.com
```

```text
Find leaked secrets in what my site ships to the browser
```

```text
Run a passive security audit on a competitor's site, ephemeral
```

The agent asks about ownership, picks the probe level that fits, exports the full findings and fixes in damage-limiting order, with rotation steps for any exposed key.

## How it works

1. Check the CLI and sign-in status, and confirm ownership to choose the probe level.
2. Run `squirrel audit` with `--rule-include security,integrity`, passive for sites that are not yours.
3. Export the full list as JSON and read `skippedChecks` and the `Not checked:` line.
4. Fix in order, handing off to `supabase-security-audit` and `security-headers` where they apply.
5. Re-audit with the same command and `--refresh`. Stop when no error-severity findings remain in `security` and `integrity`, applicable probes were checked and exposed secrets are rotated.

## Related skills

- [`supabase-security-audit`](../supabase-security-audit/): Supabase apps whose anon key may read tables.
- [`security-headers`](../security-headers/): CSP, HSTS and other header config.
- [`audit-website`](../audit-website/): findings outside security.
- [`website-ci-gate`](../website-ci-gate/): gate security findings in CI.

## Links

- [squirrelscan.com](https://squirrelscan.com)
- [docs.squirrelscan.com](https://docs.squirrelscan.com)
- [Repo README](../../README.md)
- [`SKILL.md`](./SKILL.md) for this skill
- MIT licensed
