---
name: test-coverage-analyzer
description: Analyzes test coverage gaps and suggests test cases for untested code paths. Use when user requests test improvements, coverage analysis, or wants to increase test coverage.
allowed-tools: Read, Grep, Glob, Bash, Write
---

# Test Coverage Analyzer

This skill helps identify gaps in test coverage and suggests specific test cases to improve code quality.

## When to Use This Skill

- User asks to analyze test coverage
- User wants to improve test coverage
- User requests suggestions for missing tests
- Working on increasing code coverage percentage
- User mentions "coverage gaps", "untested code", or "test suggestions"

## Instructions

### 1. Detect Testing Framework

Identify the testing framework(s) used in the project:

**JavaScript/TypeScript:**
- Jest: `jest` in package.json or `jest.config.js`
- Mocha: `mocha` in package.json or `.mocharc`
- Vitest: `vitest` in package.json or `vitest.config.js`
- Jasmine: `jasmine` in package.json

**Python:**
- pytest: `pytest` in requirements.txt or `pytest.ini`
- unittest: Standard library, check for test files
- coverage.py: `coverage` in requirements.txt

**Ruby:**
- RSpec: `rspec` in Gemfile
- Minitest: Standard library

**Go:**
- Built-in: `go test` (coverage via `go test -cover`)

**Java:**
- JUnit: Look for JUnit in pom.xml or build.gradle
- JaCoCo: Coverage tool configuration

Use Glob and Grep to find configuration files.

### 2. Locate Coverage Reports

Find existing coverage reports:

**Common locations:**
- `coverage/` directory
- `.nyc_output/` (NYC for Node.js)
- `htmlcov/` (coverage.py for Python)
- `target/site/jacoco/` (JaCoCo for Java)
- Coverage files: `lcov.info`, `coverage.json`, `.coverage`

**If no coverage report exists:**
- Guide user to run coverage: `npm test -- --coverage`, `pytest --cov`, etc.
- Wait for report generation before analyzing

### 3. Parse Coverage Data

Extract coverage information:

**From lcov.info:**
- Lines covered vs total
- Functions covered vs total
- Branches covered vs total
- Uncovered line numbers by file

**From coverage.json (Jest):**
- Statement coverage percentage
- Branch coverage percentage
- Function coverage percentage
- Line coverage percentage
- Uncovered lines per file

**From .coverage (Python):**
- Use `coverage report` or `coverage json`
- Missing line ranges
- Excluded lines

**From HTML reports:**
- Read summary statistics
- Identify files with low coverage

### 4. Identify Coverage Gaps

Prioritize files/functions that need testing:

**High priority:**
- Business logic with 0% coverage
- Public APIs and exported functions
- Error handling paths (catch blocks, error callbacks)
- Edge cases and boundary conditions
- Critical paths (authentication, payment, data validation)

**Medium priority:**
- Utility functions with partial coverage
- Private functions called by public APIs
- Configuration and initialization code

**Lower priority:**
- Simple getters/setters
- Type definitions
- Auto-generated code
- Third-party code

### 5. Analyze Untested Code Paths

For each file with coverage gaps:

1. **Read the source file** to understand the code structure
2. **Identify untested code**:
   - Uncovered lines and line ranges
   - Untested conditional branches (if/else)
   - Uncovered error handlers
   - Missing function coverage
3. **Categorize missing tests**:
   - Happy path tests
   - Error/exception tests
   - Edge case tests
   - Integration tests

### 6. Generate Test Suggestions

For each coverage gap, suggest specific test cases:

**Format:**
```
File: src/utils/validator.js (42% coverage)

Missing Coverage:
- Lines 15-18: Email validation error path
- Lines 23-25: Empty input handling
- Lines 30-35: Edge case for special characters

Suggested Tests:
1. Test email validation with invalid format (covers lines 15-18)
2. Test validator with empty string input (covers lines 23-25)
3. Test special character handling in names (covers lines 30-35)
```

**Test case details should include:**
- Test description
- Input data
- Expected output/behavior
- Lines/branches covered

### 7. Create Test Stubs (Optional)

If user wants, generate test file stubs:

- Use appropriate test framework syntax
- Include describe/test blocks with TODO comments
- Add example test structure
- Reference the template in `templates/test-template.js` (or appropriate extension)

**Example (Jest):**
```javascript
describe('Validator', () => {
  describe('validateEmail', () => {
    it('should reject invalid email format', () => {
      // TODO: Test email validation error path (lines 15-18)
      const result = validateEmail('invalid-email');
      expect(result.valid).toBe(false);
    });

    it('should handle empty string input', () => {
      // TODO: Test empty input handling (lines 23-25)
    });
  });
});
```

### 8. Calculate Coverage Metrics

Provide summary statistics:

- Overall coverage percentage
- Coverage by file/directory
- Functions/methods without tests
- Critical files with low coverage
- Coverage trend (if historical data available)

### 9. Prioritize Recommendations

Order suggestions by:

1. **Impact**: Critical business logic first
2. **Risk**: High-risk areas (security, data integrity)
3. **Complexity**: Complex logic needs more tests
4. **Ease**: Quick wins (simple tests for high coverage gain)

### 10. Output Format

Present findings in a clear, actionable format:

```
Coverage Analysis Summary
=========================

Overall Coverage: 67%
- Statements: 65%
- Branches: 58%
- Functions: 72%
- Lines: 67%

Files Needing Attention (sorted by priority):

1. src/payment/processor.js (23% coverage) - HIGH PRIORITY
   - Missing: Error handling for payment failures
   - Missing: Retry logic tests
   - Missing: Transaction validation

2. src/auth/validator.js (45% coverage) - MEDIUM PRIORITY
   - Missing: Invalid token handling
   - Missing: Expired session tests

Suggested Test Cases:
[Detailed suggestions for each file]
```

## Best Practices

1. **Focus on meaningful coverage**: 100% coverage isn't always necessary
2. **Test behavior, not implementation**: Suggest tests that verify functionality
3. **Prioritize critical paths**: Authentication, payments, data validation first
4. **Consider test types**: Unit, integration, and e2e where appropriate
5. **Check existing tests**: Don't suggest tests that already exist
6. **Realistic test data**: Use plausible inputs in examples
7. **Coverage thresholds**: Suggest minimum coverage targets (e.g., 80%)

## Running Coverage Reports

Provide commands based on detected framework:

**Jest:** `npm test -- --coverage` or `jest --coverage`
**Vitest:** `npm test -- --coverage` or `vitest run --coverage`
**Mocha + NYC:** `nyc mocha`
**pytest:** `pytest --cov=src --cov-report=html`
**Go:** `go test -cover ./...` or `go test -coverprofile=coverage.out`
**JUnit + JaCoCo:** `mvn test jacoco:report`

## Supporting Files

- `scripts/parse-coverage.sh`: Helper script to extract coverage data
- `templates/test-template.js`: Test file template for JavaScript
- `templates/test-template.py`: Test file template for Python
- `templates/test-template.go`: Test file template for Go
