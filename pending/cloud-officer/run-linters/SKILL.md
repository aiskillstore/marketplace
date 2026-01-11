---
name: run-linters
description: Run linters after code changes to verify code quality. Use this skill after completing code modifications to catch and fix any linting issues.
allowed-tools: Bash(linters:*), Read, Edit
---

# Run Linters

Execute linters after code changes are complete to ensure code quality and consistency.

## When to Use

- After completing a set of code changes (not after each small edit)
- Before creating a commit or PR
- When asked to verify code quality

## Step 1: Run Linters

Execute the `linters` command which auto-detects active linters in the current repository and runs them with proper configurations:

```bash
linters
```

## Step 2: Analyze Results

- If no issues: Report success and proceed
- If issues found: Continue to Step 3

## Step 3: Fix Issues

For each issue reported:

1. Read the affected file
2. Understand the linting error
3. Fix the issue using Edit tool
4. Re-run `linters` to verify the fix

Repeat until all issues are resolved.

## Important Rules

- Do NOT run after every small change - wait until a logical set of changes is complete
- Fix all issues before reporting completion
- If a linting rule seems incorrect, ask the user before disabling it
