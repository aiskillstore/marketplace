---
name: managing-workflow
description: |
  Manages the specification-driven development workflow. Use this skill when the user runs /orbit,
  requests to "define feature", "create plan", "implement", or needs workflow guidance.
  It detects the current phase from artifacts and executes the appropriate action.
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - AskUserQuestion
---

# Orbit Workflow

Single skill for specification-driven development. **Artifacts are the source of truth.**

## Initialization

<context-loading>
Before any workflow action, load full context with a single Bash call:

```bash
node plugins/spec/skills/managing-workflow/scripts/context-loader.js
```

This returns JSON with:
- `suggestion`: Recommended next action
- `current`: Active feature state and artifacts
- `features.active`: All features with frontmatter state
- `features.in_progress`: Features needing attention
- `architecture_files`: Available architecture docs

Use this context for all decisions. Avoid additional Read calls for state detection.
</context-loading>

## Phase Detection

Phase is stored in spec.md frontmatter `status` field:

| Status | Artifacts | Next Action |
|--------|-----------|-------------|
| `initialize` | None | Create spec.md |
| `specification` | spec.md (no [CLARIFY]) | Create plan.md |
| `clarification` | spec.md with [CLARIFY] | Resolve questions |
| `planning` | spec.md + plan.md | Create tasks.md |
| `implementation` | tasks.md has `- [ ]` | Execute tasks |
| `complete` | All tasks `- [x]` | Archive or new feature |

## Frontmatter Schema

### spec.md Frontmatter

```yaml
---
id: 001-feature-name
title: Human Readable Title
status: specification  # initialize|specification|clarification|planning|implementation|complete
priority: P1           # P1|P2|P3
created: 2025-11-27
updated: 2025-11-27
progress:
  tasks_total: 0
  tasks_done: 0
owner: team-name
tags:
  - api
  - auth
---
```

### Updating Frontmatter

On every phase transition, use the skill's built-in scripts:

```bash
# Update status and timestamp
node plugins/spec/skills/managing-workflow/scripts/update-status.js \
  ".spec/features/{feature}/spec.md" "planning"

# Log activity with ISO timestamp
node plugins/spec/skills/managing-workflow/scripts/log-activity.js \
  ".spec/features/{feature}/metrics.md" "Plan created"
```

Or with Edit tool - update the status line in frontmatter.

## Phase Gates (MANDATORY)

**You MUST validate before ANY phase transition. This is NOT optional.**

```bash
# REQUIRED before every phase change
RESULT=$(node plugins/spec/skills/managing-workflow/scripts/validate-phase.js \
  ".spec/features/{feature}" "{target-phase}")

# Check result - DO NOT PROCEED if invalid
if [[ $(echo "$RESULT" | jq -r '.valid') != "true" ]]; then
  echo "BLOCKED: $(echo "$RESULT" | jq -r '.suggestion')"
  # Create the missing artifact before continuing
fi
```

### Phase Prerequisites

| Target Phase | Required Artifacts | If Missing |
|--------------|-------------------|------------|
| specification | None | - |
| clarification | spec.md | Create spec first |
| planning | spec.md (no [CLARIFY]) | Resolve clarifications |
| implementation | spec.md, plan.md, tasks.md | Create missing artifacts |
| complete | All tasks `[x]` | Complete remaining tasks |

### Enforcement Rules

1. **NEVER skip directly to implementation** - plan.md and tasks.md MUST exist
2. **NEVER mark complete with unchecked tasks** - all `[ ]` must be `[x]`
3. **If validation fails**: Create the missing artifact, don't proceed
4. **For simple features**: Use quick-plan template (see plugins/spec/skills/managing-workflow/templates/quick-plan.md)

### Quick Planning Option

For simple features (bug fixes, < 3 files), use streamlined templates:
- `plugins/spec/skills/managing-workflow/templates/quick-plan.md` - Combined plan with inline tasks
- `plugins/spec/skills/managing-workflow/templates/quick-tasks.md` - Minimal task list

This ensures artifacts exist while reducing overhead for small changes.

## Workflow Actions

