# Commit Patterns and Anti-Patterns

## Good Patterns

### Atomic Commits

Each commit represents one logical change:

```
✅ Good:
feat(auth): add JWT validation
test(auth): add JWT validation tests
docs(auth): document JWT setup

❌ Bad:
feat(auth): implement authentication
(includes validation, tests, docs, and refactoring all mixed together)
```

### Descriptive Messages

Clear about what and why:

```
✅ Good:
fix(api): resolve race condition in user creation

The user creation endpoint had a race condition when multiple
requests arrived simultaneously. Added transaction locks to
ensure atomic user creation.

❌ Bad:
fix bug
```

### Issue Linking

Always link to related issues:

```
✅ Good:
feat(profile): add avatar upload

Implements user avatar upload with automatic resizing and
S3 storage integration.

Closes #142

❌ Bad:
feat(profile): add avatar upload
(no issue reference)
```

## Anti-Patterns

### WIP Commits

```
❌ Avoid:
wip
temp changes
checkpoint
more stuff

✅ Instead:
Squash these before merging, or make them descriptive:
refactor(auth): extract validation logic (WIP)
```

### Vague Messages

```
❌ Avoid:
fix stuff
update code
changes
improvements

✅ Instead:
fix(api): resolve timeout in user search
refactor(utils): simplify date formatting
feat(ui): add loading spinner
perf(database): optimize user queries
```

### Large Commits

```
❌ Avoid:
feat(app): implement entire user management system
(1500 lines changed across 30 files)

✅ Instead:
Split into atomic commits:
feat(user): add user model and database schema
feat(user): add user CRUD API endpoints
feat(user): add user management UI
test(user): add user management tests
docs(user): document user management API
```

### Non-Conventional Format

```
❌ Avoid:
Updated authentication
Fixed the bug
Added new feature

✅ Instead:
refactor(auth): update authentication flow
fix(api): resolve validation error
feat(profile): add avatar upload
```

## Commit Organization Strategies

### Feature Branch Pattern

```
main
  ← feat(auth): add user model
  ← feat(auth): add authentication endpoints
  ← test(auth): add authentication tests
  ← docs(auth): document authentication flow
  ← merge: Merge authentication feature
```

### Squash and Merge

Squash multiple WIP commits into one clean commit before merging:

```
Before merge:
  - wip: started auth
  - wip: more auth work
  - fix: fixed tests
  - wip: final changes

After squash:
  - feat(auth): add JWT authentication system
```

### Rebase and Clean

Use interactive rebase to clean history:

```
git rebase -i main

Commands:
- pick: keep commit as-is
- reword: change commit message
- squash: combine with previous commit
- fixup: like squash but discard message
- drop: remove commit
```

## Commit Size Guidelines

### Ideal Sizes

- **Tiny** (< 10 LOC): Single logical change
  ```
  fix(typo): correct spelling in README
  ```

- **Small** (10-50 LOC): Typical atomic commit
  ```
  feat(api): add user validation endpoint
  ```

- **Medium** (50-200 LOC): Feature component
  ```
  feat(auth): add JWT token management
  ```

- **Large** (200-500 LOC): Consider splitting
  ```
  feat(user): implement user profile management
  (Could split into: model, API, tests)
  ```

- **Too Large** (> 500 LOC): Definitely split
  ```
  feat(app): implement entire authentication system
  (Split into: models, auth logic, endpoints, tests, docs)
  ```

## Special Cases

### Breaking Changes

Always use `!` and document in footer:

```
feat(api)!: change user endpoint structure

BREAKING CHANGE: User endpoint now returns {user: {...}}
instead of direct user object. Update all API clients.

Closes #200
```

### Reverts

Use `revert` type and reference original:

```
revert: revert "feat(auth): add OAuth support"

This reverts commit abc1234.

OAuth integration caused issues with existing authentication.
Will reimplement after refactoring auth system.
```

### Co-Authors

Credit multiple authors:

```
feat(api): add GraphQL endpoint

Implements initial GraphQL API with user queries.

Co-authored-by: Alice <alice@example.com>
Co-authored-by: Bob <bob@example.com>
```

## Review Checklist

Before committing, verify:

- [ ] Atomic: One logical change only
- [ ] Formatted: Follows conventional commits
- [ ] Descriptive: Clear what and why
- [ ] Sized: Not too large (< 500 LOC)
- [ ] Linked: References issues if applicable
- [ ] Tested: Includes or updates tests
- [ ] Docs: Updates documentation if needed

## Tools

### Commitizen

Interactive commit tool:
```bash
npm install -g commitizen
git cz
```

### Commitlint

Validate commit messages:
```bash
npm install --save-dev @commitlint/cli @commitlint/config-conventional
echo "module.exports = {extends: ['@commitlint/config-conventional']}" > commitlint.config.js
```

### Conventional Changelog

Generate changelogs from commits:
```bash
npm install -g conventional-changelog-cli
conventional-changelog -p angular -i CHANGELOG.md -s
```
