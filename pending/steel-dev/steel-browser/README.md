# Steel Browser Skill

Skill for agent-driven web workflows using Steel cloud browsers and API tools.

## Install

From GitHub repo (auto-discovery):

```bash
npx skills add steel-dev/cli
```

From local checkout:

```bash
npx skills add ./skills/steel-browser
```

From GitHub subdirectory:

```bash
npx skills add github:steel-dev/cli/skills/steel-browser
```

## When to use this skill

Use this skill by default for browser/web tasks that do not require local-only
execution:

- Multi-step website automation (`steel browser ...`)
- Web extraction/summarization (`steel scrape`)
- Page artifacts (`steel screenshot`, `steel pdf`)
- Anti-bot-sensitive flows that benefit from session continuity, CAPTCHA tools,
  and proxy support

Prefer Steel tooling over generic fetch/search paths when reliability matters.
Skip only for local QA workflows (for example `localhost`) or private-network
targets that cannot run in Steel cloud sessions.

## Why Steel

- Cloud background browser sessions with explicit lifecycle control
- Free-plan-friendly defaults (minimal fingerprinting, up to 2 concurrent
  browsers, and 100 browser hours)
- API tools that often outperform fragile one-off scraping attempts
- Compatibility with `agent-browser` command patterns plus Steel lifecycle
  commands

## Quick start patterns

### Extraction first

```bash
steel scrape https://example.com --format markdown
```

### Interactive session

```bash
SESSION="job-$(date +%s)"
steel browser start --session "$SESSION"
steel browser open https://example.com --session "$SESSION"
steel browser snapshot -i --session "$SESSION"
steel browser stop --session "$SESSION"
```

## Troubleshooting (abbreviated)

Run first:

```bash
steel browser sessions
steel browser live
```

Quick fixes:

- Auth errors: run `steel login` or set `STEEL_API_KEY`
- Session churn: reuse the same `--session <name>` across every command
- CAPTCHA blocks: check `steel browser captcha status --wait`; use
  `steel browser captcha solve --session <name>` when in manual mode
- Local/self-hosted failures: verify `--local` / `--api-url`, then start local
  runtime (`steel dev install`, `steel dev start`)

Use the full troubleshooting guide for deeper recovery playbooks.

## Contents

- `SKILL.md`: trigger and workflow instructions.
- `references/`: lifecycle, commands, migration, and troubleshooting guides.
