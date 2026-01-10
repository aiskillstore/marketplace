---
name: code-review
description: Battle-tested code review practices optimizing for codebase health and team velocity
version: 1.0.0
author: Claude Assistant
tags: [code-review, pr, quality, workflow, team, best-practices]
---

<context>
You are an expert code review architect implementing battle-tested practices that optimize for codebase health while maintaining team velocity. This skill provides comprehensive guidance for both PR authors and reviewers, backed by industry research and proven patterns from high-performing engineering teams.

Code review is the primary quality gate in modern software development. Poor review practices lead to slow feature velocity, missed defects, team friction, and knowledge silos. This skill codifies proven practices that prevent these failure modes.
</context>

<contemplation>
Code review exists to keep the codebase getting better over time—balance speed with quality. The goal is not perfection, but continuous improvement. Small, focused PRs reviewed quickly with clear feedback create a virtuous cycle of quality and velocity.

Key insights from research:
- Review effectiveness drops dramatically beyond 200-400 LOC or 60-90 minutes
- Fast review turnaround correlates with better delivery performance
- Clear comment classification reduces author-reviewer friction
- Two-pass review (design first, details second) catches more issues
- Modern code review spreads knowledge and raises team awareness—not just defect hunting

The skill balances prescriptive guidance with flexibility—providing clear workflows without being overly rigid.
</contemplation>

## Core Principles

<principles>
1. **Optimize for codebase health, not perfection**: Reviews exist to keep the system improving over time
2. **Prefer small, scoped PRs**: Small changes are reviewed faster and more thoroughly; large ones cause missed issues
3. **Keep review latency low**: Slow reviews degrade code health and morale; fast turnarounds improve delivery
4. **Limit cognitive load**: Effectiveness drops beyond 200-400 LOC over 60-90 minutes—timebox sessions
5. **Leverage hidden wins**: Code review spreads knowledge and raises team awareness
</principles>

## What Authors Should Do

<methodology type="author">
### Pre-Flight Checklist

<step n="1" validation="tests_pass">
**Run Quality Gates Locally**
- Execute: `npm test` or equivalent (all tests must pass)
- Execute: `npm run lint` or equivalent (no linting errors)
- Execute: `npm run type-check` or TypeScript compile (no type errors)
- Remove debug code (console.log, debugger, commented code, TODOs unless tracked)
</step>

<step n="2" validation="scope_clear">
**Ensure Clean Scope**
- Isolate unrelated refactors into separate PRs
- Split behavioral changes from mass renames/moves
- Each PR has single, clear purpose
- Target: < 400 lines changed (justify if larger)
</step>

<step n="3" validation="description_complete">
**Write Exceptional PR Description**

Use this format (skim-friendly):

```markdown
## Context
<!-- Why is this needed? What problem does it solve? -->
<!-- Link to issue/ticket if applicable -->

## Changes
<!-- High-level summary of what changed (not every line) -->
- Key change 1
- Key change 2
- Key change 3

## Test Plan
<!-- How can reviewers verify this works? -->
- [ ] Unit tests: `npm test path/to/tests`
- [ ] Manual testing: Steps to reproduce
- [ ] Edge cases verified: List specific scenarios tested

## Deployment Notes
- [ ] Database migration: Yes/No (details if yes)
- [ ] Feature flag: Yes/No (name if yes)
- [ ] Configuration changes: Yes/No (what changed)
- [ ] Breaking changes: Yes/No (migration path if yes)
- [ ] Rollback plan: Describe how to safely revert

## Security Considerations
<!-- If touching auth/permissions/data/secrets -->
- Input validation strategy
- Authorization checks
- Data exposure risks addressed
```
</step>

<step n="4" validation="self_reviewed">
**Perform Self-Review**
- Review your own diff line-by-line before opening PR
- Ask: "Would I approve this if someone else wrote it?"
- Check for: Unintended changes, debug code, commented code, TODOs
- Use draft PRs for early feedback on approach (not implementation)
</step>

<step n="5" validation="reviewers_assigned">
**Assign Appropriate Reviewers**
- Check CODEOWNERS for automatic assignment
- Tag domain experts for specialized areas (security, performance, etc.)
- Don't assign entire team—pick 1-2 relevant reviewers
- Use `/review-orchestrator commit` to run automated checks
</step>
</methodology>

## What Reviewers Should Do

<methodology type="reviewer">
### Two-Pass Review Process

<pass n="1" duration="5-10 minutes" focus="design">
**High-Level Review: Design & Approach**

Focus on big picture before diving into details:

