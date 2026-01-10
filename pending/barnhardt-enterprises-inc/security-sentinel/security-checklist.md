# Security Pre-Deployment Checklist

Comprehensive security audit checklist. ALL items must be verified before deployment.

---

## Authentication Security

### Password Management
- [ ] Passwords hashed with bcrypt (12+ rounds) or Argon2
- [ ] Password requirements enforced (8+ chars, complexity)
- [ ] Password history maintained (prevent reuse of last 5 passwords)
- [ ] Account lockout after 5 failed login attempts
- [ ] Lockout duration: 15-30 minutes
- [ ] Failed login attempts logged with IP address
- [ ] Password reset requires email verification
- [ ] Password reset tokens expire after 1 hour
- [ ] Password reset tokens are single-use only
- [ ] Old password required when changing password

### Session Management
- [ ] Sessions expire after 24 hours of inactivity
- [ ] Session ID regenerated after login (prevent session fixation)
- [ ] Sessions invalidated on password change
- [ ] Sessions invalidated on logout
- [ ] Concurrent session limit enforced (max 5 active sessions)
- [ ] "Remember me" option creates separate long-lived token
- [ ] Session cookies have `httpOnly` flag
- [ ] Session cookies have `secure` flag (HTTPS only)
- [ ] Session cookies have `sameSite=strict` flag
- [ ] Session storage uses Redis or database (not in-memory for production)

### JWT Tokens
- [ ] JWT secret is cryptographically random (32+ bytes)
- [ ] JWT secret stored in environment variable (not hardcoded)
- [ ] JWT tokens expire after 1-24 hours
- [ ] Refresh tokens used for long-lived sessions
- [ ] Refresh tokens stored in database (revocable)
- [ ] Refresh tokens expire after 30 days
- [ ] JWT algorithm is HS256 or RS256 (not "none")
- [ ] JWT signature verified on every request
- [ ] JWT payload does not contain sensitive data
- [ ] Token revocation mechanism implemented

### Multi-Factor Authentication
- [ ] MFA option available for all users
- [ ] MFA required for admin accounts
- [ ] TOTP (Time-based One-Time Password) supported
- [ ] Backup codes generated and stored (10 codes)
- [ ] Backup codes are hashed before storage
- [ ] MFA setup requires password verification
- [ ] MFA can be disabled only after verification
- [ ] MFA status logged in audit trail

---

## Authorization Security

### Access Control
- [ ] Authorization check on EVERY protected route
- [ ] Authorization check on EVERY API endpoint
- [ ] Authorization check on EVERY Server Action
- [ ] Role-based access control (RBAC) implemented
- [ ] Roles clearly defined (ADMIN, MANAGER, USER, GUEST)
- [ ] Default role is most restrictive (USER or GUEST)
- [ ] Admin actions require ADMIN role
- [ ] No privilege escalation vulnerabilities
- [ ] Resource ownership verified before update/delete
- [ ] 401 Unauthorized returned for unauthenticated requests
- [ ] 403 Forbidden returned for insufficient permissions

### Row-Level Security
- [ ] Database queries filter by user ID (where applicable)
- [ ] Users can only access their own resources
- [ ] Admins can access all resources
- [ ] Shared resources have explicit permissions
- [ ] Organization-scoped resources filtered by organization ID
- [ ] Public resources accessible without authentication

### API Security
- [ ] All API routes require authentication (except public endpoints)
- [ ] API keys are UUIDs (not sequential integers)
- [ ] API rate limiting enforced (see Rate Limiting section)
- [ ] API versioning implemented (/api/v1/)
- [ ] Deprecated API endpoints return 410 Gone

---

## Input Validation

### General Validation
- [ ] ALL user input validated with Zod (or similar)
- [ ] Validation happens on server-side (not just client-side)
- [ ] Email addresses validated and normalized (toLowerCase)
- [ ] URLs validated for http/https protocol only
- [ ] File paths validated (no directory traversal)
- [ ] UUIDs validated with proper format
- [ ] Dates validated and sanitized
- [ ] Phone numbers validated (E.164 format)
- [ ] Strings trimmed and length-limited
- [ ] Numbers have min/max constraints
- [ ] Arrays have min/max length constraints
- [ ] No unvalidated data reaches database

