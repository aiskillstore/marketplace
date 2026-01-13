# Reviewer Guide: Two-Pass Review Methodology

<context>
This guide implements the two-pass review methodology that maximizes review effectiveness while respecting cognitive limits. Pass 1 focuses on design and approach (5-10 minutes). Pass 2 focuses on implementation details (10-20 minutes). Total time budget: < 30 minutes per review.
</context>

## Before You Start

### Assess Review Feasibility

**Check these factors before committing to review:**

1. **PR Size**: Can you review this effectively?
   - < 200 lines: Quick review, 10-15 minutes
   - 200-400 lines: Standard review, 20-30 minutes
   - 400-800 lines: Large review, 30-60 minutes (consider requesting split)
   - > 800 lines: Very large, likely needs split or multiple reviewers

2. **PR Description**: Is context clear?
   - If description is minimal or missing, ask author to add it **before reviewing**
   - You can't review effectively without understanding why/what

3. **Your Context**: Are you the right reviewer?
   - Do you have domain knowledge for this area?
   - Are you familiar with the codebase section?
   - If not, suggest a better reviewer or pair with domain expert

**If any of these are problematic, comment immediately:**

```markdown
This PR is quite large (847 lines). Could we split it into:
1. Refactor existing auth service (foundation)
2. Add new 2FA functionality (feature)
3. Update UI components (presentation)

This would make review faster and safer.
```

Or:

```markdown
I don't have enough context for this subsystem. Tagging @domain-expert who has more background in this area.
```

## Pass 1: High-Level Review (5-10 minutes)

**Goal:** Validate design and approach before diving into details.

**Set a 10-minute timer.** If you find major issues, stop and provide feedback. No need for detailed review if the approach is wrong.

### Step 1: Read PR Description (2 minutes)

**Understand the context:**
- Why is this change needed?
- What problem does it solve?
- What is the proposed solution?

**Red flags:**
- Missing or minimal description
- Unclear problem statement
- No test plan
- No deployment considerations

**If description is inadequate, stop and request more information:**
> The PR description doesn't explain why this change is needed. Could you add context about the problem this solves and why this approach was chosen?

### Step 2: Review High-Level Design (3-5 minutes)

**Focus on architecture and approach, not implementation details.**

**Questions to ask:**
1. **Correctness**: Does this solve the right problem?
2. **Approach**: Is this the right way to solve it?
3. **Architecture**: Fits existing patterns? Justified deviation?
4. **API Design**: Are interfaces clear and maintainable?
5. **Data Flow**: How does data move through the system? Any issues?

**Run automated design review:**
```bash
# For TypeScript/architecture review
/review-quality path/to/changed/files

# Focus on high-level observations in output
```

**Red flags:**
- Solving wrong problem
- Overly complex solution to simple problem
- Introduces new pattern without justification
- Breaking changes without migration path
- Performance anti-patterns (N+1 queries, unnecessary loops)

### Step 3: Security & Risk Assessment (2-3 minutes)

**If PR touches sensitive areas, run security review:**

**Sensitive areas:**
- Authentication/authorization
- User data handling
- API endpoints
- Database queries
- File uploads/downloads
- Payment processing
- Admin functionality

**Run automated security review:**
```bash
/review-security path/to/changed/files
```

**Manual security checks:**
- Input validation present?
- Authorization checks in place?
- Sensitive data logged or exposed?
- SQL injection risks (use parameterized queries)?
- XSS risks (escape user input)?
- CSRF protection if needed?

**Red flags:**
- Missing input validation
- No authorization checks
- Secrets or credentials in code
- User input directly in queries or templates
- Missing rate limiting for sensitive operations

### Step 4: Scope Check (1 minute)

**Verify PR is focused:**
- Single, clear purpose?
- Any unrelated changes?
- Reasonable size for the scope?

**Red flags:**
- Multiple unrelated features in one PR
- Behavioral changes mixed with refactoring
- Mass reformatting hiding logic changes

### Pass 1 Decision Point

