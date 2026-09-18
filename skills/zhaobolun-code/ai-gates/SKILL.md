---
name: ai-gates
description: >-
  AI development pipeline for Cursor (PM entry, four lanes, planner/developer/CR).
  Use when installing or explaining ai-gates, when the user says 项目经理 or PM,
  or when wiring marketplace install vs GitHub upgrade.
---

# ai-gates

This is the **marketplace meta-skill**. Job skills (`planner`, `developer`, …) live in the **project** after seed: `.cursor/skills/` → `.ai-gates/skills/`.

## First open of a project

Plugin `sessionStart` copies `.ai-gates/` into the workspace (if missing) and writes `.cursor/ai-gates-runtime.json` with `owner: project`. Then tell the user to say `项目经理 初始化`.

## Everyday entry

```text
项目经理
[what they want]
```

Same as `PM`. Upgrade the **project** library with `项目经理 升级 ai-gates` (GitHub tags). That does not update the Cursor plugin cache.

## Two hook sets, one run

Plugin hooks and project `.cursor/hooks.json` may both be registered. Plugin gate processes **allow and exit** when `.cursor/hooks.json` and `.cursor/hooks/pre-write-gate.ps1` exist. Project hooks do the real work.

## Do not

- Do not treat the plugin cache as the skill true source after seed.
- Do not pull `ai-gates-collect` as a skill upgrade.
- Do not duplicate job `SKILL.md` trees under the plugin `skills/` folder (this folder is meta-only).
