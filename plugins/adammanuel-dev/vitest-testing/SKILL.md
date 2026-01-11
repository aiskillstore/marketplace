---
name: vitest-testing
description: **AI-friendly comprehensive testing guidance for Vitest with practical patterns and behavior-driven development.**
---

# Vitest Testing Skill - Master Reference

**AI-friendly comprehensive testing guidance for Vitest with practical patterns and behavior-driven development.**

> **For humans:** Start with [README.md](README.md) for full navigation
> **For AI agents:** This file provides quick access to all skill resources

---

## 🎯 Quick Access for Agents

### Decision Support
- **What type of test should I write?** → [index.md](index.md)
- **How do I structure this test?** → [principles/aaa-pattern.md](principles/aaa-pattern.md)
- **Is this code testable?** → [refactoring/testability-patterns.md](refactoring/testability-patterns.md)

### Most Referenced Patterns
- **[F.I.R.S.T Principles](principles/first-principles.md)** - Fast, Isolated, Repeatable, Self-Checking, Timely
- **[AAA Pattern](principles/aaa-pattern.md)** - Arrange-Act-Assert structure
- **[Black Box Testing](strategies/black-box-testing.md)** - Test behavior through public APIs
- **[Test Doubles](patterns/test-doubles.md)** - Mocks, stubs, spies, fakes

---

## 📚 Skill Organization

### Core Principles `/principles/`
Foundation concepts that guide all testing decisions:

| File | Purpose | When to Use |
|------|---------|-------------|
| [first-principles.md](principles/first-principles.md) | F.I.R.S.T quality attributes | Every test |
| [aaa-pattern.md](principles/aaa-pattern.md) | Arrange-Act-Assert structure | Structuring tests |
| [bdd-integration.md](principles/bdd-integration.md) | Given/When/Then with AAA | Business-focused tests |

### Testing Strategies `/strategies/`
Approaches for different testing scenarios:

| File | Purpose | When to Use |
|------|---------|-------------|
| [black-box-testing.md](strategies/black-box-testing.md) | Testing via public APIs | Default approach (99% of tests) |
| [implementation-details.md](strategies/implementation-details.md) | When to test internals | Rare exceptions only |

### Practical Patterns `/patterns/`
Ready-to-use patterns for common scenarios:

| File | Purpose | When to Use |
|------|---------|-------------|
| [test-doubles.md](patterns/test-doubles.md) | Mocks, stubs, spies, fakes | Isolating dependencies |
| [async-testing.md](patterns/async-testing.md) | Testing promises, async/await | Async operations |
| [error-testing.md](patterns/error-testing.md) | Testing exceptions, edge cases | Error scenarios |
| [component-testing.md](patterns/component-testing.md) | React/Vue component patterns | UI components |
| [api-testing.md](patterns/api-testing.md) | HTTP clients, REST APIs | API integration |
| [performance-testing.md](patterns/performance-testing.md) | Benchmarks, load testing | Performance-critical code |
| [test-data.md](patterns/test-data.md) | Factories, builders, fixtures | Test data management |

### Refactoring for Testability `/refactoring/`
Transform untestable code into testable code:

| File | Purpose | When to Use |
|------|---------|-------------|
| [testability-patterns.md](refactoring/testability-patterns.md) | Extract pure functions, DI, etc. | Code hard to test |

### Quick Reference `/quick-reference/`
Fast lookups and decision aids:

| File | Purpose | When to Use |
|------|---------|-------------|
| [cheatsheet.md](quick-reference/cheatsheet.md) | Syntax, matchers, mocking | Quick syntax lookup |
| [jest-to-vitest.md](quick-reference/jest-to-vitest.md) | Migration from Jest | Migrating projects |

---

## 🤖 Agent Integration Points

### For typescript-coder Agent

**When writing tests:**
```typescript
// 1. Check decision tree
const testType = checkDecisionTree(codeType)
// Reference: /skills/vitest-testing/index.md

// 2. Apply F.I.R.S.T principles
ensureTestsAreFast()        // < 100ms
ensureTestsAreIsolated()    // No shared state
// Reference: /skills/vitest-testing/principles/first-principles.md

// 3. Use AAA structure
// Arrange → Act → Assert
// Reference: /skills/vitest-testing/principles/aaa-pattern.md

// 4. Follow black box strategy
testThroughPublicAPI()      // Not private methods
// Reference: /skills/vitest-testing/strategies/black-box-testing.md
```

