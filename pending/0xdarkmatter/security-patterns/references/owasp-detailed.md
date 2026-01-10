# OWASP Top 10 Detailed Guide

In-depth coverage of OWASP Top 10 2021 vulnerabilities.

## A01: Broken Access Control

### Description
Access control enforces policy such that users cannot act outside their intended permissions.

### Examples
- Bypassing access control by modifying URL, state, or HTML
- Viewing or editing someone else's account
- Privilege escalation (acting as user without login, or user acting as admin)
- Metadata manipulation (replay/tampering JWT, cookies, hidden fields)
- CORS misconfiguration allowing unauthorized API access
- Force browsing to authenticated pages or privileged pages

### Prevention

```python
# WRONG - Client-side check only
if user.role == "admin":
    show_admin_button()

# CORRECT - Server-side enforcement
@app.route("/admin/users")
def admin_users():
    if not current_user.has_role("admin"):
        abort(403)
    return render_template("admin/users.html")

# CORRECT - Deny by default
def get_resource(resource_id):
    resource = Resource.get(resource_id)
    if resource.owner_id != current_user.id:
        raise Forbidden("Not your resource")
    return resource
```

### Checklist
- [ ] Deny by default except for public resources
- [ ] Implement access control once, reuse everywhere
- [ ] Record access control failures, alert on repeated attempts
- [ ] Disable web server directory listing
- [ ] Ensure file metadata not accessible

## A02: Cryptographic Failures

### Description
Failures related to cryptography leading to exposure of sensitive data.

### Examples
- Data transmitted in clear text (HTTP, SMTP, FTP)
- Old/weak cryptographic algorithms (MD5, SHA1, DES)
- Default or weak crypto keys
- Improper certificate validation
- Passwords stored without salted hashing

### Prevention

```python
# WRONG - Weak hashing
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# CORRECT - bcrypt with cost factor
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

# WRONG - ECB mode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
cipher = Cipher(algorithms.AES(key), modes.ECB())

# CORRECT - GCM mode with random IV
cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
```

### Checklist
- [ ] Classify data by sensitivity
- [ ] Don't store sensitive data unnecessarily
- [ ] Encrypt all sensitive data at rest
- [ ] Use TLS for all data in transit
- [ ] Use strong, standard algorithms
- [ ] Store passwords with bcrypt, scrypt, Argon2, or PBKDF2

## A03: Injection

### Description
Hostile data sent to an interpreter as part of a command or query.

### Examples
- SQL Injection
- NoSQL Injection
- OS Command Injection
- LDAP Injection
- XPath Injection
- Template Injection

### Prevention

```python
# WRONG - SQL Injection
query = f"SELECT * FROM users WHERE name = '{name}'"

# CORRECT - Parameterized query
cursor.execute("SELECT * FROM users WHERE name = ?", [name])

# WRONG - Command Injection
os.system(f"ping {host}")

# CORRECT - Use subprocess with list
subprocess.run(["ping", "-c", "4", host], capture_output=True)

# WRONG - Template Injection
template = Template(user_input)

# CORRECT - Safe templating
template = env.get_template("page.html")
template.render(user_data=user_input)
```

### Detection Patterns

```bash
# Find SQL injection risks
rg "execute\(f['\"]|format\(|\.format\(" --type py

# Find command injection
rg "os\.system\(|subprocess\.(run|call|Popen)\([^,\[]*\+" --type py
```

## A04: Insecure Design

### Description
Missing or ineffective security controls from design phase.

### Prevention
- Use threat modeling during design
- Integrate security requirements in user stories
- Use secure design patterns
- Write unit and integration tests for security controls
- Segregate tenants robustly

## A05: Security Misconfiguration

### Description
Missing or improper security hardening across the application stack.

### Examples
- Default accounts enabled
- Unnecessary features enabled
- Error messages revealing stack traces
- Missing security headers
- Out of date software

### Prevention

```yaml
# Secure headers middleware
security_headers:
  Content-Security-Policy: "default-src 'self'"
  X-Frame-Options: "DENY"
  X-Content-Type-Options: "nosniff"
  Strict-Transport-Security: "max-age=31536000"

# Disable debug in production
DEBUG: false
ALLOWED_HOSTS: ["example.com"]
```

## A06: Vulnerable and Outdated Components

### Description
Using components with known vulnerabilities.

### Prevention

```bash
# Python - pip audit
pip install pip-audit
pip-audit

# JavaScript - npm audit
npm audit
npm audit fix

# General - Snyk
snyk test
snyk monitor

# GitHub Dependabot
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

## A07: Identification and Authentication Failures

### Description
Confirmation of user's identity and session management weaknesses.

### Examples
- Permits brute force attacks
- Permits weak passwords
- Weak credential recovery
- Plain text or weakly hashed passwords
- Missing MFA
- Session IDs in URL

### Prevention

```python
# Rate limiting
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    # Login logic

# Secure session configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
)
```

## A08: Software and Data Integrity Failures

### Description
Code and infrastructure without integrity verification.

### Examples
- Insecure CI/CD pipeline
- Auto-update without verification
- Untrusted deserialization

### Prevention

```python
# WRONG - Pickle from untrusted source
import pickle
data = pickle.loads(user_input)  # RCE vulnerability!

# CORRECT - Use JSON for untrusted data
import json
data = json.loads(user_input)

# Verify signatures
import hmac

def verify_webhook(payload, signature, secret):
    expected = hmac.new(secret, payload, 'sha256').hexdigest()
    return hmac.compare_digest(expected, signature)
```

## A09: Security Logging and Monitoring Failures

### Description
Without logging and monitoring, breaches cannot be detected.

### What to Log
- Login successes and failures
- Access control failures
- Input validation failures
- High-value transactions

### Prevention

```python
import logging

security_logger = logging.getLogger("security")

def login(username, password):
    user = authenticate(username, password)
    if user:
        security_logger.info(f"Login success: {username}")
        return user
    else:
        security_logger.warning(f"Login failed: {username}")
        raise AuthenticationError()

# Alert on suspicious patterns
if failed_logins_count > 10:
    security_logger.critical(f"Brute force detected: {ip_address}")
    alert_security_team(ip_address)
```

## A10: Server-Side Request Forgery (SSRF)

### Description
Application fetches remote resource without validating user-supplied URL.

### Examples
- Accessing internal services
- Reading cloud metadata
- Port scanning internal network

### Prevention

```python
# WRONG - Direct URL fetch
import requests

def fetch(url):
    return requests.get(url)  # Can fetch internal URLs!

# CORRECT - Validate URL
from urllib.parse import urlparse

ALLOWED_HOSTS = {"api.example.com", "cdn.example.com"}

def fetch(url):
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("Host not allowed")
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Scheme not allowed")
    return requests.get(url)
```
