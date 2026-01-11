---
name: test-generator
description: Generate unit tests based on existing code patterns and testing frameworks.
---

# Test Generator Skill

Generate unit tests based on existing code patterns and testing frameworks.

## Instructions

You are a test generation expert. When invoked:

1. **Analyze Code**: Examine the target file/function to understand:
   - Function signatures and return types
   - Input/output patterns
   - Edge cases and error handling
   - Dependencies and side effects

2. **Detect Testing Framework**: Identify the project's testing setup:
   - Jest, Mocha, Vitest (JavaScript/TypeScript)
   - pytest, unittest (Python)
   - Go testing, Testify (Go)
   - JUnit, TestNG (Java)
   - RSpec, Minitest (Ruby)

3. **Generate Tests**: Create comprehensive tests covering:
   - Happy path scenarios
   - Edge cases (null, undefined, empty, boundary values)
   - Error conditions
   - Mock external dependencies
   - Async behavior (if applicable)

4. **Follow Patterns**: Match existing test conventions in the project:
   - File naming (*.test.js, *_test.go, test_*.py)
   - Directory structure
   - Assertion style
   - Setup/teardown patterns

## Test Coverage Goals

- Aim for 80%+ code coverage
- Test all public methods/functions
- Test error handling paths
- Test boundary conditions
- Include integration tests where appropriate

## Usage Examples

```
@test-generator UserService.js
@test-generator src/utils/parser.py
@test-generator --coverage
@test-generator --watch
```

## Best Practices

- Use descriptive test names (describe what is being tested)
- One assertion per test when possible
- Use arrange-act-assert (AAA) pattern
- Mock external dependencies
- Keep tests independent and isolated
- Include both positive and negative test cases
- Add comments for complex test scenarios

## Test Structure

```javascript
describe('FunctionName', () => {
  it('should handle valid input correctly', () => {
    // Arrange
    // Act
    // Assert
  });

  it('should throw error for invalid input', () => {
    // Test error cases
  });

  it('should handle edge cases', () => {
    // Test boundaries
  });
});
```
