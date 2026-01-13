# Security Best Practices Checklist (2025)

Comprehensive security checklist based on OWASP Top 10 2025 and industry standards.

## Input Validation & Sanitization

### User Input
- [ ] All user input is validated (type, format, length)
- [ ] Whitelist validation used over blacklist
- [ ] Input sanitized before processing
- [ ] File uploads restricted (type, size, location)
- [ ] Special characters handled properly

### Data Validation
- [ ] Server-side validation for all inputs (never trust client)
- [ ] Email addresses validated with proper regex
- [ ] Phone numbers validated according to format
- [ ] URLs validated and sanitized
- [ ] JSON/XML input validated against schema

## Authentication & Authorization

### Authentication
- [ ] Passwords hashed with bcrypt, argon2, or scrypt
- [ ] Minimum password requirements enforced (length, complexity)
- [ ] Multi-factor authentication (MFA) available
- [ ] Account lockout after failed attempts
- [ ] Secure session management
- [ ] Password reset functionality secure
- [ ] Credential stuffing protection

### Authorization
- [ ] Principle of least privilege applied
- [ ] Role-based access control (RBAC) implemented
- [ ] Authorization checked on every request
- [ ] Direct object references protected (IDOR prevention)
- [ ] Vertical privilege escalation prevented
- [ ] Horizontal privilege escalation prevented

### Tokens & Sessions
- [ ] JWTs stored in HttpOnly cookies (not localStorage)
- [ ] Session tokens properly randomized
- [ ] Token expiration times appropriate (15 min for JWT)
- [ ] Refresh tokens implemented securely
- [ ] CSRF tokens on state-changing operations
- [ ] Session fixation prevented
- [ ] Secure, SameSite cookies used

## Data Protection

### Encryption
- [ ] HTTPS enforced everywhere (HSTS enabled)
- [ ] TLS 1.3 or 1.2 minimum
- [ ] Sensitive data encrypted at rest
- [ ] Database encryption enabled
- [ ] Secrets encrypted in environment variables
- [ ] Certificate validation proper

### Secrets Management
- [ ] No secrets in source code
- [ ] No secrets in version control
- [ ] Environment variables for configuration
- [ ] Secrets rotation implemented
- [ ] Key management system used
- [ ] API keys properly protected

### Personal Data
- [ ] PII identified and protected
- [ ] Data minimization principle applied
- [ ] GDPR/privacy compliance considered
- [ ] Data retention policies defined
- [ ] Secure data deletion implemented

## Injection Prevention

### SQL Injection
- [ ] Parameterized queries used (never string concatenation)
- [ ] ORM used properly
- [ ] Stored procedures used where appropriate
- [ ] Database user permissions minimal
- [ ] Input validation on all SQL inputs

### XSS (Cross-Site Scripting)
- [ ] Output encoding/escaping implemented
- [ ] Content Security Policy (CSP) headers set
- [ ] React/Vue automatic escaping utilized
- [ ] DangerouslySetInnerHTML avoided or sanitized
- [ ] User-generated content sanitized

### Command Injection
- [ ] Shell commands avoided when possible
- [ ] Input validation on system commands
- [ ] Subprocess calls properly escaped
- [ ] Limited shell access

### Other Injections
- [ ] LDAP injection prevented
- [ ] XML injection prevented
- [ ] NoSQL injection prevented
- [ ] Template injection prevented

## API Security

### Request Security
- [ ] Rate limiting implemented
- [ ] API authentication required
- [ ] API keys rotated regularly
- [ ] CORS configured properly (not allow all)
- [ ] Request size limits enforced

### Response Security
- [ ] Sensitive data not exposed in responses
- [ ] Error messages don't leak information
- [ ] Stack traces hidden in production
- [ ] Proper HTTP status codes used
- [ ] Response headers secured

## Security Headers

### Required Headers
- [ ] `Strict-Transport-Security` (HSTS)
- [ ] `Content-Security-Policy` (CSP)
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY or SAMEORIGIN`
- [ ] `X-XSS-Protection: 1; mode=block`
- [ ] `Referrer-Policy: strict-origin-when-cross-origin`
- [ ] `Permissions-Policy` configured

## Dependencies & Supply Chain

### Package Management
- [ ] Dependencies regularly updated
- [ ] Vulnerable packages identified (npm audit, Snyk)
- [ ] Dependency scanning in CI/CD
- [ ] Lockfiles committed (package-lock.json)
- [ ] Only necessary dependencies included
- [ ] Packages from trusted sources

### Code Security
- [ ] Static analysis security testing (SAST)
- [ ] Dynamic analysis security testing (DAST)
- [ ] Code reviews include security checks
- [ ] Security linting enabled

## Error Handling & Logging

### Error Handling
- [ ] Errors caught and handled properly
- [ ] Default error pages don't leak info
- [ ] Stack traces hidden in production
- [ ] User-friendly error messages
- [ ] Errors logged for monitoring

### Logging
- [ ] Security events logged
- [ ] Sensitive data not logged
- [ ] Log tampering prevented
- [ ] Logs monitored for suspicious activity
- [ ] Log retention policy defined

## Infrastructure Security

### Server Configuration
- [ ] Unnecessary services disabled
- [ ] Default credentials changed
- [ ] Security patches applied
- [ ] Firewall configured properly
- [ ] DDoS protection considered

### Container Security
- [ ] Minimal base images used
- [ ] Containers run as non-root
- [ ] Image scanning implemented
- [ ] Secrets not in images
- [ ] Resource limits set

## Testing & Monitoring

### Security Testing
- [ ] Penetration testing conducted
- [ ] Security automated tests
- [ ] Fuzz testing for inputs
- [ ] Regular security audits

### Monitoring
- [ ] Intrusion detection system (IDS)
- [ ] Security information and event management (SIEM)
- [ ] Anomaly detection
- [ ] Incident response plan

## Web-Specific

### Frontend Security
- [ ] Subresource Integrity (SRI) for CDN resources
- [ ] postMessage validation
- [ ] localStorage/sessionStorage usage secure
- [ ] Client-side validation + server-side validation
- [ ] DOM XSS prevention

### API Endpoints
- [ ] GraphQL query depth limiting
- [ ] GraphQL introspection disabled in production
- [ ] REST API versioning
- [ ] Pagination to prevent data dumps
- [ ] Webhook signature verification

---

*Part of research-agent/researching-best-practices skill*
*Last updated: 2025-01-15*
*Based on: OWASP Top 10 2025, SANS Top 25, CWE*