### SQL Injection Prevention
- [ ] ALL database queries use parameterized queries (Drizzle ORM)
- [ ] No raw SQL with string concatenation
- [ ] No user input directly in SQL queries
- [ ] Dynamic table/column names whitelisted (not user input)
- [ ] ORM protects against SQL injection
- [ ] Database user has minimal permissions (not root)

### XSS Prevention
- [ ] React escapes output by default
- [ ] No `dangerouslySetInnerHTML` without DOMPurify
- [ ] User-generated HTML sanitized with DOMPurify
- [ ] No `eval()` or `Function()` with user input
- [ ] No inline JavaScript in HTML
- [ ] Content Security Policy (CSP) header configured
- [ ] `X-XSS-Protection` header set to `1; mode=block`

### Command Injection Prevention
- [ ] No shell commands with user input
- [ ] Use `spawn()` with array arguments (not `exec()`)
- [ ] Shell commands disabled (`shell: false`)
- [ ] File operations use safe APIs (not shell commands)
- [ ] User input whitelisted before system calls

---

## Data Security

### Sensitive Data Protection
- [ ] No secrets in source code
- [ ] No secrets in environment variables committed to git
- [ ] `.env` file in `.gitignore`
- [ ] `.env.example` provided (without real values)
- [ ] API keys loaded from environment variables
- [ ] Database credentials loaded from environment variables
- [ ] Secrets rotated regularly (every 90 days)
- [ ] Secrets encrypted at rest
- [ ] TLS/SSL for data in transit
- [ ] HTTPS enforced in production

### Logging Security
- [ ] No passwords logged
- [ ] No credit card numbers logged
- [ ] No API keys logged
- [ ] No session tokens logged
- [ ] No personally identifiable information (PII) logged
- [ ] Sensitive data redacted in logs
- [ ] Log level set to INFO or WARN in production (not DEBUG)
- [ ] Logs stored securely (restricted access)
- [ ] Logs retained for 30-90 days

### Database Security
- [ ] Database connection uses TLS
- [ ] Database user has minimal permissions
- [ ] Database backups encrypted
- [ ] Database backups tested regularly
- [ ] Sensitive fields encrypted at application level
- [ ] Credit cards tokenized (not stored directly)
- [ ] Social Security Numbers encrypted
- [ ] Compliance with GDPR/CCPA (if applicable)

---

## File Upload Security

### File Validation
- [ ] File size limits enforced (5-10MB for images)
- [ ] File type whitelist (not blacklist)
- [ ] MIME type validated
- [ ] File extension validated
- [ ] File extension matches MIME type
- [ ] Image files processed with sharp (sanitizes metadata)
- [ ] PDF files scanned for malware
- [ ] SVG files not allowed (XSS risk) OR sanitized
- [ ] XML files not allowed (XXE risk) OR entity expansion disabled

### File Storage
- [ ] Uploaded files stored outside web root
- [ ] Uploaded files not executable
- [ ] Uploaded filenames sanitized (no path traversal)
- [ ] Uploaded files have random names (not user-provided)
- [ ] File access requires authentication
- [ ] File access checks ownership
- [ ] File serving uses `Content-Disposition: attachment`
- [ ] File serving sets correct `Content-Type`

---

## Rate Limiting

### Endpoint Protection
- [ ] Login endpoint: 5 attempts per 15 minutes (per IP)
- [ ] Registration endpoint: 3 accounts per hour (per IP)
- [ ] Password reset: 3 attempts per hour (per email)
- [ ] API endpoints: 100-1000 requests per minute (per user/IP)
- [ ] File upload: 10-20 files per hour (per user)
- [ ] Email sending: 10 emails per hour (per user)
- [ ] SMS sending: 5 SMS per hour (per user)

