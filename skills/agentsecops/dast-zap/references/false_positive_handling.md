# ZAP False Positive Handling Guide

Guide for identifying, verifying, and suppressing false positives in OWASP ZAP scan results.

## Overview

DAST tools like ZAP generate false positives - alerts for issues that aren't actually exploitable vulnerabilities. This guide helps you:

1. Identify common false positives
2. Verify findings manually
3. Suppress false positives in future scans
4. Tune scan policies

## Common False Positives

### 1. X-Content-Type-Options Missing

**Alert:** Missing X-Content-Type-Options header

**False Positive Scenario:**
- Static content served by CDNs
- Third-party resources
- Legacy browsers not supported

**Verification:**
```bash
curl -I https://example.com/static/script.js
# Check if browser performs MIME sniffing
```

**When to Suppress:**
- Static content only (CSS, JS, images)
- Content served from trusted CDN
- No user-controlled content in responses

**Suppression Rule:**
```tsv
10021	https://cdn.example.com/.*	.*	693	IGNORE
```

### 2. Cookie Without Secure Flag

**Alert:** Cookie without Secure flag set

**False Positive Scenario:**
- Development/testing environments (HTTP)
- Non-sensitive cookies (analytics, preferences)
- Localhost testing

**Verification:**
```bash
curl -I https://example.com
# Check Set-Cookie headers
# Verify if cookie contains sensitive data
```

**When to Suppress:**
- Non-sensitive cookies (theme preference, language)
- HTTP-only development environments
- Third-party analytics cookies

**Suppression Rule:**
```tsv
10054	https://example.com.*	_ga|_gid|theme	614	WARN
```

### 3. Cross-Domain JavaScript Source File Inclusion

**Alert:** JavaScript loaded from external domain

**False Positive Scenario:**
- Legitimate CDN usage (jQuery, Bootstrap, etc.)
- Third-party integrations (Google Analytics, Stripe)
- Using Subresource Integrity (SRI)

**Verification:**
```html
<!-- Check if SRI is used -->
<script src="https://cdn.example.com/library.js"
        integrity="sha384-HASH"
        crossorigin="anonymous"></script>
```

**When to Suppress:**
- CDN resources with SRI
- Trusted third-party services
- Company-owned CDN domains

**Suppression Rule:**
```tsv
10017	https://example.com/.*	https://cdn.jsdelivr.net/.*	829	IGNORE
```

### 4. Timestamp Disclosure

**Alert:** Unix timestamps found in response

**False Positive Scenario:**
- Legitimate timestamp fields in API responses
- Non-sensitive metadata
- Public timestamps (post dates, etc.)

**Verification:**
```json
{
  "created_at": 1640995200,  // Legitimate field
  "post_date": "2022-01-01"
}
```

**When to Suppress:**
- API responses with datetime fields
- Public-facing timestamps
- Non-sensitive metadata

**Suppression Rule:**
```tsv
10096	https://api.example.com/.*	created_at|updated_at	200	IGNORE
```

### 5. Server Version Disclosure

**Alert:** Server version exposed in headers

**False Positive Scenario:**
- Behind WAF/load balancer (version is of proxy, not app server)
- Generic server headers
- Already public knowledge

**Verification:**
```bash
curl -I https://example.com | grep Server
# Check if version matches actual server
```

**When to Suppress:**
- Proxy/WAF version (not actual app server)
- Generic headers without version numbers
- When other compensating controls exist

**Suppression Rule:**
```tsv
10036	https://example.com.*	.*	200	WARN
```

## Verification Methodology

### Step 1: Understand the Alert

Review ZAP alert details:
- **Description:** What is the potential vulnerability?
- **Evidence:** What triggered the alert?
- **CWE/OWASP Mapping:** What category does it fall under?
- **Risk Level:** How severe is it?

### Step 2: Reproduce Manually

Attempt to exploit the vulnerability:

```bash
# For XSS alerts
curl "https://example.com/search?q=<script>alert(1)</script>"
# Check if script is reflected unencoded

# For SQL injection alerts
curl "https://example.com/api/user?id=1' OR '1'='1"
# Check for SQL errors or unexpected behavior

# For path traversal alerts
curl "https://example.com/download?file=../../etc/passwd"
# Check if file is accessible
```

### Step 3: Check Context

Consider the application context:
- Is the functionality available to unauthenticated users?
- Does it handle sensitive data?
- Are there compensating controls (WAF, input validation)?

### Step 4: Document Decision

Create documentation for suppression decisions:

```markdown
## Alert: SQL Injection in /api/user

**Decision:** False Positive

**Rationale:**
- Endpoint requires authentication
- Input is validated server-side (allowlist: 0-9 only)
- WAF rule blocks SQL injection patterns
- Manual testing confirmed no injection possible

**Suppressed:** Yes (Rule ID 40018, /api/user endpoint)

**Reviewed by:** security-team@example.com
**Date:** 2024-01-15
```

## Creating Suppression Rules

### Rules File Format

ZAP uses TSV (tab-separated values) format:

```
alert_id	URL_pattern	parameter	CWE_id	action
```

- **alert_id:** ZAP alert ID (e.g., 40018 for SQL Injection)
- **URL_pattern:** Regex pattern for URL
- **parameter:** Parameter name (or .* for all)
- **CWE_id:** CWE identifier
- **action:** IGNORE, WARN, or FAIL

