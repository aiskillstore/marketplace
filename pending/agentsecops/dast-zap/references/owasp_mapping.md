# OWASP ZAP Alert Mapping to OWASP Top 10 2021 and CWE

This reference maps common OWASP ZAP alerts to OWASP Top 10 2021 categories and CWE (Common Weakness Enumeration) identifiers for compliance and reporting.

## OWASP Top 10 2021 Coverage

### A01:2021 - Broken Access Control

**ZAP Alerts:**
- Path Traversal (CWE-22)
- Directory Browsing (CWE-548)
- Cross-Domain Misconfiguration (CWE-346)
- Bypassing Access Controls (CWE-284)

**Risk Level:** High to Medium

**Remediation:**
- Implement proper access control checks on server-side
- Use allowlists for file access patterns
- Disable directory listing
- Enforce CORS policies strictly

### A02:2021 - Cryptographic Failures

**ZAP Alerts:**
- Weak SSL/TLS Ciphers (CWE-327)
- Cookie Without Secure Flag (CWE-614)
- Password Autocomplete (CWE-522)
- Sensitive Information in URL (CWE-598)

**Risk Level:** High to Medium

**Remediation:**
- Use TLS 1.2+ with strong cipher suites
- Set Secure and HttpOnly flags on all cookies
- Disable autocomplete for sensitive fields
- Never transmit sensitive data in URLs

### A03:2021 - Injection

**ZAP Alerts:**
- SQL Injection (CWE-89)
- Cross-Site Scripting (XSS) (CWE-79)
- Command Injection (CWE-78)
- LDAP Injection (CWE-90)
- XML Injection (CWE-91)
- XPath Injection (CWE-643)

**Risk Level:** High

**Remediation:**
- Use parameterized queries (prepared statements)
- Implement context-aware output encoding
- Validate and sanitize all user input
- Use allowlists for input validation
- Implement Content Security Policy (CSP)

### A04:2021 - Insecure Design

**ZAP Alerts:**
- Application Error Disclosure (CWE-209)
- Insufficient Anti-automation (CWE-799)
- Missing Rate Limiting

**Risk Level:** Medium to Low

**Remediation:**
- Implement proper error handling (generic error messages)
- Add CAPTCHA or rate limiting for sensitive operations
- Design security controls during architecture phase
- Implement anti-automation measures

### A05:2021 - Security Misconfiguration

**ZAP Alerts:**
- Missing Security Headers (CWE-693)
  - X-Content-Type-Options
  - X-Frame-Options (CWE-1021)
  - Content-Security-Policy
  - Strict-Transport-Security (HSTS)
- Server Leaks Information (CWE-200)
- Default Credentials
- Unnecessary HTTP Methods Enabled (CWE-650)

**Risk Level:** Medium to Low

**Remediation:**
- Configure all security headers properly
- Remove server version headers
- Disable unnecessary HTTP methods (PUT, DELETE, TRACE)
- Change default credentials
- Implement minimal privilege principle

### A06:2021 - Vulnerable and Outdated Components

**ZAP Alerts:**
- Outdated Software Version Detected
- Known Vulnerable Components (requires integration with CVE databases)

**Risk Level:** High to Medium

**Remediation:**
- Maintain software inventory
- Regularly update dependencies and libraries
- Subscribe to security advisories
- Use dependency scanning tools (OWASP Dependency-Check, Snyk)

### A07:2021 - Identification and Authentication Failures

**ZAP Alerts:**
- Weak Authentication (CWE-287)
- Session Fixation (CWE-384)
- Session ID in URL Rewrite (CWE-598)
- Cookie No HttpOnly Flag (CWE-1004)
- Credential Enumeration (CWE-209)

**Risk Level:** High

**Remediation:**
- Implement multi-factor authentication (MFA)
- Use secure session management
- Regenerate session IDs after login
- Set HttpOnly and Secure flags on session cookies
- Implement account lockout mechanisms
- Use generic error messages for authentication failures

### A08:2021 - Software and Data Integrity Failures

**ZAP Alerts:**
- Missing Subresource Integrity (SRI) (CWE-353)
- Insecure Deserialization (CWE-502)

**Risk Level:** High to Medium

**Remediation:**
- Implement Subresource Integrity for CDN resources
- Avoid deserializing untrusted data
- Use digital signatures for critical data
- Implement integrity checks

### A09:2021 - Security Logging and Monitoring Failures

**ZAP Alerts:**
- Authentication attempts not logged
- No monitoring of security events