### Rate Limit Responses
- [ ] 429 Too Many Requests returned on rate limit
- [ ] `Retry-After` header included in 429 response
- [ ] `X-RateLimit-Limit` header included
- [ ] `X-RateLimit-Remaining` header included
- [ ] `X-RateLimit-Reset` header included
- [ ] Rate limit key includes IP address or user ID
- [ ] Rate limiter uses Redis (not in-memory for production)

---

## Security Headers

### Required Headers
- [ ] `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY` (or `SAMEORIGIN` if needed)
- [ ] `X-XSS-Protection: 1; mode=block`
- [ ] `Referrer-Policy: strict-origin-when-cross-origin`
- [ ] `Permissions-Policy` configured (disable unused features)
- [ ] Content-Security-Policy (CSP) configured

### CSP Configuration
- [ ] `default-src 'self'`
- [ ] `script-src` allows only trusted domains
- [ ] `style-src` allows only trusted domains
- [ ] `img-src` restricts image sources
- [ ] `connect-src` restricts API endpoints
- [ ] `frame-ancestors 'none'` (or specific origins)
- [ ] `base-uri 'self'`
- [ ] `form-action 'self'`
- [ ] CSP violations reported to endpoint

### CORS Configuration
- [ ] CORS origin whitelist (not `*`)
- [ ] CORS credentials allowed only for whitelisted origins
- [ ] `Access-Control-Allow-Origin` set to specific origin (not `*`)
- [ ] `Access-Control-Allow-Methods` limited to needed methods
- [ ] `Access-Control-Allow-Headers` limited to needed headers
- [ ] `Access-Control-Max-Age` set to 24 hours

---

## Error Handling

### Error Messages
- [ ] Generic error messages in production
- [ ] Detailed errors only in development
- [ ] No stack traces in production responses
- [ ] No database error details in responses
- [ ] No file paths in error messages
- [ ] No internal IP addresses in error messages
- [ ] Login errors don't reveal if email exists
- [ ] Password reset emails sent even if email doesn't exist

### Error Logging
- [ ] All errors logged with context
- [ ] Error logs include timestamp, user ID, IP address
- [ ] Error logs include request method and path
- [ ] Error logs include user agent
- [ ] Critical errors trigger alerts
- [ ] Error rates monitored for anomalies

---

## Dependency Security

### Package Management
- [ ] `npm audit` runs clean (no high/critical vulnerabilities)
- [ ] Dependencies updated regularly (monthly)
- [ ] Automated dependency updates (Dependabot)
- [ ] Lock file (`package-lock.json`) committed
- [ ] `npm ci` used in CI/CD (not `npm install`)
- [ ] Node.js version specified in `package.json`
- [ ] Deprecated packages replaced
- [ ] Unused dependencies removed

### Supply Chain Security
- [ ] Package integrity verified (npm audit signatures)
- [ ] Packages from trusted sources only
- [ ] Package install scripts disabled (`--ignore-scripts`)
- [ ] Subresource Integrity (SRI) for CDN assets
- [ ] Dependencies reviewed before adding

---

## Monitoring and Logging

### Security Events Logged
- [ ] Login attempts (success and failure)
- [ ] Password changes
- [ ] Password reset requests
- [ ] Email changes
- [ ] MFA enable/disable
- [ ] Role changes
- [ ] Permission changes
- [ ] Account deletion
- [ ] Admin actions
- [ ] API key creation/deletion
- [ ] Suspicious activity (unusual IP, unusual time)

### Monitoring
- [ ] Failed login attempts monitored
- [ ] Rate limit violations monitored
- [ ] 4xx/5xx error rates monitored
- [ ] Database query performance monitored
- [ ] API response times monitored
- [ ] Disk space monitored
- [ ] Memory usage monitored
- [ ] CPU usage monitored

### Alerting
- [ ] Alerts configured for critical errors
- [ ] Alerts configured for unusual activity
- [ ] Alerts configured for high error rates
- [ ] Alerts configured for resource exhaustion
- [ ] Alerts sent to on-call team
- [ ] Incident response plan documented

---

## Infrastructure Security

