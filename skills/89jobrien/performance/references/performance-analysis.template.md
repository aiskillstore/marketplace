---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: performance
---

# Performance Analysis Report

**Application:** {{APPLICATION_NAME}}
**Date:** {{YYYY-MM-DD}}
**Environment:** {{PRODUCTION|STAGING|DEV}}
**Analyst:** {{NAME}}

---

## Executive Summary

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **P50 Latency** | {{MS}}ms | {{MS}}ms | {{PASS/FAIL}} |
| **P95 Latency** | {{MS}}ms | {{MS}}ms | {{PASS/FAIL}} |
| **P99 Latency** | {{MS}}ms | {{MS}}ms | {{PASS/FAIL}} |
| **Throughput** | {{N}} req/s | {{N}} req/s | {{PASS/FAIL}} |
| **Error Rate** | {{N}}% | <{{N}}% | {{PASS/FAIL}} |

### Key Findings

1. {{FINDING_1}}
2. {{FINDING_2}}
3. {{FINDING_3}}

---

## Test Configuration

### Load Profile

| Phase | Duration | Users | RPS |
|-------|----------|-------|-----|
| Ramp-up | {{TIME}} | {{N}} | {{N}} |
| Steady State | {{TIME}} | {{N}} | {{N}} |
| Peak | {{TIME}} | {{N}} | {{N}} |
| Ramp-down | {{TIME}} | {{N}} | {{N}} |

### Environment

| Component | Specification |
|-----------|---------------|
| CPU | {{SPEC}} |
| Memory | {{SPEC}} |
| Database | {{SPEC}} |
| Network | {{SPEC}} |

---

## Response Time Analysis

### By Endpoint

| Endpoint | P50 | P95 | P99 | Max | Status |
|----------|-----|-----|-----|-----|--------|
| `GET {{PATH}}` | {{MS}} | {{MS}} | {{MS}} | {{MS}} | {{OK/SLOW}} |
| `POST {{PATH}}` | {{MS}} | {{MS}} | {{MS}} | {{MS}} | {{OK/SLOW}} |
| `PUT {{PATH}}` | {{MS}} | {{MS}} | {{MS}} | {{MS}} | {{OK/SLOW}} |

### Response Time Distribution

```
P50:  ████████████████████ {{MS}}ms
P75:  ██████████████████████████ {{MS}}ms
P90:  ████████████████████████████████ {{MS}}ms
P95:  ██████████████████████████████████████ {{MS}}ms
P99:  ████████████████████████████████████████████████ {{MS}}ms
```

---

## Throughput Analysis

### Requests Per Second

| Scenario | Target | Actual | Variance |
|----------|--------|--------|----------|
| Normal Load | {{N}} | {{N}} | {{N}}% |
| Peak Load | {{N}} | {{N}} | {{N}}% |
| Stress Test | {{N}} | {{N}} | {{N}}% |

### Saturation Point

- **Max Sustainable RPS:** {{N}}
- **Breaking Point:** {{N}} RPS
- **Degradation Begins:** {{N}} RPS

---

## Resource Utilization

### CPU

| Component | Avg | Max | Status |
|-----------|-----|-----|--------|
| App Server | {{N}}% | {{N}}% | {{OK/HIGH}} |
| Database | {{N}}% | {{N}}% | {{OK/HIGH}} |
| Cache | {{N}}% | {{N}}% | {{OK/HIGH}} |

### Memory

| Component | Avg | Max | Limit | Status |
|-----------|-----|-----|-------|--------|
| App Server | {{N}}GB | {{N}}GB | {{N}}GB | {{OK/HIGH}} |
| Database | {{N}}GB | {{N}}GB | {{N}}GB | {{OK/HIGH}} |

### Network

| Metric | Value | Limit |
|--------|-------|-------|
| Bandwidth In | {{N}} Mbps | {{N}} Mbps |
| Bandwidth Out | {{N}} Mbps | {{N}} Mbps |
| Connections | {{N}} | {{N}} |

---

## Database Performance

### Query Analysis

| Query | Avg Time | Calls | Total Time | Index Used |
|-------|----------|-------|------------|------------|
| {{QUERY_DESC}} | {{MS}}ms | {{N}} | {{MS}}ms | {{Y/N}} |

### Slow Queries

```sql
{{SLOW_QUERY}}
```

**Execution Time:** {{MS}}ms
**Recommendation:** {{FIX}}

### Connection Pool

| Metric | Value | Max |
|--------|-------|-----|
| Active | {{N}} | {{N}} |
| Idle | {{N}} | {{N}} |
| Waiting | {{N}} | - |

---

## Bottlenecks Identified

### 1. {{BOTTLENECK_1}}

**Location:** {{COMPONENT}}
**Impact:** {{DESCRIPTION}}
**Evidence:**

```
{{METRICS_OR_LOGS}}
```

**Root Cause:** {{ANALYSIS}}
**Recommendation:** {{FIX}}

---

### 2. {{BOTTLENECK_2}}

**Location:** {{COMPONENT}}
**Impact:** {{DESCRIPTION}}
**Recommendation:** {{FIX}}

---

## Core Web Vitals (If Web App)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| LCP | {{S}}s | <2.5s | {{PASS/FAIL}} |
| FID | {{MS}}ms | <100ms | {{PASS/FAIL}} |
| CLS | {{SCORE}} | <0.1 | {{PASS/FAIL}} |
| TTFB | {{MS}}ms | <800ms | {{PASS/FAIL}} |

---

## Error Analysis

### Error Distribution

| Error Type | Count | Rate | Impact |
|------------|-------|------|--------|
| 5xx | {{N}} | {{N}}% | {{HIGH/MED/LOW}} |
| 4xx | {{N}} | {{N}}% | {{HIGH/MED/LOW}} |
| Timeout | {{N}} | {{N}}% | {{HIGH/MED/LOW}} |

### Error Patterns

- {{ERROR_PATTERN_1}}
- {{ERROR_PATTERN_2}}

---

## Recommendations

### Immediate Impact (Quick Wins)

| Action | Expected Improvement | Effort |
|--------|---------------------|--------|
| {{ACTION_1}} | {{METRIC}} improvement | {{LOW}} |
| {{ACTION_2}} | {{METRIC}} improvement | {{LOW}} |

### Medium-term Optimizations

| Action | Expected Improvement | Effort |
|--------|---------------------|--------|
| {{ACTION_1}} | {{METRIC}} improvement | {{MED}} |
| {{ACTION_2}} | {{METRIC}} improvement | {{MED}} |

### Long-term Architecture Changes

| Action | Expected Improvement | Effort |
|--------|---------------------|--------|
| {{ACTION_1}} | {{METRIC}} improvement | {{HIGH}} |

---

## Comparison to Baseline

| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| P95 Latency | {{MS}}ms | {{MS}}ms | {{+/-N}}% |
| Throughput | {{N}} rps | {{N}} rps | {{+/-N}}% |
| Error Rate | {{N}}% | {{N}}% | {{+/-N}}% |

---

## Appendix

### A. Test Scripts

```{{LANGUAGE}}
{{LOAD_TEST_SCRIPT}}
```

### B. Raw Metrics

<details>
<summary>Full Metrics Export</summary>

```json
{{METRICS_JSON}}
```

</details>

---

## Quality Checklist

- [ ] Baseline established
- [ ] Multiple load scenarios tested
- [ ] Resource utilization monitored
- [ ] Bottlenecks identified
- [ ] Root causes analyzed
- [ ] Recommendations prioritized
- [ ] Comparison to targets documented
