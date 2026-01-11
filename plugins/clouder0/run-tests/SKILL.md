---
name: run-tests
description: How to run tests in this project. Load when implementing or verifying code.
allowed-tools: Bash
---

# Run Tests Skill

Project-specific test execution.

## Test Commands

```bash
# Run all tests
# TODO: Add your test command
npm test
# pytest
# go test ./...
# cargo test

# Run specific file
# TODO: Add your pattern
npm test -- --testPathPattern={file}
# pytest {file} -v

# Run affected tests
npm test -- --changedSince=HEAD
```

## Test Patterns

- Test files: `**/*.test.ts` or `**/__tests__/*.ts`
- Test naming: `describe('Component', () => { it('should...') })`

## Coverage

```bash
# Run with coverage
npm test -- --coverage
```

## Debugging Failed Tests

1. Read the error message
2. Check the test file
3. Check the source file
4. Run single test in isolation