**When refactoring:**
```typescript
// Check if code is testable
if (isHardToTest(code)) {
  // Apply testability patterns
  applyPattern(testabilityPatterns)
  // Reference: /skills/vitest-testing/refactoring/testability-patterns.md
}
```

### For Code Review Agents

**Check these aspects:**
- [ ] Tests follow F.I.R.S.T principles
- [ ] Tests use AAA structure
- [ ] Tests use black box approach (public APIs only)
- [ ] Proper mocking of external dependencies
- [ ] Error scenarios covered
- [ ] Async operations handled correctly

---

## 🎯 Common Workflows

### Workflow 1: Writing Tests for New Feature

```
1. Consult decision tree → /skills/vitest-testing/index.md
2. Determine test type → Unit/Integration/Component
3. Apply F.I.R.S.T principles → /skills/vitest-testing/principles/first-principles.md
4. Structure with AAA → /skills/vitest-testing/principles/aaa-pattern.md
5. Use relevant pattern → /skills/vitest-testing/patterns/
6. Reference examples → /skills/vitest-testing/examples/ (when created)
```

### Workflow 2: Refactoring for Testability

```
1. Identify pain points → What makes this hard to test?
2. Select pattern → /skills/vitest-testing/refactoring/testability-patterns.md
3. Apply pattern → Extract pure functions, inject dependencies, etc.
4. Write tests → Black box tests for refactored code
5. Verify → All tests pass, code is easier to test
```

### Workflow 3: Testing Async Code

```
1. Check async patterns → /skills/vitest-testing/patterns/async-testing.md
2. Mock external APIs → /skills/vitest-testing/patterns/test-doubles.md
3. Control timing → Use vi.useFakeTimers()
4. Test states → Loading, success, error
5. Verify cleanup → Resources released
```

---

## 📖 Philosophy

This skill follows these core beliefs:

### 1. Behavior over Implementation
Tests should verify WHAT the code does, not HOW it does it. Focus on observable outcomes and public contracts. Implementation details should be testable indirectly through public APIs.

### 2. Example-Driven Learning
Every principle includes practical examples. Before/after refactoring shows impact. Complete examples provide working templates.

### 3. Testability by Design
Code that's hard to test is poorly designed. Refactoring patterns transform untestable code. Testability improvements enhance overall code quality.

### 4. F.I.R.S.T Quality
Fast, Isolated, Repeatable, Self-Checking, Timely tests create a valuable safety net that developers trust and maintain.

---

## 🔍 Skill Map

```
vitest-testing/
├── SKILL.md                    ← You are here (AI agent entry point)
├── README.md                   ← Human navigation hub
├── index.md                    ← Decision tree
├── principles/                 ← Testing fundamentals
│   ├── first-principles.md     ← F.I.R.S.T (most important)
│   ├── aaa-pattern.md          ← Test structure
│   └── bdd-integration.md      ← Given/When/Then
├── strategies/                 ← Testing approaches
│   ├── black-box-testing.md    ← Default strategy
│   └── implementation-details.md ← Rare exceptions
├── patterns/                   ← Practical implementations
│   ├── test-doubles.md         ← Mocking (highly referenced)
│   ├── component-testing.md    ← React/UI testing
│   ├── async-testing.md        ← Promises, async/await
│   ├── error-testing.md        ← Error scenarios
│   ├── api-testing.md          ← HTTP/API testing
│   ├── performance-testing.md  ← Benchmarks, load tests
│   └── test-data.md            ← Factories, builders
├── refactoring/                ← Making code testable
│   └── testability-patterns.md ← Extract, inject, isolate
└── quick-reference/            ← Fast lookups
    ├── cheatsheet.md           ← Syntax reference
    └── jest-to-vitest.md       ← Migration guide
```

---

## 🎓 Learning Paths

