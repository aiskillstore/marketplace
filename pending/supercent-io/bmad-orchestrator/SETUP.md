# BMAD Orchestrator — Setup Guide

> **BMAD Method v6** + **plannotator** integration
> Structured AI-driven development with visual plan review at every phase gate.

---

## What You Get

```
Your AI Agent
     │
     ▼
 /workflow-init          ← bootstrap project
     │
     ▼
 Phase 1: Analysis       ← /product-brief, /research
     │
     │  [plannotator review] ← approve before advancing
     ▼
 Phase 2: Planning       ← /prd or /tech-spec
     │
     │  [plannotator review]
     ▼
 Phase 3: Solutioning    ← /architecture  (Level 2+ only)
     │
     │  [plannotator review]
     ▼
 Phase 4: Implementation ← /sprint-planning → /dev-story
```

**plannotator** opens a visual browser UI after each phase document is created. You annotate, approve, or request changes — then your agent continues to the next phase.
Use the same cross-platform control model as JEO: `settings` configure the platform, `rules` prevent invalid phase transitions, and `hooks` enforce them.

---

## Quick Start (3 steps)

### Step 1 — Install

```bash
bash scripts/install.sh
```

This installs plannotator CLI and configures the Claude Code `ExitPlanMode` hook.
**Restart Claude Code after running this.**

Options:
```bash
bash scripts/install.sh --init-project       # Also initialize BMAD in current directory
bash scripts/install.sh --skip-plannotator   # BMAD scripts only, no plannotator
bash scripts/install.sh --dry-run            # Preview without making changes
```

### Step 2 — Initialize your project

Run this inside your AI session (Claude Code, Gemini CLI, etc.):

```
/workflow-init
```

Your agent will ask three questions:
- **Project name** — e.g. `my-app`
- **Project type** — `web-app`, `mobile-app`, `api`, `game`, `library`, `other`
- **Project level** — `0` to `4` (see level guide below)

This creates:
```
bmad/config.yaml                    ← project configuration
docs/bmm-workflow-status.yaml       ← workflow tracking
docs/stories/                       ← story files will go here
```

### Step 3 — Start working

```
/workflow-status
```

Your agent shows your current phase, what's done, and exactly what to run next.

---

## Project Level Guide

Choose the level that matches your project size:

| Level | Size | Required phases | Typical duration |
|-------|------|----------------|-----------------|
| **0** | Single fix / 1 story | Tech Spec → Story | Hours |
| **1** | Small feature / 1–10 stories | Tech Spec → Sprint | 1–5 days |
| **2** | Feature set / 5–15 stories | PRD → Architecture → Sprint | 1–3 weeks |
| **3** | Complex integration / 12–40 stories | Brief → PRD → Architecture → Sprints | 3–8 weeks |
| **4** | Enterprise / 40+ stories | Brief → Research → PRD → UX → Architecture → Sprints | 2+ months |

**Quick decision:**
- Bug fix or config change → Level 0
- New API endpoint or small UI feature → Level 1
- User auth system or payment integration → Level 2
- Third-party platform integration → Level 3
- Major system overhaul → Level 4

---

## plannotator Phase Gate Review

After each phase document is created, submit it for review before moving on:

```bash
# After /prd creates docs/prd-myapp-2026-02-25.md
bash scripts/phase-gate-review.sh docs/prd-myapp-2026-02-25.md "PRD Review: myapp"

# After /architecture creates docs/architecture-myapp-2026-02-25.md
bash scripts/phase-gate-review.sh docs/architecture-myapp-2026-02-25.md
```

Or trigger it from inside your AI session:

```
planno — review the PRD before we proceed to Phase 3
```

### What happens in the review UI

1. plannotator opens in your browser automatically
   - unless the same document hash already has a terminal review result, in which case the gate is skipped
2. Read through the document
3. Annotate specific sections:
   - `delete` — remove a risky or unnecessary element
   - `insert` — add something missing
   - `replace` — correct an approach
   - `comment` — clarify constraints
4. Choose an outcome:
   - **Approve** → your agent advances to the next phase; doc saved to your configured destination (Obsidian or Bear)
   - **Request Changes** → annotations sent back; agent revises and re-submits

### Phase gate reference

| Completing phase | Document type | Gate command |
|-----------------|---------------|--------------|
| Phase 1 → 2 | Product Brief | `bash scripts/phase-gate-review.sh docs/product-brief-*.md` |
| Phase 2 → 3 | PRD or Tech Spec | `bash scripts/phase-gate-review.sh docs/prd-*.md` |
| Phase 3 → 4 | Architecture | `bash scripts/phase-gate-review.sh docs/architecture-*.md` |
| Phase 4 wrap-up | Sprint summary | `bash scripts/phase-gate-review.sh docs/sprint-status.yaml` |

