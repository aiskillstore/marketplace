---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: testing
---

# Pytest Test Quality Report

**Generated:** {{TIMESTAMP}}
**Project:** {{PROJECT_PATH}}
**Branch:** {{GIT_BRANCH}}
**Python:** {{PYTHON_VERSION}} | **Pytest:** {{PYTEST_VERSION}}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Status** | {{STATUS}} |
| **Total Tests** | {{TOTAL_TESTS}} |
| **Pass Rate** | {{PASS_RATE}}% |
| **Coverage** | {{COVERAGE_PERCENT}}% |
| **Issues Found** | {{TOTAL_ISSUES}} |

---

## Test Execution Summary

**Command Executed:**

```bash
{{PYTEST_COMMAND}}
```

| Result | Count |
|--------|-------|
| Passed | {{PASSED_COUNT}} |
| Failed | {{FAILED_COUNT}} |
| Skipped | {{SKIPPED_COUNT}} |
| Errors | {{ERROR_COUNT}} |
| **Total** | **{{TOTAL_TESTS}}** |

**Duration:** {{DURATION}}

### Test Output

<details>
<summary>Click to expand full pytest output</summary>

```
{{PYTEST_OUTPUT}}
```

</details>

---

## Coverage Summary

**Overall Coverage:** {{COVERAGE_PERCENT}}%
**Threshold:** {{COVERAGE_THRESHOLD}}%
**Status:** {{COVERAGE_STATUS}}

### Coverage by Module

| Module | Statements | Missing | Excluded | Coverage |
|--------|------------|---------|----------|----------|

{{COVERAGE_TABLE}}

### Files Below Threshold

{{FILES_BELOW_THRESHOLD}}

### Uncovered Critical Code

{{UNCOVERED_CRITICAL_CODE}}

---

## Audit Findings

**Total Issues:** {{TOTAL_ISSUES}} (Critical: {{CRITICAL_COUNT}}, High: {{HIGH_COUNT}}, Medium: {{MEDIUM_COUNT}}, Low: {{LOW_COUNT}})

### CRITICAL (Must Fix)

{{CRITICAL_ISSUES}}

### HIGH (Should Fix)

{{HIGH_ISSUES}}

### MEDIUM (Improvements)

{{MEDIUM_ISSUES}}

### LOW (Optional)

{{LOW_ISSUES}}

---

## Test File Inventory

| File | Tests | Passed | Failed | Skipped | Duration |
|------|-------|--------|--------|---------|----------|

{{TEST_FILE_TABLE}}

---

## Recommendations

### Immediate Actions (Critical/High)

{{IMMEDIATE_ACTIONS}}

### Short-term Improvements (Medium)

{{SHORT_TERM_ACTIONS}}

### Future Enhancements (Low)

{{FUTURE_ACTIONS}}

---

## Coverage Details

### Missing Coverage by File

{{MISSING_COVERAGE_DETAILS}}

### Suggested Tests to Add

{{SUGGESTED_TESTS}}

---

## Test Quality Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Coverage | {{COVERAGE_PERCENT}}% | {{COVERAGE_THRESHOLD}}% | {{COVERAGE_STATUS}} |
| Pass Rate | {{PASS_RATE}}% | 100% | {{PASS_RATE_STATUS}} |
| Avg Test Duration | {{AVG_TEST_DURATION}} | <1s | {{DURATION_STATUS}} |
| Tests with Assertions | {{TESTS_WITH_ASSERTIONS}} | 100% | {{ASSERTION_STATUS}} |
| Fixture Usage | {{FIXTURE_USAGE}} | - | - |
| Parametrized Tests | {{PARAMETRIZED_COUNT}} | - | - |

---

## Appendix

### A. Failed Test Details

{{FAILED_TEST_DETAILS}}

### B. Slow Tests (>1s)

{{SLOW_TESTS}}

### C. Coverage Report (Raw)

<details>
<summary>Click to expand coverage JSON</summary>

```json
{{COVERAGE_JSON}}
```

</details>

---

**Report Location:** {{REPORT_PATH}}
**Next Report:** Run `/tdd-pytest:report` to regenerate