### Initialize New Feature

1. Ask user for feature name and description
2. Generate feature ID: `{NNN}-{kebab-name}`
3. Create directory and files in parallel:

```bash
mkdir -p .spec/features/{id}
```

Create these files simultaneously:
- `spec.md` with frontmatter
- `metrics.md` with tracking template

4. Set session: `set_feature "{id}"`

### spec.md Template

```markdown
---
id: {id}
title: {title}
status: specification
priority: P2
created: {date}
updated: {date}
progress:
  tasks_total: 0
  tasks_done: 0
---

# Feature: {title}

## Overview

{description}

## User Stories

### US1: {story title}

As a {role}, I want {goal} so that {benefit}.

**Acceptance Criteria:**
- [ ] AC1.1: {criterion}
- [ ] AC1.2: {criterion}

## Technical Constraints

- {constraint}

## Out of Scope

- {exclusion}
```

### metrics.md Template

```markdown
# Metrics: {title}

## Progress

| Phase | Status | Updated |
|-------|--------|---------|
| Specification | pending | |
| Clarification | pending | |
| Planning | pending | |
| Implementation | 0/0 | |

## Activity

| Timestamp | Event |
|-----------|-------|
```

Note: All timestamps use ISO 8601 format: `2025-11-27T10:30:00Z`

### Define Specification

1. Load context to check for related archived features
2. If related found, ask: "Found similar feature '{name}'. Reference it?"
3. Ask user for feature requirements (use AskUserQuestion for scope/priority)
4. Generate user stories with acceptance criteria
5. Mark unclear items with `[CLARIFY]`
6. **Ask user to review `spec.md`**
7. If approved:
   - Update frontmatter: `status: specification` (or `clarification` if tags exist)
   - Update metrics.md

### Clarify

1. Find all `[CLARIFY]` tags in spec.md
2. Batch into groups of max 4 questions
3. Use AskUserQuestion to resolve each batch
4. Update spec.md with answers, remove `[CLARIFY]` tags
5. **Ask user to review changes**
6. When all resolved and approved, update frontmatter: `status: specification`

### Create Plan

1. Validate spec completeness (no [CLARIFY] tags)
2. Read spec.md
3. Generate technical plan with:
   - Architecture decisions
   - Components and their purposes
   - Data models
   - API design (if applicable)
   - Integration points
4. Write plan.md
5. **Ask user to review `plan.md`**
6. If approved:
   - Update frontmatter: `status: planning`
   - Update metrics.md

### plan.md Template

```markdown
# Technical Plan: {title}

## Architecture

{architecture decisions and rationale}

## Components

| Component | Purpose | Dependencies |
|-----------|---------|--------------|
| {name} | {purpose} | {deps} |

## Data Models

{model definitions}

## API Design

{endpoints if applicable}

## Implementation Phases

1. **Phase 1**: {description}
2. **Phase 2**: {description}

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| {risk} | {impact} | {mitigation} |
```

### Create Tasks

1. Read spec.md + plan.md
2. Break into tasks with parallel groups and dependencies:

```markdown
## Parallel Group A
- [ ] T001: {task} [P1]
- [ ] T002: {task} [P1]

## Parallel Group B [depends:A]
- [ ] T003: {task} [P1] [depends:T001,T002]
```

3. Tag critical changes: `[critical:schema]`, `[critical:api]`, `[critical:types]`
4. Write tasks.md
5. **Ask user to review `tasks.md`**
6. If approved:
   - Update frontmatter: `status: implementation`
   - Update progress in frontmatter: `tasks_total: {count}`
   - Update metrics.md

### tasks.md Template

```markdown
# Tasks: {title}

## Parallel Group A

- [ ] T001: {description} [P1]
- [ ] T002: {description} [P1]

## Parallel Group B [depends:A]

- [ ] T003: {description} [P1] [depends:T001,T002]
- [ ] T004: {description} [P2] [depends:T001]

## Sequential

- [ ] T005: {description} [P1] [critical:api] [depends:T003,T004]

---

## Legend

- `[P1/P2/P3]` - Priority level
- `[depends:X,Y]` - Task dependencies
- `[critical:type]` - Requires extra review (schema, api, types, auth)
- `[estimate:S/M/L]` - Size estimate
```

