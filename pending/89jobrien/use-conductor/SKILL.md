---
name: use-conductor
description: Scan conductor/ directory for project direction, workflows, and task planning when present
---

# Use Conductor

Scan the `conductor/` directory at project root for structured project management files that provide direction, workflows,
and task planning context.

## When to Use

Use this skill when:

- Starting work on a project that may have conductor files
- Looking for project context, guidelines, or current tasks
- Needing to understand the project's workflow methodology
- Determining what work is in progress or next in queue

## Conductor Directory Structure

The conductor system uses this structure:

```text
conductor/
├── product.md              # Product vision and purpose
├── product-guidelines.md   # Standards and conventions
├── tech-stack.md           # Technology decisions
├── workflow.md             # Task execution methodology
├── tracks.md               # Index of active work tracks
├── setup_state.json        # Setup progress state
├── code_styleguides/       # Language-specific style guides
│   ├── general.md
│   └── python.md
└── tracks/                 # Detailed track plans
    └── <track_name>/
        ├── spec.md         # Track specification
        ├── plan.md         # Task checklist with progress
        └── metadata.json   # Track metadata
```

## File Purposes

| File | Purpose |
|------|---------|
| `product.md` | Product vision, target audience, core features |
| `product-guidelines.md` | Naming conventions, quality standards, documentation rules |
| `tech-stack.md` | Approved technologies and libraries |
| `workflow.md` | TDD methodology, task workflow, commit guidelines |
| `tracks.md` | High-level index of all work tracks |
| `tracks/<name>/plan.md` | Detailed task checklist with `[ ]`, `[~]`, `[x]` status |
| `tracks/<name>/spec.md` | Goals, scope, and success criteria for the track |

## How to Scan

1. Check if `conductor/` directory exists at project root
2. If present, read core files to understand project context:
   - `product.md` for vision
   - `product-guidelines.md` for standards
   - `tracks.md` for active work
3. For active tracks (marked `[~]`), read the track's `plan.md` to find current tasks
4. Follow the workflow methodology defined in `workflow.md`

## Task Status Markers

In `plan.md` files:

- `[ ]` - Task not started
- `[~]` - Task in progress
- `[x]` - Task completed (may include commit SHA)

## Integration with Work

When conductor files are present:

1. **Respect the plan** - Follow the task order in `plan.md`
2. **Update status** - Mark tasks as `[~]` when starting, `[x]` when done
3. **Follow workflow** - Use the TDD methodology if specified
4. **Maintain standards** - Follow `product-guidelines.md` and style guides
5. **Stay in scope** - Check `spec.md` for what's in/out of scope

## Example Usage

Before starting work on a project:

```text
User: "What should I work on next?"

Claude: [Checks for conductor/ directory]
        [Reads tracks.md to find active track]
        [Reads tracks/<active>/plan.md to find next [ ] task]
        "According to the conductor plan, the next task is..."
```
