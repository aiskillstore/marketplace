# Author Guide: Preparing Excellent Pull Requests

<context>
This guide provides comprehensive instructions for PR authors. The goal is to create pull requests that are easy to review, provide clear context, and catch issues before reviewer involvement.
</context>

## Before You Open a PR

### 1. Run Quality Gates Locally

**Never open a PR with failing tests or linting errors.** This wastes reviewer time and damages credibility.

```bash
# Run full test suite
npm test

# Run linter
npm run lint

# Run type checker
npm run type-check  # or tsc --noEmit

# Optional: Run full quality check
/review-orchestrator commit
```

**Check for common issues:**
- `console.log` statements (use proper logging)
- `debugger` statements (remove before commit)
- Commented-out code (delete it—git history preserves old code)
- `TODO` comments without tracking (create issues for TODOs)

### 2. Perform Self-Review

**Review your own diff as if reviewing someone else's code:**

1. Open the diff view in your git client or IDE
2. Read every changed line with fresh eyes
3. Ask yourself: "Would I approve this if I were the reviewer?"

**Common issues found during self-review:**
- Unintended changes (reformatting, accidental edits)
- Missing error handling
- Hardcoded values that should be configurable
- Missing tests for new functionality
- Incomplete refactors (half-finished cleanup)

**Self-review catches ~30% of issues before reviewer involvement**, saving time and improving PR quality.

### 3. Check PR Size and Scope

**Target: < 400 lines changed**

Large PRs are reviewed superficially or not at all. Research shows review effectiveness drops dramatically beyond 400 lines.

**Check your PR size:**
```bash
git diff --stat main...HEAD
```

**If too large:**
- Can you split into multiple PRs?
- Can you use feature flags for incremental delivery?
- Can you separate refactoring from behavioral changes?

**Justified exceptions:**
- Pure refactors (explain in description)
- Generated code (migrations, API clients)
- Dependency updates (with changelog)

**Scope check:**
- Does this PR do one thing well, or multiple things poorly?
- Are there unrelated changes that should be separate PRs?
- Is every change necessary for the stated goal?

## Writing PR Descriptions

**A great PR description enables fast, thorough review.** Invest 5-10 minutes writing it.

### Template Structure

```markdown
## Context
<!-- Why is this change needed? What problem does it solve? -->
<!-- Link to issue/ticket: Fixes #123 -->

Users reported that profile editing doesn't work on mobile devices.
Investigation revealed the form doesn't handle touch events properly.

## Changes
<!-- High-level summary of what changed (not every line) -->
- Refactored ProfileEditForm to use responsive form library
- Added touch event handlers for mobile interaction
- Updated validation to provide clearer error messages
- Fixed layout issues on small screens

## Test Plan
<!-- How can reviewers verify this works? -->
- [ ] Unit tests: `npm test src/components/ProfileEditForm.test.tsx`
- [ ] Manual testing (desktop):
  1. Open user profile
  2. Click "Edit Profile"
  3. Modify name and email
  4. Save and verify changes persist
- [ ] Manual testing (mobile):
  1. Repeat above on mobile device or Chrome DevTools mobile view
  2. Verify touch interactions work smoothly
- [ ] Edge cases tested:
  - Invalid email format shows error
  - Required fields prevent submission
  - Network error during save shows retry option

## Deployment Notes
- [ ] Database migration: No
- [ ] Feature flag: No
- [ ] Configuration changes: No
- [ ] Breaking changes: No
- [ ] Rollback plan: Standard rollback via deployment system

## Security Considerations
<!-- If touching auth/permissions/data/secrets -->
- Input validation: Email format validated client-side and server-side
- No new permissions required
- No sensitive data exposed in UI
```

### Context Section

**Answer these questions:**
1. **Why** is this change needed?
2. **What problem** does it solve?
3. **Who** requested it or will benefit?
4. **Links** to issues, tickets, specs, designs