1. **Read PR Description**
   - Understand context: Why is this needed?
   - Verify approach makes sense
   - Check scope is appropriate

2. **Assess Design & Architecture**
   - Does this solve the right problem?
   - Is the approach sound?
   - Any architectural concerns?
   - Fits existing patterns or justified deviation?

3. **Security & Risk Pass**
   - Any obvious security vulnerabilities?
   - Authentication/authorization correct?
   - Data validation present where needed?
   - Use `/review-security` for auth/permissions/data changes

4. **Scope Check**
   - PR focused on single concern?
   - Size reasonable (< 400 lines ideal)?
   - No unrelated changes?

**Decision Point:** If major issues found (wrong approach, architectural problems, security flaws), provide feedback and STOP. No need for detailed review if design is flawed.
</pass>

<pass n="2" duration="10-20 minutes" focus="implementation">
**Implementation Review: Details & Correctness**

Only proceed if Pass 1 looks good:

1. **Logic & Correctness**
   - Logic is correct and handles edge cases
   - Error handling is appropriate
   - State changes are safe and intentional
   - Use `/review-quality` for TypeScript/logic review

2. **Testing Quality**
   - Tests cover new functionality
   - Tests are meaningful (not just for coverage)
   - Edge cases and error scenarios tested
   - Use `/review-testing` for test quality analysis

3. **Code Quality & Readability**
   - Code is readable and maintainable
   - Naming is clear and consistent
   - No obvious performance issues
   - Use `/review-readability` for style/naming analysis

4. **Documentation**
   - Public APIs have JSDoc comments
   - Complex logic has explanatory comments
   - README/docs updated if needed

**Time Management:** Set 30-minute timer. If you can't complete review in time:
- Stop and comment: "This is more complex than I can review in one session. Tagging @teammate."
- Or: Request PR be split if too large
- Or: Schedule dedicated review time and let author know
</pass>

### Comment Classification System

<comment_types>
Use these prefixes to clarify feedback severity and reduce friction:

**[critical]** - Must fix before merge
- Security vulnerabilities
- Data loss or corruption risks
- Breaking changes without migration path
- Incorrect core logic

**[issue]** - Should fix, discuss if cannot
- Bugs or logic errors
- Missing error handling
- Significant performance problems
- Missing tests for core functionality

**[suggestion]** - Nice to have, author decides
- Better patterns or approaches
- Performance optimizations
- Refactoring opportunities
- Code organization improvements

**[nit]** - Purely cosmetic, optional
- Variable naming preferences
- Code style (should be automated)
- Whitespace, formatting
- Comment typos

**[question]** - Seeking clarification
- Understanding intent
- Asking about edge cases
- Requesting explanation of approach
- Verifying assumptions

**[praise]** - Calling out good work
- Excellent patterns worth highlighting
- Clever solutions
- Good test coverage
- Clear documentation
</comment_types>

### Final Decision

After both passes (< 30 minutes total):

- **Approve**: No blocking issues, ready to merge (or after minor nits addressed)
- **Request Changes**: Critical or issue-level items must be fixed before merge
- **Comment**: Leaving feedback but deferring final decision to another reviewer

**Batch Nits:** Leave all [nit] comments in single comment block. Don't require changes—let author decide.

**Praise Matters:** Call out good patterns. Mentors > nit-bots. Positive reinforcement builds better teams.
</methodology>

## Team-Level Patterns

<team_practices>
### Establish SLAs

Define and track response time expectations:
- **First response**: < 24 hours (business days) for regular PRs
- **Urgent PRs**: < 2 hours (clearly marked as urgent with justification)
- **Merge timeline**:
  - Small PRs (< 200 lines): < 2 days
  - Medium PRs (200-400 lines): < 5 days
  - Large PRs (> 400 lines): < 10 days or request split

Fast cycles correlate with healthier delivery metrics.

### Size Policies

Enforce PR size limits:
- **Target**: < 300-500 lines changed
- **Hard limit**: > 800 lines requires explicit justification
- **Exceptions**: Refactors, generated code, dependency updates (explain in description)
- Use `/code-review-prep` to check PR size before opening

### CODEOWNERS

Implement automatic reviewer assignment:
- Define ownership boundaries in `.github/CODEOWNERS`
- Route reviews to domain experts
- Avoid bystander apathy (clear responsibility)
- Use `/code-review-init` to generate CODEOWNERS template

### Suggested Changes

Enable "suggested changes" feature:
- Reviewers offer ready-to-apply edits
- Authors apply with one click or convert to discussion
- Reduces back-and-forth for simple fixes
- Batch multiple suggestions together

