# Checkpoint Framework

Detailed requirements for each quality gate.

## Pre-Implementation Gate

### Purpose
Ensure complete understanding before writing code. Prevents wasted effort and architectural mistakes.

### Requirements

#### 1. Requirements Understanding
- [ ] All user requirements documented
- [ ] All test requirements understood
- [ ] Success criteria defined
- [ ] Edge cases identified
- [ ] Error conditions listed

**How to verify:**
- Can you explain the feature in 2-3 sentences?
- Can you list all test cases from memory?
- Do you know what "done" looks like?

#### 2. Architecture Decision
- [ ] Component structure planned (Server vs Client)
- [ ] Data flow designed (RSC, React Query, SSE)
- [ ] File locations decided
- [ ] Dependencies identified
- [ ] Integration points mapped

**How to verify:**
- Can you draw the data flow?
- Do you know which files to create/modify?
- Do you know what to import and from where?

#### 3. Type Planning
- [ ] All interfaces defined
- [ ] All types defined
- [ ] Zod schemas planned
- [ ] API contracts documented
- [ ] Database schema known

**How to verify:**
- Can you write type signatures without running code?
- Do you know what Zod schemas you need?
- Are database types compatible?

#### 4. Security Assessment
- [ ] Authentication needed? How?
- [ ] Authorization needed? What rules?
- [ ] Input validation? What schemas?
- [ ] Sensitive data? How to protect?
- [ ] OWASP Top 10 reviewed for applicable risks

**How to verify:**
- Is this endpoint public or protected?
- What user inputs exist? Are they validated?
- Is sensitive data logged or exposed?

#### 5. Pattern Compliance
- [ ] Identified which architectural patterns apply
- [ ] Found existing examples of pattern usage
- [ ] Understand pattern implementation
- [ ] Know pattern testing requirements

**How to verify:**
- Which pattern are you using? (SSE, RSC, React Query, etc.)
- Can you point to an existing example?
- Do you know how to test this pattern?

### Passing Criteria
**You may proceed to implementation when:**
- All 5 areas above are checked
- You can explain the solution without looking at code
- You know what tests need to pass
- You have a clear mental model

### Failing Criteria
**Stop and gather more information if:**
- Any checkbox is unchecked
- You have unanswered questions
- You're not sure about architecture
- You don't know what success looks like

---

## Implementation Gate

### Purpose
Ensure code quality while writing. Prevents technical debt and security vulnerabilities.

### Requirements

#### 1. TypeScript Strict Mode
- [ ] No `any` type used
- [ ] No `@ts-ignore` comments
- [ ] No `!` non-null assertions without explanation
- [ ] Explicit types on all function parameters
- [ ] Explicit return types on all functions
- [ ] Type guards for runtime validation

**Validation:**
```bash
# Check for violations
npx tsc --noEmit
grep -r ": any" src/
grep -r "@ts-ignore" src/
grep -r "!" src/ | grep -v "!=" | grep -v "!=="
```

#### 2. Error Handling
- [ ] All async operations have try/catch
- [ ] All errors are logged with context
- [ ] User-facing errors are informative
- [ ] No silent failures
- [ ] Proper error types used

**Pattern:**
```typescript
async function operation(): Promise<Result> {
  try {
    const result = await riskyOperation()
    return result
  } catch (error) {
    logger.error('operation failed', { context, error })
    throw new Error('User-friendly message')
  }
}
```

#### 3. Input Validation
- [ ] All user input validated with Zod
- [ ] All API inputs validated
- [ ] All form inputs validated
- [ ] Validation errors are informative
- [ ] Edge cases handled (empty, null, max, min)

**Pattern:**
```typescript
const schema = z.object({
  email: z.string().email().max(255),
  age: z.number().min(0).max(150),
})

const validated = schema.parse(input) // Throws on invalid
```

#### 4. Security Best Practices
- [ ] No hardcoded secrets
- [ ] Environment variables used for config
- [ ] Authentication checked on protected routes
- [ ] Authorization enforced (user owns resource)
- [ ] SQL injection prevented (using Prisma)
- [ ] XSS prevented (no dangerouslySetInnerHTML without sanitization)

**Validation:**
```bash
# Check for hardcoded secrets
grep -r "api_key\|apiKey\|secret\|password" src/ | grep -v "process.env"

# Check for XSS risks
grep -r "dangerouslySetInnerHTML" src/
```

#### 5. Code Quality
- [ ] No console.log statements
- [ ] No commented-out code
- [ ] No TODO without GitHub issue
- [ ] Functions have single responsibility
- [ ] Variable names are descriptive
- [ ] No dead code

**Validation:**
```bash
# Check for debug code
grep -r "console.log\|console.debug" src/
grep -r "debugger" src/

# Check for TODOs
grep -r "TODO\|FIXME\|HACK" src/
```

### Passing Criteria
**Continue coding when:**
- All validations pass
- TypeScript compiles without errors
- No security vulnerabilities detected
- Code follows patterns

### Failing Criteria
**Stop and fix when:**
- TypeScript compilation fails
- Security check fails
- Code quality check fails
- Pattern violation detected

---

## Testing Gate

### Purpose
Ensure comprehensive test coverage and quality. Prevents bugs from reaching production.

### Requirements

#### 1. TDD Compliance
- [ ] Tests written BEFORE implementation
- [ ] Tests failed initially (red)
- [ ] Implementation made tests pass (green)
- [ ] Code refactored while tests pass (refactor)
- [ ] No skipped tests (`.skip()`) without reason

**Verification:**
```bash
# Check for skipped tests
grep -r ".skip\|.todo" tests/

# Check for focused tests
grep -r ".only" tests/
```