**If you found major issues:**
- Leave comments with `[critical]` or `[issue]` classification
- Mark "Request Changes"
- Stop review—no need for Pass 2 until issues resolved

**If high-level looks good:**
- Proceed to Pass 2
- Or: Leave preliminary "looks good so far" comment and schedule Pass 2

## Pass 2: Implementation Review (10-20 minutes)

**Goal:** Verify implementation correctness, test quality, and code maintainability.

**Set a 20-minute timer.** Focus on details that affect correctness and maintainability.

### Step 1: Logic & Correctness (5-7 minutes)

**Read the actual implementation:**

**Questions to ask:**
1. **Correctness**: Does the code do what it's supposed to?
2. **Edge Cases**: What happens with null/undefined/empty/zero values?
3. **Error Handling**: Are errors caught and handled appropriately?
4. **State Management**: Are state changes safe and intentional?
5. **Concurrency**: Any race conditions or async issues?

**Run automated quality review:**
```bash
/review-quality path/to/changed/files
```

**Common logic issues:**
- Off-by-one errors
- Missing null checks
- Incorrect boolean logic
- Not handling async properly (missing await)
- Mutation of shared state
- Infinite loops or recursion without base case

**Example comments:**
```markdown
[issue] This will throw if `user` is null. Add a null check:
``​`typescript
if (!user) {
  throw new Error('User not found');
}
``​`

[critical] Race condition: Two simultaneous requests could both read the old value and increment, losing one update. Use atomic increment or locking.
```

### Step 2: Testing Quality (3-5 minutes)

**Verify tests are meaningful:**

**Questions to ask:**
1. **Coverage**: Are new functions/features tested?
2. **Quality**: Do tests actually verify behavior, or just call functions?
3. **Edge Cases**: Are error scenarios and boundary conditions tested?
4. **Clarity**: Can you understand what's being tested?

**Run automated testing review:**
```bash
/review-testing path/to/changed/files
```

**Red flags:**
- No tests for new functionality
- Tests that don't assert anything meaningful
- Tests that test implementation details, not behavior
- Missing edge case tests
- Tests that will pass even if feature is broken

**Example comments:**
```markdown
[issue] The `createUser` function isn't tested. Please add tests covering:
- Successful user creation
- Duplicate email error
- Invalid email format error
- Database connection error

[suggestion] This test checks internal state instead of observable behavior. Consider testing the output/side effects instead of implementation details.
```

### Step 3: Code Quality & Readability (3-5 minutes)

**Assess maintainability:**

**Questions to ask:**
1. **Naming**: Are names clear and consistent?
2. **Structure**: Is code organized logically?
3. **Complexity**: Is this as simple as it can be?
4. **Duplication**: Any copy-pasted code?
5. **Documentation**: Are complex parts explained?

**Run automated readability review:**
```bash
/review-readability path/to/changed/files
```

**Common readability issues:**
- Unclear variable names (`data`, `temp`, `x`)
- Functions doing too many things
- Deep nesting (> 3 levels)
- Long functions (> 50 lines)
- Magic numbers without explanation
- Insufficient comments for complex logic

**Example comments:**
```markdown
[nit] Variable name `c` is unclear. Consider `verificationCode` for better readability.

[suggestion] This function is doing three distinct things: validation, database query, and email sending. Consider extracting into separate functions for better testability and clarity.

[suggestion] This conditional logic is complex. Adding a comment explaining the business rule would help future maintainers.
```

### Step 4: Documentation Review (2-3 minutes)

**Check for adequate documentation:**

**What should be documented:**
- Public APIs (JSDoc with param/return types and descriptions)
- Complex algorithms (explain the "why", not just the "what")
- Non-obvious business rules
- README updates for new features
- Architecture docs for significant changes

**What doesn't need documentation:**
- Self-explanatory code
- Simple getters/setters
- Obvious logic

