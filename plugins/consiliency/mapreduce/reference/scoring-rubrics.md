# Scoring Rubrics Reference

> Standardized criteria for evaluating and comparing outputs in MapReduce workflows

## Overview

This document defines the scoring rubrics used by reducer agents to evaluate
and compare outputs from parallel workers. Each use case (planning, code,
debugging) has its own rubric optimized for that domain.

## Plan Rubric

Used by: `plan-reducer`

### Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Completeness | 25% | Covers all requirements and edge cases |
| Feasibility | 25% | Realistic given constraints and resources |
| Risk Management | 20% | Identifies risks with mitigations |
| Clarity | 15% | Easy to understand and follow |
| Innovation | 15% | Leverages modern approaches appropriately |

### Scoring Guide

#### Completeness (25%)

| Score | Description |
|-------|-------------|
| 5 | All requirements addressed; edge cases covered; nothing missing |
| 4 | Core requirements complete; minor gaps in edge cases |
| 3 | Most requirements addressed; some notable gaps |
| 2 | Significant requirements missing |
| 1 | Incomplete; major requirements absent |

#### Feasibility (25%)

| Score | Description |
|-------|-------------|
| 5 | All approaches proven; resources available; timeline realistic |
| 4 | Mostly proven; minor unknowns; timeline achievable |
| 3 | Some unproven elements; timeline tight but possible |
| 2 | Significant unknowns; timeline optimistic |
| 1 | Unrealistic; major technical or resource gaps |

#### Risk Management (20%)

| Score | Description |
|-------|-------------|
| 5 | Comprehensive risk matrix; all mitigations planned; rollback ready |
| 4 | Major risks identified; mitigations in place |
| 3 | Some risks noted; mitigations partial |
| 2 | Risks acknowledged but not addressed |
| 1 | No risk consideration |

#### Clarity (15%)

| Score | Description |
|-------|-------------|
| 5 | Crystal clear; easy to follow; well-structured |
| 4 | Clear with minor ambiguities |
| 3 | Understandable with effort |
| 2 | Confusing structure or language |
| 1 | Incomprehensible |

#### Innovation (15%)

| Score | Description |
|-------|-------------|
| 5 | Modern patterns; clever optimizations; future-proof |
| 4 | Good use of current best practices |
| 3 | Standard approaches; nothing dated |
| 2 | Outdated patterns; missed opportunities |
| 1 | Legacy approaches; technical debt |

### Calculation

```
Total = (Completeness × 0.25) + (Feasibility × 0.25) +
        (Risk × 0.20) + (Clarity × 0.15) + (Innovation × 0.15)
```

---

## Code Rubric

Used by: `code-reducer`

### Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Correctness | 30% | Works correctly; tests pass |
| Readability | 20% | Easy to understand |
| Maintainability | 20% | Easy to modify and extend |
| Performance | 15% | Efficient resource usage |
| Security | 15% | No vulnerabilities |

### Scoring Guide

#### Correctness (30%)

| Score | Description |
|-------|-------------|
| 5 | All tests pass; handles all edge cases; robust |
| 4 | Tests pass; minor edge case gaps |
| 3 | Most tests pass; some failures |
| 2 | Significant test failures |
| 1 | Doesn't work |

#### Readability (20%)

| Score | Description |
|-------|-------------|
| 5 | Self-documenting; clear naming; obvious flow |
| 4 | Easy to follow with minimal comments |
| 3 | Understandable with some effort |
| 2 | Confusing structure or naming |
| 1 | Incomprehensible |

#### Maintainability (20%)

| Score | Description |
|-------|-------------|
| 5 | Modular; well-tested; easy to extend |
| 4 | Good structure; reasonable to modify |
| 3 | Workable; some coupling |
| 2 | Tight coupling; hard to change |
| 1 | Monolithic; fragile |

#### Performance (15%)

| Score | Description |
|-------|-------------|
| 5 | Optimal algorithm; efficient resources |
| 4 | Good performance; minor optimizations possible |
| 3 | Acceptable performance |
| 2 | Noticeable slowness |
| 1 | Unacceptably slow |

#### Security (15%)

| Score | Description |
|-------|-------------|
| 5 | No vulnerabilities; follows best practices |
| 4 | Minor issues; good practices overall |
| 3 | Some concerns; no critical issues |
| 2 | Significant vulnerabilities |
| 1 | Critical security flaws |

