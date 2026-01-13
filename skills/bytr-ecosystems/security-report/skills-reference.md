# Claude Skills Reference Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Configuration Layers                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ userPreferences │  │   userStyle     │  │     Memory      │ │
│  │                 │  │                 │  │                 │ │
│  │ • Tone/format   │  │ • Writing style │  │ • Facts about   │ │
│  │ • Tech level    │  │ • Teaching mode │  │   you           │ │
│  │ • Principles    │  │ • Response      │  │ • Preferences   │ │
│  │                 │  │   patterns      │  │ • Context       │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │           │
│           └────────────────────┼────────────────────┘           │
│                                ▼                                 │
│                    ┌───────────────────────┐                    │
│                    │  ALL CONVERSATIONS    │                    │
│                    └───────────────────────┘                    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                         Skills                               ││
│  │                                                              ││
│  │   /mnt/skills/public/   → Core (docx, xlsx, pptx, pdf)      ││
│  │   /mnt/skills/user/     → Your custom skills                ││
│  │   /mnt/skills/examples/ → Templates                         ││
│  │                                                              ││
│  └────────────────────────────┬────────────────────────────────┘│
│                               ▼                                  │
│                    ┌───────────────────────┐                    │
│                    │  COMPUTER USE ONLY    │                    │
│                    │  (file creation)      │                    │
│                    └───────────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Distinction

| Layer | Scope | Use For |
|-------|-------|---------|
| `userPreferences` | All conversations | Behavioral rules, tone, format preferences |
| `userStyle` | All conversations | Writing patterns, teaching approach |
| Memory | Cross-conversation | Persistent facts, confirmations, context |
| **Skills** | **Computer use only** | **File creation procedures, library choices** |

## Skill Structure

```
my-skill/
├── SKILL.md              # Required - main instructions (<500 lines)
├── scripts/              # Optional - deterministic operations
│   └── process.py
├── references/           # Optional - detailed docs (loaded on-demand)
│   └── advanced.md
└── assets/               # Optional - templates, images, fonts
    └── template.docx
```

## SKILL.md Anatomy

```yaml
---
name: skill-name                    # Required
description: |                      # Required - THIS IS THE TRIGGER
  What it does + when to use it.
  Be specific about file types, 
  keywords, and task patterns.
---
```

```markdown
# Skill Name

## Quick Start
[80% use case - minimal working example]

## Core Workflow
[Step-by-step, imperative form]

## Critical Gotchas
[Failure modes discovered through iteration]

## Advanced Features
[Links to references/ files]
```

## Progressive Disclosure

Claude loads context in stages:

1. **Always loaded**: `name` + `description` (~100 tokens)
2. **On trigger**: SKILL.md body (<5k tokens)
3. **On demand**: references/, scripts/, assets/

This prevents context window bloat.

## When to Use Skills vs Other Config

### Use Skills For:
- ✅ Document generation workflows (docx, xlsx, pptx)
- ✅ Code generation patterns
- ✅ File format handling procedures
- ✅ API-specific instructions
- ✅ Domain workflows with scripts/templates

### Use userPreferences For:
- ✅ Communication style ("direct, no sugar coating")
- ✅ Technical level assumptions
- ✅ Format preferences (bullets vs prose)
- ✅ Language preferences

### Use Memory For:
- ✅ "Always confirm before generating large outputs"
- ✅ Persistent facts about projects
- ✅ Ongoing context that should survive sessions

## Comparison: GPT vs Claude

| Feature | GPT Custom Instructions | Claude Skills |
|---------|------------------------|---------------|
| Scope | All interactions | Computer use only |
| Format | YAML/text | Markdown + YAML frontmatter |
| Triggers | Always applied | Description-based matching |
| Resources | None | scripts/, references/, assets/ |
| Progressive loading | No | Yes (context-efficient) |

## Creating a Custom Skill

1. Identify repetitive file creation tasks
2. Document the workflow that works
3. Extract gotchas and failure modes
4. Package scripts for deterministic operations
5. Test with real tasks
6. Iterate based on failures

## Installation

Skills go in `/mnt/skills/user/` via file upload in Claude's interface.

## Anti-Patterns

❌ Don't put behavioral preferences in skills (wrong layer)
❌ Don't create skills for things Claude already knows
❌ Don't duplicate content between SKILL.md and references/
❌ Don't create README.md, CHANGELOG.md, etc. (no humans reading this)
❌ Don't nest references more than one level deep
