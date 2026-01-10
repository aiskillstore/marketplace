---
name: self-test
description: Pattern for testing your own code during implementation. Ensures quality before declaring complete.
allowed-tools: Bash, Read
---

# Self-Test Skill

Pattern for iterative testing during implementation.

## When to Load This Skill

- You are implementing code
- You need to verify your work before completing
- You want to catch issues early

## Self-Test Loop

```
WHILE implementation not complete:
    Write/modify code
        ↓
    Write tests for new code
        ↓
    Run tests
        ↓
    FAIL? → Fix code, retry
        ↓
    Run lint
        ↓
    FAIL? → Fix issues, retry
        ↓
    Run typecheck
        ↓
    FAIL? → Fix types, retry
        ↓
    Continue to next piece
```

## Running Tests

Use project-specific test commands:
@.claude/skills/project/run-tests/SKILL.md

Common patterns:
```bash
# Run specific test file
npm test -- --testPathPattern={file}
pytest {file} -v

# Run affected tests
npm test -- --changedSince=HEAD
```

## Running Lint/Typecheck

Use project-specific commands:
@.claude/skills/project/lint/SKILL.md

Common patterns:
```bash
# TypeScript
npx tsc --noEmit
npx eslint {files} --fix

# Python
mypy {files}
ruff check {files} --fix
```

## Before Declaring Pre-Complete

Checklist:
- [ ] New code has tests
- [ ] All tests pass
- [ ] Lint passes
- [ ] Typecheck passes
- [ ] No console errors/warnings

If ANY fails, status is NOT `pre_complete`.

## Principles

- **Test as you go** - Don't batch at the end
- **Fix immediately** - Don't accumulate failures
- **Be honest** - Report actual status
