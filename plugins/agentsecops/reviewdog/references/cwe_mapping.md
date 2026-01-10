# CWE Mapping for Security Tools

This reference maps common security tool findings to CWE (Common Weakness Enumeration) categories.

## Table of Contents

- [OWASP Top 10 to CWE Mapping](#owasp-top-10-to-cwe-mapping)
- [Tool-Specific CWE Coverage](#tool-specific-cwe-coverage)
- [CWE Categories](#cwe-categories)
- [Severity Mapping](#severity-mapping)

## OWASP Top 10 to CWE Mapping

Map OWASP Top 10 2021 vulnerabilities to their primary CWEs:

| OWASP Category | CWE IDs | Reviewdog Detection |
|----------------|---------|---------------------|
| **A01: Broken Access Control** | CWE-22, CWE-23, CWE-35, CWE-59, CWE-200, CWE-201, CWE-219, CWE-264, CWE-275, CWE-284, CWE-285, CWE-352, CWE-359, CWE-377, CWE-402, CWE-425, CWE-441, CWE-497, CWE-538, CWE-540, CWE-548, CWE-552, CWE-566, CWE-601, CWE-639, CWE-651, CWE-668, CWE-706, CWE-862, CWE-863, CWE-913, CWE-922, CWE-1275 | Semgrep, Bandit, Checkov |
| **A02: Cryptographic Failures** | CWE-259, CWE-327, CWE-328, CWE-329, CWE-330, CWE-331, CWE-335, CWE-336, CWE-337, CWE-338, CWE-340, CWE-347, CWE-523, CWE-720, CWE-757, CWE-759, CWE-760, CWE-780, CWE-818, CWE-916 | Bandit, Semgrep, Gitleaks |
| **A03: Injection** | CWE-20, CWE-74, CWE-75, CWE-77, CWE-78, CWE-79, CWE-80, CWE-83, CWE-87, CWE-88, CWE-89, CWE-90, CWE-91, CWE-93, CWE-94, CWE-95, CWE-96, CWE-97, CWE-98, CWE-99, CWE-100, CWE-113, CWE-116, CWE-138, CWE-184, CWE-470, CWE-471, CWE-564, CWE-610, CWE-643, CWE-644, CWE-652, CWE-917 | Semgrep, Bandit, ESLint |
| **A04: Insecure Design** | CWE-73, CWE-183, CWE-209, CWE-213, CWE-235, CWE-256, CWE-257, CWE-266, CWE-269, CWE-280, CWE-311, CWE-312, CWE-313, CWE-316, CWE-419, CWE-430, CWE-434, CWE-444, CWE-451, CWE-472, CWE-501, CWE-522, CWE-525, CWE-539, CWE-579, CWE-598, CWE-602, CWE-642, CWE-646, CWE-650, CWE-653, CWE-656, CWE-657, CWE-799, CWE-807, CWE-840, CWE-841, CWE-927, CWE-1021, CWE-1173 | Architecture review |
| **A05: Security Misconfiguration** | CWE-2, CWE-11, CWE-13, CWE-15, CWE-16, CWE-260, CWE-315, CWE-520, CWE-526, CWE-537, CWE-541, CWE-547, CWE-611, CWE-614, CWE-756, CWE-776, CWE-942, CWE-1004, CWE-1032, CWE-1174 | Checkov, Hadolint, Trivy |
| **A06: Vulnerable Components** | CWE-1104, CWE-1035 | Trivy, Dependabot, Snyk |
| **A07: Authentication Failures** | CWE-255, CWE-259, CWE-287, CWE-288, CWE-290, CWE-294, CWE-295, CWE-297, CWE-300, CWE-302, CWE-304, CWE-306, CWE-307, CWE-346, CWE-384, CWE-521, CWE-613, CWE-620, CWE-640, CWE-798, CWE-940, CWE-1216 | Semgrep, Bandit, Gitleaks |
| **A08: Software/Data Integrity** | CWE-345, CWE-353, CWE-426, CWE-494, CWE-502, CWE-565, CWE-784, CWE-829, CWE-830, CWE-915 | Bandit, Semgrep |
| **A09: Security Logging Failures** | CWE-117, CWE-223, CWE-532, CWE-778 | Semgrep |
| **A10: SSRF** | CWE-918 | Semgrep, Bandit |

## Tool-Specific CWE Coverage

### Semgrep

**Primary CWE Coverage**:
- CWE-20: Improper Input Validation
- CWE-22: Path Traversal
- CWE-78: OS Command Injection
- CWE-79: Cross-site Scripting (XSS)
- CWE-89: SQL Injection
- CWE-94: Code Injection
- CWE-327: Use of Broken Cryptography
- CWE-502: Deserialization of Untrusted Data
- CWE-601: Open Redirect
- CWE-611: XXE
- CWE-798: Hardcoded Credentials
- CWE-918: SSRF

**Example Detections**:
```bash
# SQL Injection (CWE-89)
semgrep --config "p/sql-injection" --json | reviewdog -f=semgrep

# XSS (CWE-79)
semgrep --config "p/xss" --json | reviewdog -f=semgrep

# Command Injection (CWE-78)
semgrep --config "p/command-injection" --json | reviewdog -f=semgrep
```

---

### Bandit (Python)

**Primary CWE Coverage**:
- CWE-78: OS Command Injection (shell=True)
- CWE-89: SQL Injection
- CWE-259: Hard-coded Password
- CWE-295: Improper Certificate Validation
- CWE-327: Broken Crypto (MD5, SHA1)
- CWE-338: Weak PRNG
- CWE-502: Pickle Deserialization
- CWE-798: Hardcoded Credentials

**Bandit Test ID to CWE**:
| Bandit Test | CWE | Description |
|-------------|-----|-------------|
| B201 | CWE-209 | Flask debug mode |
| B301 | CWE-502 | Pickle usage |
| B302 | CWE-327 | MD5 usage |
| B303 | CWE-327 | SHA1 usage |
| B304 | CWE-327 | Insecure ciphers |
| B305 | CWE-327 | Insecure cipher modes |
| B306 | CWE-378 | Insecure temp file |
| B307 | CWE-78  | eval() usage |
| B308 | CWE-94  | mark_safe usage |
| B310 | CWE-601 | URL open |
| B311 | CWE-338 | Weak random |
| B324 | CWE-327 | hashlib.new insecure |
| B501 | CWE-295 | Cert validation disabled |
| B601 | CWE-78  | Paramiko exec |
| B602 | CWE-78  | Shell injection |
| B603 | CWE-78  | Subprocess w/o shell |
| B604 | CWE-78  | Shell=True |
| B605 | CWE-78  | Shell command strings |
| B607 | CWE-78  | Partial path process |

**Example**:
```bash
bandit -r . -f json | reviewdog -f=bandit -reporter=github-pr-review
```

---

### Gitleaks

**Primary CWE Coverage**:
- CWE-798: Use of Hard-coded Credentials

**Detected Secret Types**:
- API keys and tokens
- AWS credentials
- Database passwords
- Private keys (SSH, PGP, certificates)
- OAuth tokens
- JWT secrets

**Example**:
```bash
gitleaks detect --report-format json | reviewdog -f=gitleaks -reporter=github-pr-review
```

---

### Checkov (IaC)

**Primary CWE Coverage**:
- CWE-250: Execution with Unnecessary Privileges
- CWE-284: Improper Access Control
- CWE-326: Inadequate Encryption Strength
- CWE-521: Weak Password Requirements
- CWE-601: Open Redirect
- CWE-668: Exposure of Resource

**Common Findings**:
```bash
# S3 bucket public access (CWE-284, CWE-668)
# Unencrypted storage (CWE-326)
# Overly permissive IAM (CWE-250, CWE-284)
# Missing encryption in transit (CWE-319)

checkov -d . --framework terraform -o json | reviewdog -f=checkov
```

---

### Hadolint (Dockerfile)

**Primary CWE Coverage**:
- CWE-250: Execution with Unnecessary Privileges (USER root)
- CWE-798: Hardcoded Credentials in ENV

**Common Issues**:
- DL3000-DL3999: Dockerfile best practices
- DL4000-DL4999: Security issues

**Example**:
```bash
hadolint Dockerfile --format json | reviewdog -f=hadolint
```

---

### ShellCheck

**Primary CWE Coverage**:
- CWE-78: OS Command Injection
- CWE-377: Insecure Temporary File

**Example**:
```bash
shellcheck -f json script.sh | reviewdog -f=shellcheck
```

---

## CWE Categories

### CWE Top 25 (2023)

The most dangerous software weaknesses:

| Rank | CWE-ID | Name | Reviewdog Tools |
|------|--------|------|-----------------|
| 1 | CWE-787 | Out-of-bounds Write | - |
| 2 | CWE-79 | Cross-site Scripting | Semgrep, ESLint |
| 3 | CWE-89 | SQL Injection | Semgrep, Bandit |
| 4 | CWE-20 | Improper Input Validation | Semgrep, Bandit |
| 5 | CWE-125 | Out-of-bounds Read | - |
| 6 | CWE-78 | OS Command Injection | Semgrep, Bandit, ShellCheck |
| 7 | CWE-416 | Use After Free | - |
| 8 | CWE-22 | Path Traversal | Semgrep, Bandit |
| 9 | CWE-352 | CSRF | Semgrep |
| 10 | CWE-434 | Unrestricted Upload | Semgrep |
| 11 | CWE-862 | Missing Authorization | Semgrep |
| 12 | CWE-476 | NULL Pointer Dereference | - |
| 13 | CWE-287 | Improper Authentication | Semgrep, Bandit |
| 14 | CWE-190 | Integer Overflow | - |
| 15 | CWE-502 | Deserialization | Bandit, Semgrep |
| 16 | CWE-77 | Command Injection | Semgrep, Bandit |
| 17 | CWE-119 | Memory Buffer Errors | - |
| 18 | CWE-798 | Hardcoded Credentials | Gitleaks, Bandit, Semgrep |
| 19 | CWE-918 | SSRF | Semgrep |
| 20 | CWE-306 | Missing Authentication | Semgrep |
| 21 | CWE-362 | Race Condition | - |
| 22 | CWE-269 | Improper Privilege Mgmt | Checkov, Semgrep |
| 23 | CWE-94 | Code Injection | Semgrep, Bandit |
| 24 | CWE-863 | Incorrect Authorization | Semgrep |
| 25 | CWE-276 | Incorrect Permissions | Checkov, Semgrep |

---

## Severity Mapping

Map CWE to severity levels for reviewdog filtering:

### Critical (fail-on-error)

- CWE-78: OS Command Injection
- CWE-79: Cross-site Scripting
- CWE-89: SQL Injection
- CWE-94: Code Injection
- CWE-502: Deserialization of Untrusted Data
- CWE-798: Hardcoded Credentials
- CWE-918: SSRF

**Reviewdog Configuration**:
```bash
semgrep --severity=ERROR --json | \
  reviewdog -f=semgrep -level=error -fail-on-error=true
```

---

### High (block PR merge)

- CWE-22: Path Traversal
- CWE-77: Command Injection
- CWE-287: Improper Authentication
- CWE-306: Missing Authentication
- CWE-327: Broken Cryptography
- CWE-601: Open Redirect
- CWE-611: XXE
- CWE-862: Missing Authorization
- CWE-863: Incorrect Authorization

**Reviewdog Configuration**:
```bash
semgrep --severity=WARNING --json | \
  reviewdog -f=semgrep -level=error -fail-on-error=true
```

---

### Medium (comment, don't block)

- CWE-200: Information Exposure
- CWE-209: Error Message Information Leak
- CWE-284: Improper Access Control
- CWE-295: Improper Certificate Validation
- CWE-338: Weak PRNG
- CWE-352: CSRF
- CWE-434: Unrestricted File Upload
- CWE-532: Information Exposure Through Log Files

**Reviewdog Configuration**:
```bash
semgrep --severity=WARNING --json | \
  reviewdog -f=semgrep -level=warning
```

---

### Low/Info (informational)

- CWE-1104: Use of Unmaintained Third Party Components
- CWE-710: Improper Coding Practices
- Configuration best practices
- Code quality issues

**Reviewdog Configuration**:
```bash
semgrep --severity=INFO --json | \
  reviewdog -f=semgrep -level=info
```

---

## Example: Comprehensive CWE-Based Scanning

```yaml
name: CWE-Based Security Scan

on: [pull_request]

jobs:
  critical-cwe:
    name: Critical CWE (78, 79, 89, 94, 502, 798, 918)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: reviewdog/action-setup@v1

      - name: Scan for Critical CWE
        env:
          REVIEWDOG_GITHUB_API_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # CWE-78, 89, 94 - Injection
          semgrep --config "p/security-audit" \
                  --severity=ERROR \
                  --json | \
            reviewdog -f=semgrep \
                     -name="Critical: Injection (CWE-78,89,94)" \
                     -reporter=github-pr-review \
                     -fail-on-error=true

          # CWE-798 - Hardcoded credentials
          gitleaks detect --report-format json | \
            reviewdog -f=gitleaks \
                     -name="Critical: Hardcoded Secrets (CWE-798)" \
                     -reporter=github-pr-review \
                     -fail-on-error=true

  high-cwe:
    name: High CWE (22, 287, 327, 601, 862)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: reviewdog/action-setup@v1

      - name: Scan for High CWE
        env:
          REVIEWDOG_GITHUB_API_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          semgrep --config "p/owasp-top-ten" \
                  --json | \
            reviewdog -f=semgrep \
                     -name="High: OWASP/CWE" \
                     -reporter=github-pr-review \
                     -level=error
```

---

## References

- [CWE Top 25](https://cwe.mitre.org/top25/)
- [CWE OWASP Top 10 Mapping](https://owasp.org/Top10/)
- [CWE List](https://cwe.mitre.org/data/index.html)
- [CAPEC](https://capec.mitre.org/) - Attack patterns for CWEs
