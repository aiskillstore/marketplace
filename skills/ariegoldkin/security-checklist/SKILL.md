---
name: security-checklist
description: Use this skill when implementing security measures or conducting security audits. Provides OWASP Top 10 mitigations, authentication patterns, input validation strategies, and compliance guidelines. Ensures applications are secure against common vulnerabilities.
version: 1.0.0
author: AI Agent Hub
tags: [security, owasp, authentication, compliance, vulnerabilities]
---

# Security Checklist

## Overview

This skill provides comprehensive security guidance for building secure applications. Whether performing a security audit, implementing new features, or hardening existing systems, this framework helps identify and mitigate common vulnerabilities.

**When to use this skill:**
- Conducting security audits or reviews
- Implementing authentication and authorization
- Validating and sanitizing user input
- Handling sensitive data (PII, credentials, payment info)
- Ensuring compliance (GDPR, HIPAA, SOC2)
- Preparing for security assessments or penetration tests
- Reviewing third-party dependencies for vulnerabilities

## Required Tools

This skill requires the following tools to be installed on your system:

### For JavaScript/TypeScript Projects
- **Node.js 18+** with npm
- **Command:** `npm audit`
- **Install:** Node.js comes with npm pre-installed

### For Python Projects
- **Python 3.8+** with pip
- **pip-audit:** Security scanner for Python dependencies
  - **Install:** `pip install pip-audit`
  - **Command:** `pip-audit`

### Optional (Advanced Security Scanning)
- **Semgrep:** Static analysis tool
  - **Install (macOS):** `brew install semgrep`
  - **Install (pip):** `pip install semgrep`
  - **Command:** `semgrep --config=auto .`

- **Bandit:** Python security linter
  - **Install:** `pip install bandit`
  - **Command:** `bandit -r .`

- **TruffleHog:** Secrets detection
  - **Install (macOS):** `brew install trufflesecurity/trufflehog/trufflehog`
  - **Install (Go):** `go install github.com/trufflesecurity/trufflehog/v3@latest`
  - **Command:** `trufflehog filesystem .`

### Installation Verification
```bash
# Verify Node.js & npm
node --version
npm --version

# Verify Python & pip
python --version
pip --version

# Verify pip-audit
pip-audit --version

# Verify optional tools
semgrep --version
bandit --version
trufflehog --version
```

**Note:** The skill will automatically detect which tools are available and use appropriate commands for your project type.

## Security Principles

### Defense in Depth
- Multiple layers of security controls
- Assume each layer can fail, design redundancy
- Security at database, application, network, and infrastructure levels

### Least Privilege
- Grant minimum permissions necessary
- Separate read/write database accounts
- Service accounts with limited scope

### Fail Securely
- Errors don't expose sensitive information
- Authentication failures don't reveal if user exists
- Rate limiting prevents brute force attacks

### Don't Trust User Input
- **All** input is untrusted until validated
- Validate, sanitize, and escape
- Apply principle to query params, headers, cookies, POST data

---

## OWASP Top 10 (2021 Edition)

### 1. Broken Access Control

**Vulnerability**: Users can access resources they shouldn't.

**Examples:**
```python
# ❌ Bad: No authorization check
@app.route('/api/users/<user_id>')
def get_user(user_id):
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ Good: Verify user can access this resource
@app.route('/api/users/<user_id>')
@login_required
def get_user(user_id):
    current_user = get_current_user()
    if current_user.id != user_id and not current_user.is_admin:
        abort(403, "Forbidden")
    return db.query("SELECT * FROM users WHERE id = ?", [user_id])
```

**Mitigations:**
- Deny by default (require explicit authorization)
- Enforce ownership checks (users can only access their own data)
- Implement RBAC (Role-Based Access Control)
- Test for IDOR (Insecure Direct Object References)
- Log access control failures

---

### 2. Cryptographic Failures

**Vulnerability**: Sensitive data exposed due to weak or missing encryption.

**Examples:**
```python
# ❌ Bad: Storing passwords in plaintext
user.password = request.form['password']

# ✅ Good: Hashing passwords with bcrypt
from bcrypt import hashpw, gensalt

hashed = hashpw(password.encode('utf-8'), gensalt())
user.password_hash = hashed

# ❌ Bad: Using weak hashing (MD5, SHA1)
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# ✅ Good: Using strong hashing (bcrypt, argon2, scrypt)
from argon2 import PasswordHasher

ph = PasswordHasher()
password_hash = ph.hash(password)
```

**Mitigations:**
- Use TLS/HTTPS for all traffic (enforce, not optional)
- Hash passwords with bcrypt, argon2, or scrypt
- Encrypt sensitive data at rest (PII, payment info)
- Never store credit card numbers (use tokenization)
- Use strong random number generators (`secrets` module in Python)
- Rotate encryption keys regularly

---

### 3. Injection (SQL, NoSQL, Command, LDAP)

**Vulnerability**: Untrusted data sent to an interpreter as part of a command.

**SQL Injection:**
```python
# ❌ Bad: String concatenation (vulnerable to SQL injection)
query = f"SELECT * FROM users WHERE email = '{email}'"
db.execute(query)

# ✅ Good: Parameterized queries
query = "SELECT * FROM users WHERE email = ?"
db.execute(query, [email])
```

**Command Injection:**
```python
# ❌ Bad: Shell=True with user input
import subprocess
filename = request.form['filename']
subprocess.run(f"cat {filename}", shell=True)

# ✅ Good: Avoid shell, use list arguments
subprocess.run(["cat", filename], shell=False)
```

**Mitigations:**
- Use parameterized queries (prepared statements)
- Use ORMs with proper query builders
- Validate and sanitize all input
- Avoid `eval()`, `exec()`, shell=True
- Use allowlists for permitted values
- Escape special characters in dynamic queries

---

### 4. Insecure Design

**Vulnerability**: Design flaws that can't be fixed with implementation.

**Examples:**
- No rate limiting on login/password reset
- Unlimited file upload sizes
- Sequential or guessable IDs
- Password reset without account verification

**Mitigations:**
- Threat modeling during design phase
- Rate limiting on all public endpoints
- Use UUIDs instead of sequential IDs for public resources
- Require email verification for password resets
- Implement CAPTCHA for sensitive operations
- Design for secure defaults (opt-in, not opt-out)

---

### 5. Security Misconfiguration

**Vulnerability**: Default configs, incomplete setups, verbose errors.

**Examples:**
```python
# ❌ Bad: Debug mode in production
app.debug = True

# ✅ Good: Debug mode only in development
app.debug = os.getenv('FLASK_ENV') == 'development'

# ❌ Bad: Verbose error messages
@app.errorhandler(Exception)
def handle_error(e):
    return str(e), 500  # Exposes stack traces

# ✅ Good: Generic error messages
@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"Error: {e}")
    return {"error": "Internal server error"}, 500
```

**Mitigations:**
- Disable debug mode in production
- Remove default credentials
- Close unnecessary ports and services
- Set security headers (CSP, X-Frame-Options, HSTS)
- Keep software updated (dependencies, frameworks, OS)
- Use environment variables for secrets (not hardcoded)

---

### 6. Vulnerable and Outdated Components

**Vulnerability**: Using libraries with known vulnerabilities.

**Mitigations:**
```bash
# Check for vulnerabilities
npm audit
npm audit fix

# Python
pip-audit
safety check
```

**Best Practices:**
- Pin dependency versions in lock files
- Scan dependencies regularly (CI/CD integration)
- Subscribe to security advisories (GitHub Dependabot, Snyk)
- Update dependencies regularly (monthly at minimum)
- Remove unused dependencies

---

### 7. Identification and Authentication Failures

**Vulnerability**: Weak authentication, credential stuffing, session hijacking.

**Examples:**
```python
# ❌ Bad: Weak password requirements
if len(password) < 6:
    return "Password too short"

# ✅ Good: Strong password requirements
import re

def validate_password(password):
    if len(password) < 12:
        return "Password must be at least 12 characters"
    if not re.search(r"[A-Z]", password):
        return "Password must contain uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain lowercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain a number"
    return None  # Valid
```

