# Issue Conventions Reference

Comprehensive guide to creating well-formed GitHub issues that follow project conventions.

## Table of Contents

1. [Title Conventions](#title-conventions)
2. [Label Taxonomy](#label-taxonomy)
3. [Body Structure](#body-structure)
4. [Relationships](#relationships)
5. [Milestones](#milestones)
6. [Project Board Integration](#project-board-integration)
7. [Common Mistakes](#common-mistakes)

---

## Title Conventions

### Format Rules

- **No type prefixes**: Never use `[BUG]`, `[FEATURE]`, `[ENHANCEMENT]`, etc.
- **Imperative mood**: Write as a command (e.g., "Fix", "Add", "Update")
- **Length**: 50-72 characters recommended
- **Descriptive**: Explain the work, not the category

### Why No Prefixes?

Labels already indicate the issue type. Prefixes are redundant and clutter search results.

```
❌ [BUG] Login fails when password contains special characters
✅ Fix login authentication for passwords with special characters
   (label: bug)
```

### Title Patterns by Type

| Type | Pattern | Example |
|------|---------|---------|
| Bug | `Fix <problem>` | Fix race condition in file writes |
| Feature | `Add <capability>` | Add two-factor authentication |
| Enhancement | `Improve <aspect>` | Improve error message clarity |
| Documentation | `Update/Add <doc>` | Update API reference for v2 |
| Refactor | `Refactor <component>` | Refactor validation logic |
| Chore | `Update/Clean <thing>` | Update dependencies to latest |

### Good Action Verbs

**Primary verbs** (most common):
- `Fix` - Resolve a bug or issue
- `Add` - New functionality
- `Update` - Modify existing
- `Remove` - Delete functionality
- `Improve` - Enhance quality

**Secondary verbs**:
- `Implement` - Build new feature
- `Refactor` - Restructure code
- `Optimize` - Improve performance
- `Migrate` - Move/convert
- `Validate` - Add checks

### Length Guidelines

| Length | Status | Example |
|--------|--------|---------|
| < 10 chars | ❌ Too short | "Fix bug" |
| 10-50 chars | ✅ Ideal | "Fix login timeout error" |
| 51-72 chars | ⚠️ Acceptable | "Fix race condition when multiple users save simultaneously" |
| > 72 chars | ⚠️ Too long | Consider shortening |

---

## Label Taxonomy

### Required Labels

Every issue MUST have:

1. **One Type Label**
2. **One Priority Label**

### Type Labels

Select based on the primary nature of the work:

| Label | When to Use | Example Issue |
|-------|-------------|---------------|
| `bug` | Something is broken | "Fix null pointer in auth" |
| `feature` | New capability | "Add dark mode support" |
| `enhancement` | Improve existing | "Improve search performance" |
| `documentation` | Docs only | "Update installation guide" |
| `refactor` | Code restructure | "Refactor user service" |
| `chore` | Maintenance | "Update dependencies" |
| `test` | Test-only changes | "Add unit tests for auth" |

### Type Selection Decision Tree

```
Is something broken?
├─ Yes → bug
└─ No → Is it a new capability?
         ├─ Yes → feature
         └─ No → Is it improving existing functionality?
                  ├─ Yes → enhancement
                  └─ No → Is it documentation only?
                           ├─ Yes → documentation
                           └─ No → Is it code restructuring?
                                    ├─ Yes → refactor
                                    └─ No → chore
```

### Priority Labels

| Label | When to Use | SLA |
|-------|-------------|-----|
| `priority:high` | Critical path, blocking, security | This sprint |
| `priority:medium` | Important but not blocking | Next sprint |
| `priority:low` | Nice to have, backlog | Future |

### Priority Selection Criteria

**High Priority**:
- Blocks other work
- Security vulnerability
- Data loss risk
- Production outage
- Critical user journey broken

**Medium Priority**:
- Important feature
- Significant bug (workaround exists)
- Performance degradation
- User-facing improvement

**Low Priority**:
- Minor enhancement
- Code cleanup
- Nice-to-have feature
- Non-critical documentation

### Required Labels

#### Scope Labels

Indicate which component/plugin the issue affects (REQUIRED):

```
scope:agent-builder
scope:github-workflows
scope:self-improvement
```

### Optional Labels

#### Branch Labels

Link issues to feature branches:

```
branch:feature/auth
branch:release/v2.0
branch:plugin/agent-builder
```

Format: `branch:<branch-name>`

---

## Body Structure

### Standard Template

```markdown
## Summary

[Clear description of what needs to be done]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Additional Context

[Any relevant context]
```

### Acceptance Criteria Guidelines

Good criteria are:
- **Specific**: Clear and unambiguous
- **Measurable**: Can verify completion
- **Achievable**: Realistic for the issue scope
- **Relevant**: Directly related to the issue
- **Testable**: Can write tests for them

Examples:

```markdown
❌ Bad criteria:
- [ ] Code works
- [ ] Tests pass

✅ Good criteria:
- [ ] Login accepts passwords with special characters (!@#$%^&*)
- [ ] Error message displays specific validation failure reason
- [ ] Unit tests cover all validation edge cases
- [ ] No regression in existing login functionality
```

### Type-Specific Sections

**Bug Reports** should include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Error messages/stack traces

**Feature Requests** should include:
- Use cases
- Proposed solution
- Out of scope

---

## Relationships

### Parent Issues (Epics)

For large features spanning multiple issues:

```markdown
## Parent Issue

Part of #123 - Implement user authentication system
```

### Blocking Issues

When this issue cannot proceed without another:

```markdown
## Blocked By

- #45 - Database schema migration
- #46 - API endpoint implementation
```

### Related Issues

For context and cross-reference:

```markdown
## Related Issues

- #78 - Similar bug in password reset
- #92 - Performance optimization effort
```

### Creating Parent/Child Structure

1. Create parent issue first (the epic)
2. Reference parent in child issues
3. Use milestone to group all related issues
4. Track progress through milestone completion

---

## Milestones

### When to Use Milestones

- **Phases**: `Phase: Authentication`
- **Releases**: `v2.0.0`
- **Sprints**: `Sprint 5`
- **Quarters**: `Q1 2025`

### Milestone Naming

| Type | Format | Example |
|------|--------|---------|
| Phase | `Phase: <Name>` | Phase: Hooks Validation |
| Release | `v<semver>` | v2.0.0 |
| Sprint | `Sprint <n>` | Sprint 5 |
| Quarter | `Q<n> <year>` | Q1 2025 |

### Milestone Assignment

Assign issues to milestones when:
- Part of a planned release
- Belongs to a sprint
- Part of a feature phase
- Has a target completion date

---

## Project Board Integration

### Status Workflow

```
Backlog → Todo → In Progress → In Review → Done
                     ↓
                  Blocked/On Hold
```

### Initial Placement

New issues start in **Backlog**.

Move to **Todo** when:
- Requirements are clear
- Acceptance criteria defined
- Priority assigned
- Dependencies resolved
- Ready to be picked up

### Status Meanings

| Status | Description |
|--------|-------------|
| Backlog | Not yet refined or prioritized |
| Todo | Ready to start, assigned to sprint |
| In Progress | Actively being worked on |
| On Hold | Temporarily paused (external reason) |
| Blocked | Cannot proceed (internal dependency) |
| Pending | Waiting for external input |
| In Review | PR submitted, awaiting review |
| Done | Completed and verified |
| Cancelled | Will not be done |

---

## Common Mistakes

### Mistake 1: Type Prefix in Title

```
❌ [BUG] Login fails
❌ [FEATURE] Add dark mode
❌ BUG: Authentication broken

✅ Fix login authentication failure (label: bug)
✅ Add dark mode support (label: feature)
✅ Fix authentication token validation (label: bug)
```

### Mistake 2: Vague Titles

```
❌ Fix bug
❌ Update code
❌ Add feature
❌ Make it work

✅ Fix null pointer in user authentication
✅ Update API to support pagination
✅ Add export to CSV functionality
✅ Fix validation to accept international phone numbers
```

### Mistake 3: Multiple Type Labels

```
❌ Labels: bug, enhancement
❌ Labels: feature, refactor

✅ Labels: bug (choose primary type)
✅ Labels: feature (refactor is implementation detail)
```

### Mistake 4: Missing Acceptance Criteria

```
❌ Body: "Fix the login bug"

✅ Body with criteria:
## Summary
Fix login failing for users with special characters in password.

## Acceptance Criteria
- [ ] Login accepts !@#$%^&* in passwords
- [ ] Error message is specific about validation failure
- [ ] Unit tests cover special character cases
- [ ] No regression in normal login flow
```

### Mistake 5: Wrong Label for Work Type

```
❌ "Add validation to existing form" → feature
✅ "Add validation to existing form" → enhancement

❌ "Restructure auth module" → enhancement
✅ "Restructure auth module" → refactor

❌ "Fix typo in README" → bug
✅ "Fix typo in README" → documentation
```

### Mistake 6: Status as Label

```
❌ Labels: status:in-progress, status:blocked

✅ Move issue to appropriate column in project board
```

Status is managed through project board columns, not labels.

---

## Quick Reference

### Issue Creation Checklist

- [ ] Title follows conventions (no prefix, imperative mood, 50-72 chars)
- [ ] Type label assigned (bug/feature/enhancement/etc.)
- [ ] Priority label assigned (high/medium/low)
- [ ] Scope label if applicable (plugin:*)
- [ ] Branch label if on feature branch
- [ ] Summary clearly explains the work
- [ ] Acceptance criteria are specific and measurable
- [ ] Relationships documented (parent/blocking/related)
- [ ] Milestone assigned if part of phase/sprint
- [ ] Added to project board

### Label Quick Reference

```
Required:
  Type: bug | feature | enhancement | documentation | refactor | chore | test
  Priority: priority:high | priority:medium | priority:low

Optional:
  Scope: plugin:<name>
  Branch: branch:<branch-name>
```

### Validation Command

```bash
python scripts/validate-issue-title.py "Your issue title here"
```
