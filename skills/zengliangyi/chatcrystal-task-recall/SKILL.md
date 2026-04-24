---
name: chatcrystal-task-recall
description: Recall project-first and global-supplement ChatCrystal memories before substantive implementation, refactoring, migration, configuration, investigation, or optimization work. Use when the task is non-trivial, has repository or project context, and prior fixes, decisions, pitfalls, or reusable patterns may change the approach.
---

# ChatCrystal Task Recall

Use this skill as a thin workflow on top of ChatCrystal Core. Do not invent a parallel memory system in the skill.

## Workflow

1. Decide whether the task is substantial enough to justify recall.
2. Trigger for non-trivial `implement`, `refactor`, `migration`, `config`, `investigate`, or `optimization` work.
3. Skip trivial edits, one-line answers, or purely conversational requests.
4. If `recall_for_task` is available, call it before substantive work with:
   - `mode: "task"`
   - `task.goal`: the concrete task objective
   - `task.task_kind`: the best matching task kind
   - `task.project_dir` and `task.cwd` when repository context exists
   - `task.branch` when known
   - `task.related_files` or `task.files_touched` when known
   - `task.source_agent` when the runtime has a stable value
5. Treat `project_memories` as primary context and `global_memories` as supplemental context.
6. Apply recalled pitfalls, patterns, and prior decisions before proposing or writing code.

## Example MCP Input

Use this shape when calling `recall_for_task` for implementation or investigation work:

```json
{
  "mode": "task",
  "task": {
    "goal": "Add a paginated notes export endpoint",
    "task_kind": "implement",
    "project_dir": "/path/to/project",
    "cwd": "/path/to/project",
    "branch": "feature/export-notes",
    "related_files": [
      "server/src/routes/notes.ts",
      "shared/types/index.ts"
    ],
    "source_agent": "codex"
  },
  "options": {
    "project_limit": 5,
    "global_limit": 3,
    "include_relations": true
  }
}
```

## Full Mode

Full mode requires ChatCrystal Core plus MCP access to `recall_for_task`.

- Prefer the current repository or workspace path so Core can derive `project_key`.
- Surface relevant warnings such as `no-project-key` or `no-matches`, but do not treat them as failures.
- If recall returns nothing useful, continue the task normally.

## Degraded Mode

If ChatCrystal Core or the MCP tool is unavailable:

- Continue the task without blocking.
- State briefly that long-term recall is unavailable in this environment.
- Do not claim that any memory was recalled.
- Do not instruct the runtime to auto-install ChatCrystal Core as part of the skill flow.
