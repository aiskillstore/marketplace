---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: security-audit
---

# Security Audit Report

**Target:** {{APPLICATION_OR_SYSTEM}}
**Date:** {{YYYY-MM-DD}}
**Auditor:** {{NAME}}
**Scope:** {{SCOPE_DESCRIPTION}}

---

## Executive Summary

| Severity | Count |
|----------|-------|
| Critical | {{N}} |
| High | {{N}} |
| Medium | {{N}} |
| Low | {{N}} |
| Info | {{N}} |

**Overall Risk Level:** {{CRITICAL|HIGH|MEDIUM|LOW}}

### Key Findings

1. {{CRITICAL_FINDING_SUMMARY}}
2. {{HIGH_FINDING_SUMMARY}}
3. {{NOTABLE_FINDING_SUMMARY}}

---

## Scope & Methodology

### In Scope

- {{COMPONENT_1}}
- {{COMPONENT_2}}
- {{ENDPOINT_RANGE}}

### Out of Scope

- {{EXCLUDED_1}}
- {{EXCLUDED_2}}

### Testing Methodology

| Type | Performed |
|------|-----------|
| Static Analysis | {{YES/NO}} |
| Dynamic Testing | {{YES/NO}} |
| Dependency Scan | {{YES/NO}} |
| Manual Review | {{YES/NO}} |
| Penetration Test | {{YES/NO}} |

### Tools Used

- {{TOOL_1}}: {{PURPOSE}}
- {{TOOL_2}}: {{PURPOSE}}

---

## Findings

### CRITICAL: {{FINDING_TITLE}}

**ID:** {{VULN-001}}
**CVSS:** {{SCORE}} ({{VECTOR}})
**CWE:** {{CWE-XXX}}
**Location:** `{{FILE_PATH}}:{{LINE}}`

**Description:**
{{DETAILED_DESCRIPTION}}

**Proof of Concept:**

```{{LANGUAGE}}
{{POC_CODE_OR_STEPS}}
```

**Impact:**
{{WHAT_AN_ATTACKER_COULD_DO}}

**Recommendation:**

```{{LANGUAGE}}
{{REMEDIATION_CODE}}
```

**References:**

- [{{REFERENCE}}]({{URL}})

---

### HIGH: {{FINDING_TITLE}}

**ID:** {{VULN-002}}
**CVSS:** {{SCORE}}
**CWE:** {{CWE-XXX}}
**Location:** `{{FILE_PATH}}`

**Description:**
{{DETAILED_DESCRIPTION}}

**Impact:**
{{IMPACT_DESCRIPTION}}

**Recommendation:**
{{REMEDIATION_STEPS}}

---

### MEDIUM: {{FINDING_TITLE}}

**ID:** {{VULN-003}}
**Location:** `{{FILE_PATH}}`

**Description:**
{{DESCRIPTION}}

**Recommendation:**
{{REMEDIATION}}

---

### LOW: {{FINDING_TITLE}}

**ID:** {{VULN-004}}

**Description:**
{{DESCRIPTION}}

**Recommendation:**
{{REMEDIATION}}

---

## OWASP Top 10 Coverage

| Category | Status | Findings |
|----------|--------|----------|
| A01: Broken Access Control | {{TESTED}} | {{N}} |
| A02: Cryptographic Failures | {{TESTED}} | {{N}} |
| A03: Injection | {{TESTED}} | {{N}} |
| A04: Insecure Design | {{TESTED}} | {{N}} |
| A05: Security Misconfiguration | {{TESTED}} | {{N}} |
| A06: Vulnerable Components | {{TESTED}} | {{N}} |
| A07: Auth Failures | {{TESTED}} | {{N}} |
| A08: Data Integrity Failures | {{TESTED}} | {{N}} |
| A09: Logging Failures | {{TESTED}} | {{N}} |
| A10: SSRF | {{TESTED}} | {{N}} |

---

## Dependency Audit

### Vulnerable Dependencies

| Package | Version | Vulnerability | Severity | Fix Version |
|---------|---------|---------------|----------|-------------|
| {{PKG}} | {{VER}} | {{CVE-XXXX}} | {{SEV}} | {{VER}} |

### Outdated Dependencies

| Package | Current | Latest | Risk |
|---------|---------|--------|------|
| {{PKG}} | {{VER}} | {{VER}} | {{RISK}} |

---

## Authentication & Authorization

| Control | Status | Notes |
|---------|--------|-------|
| Password Policy | {{PASS/FAIL}} | {{NOTES}} |
| Session Management | {{PASS/FAIL}} | {{NOTES}} |
| MFA Support | {{PASS/FAIL}} | {{NOTES}} |
| Role-Based Access | {{PASS/FAIL}} | {{NOTES}} |
| Token Security | {{PASS/FAIL}} | {{NOTES}} |

---

## Data Protection

| Control | Status | Notes |
|---------|--------|-------|
| Encryption at Rest | {{PASS/FAIL}} | {{NOTES}} |
| Encryption in Transit | {{PASS/FAIL}} | {{NOTES}} |
| PII Handling | {{PASS/FAIL}} | {{NOTES}} |
| Secrets Management | {{PASS/FAIL}} | {{NOTES}} |

---

## Infrastructure Security

| Control | Status | Notes |
|---------|--------|-------|
| Firewall Rules | {{PASS/FAIL}} | {{NOTES}} |
| Network Segmentation | {{PASS/FAIL}} | {{NOTES}} |
| Container Security | {{PASS/FAIL}} | {{NOTES}} |
| Cloud Config | {{PASS/FAIL}} | {{NOTES}} |

---

## Remediation Roadmap

### Immediate (24-48 hours)

1. [ ] {{CRITICAL_FIX_1}}
2. [ ] {{CRITICAL_FIX_2}}

### Short-term (1-2 weeks)

1. [ ] {{HIGH_FIX_1}}
2. [ ] {{HIGH_FIX_2}}

### Medium-term (1 month)

1. [ ] {{MEDIUM_FIX_1}}
2. [ ] {{MEDIUM_FIX_2}}

---

## Appendix

### A. Scan Outputs

<details>
<summary>Static Analysis Results</summary>

```
{{SCAN_OUTPUT}}
```

</details>

### B. Testing Evidence

| Test | Evidence |
|------|----------|
| {{TEST}} | {{SCREENSHOT_OR_LOG}} |

---

## Quality Checklist

- [ ] All in-scope components tested
- [ ] OWASP Top 10 covered
- [ ] Dependencies scanned
- [ ] Findings reproducible
- [ ] Remediation actionable
- [ ] Risk ratings justified
- [ ] Evidence documented
