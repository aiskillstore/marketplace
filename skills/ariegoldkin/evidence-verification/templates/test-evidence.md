# Test Evidence Template

Copy and fill in this template when documenting test execution evidence.

---

## Test Execution Evidence

### Basic Information

**Task/Feature:** [Brief description of what was tested]
**Agent:** [Agent name that ran the tests]
**Timestamp:** [YYYY-MM-DD HH:MM:SS]

### Test Command

```bash
[Exact command used to run tests]
# Example: npm test
# Example: pytest --cov
# Example: cargo test
# Example: go test ./...
```

### Test Results

**Exit Code:** [0 for success, non-zero for failure] ✅/❌

**Summary:**
- Tests Passed: [number]
- Tests Failed: [number]
- Tests Skipped: [number]
- Total Tests: [number]

**Duration:** [time in seconds or MM:SS format]

### Coverage (if available)

**Overall Coverage:** [percentage]%

**Detailed Coverage:**
- Statements: [percentage]%
- Branches: [percentage]%
- Functions: [percentage]%
- Lines: [percentage]%

### Test Output

```
[Paste first 10-20 lines of test output here]
[Include key information: which tests ran, any errors, summary]
```

### Environment

**Runtime:** [e.g., Node v20.5.0, Python 3.11, Rust 1.75]
**OS:** [e.g., macOS 14.0, Ubuntu 22.04, Windows 11]
**Test Framework:** [e.g., Jest, Pytest, Cargo Test, Go Test]

### Issues Found (if any)

| Test Name | Error | Expected | Actual |
|-----------|-------|----------|--------|
| [test name] | [error message] | [expected value] | [actual value] |

### Evidence File

**Location:** `.claude/quality-gates/evidence/tests-[timestamp].log`

### Conclusion

[✅ All tests passed / ❌ X tests failed - needs fixing]

---

## Example: Successful Test Run

### Basic Information

**Task/Feature:** User authentication login endpoint
**Agent:** Backend System Architect
**Timestamp:** 2025-11-02 14:25:33

### Test Command

```bash
npm test -- --coverage
```

### Test Results

**Exit Code:** 0 ✅

**Summary:**
- Tests Passed: 24
- Tests Failed: 0
- Tests Skipped: 1
- Total Tests: 25

**Duration:** 12.4 seconds

### Coverage

**Overall Coverage:** 87.5%

**Detailed Coverage:**
- Statements: 88.2%
- Branches: 82.4%
- Functions: 91.7%
- Lines: 87.9%

### Test Output

```
PASS  src/auth/login.test.ts
  ✓ should login with valid credentials (42ms)
  ✓ should reject invalid password (38ms)
  ✓ should reject non-existent user (35ms)
  ✓ should return JWT token on success (45ms)

PASS  src/auth/logout.test.ts
  ✓ should logout successfully (25ms)
  ✓ should clear session (28ms)

Test Suites: 5 passed, 5 total
Tests:       24 passed, 1 skipped, 25 total
Snapshots:   0 total
Time:        12.438 s
```

### Environment

**Runtime:** Node v20.5.0
**OS:** macOS 14.0
**Test Framework:** Jest 29.5.0

### Issues Found

None - all tests passed

### Evidence File

**Location:** `.claude/quality-gates/evidence/tests-2025-11-02-142533.log`

### Conclusion

✅ All tests passed. Coverage at 87.5%, exceeding 70% minimum. Authentication feature verified and ready for production.

---

## Example: Failed Test Run

### Basic Information

**Task/Feature:** User profile update endpoint
**Agent:** Backend System Architect
**Timestamp:** 2025-11-02 15:10:45

### Test Command

```bash
npm test
```

### Test Results

**Exit Code:** 1 ❌

**Summary:**
- Tests Passed: 18
- Tests Failed: 3
- Tests Skipped: 0
- Total Tests: 21

**Duration:** 8.7 seconds

### Coverage

**Overall Coverage:** 72.3%

**Detailed Coverage:**
- Statements: 73.1%
- Branches: 68.5%
- Functions: 77.2%
- Lines: 72.8%

### Test Output

```
FAIL  src/profile/update.test.ts
  ✓ should update user name (38ms)
  ✓ should update user email (42ms)
  ✕ should validate email format (51ms)
  ✕ should prevent duplicate email (48ms)
  ✓ should update profile picture (65ms)

  ● should validate email format

    expect(received).toBe(expected)

    Expected: 400
    Received: 200

Test Suites: 3 passed, 1 failed, 4 total
Tests:       18 passed, 3 failed, 21 total
```

### Environment

**Runtime:** Node v20.5.0
**OS:** macOS 14.0
**Test Framework:** Jest 29.5.0

### Issues Found

| Test Name | Error | Expected | Actual |
|-----------|-------|----------|--------|
| should validate email format | Invalid email accepted | 400 Bad Request | 200 OK |
| should prevent duplicate email | Duplicate email allowed | 400 Bad Request | 200 OK |
| should handle missing fields | Missing field accepted | 400 Bad Request | 200 OK |

### Evidence File

**Location:** `.claude/quality-gates/evidence/tests-2025-11-02-151045.log`

### Conclusion

❌ 3 tests failed. Email validation not working correctly. Need to:
1. Add email format validation in update endpoint
2. Check for duplicate emails before updating
3. Validate required fields are present

Task NOT complete. Fixing validation errors now.

---

## Quick Fill Template

Use this for quick evidence capture:

```
## Test Evidence

**Task:** [description]
**Command:** `[command]`
**Exit Code:** [0/non-zero] [✅/❌]
**Results:** [X passed, X failed, X skipped]
**Coverage:** [X]%
**Duration:** [X]s
**Timestamp:** [YYYY-MM-DD HH:MM:SS]

**Status:** [All passed ✅ / X failed ❌]
```