**Risk Level:** Low (detection issue, not vulnerability)

**Remediation:**
- Log all authentication attempts
- Monitor for security anomalies
- Implement centralized logging
- Set up alerts for suspicious activities

### A10:2021 - Server-Side Request Forgery (SSRF)

**ZAP Alerts:**
- Server-Side Request Forgery (CWE-918)
- External Redirect (CWE-601)

**Risk Level:** High

**Remediation:**
- Validate and sanitize all URLs
- Use allowlists for allowed domains
- Disable unnecessary URL schemas (file://, gopher://)
- Implement network segmentation

## ZAP Alert ID to OWASP/CWE Quick Reference

| Alert ID | Alert Name | OWASP 2021 | CWE | Risk |
|----------|-----------|------------|-----|------|
| 40018 | SQL Injection | A03 | CWE-89 | High |
| 40012 | Cross-Site Scripting (Reflected) | A03 | CWE-79 | High |
| 40014 | Cross-Site Scripting (Persistent) | A03 | CWE-79 | High |
| 40013 | Cross-Site Scripting (DOM) | A03 | CWE-79 | High |
| 6 | Path Traversal | A01 | CWE-22 | High |
| 7 | Remote File Inclusion | A01 | CWE-98 | High |
| 90019 | Server-Side Code Injection | A03 | CWE-94 | High |
| 90020 | Remote OS Command Injection | A03 | CWE-78 | High |
| 90033 | Loosely Scoped Cookie | A07 | CWE-565 | Medium |
| 10021 | X-Content-Type-Options Missing | A05 | CWE-693 | Low |
| 10020 | X-Frame-Options Missing | A05 | CWE-1021 | Medium |
| 10038 | Content Security Policy Missing | A05 | CWE-693 | Medium |
| 10035 | Strict-Transport-Security Missing | A05 | CWE-319 | Low |
| 10054 | Cookie Without Secure Flag | A02 | CWE-614 | Medium |
| 10010 | Cookie No HttpOnly Flag | A07 | CWE-1004 | Medium |
| 10098 | Cross-Domain Misconfiguration | A01 | CWE-346 | Medium |
| 10055 | CSP Scanner: Wildcard Directive | A05 | CWE-693 | Medium |
| 10096 | Timestamp Disclosure | A05 | CWE-200 | Low |
| 10049 | Weak Authentication Method | A07 | CWE-287 | Medium |
| 40029 | Server-Side Request Forgery | A10 | CWE-918 | High |

## Risk Level Priority Matrix

### High Risk (Immediate Action Required)
- SQL Injection
- Remote Code Execution
- Authentication Bypass
- SSRF
- XXE (XML External Entity)

### Medium Risk (Fix in Current Sprint)
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- Missing Security Headers (CSP, X-Frame-Options)
- Insecure Cookie Configuration
- Path Traversal (with limited impact)

### Low Risk (Fix in Backlog)
- Information Disclosure (version headers)
- Missing Informational Headers
- Timestamp Disclosure
- Autocomplete on Form Fields

### Informational (Documentation/Awareness)
- Server Technology Disclosure
- Application Error Messages
- Charset Mismatch

## Compliance Mapping

### PCI-DSS 3.2.1
- **Requirement 6.5.1** (Injection): SQL Injection, Command Injection, XSS
- **Requirement 6.5.3** (Insecure Cryptography): Weak SSL/TLS, Insecure Cookies
- **Requirement 6.5.7** (XSS): All XSS variants
- **Requirement 6.5.8** (Access Control): Path Traversal, Broken Access Control
- **Requirement 6.5.10** (Authentication): Weak Authentication, Session Management

### NIST 800-53
- **AC-3** (Access Enforcement): Path Traversal, Authorization Issues
- **IA-5** (Authenticator Management): Weak Authentication
- **SC-8** (Transmission Confidentiality): Missing HTTPS, Weak TLS
- **SI-10** (Information Input Validation): All Injection Flaws

### GDPR
- **Article 32** (Security of Processing): All High/Medium findings affecting data security
- **Article 25** (Data Protection by Design): Security Misconfigurations

## Usage in Reports

When generating compliance reports, reference this mapping to:

1. **Categorize findings** by OWASP Top 10 category
2. **Assign CWE IDs** for standardized vulnerability classification
3. **Map to compliance requirements** for audit trails
4. **Prioritize remediation** based on risk level and compliance impact
5. **Track metrics** by OWASP category over time

## Additional Resources

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [ZAP Alert Details](https://www.zaproxy.org/docs/alerts/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