**Example comments:**
```markdown
[issue] This is a public API function but has no JSDoc. Please add:
``​`typescript
/**
 * Sends a password reset email to the user.
 *
 * @param email - User's email address
 * @returns Promise resolving to true if email sent, false if user not found
 * @throws {EmailServiceError} if email service is unavailable
 */
export async function sendPasswordReset(email: string): Promise<boolean>
``​`

[suggestion] This algorithm is non-obvious. A comment explaining why we use this approach would help future maintainers.
```

## Comment Classification

**Always classify your comments** to reduce friction and set clear expectations.

### [critical] - Must Fix Before Merge

**Use for:**
- Security vulnerabilities
- Data loss or corruption risks
- Breaking changes without migration
- Incorrect core logic that will cause failures

**Example:**
```markdown
[critical] This endpoint doesn't check user permissions. Attackers could access other users' private data.

Fix by adding permission check:
``​`typescript
if (currentUser.id !== requestedUserId && !currentUser.isAdmin) {
  throw new UnauthorizedError();
}
``​`
```

### [issue] - Should Fix

**Use for:**
- Bugs that may not always manifest
- Missing error handling
- Significant performance problems
- Missing tests for core functionality
- Incorrect behavior in edge cases

**Example:**
```markdown
[issue] This will fail if the API returns an empty array. Add a check:
``​`typescript
if (results.length === 0) {
  return defaultValue;
}
``​`
```

### [suggestion] - Nice to Have

**Use for:**
- Better patterns or approaches
- Performance optimizations (non-critical)
- Refactoring opportunities
- Code organization improvements

**Example:**
```markdown
[suggestion] Consider using `Array.map()` here for better readability:
``​`typescript
const names = users.map(u => u.name);
``​`

Instead of:
``​`typescript
const names = [];
for (const u of users) {
  names.push(u.name);
}
``​`
```

### [nit] - Purely Cosmetic

**Use sparingly.** Batch multiple nits into one comment. Don't block PR on nits.

**Use for:**
- Typos in comments
- Formatting (should be automated)
- Minor naming preferences
- Whitespace

**Example:**
```markdown
[nit] A few minor items (non-blocking):
- Line 45: Typo in comment: "recieve" → "receive"
- Line 67: Extra blank line
- Line 89: Variable could be named `userData` instead of `data` for clarity
```

### [question] - Seeking Clarification

**Use to understand intent, not to imply wrongness.**

**Example:**
```markdown
[question] How does this handle the case where the user's session has expired? Do we redirect to login or refresh the token?

[question] Is there a reason we're using a Set here instead of an Array? Just curious about the data structure choice.
```

### [praise] - Calling Out Good Work

**Don't just point out problems—call out good patterns!**

**Example:**
```markdown
[praise] Excellent use of the builder pattern here. Much cleaner than the old approach!

[praise] Great test coverage! I especially like the edge case tests for empty arrays and null values.

[praise] This error message is really clear and actionable. Users will know exactly what went wrong and how to fix it.
```

## Making Your Final Decision

### Approve

**Use when:**
- No `[critical]` or `[issue]` items
- Only `[suggestion]` and `[nit]` items remain
- Confident this won't break production
- Author has addressed previous round of feedback

**Approval comment example:**
```markdown
Great work! Just a few minor suggestions (non-blocking):

[suggestion] Consider extracting the validation logic for reuse
[nit] Typo in comment on line 45

Feel free to address or ignore these—approving now. ✅
```

### Request Changes

**Use when:**
- Any `[critical]` items found
- Multiple `[issue]` items that need fixing
- Approach needs rethinking
- Missing critical functionality (like tests)

**Request changes comment example:**
```markdown
Thanks for the PR! Found a few issues that need to be addressed:

[critical] Security issue on line 78: Missing authorization check
[issue] Missing error handling on line 102
[issue] No tests for the new `createUser` function

Please fix these and I'll take another look. Happy to discuss any questions!
```

### Comment (No Approval Decision)

**Use when:**
- Leaving feedback but deferring to another reviewer
- Partial review completed, someone else should finish
- Waiting on author clarification before deciding

