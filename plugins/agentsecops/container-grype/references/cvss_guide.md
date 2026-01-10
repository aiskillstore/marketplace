# CVSS Severity Rating Guide

Common Vulnerability Scoring System (CVSS) is a standardized framework for rating vulnerability severity.

## Table of Contents
- [CVSS Score Ranges](#cvss-score-ranges)
- [Severity Ratings](#severity-ratings)
- [CVSS Metrics](#cvss-metrics)
- [Interpreting Scores](#interpreting-scores)
- [Remediation SLAs](#remediation-slas)

## CVSS Score Ranges

| CVSS Score | Severity Rating | Description |
|------------|----------------|-------------|
| 0.0 | None | No vulnerability |
| 0.1 - 3.9 | Low | Minimal security impact |
| 4.0 - 6.9 | Medium | Moderate security impact |
| 7.0 - 8.9 | High | Significant security impact |
| 9.0 - 10.0 | Critical | Severe security impact |

## Severity Ratings

### Critical (9.0 - 10.0)

**Characteristics**:
- Trivial to exploit
- No user interaction required
- Remote code execution or complete system compromise
- Affects default configurations

**Examples**:
- Unauthenticated remote code execution
- Critical SQL injection allowing full database access
- Authentication bypass in critical services

**Action**: Remediate immediately (within 24-48 hours)

### High (7.0 - 8.9)

**Characteristics**:
- Easy to exploit with moderate skill
- May require user interaction or specific conditions
- Significant data exposure or privilege escalation
- Affects common configurations

**Examples**:
- Authenticated remote code execution
- Cross-site scripting (XSS) in privileged contexts
- Privilege escalation vulnerabilities

**Action**: Remediate within 7 days

### Medium (4.0 - 6.9)

**Characteristics**:
- Requires specific conditions or elevated privileges
- Limited impact or scope
- May require local access or user interaction

**Examples**:
- Information disclosure of non-sensitive data
- Denial of service with mitigating factors
- Cross-site request forgery (CSRF)

**Action**: Remediate within 30 days

### Low (0.1 - 3.9)

**Characteristics**:
- Difficult to exploit
- Minimal security impact
- Requires significant user interaction or unlikely conditions

**Examples**:
- Information leakage of minimal data
- Low-impact denial of service
- Security misconfigurations with limited exposure

**Action**: Remediate within 90 days or next maintenance cycle

## CVSS Metrics

CVSS v3.1 scores are calculated from three metric groups:

### Base Metrics (Primary Factors)

**Attack Vector (AV)**:
- Network (N): Remotely exploitable
- Adjacent (A): Requires local network access
- Local (L): Requires local system access
- Physical (P): Requires physical access

**Attack Complexity (AC)**:
- Low (L): No specialized conditions required
- High (H): Requires specific conditions or expert knowledge

**Privileges Required (PR)**:
- None (N): No authentication needed
- Low (L): Basic user privileges required
- High (H): Administrator privileges required

**User Interaction (UI)**:
- None (N): No user interaction required
- Required (R): Requires user action (e.g., clicking a link)

**Scope (S)**:
- Unchanged (U): Vulnerability affects only the vulnerable component
- Changed (C): Vulnerability affects resources beyond the vulnerable component

**Impact Metrics** (Confidentiality, Integrity, Availability):
- None (N): No impact
- Low (L): Limited impact
- High (H): Total or serious impact

### Temporal Metrics (Optional)

Time-dependent factors:
- Exploit Code Maturity
- Remediation Level
- Report Confidence

### Environmental Metrics (Optional)

Organization-specific factors:
- Modified Base Metrics
- Confidentiality/Integrity/Availability Requirements

## Interpreting Scores

### Context Matters

CVSS scores should be interpreted in context:

**High-Value Systems**: Escalate severity for:
- Production systems
- Customer-facing applications
- Systems handling PII or financial data
- Critical infrastructure

**Low-Value Systems**: May de-prioritize for:
- Development/test environments
- Internal tools with limited access
- Deprecated systems scheduled for decommission

### Complementary Metrics

Consider alongside CVSS:

**EPSS (Exploit Prediction Scoring System)**:
- Probability (0-100%) that a vulnerability will be exploited in the wild
- High EPSS + High CVSS = Urgent remediation

**CISA KEV (Known Exploited Vulnerabilities)**:
- Active exploitation confirmed in the wild
- KEV presence overrides CVSS - remediate immediately

**Reachability**:
- Is the vulnerable code path actually executed?
- Is the vulnerable dependency directly or transitively included?

## Remediation SLAs

### Industry Standard SLA Examples

| Severity | Timeframe | Priority |
|----------|-----------|----------|
| Critical | 24-48 hours | P0 - Drop everything |
| High | 7 days | P1 - Next sprint |
| Medium | 30 days | P2 - Planned work |
| Low | 90 days | P3 - Maintenance cycle |

### Adjusted for Exploitability

**If CISA KEV or EPSS > 50%**:
- Reduce timeframe by 50%
- Example: High (7 days) → 3-4 days

**If proof-of-concept exists**:
- Treat High as Critical
- Treat Medium as High

**If actively exploited**:
- All severities become Critical (immediate remediation)

## False Positives and Suppressions

Not all reported vulnerabilities require immediate action:

### Valid Suppression Reasons

- **Not Reachable**: Vulnerable code path not executed
- **Mitigated**: Compensating controls in place (WAF, network segmentation)
- **Not Affected**: Version mismatch or platform-specific vulnerability
- **Risk Accepted**: Business decision with documented justification

### Documentation Requirements

For all suppressions:
1. CVE ID and affected package
2. Detailed justification
3. Approver and approval date
4. Review/expiration date (quarterly recommended)
5. Compensating controls if applicable

## References

- [CVSS v3.1 Specification](https://www.first.org/cvss/specification-document)
- [CVSS Calculator](https://www.first.org/cvss/calculator/3.1)
- [NVD CVSS Severity Distribution](https://nvd.nist.gov/vuln/severity-distribution)