### For Beginners
1. [F.I.R.S.T Principles](principles/first-principles.md) - Understand quality attributes
2. [AAA Pattern](principles/aaa-pattern.md) - Learn test structure
3. [Cheatsheet](quick-reference/cheatsheet.md) - Basic syntax
4. [Test Doubles](patterns/test-doubles.md) - Mocking basics

### For Intermediate Developers
1. [Black Box Testing](strategies/black-box-testing.md) - Strategy
2. [BDD Integration](principles/bdd-integration.md) - Business focus
3. [Async Testing](patterns/async-testing.md) - Handle promises
4. [Component Testing](patterns/component-testing.md) - UI testing

### For Advanced Developers
1. [Testability Patterns](refactoring/testability-patterns.md) - Design for testability
2. [Implementation Details](strategies/implementation-details.md) - Rare exceptions
3. [Performance Testing](patterns/performance-testing.md) - Benchmarking
4. [Architecture Alignment](integration/architecture-alignment.md) - DDD/Clean Architecture

---

## 🚀 Integration with Other Skills

### With architecture-patterns Skill
- **Domain Models** → Test business rules (black box)
- **Aggregates** → Test invariants
- **Use Cases** → Test orchestration with mocks
- **Repositories** → Test with in-memory implementations

### With typescript-coder Agent
- Automatically references this skill for test generation
- Applies F.I.R.S.T principles
- Uses AAA structure
- Follows black box strategy

---

## 📊 Statistics

**Files Created:** 20+
**Coverage:**
- ✅ Core principles (F.I.R.S.T, AAA, BDD)
- ✅ Testing strategies (black box, implementation details)
- ✅ Practical patterns (mocks, async, errors, components, APIs, performance, test data)
- ✅ Refactoring guidance (testability patterns)
- ✅ Quick references (cheatsheet, migration guide)

**Integration:**
- ✅ typescript-coder agent updated
- ✅ Cross-references to architecture-patterns
- ✅ Decision trees for quick pattern selection

---

## 💡 Usage Examples for Agents

### Example 1: Agent Writing a Test

```typescript
// Agent receives: "Write a test for the UserService.register function"

// Step 1: Check decision tree (index.md)
// → New feature → Unit test (Black Box)

// Step 2: Apply F.I.R.S.T (first-principles.md)
// → Fast: Mock database
// → Isolated: Fresh mocks in beforeEach
// → Repeatable: Control time
// → Self-Checking: Use expect()
// → Timely: Write now

// Step 3: Use AAA pattern (aaa-pattern.md)
describe('UserService.register', () => {
  it('creates user and sends welcome email', async () => {
    // ARRANGE
    const mockDb = { users: { create: vi.fn().mockResolvedValue({...}) } }
    const mockEmailer = { sendWelcome: vi.fn() }
    const service = new UserService(mockDb, mockEmailer)

    // ACT
    const user = await service.register({ email: 'test@example.com' })

    // ASSERT
    expect(mockDb.users.create).toHaveBeenCalled()
    expect(mockEmailer.sendWelcome).toHaveBeenCalledWith('test@example.com')
  })
})

// Step 4: Add error scenarios (error-testing.md)
it('throws ValidationError for invalid email', async () => {
  const service = new UserService(mockDb, mockEmailer)

  await expect(service.register({ email: 'invalid' }))
    .rejects.toThrow(ValidationError)
})
```

### Example 2: Agent Refactoring Code

```typescript
// Agent receives: "Make this code testable"

// Step 1: Identify issue (testability-patterns.md)
// → Mixed logic and side effects

// Step 2: Apply Pattern 1: Extract Pure Functions
// Before:
class OrderService {
  async processOrder(order) {
    let total = 0
    for (const item of order.items) {
      total += item.price * item.quantity
    }
    await this.db.save({ ...order, total })
  }
}

// After:
export function calculateOrderTotal(order) {
  return order.items.reduce((sum, item) => sum + item.price * item.quantity, 0)
}

class OrderService {
  async processOrder(order) {
    const total = calculateOrderTotal(order)
    await this.db.save({ ...order, total })
  }
}

// Step 3: Write tests (black-box-testing.md)
describe('calculateOrderTotal', () => {
  it.each([
    [{ items: [{ price: 10, quantity: 2 }] }, 20],
    [{ items: [{ price: 15, quantity: 3 }] }, 45],
  ])('calculates %o as %d', (order, expected) => {
    expect(calculateOrderTotal(order)).toBe(expected)
  })
})
```

