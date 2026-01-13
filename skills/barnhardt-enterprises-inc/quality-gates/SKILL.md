---
name: quality-gates
description: Checkpoint framework and validation rules for all agents. Ensures quality gates are passed at every stage of development.
allowed-tools: Read, Grep, Bash
---

# Quality Gates (Checkpoint Framework)

## When to Use
- Before starting implementation (pre-implementation gate)
- During implementation (implementation gate)
- After writing tests (testing gate)
- Before completing work (review gate)

## Overview

Quality gates are checkpoints that prevent bugs from being committed. Every agent must pass these gates before proceeding.

## Gate Framework

### Pre-Implementation Gate
**Must pass BEFORE writing any code:**

- [ ] Requirements fully understood
- [ ] Architecture decision made
- [ ] Types and interfaces planned
- [ ] Dependencies identified
- [ ] Security implications assessed
- [ ] Pattern compliance verified

**How to pass:**
1. Read all related files and tests
2. Document understanding in brief plan
3. Identify which architectural patterns apply
4. List all types/interfaces needed
5. Check for security concerns (auth, input validation, etc.)

### Implementation Gate
**Must pass DURING code writing:**

- [ ] TypeScript strict mode (no `any`, no `@ts-ignore`)
- [ ] Explicit types on all functions (params + return)
- [ ] Error handling for all failure cases
- [ ] Input validation using Zod schemas
- [ ] No hardcoded secrets (use env vars)
- [ ] No console.log statements
- [ ] Security best practices followed

**How to pass:**
1. Run TypeScript compiler: `npx tsc --noEmit`
2. Check for `any` types: `grep -r ": any" src/`
3. Check for `@ts-ignore`: `grep -r "@ts-ignore" src/`
4. Verify Zod validation on all inputs
5. Verify error handling with try/catch
6. Check environment variables used correctly

**Validators:**
- typescript-strict-guard/validate-types.py
- security-sentinel/validate-security.py
- nextjs-15-specialist/validate-patterns.py

### Testing Gate
**Must pass AFTER implementation:**

- [ ] Tests written FIRST (TDD)
- [ ] AAA pattern followed (Arrange, Act, Assert)
- [ ] Coverage ≥ 75% overall
- [ ] Coverage ≥ 90% for business logic (services, utils)
- [ ] All tests passing
- [ ] No skipped tests without reason
- [ ] E2E tests for visual state changes

**How to pass:**
1. Run tests: `npm test -- --run`
2. Check coverage: `npm test -- --coverage`
3. Verify AAA pattern in all tests
4. Ensure no `.skip()` or `.only()` in tests
5. Check E2E tests exist for UI changes

**Validators:**
- tdd-enforcer/validate-coverage.py
- quality-gates/validate-test-quality.py

### Review Gate
**Must pass BEFORE finishing:**

- [ ] Code review passed (no critical issues)
- [ ] Security audit passed (OWASP Top 10)
- [ ] All quality gates passed
- [ ] Documentation updated if needed
- [ ] No breaking changes without migration plan
- [ ] Build succeeds: `npm run build`

**How to pass:**
1. Run code-reviewer agent
2. Run security-auditor agent (for auth/API/data handling)
3. Run all validators: `quality-gates/validate.py`
4. Verify build: `npm run build`
5. Check documentation updated

**Validators:**
- quality-gates/validate.py (aggregates all)
- security-sentinel/validate-security.py
- drizzle-orm-patterns/validate-queries.py

## Validation Rules

### TypeScript Strict Mode
```typescript
// ❌ BLOCKS: Using 'any' type
function process(data: any) { }

// ✅ PASSES: Explicit types
function process(data: UserData): ProcessedData { }

// ❌ BLOCKS: @ts-ignore
// @ts-ignore
const value = getData()

// ✅ PASSES: Type guard
if (isValidData(value)) {
  const data = getData()
}

// ❌ BLOCKS: Non-null assertion
const user = users.find(u => u.id === id)!

// ✅ PASSES: Null handling
const user = users.find(u => u.id === id)
if (!user) throw new Error('User not found')
```

