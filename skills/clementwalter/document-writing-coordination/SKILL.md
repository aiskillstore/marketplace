---
name: Document Writing Coordination
description: This skill should be used when the user asks to "coordinate document writing", "manage doc writers", "create a design document with multiple writers", "orchestrate documentation", "delegate doc sections", "cos for documentation", "chief of staff for docs", or needs to break a large document into sections and delegate writing to multiple agents via VibeKanban.
version: 1.0.0
---

# Document Writing Coordination via VibeKanban

Coordinate multi-section document creation by delegating to doc writer agents through VibeKanban task management. The coordinator (Chief of Staff) plans and monitors but never writes content directly.

## Core Principles

### Role Separation

| Role                  | Responsibility                     | Does NOT           |
| --------------------- | ---------------------------------- | ------------------ |
| **Coordinator (You)** | Outline, delegate, monitor, review | Write content      |
| **Doc Writers**       | Write assigned sections            | Plan or coordinate |
| **Reviewer (You)**    | Approve/reject, ensure consistency | Implement fixes    |

### Workflow Overview

```text
1. Explore codebase → Understand scope
2. Create outline → Scaffold document structure
3. Create VK tasks → One per section
4. Spawn attempts → Launch doc writer agents
5. Monitor → Poll status periodically
6. Review → Approve or send back
7. Consistency check → After each merge
8. Complete → When no pending tasks remain
```

## Phase 1: Document Outline Creation

### Explore First

Before creating the outline, thoroughly explore the codebase:

```text
Use Task tool with subagent_type=Explore to understand:
- Project structure and components
- Key technologies and patterns
- Existing documentation
- Recent changes and evolution
```

### Create Skeleton Document

Write the document outline with:

- Table of contents with all sections
- HTML comments in each section describing scope
- "TODO: Section pending" placeholder for content
- Clear section numbering (1, 2, 3.1, 3.2, etc.)

Example section scaffold:

```markdown
## 3.1 Component Name

<!--
SCOPE: What this section covers
- Key topics to address
- Source files to reference
- Diagrams to include
-->

TODO: Section pending
```

## Phase 2: Task Creation

### Task Description Template

Each VK task MUST include:

```markdown
## Task

Write Section X "Section Title" of `/path/to/document.md`.

## Required Skill

**MUST use doc writer skill** - Invoke `document-skills:doc-coauthoring` skill before writing.

## Context

[2-3 sentences of essential background for a fresh agent]

## Scope

- [Bullet list of what to cover]
- [Specific topics]
- [Diagrams to create]

## Source Files to Reference

- `path/to/relevant/file.ts`
- `path/to/another/file.md`

## Output

Edit `/path/to/document.md` replacing "TODO: Section pending" under Section X with complete content.

## Delegation Rule

If this section exceeds [N] words, scaffold subsections and create new VK tasks using vibe_kanban MCP tools (project_id: [UUID]):

- X.1 Subsection A
- X.2 Subsection B

## VK Task ID: [task-uuid]

When done, mark task as "inreview" in VK.
```

### Key Task Properties

- **Title format**: `Doc: Section X.Y - Section Name`
- **Context**: Succinct, self-contained for fresh agent
- **Skill requirement**: Explicit doc-coauthoring skill invocation
- **Delegation rule**: Word limit triggers for cascading
- **VK tracking**: Include task ID for status updates

### Creating Tasks via MCP

```text
mcp__vibe_kanban__create_task:
  project_id: [project-uuid]
  title: "Doc: Section 1 - Executive Summary"
  description: [full template above]
```

## Phase 3: Spawning Attempts

### VK Attempt Requirements

To spawn agents via VK `start_workspace_session`:

```text
mcp__vibe_kanban__start_workspace_session:
  task_id: [task-uuid]
  executor: CLAUDE_CODE
  repos: [{repo_id: [repo-uuid], base_branch: main}]
```

**Critical**: Requires `repo_id` from VK project configuration. Use `list_repos` to retrieve, or ask user to configure repository in VK dashboard first.

### Fallback: Task Tool

If VK repos not configured, use hybrid approach:

1. Update VK task status to `inprogress`
2. Spawn agent via Task tool with full context
3. Update VK to `inreview` when agent completes

```text
mcp__vibe_kanban__update_task:
  task_id: [uuid]
  status: inprogress

Task tool:
  subagent_type: general-purpose
  prompt: [task description]
  run_in_background: true
```

## Phase 4: Monitoring

### Status Polling

Poll VK every ~60 seconds during active work:

```text
mcp__vibe_kanban__list_tasks:
  project_id: [uuid]
  status: inprogress  # or inreview, todo
```

### Status Report Format

```markdown
## Backlog Status

| Section         | Task ID | Status     | Notes            |
| --------------- | ------- | ---------- | ---------------- |
| 1. Exec Summary | 88e5... | inreview   | Ready for review |
| 2. Repo Org     | f722... | inprogress | Writing          |
| 3.1 Benchmark   | 371c... | todo       | Blocked          |

**Active**: 5/15 | **In Review**: 2 | **Done**: 8
```

## Phase 5: Review Process

### When Task Reaches `inreview`

1. Read the updated document section
2. Check for:
   - Accuracy against source files
   - Consistency with other sections
   - Completeness per scope
   - Proper formatting and diagrams
3. Decision:
   - **Approve**: Update to `done`, check doc consistency
   - **Reject**: Update to `inprogress` with feedback task

### Rejection Feedback

Create follow-up task or update description:

```markdown
## Revision Required

**Issues Found:**

- [ ] Missing architecture diagram
- [ ] Incorrect API reference in line 45
- [ ] Inconsistent terminology (use "coprocessor" not "processor")

**Action**: Fix issues and return to inreview.
```

## Phase 6: Consistency Reviews

After each section merges to `done`:

1. Read entire document
2. Check cross-references between sections
3. Verify terminology consistency
4. Ensure no duplicate content
5. If issues found, create new VK tasks for fixes

## Completion Criteria

Task is complete when:

- All VK tasks in `done` status
- No pending or in-progress tasks
- Document passes consistency review
- User confirms acceptance

## Quick Reference

### VK MCP Tools

| Tool                      | Purpose                      |
| ------------------------- | ---------------------------- |
| `list_projects`           | Get project UUIDs            |
| `list_tasks`              | View all tasks with status   |
| `create_task`             | Create new section task      |
| `update_task`             | Change status/description    |
| `get_task`                | Get task details             |
| `start_workspace_session` | Launch agent (needs repo_id) |
| `list_repos`              | Get repository UUID          |

### Task Status Flow

```text
todo → inprogress → inreview → done
                  ↘ (rejected) → inprogress
```

### Coordinator Commands

- "Create outline for [doc]" → Phase 1
- "Delegate sections" → Phase 2-3
- "Check status" → Phase 4
- "Review [section]" → Phase 5
- "Consistency check" → Phase 6

## Additional Resources

### Reference Files

- **`references/task-templates.md`** - Full task description templates
- **`references/review-checklist.md`** - Detailed review criteria

### Examples

- **`examples/design-doc-outline.md`** - Sample document skeleton
- **`examples/section-task.md`** - Complete task description example
