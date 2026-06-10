# Prompt Snippets

Use these as starting points. Replace bracketed sections with project-specific details.

## Planning

```text
Read the relevant files first, then propose a short implementation plan. Keep the plan scoped to [feature/bug]. Do not edit files yet.
```

## Implementation

```text
Implement [specific outcome]. Follow existing project patterns. Keep changes limited to [files/modules]. Do not revert unrelated changes. Run [validation commands] before the final response.
```

## Code Review

```text
Review this change as a senior engineer. Prioritize bugs, regressions, missing tests, unsafe assumptions, and security issues. Put findings first with file and line references.
```

## Recovery When The Agent Drifts

```text
Stop expanding scope. Return to the original acceptance criteria:
- [criterion 1]
- [criterion 2]
- [criterion 3]

List any changes outside that scope and whether they are necessary. Do not make more edits until this is clear.
```

## Delegation

```text
Split this into independent agent tasks with disjoint write scopes. For each task, give the files owned, expected output, acceptance criteria, and validation commands.
```

## Final Verification

```text
Before finalizing, run the agreed checks and inspect the diff. Report:
- Files changed
- Commands run
- Result
- Known risks
- Follow-ups that should not block shipping
```
