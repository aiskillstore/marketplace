---
name: git-commit
description: Guide for breaking changes into logical, atomic commits using interactive staging. Use when committing changes that span multiple concerns, when needing to stage parts of files (hunks), when asked to create well-organized commit history, or when changes should be split into multiple commits.
---

# Git Commit

Break changes into logical, atomic commits using interactive staging.

## Workflow

1. Analyze all changes
2. Identify logical units (one concern per commit)
3. Stage relevant changes (whole files or hunks)
4. Commit with a good message
5. Repeat until all changes are committed

## Analyzing Changes

```bash
git status                 # overview of changed files
git diff                   # unstaged changes
git diff --cached          # staged changes
git diff HEAD              # all changes (staged + unstaged)
```

Look for natural boundaries: different features, bug fixes, refactors, or config changes.

## Identifying Logical Commits

Each commit should represent one logical change. Signs that changes belong in separate commits:

- Different purposes (bug fix vs feature vs refactor)
- Unrelated files or components
- Changes that could be reverted independently
- Separate items from a PR review or task list

Common groupings:
- Related files implementing a single feature
- A bug fix with its test
- Rename/move operations separate from behavior changes
- Config or dependency changes separate from code

## Staging Strategies

### Whole files

```bash
git add <file>             # stage entire file
git add <dir>/             # stage all files in directory
git reset HEAD <file>      # unstage file
```

### Partial files (hunk staging)

Use `git add -p` to stage specific hunks within a file:

```bash
git add -p                 # interactively stage hunks from all files
git add -p <file>          # interactively stage hunks from specific file
```

Hunk commands:
- `y` - stage this hunk
- `n` - skip this hunk
- `s` - split into smaller hunks (if hunk contains multiple changes)
- `q` - quit, keeping already-staged hunks
- `?` - show help

### Verify staged changes

```bash
git diff --cached          # review exactly what will be committed
```

## Commit Messages

Use the **commit-message** skill for formatting. Key points:

- Conventional Commits format: `type(scope): description`
- Imperative mood ("Add feature" not "Added feature")
- Explain why in the body, not what (the diff shows what)

## Repeat

After each commit:

```bash
git status                 # check remaining changes
git log --oneline -3       # verify commit was created
```

Continue staging and committing until all changes are organized into logical commits.