### Input Validation
```typescript
// ❌ BLOCKS: No validation
export async function POST(request: Request) {
  const body = await request.json()
  const user = await createUser(body) // Unsafe!
}

// ✅ PASSES: Zod validation
import { z } from 'zod'

const createUserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

export async function POST(request: Request) {
  const body = await request.json()
  const validated = createUserSchema.parse(body)
  const user = await createUser(validated)
}
```

### Error Handling
```typescript
// ❌ BLOCKS: No error handling
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`)
  return response.json() // What if it fails?
}

// ✅ PASSES: Proper error handling
async function fetchUser(id: string): Promise<User> {
  try {
    const response = await fetch(`/api/users/${id}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    logger.error('fetchUser failed', { id, error })
    throw new Error(`Failed to fetch user ${id}`)
  }
}
```

### Security
```typescript
// ❌ BLOCKS: Hardcoded secrets
const apiKey = 'sk_live_abc123'

// ✅ PASSES: Environment variables
const apiKey = process.env.STRIPE_API_KEY
if (!apiKey) throw new Error('STRIPE_API_KEY not set')

// ❌ BLOCKS: SQL injection risk
const query = `SELECT * FROM users WHERE email = '${email}'`

// ✅ PASSES: Parameterized queries (Prisma)
const user = await prisma.user.findUnique({ where: { email } })
```

### Test Quality
```typescript
// ❌ BLOCKS: No AAA pattern
it('should work', () => {
  const result = doThing()
  expect(result).toBe(true)
  const other = doOther()
  expect(other).toBe(false)
})

// ✅ PASSES: AAA pattern
it('should return true for valid input', () => {
  // ARRANGE: Setup test data
  const input = { valid: true }

  // ACT: Execute behavior
  const result = doThing(input)

  // ASSERT: Verify outcome
  expect(result).toBe(true)
})

// ❌ BLOCKS: Only mock assertions for UI
it('should change color', () => {
  fireEvent.click(button)
  expect(mockSetColor).toHaveBeenCalled()
})

// ✅ PASSES: DOM state assertions
it('should change color', () => {
  const button = getByTestId('button')
  expect(button).toHaveClass('bg-blue-500')

  fireEvent.click(button)
  expect(button).toHaveClass('bg-red-500')
})
```

## Progressive Disclosure

Agents load metadata first (this file), then supporting files as needed:

1. **SKILL.md** (this file) - Overview and quick reference
2. **checkpoint-framework.md** - Detailed gate requirements
3. **validation-rules.md** - Comprehensive validation criteria
4. **test-patterns.md** - TDD patterns and coverage requirements
5. **validate.py** - Automated validation script

## Usage Pattern

```typescript
// Agent workflow example:
1. Load quality-gates skill metadata
2. Check pre-implementation gate
3. Plan implementation
4. Check implementation gate during coding
5. Write tests
6. Check testing gate
7. Request code review
8. Check review gate
9. Finish only when all gates pass
```

## Integration with Other Skills

Quality gates aggregate validation from:
- **typescript-strict-guard**: Type safety validation
- **security-sentinel**: Security vulnerability checks
- **nextjs-15-specialist**: Next.js pattern compliance
- **drizzle-orm-patterns**: Database query safety
- **tdd-enforcer**: Test coverage and quality

## Critical Rules

1. **Never bypass gates** - If a gate fails, fix the issue, don't skip
2. **Fail fast** - Check gates early and often
3. **Automate validation** - Use validate.py before finishing
4. **Document exceptions** - Any deviation needs explicit approval

## See Also

- checkpoint-framework.md - Detailed gate requirements
- validation-rules.md - Complete validation rules
- test-patterns.md - TDD patterns
- ../typescript-strict-guard/SKILL.md - TypeScript validation
- ../security-sentinel/SKILL.md - Security validation
