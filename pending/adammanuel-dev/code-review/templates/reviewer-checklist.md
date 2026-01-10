# Reviewer Checklist - Two-Pass Review

Use this checklist to conduct effective reviews in < 30 minutes. Focus on high-impact issues.

---

## Pre-Review Assessment (2 minutes)

**Before committing to review, check:**

- [ ] **PR size is reviewable**
  - < 200 lines: Quick review (10-15 min)
  - 200-400 lines: Standard review (20-30 min)
  - 400-800 lines: Large review (30-60 min) - consider requesting split
  - > 800 lines: Very large - should be split or reviewed commit-by-commit

- [ ] **PR description is complete**
  - Context explains WHY
  - Changes explain WHAT
  - Test plan provided
  - If inadequate, request more info before reviewing

- [ ] **You're the right reviewer**
  - Have domain knowledge for this area?
  - Familiar with this part of codebase?
  - If not, tag someone else or pair review

**If any issues, comment immediately:**
> This PR is quite large (847 lines). Could we split it into smaller PRs for safer review?

Or:
> The PR description is missing context. Could you add: why this change is needed, test plan, and deployment notes?

---

## Pass 1: High-Level Review (5-10 minutes)

**Goal:** Validate design and approach. Set 10-minute timer.

### Step 1: Understand Context (2 min)

- [ ] **Read PR description**
  - Understand the problem being solved
  - Understand the proposed solution
  - Check linked issues/tickets

- [ ] **Skim the diff at high level**
  - What files are being changed?
  - What's the overall structure?
  - Any obvious architectural concerns?

### Step 2: Design & Architecture (3-5 min)

- [ ] **Approach solves the right problem**
  - Is this addressing the stated issue?
  - Is it solving the root cause or just symptoms?

- [ ] **Design is sound**
  - Fits existing architecture patterns?
  - Justified deviation if introducing new pattern?
  - API design is clear and maintainable?
  - Data flow makes sense?

- [ ] **No obvious anti-patterns**
  - No circular dependencies
  - No God objects/classes
  - No premature optimization
  - No reinventing the wheel

- [ ] **Run automated design review** (optional)
  ```bash
  /review-quality path/to/changed/files
  ```

### Step 3: Security & Risk (2-3 min)

**If PR touches sensitive areas, run security review:**

- [ ] **Security considerations addressed** (if applicable)
  - Input validation present?
  - Authorization checks in place?
  - No sensitive data logged or exposed?
  - No SQL injection/XSS risks?
  - Rate limiting for sensitive operations?

- [ ] **Run automated security review** (if applicable)
  ```bash
  /review-security path/to/changed/files
  ```

### Step 4: Scope Check (1 min)

- [ ] **PR is focused**
  - Single, clear purpose?
  - No unrelated changes mixed in?
  - Size is reasonable for the scope?

---

## Pass 1 Decision Point

**If you found major issues:**
- [ ] Leave comments with `[critical]` or `[issue]` classification
- [ ] Mark "Request Changes"
- [ ] **STOP** - No need for Pass 2 until issues resolved

**If high-level looks good:**
- [ ] Proceed to Pass 2
- [ ] Or: Leave "looks good so far" and schedule Pass 2 later

---

## Pass 2: Implementation Review (10-20 minutes)

**Goal:** Verify correctness and quality. Set 20-minute timer.

### Step 1: Logic & Correctness (5-7 min)

- [ ] **Logic is correct**
  - Does the code do what it's supposed to?
  - Algorithms implemented correctly?
  - Boolean logic is correct?

- [ ] **Edge cases handled**
  - Null/undefined/empty values?
  - Zero/negative numbers?
  - Empty arrays/objects?
  - Boundary conditions?

- [ ] **Error handling is appropriate**
  - Errors caught and handled?
  - Error messages are clear and actionable?
  - No swallowed errors?
  - Appropriate error types thrown?

- [ ] **State management is safe**
  - No unintended mutations?
  - State changes are intentional?
  - No race conditions?
  - Async operations handled properly?

- [ ] **Run automated quality review**
  ```bash
  /review-quality path/to/changed/files
  ```

**Common issues to watch for:**
- Off-by-one errors
- Missing null checks
- Incorrect boolean logic
- Missing `await` for async calls
- Mutation of shared state

### Step 2: Testing Quality (3-5 min)

- [ ] **Tests cover new functionality**
  - Unit tests for new functions?
  - Integration tests for features?
  - E2E tests for critical flows (if applicable)?

- [ ] **Tests are meaningful**
  - Actually verify behavior, not just call functions?
  - Test edge cases and error scenarios?
  - Tests would fail if feature is broken?

- [ ] **Tests are maintainable**
  - Clear test names?
  - Well-organized (arrange/act/assert)?
  - Not testing implementation details?

- [ ] **Run automated testing review**
  ```bash
  /review-testing path/to/changed/files
  ```

### Step 3: Code Quality (3-5 min)

- [ ] **Naming is clear and consistent**
  - Variable names are descriptive?
  - Function names explain what they do?
  - No abbreviations or unclear names?

- [ ] **Code is readable**
  - Functions are focused (single responsibility)?
  - Nesting is not too deep (< 3 levels)?
  - No overly complex conditionals?
  - No magic numbers (use named constants)?

