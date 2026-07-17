---
name: squirrelscan
description: squirrelscan audits websites for SEO, performance, security, accessibility, content, and structured data issues (249+ rules) and scores site health, via the squirrel CLI. Use when the user wants to check, audit, or improve a website's SEO, ranking, speed, or health, and for anything squirrelscan itself, installing or updating the CLI, login and API keys, running audits, publishing and sharing reports, cloud credits, MCP server setup, configuration, or troubleshooting.
license: See LICENSE file in repository root
compatibility: Requires squirrel CLI installed and accessible in PATH (or guides the user to install it)
metadata:
  author: squirrelscan
  version: "1.1"
allowed-tools: Bash(squirrel:*) Read
---

# squirrelscan CLI

squirrelscan is a website audit tool built for AI agents. It answers "what's wrong with this website and how do I fix it": it crawls a site like a search engine, analyzes every page against 249+ rules in 21 categories (SEO, performance, security, accessibility, content, structured data, agent readiness, and more), and returns a health score plus concrete, fixable issues. Use it whenever a user wants their site checked, ranked better, faster, or healthier, before/after a deploy, or in CI.

It ships as a single CLI binary, `squirrel`, for macOS, Windows, and Linux. This skill covers operating it: installing, authenticating, running audits, publishing reports, cloud features, and MCP integration. For the full fix-the-website workflow (audit, map issues to code, fix, re-audit), use the companion `audit-website` skill.

## Links