### Example Rules File

`.zap/rules.tsv`:

```tsv
# Suppress X-Content-Type-Options for CDN static content
10021	https://cdn.example.com/static/.*	.*	693	IGNORE

# Warn (don't fail) on analytics cookies without Secure flag
10054	https://example.com/.*	_ga|_gid	614	WARN

# Ignore timestamp disclosure in API responses
10096	https://api.example.com/.*	.*	200	IGNORE

# Ignore legitimate external JavaScript (with SRI)
10017	https://example.com/.*	https://cdn.jsdelivr.net/.*	829	IGNORE

# Suppress CSRF warnings for stateless API
10202	https://api.example.com/.*	.*	352	IGNORE
```

### Using Rules File

```bash
# Baseline scan with rules
docker run -t zaproxy/zap-stable zap-baseline.py \
  -t https://example.com \
  -c .zap/rules.tsv \
  -r report.html

# Full scan with rules
docker run -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable zap-full-scan.py \
  -t https://example.com \
  -c /zap/wrk/.zap/rules.tsv \
  -r /zap/wrk/report.html
```

## Custom Scan Policies

### Disable Entire Scan Rules

Create custom scan policy to disable problematic rules:

1. **Via ZAP GUI:**
   - Analyze > Scan Policy Manager
   - Create new policy
   - Disable specific rules
   - Export policy file

2. **Via Automation Framework:**

```yaml
# zap_automation.yaml
jobs:
  - type: activeScan
    parameters:
      policy: Custom-Policy
    rules:
      - id: 40018  # SQL Injection
        threshold: MEDIUM
        strength: HIGH
      - id: 10202  # CSRF
        threshold: OFF  # Disable completely
```

## Handling Different Alert Types

### High-Risk Alerts (Never Suppress Without Verification)

- SQL Injection
- Command Injection
- Remote Code Execution
- Authentication Bypass
- Server-Side Request Forgery (SSRF)

**Process:**
1. Manual verification required
2. Security team review
3. Document compensating controls
4. Re-test after fixes

### Medium-Risk Alerts (Contextual Suppression)

- XSS (if output is properly encoded)
- CSRF (if tokens are implemented)
- Missing headers (if compensating controls exist)

**Process:**
1. Verify finding
2. Check for compensating controls
3. Document decision
4. Suppress with WARN (not IGNORE)

### Low-Risk Alerts (Can Be Suppressed)

- Informational headers
- Timestamp disclosure
- Technology fingerprinting

**Process:**
1. Quick verification
2. Document reason
3. Suppress with IGNORE

## Quality Assurance

### Review Suppression Rules Regularly

```bash
# Monthly review checklist
- [ ] Review all suppression rules for continued relevance
- [ ] Check if suppressed issues have been fixed
- [ ] Verify compensating controls are still in place
- [ ] Update rules file with new false positives
```

### Track Suppression Metrics

Monitor suppression trends:

```bash
# Count suppressions by alert type
grep -v '^#' .zap/rules.tsv | awk '{print $1}' | sort | uniq -c

# Alert if suppression count increases significantly
```

### Peer Review Process

Require security team approval for suppressing high-risk alerts:

```yaml
# .github/workflows/security-review.yml
- name: Check for new suppressions
  run: |
    git diff origin/main .zap/rules.tsv > suppressions.diff
    if [ -s suppressions.diff ]; then
      echo "New suppressions require security team review"
      # Notify security team
    fi
```

## Anti-Patterns to Avoid

### ❌ Don't Suppress Everything

Never create blanket suppression rules:

```tsv
# BAD: Suppresses all XSS findings
40012	.*	.*	79	IGNORE
```

### ❌ Don't Suppress Without Documentation

Always document why a finding is suppressed:

```tsv
# BAD: No context
10054	https://example.com/.*	session_id	614	IGNORE

# GOOD: Documented reason
# Session cookie is HTTPS-only in production; suppressing for staging environment
10054	https://staging.example.com/.*	session_id	614	IGNORE
```

### ❌ Don't Ignore High-Risk Findings

Never suppress critical vulnerabilities without thorough investigation:

```tsv
# DANGEROUS: Never suppress SQL injection without verification
40018	https://example.com/.*	.*	89	IGNORE
```

## Tools and Scripts

### Analyze ZAP JSON Report

```python
#!/usr/bin/env python3
import json
import sys

with open('report.json') as f:
    report = json.load(f)

false_positives = []
for site in report['site']:
    for alert in site['alerts']:
        if alert['risk'] in ['High', 'Medium']:
            print(f"{alert['alert']} - {alert['risk']}")
            print(f"  URL: {alert['url']}")
            print(f"  Evidence: {alert.get('evidence', 'N/A')}")
            print()
```

### Generate Suppression Rules Template

```bash
# Extract unique alert IDs from report
jq -r '.site[].alerts[] | "\(.pluginid)\t\(.url)\t.*\t\(.cweid)\tWARN"' report.json \
  | sort -u > rules-template.tsv
```

## Additional Resources

- [ZAP Alert Details](https://www.zaproxy.org/docs/alerts/)
- [ZAP Scan Rules](https://www.zaproxy.org/docs/docker/baseline-scan/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
