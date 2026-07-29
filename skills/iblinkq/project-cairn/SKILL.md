---
name: project-cairn
description: Standardize how an AI-collaboration project turns work into reusable knowledge. Use when initializing or retrofitting Project Cairn in a project, recording progress after meaningful work, maintaining AGENTS/CLAUDE/cairn docs, auditing project knowledge for drift or missing records, pulling and citing external knowledge, or graduating validated project experience into a reusable knowledge base.
---

# Project Cairn

Project Cairn gives AI-collaboration projects a durable way to keep and reuse what they learn while doing real work. The **Skill** supplies the method, **AGENTS.md** carries always-read project rules, and **`.cairn/config.yaml`** stores machine-readable configuration.

This Skill is documentation-first. It provides instructions, templates, references, and provider adapters. It has no CLI, MCP server, background hook, chat-end trigger, automatic provider write, or automatic history migration. Routine maintenance happens during normal work because `AGENTS.md` carries the rules. Provider writes require human confirmation.

## Routing

Load exactly the reference you need:

- `references/init.md` — initialize, retrofit, bootstrap, or set up Project Cairn in a project.
- `references/consume.md` — pull, cite, reuse, or apply external knowledge from the configured knowledge base.
- `references/maintenance.md` — record progress, update LOG, update ROADMAP, maintain topic notes, or apply Cairn rules after work.
- `references/audit.md` — inspect, audit, validate, clean up, or find missing project knowledge records.
- `references/upgrade.md` — upgrade an initialized project instance to the current skill spec, or check how far it has drifted (instance drift after the skill itself evolved).
- `references/graduation.md` — graduate knowledge, move reusable experience to a knowledge base, or judge graduation-readiness; a provider write additionally reads only the selected `references/graduation/<provider>.md`.
- `references/frontmatter.md` — create or review Cairn topic notes or knowledge-base notes.
- `references/branch-closure.md` — review, close, abandon, or roll back an exploration branch and salvage its `cairn/` knowledge before it disappears.
- `references/zh-glossary.md` — writing project docs in Chinese (or resolving what a Chinese term should be); fixed English↔Chinese terminology mapping for Project Cairn's own vocabulary.

The description frontmatter describes triggering situations, not the workflow in detail.

## Templates

`assets/templates/` holds templates used by `init` and by later triggered actions: `AGENTS.md`, `CLAUDE.md`, `config.yaml`, `LOG.md`, `ROADMAP.md`, `topic.md`, `Cited.md`. `init` only scaffolds the core set (`AGENTS.md`, `CLAUDE.md`, `.cairn/config.yaml`, `cairn/LOG.md`, and optionally `cairn/ROADMAP.md`); `topic.md`, `Cited.md`, and `Reference/` are created on first trigger, not pre-stamped. Templates use `{{PLACEHOLDER}}` tokens; never hardcode a specific provider or knowledge path into a template.

## Boundaries

- No background hook and no chat-end trigger are assumed.
- Day-to-day maintenance happens because `AGENTS.md` is read as project rules.
- Audit is the safety net for missed records.
- Graduation is candidate detection plus human confirmation.
- Historical migration is optional and separate from init.
- Provider adapter scripts under `scripts/*.sh` are bash — verified on macOS/Linux; Windows users need WSL or Git Bash. `scripts/*.py` scripts only need a Python 3 interpreter, no shell required.
