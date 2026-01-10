# OWASP Top 10 Security Checklist

Use this checklist to audit applications against OWASP Top 10 vulnerabilities.

---

## 1. Broken Access Control

### Authorization Checks

- [ ] **All protected endpoints require authentication**
- [ ] **Ownership verified before data access** (users can only see their own data)
- [ ] **Role-based access control (RBAC) implemented**
- [ ] **Default deny** (explicit authorization required, not assumed)
- [ ] **IDOR prevention** (insecure direct object references blocked)
- [ ] **Admin functions require admin role**
- [ ] **API endpoints validate permissions**
- [ ] **File uploads restricted by user permissions**

### Testing

- [ ] Try accessing other users' resources by changing IDs
- [ ] Try accessing admin endpoints as regular user
- [ ] Test horizontal privilege escalation (user A → user B)
- [ ] Test vertical privilege escalation (user → admin)

---

## 2. Cryptographic Failures

### Data Encryption

- [ ] **HTTPS enforced** (all traffic uses TLS)
- [ ] **Sensitive data encrypted at rest** (PII, payment info)
- [ ] **Passwords hashed** with bcrypt, argon2, or scrypt
- [ ] **Never store plaintext passwords**
- [ ] **Credit cards not stored** (use tokenization)
- [ ] **TLS 1.2+ only** (no TLS 1.0 or 1.1)
- [ ] **Strong ciphers configured** (no weak ciphers)
- [ ] **Encryption keys rotated** regularly

### Password Hashing

- [ ] **Using bcrypt, argon2, or scrypt** (not MD5, SHA1, or plain SHA256)
- [ ] **Salt automatically handled** by hashing algorithm
- [ ] **Password verification secure** (timing-attack resistant)

---

## 3. Injection

### SQL Injection

- [ ] **Parameterized queries used** (prepared statements)
- [ ] **No string concatenation** in SQL queries
- [ ] **ORMs used correctly** (query builders, not raw SQL)
- [ ] **Database user has least privilege** (not root/admin)

### Command Injection

- [ ] **Avoid system calls** with user input
- [ ] **If unavoidable, use list arguments** (not shell=True)
- [ ] **Input validated with allowlist**
- [ ] **Special characters escaped**

### NoSQL Injection

- [ ] **Query operators sanitized** ($where, $regex, etc.)
- [ ] **Input validated before database queries**

### Testing

- [ ] Test with `' OR '1'='1` in inputs
- [ ] Test with `"; DROP TABLE users;--`
- [ ] Test with `$(whoami)` or backticks in inputs

---

## 4. Insecure Design

### Threat Modeling

- [ ] **Threat model created** for critical features
- [ ] **Security requirements defined** early in design
- [ ] **Attack surface minimized**

### Design Security

- [ ] **Rate limiting on all public endpoints**
- [ ] **CAPTCHA on sensitive operations** (login, password reset, registration)
- [ ] **UUIDs used instead of sequential IDs** for public resources
- [ ] **File upload size limits** enforced
- [ ] **Email verification required** for password reset
- [ ] **Secure by default** (opt-in, not opt-out for security features)

---

## 5. Security Misconfiguration

### Configuration

- [ ] **Debug mode disabled in production**
- [ ] **Default credentials changed** or removed
- [ ] **Unnecessary services disabled**
- [ ] **Error messages generic** (no stack traces in production)
- [ ] **Security headers set** (CSP, X-Frame-Options, HSTS, etc.)
- [ ] **Directory listing disabled**
- [ ] **Unnecessary HTTP methods disabled** (OPTIONS, TRACE)

### Software Updates

- [ ] **Dependencies up to date**
- [ ] **Framework up to date**
- [ ] **Operating system patched**
- [ ] **Automated security updates enabled**

### Secrets Management

- [ ] **No secrets in code** (API keys, passwords)
- [ ] **Environment variables for secrets**
- [ ] **Secrets not in version control** (.env in .gitignore)
- [ ] **Vault or secrets manager used** (AWS Secrets Manager, HashiCorp Vault)

---

## 6. Vulnerable and Outdated Components

### Dependency Management

- [ ] **Dependencies scanned regularly** (npm audit, pip-audit, Snyk)
- [ ] **No known vulnerabilities** in dependencies
- [ ] **Dependencies pinned** in lock files (package-lock.json, Pipfile.lock)
- [ ] **Unused dependencies removed**
- [ ] **Security advisories monitored** (GitHub Dependabot, email alerts)

### Testing

```bash
# Node.js
npm audit
npm audit fix

# Python
pip-audit
safety check

# Ruby
bundle audit
```

---

## 7. Identification and Authentication Failures

### Password Requirements

- [ ] **Minimum 12 characters**
- [ ] **Uppercase and lowercase required**
- [ ] **Numbers and symbols required**
- [ ] **Common passwords blocked** (haveibeenpwned.com API)
- [ ] **Password strength meter shown** to users

### Authentication

- [ ] **Multi-factor authentication (MFA) available**
- [ ] **MFA required for admins**
- [ ] **Rate limiting on login** (5 attempts per 15 minutes)
- [ ] **Account lockout after failed attempts** (temporary or until reset)
- [ ] **Generic error messages** ("Invalid credentials" vs "User not found")
- [ ] **No username enumeration** (same response for valid/invalid emails)

### Session Management

- [ ] **Secure session cookies** (HTTPOnly, Secure, SameSite)
- [ ] **Session timeout after inactivity** (15-30 minutes)
- [ ] **Session invalidated on logout**
- [ ] **Session ID regenerated after login** (prevent session fixation)
- [ ] **Sessions invalidated on password change**

---

## 8. Software and Data Integrity Failures

### Supply Chain Security

- [ ] **CDN scripts use Subresource Integrity (SRI)**
- [ ] **Package signatures verified** (npm, PyPI)
- [ ] **Dependencies from trusted sources**
- [ ] **CI/CD pipeline secured** (signed commits, protected branches)

### Code Integrity

- [ ] **Code review required** for all changes
- [ ] **Signed commits enforced** (GPG signatures)
- [ ] **Branch protection rules** (require reviews, passing tests)
- [ ] **Deployment from trusted sources** (not developer laptops)

---

## 9. Security Logging and Monitoring Failures

### Logging

- [ ] **Security events logged** (login, logout, failed auth, authorization failures)
- [ ] **Logs centralized** (ELK, Splunk, CloudWatch)
- [ ] **Logs contain context** (user ID, IP, timestamp, action)
- [ ] **Sensitive data not logged** (passwords, tokens, credit cards)
- [ ] **Log retention policy defined** (at least 90 days)

### Monitoring

- [ ] **Alerts configured** for suspicious patterns (failed logins, unusual access)
- [ ] **SIEM integration** (Security Information and Event Management)
- [ ] **Anomaly detection** enabled
- [ ] **Regular log reviews** scheduled

### Testing

- [ ] Verify login attempts are logged
- [ ] Verify failed authorization is logged
- [ ] Verify sensitive data is NOT logged

---

## 10. Server-Side Request Forgery (SSRF)

### URL Validation

- [ ] **User-provided URLs validated**
- [ ] **Domain allowlist enforced**
- [ ] **Internal IPs blocked** (127.0.0.1, 10.0.0.0/8, 192.168.0.0/16, 169.254.0.0/16)
- [ ] **Redirects disabled or validated**
- [ ] **Timeout set on external requests**

### Network Segmentation

- [ ] **External services isolated** from internal network
- [ ] **Firewall rules prevent SSRF**
- [ ] **Internal services not accessible from application**

### Testing

- [ ] Test with `http://localhost:8080/admin`
- [ ] Test with `http://169.254.169.254/` (AWS metadata)
- [ ] Test with `http://10.0.0.1` (internal network)

---

## Additional Security Checks

### Cross-Site Scripting (XSS)

- [ ] **Output encoding** for all user-generated content
- [ ] **Content Security Policy (CSP)** header set
- [ ] **DOMPurify or similar** for HTML sanitization
- [ ] **No eval(), innerHTML with user data**

### Cross-Site Request Forgery (CSRF)

- [ ] **CSRF tokens on all state-changing operations**
- [ ] **SameSite cookie attribute** set to Strict or Lax
- [ ] **Double-submit cookie pattern** (if stateless)

### Clickjacking

- [ ] **X-Frame-Options: DENY** or SAMEORIGIN
- [ ] **CSP frame-ancestors** directive set

### Security Headers

- [ ] **Content-Security-Policy**
- [ ] **X-Content-Type-Options: nosniff**
- [ ] **X-Frame-Options: DENY**
- [ ] **Strict-Transport-Security** (HSTS)
- [ ] **Referrer-Policy: no-referrer** or strict-origin
- [ ] **Permissions-Policy** (formerly Feature-Policy)

---

## Pre-Production Checklist

Before deploying:

- [ ] **Security scan completed** (Burp Suite, OWASP ZAP)
- [ ] **Dependency vulnerabilities resolved**
- [ ] **All tests passing** (including security tests)
- [ ] **Secrets rotated** (API keys, database passwords)
- [ ] **Monitoring alerts configured**
- [ ] **Incident response plan** documented
- [ ] **Backup and recovery tested**

---

## Continuous Security

- [ ] **Weekly dependency scans** (automated)
- [ ] **Monthly security reviews**
- [ ] **Quarterly penetration tests**
- [ ] **Yearly security audit** (external)
- [ ] **Bug bounty program** (optional)

---

**Checklist Version**: 1.0.0
**Skill**: security-checklist v1.0.0
**Last Updated**: 2025-10-31