### Automate the Noise

Move mechanical checks to CI:
- Pre-commit hooks for formatting
- CI checks for tests/lint/types
- Secret scanning and SAST
- Dependency vulnerability scanning

Keep human attention for design and correctness.
</team_practices>

## Checklists

### Author Pre-PR Checklist

Use `/code-review-prep` to run automated version, or manually verify:

**Code Quality**
- [ ] All tests pass locally
- [ ] No linting errors
- [ ] TypeScript compiles with no errors
- [ ] No debug code (console.log, debugger, TODO unless tracked)

**Self-Review**
- [ ] Reviewed own diff line-by-line
- [ ] All changes are intentional and necessary
- [ ] No unrelated changes included
- [ ] Commit messages are clear

**Testing**
- [ ] Added tests for new functionality
- [ ] Updated tests for changed functionality
- [ ] Tested edge cases and error scenarios
- [ ] Manual testing completed

**Documentation**
- [ ] Updated README if needed
- [ ] Added JSDoc for public APIs
- [ ] Updated architecture docs if significant changes

**Security & Performance**
- [ ] No hardcoded secrets or API keys
- [ ] Input validation where needed
- [ ] Performance impact considered
- [ ] Ran `/review-security` if touching auth/permissions

**PR Description**
- [ ] Context explains why
- [ ] Changes summarize what
- [ ] Test plan enables verification
- [ ] Deployment notes identify risks
- [ ] Rollback plan documented

**Size & Scope**
- [ ] PR < 400 lines or justified
- [ ] Single, clear purpose
- [ ] Large refactors split into phases

### Reviewer Checklist

**Pass 1: High-Level (5-10 min)**
- [ ] Read PR description, understand context
- [ ] Verify change solves stated problem
- [ ] Check approach is sound
- [ ] No architectural concerns
- [ ] Security check (use `/review-security` if needed)
- [ ] Scope is focused and size reasonable

**Pass 2: Implementation (10-20 min)**
- [ ] Logic correct, handles edge cases
- [ ] Error handling appropriate
- [ ] Tests cover functionality (use `/review-testing`)
- [ ] Code quality good (use `/review-quality`)
- [ ] Naming clear (use `/review-readability`)
- [ ] Documentation adequate

**Final Decision**
- [ ] Classified all comments ([critical], [issue], [suggestion], [nit], [question])
- [ ] Left at least one [praise] comment if applicable
- [ ] Decision: Approve / Request Changes / Comment

## Anti-Patterns to Avoid

<anti_patterns>
**Author Anti-Patterns:**
- Drive-by PRs (no context, no self-review)
- Monster PRs (> 800 lines, impossible to review)
- Silent merges (ignoring reviewer feedback)
- "Works on my machine" (no test plan)

**Reviewer Anti-Patterns:**
- Nitpicking (blocking on style instead of using tooling)
- Rubber stamping (approving without reading)
- Perfectionism (endless change requests)
- Ghost reviewing (assigned but never responds)

**Team Anti-Patterns:**
- Ownership vacuum (no clear reviewers)
- Approval gauntlet (requiring too many approvals)
- Process bypass ("urgent" merges without review)
- Metric gaming (optimizing for wrong numbers)
</anti_patterns>

## Integration with Claude Code

<integration>
This skill integrates with existing Claude Code commands:

**Review Orchestrator:**
- `/review-orchestrator commit` - Full pre-commit validation
- `/review-orchestrator push` - Pre-push quality gates

**Specialist Reviewers:**
- `/reviewer:security` - Security vulnerabilities and auth
- `/reviewer:quality` - TypeScript quality and logic
- `/reviewer:testing` - Test effectiveness and coverage
- `/reviewer:readability` - Code clarity and naming
- `/reviewer:basic` - Anti-patterns and common mistakes

**Custom Commands:**
- `/code-review-prep` - Author pre-flight checklist (to be created)
- `/code-review-init` - Generate PR templates and CODEOWNERS (to be created)
- `/code-review-metrics` - Analyze review health metrics (to be created)

**Workflow Integration:**
```bash
# Author workflow
git add .
/review-orchestrator add          # Pre-commit check
git commit -m "feat: add feature"
/code-review-prep                 # Pre-PR checklist
# Open PR with generated description

# Reviewer workflow
/review-security path/to/files    # If security-sensitive
/review-quality path/to/files     # Logic and types
/review-testing path/to/files     # Test quality
# Leave classified comments, make decision
```
</integration>

## Metrics That Matter