### Implement

**GATE CHECK REQUIRED** - Before implementing, MUST validate:

```bash
# MANDATORY: Run this before any implementation
RESULT=$(node plugins/spec/skills/managing-workflow/scripts/validate-phase.js \
  ".spec/features/{feature}" "implementation")

# If not valid, STOP and create missing artifacts
if [[ $(echo "$RESULT" | jq -r '.valid') != "true" ]]; then
  MISSING=$(echo "$RESULT" | jq -r '.missing')
  echo "Cannot implement: missing $MISSING"
  # Go back and create: plan.md or tasks.md
fi
```

**Only after validation passes**, delegate to `task-implementer` agent:

```
Task: task-implementer agent

Feature: {feature-path}
Tasks file: .spec/features/{feature}/tasks.md

Execute tasks in parallel groups where possible.
Update task checkboxes as completed.
Report any blockers.
```

After implementation:
- Update frontmatter progress: `tasks_done: {count}`
- If all complete, update: `status: complete`

### Validate

Delegate to `artifact-validator` agent:

```
Task: artifact-validator agent

Feature: {feature-path}

Validate:
1. Spec completeness (all AC have tasks)
2. Plan coverage (all US have implementation)
3. Task consistency (dependencies valid)
```

### Archive Feature

When feature is complete:

1. Ask user: "Archive this feature?"
2. If yes:
   a. Check for repeatable patterns in completed work
   b. If patterns detected (2+ similar files/tasks), offer tooling suggestions
3. Run archive_feature

```bash
node plugins/spec/skills/managing-workflow/scripts/archive-feature.js "{feature-id}"
```

3. If new skills/agents were created during the feature:
   - Inform user: "New tooling was created. Restart Claude to use it."
   - Suggest: `claude --continue` to resume after restart
4. Suggest next action from context loader

### Tooling Check on Archive

Before archiving, analyze the completed feature for automation opportunities:

```
Pattern Detection (only for repeatable tasks):
- Created 3+ similar files? → Suggest generator skill
- Wrote 3+ test files? → Suggest testing-code skill
- Added 3+ API endpoints? → Suggest api-testing agent
- Similar task structure repeated? → Suggest workflow skill
```

**Skip tooling suggestions if:**
- Feature was one-off (migration, unique integration)
- Pattern count < 2
- Similar tooling already exists

If tooling is created:
```markdown
## New Tooling Created

| Type | Name | Location |
|------|------|----------|
| Skill | {name} | .claude/skills/{name}/ |
| Agent | {name} | .claude/agents/{name}.md |

**Restart Required**: Run `claude --continue` to use new tooling.
```

## User Questions

Use AskUserQuestion strategically:

### On Initialize
```yaml
questions:
  - header: "Project Type"
    question: "What type of project is this?"
    options:
      - label: "Greenfield"
        description: "New project from scratch"
      - label: "Brownfield"
        description: "Existing codebase"
```

### On Feature Selection (multiple features)
```yaml
questions:
  - header: "Feature"
    question: "Which feature to work on?"
    options:
      - label: "{feature-1}"
        description: "{status} - {progress}"
      - label: "{feature-2}"
        description: "{status}"
      - label: "New Feature"
        description: "Start fresh"
```

### On Implementation Start
```yaml
questions:
  - header: "Execution"
    question: "How to execute tasks?"
    options:
      - label: "Guided"
        description: "Confirm each task"
      - label: "Autonomous"
        description: "Execute all, report at end"
```

## Error Handling

- Missing artifact → Start from that phase
- Validation fails → Show gaps, offer to fix
- Task blocked → Log blocker, skip to next, report at end
- Frontmatter missing → Add it on next update

## Parallel Execution Guidelines

Execute in parallel when independent:
- File creation (spec.md + metrics.md)
- Multiple validations
- Independent task groups

Execute sequentially when dependent:
- Spec → Plan → Tasks
- Dependent task groups