### Automated Inputs

The code reducer should gather these objective metrics:

```markdown
| Metric | Tool | Scoring Impact |
|--------|------|----------------|
| Type errors | tsc/mypy | Correctness -1 per error |
| Lint warnings | eslint/ruff | Readability -0.1 per warning |
| Complexity | eslint/radon | Maintainability penalty if >15 |
| Test pass rate | jest/pytest | Correctness = rate × 5 |
| Test coverage | istanbul/coverage.py | Maintainability bonus if >80% |
```

### Calculation

```
Total = (Correctness × 0.30) + (Readability × 0.20) +
        (Maintainability × 0.20) + (Performance × 0.15) + (Security × 0.15)
```

---

## Debug Rubric

Used by: `debug-reducer`

### Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Correctness | 40% | Fix works; bug resolved |
| Minimality | 20% | Smallest effective change |
| Safety | 20% | No side effects or regressions |
| Clarity | 10% | Fix is understandable |
| Root Cause | 10% | Addresses true root cause |

### Scoring Guide

#### Correctness (40%)

| Score | Description |
|-------|-------------|
| 5 | Bug fixed; all tests pass; verified |
| 4 | Bug fixed; minor unrelated failures |
| 3 | Bug partially fixed |
| 2 | Bug not fixed; no regressions |
| 1 | Fix introduces new bugs |

#### Minimality (20%)

| Score | Description |
|-------|-------------|
| 5 | Single-line or few-character fix |
| 4 | Few lines; focused change |
| 3 | Moderate change; contained |
| 2 | Large change |
| 1 | Sweeping changes; refactoring |

#### Safety (20%)

| Score | Description |
|-------|-------------|
| 5 | No side effects; defensive coding |
| 4 | Minimal side effects; documented |
| 3 | Some side effects; manageable |
| 2 | Significant side effects |
| 1 | Dangerous; could cause more bugs |

#### Clarity (10%)

| Score | Description |
|-------|-------------|
| 5 | Fix is self-explanatory |
| 4 | Easy to understand with context |
| 3 | Requires explanation |
| 2 | Confusing |
| 1 | Incomprehensible |

#### Root Cause (10%)

| Score | Description |
|-------|-------------|
| 5 | Fixes true root cause |
| 4 | Fixes proximate cause; prevents recurrence |
| 3 | Works but unclear why |
| 2 | Symptom suppression |
| 1 | Coincidentally works |

### Verification Requirements

Debug fixes MUST be verified before scoring:

```markdown
## Verification Checklist

- [ ] Bug can be reproduced before fix
- [ ] Bug is resolved after fix
- [ ] All existing tests pass
- [ ] Regression test added
- [ ] No new lint/type errors
```

### Calculation

```
Total = (Correctness × 0.40) + (Minimality × 0.20) +
        (Safety × 0.20) + (Clarity × 0.10) + (RootCause × 0.10)
```

---

## Confidence Levels

Assign confidence to consolidated outputs based on source agreement:

| Level | Criteria | Interpretation |
|-------|----------|----------------|
| **HIGH** | 3+ sources agree | Strong consensus; high reliability |
| **MEDIUM** | 2 sources agree | Moderate consensus; review recommended |
| **LOW** | Single source only | No validation; careful review required |
| **CONFLICTING** | Sources disagree | Manual review required; document resolution |

## Tie-Breaking

When scores are equal:

### Plans
1. Prefer more feasible
2. Prefer clearer
3. Prefer more complete

### Code
1. Prefer more correct
2. Prefer more maintainable
3. Prefer simpler

### Debug
1. Prefer verified fix
2. Prefer minimal fix
3. Prefer clearer fix

## Weighting Adjustments

Context may require adjusting weights:

```markdown
## Context-Specific Overrides

| Context | Adjustment |
|---------|------------|
| Security-critical code | Security weight → 30% |
| Prototype/MVP | Innovation weight → 25% |
| Legacy system | Maintainability weight → 30% |
| Performance-critical | Performance weight → 25% |
| Compliance-required | Completeness weight → 35% |
```

Apply overrides by specifying in reducer prompt:

```markdown
Task(subagent_type="code-reducer", prompt="""
  ...
  Weight adjustments:
    Security: 30% (auth-related code)
    Performance: 10% (not performance-critical)
""")
```