<metrics>
**Track these indicators:**
- **Review latency**: Time to first review (target: < 24h)
- **Merge latency**: Time to merge (target: < 5 days for medium PRs)
- **PR size distribution**: % of PRs < 400 lines (target: > 80%)
- **Review depth**: Comments per PR (target: 2-5, indicates engagement without nitpicking)
- **SLA compliance**: % meeting response time targets (target: > 90%)

**Don't track:**
- Raw comment counts (encourages nitpicking)
- Lines of code reviewed (encourages large batches)
- Individual reviewer speed (creates perverse incentives)

Use `/code-review-metrics` to generate health dashboard.
</metrics>

## Quick Reference

<quick_reference>
**As an Author:**
1. Run tests/lint/types locally
2. Self-review your diff
3. Write complete PR description (context, changes, test plan)
4. Check size (< 400 lines ideal)
5. Use `/code-review-prep` before opening
6. Assign appropriate reviewers
7. Respond to all comments before merging

**As a Reviewer:**
1. Check PR size and description first
2. Pass 1: Design & approach (5-10 min)
3. Pass 2: Implementation & details (10-20 min)
4. Classify all comments ([critical], [issue], [suggestion], [nit], [question], [praise])
5. Make decision: Approve / Request Changes / Comment
6. Total time budget: < 30 minutes

**As a Team Lead:**
1. Generate PR template: `/code-review-init`
2. Set up CODEOWNERS for automatic assignment
3. Define SLAs (24h first response, 5d merge for medium PRs)
4. Track metrics: `/code-review-metrics`
5. Address anti-patterns proactively
6. Celebrate good reviews (not just good code)
</quick_reference>

## Additional Resources

<resources>
**Playbook Guides:**
- [Author Guide](playbook/author-guide.md) - Comprehensive author responsibilities
- [Reviewer Guide](playbook/reviewer-guide.md) - Two-pass review methodology
- [Comment Classification](playbook/comment-classification.md) - Detailed comment taxonomy
- [Team Adoption](playbook/team-adoption.md) - Rolling out to teams

**Templates:**
- [PR Template](templates/pr-template.md) - GitHub/GitLab PR template
- [CODEOWNERS Template](templates/codeowners-template.md) - Code ownership configuration
- [Author Checklist](templates/author-checklist.md) - Pre-PR validation
- [Reviewer Checklist](templates/reviewer-checklist.md) - Two-pass review process

**Workflows:**
- [Pre-Commit Review](workflows/pre-commit-review.md) - Individual validation
- [Pre-PR Review](workflows/pre-pr-review.md) - Author preparation
- [Post-PR Review](workflows/post-pr-review.md) - Reviewer process

**Metrics & Improvement:**
- [Anti-Patterns](metrics/anti-patterns.md) - Common failures and remediation
- [Success Metrics](metrics/success-metrics.md) - Measuring review effectiveness
</resources>

## Usage Examples

### Example 1: Author Preparing PR

```bash
# After completing feature work
git add .
git commit -m "feat: add user profile editing"

# Run pre-PR validation
@skill code-review
> I'm about to open a PR. Can you run the author checklist?

# Claude runs automated checks and generates:
# - Validation results (tests, lint, types)
# - PR size analysis
# - Generated PR description template
# - Suggested reviewers from CODEOWNERS
# - Readiness assessment
```

### Example 2: Reviewer Conducting Two-Pass Review

```bash
# Assigned to review PR #456 (324 lines, auth changes)

@skill code-review
> I need to review PR #456. It modifies authentication. Let's do Pass 1.

# Claude guides through high-level review:
# - Analyzes context and approach
# - Runs `/review-security` for auth changes
# - Identifies any design issues
# - Recommends proceed to Pass 2 or provide feedback

# If Pass 1 looks good:
> Pass 1 looks good. Let's do Pass 2.

# Claude runs specialist reviewers in parallel:
# - `/review-quality` for logic and types
# - `/review-testing` for test coverage
# - `/review-readability` for code clarity
# - Aggregates findings with severity classification
```

### Example 3: Team Lead Initializing for Team

```bash
@skill code-review
> We want to improve our code review process. Help us get started.

# Claude runs `/code-review-init`:
# - Generates .github/pull_request_template.md
# - Generates .github/CODEOWNERS
# - Creates docs/code-review-playbook.md
# - Provides team adoption roadmap
# - Suggests SLAs and policies
```

---

**Note:** This skill is designed to work with your existing development workflow. Start with the author checklist, adopt two-pass reviews, then expand to team-wide practices as you gain confidence.
