# Task Description Templates

## Standard Section Task

```markdown
## Task

Write Section [X] "[Section Title]" of `/path/to/document.md`.

## Required Skill

**MUST use doc writer skill** - Invoke `document-skills:doc-coauthoring` skill before writing.

## Context

[2-3 sentences providing essential background. Assume a fresh agent with no prior context. Include project name, what it does, and relevant tech stack.]

## Scope

[Bullet list of specific topics to cover]

- Topic A with specific details
- Topic B referencing specific files
- Diagrams or tables to create
- What NOT to include (boundaries)

## Source Files to Reference

- `path/to/main/file.ts` - [brief description]
- `path/to/config.json` - [brief description]
- `path/to/README.md` - [brief description]

## Output

Edit `/path/to/document.md` replacing "TODO: Section pending" under Section [X] with complete content.

## Acceptance Criteria

- [ ] All scope items addressed
- [ ] Source files accurately referenced
- [ ] Diagrams included where specified
- [ ] Consistent with document style

## Delegation Rule

If this section exceeds [N] words, scaffold subsections and create new VK tasks using vibe_kanban MCP tools (project_id: [UUID]):

- [X.1] Subsection A
- [X.2] Subsection B

## VK Task ID: [task-uuid]

When done, update this task to "inreview" status in VK.
```

## Complex Technical Section Task

```markdown
## Task

Write Section [X] "[Technical Component Name]" of `/path/to/document.md`.

## Required Skill

**MUST use doc writer skill** - Invoke `document-skills:doc-coauthoring` skill before writing.

## Context

[Component name] is a [brief description of what it is and why it exists]. It uses [key technologies] to achieve [main goal].

## Scope

### Architecture

- System diagram showing component relationships
- Data flow between components
- Key interfaces and APIs

### Implementation Details

- Core modules and their responsibilities
- Configuration options
- Extension points

### Usage

- Basic usage example
- Advanced configuration
- Common patterns

## Source Files to Reference

- `src/core/main.ts` - Entry point and initialization
- `src/lib/` - Core library modules
- `config/` - Configuration files
- `tests/` - Test files showing usage patterns

## Output

Edit document Section [X]. Create ASCII diagrams for architecture. Include code snippets from source files.

## Delegation Rule

**CRITICAL**: This is a complex section. If content exceeds 600 words, MUST split into sub-tasks:

- [X.1] Architecture Overview
- [X.2] Implementation Deep Dive
- [X.3] Usage Guide

Create sub-tasks using:
```

mcp**vibe_kanban**create_task:
project_id: [UUID]
title: "Doc: Section X.1 - [Subsection Name]"
description: [use this template]

```text

## VK Task ID: [task-uuid]
```

## Overview/Summary Section Task

```markdown
## Task

Write Section [X] "[Overview Section]" of `/path/to/document.md`.

## Required Skill

**MUST use doc writer skill** - Invoke `document-skills:doc-coauthoring` skill before writing.

## Context

This is an overview section for [document/project name]. Summarize the entire [scope] at a high level for readers who need quick orientation.

## Scope

- Purpose and goals (2-3 sentences)
- Key components overview (bullet list)
- Target audience identification
- Document structure guide ("Section X covers Y")

## Source Files to Reference

- All project README.md files for component summaries
- Recent git log for evolution context: `git log --oneline -20`

## Output

Edit document Section [X]. Keep concise (<400 words). Use bullet points for scanability.

## VK Task ID: [task-uuid]
```

## Utility/Minor Section Task

```markdown
## Task

Write Section [X] "[Utility Section]" of `/path/to/document.md`.

## Required Skill

**MUST use doc writer skill** - Invoke `document-skills:doc-coauthoring` skill before writing.

## Context

Brief overview of utility components that support main functionality.

## Scope

For each utility:

- Purpose (1 sentence)
- Status (active/deprecated/experimental)
- Key files
- Usage notes

## Source Files to Reference

- `utility_a/README.md`
- `utility_b/README.md`

## Output

Edit document Section [X]. Use consistent format per utility. Keep brief.

## VK Task ID: [task-uuid]
```

## Security/Critical Section Task

```markdown
## Task

Write Section [X] "Security Considerations" of `/path/to/document.md`.

## Required Skill

**MUST use doc writer skill** - Invoke `document-skills:doc-coauthoring` skill before writing.

## Context

[Project] handles [sensitive operations]. Document the security model clearly, including what IS and IS NOT protected.

## Scope

### Protected Against

- Attack vector A: How it's mitigated
- Attack vector B: How it's mitigated

### Trust Assumptions

- What components must be trusted
- External dependencies

### Known Limitations

- What is NOT secured
- Acceptable risk areas

### Audit Checklist

- [ ] Verification point 1
- [ ] Verification point 2

## Source Files to Reference

- `contracts/src/Security.sol` - Security-related code
- `src/crypto/` - Cryptographic implementations
- Code comments mentioning security

## Output

Edit document Section [X]. Be explicit about what IS and IS NOT secured. No security theater.

## Delegation Rule

If complex, split into:

- [X.1] Security Model
- [X.2] Trust Assumptions
- [X.3] Audit Guide

## VK Task ID: [task-uuid]
```

## MCP Tool Reference

### Create Task

```text
mcp__vibe_kanban__create_task:
  project_id: "uuid-here"
  title: "Doc: Section X - Title"
  description: "full markdown description"
```

### Update Task Status

```text
mcp__vibe_kanban__update_task:
  task_id: "uuid-here"
  status: "inprogress" | "inreview" | "done" | "cancelled"
```

### Start Task Attempt (if repos configured)

```text
mcp__vibe_kanban__start_workspace_session:
  task_id: "uuid-here"
  executor: "CLAUDE_CODE"
  repos: [{"repo_id": "uuid", "base_branch": "main"}]
```
