---
name: security-audit
description: "Run squirrelscan's security and integrity audit rules (squirrel CLI or hosted squirrelscan MCP server) in Claude Code, GitHub Copilot, Codex, Cursor and other coding agents to find leaked secrets, exposed files and endpoints, weak headers and cookies, mixed content and signs of compromise. It asks whether you own or may test the site before any aggressive probing, defaults to passive and ephemeral runs otherwise, and orders fixes to limit damage. Not a penetration test. Use when asked \"check my site's security\" or \"find leaked secrets\"."
license: See LICENSE file in repository root
compatibility: Requires the squirrel CLI installed and accessible in PATH, or the hosted squirrelscan MCP server connected
metadata:
  author: squirrelscan
  version: "0.1.3"
allowed-tools: Bash(squirrel:*) Read Edit Grep Glob
---

# Security Audit

Find what a site exposes to visitors and attackers: leaked secrets, open files and endpoints, weak headers and cookies, mixed content, and signs of compromise. Then fix it in the order that limits damage.

This is not a penetration test. squirrelscan reports what it can see and prove from outside; a clean run means these checks found nothing, not that the site is secure.

## Before the first audit

Run `squirrel --version`. If it fails, install the CLI from [squirrelscan.com/download](https://squirrelscan.com/download) (the `squirrelscan` skill has `references/install.md`). Then run `squirrel auth status`:

- **Signed out, or `--offline`**: the audit runs on this machine, is free, and nothing is published.
- **Signed in**: the audit is billed in credits (50 plus 2 per audited page, plus 1 per distinct external link the cloud verifies), adds the site to the user's dashboard, can turn on recurring audits and publishes an unlisted report. Tell the user the cost (`squirrel credits`) and get a yes. Offer `--offline` or `--no-publish`. For a site the user does not own, add `--ephemeral`: nothing is added to the dashboard, scheduled or published.

Every flag below is checked against the squirrel CLI docs (https://docs.squirrelscan.com/cli/audit). Rule docs: `https://docs.squirrelscan.com/rules/{category}/{rule_id}`.

## Who owns the site decides the probe level

squirrelscan can send probes beyond the crawl (see `--probe`). Ask first: "Do you own this site, or are you authorized to test it?"

| Situation | Command |
|-----------|---------|
| Not the user's site, or unknown | `squirrel audit <url> --rule-include security,integrity --passive --ephemeral --format llm` |
| The user's own site, normal check | `squirrel audit <url> --rule-include security,integrity --level surface --format llm` (probing defaults to `active`: a handful of requests that look like normal traffic) |
| The user's own site, deep check | Only after the user says in this conversation that they own it or may test it: `squirrel audit <url> --rule-include security,integrity --level full --aggressive --probe-budget 2m --format llm` |

Never add `--aggressive` or `--pentest` on your own. Aggressive probing makes many requests and many 404s, requests paths that `robots.txt` disallows on purpose, can trip a WAF, and is what runs `security/exposed-files` and `security/supabase-rls`. An aggressive run also asks for `/actuator/heapdump`, which makes an exposed Spring server write a dump to disk.

`--offline` does not make probing passive: add `--passive` for that. A hosted (cloud) audit of a site whose ownership is not confirmed stays passive, so the probing rules are not checked there; do not report them as clean.

## Reading the findings

1. Export the full list: `squirrel audit <url> --rule-include security,integrity --format json -o security.json` (the `llm` format samples 5 pages and 5 items per rule).
2. Read `skippedChecks`, `summary.skipped` and the `Not checked:` line. A probe rule that was skipped (`probing-passive`, `probing-not-aggressive`, `external-requests-off`) is not clean: say which checks did not run and what would run them.
3. Re-render later without recrawling: `squirrel report <audit-id> --group security --severity error --format llm`.
4. Never paste a leaked secret into chat, a commit or a PR. Name the rule, the file or URL and the key type only.

## Fix order

1. **`integrity/*` findings first** (injected pages, cloaking, phishing kits, obfuscated scripts, `integrity/known-malicious-url`). These can mean the site is compromised. Tell the user before changing anything; do not just delete files, since the entry point (a plugin, a CI token, a stolen login) is still open. Hand off to their host or incident process.
2. **Leaked secrets** (`security/leaked-secrets`, `security/token-storage`): removing the key from the code is not enough. Rotate it at the provider, then remove it, then check git history. A key that shipped to browsers was read.
3. **Exposed files and endpoints** (`security/exposed-files`, `security/exposed-actuator`, `security/graphql-introspection`, `security/graphql-get-mutations`, `security/unauthenticated-api`, `security/json-sensitive-fields`, `security/auth-endpoint-disclosure`, `security/client-side-authz`): block at the server or the edge, or add authentication. Hiding a link does not fix an open endpoint.
4. **Supabase tables** (`security/supabase-rls`): use the `supabase-security-audit` skill.
5. **Transport** (`security/https`, `security/http-to-https`, `security/tls-certificate`, `security/mixed-content`, `security/hsts`, `security/form-https`, `security/password-form-get`).
6. **Headers** (`security/csp`, `security/x-frame-options`, `security/x-content-type`, `security/referrer-policy`, `security/permissions-policy`): use the `security-headers` skill for the config.
7. **Cookies and third parties** (`security/cookie-flags`, `security/third-party-cookies`, `security/sri`, `security/open-redirect`, `security/new-tab`, `security/version-disclosure`, `security/security-txt`).

## Where the fix usually lives

| Stack | Look here |
|-------|-----------|
| Next.js | `next.config.*` `headers()`, `middleware.ts`, route handlers under `app/api/`, `NEXT_PUBLIC_*` env vars (anything with that prefix ships to the browser) |
| WordPress | `wp-config.php`, `.htaccess` or the server block, plugin updates, removing unused plugins and themes, backup and debug files in the web root |
| Shopify | theme code (`theme.liquid`, `*.liquid`), installed apps that inject scripts; Shopify controls headers and TLS itself, so those are usually not fixable by the merchant |
| Webflow | Site settings, custom code (head and body), the hosting settings; headers are limited to what Webflow exposes |
| Cloudflare | Rules, then Transform Rules (modify response headers); SSL/TLS, Always Use HTTPS, WAF custom rules for blocking paths |
| Vercel | `vercel.json` `headers`, `redirects`, environment variables, deployment protection |
| Netlify | `_headers`, `netlify.toml`, redirects, environment variables |
| Supabase | Row Level Security policies, the API keys page, Edge Functions; see `supabase-security-audit` |

## Stop condition

Stop when a re-audit with the same command and `--refresh` shows no error-severity findings in `security` and `integrity`, every probe rule that applies was checked (not skipped), exposed secrets are rotated (ask the user to confirm), and anything left is a documented decision. A finding that is intentional (a public file listed in `security/exposed-files`, a table public by design) is waived with an `[[ignore]]` entry that has a `reason`, not by disabling the rule. See `references/configuration.md` in the `squirrelscan` skill.

## Hand off

- Supabase app: `supabase-security-audit`. Header and CSP config: `security-headers`.
- Findings outside security (SEO, links, performance): `audit-website`.
- Gate it in CI: `website-ci-gate`.
