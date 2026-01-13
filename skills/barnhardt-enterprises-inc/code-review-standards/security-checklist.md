# Security Checklist

For complete security patterns, see: [security-sentinel skill](../security-sentinel/SKILL.md)

## OWASP Top 10 Quick Checklist

### 1. Injection Attacks
- [ ] No SQL string concatenation (use Drizzle ORM)
- [ ] No command injection (no `exec()` with user input)
- [ ] No NoSQL injection (validate with Zod)

### 2. Broken Authentication
- [ ] Passwords hashed with bcrypt (12+ rounds)
- [ ] JWTs use strong secret from environment
- [ ] Session tokens cryptographically secure
- [ ] Cookies have HttpOnly, Secure, SameSite flags

### 3. Sensitive Data Exposure
- [ ] No hardcoded secrets (use environment variables)
- [ ] Sensitive data not logged (passwords, credit cards)
- [ ] Passwords excluded from API responses
- [ ] HTTPS enforced in production

### 4. XML External Entities (XXE)
- [ ] External entities disabled in XML parsers

### 5. Broken Access Control
- [ ] Authentication checked on protected routes
- [ ] Authorization enforced (resource ownership)
- [ ] No IDOR vulnerabilities (insecure direct object reference)

### 6. Security Misconfiguration
- [ ] CORS allows specific origins only
- [ ] Error messages don't leak internal details
- [ ] Security headers set (CSP, X-Frame-Options, etc.)
- [ ] Dependencies up to date (`npm audit`)

### 7. Cross-Site Scripting (XSS)
- [ ] No dangerouslySetInnerHTML without DOMPurify
- [ ] URLs validated before use
- [ ] User input escaped in templates

### 8. Insecure Deserialization
- [ ] No `eval()` or `Function()` with user input
- [ ] JSON parsed and validated with Zod

### 9. Using Components with Known Vulnerabilities
- [ ] Dependencies audited (`npm audit`)
- [ ] No critical vulnerabilities
- [ ] Dependencies regularly updated

### 10. Insufficient Logging & Monitoring
- [ ] Security events logged (login, logout, failed auth)
- [ ] Errors logged with context
- [ ] No sensitive data in logs

---

## Critical Review Points

### Authentication Code
```typescript
// Check for:
- [ ] Password hashing (bcrypt, 12+ rounds)
- [ ] JWT secret from environment
- [ ] Session token generation (crypto.randomBytes)
- [ ] Secure cookie flags
```

### API Routes
```typescript
// Check for:
- [ ] Input validation with Zod
- [ ] Authentication check
- [ ] Authorization check (ownership)
- [ ] Error handling
- [ ] No sensitive data in responses
```

### Database Queries
```typescript
// Check for:
- [ ] Using Drizzle ORM (not raw SQL)
- [ ] Parameterized queries
- [ ] No string concatenation
- [ ] Transactions for multi-step operations
```

---

## Security Review Template

```markdown
## 🔴 Security Issues

### [Vulnerability Type]
**OWASP**: [Which of Top 10]
**Location**: `src/path/file.ts:line`
**Risk Level**: CRITICAL | HIGH | MEDIUM | LOW

**Issue**: [Description]

**Attack Scenario**:
1. [How an attacker could exploit this]
2. [What data/access they could gain]

**Fix**:
```typescript
// Suggested secure implementation
```

**Reference**: [security-sentinel skill link or OWASP article]
```

---

## See Also

- [security-sentinel/SKILL.md](../security-sentinel/SKILL.md) - Complete security patterns
- [../quality-gates/validation-rules.md](../quality-gates/validation-rules.md) - Validation rules
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
