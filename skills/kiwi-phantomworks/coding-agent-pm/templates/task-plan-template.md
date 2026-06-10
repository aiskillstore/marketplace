# Coding Agent Task Plan Template

## Project

Name:

Goal:

Owner:

Deadline or review point:

## Current State

- What exists now:
- What is broken or missing:
- Relevant files:
- Relevant commands:

## Target State

- User-visible result:
- Internal behavior:
- Files expected to change:
- Files that should not change:

## Work Plan

1. Inspect the relevant files and current behavior.
2. Make the smallest coherent implementation.
3. Add or update focused tests if the change affects behavior.
4. Run validation commands.
5. Summarize changes, verification, and risks.

## Agent Assignment Prompt

```text
You are working in this codebase with other possible edits in progress. Do not revert unrelated changes.

Goal:
[one sentence]

Scope:
- You own: [files/modules]
- Do not edit: [files/modules]

Context:
[relevant facts]

Acceptance criteria:
- [criterion 1]
- [criterion 2]
- [criterion 3]

Verification:
Run [commands] and report the result.
```

## Human Review Notes

- Surprising changes:
- Missing checks:
- Follow-up tasks:
- Ship decision:
