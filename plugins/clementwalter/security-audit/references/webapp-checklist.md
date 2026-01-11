# Web Application Security Checklist

Based on OWASP Top 10 (2025) and ASVS.

## A01: Broken Access Control

- [ ] Default deny for all resources
- [ ] Deny by resource ID, not just endpoint
- [ ] Server-side authorization checks (not client-only)
- [ ] Disable directory listing
- [ ] Log access control failures
- [ ] Rate limit API access
- [ ] Invalidate JWT/sessions on logout
- [ ] CORS properly configured

## A02: Cryptographic Failures

- [ ] No sensitive data in URLs
- [ ] HTTPS everywhere (HSTS enabled)
- [ ] Strong TLS configuration (TLS 1.2+)
- [ ] Sensitive data encrypted at rest
- [ ] No deprecated crypto (MD5, SHA1, DES)
- [ ] Proper key management
- [ ] Password hashing with modern KDF

## A03: Injection

- [ ] Parameterized queries (no string concat)
- [ ] Input validation (allowlist preferred)
- [ ] Output encoding (context-aware)
- [ ] ORM/query builder used safely
- [ ] No eval() with user input
- [ ] No OS command execution with user input
- [ ] LDAP injection prevention

## A04: Insecure Design

- [ ] Threat model documented
- [ ] Security requirements defined
- [ ] Secure design patterns used
- [ ] Abuse cases tested
- [ ] Rate limiting designed in
- [ ] Segregation of tenants/users

## A05: Security Misconfiguration

- [ ] Hardened server configuration
- [ ] Unnecessary features disabled
- [ ] Default credentials changed
- [ ] Error messages don't leak info
- [ ] Security headers configured
- [ ] Cloud permissions minimal
- [ ] XML external entities disabled

## A06: Vulnerable Components

- [ ] Component inventory maintained
- [ ] Automated vulnerability scanning
- [ ] Only necessary components
- [ ] Official sources only
- [ ] Signed/verified components
- [ ] Patch management process

## A07: Authentication Failures

- [ ] MFA available/enforced
- [ ] No default credentials
- [ ] Weak password prevention
- [ ] Brute force protection
- [ ] Secure password recovery
- [ ] Session IDs rotated on login
- [ ] Session timeout configured

## A08: Data Integrity Failures

- [ ] CI/CD pipeline secured
- [ ] Code/data integrity verified
- [ ] Deserialization safe
- [ ] Update mechanism secured
- [ ] Signed updates where applicable

## A09: Logging & Monitoring

- [ ] Login/access control logged
- [ ] Input validation failures logged
- [ ] Logs don't contain secrets
- [ ] Log injection prevented
- [ ] Alerting configured
- [ ] Incident response ready

## A10: SSRF

- [ ] URL validation (allowlist)
- [ ] No raw redirects with user input
- [ ] Metadata endpoints blocked (169.254.x.x)
- [ ] DNS rebinding prevention
- [ ] Response handling safe

## Security Headers

```text
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), camera=(), microphone=()
```

## Cookie Security

- [ ] HttpOnly flag
- [ ] Secure flag
- [ ] SameSite=Strict or Lax
- [ ] Appropriate expiration
- [ ] No sensitive data in cookies

## API Security

- [ ] Authentication on all endpoints
- [ ] Rate limiting
- [ ] Input validation
- [ ] Output filtering (no over-exposure)
- [ ] Versioning strategy
- [ ] Documentation doesn't expose sensitive details

## File Upload

- [ ] File type validation (magic bytes, not extension)
- [ ] Size limits
- [ ] Stored outside web root
- [ ] Randomized filenames
- [ ] Malware scanning
- [ ] No execution permissions

## Session Management

- [ ] Secure session ID generation
- [ ] Session bound to user agent/IP (optional)
- [ ] Absolute and idle timeout
- [ ] Regenerate on privilege change
- [ ] Secure storage (server-side preferred)
- [ ] Logout invalidates session
