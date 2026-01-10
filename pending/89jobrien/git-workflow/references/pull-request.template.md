---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: git-workflow
---

# Pull Request Template

## Title Format

```
<type>[scope]: <short description>
```

Examples:

- `feat(auth): add OAuth2 integration`
- `fix(api): resolve rate limiting bypass`
- `docs: update API documentation`

---

## PR Body Template

```markdown
## Summary

<1-3 bullet points describing what this PR does>

- Implements X feature for Y use case
- Fixes bug where Z happened
- Refactors W to improve maintainability

## Motivation

<Why is this change needed? Link to issue if applicable>

Closes #{{ISSUE_NUMBER}}

## Changes

### Added
- {{NEW_FILE_OR_FEATURE}}

### Changed
- {{MODIFIED_BEHAVIOR}}

### Removed
- {{DEPRECATED_CODE}}

## Test Plan

- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Edge cases considered

### Testing Steps

1. {{STEP_1}}
2. {{STEP_2}}
3. Expected: {{EXPECTED_RESULT}}

## Screenshots

<If UI changes, include before/after screenshots>

| Before | After |
|--------|-------|
| ![before](url) | ![after](url) |

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Dependencies updated in lockfile

## Breaking Changes

<List any breaking changes and migration steps>

- **Before:** `oldMethod()`
- **After:** `newMethod(options)`
- **Migration:** Update all callsites to use new signature

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## Quick Templates

### Feature PR

```markdown
## Summary

- Adds {{FEATURE_NAME}} functionality
- Enables users to {{USER_BENEFIT}}

## Test Plan

- [ ] Happy path tested
- [ ] Error cases handled
- [ ] Performance acceptable

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Bug Fix PR

```markdown
## Summary

- Fixes {{BUG_DESCRIPTION}}
- Root cause: {{ROOT_CAUSE}}

Closes #{{ISSUE}}

## Test Plan

- [ ] Regression test added
- [ ] Original issue no longer reproducible

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Refactor PR

```markdown
## Summary

- Refactors {{COMPONENT}} for improved {{BENEFIT}}
- No functional changes

## Test Plan

- [ ] All existing tests pass
- [ ] No behavior changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Branch Naming

```
<type>/<issue-number>-<short-description>
```

Examples:

- `feat/123-oauth-login`
- `fix/456-null-pointer`
- `refactor/789-extract-utils`

## Quality Checklist

- [ ] PR title follows conventional format
- [ ] Summary explains WHAT and WHY
- [ ] Test plan is specific and actionable
- [ ] Breaking changes documented with migration
- [ ] Linked to issue if applicable
- [ ] Screenshots for UI changes
