# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Test Stability & Reliability (stable)

**Impact:** CRITICAL  
**Description:** Flaky tests are the #1 enemy of test automation. Unstable tests waste developer time, reduce confidence, and can mask real bugs. Eliminating flakiness yields the largest gains in test suite value.

## 2. Test Execution Speed (speed)

**Impact:** CRITICAL  
**Description:** Fast test execution enables rapid feedback loops and efficient CI/CD pipelines. Slow tests reduce developer productivity and increase costs.

## 3. Locator Best Practices (locator)

**Impact:** HIGH  
**Description:** Robust, resilient locators are the foundation of maintainable tests. Good locator strategies ensure tests survive UI refactoring and changes.

## 4. Assertions & Waiting (assertion)

**Impact:** HIGH  
**Description:** Proper assertions with automatic waiting ensure tests validate the correct behavior without race conditions or false positives.

## 5. Parallel Execution (parallel)

**Impact:** MEDIUM-HIGH  
**Description:** Efficient parallel test execution dramatically reduces total test suite runtime. Proper isolation and resource management are essential.

## 6. Fixtures & Test Organization (fixture)

**Impact:** MEDIUM  
**Description:** Well-structured tests with proper fixtures and hooks improve code reusability, maintainability, and test clarity.

## 7. Debugging & Maintenance (debug)

**Impact:** MEDIUM  
**Description:** Effective debugging practices and maintainable test code reduce the time spent investigating failures and updating tests.

## 8. Advanced Patterns (advanced)

**Impact:** LOW  
**Description:** Advanced patterns for specific use cases such as visual testing, API interception, custom matchers, and performance testing.