---

## Common Commands

### Check status anytime

```
/workflow-status
```

Output example:
```
Project: my-app (web-app, Level 2)

✓ Phase 1: Analysis
  ✓ product-brief (docs/product-brief-my-app-2026-02-25.md)

→ Phase 2: Planning [CURRENT]
  ⚠ prd (required - NOT STARTED)

  Phase 3: Solutioning
  - architecture (required)

  Phase 4: Implementation
  - sprint-planning (required)

Recommended next step: Run /prd to continue
```

### Validate your config

```bash
bash scripts/validate-config.sh
```

### Check BMAD + plannotator status

```bash
bash scripts/check-status.sh
```

---

## Workflow by Project Level

### Level 0–1 (Fast Track)

```
/workflow-init  →  /tech-spec
     ↓
planno review
     ↓
/sprint-planning  →  /dev-story
```

### Level 2 (Standard Feature)

```
/workflow-init  →  /product-brief  →  /prd
                                        ↓
                               planno review (Phase 2 gate)
                                        ↓
                               /architecture
                                        ↓
                               planno review (Phase 3 gate)
                                        ↓
                               /sprint-planning  →  /dev-story
```

### Level 3–4 (Enterprise)

```
/workflow-init  →  /product-brief  →  /research
                                        ↓
                                      /prd  →  /create-ux-design
                                        ↓
                               planno review (Phase 2 gate)
                                        ↓
                               /architecture  →  /solutioning-gate-check
                                        ↓
                               planno review (Phase 3 gate)
                                        ↓
                               /sprint-planning  →  /create-story  →  /dev-story
                                        ↓
                               /code-review  (per sprint)
```

---

## Notes Auto-Save: Obsidian or Bear (Optional)

Approved phase documents can be auto-saved with YAML frontmatter and `[[BMAD Plans]]` backlinks.

**Setup (choose one or both):**
1. Open any plannotator review in your browser
2. Click ⚙️ Settings → **Saving** tab
3. Toggle ON **Obsidian Integration** and/or **Bear Notes**
4. For Obsidian: select your vault from the dropdown
5. For Bear: verify callback works first:
   ```bash
   open "bear://x-callback-url/create?title=Test&text=OK"
   ```

Each approved document saves as:
```
vault/plannotator/PRD Review myapp - Feb 25, 2026 10-30pm.md
```

With frontmatter:
```yaml
---
created: 2026-02-25T22:30:00.000Z
source: plannotator
tags: [bmad, phase-2, prd, my-app]
---

[[BMAD Plans]]

# PRD: my-app
...
```

---

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `install.sh` | Full setup: plannotator + hooks + scripts | `bash scripts/install.sh` |
| `init-project.sh` | Initialize BMAD in a project | `bash scripts/init-project.sh --name MyApp --type web-app --level 2` |
| `check-status.sh` | Display current workflow status | `bash scripts/check-status.sh` |
| `phase-gate-review.sh` | Submit doc to plannotator for review | `bash scripts/phase-gate-review.sh docs/prd-*.md` |
| `validate-config.sh` | Validate YAML config files | `bash scripts/validate-config.sh` |

---

## Troubleshooting

**BMAD not detected:**
```bash
# Check if config exists
ls bmad/config.yaml

# Re-initialize if missing
/workflow-init
```

**plannotator doesn't open:**
```bash
# Check installation
plannotator --version

# Re-install
curl -sSfL https://plannotator.ai/install.sh | sh
```

**Hook not firing on plan exit:**
```bash
# Re-run hook setup (from plannotator skill)
bash .agent-skills/plannotator/scripts/setup-hook.sh

# Restart Claude Code after this
```

**Status file out of sync:**
```bash
# Validate config
bash scripts/validate-config.sh

# Manually edit status
# File: docs/bmm-workflow-status.yaml
```

---

## Related Skills

| Skill | Purpose | Install |
|-------|---------|---------|
| `plannotator` | Visual plan & diff review | `npx skills add ... --skill plannotator` |
| `ralph` | Persistence loop until task completes | `npx skills add ... --skill ralph` |
| `vibe-kanban` | Visual kanban for agent stories | `npx skills add ... --skill vibe-kanban` |
| `jeo` | Full orchestration: plan → execute → track | `npx skills add ... --skill jeo` |

---

> **Source:** [BMAD Method](https://github.com/bmad-method/bmad) · [plannotator](https://plannotator.ai) · [skills-template](https://github.com/supercent-io/skills-template)
