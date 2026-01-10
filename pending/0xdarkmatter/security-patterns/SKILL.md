---
name: security-patterns
description: "Security patterns and OWASP guidelines. Triggers on: security review, OWASP, XSS, SQL injection, CSRF, authentication, authorization, secrets management, input validation, secure coding."
compatibility: "Language-agnostic patterns with framework-specific examples in references."
allowed-tools: "Read Write Bash Grep"
---

# Security Patterns

Essential security patterns for web applications.

## OWASP Top 10 Quick Reference

| Rank | Vulnerability | Prevention |
|------|--------------|------------|
| A01 | Broken Access Control | Check permissions server-side, deny by default |
| A02 | Cryptographic Failures | Use TLS, hash passwords, encrypt sensitive data |
| A03 | Injection | Parameterized queries, validate input |
| A04 | Insecure Design | Threat modeling, secure defaults |
| A05 | Security Misconfiguration | Harden configs, disable unused features |
| A06 | Vulnerable Components | Update dependencies, audit regularly |
| A07 | Auth Failures | MFA, rate limiting, secure session management |
| A08 | Data Integrity Failures | Verify signatures, use trusted sources |
| A09 | Logging Failures | Log security events, protect logs |
| A10 | SSRF | Validate URLs, allowlist destinations |

## Input Validation

```python
# WRONG - Trust user input
def search(query):
    return db.execute(f"SELECT * FROM users WHERE name = '{query}'")

# CORRECT - Parameterized query
def search(query):
    return db.execute("SELECT * FROM users WHERE name = ?", [query])
```

### Validation Rules
```
Always validate:
- Type (string, int, email format)
- Length (min/max bounds)
- Range (numeric bounds)
- Format (regex for patterns)
- Allowlist (known good values)

Never trust:
- URL parameters
- Form data
- HTTP headers
- Cookies
- File uploads
```

## Output Encoding

```javascript
// WRONG - Direct HTML insertion
element.innerHTML = userInput;

// CORRECT - Text content (auto-escapes)
element.textContent = userInput;

// CORRECT - Template with escaping
render(`<div>${escapeHtml(userInput)}</div>`);
```

### Encoding by Context
| Context | Encoding |
|---------|----------|
| HTML body | HTML entity encode |
| HTML attribute | Attribute encode + quote |
| JavaScript | JS encode |
| URL parameter | URL encode |
| CSS | CSS encode |

## Authentication

```python
# Password hashing (use bcrypt, argon2, or scrypt)
import bcrypt

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)
```

### Auth Checklist
- [ ] Hash passwords with bcrypt/argon2 (cost factor 12+)
- [ ] Implement rate limiting on login
- [ ] Use secure session tokens (random, long)
- [ ] Set secure cookie flags (HttpOnly, Secure, SameSite)
- [ ] Implement account lockout after failed attempts
- [ ] Support MFA for sensitive operations

## Authorization

```python
# WRONG - Check only authentication
@login_required
def delete_post(post_id):
    post = Post.get(post_id)
    post.delete()

# CORRECT - Check authorization
@login_required
def delete_post(post_id):
    post = Post.get(post_id)
    if post.author_id != current_user.id and not current_user.is_admin:
        raise Forbidden("Not authorized to delete this post")
    post.delete()
```

## Secrets Management

```bash
# WRONG - Hardcoded secrets
API_KEY = "sk-1234567890abcdef"

# CORRECT - Environment variables
API_KEY = os.environ["API_KEY"]

# BETTER - Secrets manager
API_KEY = secrets_client.get_secret("api-key")
```

### Secret Handling Rules
```
DO:
- Use environment variables or secrets manager
- Rotate secrets regularly
- Use different secrets per environment
- Audit secret access

DON'T:
- Commit secrets to git
- Log secrets
- Include secrets in error messages
- Share secrets in plain text
```

## Security Headers

```
Content-Security-Policy: default-src 'self'; script-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), camera=()
```

## Quick Security Audit

```bash
# Find hardcoded secrets
rg -i "(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]" --type py

# Find SQL injection risks
rg "execute\(f['\"]|format\(" --type py

# Find eval/exec usage
rg "\b(eval|exec)\s*\(" --type py

# Check for TODO security items
rg -i "TODO.*security|FIXME.*security"
```

## Additional Resources

- `./references/owasp-detailed.md` - Full OWASP Top 10 details
- `./references/auth-patterns.md` - JWT, OAuth, session management
- `./references/crypto-patterns.md` - Encryption, hashing, signatures
- `./references/secure-headers.md` - HTTP security headers guide

## Scripts

- `./scripts/security-scan.sh` - Quick security grep patterns
- `./scripts/dependency-audit.sh` - Check for vulnerable dependencies
