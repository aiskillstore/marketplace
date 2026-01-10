---
name: obsidian-plan-wiki
description: This skill should be used when creating or working with modular project plans stored as Obsidian-compatible markdown wikis. Use when the user asks to create a plan, roadmap, or documentation system that needs to be navigable in Obsidian, or when working with existing plan wikis that use the %% [ ] %% task tracking format.
---

# Obsidian Plan Wiki

Create and manage modular project plans as Obsidian-compatible markdown wikis with progressive disclosure, task tracking, and research integration.

## When to Use

- Creating new project plans, roadmaps, or documentation systems
- Working with existing plan wikis using `%% [ ] %%` task format
- User mentions "plan", "roadmap", "wiki", or "Obsidian"
- Need to organize complex multi-phase projects

## Directory Structure

Initialize new plan wikis with this structure:

```
plan-name/
├── README.md           # Index - start here, links to everything
├── CLAUDE.md           # Rules for Claude working with this plan
├── changelog.md        # Amendment history (Keep a Changelog format)
├── deferred.md         # Preserved deferred work (optional)
├── phases/             # High-level phase overviews
│   ├── 01-phase-name.md
│   └── 02-phase-name.md
├── tasks/              # Individual task specifications
│   ├── 1.1-task-slug.md
│   └── 1.2-task-slug.md
├── reference/          # Supporting documentation
│   └── architecture.md
└── research/           # Oracle/Delphi research outputs
    ├── index.md
    └── topic-name.md
```

## Core Principles

### 1. Progressive Disclosure

Load only what's needed for the current task:

```
User asks about camera → Read tasks/3.3-camera.md only
User asks about Phase 2 → Read phases/02-entity-system.md only
User asks for overview → Read README.md only
```

Never load the entire plan into context at once.

### 2. Task Tracking with Obsidian Comments

Track open questions and tasks using hidden Obsidian comments:

```markdown
%% [ ] this is an open question/task %%
%% [x] this was completed → see [[research/result]] %%
```

To find all open tasks:
```bash
grep -r '%% \[ \]' path/to/plan/
```

When completing a task:
1. Change `[ ]` to `[x]`
2. Add arrow `→` with link to result
3. Add entry to changelog.md

### 3. Research Workflow

When a `%% [ ] %%` comment needs research:

**Simple question:** Launch single oracle agent (Task tool with general-purpose)

**Complex/uncertain:** Use Delphi pattern (3 parallel oracles + synthesis)
- Launch 3 agents with same question but different search angles
- Synthesize results into single research document
- Store in `research/` directory

**After research:**
```markdown
%% [x] question → Delphi complete: [[research/topic-delphi]] %%
> **Research:** See [[research/topic]] for details
```

### 4. Changelog Protocol

Every change must be logged in `changelog.md` using Keep a Changelog format:

```markdown
## YYYY-MM-DD (Session N)

### Added
- [[path/to/file]] - Description

### Changed
- [[path/to/file]] - What changed and why

### Research
- **Topic:** Summary of findings
```

### 5. Wiki-Link Format

Use Obsidian wiki-links for all internal references:

```markdown
[[tasks/1.1-project-structure]]           # Same directory
[[../research/unity-cinemachine]]         # Relative path
[[tasks/4.1-ui-framework|UI Framework]]   # With display text
```

## File Templates

### README.md Template

```markdown
# Project Name

> **For Claude:** Read specific phase/task files as needed. Don't load everything at once.

**Goal:** [One sentence goal]

**Tech Stack:** [Key technologies]

---

## Quick Links

- [[CLAUDE]] - **Rules for Claude** (read first)
- [[changelog]] - Amendment history with links

## Research

- [[research/topic]] - Description

## Phases

| Phase | Description | File |
|-------|-------------|------|
| 1 | Phase Name | [[phases/01-name]] |
| 2 | Phase Name | [[phases/02-name]] |

## Task Index

### Phase 1: Name
- [[tasks/1.1-slug|1.1 Task Title]]
- [[tasks/1.2-slug|1.2 Task Title]]
```

### Task File Template

```markdown
# Task X.Y: Title

**Phase:** N - Phase Name
**Commit:** `type(scope): description`

%% [ ] any open questions %%

> **Research:** See [[../research/topic]] if applicable

## Overview
[Brief description]

## Files
- Create: `path/to/file.ext`
- Update: `path/to/existing.ext`

## Steps

### Step 1: Name
[Implementation details]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

### CLAUDE.md Template

See `references/claude-template.md` for the full template.

## Workflow Patterns

### Creating a New Plan

1. Create directory structure (see above)
2. Write README.md with phase overview
3. Create CLAUDE.md with plan-specific rules
4. Initialize changelog.md
5. Create phase files with task lists
6. Create individual task files as needed

### Processing Open Tasks

1. Find open tasks: `grep -r '%% \[ \]' path/to/plan/`
2. For each task:
   - Read the file containing the task
   - Determine if research is needed
   - Execute research (oracle or Delphi)
   - Update task marker to `[x]` with result link
   - Update changelog

### Adding Research

1. Create file in `research/` directory
2. Use descriptive name: `topic-name.md` or `topic-delphi.md` for Delphi synthesis
3. Include metadata header:
   ```markdown
   > **Research Type:** Oracle | Delphi
   > **Date:** YYYY-MM-DD
   > **Topic:** Brief description
   ```
4. Update research index if exists
5. Link from relevant task files
6. Add to changelog

### Converting Diagrams to Mermaid

Replace ASCII art and text flow diagrams with Mermaid:

```markdown
# Before (ASCII)
Phase 1 → Phase 2 → Phase 3

# After (Mermaid)
​```mermaid
graph LR
    P1[Phase 1] --> P2[Phase 2] --> P3[Phase 3]
​```
```

Preserve directory trees as-is (they're fine as ASCII).

## Best Practices

1. **Keep files focused** - One topic per file, link to related content
2. **Use consistent naming** - `{phase}.{task}-{slug}.md` for tasks
3. **Update changelog immediately** - Don't batch changes
4. **Preserve deferred work** - Never delete, move to `deferred.md`
5. **Version before major changes** - Copy to `{filename}.v{n}.md`
6. **Research before deciding** - Use oracles for uncertain questions
