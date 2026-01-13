# Quick Tasks Template

Minimal task file for simple features.

## Template

```markdown
# Tasks: {title}

- [ ] T001: {main implementation task} [P1]
- [ ] T002: {verification/testing task} [P1]
- [ ] T003: {cleanup if needed} [P2]
```

## Guidelines

- 2-5 tasks maximum
- No parallel groups needed
- No complex dependencies
- P1 for required, P2 for optional

## Example

```markdown
# Tasks: Add user avatar support

- [ ] T001: Add avatar_url field to User model [P1]
- [ ] T002: Update profile API to accept avatar uploads [P1]
- [ ] T003: Add avatar display to profile component [P1]
- [ ] T004: Write tests for avatar upload [P1]
- [ ] T005: Update API documentation [P2]
```