- [ ] **No obvious duplication**
  - Similar code extracted into functions?
  - Reusing existing utilities?
  - DRY principle followed?

- [ ] **Performance is reasonable**
  - No N+1 query problems?
  - No unnecessary loops?
  - No obvious performance anti-patterns?

- [ ] **Run automated readability review**
  ```bash
  /review-readability path/to/changed/files
  ```

### Step 4: Documentation (2-3 min)

- [ ] **Public APIs have JSDoc**
  - Function purpose documented?
  - Parameters and return values described?
  - Examples for complex APIs?

- [ ] **Complex logic has comments**
  - Explaining "why", not "what"?
  - Business rules clarified?
  - Non-obvious algorithms explained?

- [ ] **README/docs updated** (if applicable)
  - New features documented?
  - Changed APIs reflected?
  - Architecture docs updated for significant changes?

---

## Comment Classification

**Classify every comment you leave:**

- [ ] **Use `[critical]` for must-fix issues**
  - Security vulnerabilities
  - Data loss/corruption risks
  - Breaking changes without migration
  - Incorrect core logic

- [ ] **Use `[issue]` for should-fix problems**
  - Bugs in edge cases
  - Missing error handling
  - Missing tests for core functionality
  - Significant performance problems

- [ ] **Use `[suggestion]` for nice-to-have improvements**
  - Better patterns/approaches
  - Non-critical performance improvements
  - Refactoring opportunities
  - Code organization improvements

- [ ] **Use `[nit]` for cosmetic issues (sparingly)**
  - Typos in comments
  - Minor naming preferences
  - Formatting (should be automated)
  - **Batch multiple nits into one comment**

- [ ] **Use `[question]` for clarification**
  - Understanding intent
  - Asking about edge cases
  - Verifying assumptions

- [ ] **Use `[praise]` for good work**
  - Excellent patterns
  - Clever solutions
  - Great test coverage
  - Clear documentation

---

## Final Decision (< 30 minutes total)

### Time Check
- [ ] **Review completed in < 30 minutes**
  - If not, stop and explain what you've reviewed
  - Or request PR be split
  - Or bring in additional reviewer

### Make Your Decision

**✅ Approve** if:
- [ ] No `[critical]` or `[issue]` items
- [ ] Only `[suggestion]` and `[nit]` items remain
- [ ] Confident this won't break production
- [ ] Author has addressed previous feedback

**Comment template:**
> Great work! Just a few minor suggestions (non-blocking):
>
> [suggestion] Consider extracting validation logic for reuse
> [nit] Typo in comment on line 45
>
> Feel free to address or ignore—approving now. ✅

---

**🔄 Request Changes** if:
- [ ] Any `[critical]` items found
- [ ] Multiple `[issue]` items need fixing
- [ ] Approach needs rethinking
- [ ] Missing critical functionality

**Comment template:**
> Thanks for the PR! Found a few issues that need addressing:
>
> [critical] Security issue on line 78: Missing authorization check
> [issue] Missing error handling on line 102
> [issue] No tests for `createUser` function
>
> Please fix these and I'll review again. Happy to discuss!

---

**💬 Comment** (no decision) if:
- [ ] Leaving feedback but deferring to another reviewer
- [ ] Partial review completed, someone else should finish
- [ ] Waiting on clarification

**Comment template:**
> Reviewed authentication changes—security looks good. Deferring to @backend-expert for database migration aspects.
>
> [question] How does this handle token refresh?

---

## Review Hygiene

- [ ] **Batch nits and suggestions**
  - Don't leave 10 separate nit comments
  - Group minor issues into one comment
  - Make it clear they're non-blocking

- [ ] **Leave at least one `[praise]` comment** (if applicable)
  - Reinforce good patterns
  - Build positive team culture
  - Mentors > nit-bots

- [ ] **Be constructive and specific**
  - Explain the problem clearly
  - Suggest solutions
  - Assume good intent

- [ ] **Respond to all author replies**
  - Answer questions promptly
  - Acknowledge fixes
  - Re-review when requested

---

## Advanced Scenarios

### Large PR (> 400 lines)
- [ ] Ask: Can this be split?
- [ ] If not, review commit-by-commit
- [ ] Comment on specific commits
- [ ] May need multiple review sessions

### Complex Refactor
- [ ] Verify behavior unchanged (tests pass)
- [ ] Check test coverage maintained
- [ ] Look for subtle logic changes
- [ ] Validate performance not degraded

### Disagreement with Author
- [ ] Assume good intent
- [ ] Ask questions to understand reasoning
- [ ] Provide specific concerns
- [ ] Seek compromise or escalate if needed

---

## Post-Review

- [ ] **Monitor for author responses**
  - Respond to questions quickly
  - Acknowledge fixes
  - Re-review if significant changes

- [ ] **Learn from the review**
  - Patterns to apply elsewhere?
  - Anti-patterns to watch for?
  - Knowledge gaps to fill?

---

**Remember:** Your goal is catching problems that harm the codebase while enabling fast shipping. Balance thoroughness with velocity.

**Questions?** See:
- [Reviewer Guide](../playbook/reviewer-guide.md) - Detailed methodology
- [Comment Classification](../playbook/comment-classification.md) - Detailed taxonomy
- [Main Skill](../SKILL.md) - Overview and principles
