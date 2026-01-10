# Nuclei False Positive Handling Guide

## Table of Contents
- [Understanding False Positives](#understanding-false-positives)
- [Common False Positive Scenarios](#common-false-positive-scenarios)
- [Verification Techniques](#verification-techniques)
- [Template Filtering Strategies](#template-filtering-strategies)
- [Custom Template Refinement](#custom-template-refinement)

## Understanding False Positives

False positives occur when Nuclei reports a finding that doesn't represent an actual security vulnerability in the context of your application.

### Types of False Positives

1. **Context-Specific**: Finding is valid in general but not applicable to your application
2. **Version-Specific**: CVE template triggers but your version is patched
3. **Configuration-Based**: Security control exists but Nuclei can't detect it
4. **Pattern Matching Errors**: Regex/word matchers trigger on benign content

## Common False Positive Scenarios

### 1. Missing Security Headers (Info/Low Severity)

**Finding**: Missing `X-Frame-Options`, `Content-Security-Policy`

**False Positive When**:
- Headers set at CDN/WAF level (not visible to scanner)
- Application is not intended for browser rendering (pure API)
- Modern browsers already protect against clickjacking

**Verification**:
```bash
# Check headers from actual browser
curl -I https://target-app.com
curl -I https://target-app.com -H "User-Agent: Mozilla/5.0"

# Check if CDN adds headers
curl -I https://target-app.com -v 2>&1 | grep -i "x-frame-options\|content-security"
```

**Filter Strategy**:
```bash
# Exclude header-related info findings
nuclei -u https://target-app.com -etags headers -severity critical,high
```

### 2. Directory Listing / Exposed Paths

**Finding**: Directory listing enabled, exposed paths like `/admin`, `/backup`

**False Positive When**:
- Path requires authentication (Nuclei tested unauthenticated)
- Path is intentionally public (documentation, public assets)
- CDN/WAF blocks access (returns 200 with error page)

**Verification**:
```bash
# Manual verification with authentication
curl https://target-app.com/admin \
  -H "Authorization: Bearer $TOKEN" \
  -H "Cookie: session=$SESSION"

# Check actual response content
curl https://target-app.com/backup | head -20
```

**Filter Strategy**:
```bash
# Exclude exposure templates for authenticated scans
nuclei -u https://target-app.com \
  -header "Authorization: Bearer $TOKEN" \
  -etags exposure
```

### 3. CVE Templates Against Patched Versions

**Finding**: CVE-2024-XXXXX detected

**False Positive When**:
- Application version is patched but template matches on generic patterns
- Backported patches applied without version number change
- Template uses loose detection criteria

**Verification**:
```bash
# Check actual version
curl https://target-app.com/version
curl https://target-app.com -v 2>&1 | grep -i "server:"

# Cross-reference with CVE details
# Check if version is vulnerable per NVD/vendor advisory
```

**Filter Strategy**:
```bash
# Scan only recent CVEs
nuclei -u https://target-app.com \
  -tags cve \
  -template-condition "contains(id, 'CVE-2024') || contains(id, 'CVE-2023')"

# Exclude specific false positive templates
nuclei -u https://target-app.com \
  -exclude-id CVE-2018-12345,CVE-2019-67890
```

### 4. Technology Detection False Positives

**Finding**: WordPress, Drupal, or other CMS detected

**False Positive When**:
- Generic strings match (like "wp-" in custom code)
- Legacy migration artifacts remain
- Application mimics CMS structure but isn't actually that CMS

**Verification**:
```bash
# Check for actual CMS files
curl https://target-app.com/wp-admin/
curl https://target-app.com/wp-includes/
curl https://target-app.com/readme.html

# Technology fingerprinting
whatweb https://target-app.com
wappalyzer https://target-app.com
```

**Filter Strategy**:
```bash
# Exclude tech detection templates
nuclei -u https://target-app.com -etags tech
```

### 5. Default Login Pages

**Finding**: Admin panel or login page detected

**False Positive When**:
- Panel is legitimate and intended to be accessible
- Panel requires MFA even if default credentials work
- Detection based on title/strings only without credential testing

**Verification**:
```bash
# Test if default credentials actually work
curl -X POST https://target-app.com/login \
  -d "username=admin&password=admin" \
  -v

# Check if MFA is required
curl -X POST https://target-app.com/login \
  -d "username=admin&password=admin" \
  -c cookies.txt

curl https://target-app.com/dashboard \
  -b cookies.txt
```

**Filter Strategy**:
```bash
# Scan with authentication to skip login detection
nuclei -u https://target-app.com \
  -header "Authorization: Bearer $TOKEN" \
  -etags default-logins,exposed-panels
```

### 6. API Endpoints Reporting Errors

**Finding**: SQL errors, stack traces, or verbose errors detected

**False Positive When**:
- Errors are intentional validation messages
- Stack traces only shown in dev/staging (not production)
- API returns structured error JSON (not actual stack trace)

**Verification**:
```bash
# Check actual error response
curl https://api.target.com/endpoint?id=invalid -v

# Verify it's not SQL error but validation error
curl https://api.target.com/endpoint?id=' OR '1'='1 -v
```

### 7. CORS Misconfiguration

**Finding**: `Access-Control-Allow-Origin: *`

**False Positive When**:
- Intentional for public APIs
- Only applies to non-sensitive endpoints
- Additional CORS headers restrict actual access

**Verification**:
```bash
# Check if sensitive endpoints have CORS
curl https://api.target.com/public/data \
  -H "Origin: https://evil.com" -v

curl https://api.target.com/private/users \
  -H "Origin: https://evil.com" \
  -H "Authorization: Bearer $TOKEN" -v
```

## Verification Techniques

### Manual Verification Checklist

For each critical/high severity finding:

1. **Reproduce the finding**:
   ```bash
   # Use exact URL and parameters from Nuclei output
   curl "https://target-app.com/vulnerable-path" -v
   ```

2. **Check authentication context**:
   ```bash
   # Test with authentication
   curl "https://target-app.com/vulnerable-path" \
     -H "Authorization: Bearer $TOKEN" -v
   ```

3. **Verify exploitability**:
   - Can you actually exploit the vulnerability?
   - Is there a working PoC?
   - What's the actual impact?

4. **Check mitigating controls**:
   - WAF rules blocking exploitation
   - Network segmentation limiting access
   - Monitoring and alerting in place

5. **Consult security team**:
   - Discuss edge cases with security engineers
   - Review against threat model

### Automated Verification Script

Use bundled script to batch verify findings:

```bash
python3 scripts/verify_findings.py \
  --input nuclei-results.jsonl \
  --auth-token $AUTH_TOKEN \
  --output verified-findings.jsonl
```

## Template Filtering Strategies

### Strategy 1: Severity-Based Filtering

Focus on high-impact findings:

```bash
# Critical and high only
nuclei -u https://target-app.com -severity critical,high

# Exclude info findings
nuclei -u https://target-app.com -exclude-severity info
```

### Strategy 2: Tag-Based Filtering

Filter by vulnerability type:

```bash
# Only CVEs and OWASP vulnerabilities
nuclei -u https://target-app.com -tags cve,owasp

# Exclude informational tags
nuclei -u https://target-app.com -etags tech,info,headers
```

### Strategy 3: Template Exclusion

Exclude known false positive templates:

```bash
# Exclude specific templates
nuclei -u https://target-app.com \
  -exclude-id CVE-2018-12345,generic-login-panel

# Exclude template directories
nuclei -u https://target-app.com \
  -exclude-templates nuclei-templates/http/misconfiguration/
```

### Strategy 4: Custom Template Allowlist

Use only verified templates:

```bash
# Scan with curated template set
nuclei -u https://target-app.com \
  -t custom-templates/verified/ \
  -t nuclei-templates/http/cves/2024/
```

### Strategy 5: Conditional Template Execution

Use template conditions:

```bash
# Only recent critical CVEs
nuclei -u https://target-app.com \
  -tags cve \
  -severity critical \
  -template-condition "contains(id, 'CVE-2024')"
```

## Custom Template Refinement

### Improving Matcher Accuracy

**Before (High False Positives)**:
```yaml
matchers:
  - type: word
    words:
      - "admin"
```

**After (Lower False Positives)**:
```yaml
matchers-condition: and
matchers:
  - type: status
    status:
      - 200

  - type: word
    part: body
    words:
      - "admin"
      - "dashboard"
      - "login"
    condition: and

  - type: regex
    regex:
      - '<title>[^<]*admin[^<]*panel[^<]*</title>'
    case-insensitive: true
```

### Adding Negative Matchers

Exclude known false positive patterns:

```yaml
matchers:
  - type: word
    words:
      - "SQL syntax error"

  # Negative matcher - must NOT match
  - type: word
    negative: true
    words:
      - "validation error"
      - "input error"
```

### Version-Specific Matching

Match specific vulnerable versions:

```yaml
matchers-condition: and
matchers:
  - type: regex
    regex:
      - 'WordPress/([0-5]\.[0-9]\.[0-9])'  # Versions < 6.0.0

  - type: word
    words:
      - "wp-admin"
```

### Confidence-Based Classification

Add confidence levels to findings:

```yaml
info:
  metadata:
    confidence: high  # low, medium, high

matchers-condition: and  # More matchers = higher confidence
matchers:
  - type: status
    status: [200]

  - type: word
    words: ["vulnerable_signature_1", "vulnerable_signature_2"]
    condition: and

  - type: regex
    regex: ['specific[_-]pattern']
```

## False Positive Tracking

### Document Known False Positives

Create suppression file:

```yaml
# false-positives.yaml
suppressions:
  - template: CVE-2018-12345
    reason: "Application version is patched (backport applied)"
    verified_by: security-team
    verified_date: 2024-11-20

  - template: exposed-admin-panel
    urls:
      - https://target-app.com/admin
    reason: "Admin panel requires MFA and IP allowlist"
    verified_by: security-team
    verified_date: 2024-11-20

  - template: missing-csp-header
    reason: "CSP header added at CDN level (Cloudflare)"
    verified_by: devops-team
    verified_date: 2024-11-20
```

### Use Suppression in Scans

```bash
# Filter out documented false positives
python3 scripts/filter_suppressions.py \
  --scan-results nuclei-results.jsonl \
  --suppressions false-positives.yaml \
  --output filtered-results.jsonl
```

## Best Practices

1. **Always Verify Critical Findings Manually**: Don't trust automated tools blindly
2. **Context Matters**: What's vulnerable in one app may be safe in another
3. **Track False Positives**: Document and share with team
4. **Refine Templates**: Improve matcher accuracy over time
5. **Use Multiple Tools**: Cross-verify with other scanners (ZAP, Burp, etc.)
6. **Severity Calibration**: Adjust severity based on your environment
7. **Regular Template Updates**: Keep templates current to reduce false positives
8. **Authenticated Scanning**: Many false positives occur in unauthenticated scans

## Tools and Resources

### Verification Tools

```bash
# cURL for manual verification
curl -v https://target-app.com/endpoint

# httpie (user-friendly HTTP client)
http https://target-app.com/endpoint

# Burp Suite for manual testing
# ZAP for cross-verification
```

### Analysis Scripts

Use bundled scripts:

```bash
# Compare findings across scans
python3 scripts/compare_scans.py \
  --baseline scan1.jsonl \
  --current scan2.jsonl

# Filter findings by confidence
python3 scripts/filter_by_confidence.py \
  --input scan-results.jsonl \
  --min-confidence high \
  --output high-confidence.jsonl
```

## Conclusion

False positives are inevitable in automated security scanning. The key is to:
- Understand WHY false positives occur
- Develop systematic verification processes
- Refine templates and filters over time
- Document and track false positives for future reference
- Balance automation with manual verification

A good rule of thumb: **Spend time refining your scanning approach to maximize signal-to-noise ratio**.