#### 2. AAA Pattern
- [ ] Every test has Arrange section
- [ ] Every test has Act section
- [ ] Every test has Assert section
- [ ] Sections are clearly separated
- [ ] Each test tests ONE behavior

**Good Example:**
```typescript
it('should create user with hashed password', async () => {
  // ARRANGE: Setup test data
  const userData = { email: 'test@example.com', password: 'Pass123!' }

  // ACT: Execute behavior
  const user = await authService.register(userData)

  // ASSERT: Verify outcome
  expect(user.id).toBeDefined()
  expect(user).not.toHaveProperty('password')
})
```

#### 3. Coverage Requirements
- [ ] Overall coverage ≥ 75%
- [ ] Business logic (services/) ≥ 90%
- [ ] Utilities (utils/) ≥ 90%
- [ ] API routes ≥ 75%
- [ ] UI components ≥ 60%
- [ ] All branches covered
- [ ] All edge cases tested

**Validation:**
```bash
npm test -- --coverage --run
```

**Coverage Report Must Show:**
- Statements: ≥ 75%
- Branches: ≥ 75%
- Functions: ≥ 75%
- Lines: ≥ 75%

#### 4. Test Quality
- [ ] Tests are independent (no order dependency)
- [ ] Tests clean up after themselves
- [ ] Tests use proper mocks
- [ ] Tests verify behavior, not implementation
- [ ] UI tests verify DOM state, not just mocks
- [ ] E2E tests exist for visual changes

**UI Testing:**
```typescript
// ❌ BAD: Only mock assertions
it('should toggle state', () => {
  fireEvent.click(button)
  expect(mockToggle).toHaveBeenCalled()
})

// ✅ GOOD: DOM state assertions
it('should toggle state', () => {
  const button = getByTestId('toggle-button')
  expect(button).toHaveClass('bg-blue-500')

  fireEvent.click(button)
  expect(button).toHaveClass('bg-red-500')
  expect(button).not.toHaveClass('bg-blue-500')
})
```

#### 5. E2E Requirements
- [ ] Critical user journeys have E2E tests
- [ ] Visual state changes have E2E tests
- [ ] Multi-step flows have E2E tests
- [ ] Authentication flows have E2E tests
- [ ] Payment flows have E2E tests (if applicable)

### Passing Criteria
**Proceed to review when:**
- All tests pass: `npm test -- --run`
- Coverage meets thresholds
- AAA pattern followed
- No skipped/focused tests
- E2E tests exist where needed

### Failing Criteria
**Stop and improve tests when:**
- Any test fails
- Coverage below threshold
- Tests don't follow AAA pattern
- UI tests only check mocks
- Missing E2E tests for critical flows

---

## Review Gate

### Purpose
Final quality check before completion. Prevents shipping known issues.

### Requirements

#### 1. Code Review
- [ ] Code-reviewer agent passed
- [ ] No critical issues found
- [ ] No security vulnerabilities
- [ ] No performance issues
- [ ] No maintainability issues
- [ ] All feedback addressed

**How to verify:**
Run code-reviewer agent and address all findings.

#### 2. Security Audit
- [ ] Security-auditor passed (for auth/API/data code)
- [ ] OWASP Top 10 checked
- [ ] No injection vulnerabilities
- [ ] No authentication bypasses
- [ ] No sensitive data exposure
- [ ] All security feedback addressed

**How to verify:**
Run security-auditor agent for auth, API routes, user input handling.

#### 3. Build Verification
- [ ] TypeScript compiles: `npx tsc --noEmit`
- [ ] Tests pass: `npm test -- --run`
- [ ] Linting passes: `npm run lint`
- [ ] Build succeeds: `npm run build`
- [ ] No runtime errors in dev: `npm run dev`

**Validation:**
```bash
npx tsc --noEmit
npm run lint
npm test -- --run
npm run build
```

#### 4. Documentation
- [ ] Public APIs documented
- [ ] Complex logic has comments
- [ ] README updated if needed
- [ ] CLAUDE.md updated if patterns changed
- [ ] Migration guide if breaking changes

**When to update docs:**
- New architectural pattern introduced
- New environment variable required
- Breaking API change
- New critical dependency

#### 5. Final Validation
- [ ] All quality gates passed
- [ ] validate.py runs successfully
- [ ] No known issues
- [ ] Ready for deployment

**Run final validation:**
```bash
.claude/skills/quality-gates/validate.py
```

### Passing Criteria
**Complete work when:**
- All 5 areas checked
- All validators pass
- Build succeeds
- No known issues
- Documentation current

### Failing Criteria
**Keep working when:**
- Any validation fails
- Code review found issues
- Security audit found vulnerabilities
- Build fails
- Documentation outdated

---

## Gate Bypass Process

### When Bypass is Allowed
**NEVER** for:
- TypeScript strict mode violations
- Security vulnerabilities
- Test coverage below threshold
- Failing tests

**RARELY** for:
- Specific `@ts-ignore` with extensive comment explaining why
- Console.log in development-only code with clear comment

### How to Request Bypass
1. Document exact reason bypass is needed
2. Document why fix is not possible
3. Document plan to fix in future
4. Create GitHub issue to track
5. Get explicit user approval
6. Add extensive comment in code

### Bypass Documentation Template
```typescript
// BYPASS: quality-gate-name
// REASON: [Detailed explanation of why bypass is needed]
// ISSUE: #123 [Link to GitHub issue]
// APPROVED: [User name] [Date]
// PLAN: [How this will be fixed]
```

---

## Summary

**4 Gates:**
1. **Pre-Implementation** - Understand before coding
2. **Implementation** - Quality while coding
3. **Testing** - Comprehensive tests
4. **Review** - Final verification

**Purpose:**
Prevent bugs from being committed through systematic checkpoints.

**Critical Rule:**
Never bypass gates without explicit approval and documentation.