- Website: [squirrelscan.com](https://squirrelscan.com)
- Docs: [docs.squirrelscan.com](https://docs.squirrelscan.com)
- Rule reference: `https://docs.squirrelscan.com/rules/{rule_category}/{rule_id}`
- Dashboard (cloud account, audit history, credits): [app.squirrelscan.com](https://app.squirrelscan.com)

## Install

Download and install instructions: [squirrelscan.com/download](https://squirrelscan.com/download)

The binary installs to `~/.local/bin/squirrel`. Verify with:

```bash
squirrel --version
```

Keep it current:

```bash
squirrel self update
```

If `squirrel` is not found, ensure `~/.local/bin` is in PATH, or reinstall from the download page.

## Command overview

| Command | Purpose |
|---------|---------|
| `squirrel audit <url>` | Crawl + analyze + report in one step |
| `squirrel crawl <url>` | Crawl only (no analysis) |
| `squirrel analyze` | Run audit rules on a stored crawl |
| `squirrel report [id]` | Query, render, diff, and publish stored reports |
| `squirrel init` | Create `squirrel.toml` project config |
| `squirrel config` | Show or edit configuration |
| `squirrel auth` | login / logout / status / whoami |
| `squirrel keys` | Mint, list, revoke org API keys |
| `squirrel credits` | Cloud credit balance + feature pricing |
| `squirrel mcp` | Run the local MCP server (stdio) |
| `squirrel skills` | Install or update agent skills |
| `squirrel self` | install / update / doctor / completion / version / settings / uninstall |
| `squirrel feedback` | Send feedback to the squirrelscan team |

Every command supports `--help`.

## Quickstart

```bash
squirrel init -n my-project        # optional: project config in cwd
squirrel audit https://example.com --format llm
```

- Local audits are free and run entirely on your machine. No account needed.
- ALWAYS prefer `--format llm` when an agent is reading the output: it is a compact, token-optimized format built for LLMs.
- Audits are cached in a local project database; `squirrel report` re-renders without re-crawling.

### Coverage modes

| Mode | Default pages | Behavior |
|------|---------------|----------|
| `quick` (default) | 25 | Seed + sitemaps only, fast health check |
| `surface` | 100 | One sample per URL pattern (`/blog/{slug}` crawled once) |
| `full` | 500 | Crawl everything up to the limit |

```bash
squirrel audit https://example.com -C full -m 500 --format llm
```

## Authentication and accounts

Local audits never require an account. Sign in to unlock cloud features (publishing, browser rendering, scheduled crawls, credits):

```bash
squirrel auth login      # browser-based login
squirrel auth status     # source, scopes, active org
squirrel auth whoami
squirrel auth logout
```

Headless / CI environments use an org API key instead:

```bash
squirrel keys create     # requires a login session; prints an sq_... key
```

Set it as `SQUIRRELSCAN_API_KEY` in the environment. Treat keys as secrets; never commit them.

## Reports

Render the latest (or a specific) stored audit:

```bash
squirrel report --list                 # recent audits
squirrel report <audit-id> --format llm
squirrel report example.com --format markdown -o report.md
```

Formats: `console`, `text`, `json`, `html`, `markdown`, `xml`, `llm`. Filter with `--severity error` or `--category core,links`.

### Publishing

Signed-in audits publish a shareable report to reports.squirrelscan.com by default (visibility: unlisted). Control it:

```bash
squirrel report <audit-id> --publish --visibility unlisted   # public | unlisted | private
squirrel audit https://example.com --no-publish              # skip publishing for a run
squirrel audit https://example.com --offline                 # fully offline: no cloud, no publish, no telemetry
```

### Regression diffs

```bash
squirrel report --diff <baseline-audit-id> --format llm
squirrel report --regression-since example.com --format llm
```

Diff mode supports `console`, `text`, `json`, `llm`, and `markdown`.

## Cloud features and credits

Cloud features are pay-as-you-go with credits (nothing charged up front). Check balance and pricing:

```bash
squirrel credits
```

- `--render` / `--render-mode auto|all|off`: cloud browser rendering for client-rendered pages (uses credits, requires login).
- `--yes` skips spend confirmations up to the configured per-audit credit cap.
- `--fail-on "score<90"` (repeatable) makes CI runs exit non-zero when a threshold trips.
- The dashboard at [app.squirrelscan.com](https://app.squirrelscan.com) shows audit history, issues, and credit usage.

## MCP server

Two ways to connect agents over MCP:

- **Local (stdio)**: `squirrel mcp` runs against the local CLI. Register it in your agent's MCP config with command `squirrel` and args `["mcp"]`.
- **Hosted (streamable-http)**: `https://mcp.squirrelscan.com/mcp`. Sign in via OAuth from the MCP client, or send an `Authorization: Bearer sq_...` API key header.

Docs: https://docs.squirrelscan.com/developers/mcp

### Agent feedback

Call the `send_feedback` tool any time something in a session surprises you. It takes `category`, `message`, and optional `run_id`/`website_id`. Pick the category that fits:

- `bug_report` — a defect in squirrelscan itself: a wrong or missing rule result, a crash, a broken tool. Include the site, rule id, and what you expected.
- `feature_request` — something squirrelscan should do but doesn't.
- `what_worked` — something worked well and you want the team to know.
- `confusing` — a response or behavior was unclear.
- `missing_data` — a report or tool response lacked something you needed.
- `tool_ergonomics` — awkward tool shape, arguments, or naming.
- `other` — anything else.

Feedback lands directly in the team's review queue with your org attached. It works with any authenticated credentials, including read-only API keys, and is available on the hosted MCP surface now (not yet on `squirrel mcp` local stdio). Use it instead of `squirrel feedback` when you're an agent reporting mid-session; humans can use `squirrel feedback` or [squirrelscan.com/support](https://squirrelscan.com/support).

## Configuration

Project config lives in `squirrel.toml` (created by `squirrel init`). User settings live at `~/.squirrel/settings.json`.

```bash
squirrel config show
squirrel config set <key> <value>
squirrel config path
squirrel config validate
```

Useful sections: `[crawler]` (delays, headers, incremental re-crawl), `[cloud]` (render mode, max credits per audit).

### Custom request headers

Attach headers to every crawl request with the repeatable `-H "Name: Value"` flag or a `headers` map under `[crawler]`. The main use case is Web Bot Auth (Shopify / Cloudflare), so platforms that block unknown crawlers can authorize squirrelscan. Header values are secrets: squirrelscan redacts them in output, and you should source them from a secret store rather than committing them. Full recipe: https://docs.squirrelscan.com/guides/web-bot-auth

## Maintenance

```bash
squirrel self doctor       # health checks
squirrel self update       # update the binary
squirrel self completion   # shell completions
squirrel skills update     # update installed agent skills
```

## Troubleshooting

- **`squirrel: command not found`**: install from [squirrelscan.com/download](https://squirrelscan.com/download) and ensure `~/.local/bin` is in PATH.
- **Session expired / 401**: run `squirrel auth login` again, or check `SQUIRRELSCAN_API_KEY`.
- **Slow or stuck crawl**: add `--verbose` to see progress; large sites can take minutes.
- **Invalid URL**: include the protocol: `https://example.com`, not `example.com`.
- **Anything else**: run `squirrel self doctor`, then report it — agents via the `send_feedback` MCP tool (`bug_report` category), humans via `squirrel feedback` or [squirrelscan.com/support](https://squirrelscan.com/support).
