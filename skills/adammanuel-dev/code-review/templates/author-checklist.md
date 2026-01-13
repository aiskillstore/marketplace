# Author Pre-PR Checklist

Use this checklist before opening a pull request. Each item helps ensure your PR is easy to review and merge quickly.

## Code Quality

- [ ] **All tests pass locally**
  ```bash
  npm test
  # or: yarn test, pnpm test, pytest, etc.
  ```

- [ ] **No linting errors**
  ```bash
  npm run lint
  # or: yarn lint, pnpm lint, etc.
  ```

- [ ] **TypeScript compiles without errors** (if applicable)
  ```bash
  npm run type-check
  # or: tsc --noEmit
  ```

- [ ] **No debug code**
  - No `console.log` statements (use proper logging)
  - No `debugger` statements
  - No commented-out code blocks
  - No untracked `TODO` comments (create issues for TODOs)

## Self-Review

- [ ] **Reviewed my own diff line-by-line**
  - Open the diff in your git client or IDE
  - Read every changed line with fresh eyes
  - Ask: "Would I approve this if someone else wrote it?"

- [ ] **All changes are intentional and necessary**
  - No accidental reformatting of unrelated code
  - No unintended file changes
  - No large file additions (check for accidentally committed binaries, node_modules, etc.)

- [ ] **No unrelated changes**
  - Each PR should have a single, clear purpose
  - Unrelated bug fixes or refactors belong in separate PRs

- [ ] **Commit messages are clear and follow conventions**
  - Use conventional commit format: `type(scope): description`
  - Types: feat, fix, docs, style, refactor, perf, test, chore

## Testing

- [ ] **Added tests for new functionality**
  - Unit tests for new functions/methods
  - Integration tests for new features
  - E2E tests for critical user flows (if applicable)

- [ ] **Updated tests for changed functionality**
  - Existing tests still pass
  - Tests accurately reflect new behavior
  - Removed tests for removed functionality

- [ ] **Tested edge cases and error scenarios**
  - Null/undefined values
  - Empty arrays/objects
  - Invalid input
  - Network errors
  - Concurrent operations (if applicable)

- [ ] **Manual testing completed**
  - Tested in development environment
  - Verified all acceptance criteria met
  - Tested on different browsers/devices (if UI changes)

## Documentation

- [ ] **Updated README if needed**
  - New features documented
  - Changed APIs reflected
  - New dependencies listed
  - Updated setup instructions (if changed)

- [ ] **Added JSDoc comments for public APIs**
  - Function purpose and behavior
  - Parameter descriptions
  - Return value descriptions
  - Example usage (for complex APIs)

- [ ] **Updated architecture docs for significant changes**
  - New patterns documented
  - Architectural decisions recorded
  - Dependencies and interactions explained

- [ ] **Added inline comments for complex logic**
  - Explain "why", not "what"
  - Document non-obvious algorithms
  - Clarify business rules

## Security & Performance

- [ ] **No hardcoded secrets or API keys**
  - All secrets in environment variables
  - `.env.example` updated with new variables
  - No credentials in commit history

- [ ] **Input validation implemented**
  - All user input validated
  - Type checking in place
  - Sanitization for XSS prevention (if applicable)

- [ ] **Authorization checks in place**
  - User permissions verified
  - Resource ownership validated
  - No unauthorized data access possible

- [ ] **Performance impact considered**
  - No N+1 query problems
  - No unnecessary loops or iterations
  - Large datasets handled efficiently
  - Consider caching if applicable

- [ ] **Ran security review for sensitive changes** (if applicable)
  ```bash
  # If touching auth/permissions/data
  /review-security path/to/changed/files
  ```

## PR Description

- [ ] **Context section explains WHY**
  - What problem does this solve?
  - Why is this change needed?
  - Who requested it or will benefit?
  - Link to issue/ticket

- [ ] **Changes section summarizes WHAT**
  - High-level bullet points
  - Not a line-by-line diff
  - Group related changes
  - Mention deletions/removals explicitly

- [ ] **Test plan enables verification**
  - Specific commands to run tests
  - Step-by-step manual testing instructions
  - Edge cases and error scenarios listed
  - Screenshots/videos for UI changes

- [ ] **Deployment notes identify risks**
  - Database migration needed? (describe it)
  - Feature flag needed? (name it)
  - Configuration changes? (list them)
  - Breaking changes? (migration path)
  - Rollback plan (how to safely revert)

## Size & Scope

- [ ] **PR is < 400 lines changed** (or justified)
  ```bash
  # Check PR size
  git diff --stat main...HEAD
  ```
  - If larger: Can it be split?
  - If large refactor: Explain in description
  - If generated code: Separate from logic changes

- [ ] **PR has single, clear purpose**
  - Not mixing features with refactors
  - Not including unrelated bug fixes
  - Not combining multiple features

- [ ] **Large refactors split into separate PRs**
  - Phase 1: Extract/setup
  - Phase 2: Migrate usage
  - Phase 3: Remove old code

## Reviewer Assignment

- [ ] **Appropriate reviewers assigned**
  - Check CODEOWNERS for automatic assignment
  - Tag domain experts for specialized areas
  - Don't assign entire team (causes bystander effect)
  - 1-2 reviewers is ideal

- [ ] **Labels and metadata added**
  - Apply relevant labels (feature, bug, refactor, etc.)
  - Set milestone (if applicable)
  - Link to project board (if applicable)

## Pre-Submit Validation

- [ ] **Run automated quality check** (optional but recommended)
  ```bash
  /review-orchestrator commit
  ```
  This runs:
  - Anti-pattern detection
  - Code quality analysis
  - Security review (if applicable)
  - Test coverage check

---

## ✅ Ready to Open PR!

If all items above are checked, you're ready to create your pull request.

**Before clicking "Create Pull Request":**
1. Choose regular PR (not draft) if ready for full review
2. Choose draft PR if seeking early feedback on approach
3. Use PR template to fill in description
4. Double-check reviewers are assigned
5. Add any relevant labels/metadata

---

**Time Investment:** This checklist takes 5-10 minutes but saves 30+ minutes in review cycles.

**Questions?** See:
- [Author Guide](../playbook/author-guide.md) - Detailed guidance
- [Main Skill](../SKILL.md) - Overview and principles