**Comment example:**
```markdown
Reviewed the authentication changes—security looks good. Deferring to @backend-expert for the database migration aspects as that's outside my expertise.

[question] Clarify how this handles token refresh?
```

## Time Management

### Respect Your Time Budget

**Target: < 30 minutes per review**

**If you can't complete in 30 minutes:**
- **Option 1**: Stop and comment on what you've reviewed so far
  > Reviewed Pass 1—approach looks good. Need more time for detailed implementation review. Will continue tomorrow.

- **Option 2**: Request PR be split
  > This PR is too large for effective review in one session (>800 lines). Could we split into smaller PRs?

- **Option 3**: Bring in additional reviewer
  > This is more complex than I can review alone. Tagging @expert for a second opinion on the algorithm implementation.

### Batch Nits and Suggestions

**Don't leave 15 individual comments for minor issues.**

**Bad (many individual comments):**
- Line 10: typo
- Line 15: rename variable
- Line 23: extra whitespace
- Line 34: comment typo
- ... (11 more)

**Good (single batched comment):**
```markdown
[nit] Minor formatting/naming items (all optional):
- Line 10: Typo "recieve" → "receive"
- Line 15: Consider renaming `data` to `userData`
- Line 23: Extra whitespace
- Line 34: Comment typo "teh" → "the"

None of these block approval—feel free to batch fix if you have time.
```

## Advanced Scenarios

### Reviewing Large PRs (> 400 lines)

**If PR can't be split, use commit-by-commit review:**

1. Ask author: "Are commits structured logically?"
2. Review each commit individually
3. Comment on specific commits
4. Easier to digest than entire diff at once

**Example:**
> I'll review this commit-by-commit since it's large:
>
> **Commit 1** (Add AuthService skeleton): ✅ Looks good, clean interfaces
> **Commit 2** (Implement login logic): [issue] Missing rate limiting
> **Commit 3** (Add 2FA): ✅ Well tested
> ...

### Reviewing Refactors

**Refactors are high-risk—pay extra attention:**

1. **Verify behavior unchanged:** Tests should still pass
2. **Check test coverage:** Refactor shouldn't reduce coverage
3. **Look for subtle logic changes:** Easy to introduce bugs
4. **Validate performance:** Ensure refactor doesn't degrade performance

**Use tools to verify:**
```bash
# Run tests before and after to verify behavior unchanged
npm test

# Check test coverage
npm run test:coverage
```

### Handling Disagreements

**If you and author disagree:**

1. **Assume good intent:** They may have context you lack
2. **Ask questions:** "Help me understand why you chose this approach?"
3. **Provide reasoning:** Explain your concern with specifics
4. **Seek compromise:** Is there a middle ground?
5. **Escalate if needed:** Tag team lead or architect for tiebreaker

**Example:**
> I suggested extracting this into a service, but you kept it inline. I'm concerned about testability—how would we unit test this logic without the full component setup?
>
> If there's a testing strategy I'm missing, I'm happy to approve as-is. Otherwise, could we discuss alternatives?

## Review Checklist

Use this as a mental model during reviews:

**Pass 1 (High-Level):**
- [ ] PR description clear and complete
- [ ] Approach solves the right problem
- [ ] Design fits architecture
- [ ] Security considerations addressed (if applicable)
- [ ] Scope is focused and size reasonable

**Pass 2 (Implementation):**
- [ ] Logic is correct and handles edge cases
- [ ] Error handling appropriate
- [ ] Tests cover functionality meaningfully
- [ ] Code is readable and maintainable
- [ ] Naming is clear
- [ ] Documentation adequate

**Final Decision:**
- [ ] All comments classified
- [ ] At least one `[praise]` comment (if applicable)
- [ ] Decision made: Approve / Request Changes / Comment
- [ ] Total time: < 30 minutes (or justified if longer)

---

**Remember:** Your goal is not to find every tiny issue, but to catch problems that would harm the codebase while enabling authors to ship quality code quickly. Balance thoroughness with velocity.
