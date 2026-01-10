---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: git-commit-helper
---

# Git Commit Message Template

Follow Conventional Commits specification for consistent, machine-readable commit history.

## Commit Message Structure

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types

| Type | Description | SemVer Impact |
|------|-------------|---------------|
| `feat` | New feature | MINOR |
| `fix` | Bug fix | PATCH |
| `docs` | Documentation only | - |
| `style` | Formatting, no code change | - |
| `refactor` | Code change, no feature/fix | - |
| `perf` | Performance improvement | PATCH |
| `test` | Adding/updating tests | - |
| `build` | Build system/dependencies | - |
| `ci` | CI configuration | - |
| `chore` | Maintenance tasks | - |
| `revert` | Revert previous commit | - |

## Examples

### Simple Feature

```
feat: add user authentication endpoint
```

### Feature with Scope

```
feat(auth): add OAuth2 login support
```

### Bug Fix with Issue Reference

```
fix: resolve null pointer in user service

The getUser method was not handling missing records properly.

Closes #123
```

### Breaking Change (Footer)

```
feat: update API response format

BREAKING CHANGE: response now returns data in `items` array instead of `results`
```

### Breaking Change (Type Prefix)

```
feat!: drop support for Node 14
```

### Multi-paragraph Body

```
fix(parser): handle edge cases in date parsing

Previously the parser would fail silently on malformed dates.
Now it throws a descriptive error with the invalid input.

This change affects all date fields in the API response.

Reviewed-by: Jane Doe
Refs: #456
```

## Footer Tokens

| Token | Purpose |
|-------|---------|
| `BREAKING CHANGE:` | Indicates breaking API change |
| `Closes #N` | Auto-closes issue N |
| `Fixes #N` | Auto-closes issue N |
| `Refs: #N` | References issue without closing |
| `Reviewed-by:` | Code reviewer attribution |
| `Co-authored-by:` | Pair programming attribution |

## Claude Code Attribution

When Claude generates the commit:

```
feat(api): implement rate limiting

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Rules

1. Type is REQUIRED and lowercase
2. Scope is OPTIONAL, noun in parentheses
3. Description is REQUIRED, imperative mood ("add" not "added")
4. Body is OPTIONAL, separated by blank line
5. Footer is OPTIONAL, separated by blank line
6. Breaking changes MUST be indicated with `!` or `BREAKING CHANGE:` footer
7. Maximum 72 characters for subject line
8. Use present tense ("add feature" not "added feature")

## Quality Checklist

- [ ] Type matches the change category
- [ ] Description is concise and imperative
- [ ] Subject line under 72 characters
- [ ] Body explains WHY, not just WHAT
- [ ] Breaking changes clearly indicated
- [ ] Issue references included if applicable