---

## 🔗 External Resources

- **[Vitest Documentation](https://vitest.dev/)** - Official docs
- **[Testing Library](https://testing-library.com/)** - React/DOM testing
- **[MSW](https://mswjs.io/)** - API mocking
- **[@faker-js/faker](https://fakerjs.dev/)** - Test data generation

---

## 📋 Agent Checklist

When generating tests, ensure:

- [ ] Test follows [F.I.R.S.T principles](principles/first-principles.md)
- [ ] Test uses [AAA structure](principles/aaa-pattern.md)
- [ ] Test uses [black box approach](strategies/black-box-testing.md)
- [ ] External dependencies are [mocked](patterns/test-doubles.md)
- [ ] [Error scenarios](patterns/error-testing.md) are covered
- [ ] [Async operations](patterns/async-testing.md) handled correctly
- [ ] Test is fast (< 100ms), isolated, and repeatable

---

## 🎯 Common Agent Tasks

### Task: Generate Unit Test
1. Read [index.md](index.md) → Identify test type
2. Apply [first-principles.md](principles/first-principles.md) → F.I.R.S.T
3. Structure with [aaa-pattern.md](principles/aaa-pattern.md)
4. Mock using [test-doubles.md](patterns/test-doubles.md)
5. Reference [cheatsheet.md](quick-reference/cheatsheet.md) for syntax

### Task: Generate Component Test
1. Read [component-testing.md](patterns/component-testing.md)
2. Use Testing Library queries
3. Test user interactions
4. Handle [async operations](patterns/async-testing.md)
5. Cover [error states](patterns/error-testing.md)

### Task: Refactor for Testability
1. Read [testability-patterns.md](refactoring/testability-patterns.md)
2. Identify pattern (extract, inject, wrap)
3. Apply refactoring
4. Generate tests for refactored code

### Task: Review Test Quality
1. Check [F.I.R.S.T compliance](principles/first-principles.md)
2. Verify [AAA structure](principles/aaa-pattern.md)
3. Ensure [black box approach](strategies/black-box-testing.md)
4. Validate [mock usage](patterns/test-doubles.md)
5. Check [error coverage](patterns/error-testing.md)

---

## 📖 Skill Metadata

**Version:** 1.0.0
**Type:** Testing guidance
**Framework:** Vitest
**Language:** TypeScript/JavaScript
**Integration:** typescript-coder agent, architecture-patterns skill
**Status:** Production ready (core files complete)

**Files:** 20+ markdown documents
**Categories:** Principles (3), Strategies (2), Patterns (7), Refactoring (1), Quick Reference (2)

---

## 💡 Quick Decision Trees

### "What test should I write?"

```
Is it a new feature?
└─ YES → Unit test (black box) + [index.md](index.md#new-feature)

Is it a bug fix?
└─ YES → Regression test + [index.md](index.md#bug-fix)

Is it async code?
└─ YES → [async-testing.md](patterns/async-testing.md)

Is it a React component?
└─ YES → [component-testing.md](patterns/component-testing.md)

Is it an API client?
└─ YES → [api-testing.md](patterns/api-testing.md)

Is it complex logic?
└─ YES → Extract pure function + black box test
```

### "How do I make this testable?"

```
Mixed logic and side effects?
└─ [testability-patterns.md](refactoring/testability-patterns.md#pattern-1)

Hard-coded dependencies?
└─ [testability-patterns.md](refactoring/testability-patterns.md#pattern-2)

Complex private method?
└─ [testability-patterns.md](refactoring/testability-patterns.md#pattern-3)

Time-dependent code?
└─ [testability-patterns.md](refactoring/testability-patterns.md#pattern-5)
```

---

**This is the master reference for AI agents. For human-friendly navigation, see [README.md](README.md).**
