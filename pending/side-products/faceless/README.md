# Faceless.so Claude Skill

An agent skill that lets Claude (and other SKILL.md-compatible agents) drive [Faceless.so](https://faceless.so): turn scripts into rendered AI faceless videos, run automated series, and publish or schedule them to YouTube, TikTok, Instagram, X, Facebook, LinkedIn and Threads.

## Install

With the [skills CLI](https://github.com/anthropics/skills):

```bash
npx skills add Side-Products/faceless-skill
```

Or manually: copy this repo's contents into your agent's skills directory (for Claude Code: `~/.claude/skills/faceless/`).

## Requirements

- A Faceless.so account with an API key: create one at https://faceless.so/developers
- Node.js 18+ for the CLI (the skill installs `faceless-cli` from npm on first use, or uses `npx`)

Set `FACELESS_API_KEY` in the agent's environment, or let the agent run `faceless login` interactively.

## What is in here

- `SKILL.md`: the skill itself (setup, command reference, workflows, error handling)
- `references/api-reference.md`: full API reference
- `references/workflows.md`: step-by-step recipes

## Docs

- Developer docs: https://faceless.so/developers
- OpenAPI spec: https://faceless.so/api/v1/openapi.json
- Agent index: https://faceless.so/llms.txt

## Note

This repo is generated from the main Faceless.so codebase (`npm run generate:agents` + `npm run sync-skill`). Do not edit files here directly; changes will be overwritten on the next sync.