**Example (good):**
> Users reported errors when editing profiles on mobile (issue #456). Investigation showed the form library doesn't support touch events. This PR switches to a responsive form library and adds proper mobile support.

**Example (bad):**
> Fixed profile editing.

### Changes Section

**High-level summary, not every line.**

Use bullet points for scannability:
- Start with most important changes
- Group related changes together
- Mention deletions/removals explicitly
- Note any architectural decisions

**Example (good):**
> - Replaced Formik with React Hook Form (better mobile support)
> - Added touch event handlers for form inputs
> - Extracted validation logic into `validateProfileData.ts` for reuse
> - Removed deprecated `ProfileEditModal` component

**Example (bad):**
> - Changed line 45
> - Updated component
> - Fixed stuff

### Test Plan Section

**Enable reviewers to verify your changes work.**

Include:
1. **Automated tests:** Exact commands to run
2. **Manual testing steps:** Step-by-step instructions
3. **Edge cases:** Specific scenarios you tested

**Use checkboxes for clarity:**
- [ ] Unit tests pass
- [ ] Manual testing completed
- [ ] Edge cases verified

Reviewers can check these off as they verify.

### Deployment Notes Section

**Identify any special deployment considerations:**

Answer these questions:
- Database migration required?
- Feature flag needed for rollout?
- Configuration changes (env vars, etc.)?
- Breaking changes affecting other services?
- Rollback plan if issues arise?

**If any answer is "yes", provide details.**

## Responding to Review Feedback

### Comment Classification

Reviewers should classify comments:
- `[critical]` - Must fix before merge
- `[issue]` - Should fix, discuss if can't
- `[suggestion]` - Nice to have, your decision
- `[nit]` - Cosmetic, optional
- `[question]` - Seeking clarification

**Your response strategy:**

**[critical] comments:**
- Fix immediately
- Push new commit
- Reply confirming fixed

**[issue] comments:**
- Fix if agree
- If disagree, discuss constructively with reasoning
- Come to agreement before merging

**[suggestion] comments:**
- Consider merit
- Apply if improves code
- Politely decline if out of scope or doesn't fit
- Can defer to follow-up PR if valuable but not urgent

**[nit] comments:**
- Fix if quick/easy
- Batch with other nits
- OK to ignore if preference-based

**[question] comments:**
- Answer clearly
- May indicate need for code comments or better naming
- Clarify intent

### When to Push Back (Constructively)

**It's OK to disagree with reviewers.** You have context they may lack.

**Push back when:**
- Suggestion contradicts project patterns
- Request expands scope significantly
- Reviewer misunderstands intent
- Change would harm performance/maintainability

**How to push back constructively:**
1. Acknowledge the feedback
2. Explain your reasoning with specifics
3. Ask questions to understand their concern
4. Propose alternatives if applicable

**Example:**
> Thanks for the suggestion to extract this into a separate service. I considered that approach, but kept it inline because:
> 1. This logic is only used in this one component
> 2. Extracting adds indirection without reuse benefit
> 3. Our project pattern (per docs/architecture.md) is to extract only when reused
>
> Does that reasoning make sense, or am I missing something about future reuse?

### Iterative vs. Batched Changes

**Batch small changes when possible:**
- Don't push after every nit fix
- Group related changes into single commit
- Push once with message: "Address review feedback: fixed X, Y, Z"

**Iterate quickly for [critical] items:**
- Push fix immediately
- Comment: "Fixed in commit abc123"
- Unblock reviewer approval

## Using Draft PRs

**Draft PRs are for early feedback on approach, not implementation.**

**When to use draft:**
- Want feedback on technical approach before full implementation
- Need CI to run (tests, builds) before manual testing
- Waiting on dependent PRs to merge
- Still working but want to share progress

**Draft PR description should clarify:**
> **🚧 DRAFT - Not ready for full review**
>
> Seeking feedback on:
> - Overall approach to solving X
> - Architecture decision: Service layer vs. inline logic
> - API design for new endpoint
>
> Still TODO:
> - Add tests
> - Update documentation
> - Handle edge case Y

**Convert to regular PR when:**
- All checklist items complete
- Ready for full review
- Would merge if approved

## Commit Message Standards

**Follow conventional commits format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc. (no code change)
- `refactor`: Code change that neither fixes bug nor adds feature
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, etc.

**Examples:**
```
feat(auth): add two-factor authentication support

Implemented SMS-based 2FA using Twilio. Users can enable 2FA
in account settings. Includes backup codes for account recovery.

Fixes #456
```

```
fix(profile): handle touch events on mobile devices

Profile edit form now properly responds to touch interactions.
Switched from Formik to React Hook Form for better mobile support.

Fixes #789
```

**Keep commits focused:**
- One logical change per commit
- Squash "fix typo" and "forgot to add file" commits before opening PR
- Use `git rebase -i` to clean up commit history

## Checklist Summary

Before opening PR, verify:

**Code Quality:**
- [ ] All tests pass
- [ ] No linting errors
- [ ] TypeScript compiles
- [ ] No debug code

**Self-Review:**
- [ ] Reviewed diff line-by-line
- [ ] All changes intentional
- [ ] No unrelated changes

**Testing:**
- [ ] Tests added/updated
- [ ] Edge cases tested
- [ ] Manual testing done

**Documentation:**
- [ ] README updated if needed
- [ ] JSDoc for public APIs
- [ ] Architecture docs updated

**Security:**
- [ ] No secrets in code
- [ ] Input validation present
- [ ] Ran `/review-security` if touching auth

**PR Description:**
- [ ] Context explains why
- [ ] Changes summarize what
- [ ] Test plan enables verification
- [ ] Deployment notes complete

**Size & Scope:**
- [ ] < 400 lines or justified
- [ ] Single purpose
- [ ] Refactors split out

---

**Remember:** Time spent preparing a great PR saves multiples of that time in review cycles. Invest in PR quality—your reviewers and future self will thank you.
