---
name: chatcrystal-debug-recall
description: Recall ChatCrystal memories for debugging tasks involving failing tests, compiler errors, runtime exceptions, dependency issues, environment breakage, or performance regressions. Use when historical root causes, fixes, or pitfalls may accelerate diagnosis before proposing a fix.
---

# ChatCrystal Debug Recall

Use this skill when the task is clearly about diagnosis or debugging. Keep the skill thin and let ChatCrystal Core handle retrieval.

## Workflow

1. Trigger when the task includes failing tests, compiler errors, runtime exceptions, broken dependencies, environment problems, or performance regressions.
2. If `recall_for_task` is available, call it before proposing a fix with:
   - `mode: "debug"`
   - `task.goal`: the concrete debugging objective
   - `task.task_kind: "debug"`
   - `task.project_dir` and `task.cwd` when known
   - `task.branch` when known
   - `task.related_files` or `task.files_touched` when known
   - `task.error_signatures` populated with the most useful identifiers available
3. Prefer concrete signals such as:
   - failing test names
   - exception classes
   - error codes
   - log signatures
   - package or tool versions when they materially affect the failure
4. Prioritize returned memories that explain root cause, remediation, or known pitfalls.
5. Use recalled memories to sharpen diagnosis, not to skip verification in the current environment.

## Example MCP Input

Use this shape when calling `recall_for_task` for debugging:

```json
{
  "mode": "debug",
  "task": {
    "goal": "Diagnose failing build after TypeScript upgrade",
    "task_kind": "debug",
    "project_dir": "/path/to/project",
    "cwd": "/path/to/project",
    "branch": "upgrade/typescript",
    "related_files": [
      "server/src/cli/mcp/server.ts",
      "tsconfig.base.json"
    ],
    "error_signatures": [
      "TS2322",
      "Type is not assignable"
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

- Keep `project_memories` primary and `global_memories` secondary.
- If the response includes warnings or `no-matches`, continue debugging normally.
- Do not overfit to a recalled fix when the current failure signature diverges materially.

## Degraded Mode

If ChatCrystal Core or the MCP tool is unavailable:

- Continue the debugging task without blocking.
- State briefly that long-term debug recall is unavailable.
- Do not fabricate historical failures, causes, or fixes.
- Do not turn installation commands into automatic skill steps.
