---
name: agent-skill-trust-check
description: Static pre-install trust review for SKILL.md, OpenClaw, Hermes, MCP, and agent-skill marketplace packages before they request local, account, payment, or external access.
license: MIT
tags:
  - security
  - agent-skills
  - skill-review
  - mcp
---

# Agent Skill Trust Check

Use this skill before installing a third-party agent skill, SKILL.md package, MCP-linked skill, or marketplace listing.

## What This Skill Does

- Reads a public or local skill description before install.
- Flags patterns that deserve review: shell execution, destructive commands, secrets, wallet/payment actions, network output, persistence, and prompt-boundary issues.
- Separates basic provenance signals from risky behavior signals.
- Produces a patch order that a maintainer can resolve before the skill is trusted.

## When To Use

Use this when an agent is about to install or recommend a skill from:

- OpenClaw, Hermes, or ClawHub-style marketplaces.
- Claude Code, Codex, Cursor, Windsurf, or Gemini skill directories.
- MCP-linked skill bundles.
- GitHub repositories that include a `SKILL.md`, tool manifest, or install script.

## Run From The Public Repo

```bash
git clone https://github.com/TateLyman/agent-skill-trust-check.git
cd agent-skill-trust-check
npm run check
node bin/agent-skill-trust-check.js ./SKILL.md
```

For JSON output:

```bash
node bin/agent-skill-trust-check.js ./SKILL.md --json
```

npm command:

```bash
npx --yes agent-skill-trust-check ./SKILL.md --json
```

## Review Rules

Before installation, check:

- Does the skill run shell commands, package installers, or process-spawn APIs?
- Does it read secrets, environment variables, wallet data, credentials, cookies, or private keys?
- Does it send content to remote URLs or webhooks?
- Does it create persistent background jobs?
- Does it ask the agent to ignore or override higher-priority instructions?
- Does it document source, license, version, tests, permissions, and uninstall steps?

## Boundaries

This is a static pre-install check. It does not execute the target skill and does not prove the runtime is safe.

For marketplace-grade review, use the paid Agent Skill Trust Check listing:

https://orkai.ai/skills/agent-skill-trust-check
