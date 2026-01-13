# OWASP Top 10 2021 Mapping for Nuclei Findings

## Table of Contents
- [A01:2021 - Broken Access Control](#a012021---broken-access-control)
- [A02:2021 - Cryptographic Failures](#a022021---cryptographic-failures)
- [A03:2021 - Injection](#a032021---injection)
- [A04:2021 - Insecure Design](#a042021---insecure-design)
- [A05:2021 - Security Misconfiguration](#a052021---security-misconfiguration)
- [A06:2021 - Vulnerable and Outdated Components](#a062021---vulnerable-and-outdated-components)
- [A07:2021 - Identification and Authentication Failures](#a072021---identification-and-authentication-failures)
- [A08:2021 - Software and Data Integrity Failures](#a082021---software-and-data-integrity-failures)
- [A09:2021 - Security Logging and Monitoring Failures](#a092021---security-logging-and-monitoring-failures)
- [A10:2021 - Server-Side Request Forgery (SSRF)](#a102021---server-side-request-forgery-ssrf)

## A01:2021 - Broken Access Control

### Nuclei Template Tags
- `exposure` - Exposed sensitive files and directories
- `idor` - Insecure Direct Object References
- `auth-bypass` - Authentication bypass vulnerabilities
- `privilege-escalation` - Privilege escalation issues

### Common Findings
- **Exposed Admin Panels**: `/admin`, `/administrator`, `/wp-admin` accessible without authentication
- **Directory Listing**: Open directory listings exposing sensitive files
- **Backup Files Exposed**: `.bak`, `.sql`, `.zip` files publicly accessible
- **Git/SVN Exposure**: `.git`, `.svn` directories exposed
- **API Access Control**: Missing authorization checks on API endpoints

### Remediation Priority
**Critical** - Immediate action required for exposed admin panels and authentication bypasses

## A02:2021 - Cryptographic Failures

### Nuclei Template Tags
- `ssl` - SSL/TLS configuration issues
- `weak-crypto` - Weak cryptographic implementations
- `exposed-keys` - Exposed cryptographic keys

### Common Findings
- **Weak TLS Versions**: TLS 1.0, TLS 1.1 still enabled
- **Weak Cipher Suites**: RC4, DES, 3DES in use
- **Missing HSTS**: HTTP Strict Transport Security not configured
- **Self-Signed Certificates**: Invalid or self-signed SSL certificates
- **Exposed Private Keys**: Private keys in public repositories or directories

### Remediation Priority
**High** - Update to TLS 1.2+ and modern cipher suites

## A03:2021 - Injection

### Nuclei Template Tags
- `sqli` - SQL Injection
- `xss` - Cross-Site Scripting
- `xxe` - XML External Entity
- `ssti` - Server-Side Template Injection
- `nosqli` - NoSQL Injection
- `cmdi` - Command Injection

### Common Findings
- **SQL Injection**: User input reflected in database queries
- **Cross-Site Scripting (XSS)**: Reflected, Stored, and DOM-based XSS
- **Command Injection**: OS command execution via user input
- **LDAP Injection**: LDAP query manipulation
- **Template Injection**: Server-side template injection in Jinja2, Twig, etc.

### Remediation Priority
**Critical** - SQL Injection and Command Injection require immediate remediation

## A04:2021 - Insecure Design

### Nuclei Template Tags
- `logic` - Business logic flaws
- `workflow` - Workflow bypass vulnerabilities

### Common Findings
- **Rate Limiting Bypass**: Missing rate limiting on authentication endpoints
- **Workflow Bypass**: Steps in business processes can be skipped
- **Insufficient Resource Allocation**: No limits on resource consumption
- **Unvalidated Redirects**: Open redirect vulnerabilities

### Remediation Priority
**Medium to High** - Depends on business impact and exploitability

## A05:2021 - Security Misconfiguration

### Nuclei Template Tags
- `misconfig` - Generic misconfigurations
- `headers` - Missing security headers
- `cors` - CORS misconfigurations
- `debug` - Debug modes enabled in production

### Common Findings
- **Missing Security Headers**:
  - `Content-Security-Policy`
  - `X-Frame-Options`
  - `X-Content-Type-Options`
  - `Strict-Transport-Security`
- **CORS Misconfiguration**: `Access-Control-Allow-Origin: *`
- **Debug Mode Enabled**: Stack traces, verbose errors in production
- **Default Configurations**: Unchanged default credentials and settings
- **Directory Indexing**: Apache/Nginx directory listing enabled

### Remediation Priority
**Medium** - Apply hardening configurations and remove debug modes

## A06:2021 - Vulnerable and Outdated Components

### Nuclei Template Tags
- `cve` - Known CVE vulnerabilities
- `eol` - End-of-life software
- `outdated` - Outdated software versions

### Common Findings
- **Known CVEs**: Outdated libraries with public CVEs (Log4Shell, Spring4Shell, etc.)
- **End-of-Life Software**: Unsupported versions of frameworks and libraries
- **Vulnerable JavaScript Libraries**: jQuery, Angular, React with known vulnerabilities
- **CMS Vulnerabilities**: WordPress, Drupal, Joomla plugin vulnerabilities

### Remediation Priority
**Critical to High** - Patch immediately based on CVSS score and exploitability

### Example CVE Mappings
```
CVE-2021-44228 (Log4Shell)         → Critical → A06
CVE-2022-22965 (Spring4Shell)      → Critical → A06
CVE-2017-5638 (Struts2 RCE)        → Critical → A06
CVE-2021-26855 (Exchange ProxyLogon) → Critical → A06
```

## A07:2021 - Identification and Authentication Failures

### Nuclei Template Tags
- `auth` - Authentication issues
- `jwt` - JWT vulnerabilities
- `oauth` - OAuth misconfigurations
- `default-logins` - Default credentials
- `session` - Session management issues

### Common Findings
- **Default Credentials**: Admin/admin, root/root, default passwords
- **Weak Password Policies**: No complexity requirements
- **Session Fixation**: Session tokens not regenerated after login
- **JWT Vulnerabilities**: `alg=none` bypass, weak signing keys
- **Missing MFA**: No multi-factor authentication for privileged accounts
- **Predictable Session IDs**: Sequential or easily guessable tokens

### Remediation Priority
**High** - Change default credentials immediately, enforce strong password policies

## A08:2021 - Software and Data Integrity Failures

### Nuclei Template Tags
- `rce` - Remote Code Execution
- `deserialization` - Insecure deserialization
- `integrity` - Integrity check failures

### Common Findings
- **Insecure Deserialization**: Unsafe object deserialization in Java, Python, PHP
- **Unsigned Updates**: Software updates without signature verification
- **CI/CD Pipeline Compromise**: Insufficient pipeline security controls
- **Dependency Confusion**: Private packages replaced by public malicious packages

### Remediation Priority
**Critical** - Insecure deserialization leading to RCE requires immediate action

## A09:2021 - Security Logging and Monitoring Failures

### Nuclei Template Tags
- `logging` - Logging issues
- `monitoring` - Monitoring gaps

### Common Findings
- **Missing Audit Logs**: Authentication failures, access control violations not logged
- **Insufficient Log Retention**: Logs deleted too quickly for forensic analysis
- **No Alerting**: No real-time alerts for suspicious activities
- **Log Injection**: User input reflected in logs without sanitization

### Remediation Priority
**Low to Medium** - Improve logging and monitoring infrastructure

## A10:2021 - Server-Side Request Forgery (SSRF)

### Nuclei Template Tags
- `ssrf` - SSRF vulnerabilities
- `redirect` - Open redirect issues

### Common Findings
- **SSRF via URL Parameters**: User-controlled URLs fetched by server
- **Cloud Metadata Access**: SSRF accessing AWS/GCP/Azure metadata endpoints
- **Internal Port Scanning**: SSRF used to scan internal networks
- **Webhook Vulnerabilities**: SSRF via webhook URLs

### Remediation Priority
**High to Critical** - Especially if cloud metadata or internal services accessible

## Severity Mapping Guide

Use this table to map Nuclei severity levels to OWASP categories:

| Nuclei Severity | OWASP Priority | Action Required |
|-----------------|----------------|-----------------|
| **Critical** | P0 - Immediate | Patch within 24 hours |
| **High** | P1 - Urgent | Patch within 7 days |
| **Medium** | P2 - Important | Patch within 30 days |
| **Low** | P3 - Normal | Patch in next release cycle |
| **Info** | P4 - Informational | Document and track |

## Integration with Security Workflows

### Finding Triage Process
1. **Critical/High Findings**: Assign to security team immediately
2. **Verify Exploitability**: Confirm with manual testing
3. **Map to OWASP**: Use this guide to categorize findings
4. **Assign Remediation Owner**: Development team or infrastructure team
5. **Track in JIRA/GitHub**: Create tickets with OWASP category labels
6. **Re-scan After Fix**: Verify vulnerability is resolved

### Reporting Template
```markdown
## Security Finding: [Nuclei Template ID]

**OWASP Category**: A03:2021 - Injection
**Severity**: Critical
**CWE**: CWE-89 (SQL Injection)
**CVE**: CVE-2024-XXXXX (if applicable)

### Description
[Description from Nuclei output]

### Affected URLs
- https://target-app.com/api/users?id=1

### Remediation
Use parameterized queries instead of string concatenation.

### References
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
```

## Additional Resources

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [Nuclei Templates Repository](https://github.com/projectdiscovery/nuclei-templates)