**Mitigations:**
- Require strong passwords (12+ chars, mixed case, numbers, symbols)
- Implement multi-factor authentication (MFA)
- Rate limit login attempts (5 attempts per 15 minutes)
- Use secure session management (HTTPOnly, Secure, SameSite cookies)
- Invalidate sessions after logout or inactivity
- Don't reveal whether email exists during password reset
- Implement account lockout after failed attempts

---

### 8. Software and Data Integrity Failures

**Vulnerability**: Code or infrastructure updates without integrity verification.

**Examples:**
- Loading libraries from untrusted CDNs
- No verification of CI/CD pipeline artifacts
- Auto-update without signature verification

**Mitigations:**
- Use Subresource Integrity (SRI) for CDN scripts
```html
<script src="https://cdn.example.com/lib.js"
        integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
        crossorigin="anonymous"></script>
```
- Verify package signatures (npm, PyPI)
- Review code changes before deployment
- Use signed commits and releases

---

### 9. Security Logging and Monitoring Failures

**Vulnerability**: Insufficient logging prevents detection of breaches.

**Examples:**
```python
# ❌ Bad: No logging
@app.route('/login', methods=['POST'])
def login():
    user = authenticate(email, password)
    return {"token": create_token(user)}

# ✅ Good: Log security events
import logging

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    user = authenticate(email, password)

    if user:
        logger.info(f"Successful login: {email}")
        return {"token": create_token(user)}
    else:
        logger.warning(f"Failed login attempt: {email}")
        return {"error": "Invalid credentials"}, 401
```

**Mitigations:**
- Log all authentication events (login, logout, failed attempts)
- Log authorization failures (403 errors)
- Log input validation failures
- Log security-relevant events (password changes, MFA changes)
- Centralize logs (ELK, Splunk, CloudWatch)
- Set up alerts for suspicious patterns
- **Never log passwords, tokens, or sensitive data**

---

### 10. Server-Side Request Forgery (SSRF)

**Vulnerability**: Application fetches remote resources without validating URL.

**Examples:**
```python
# ❌ Bad: Fetching user-provided URL without validation
import requests

@app.route('/fetch')
def fetch():
    url = request.args.get('url')
    response = requests.get(url)  # Can access internal services!
    return response.text

# ✅ Good: Validate URL and use allowlist
from urllib.parse import urlparse

ALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com']

@app.route('/fetch')
def fetch():
    url = request.args.get('url')
    parsed = urlparse(url)

    if parsed.hostname not in ALLOWED_DOMAINS:
        abort(400, "Invalid domain")

    response = requests.get(url, timeout=5)
    return response.text
```

**Mitigations:**
- Validate and sanitize all URLs
- Use allowlist of permitted domains
- Disable redirects or validate redirect targets
- Block access to internal IPs (127.0.0.1, 10.0.0.0/8, 192.168.0.0/16)
- Network segmentation (separate internal and external services)

---

## Authentication & Authorization

### Password Security

```python
# ✅ Secure password hashing
from argon2 import PasswordHasher

ph = PasswordHasher()

# Hashing
password_hash = ph.hash(password)

# Verification
try:
    ph.verify(password_hash, password)
    # Password correct
except:
    # Password incorrect
    pass
```