### Server Configuration
- [ ] Firewall configured (only ports 80, 443 open)
- [ ] SSH access key-based (not password)
- [ ] Root login disabled
- [ ] Operating system updated regularly
- [ ] Unnecessary services disabled
- [ ] Security patches applied automatically
- [ ] Server time synchronized (NTP)

### Database Security
- [ ] Database not publicly accessible
- [ ] Database firewall rules configured
- [ ] Database backups encrypted
- [ ] Database connection pooling configured
- [ ] Database slow query log enabled
- [ ] Database audit log enabled

### Network Security
- [ ] HTTPS enforced (redirect HTTP to HTTPS)
- [ ] TLS 1.2 or higher required
- [ ] TLS 1.0 and 1.1 disabled
- [ ] SSL certificate valid and not expired
- [ ] SSL certificate from trusted CA
- [ ] HSTS preload list submission
- [ ] DDoS protection enabled (Cloudflare, AWS Shield)

---

## Compliance

### GDPR (if applicable)
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] Cookie consent banner implemented
- [ ] User data export functionality
- [ ] User data deletion functionality
- [ ] Data processing agreements with vendors
- [ ] Data breach notification plan

### PCI DSS (if handling credit cards)
- [ ] Credit cards not stored (use Stripe, PayPal)
- [ ] If stored: encrypted at rest
- [ ] If stored: encrypted in transit
- [ ] If stored: access logged
- [ ] If stored: regular security audits
- [ ] Tokenization used for recurring payments

---

## Pre-Deployment Final Checks

### Code Review
- [ ] All code reviewed by another developer
- [ ] Security-sensitive code reviewed by security team
- [ ] No TODO or FIXME comments related to security
- [ ] No commented-out security checks
- [ ] No debug code left in production

### Testing
- [ ] Unit tests passing (90%+ coverage for business logic)
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Security tests passing
- [ ] Load tests passing
- [ ] Penetration testing completed (for sensitive apps)

### Documentation
- [ ] API documentation up to date
- [ ] Security practices documented
- [ ] Incident response plan documented
- [ ] Deployment runbook documented
- [ ] Rollback plan documented

### Environment
- [ ] Production environment variables set
- [ ] Secrets rotated for production
- [ ] Database migrations tested
- [ ] Database backups verified
- [ ] Monitoring dashboards configured
- [ ] Alerts configured and tested
- [ ] Error tracking configured (Sentry, etc.)

---

## Post-Deployment

### Verification
- [ ] HTTPS working correctly
- [ ] Security headers verified (securityheaders.com)
- [ ] SSL certificate verified (ssllabs.com)
- [ ] CSP validated (csp-evaluator.withgoogle.com)
- [ ] CORS configuration tested
- [ ] Authentication flows tested
- [ ] Authorization checks verified
- [ ] Rate limiting verified
- [ ] Error pages tested (404, 500, etc.)

### Monitoring
- [ ] Error rates normal
- [ ] Response times normal
- [ ] Resource usage normal
- [ ] No security alerts triggered
- [ ] Logs reviewed for anomalies

---

## Continuous Security

### Regular Tasks
- [ ] Weekly: Review error logs
- [ ] Weekly: Review security alerts
- [ ] Monthly: Update dependencies
- [ ] Monthly: Run npm audit
- [ ] Quarterly: Review access permissions
- [ ] Quarterly: Rotate API keys
- [ ] Quarterly: Security training for team
- [ ] Annually: Penetration testing
- [ ] Annually: Security audit

### Incident Response
- [ ] Incident response plan documented
- [ ] Incident response team identified
- [ ] Incident communication plan
- [ ] Data breach notification procedure
- [ ] Post-incident review process

---

## Summary

**Critical items (MUST be completed):**
1. All passwords hashed with bcrypt (12+ rounds)
2. All user input validated with Zod
3. All protected routes have authorization checks
4. HTTPS enforced in production
5. No secrets in source code
6. Rate limiting on authentication endpoints
7. Security headers configured
8. npm audit passes (no high/critical)
9. All code reviewed
10. All tests passing

**Total checklist items: 250+**

**Deployment approval requires: 100% completion of critical items, 95%+ completion of all items.**
