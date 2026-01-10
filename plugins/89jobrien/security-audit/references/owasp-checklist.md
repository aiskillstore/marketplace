---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: security-audit
---

# OWASP Top 10 Security Checklist

Quick reference for OWASP Top 10 (2021) vulnerability categories.

## A01: Broken Access Control

- [ ] Verify authorization on all endpoints
- [ ] Check for IDOR vulnerabilities
- [ ] Validate role-based access controls
- [ ] Test for privilege escalation
- [ ] Verify JWT/session token handling

## A02: Cryptographic Failures

- [ ] Check for sensitive data in transit (TLS 1.2+)
- [ ] Verify encryption at rest for sensitive data
- [ ] Review password hashing (bcrypt, Argon2)
- [ ] Check for hardcoded secrets/keys
- [ ] Validate certificate handling

## A03: Injection

- [ ] SQL injection (parameterized queries)
- [ ] Command injection (input sanitization)
- [ ] XSS (output encoding)
- [ ] LDAP injection
- [ ] NoSQL injection

## A04: Insecure Design

- [ ] Threat modeling completed
- [ ] Security requirements defined
- [ ] Attack surface minimized
- [ ] Defense in depth applied
- [ ] Fail-secure defaults

## A05: Security Misconfiguration

- [ ] Default credentials changed
- [ ] Unnecessary features disabled
- [ ] Error handling doesn't leak info
- [ ] Security headers configured
- [ ] Cloud permissions least-privilege

## A06: Vulnerable Components

- [ ] Dependency audit (npm audit, pip-audit)
- [ ] No known CVEs in dependencies
- [ ] Components up to date
- [ ] Unused dependencies removed
- [ ] License compliance checked

## A07: Authentication Failures

- [ ] Strong password policy enforced
- [ ] MFA available/required
- [ ] Account lockout implemented
- [ ] Session management secure
- [ ] Password recovery secure

## A08: Software and Data Integrity

- [ ] CI/CD pipeline secured
- [ ] Code signing implemented
- [ ] Dependency integrity verified
- [ ] Serialization safe
- [ ] Update mechanism secure

## A09: Security Logging and Monitoring

- [ ] Authentication events logged
- [ ] Authorization failures logged
- [ ] Input validation failures logged
- [ ] Logs protected from tampering
- [ ] Alerting configured

## A10: Server-Side Request Forgery (SSRF)

- [ ] URL validation on user input
- [ ] Allowlist for external requests
- [ ] Internal network access blocked
- [ ] Response handling secure
- [ ] Cloud metadata endpoints blocked

## CVSS Scoring Reference

| Severity | Score Range | Response Time |
|----------|-------------|---------------|
| Critical | 9.0 - 10.0  | Immediate     |
| High     | 7.0 - 8.9   | 24-48 hours   |
| Medium   | 4.0 - 6.9   | 1-2 weeks     |
| Low      | 0.1 - 3.9   | Next release  |

## Common CWE References

- CWE-79: Cross-site Scripting (XSS)
- CWE-89: SQL Injection
- CWE-287: Improper Authentication
- CWE-352: Cross-Site Request Forgery (CSRF)
- CWE-434: Unrestricted File Upload
- CWE-502: Deserialization of Untrusted Data
- CWE-611: XML External Entity (XXE)
- CWE-798: Use of Hard-coded Credentials
- CWE-862: Missing Authorization
- CWE-918: Server-Side Request Forgery (SSRF)