**Requirements:**
- Minimum 12 characters
- Mix of upper/lowercase, numbers, symbols
- No common passwords (use [haveibeenpwned](https://haveibeenpwned.com/API/v3))
- Bcrypt, Argon2, or scrypt for hashing
- Salt automatically handled by these algorithms

### Session Management

```python
# ✅ Secure session cookies
app.config['SESSION_COOKIE_SECURE'] = True      # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True    # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
```

### JWT Tokens

```python
import jwt
from datetime import datetime, timedelta

# ✅ Secure JWT generation
def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1),  # Expiration
        'iat': datetime.utcnow(),  # Issued at
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# ✅ Secure JWT verification
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
```

---

## Input Validation & Sanitization

### Validation

```python
# ✅ Allowlist validation
def validate_sort_column(column):
    allowed_columns = ['name', 'email', 'created_at']
    if column not in allowed_columns:
        raise ValueError("Invalid sort column")
    return column

# ✅ Type validation
from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    email: EmailStr
    name: constr(min_length=2, max_length=100)
    age: int = Field(ge=0, le=150)

# Usage
try:
    user = UserCreate(**request.json)
except ValidationError as e:
    return {"errors": e.errors()}, 400
```

### Sanitization

```python
# ✅ HTML escaping
from markupsafe import escape

@app.route('/comment', methods=['POST'])
def create_comment():
    content = escape(request.form['content'])
    db.execute("INSERT INTO comments (content) VALUES (?)", [content])
    return {"status": "ok"}
```

---

## Security Headers

```python
# ✅ Set security headers
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

---

## 🔍 Automated Security Scanning (v3.5.0)

### Overview

Automated security scanning catches vulnerabilities early. This section teaches agents HOW to run security tools and record evidence.

**When to auto-scan:**
- Before marking code review as complete
- After installing/updating dependencies
- During CI/CD pipeline execution
- When adding new external integrations
- Before production deployments

### Scanning Workflow

```
1. Identify Scan Type (dependencies, code, configuration)
2. Run Appropriate Tool (npm audit, pip-audit, semgrep)
3. Capture Results (exit codes, vulnerability counts)
4. Record Evidence in Context
5. Escalate Critical Findings
```

---

### 1. Dependency Vulnerability Scanning

#### JavaScript/TypeScript (NPM)

```bash
# Run npm audit and capture results
npm audit --json > security-audit.json
EXIT_CODE=$?

# Check exit code
if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ No vulnerabilities found"
else
  echo "⚠️ Vulnerabilities detected (exit code: $EXIT_CODE)"
fi

# Parse for critical/high vulnerabilities
CRITICAL=$(npm audit --json | jq '.metadata.vulnerabilities.critical')
HIGH=$(npm audit --json | jq '.metadata.vulnerabilities.high')

if [ "$CRITICAL" -gt 0 ] || [ "$HIGH" -gt 0 ]; then
  echo "🚨 CRITICAL: $CRITICAL critical, $HIGH high severity vulnerabilities"
fi
```

**Record evidence:**
```javascript
context.quality_evidence = context.quality_evidence || { last_updated: new Date().toISOString() };
context.quality_evidence.security_scan = {
  executed: true,
  tool: 'npm audit',
  critical: 2,
  high: 5,
  moderate: 10,
  low: 3,
  timestamp: new Date().toISOString()
};
context.writeContext();
```

#### Python (pip-audit / safety)

```bash
# Using pip-audit (official tool)
pip-audit --format=json > security-audit.json
EXIT_CODE=$?

# Alternative: using safety
safety check --json > security-audit.json

# Check for critical vulnerabilities
CRITICAL_COUNT=$(cat security-audit.json | jq '[.vulnerabilities[] | select(.severity == "critical")] | length')
```

**Evidence recording:**
```python
# Record in context
context['quality_evidence'] = context.get('quality_evidence', {})
context['quality_evidence']['security_scan'] = {
    'executed': True,
    'tool': 'pip-audit',
    'critical': critical_count,
    'high': high_count,
    'moderate': moderate_count,
    'low': low_count,
    'timestamp': datetime.now().isoformat()
}
```

---

### 2. Static Code Analysis (SAST)

#### Semgrep (Multi-language)

```bash
# Run Semgrep with security rules
semgrep --config=auto --json > semgrep-results.json
EXIT_CODE=$?

# Count findings by severity
CRITICAL=$(cat semgrep-results.json | jq '[.results[] | select(.extra.severity == "ERROR")] | length')
HIGH=$(cat semgrep-results.json | jq '[.results[] | select(.extra.severity == "WARNING")] | length')
```

**Common security patterns detected:**
- SQL Injection
- XSS (Cross-Site Scripting)
- Command Injection
- Path Traversal
- Hardcoded secrets
- Insecure cryptography

#### Bandit (Python)

```bash
# Run Bandit for Python security issues
bandit -r . -f json -o bandit-report.json
EXIT_CODE=$?

# Count high/medium severity issues
HIGH=$(cat bandit-report.json | jq '[.results[] | select(.issue_severity == "HIGH")] | length')
MEDIUM=$(cat bandit-report.json | jq '[.results[] | select(.issue_severity == "MEDIUM")] | length')
```

---

### 3. Secret Detection

#### TruffleHog / Gitleaks

```bash
# Scan for secrets in git history
trufflehog git file://. --json > secrets-scan.json

# Check if any secrets found
SECRET_COUNT=$(cat secrets-scan.json | jq '. | length')

if [ "$SECRET_COUNT" -gt 0 ]; then
  echo "🚨 CRITICAL: $SECRET_COUNT secrets detected!"
  # Extract types
  cat secrets-scan.json | jq -r '.[] | .DetectorType' | sort | uniq
fi
```

**Common secrets detected:**
- AWS API keys
- GitHub tokens
- Private keys (RSA, SSH)
- Database credentials
- API keys (Stripe, Twilio, etc.)

---

### 4. Container Security (Docker)

```bash
# Scan Docker images with Trivy
trivy image myapp:latest --format json > trivy-scan.json

# Count vulnerabilities
CRITICAL=$(cat trivy-scan.json | jq '[.Results[].Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length')
HIGH=$(cat trivy-scan.json | jq '[.Results[].Vulnerabilities[]? | select(.Severity == "HIGH")] | length')
```

---

### 5. Evidence Recording Template

After running security scans, record evidence in shared context:

```typescript
import { ContextManager } from '../lib/context/context-manager.js';

const context = new ContextManager();

// Record security scan evidence
context.recordSecurityScanEvidence({
  executed: true,
  tool: 'npm audit + semgrep',
  critical: 2,
  high: 5,
  moderate: 10,
  low: 3,
  timestamp: new Date().toISOString(),
  scan_details: {
    dependency_scan: {
      tool: 'npm audit',
      critical: 2,
      high: 3,
      vulnerabilities: [
        { id: 'GHSA-xxxx', severity: 'critical', package: 'lodash@4.17.19' }
      ]
    },
    code_scan: {
      tool: 'semgrep',
      critical: 0,
      high: 2,
      patterns: ['sql-injection', 'xss']
    }
  }
});
```

---

### 6. Critical Threshold Escalation

**MANDATORY: Escalate if critical/high vulnerabilities found**

```javascript
// After scanning
const securityEvidence = context.getQualityEvidence()?.security_scan;

if (!securityEvidence) {
  console.log('⚠️ WARNING: No security scan performed');
  return;
}

// Check for critical/high vulnerabilities
if (securityEvidence.critical > 0 || securityEvidence.high > 5) {
  console.log('🚨 SECURITY ALERT: Critical vulnerabilities detected');

  // BLOCK deployment
  const blockingReasons = [];

  if (securityEvidence.critical > 0) {
    blockingReasons.push(`${securityEvidence.critical} CRITICAL vulnerabilities`);
  }

  if (securityEvidence.high > 5) {
    blockingReasons.push(`${securityEvidence.high} HIGH vulnerabilities (>5 threshold)`);
  }

  // Escalate to user
  console.log('BLOCKED: ' + blockingReasons.join(', '));
  console.log('Action Required: Fix critical/high vulnerabilities before proceeding');

  return { approved: false, blockingReasons };
}

console.log('✅ Security scan passed');
```

**Escalation Thresholds:**
- **CRITICAL**: Any critical vulnerability → BLOCK
- **HIGH**: >5 high severity vulnerabilities → BLOCK
- **MODERATE**: >20 moderate vulnerabilities → WARNING
- **LOW**: >50 low vulnerabilities → WARNING

---

### 7. Auto-Scan Checklist

Use this checklist when performing security reviews:

```markdown
## Security Scan Checklist

- [ ] **Dependency Scan**: npm audit / pip-audit executed
- [ ] **Exit Code Captured**: 0 = clean, non-zero = vulnerabilities
- [ ] **Severity Counts**: Critical, High, Moderate, Low recorded
- [ ] **Evidence Recorded**: Added to context.quality_evidence.security_scan
- [ ] **Critical Threshold Check**: BLOCK if critical > 0 or high > 5
- [ ] **Scan Results Saved**: JSON output saved for review
- [ ] **False Positives Noted**: Known safe issues documented
- [ ] **Fix Recommendations**: Upgrade paths or mitigations documented
```

---

### 8. Integration with Code Quality Reviewer

When Code Quality Reviewer agent performs review:

```markdown
1. Run linter/type checker (already implemented)
2. **AUTO-TRIGGER**: Run security scan
   - npm audit (for JS/TS projects)
   - pip-audit (for Python projects)
3. Capture and record evidence
4. Check critical thresholds
5. BLOCK approval if critical vulnerabilities found
6. Include security scan summary in review output
```

**Example output:**
```
## Code Quality Review

### Lint & Type Check: ✅ PASS
- ESLint: 0 errors, 2 warnings
- TypeScript: 0 errors

### Security Scan: ⚠️ WARNING
- Tool: npm audit
- Critical: 0
- High: 3
- Moderate: 8
- Low: 2

**Recommendation**: 3 high severity vulnerabilities detected. Run `npm audit fix` to address:
- lodash@4.17.19 (Prototype Pollution - High)
- minimist@1.2.5 (Prototype Pollution - High)
- axios@0.21.1 (SSRF - High)

### Overall Status: BLOCKED
Security vulnerabilities must be resolved before approval.
```

---

### 9. Tool Installation Guide

**JavaScript/TypeScript:**
```bash
# npm audit (built-in, no install needed)
npm audit

# Semgrep
pip install semgrep

# TruffleHog
docker run --rm trufflesecurity/trufflehog:latest
```

**Python:**
```bash
# pip-audit (official tool)
pip install pip-audit

# safety
pip install safety

# Bandit
pip install bandit
```

**General:**
```bash
# Trivy (containers, dependencies, code)
brew install aquasecurity/trivy/trivy

# Gitleaks (secrets)
brew install gitleaks
```

---

## Compliance

### GDPR (General Data Protection Regulation)

- [ ] **Data Inventory**: Know what personal data you collect
- [ ] **Lawful Basis**: Have legal basis for processing (consent, contract, etc.)
- [ ] **Privacy Policy**: Clear, accessible privacy policy
- [ ] **User Rights**: Implement data access, deletion, portability
- [ ] **Data Minimization**: Collect only necessary data
- [ ] **Breach Notification**: Process for reporting breaches within 72 hours

### SOC 2 (Service Organization Control)

- [ ] **Access Controls**: Role-based access, MFA, least privilege
- [ ] **Encryption**: Data encrypted at rest and in transit
- [ ] **Logging & Monitoring**: Audit logs for all security events
- [ ] **Incident Response**: Documented incident response plan
- [ ] **Vendor Management**: Third-party security assessments

---

## Integration with Agents

### Code Quality Reviewer
- Applies security checklist during code reviews
- Identifies SQL injection, XSS, and other vulnerabilities
- Validates authentication and authorization patterns

### Backend System Architect
- Designs systems with security in mind (defense in depth)
- Plans for least privilege access
- Implements rate limiting and DDOS protection

### Frontend UI Developer
- Implements CSP headers
- Prevents XSS through output encoding
- Validates input on client-side (with server-side validation)

---

## Quick Start Checklist

When securing an application:

- [ ] All input validated and sanitized
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (output encoding)
- [ ] CSRF protection enabled
- [ ] HTTPS enforced (no HTTP in production)
- [ ] Security headers set (CSP, X-Frame-Options, HSTS)
- [ ] Passwords hashed with bcrypt/argon2
- [ ] Rate limiting on sensitive endpoints
- [ ] Authentication required for protected routes
- [ ] Authorization checks on all data access
- [ ] Secrets in environment variables (not code)
- [ ] Dependencies scanned for vulnerabilities
- [ ] Error messages don't leak information
- [ ] Logging enabled for security events
- [ ] MFA available for users

---

**Skill Version**: 1.0.0
**Last Updated**: 2025-10-31
**Maintained by**: AI Agent Hub Team
