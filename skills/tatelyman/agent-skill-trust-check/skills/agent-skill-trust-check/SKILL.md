---
spec: usk/1.0
name: agent-skill-trust-check
version: 0.1.2
description: Static pre-install trust review for SKILL.md, OpenClaw, Hermes, MCP, and agent-skill marketplace packages before they request local, account, payment, or external access.
interface:
  type: cli
  entry_point: bin/agent-skill-trust-check-stdin.js
  runtime: node
  call_pattern: stdin_stdout
input_schema:
  type: object
  properties:
    text:
      type: string
      description: SKILL.md, marketplace description, or install instructions to review before installation.
    target:
      type: string
      description: Optional source label for the reviewed text.
  required:
    - text
output_schema:
  type: object
  properties:
    verdict:
      type: string
      description: Static install-readiness verdict.
    risk_score:
      type: integer
      description: Aggregate static risk score.
    findings:
      type: array
      description: Matched risky behavior signals and suggested fixes.
    missing_signals:
      type: array
      description: Provenance or safety signals not found in the target text.
permissions:
  network: false
  filesystem: false
  subprocess: false
  env_vars: []
category: security
capabilities:
  - skill_review
  - agent_skill_security
  - marketplace_vetting
  - mcp_review
license: MIT
tags:
  - security
  - agent-skills
  - skill-review
  - mcp
author: Tate Programs
homepage: https://github.com/TateLyman/agent-skill-trust-check
platform_compatibility:
  - Claude Code
  - Codex CLI
  - Cursor
  - Gemini CLI
  - OpenClaw Agent
requirements:
  node: ">=20"
changelog: Added a marketplace-safe stdin runner that needs no filesystem or network access.
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

Marketplace-safe stdin mode:

```bash
node bin/agent-skill-trust-check-stdin.js < ./SKILL.md
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

This is a static pre-install check. The marketplace-safe runner reads only stdin and returns JSON. The local CLI can also read a local path or a public GitHub/raw/Gist URL when run from the repository checkout. Neither mode executes the target skill or proves the runtime is safe.

For marketplace-grade review, use the paid Agent Skill Trust Check listing:

https://orkai.ai/skills/agent-skill-trust-check
