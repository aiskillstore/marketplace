---
name: checkpoint
description: Save current progress to memory-keeper to prevent work loss.
---

# Checkpoint Skill

Automatically checkpoint current progress to memory-keeper to prevent catastrophic work loss when context is exhausted.

## When to Use

- Every 5-10 tool calls during implementation
- After completing a significant piece of work
- Before starting a large operation
- When switching tasks
- Before ending a session
- When explicitly requested via `/checkpoint`

## Checkpoint Actions

### 1. Gather Current State

Collect the following information:
- Current task description from todo list
- List of files modified this session
- Implementation progress (percentage or phase)
- Current blockers or issues
- Next action to take

### 2. Save to Memory-Keeper

```
context_save(key: "current-task", value: "<task description>", category: "progress", priority: "high")
context_save(key: "files-modified", value: "<comma-separated file list>", category: "progress")
context_save(key: "implementation-progress", value: "<percentage or phase>", category: "progress")
context_save(key: "next-action", value: "<exact next step>", category: "progress", priority: "high")
```

### 3. Create Named Checkpoint

```
context_checkpoint(
  name: "checkpoint-<timestamp>",
  description: "Task: <task>, Progress: <progress>, Files: <count>, Next: <action>"
)
```

### 4. Prepare for Compaction (if context is large)

```
context_prepare_compaction()
```

## Checkpoint Frequency Guidelines

| Activity | Checkpoint Frequency |
|----------|---------------------|
| File creation/modification | After every file |
| Running tests | After each test run |
| Research/exploration | Every 10 tool calls |
| Debugging | After each hypothesis tested |
| Multi-step implementation | After each step |

## Key Items to Always Save

| Key | Description | Priority |
|-----|-------------|----------|
| `current-task` | What you're currently working on | high |
| `files-modified` | All files touched this session | normal |
| `implementation-progress` | How far along (%, phase) | normal |
| `next-action` | Exact next step to take | high |
| `blockers` | Current issues/blockers | high |
| `todo-state` | Serialized todo list | normal |

## Checkpoint Output

After checkpointing, confirm with:
```
Checkpoint saved:
- Task: <current task>
- Progress: <progress>
- Files modified: <count>
- Next action: <next step>
```

## Recovery Reference

If context is lost, use `/recover` to restore state from checkpoints.
