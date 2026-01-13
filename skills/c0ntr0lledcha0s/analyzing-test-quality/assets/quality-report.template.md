# Test Quality Analysis Report

**Project**: [Project Name]  
**Date**: [Date]  
**Analyzed by**: [Name/Tool]

---

## Executive Summary

**Overall Quality Score**: X/10

| Dimension | Score | Status |
|-----------|-------|--------|
| Structure | X/10 | ✅/⚠️/❌ |
| Coverage | X/10 | ✅/⚠️/❌ |
| Reliability | X/10 | ✅/⚠️/❌ |
| Maintainability | X/10 | ✅/⚠️/❌ |
| Performance | X/10 | ✅/⚠️/❌ |

---

## Metrics Overview

### Test Statistics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Tests | | | |
| Test Files | | | |
| Test/Code Ratio | | >0.8 | |
| Avg Test Duration | | <100ms | |
| Total Suite Time | | | |

### Coverage Metrics

| Type | Current | Target | Status |
|------|---------|--------|--------|
| Statements | X% | 80% | |
| Branches | X% | 75% | |
| Functions | X% | 80% | |
| Lines | X% | 80% | |

### Mutation Score (if applicable)

| Metric | Value |
|--------|-------|
| Mutation Score | X% |
| Killed Mutants | |
| Survived Mutants | |
| Timeout | |

---

## Critical Issues

### Issue 1: [Title]

**Severity**: Critical / High / Medium / Low  
**Location**: [file:line]  
**Type**: [Flaky Test / Missing Coverage / Anti-Pattern / etc.]

**Description**:
[Detailed description of the issue]

**Impact**:
[How this affects test reliability/maintainability]

**Recommendation**:
```typescript
// Before
[problematic code]

// After
[fixed code]
```

---

### Issue 2: [Title]

[Repeat format for each issue]

---

## Coverage Gaps

### Untested Areas

| File | Function/Method | Risk Level | Priority |
|------|-----------------|------------|----------|
| | | High/Medium/Low | P1/P2/P3 |

### Suggested Test Cases

#### 1. [Function/Component Name]

```typescript
// Suggested test
test('should [expected behavior]', () => {
  // Arrange
  
  // Act
  
  // Assert
});
```

---

## Anti-Patterns Detected

| Pattern | Count | Files Affected |
|---------|-------|----------------|
| Test Pollution | | |
| Over-Mocking | | |
| Flaky Assertions | | |
| Mystery Guest | | |
| Assertion Roulette | | |

---

## Recommendations

### High Priority (Do First)

1. **[Recommendation Title]**
   - Description: [What to do]
   - Files: [Affected files]
   - Effort: [Estimated time]

### Medium Priority

1. **[Recommendation Title]**
   - [Details]

### Low Priority (Nice to Have)

1. **[Recommendation Title]**
   - [Details]

---

## Test Pyramid Analysis

```
         /\
        /  \     E2E: X tests (X%)
       /____\
      /      \   Integration: X tests (X%)
     /________\
    /          \ Unit: X tests (X%)
   /____________\
```

**Assessment**: [Balanced / Top-Heavy / Bottom-Heavy]

**Recommendation**: [Add more unit tests / Reduce E2E tests / etc.]

---

## Trend Analysis (if historical data available)

| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Coverage | | | ↑/↓ X% |
| Test Count | | | ↑/↓ X |
| Flaky Tests | | | ↑/↓ X |
| Suite Duration | | | ↑/↓ Xs |

---

## Action Items

| # | Action | Owner | Due Date | Status |
|---|--------|-------|----------|--------|
| 1 | | | | ⬜ |
| 2 | | | | ⬜ |
| 3 | | | | ⬜ |

---

## Appendix

### Files Analyzed

```
[List of files included in analysis]
```

### Tools Used

- Coverage: [Jest/Istanbul/c8]
- Mutation: [Stryker]
- Static Analysis: [ESLint/etc.]

### Methodology

[Brief description of how analysis was performed]
