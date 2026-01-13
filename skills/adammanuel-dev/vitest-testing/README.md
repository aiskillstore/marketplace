# Vitest Testing Skill

**AI-friendly testing guidance for Vitest with focus on practical patterns, testability, and behavior-driven development.**

> **📋 Note:** This skill is currently in development (40% complete). See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for complete context on progress and how to resume development.

## 🎯 Quick Start

### I need to...
- **Write a test for a new feature** → Start with [Decision Tree](index.md)
- **Make code more testable** → See [Testability Patterns](refactoring/testability-patterns.md)
- **Understand testing principles** → Read [F.I.R.S.T Principles](principles/first-principles.md)
- **Find quick syntax** → Check [Cheatsheet](quick-reference/cheatsheet.md)
- **See a complete example** → Explore [Authentication Example](examples/authentication/)

## 📚 Skill Organization

### Core Principles
Testing fundamentals that guide all decisions:
- **[F.I.R.S.T Principles](principles/first-principles.md)** - Fast, Isolated, Repeatable, Self-Checking, Timely
- **[AAA Pattern](principles/aaa-pattern.md)** - Arrange-Act-Assert structure
- **[BDD Integration](principles/bdd-integration.md)** - Given/When/Then with AAA
- **[Testing Pyramid](principles/testing-pyramid.md)** - Unit/Integration/E2E strategy

### Testing Strategies
Approaches for different testing scenarios:
- **[Black Box Testing](strategies/black-box-testing.md)** - Testing behavior via public APIs
- **[White Box Testing](strategies/white-box-testing.md)** - When to test implementation details
- **[Implementation Details](strategies/implementation-details.md)** - Guidelines for testing internals
- **[Coverage Strategies](strategies/coverage-strategies.md)** - Meaningful coverage patterns

### Practical Patterns
Ready-to-use patterns for common scenarios:
- **[Test Doubles](patterns/test-doubles.md)** - Mocks, stubs, spies, fakes
- **[Async Testing](patterns/async-testing.md)** - Testing promises and async/await
- **[Error Testing](patterns/error-testing.md)** - Exception and error scenarios
- **[Component Testing](patterns/component-testing.md)** - React/Vue component patterns
- **[API Testing](patterns/api-testing.md)** - HTTP/API client testing

### Refactoring for Testability
Transform hard-to-test code into testable code:
- **[Testability Patterns](refactoring/testability-patterns.md)** - Making code testable
- **[Dependency Injection](refactoring/dependency-injection.md)** - DI patterns for testing
- **[Pure Functions](refactoring/pure-functions.md)** - Extracting pure logic
- **[Side Effect Isolation](refactoring/side-effect-isolation.md)** - Isolating side effects

### Complete Examples
Full implementations with tests:
- **[Authentication](examples/authentication/)** - Login, logout, token refresh
- **[CRUD Operations](examples/crud-operations/)** - Create, read, update, delete
- **[State Management](examples/state-management/)** - Redux/Zustand testing
- **[API Integration](examples/api-integration/)** - API client with error handling

### Quick Reference
Fast lookups and decision aids:
- **[Decision Tree](quick-reference/decision-tree.md)** - Visual decision flow
- **[Cheatsheet](quick-reference/cheatsheet.md)** - Matchers, setup, mocking
- **[Matchers Reference](quick-reference/matchers-reference.md)** - Complete matcher guide
- **[Setup Patterns](quick-reference/setup-patterns.md)** - beforeEach, afterEach, fixtures

### Agent Integration
How this skill integrates with Claude Code agents:
- **[TypeScript Coder Hooks](integration/typescript-coder-hooks.md)** - TS coder integration
- **[Architecture Alignment](integration/architecture-alignment.md)** - DDD/Clean Architecture
- **[Workflow Patterns](integration/workflow-patterns.md)** - Development workflows

## 🚀 Common Workflows

### New Feature Development
```
1. Check Decision Tree → What type of test?
2. Apply F.I.R.S.T Principles → Fast, isolated tests
3. Use AAA Pattern → Arrange, Act, Assert
4. Follow Black Box Strategy → Test public APIs
5. Reference Complete Example → Template for implementation
```

### Fixing Bugs
```
1. Write Failing Test → Reproduce the bug
2. Fix Implementation → Make test pass
3. Add Edge Cases → Prevent regression
4. Verify with Coverage → Ensure adequate coverage
```

### Refactoring
```
1. Ensure Tests Pass → Green before refactor
2. Extract Testable Units → Use refactoring patterns
3. Add Granular Tests → Test extracted units
4. Verify Behavior → All tests still pass
```

### Code Review
```
1. Check Test Coverage → Adequate coverage?
2. Review Test Quality → F.I.R.S.T principles?
3. Verify Black Box → Testing behavior not implementation?
4. Assess Maintainability → Clear, readable tests?
```

## 🎓 Learning Path

### Beginner
1. [F.I.R.S.T Principles](principles/first-principles.md)
2. [AAA Pattern](principles/aaa-pattern.md)
3. [Cheatsheet](quick-reference/cheatsheet.md)
4. [Authentication Example](examples/authentication/)

### Intermediate
1. [Black Box Testing](strategies/black-box-testing.md)
2. [Test Doubles](patterns/test-doubles.md)
3. [Async Testing](patterns/async-testing.md)
4. [Testability Patterns](refactoring/testability-patterns.md)

### Advanced
1. [Implementation Details](strategies/implementation-details.md)
2. [BDD Integration](principles/bdd-integration.md)
3. [Side Effect Isolation](refactoring/side-effect-isolation.md)
4. [Architecture Alignment](integration/architecture-alignment.md)

## 🔗 Related Skills

- **[@skills/architecture-patterns/](../architecture-patterns/)** - DDD, Clean Architecture, Hexagonal patterns
  - Tests should align with architectural boundaries
  - Domain models → Test business rules (black box)
  - Use cases → Test orchestration with mocks
  - Repositories → Test with in-memory implementations

## 💡 Philosophy

This skill follows these core beliefs:

**Behavior over Implementation**
- Tests should verify WHAT the code does, not HOW it does it
- Focus on observable outcomes and public contracts
- Implementation details should be testable indirectly

**Example-Driven Learning**
- Every principle includes practical examples
- Before/after refactoring shows the impact
- Complete examples provide working templates

**Integration with Workflow**
- Seamless integration with typescript-coder agent
- Decision trees reduce cognitive load
- Quick references support flow state

**Testability by Design**
- Code that's hard to test is poorly designed
- Refactoring patterns transform untestable code
- Testability improves overall code quality

---

**Start here:** [Decision Tree](index.md) - Find the right testing approach for your scenario
