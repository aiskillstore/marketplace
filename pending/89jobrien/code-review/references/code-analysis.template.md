---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: code-review
---

# Code Analysis Report Template

**Generated:** {{TIMESTAMP}}
**Target:** {{FILE_OR_DIRECTORY}}
**Analyzer:** {{TOOL_OR_METHOD}}

---

## Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| **Overall Grade** | {{A-F}} | {{PASS/WARN/FAIL}} |
| **Files Analyzed** | {{COUNT}} | - |
| **Issues Found** | {{TOTAL}} | - |
| **Critical Issues** | {{COUNT}} | {{STATUS}} |
| **Test Coverage** | {{PERCENT}}% | {{STATUS}} |

---

## Findings Summary

| Severity | Count | Categories |
|----------|-------|------------|
| 🔴 Critical | {{N}} | {{CATEGORIES}} |
| 🟠 High | {{N}} | {{CATEGORIES}} |
| 🟡 Medium | {{N}} | {{CATEGORIES}} |
| 🟢 Low | {{N}} | {{CATEGORIES}} |

---

## Critical Issues

### {{ISSUE_ID}}: {{ISSUE_TITLE}}

**File:** `{{FILE_PATH}}:{{LINE_NUMBER}}`
**Category:** {{SECURITY/PERFORMANCE/BUG/STYLE}}

```{{LANGUAGE}}
{{CODE_SNIPPET}}
```

**Problem:** {{DESCRIPTION}}

**Impact:** {{IMPACT_DESCRIPTION}}

**Recommendation:**

```{{LANGUAGE}}
{{FIXED_CODE}}
```

---

## Architecture Analysis

### Dependencies

```
{{DEPENDENCY_TREE_OR_DIAGRAM}}
```

### Complexity Metrics

| File | Cyclomatic | Cognitive | Lines | Status |
|------|------------|-----------|-------|--------|
| {{FILE}} | {{N}} | {{N}} | {{N}} | {{STATUS}} |

### Code Smells

| Smell | Occurrences | Files Affected |
|-------|-------------|----------------|
| Long Method | {{N}} | {{FILES}} |
| Large Class | {{N}} | {{FILES}} |
| Duplicate Code | {{N}} | {{FILES}} |
| Dead Code | {{N}} | {{FILES}} |

---

## Security Analysis

### Vulnerabilities

| ID | Severity | Type | Location |
|----|----------|------|----------|
| {{CVE/CWE}} | {{SEV}} | {{TYPE}} | {{FILE:LINE}} |

### Dependency Audit

| Package | Current | Latest | Vulnerabilities |
|---------|---------|--------|-----------------|
| {{PKG}} | {{VER}} | {{VER}} | {{COUNT}} |

### Secrets Detection

| Type | File | Status |
|------|------|--------|
| API Key | {{FILE}} | {{EXPOSED/SAFE}} |

---

## Performance Analysis

### Hot Spots

| File | Function | Time % | Calls |
|------|----------|--------|-------|
| {{FILE}} | {{FUNC}} | {{N}}% | {{N}} |

### Memory Usage

| Component | Allocated | Retained | Status |
|-----------|-----------|----------|--------|
| {{COMP}} | {{SIZE}} | {{SIZE}} | {{STATUS}} |

### Database Queries

| Query | Avg Time | N+1 Risk | Index Used |
|-------|----------|----------|------------|
| {{QUERY}} | {{MS}}ms | {{Y/N}} | {{Y/N}} |

---

## Test Coverage

### Coverage by Module

| Module | Lines | Branches | Functions |
|--------|-------|----------|-----------|
| {{MOD}} | {{N}}% | {{N}}% | {{N}}% |

### Untested Code

| File | Lines Missing | Critical |
|------|---------------|----------|
| {{FILE}} | {{LINES}} | {{Y/N}} |

---

## Recommendations

### Immediate Actions (Critical/High)

1. **{{ACTION_1}}**
   - File: `{{FILE}}`
   - Effort: {{LOW/MED/HIGH}}
   - Impact: {{DESCRIPTION}}

### Short-term Improvements

1. {{IMPROVEMENT_1}}
2. {{IMPROVEMENT_2}}

### Technical Debt

| Item | Priority | Effort | Value |
|------|----------|--------|-------|
| {{ITEM}} | {{P1-4}} | {{EST}} | {{HIGH/MED/LOW}} |

---

## Appendix

### A. Full Issue List

<details>
<summary>Click to expand ({{N}} issues)</summary>

{{FULL_ISSUE_LIST}}

</details>

### B. Tool Configuration

```json
{{TOOL_CONFIG}}
```

### C. Analysis Commands

```bash
{{COMMANDS_USED}}
```

---

## Quality Checklist

- [ ] All critical issues have recommendations
- [ ] Security vulnerabilities documented
- [ ] Performance bottlenecks identified
- [ ] Test coverage gaps highlighted
- [ ] Technical debt quantified
- [ ] Recommendations prioritized by impact
