---
name: bmad-orchestrator
description: Orchestrates BMAD workflows for structured AI-driven development. Routes work across Analysis, Planning, Solutioning, and Implementation phases.
allowed-tools: Read Write Bash Grep Glob
metadata:
  tags: bmad, orchestrator, workflow, planning, implementation
  platforms: Claude, Gemini, Codex, OpenCode
  keyword: bmad
  version: 1.2.0
  source: user-installed skill
---


# bmad-orchestrator - BMAD Workflow Orchestration

## When to use this skill

- Initializing BMAD in a new project
- Checking and resuming BMAD workflow status
- Routing work across Analysis, Planning, Solutioning, and Implementation
- Managing structured handoff between phases

---

## Installation

```bash
npx skills add https://github.com/supercent-io/skills-template --skill bmad-orchestrator
```

## Notes for Codex Usage

`bmad-orchestrator`'s default execution path is Claude Code.
To run the same flow directly in Codex, we recommend operating BMAD stages via a higher-level orchestration path such as `omx`/`ohmg`.

## Control Model

BMAD phase routing should be treated with the same three-layer abstraction used by JEO:

- `settings`: platform-specific runtime configuration such as Claude hooks, Codex/Gemini instructions, and MCP setup
- `rules`: phase constraints such as "do not advance before the current phase document is approved" and "do not reopen the same unchanged phase document for review"
- `hooks`: platform callbacks such as Claude `ExitPlanMode`, Codex `notify`, or Gemini `AfterAgent`

For BMAD phase gates, the intended rule is strict:

- review the current phase document before moving forward
- if the document hash has not changed since the last terminal review result, do not relaunch plannotator
- only a revised document resets the gate and permits another review cycle

---

## BMAD Execution Commands

## Platform Support Status (Current)

| Platform | Current support mode | Requirements |
|---|---|---|
| Gemini CLI | Native (recommended) | Register the `bmad` keyword, then run `/workflow-init` |
| Claude Code | Native (recommended) | Install skill + `remember` pattern |
| OpenCode | Orchestration integration | Use an `omx`/`ohmg`/`omx`-style bridge |
| Codex | Orchestration integration | Use an `omx`/`ohmg`-style bridge |

Possible with `this skill alone`:
- Gemini CLI/Claude Code: **Yes**
- OpenCode/Codex: **Yes (via orchestration)**

Use these in your AI session:

```text
/workflow-init
/workflow-status
```

Typical flow:

1. Run `/workflow-init` to bootstrap BMAD config.
2. Move through phases in order: Analysis -> Planning -> Solutioning -> Implementation.
3. Run `/workflow-status` any time to inspect current phase and progress.

---

## Quick Reference

| Action | Command |
|--------|---------|
| Initialize BMAD | `/workflow-init` |
| Check BMAD status | `/workflow-status` |


---

## plannotator Integration (Phase Review Gate)

Each BMAD phase produces a key document (PRD, Tech Spec, Architecture). Before transitioning to the next phase, review that document with **plannotator** and auto-save it to Obsidian.

### Why use plannotator with BMAD?

- **Quality gate**: Approve or request changes before locking in a phase deliverable
- **Obsidian archive**: Every approved phase document auto-saves with YAML frontmatter and `[[BMAD Plans]]` backlink
- **Team visibility**: Share a plannotator link so stakeholders can annotate the PRD/Architecture before implementation begins

### Phase Review Pattern

After completing any phase document, submit it for review:

```bash
# After /prd → docs/prd-myapp-2026-02-22.md is created
bash scripts/phase-gate-review.sh docs/prd-myapp-2026-02-22.md "PRD Review: myapp"

# After /architecture → docs/architecture-myapp-2026-02-22.md is created
bash scripts/phase-gate-review.sh docs/architecture-myapp-2026-02-22.md "Architecture Review: myapp"
```

Or submit the plan directly from within your AI session:

```text
# In Claude Code after /prd completes:
planno — review the PRD before we proceed to Phase 3
```

The agent will open the plannotator UI for review. In Claude Code: call `EnterPlanMode` → write plan → call `ExitPlanMode` (hook fires automatically). In OpenCode: the `submit_plan` plugin tool is available directly.

### Phase Gate Flow

```
/prd completes → docs/prd-myapp.md created
       ↓
 bash scripts/phase-gate-review.sh docs/prd-myapp.md
       ↓
 hash guard checks whether this exact document was already reviewed
       ↓
 unchanged hash? yes → keep previous terminal result, do not reopen UI
       ↓ no
 plannotator UI opens in browser
       ↓
  [Approve]              [Request Changes]
       ↓                        ↓
 Obsidian saved          Agent revises doc
 bmm-workflow-status     Re-submit for review
 updated automatically
       ↓
 /architecture (Phase 3)
```

### Obsidian Save Format

Approved phase documents are saved to your Obsidian vault with:

```yaml
---
created: 2026-02-22T22:45:30.000Z
source: plannotator
tags: [bmad, phase-2, prd, myapp]
---

[[BMAD Plans]]

# PRD: myapp
...
```

### Quick Reference

| Phase | Document | Gate Command |
|-------|----------|--------------|
| Phase 1 → 2 | Product Brief | `bash scripts/phase-gate-review.sh docs/product-brief-*.md` |
| Phase 2 → 3 | PRD / Tech Spec | `bash scripts/phase-gate-review.sh docs/prd-*.md` |
| Phase 3 → 4 | Architecture | `bash scripts/phase-gate-review.sh docs/architecture-*.md` |
| Phase 4 done | Sprint Plan | `bash scripts/phase-gate-review.sh docs/sprint-status.yaml` |
