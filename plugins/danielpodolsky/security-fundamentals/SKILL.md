---
name: Security Fundamentals
description: Auto-invoke when reviewing authentication, authorization, input handling, data exposure, or any user-facing code. Enforces OWASP top 10 awareness and security-first thinking.
---

# Security Fundamentals Review

> "Security is not a feature. It's a foundation. Build on sand, and the house falls."

## When to Apply

Activate this skill when reviewing:
- Authentication/login flows
- Authorization checks
- User input handling
- Database queries
- File uploads
- API endpoints
- Data exposure in responses

---

## Review Checklist

### Input Validation (NEVER Trust the Client)

- [ ] **All inputs validated**: Is every user input checked before use?
- [ ] **Server-side validation**: Is validation done on the server, not just client?
- [ ] **Type checking**: Are expected types enforced?
- [ ] **Length limits**: Are string lengths bounded?
- [ ] **Whitelist over blacklist**: Are allowed values explicitly defined?

### Authentication

- [ ] **Password hashing**: Are passwords hashed (bcrypt, argon2), not encrypted?
- [ ] **No plaintext secrets**: Are secrets in env vars, not code?
- [ ] **Token expiry**: Do JWTs/sessions have reasonable expiration?
- [ ] **Secure transmission**: Is HTTPS enforced?

### Authorization

- [ ] **Ownership checks**: Can users only access THEIR data?
- [ ] **Role verification**: Are admin routes protected by role checks?
- [ ] **No client-side auth**: Is authorization enforced server-side?

### Data Exposure

- [ ] **Minimal response**: Does the API return only necessary fields?
- [ ] **No sensitive data in URLs**: Are tokens/IDs not in query strings?
- [ ] **No sensitive data in logs**: Are passwords/tokens excluded from logs?

---

## OWASP Top 10 Quick Check

### 1. Injection (SQL, NoSQL, Command)
```
❌ db.query(`SELECT * FROM users WHERE id = ${userId}`);

✅ db.query('SELECT * FROM users WHERE id = ?', [userId]);
```

### 2. Broken Authentication
```
❌ if (req.headers.admin === 'true') { /* allow admin */ }

✅ const user = await verifyToken(req.headers.authorization);
   if (user.role !== 'admin') throw new ForbiddenError();
```

### 3. Sensitive Data Exposure
```
❌ res.json({ user: { ...user, password, ssn } });

✅ res.json({ user: { id: user.id, name: user.name } });
```

### 4. Broken Access Control
```
❌ app.get('/users/:id', async (req, res) => {
     const user = await User.findById(req.params.id);
     res.json(user);
   });

✅ app.get('/users/:id', async (req, res) => {
     const user = await User.findById(req.params.id);
     if (user.id !== req.user.id && req.user.role !== 'admin') {
       throw new ForbiddenError();
     }
     res.json(user);
   });
```

### 5. Security Misconfiguration
```
❌ CORS: origin: '*'
❌ Detailed error messages in production
❌ Debug mode enabled in production

✅ CORS: origin: process.env.ALLOWED_ORIGINS
✅ Generic error messages to clients
✅ Debug mode disabled in production
```

### 6. Cross-Site Scripting (XSS)
```
❌ element.innerHTML = userInput;

✅ element.textContent = userInput;
✅ DOMPurify.sanitize(userInput);
```

---

## Socratic Questions

Ask the junior these questions instead of giving answers:

1. **Trust**: "What stops a malicious user from sending anything they want here?"
2. **Ownership**: "How do you know this user owns this resource?"
3. **Exposure**: "What's the worst thing that could happen if this endpoint is exposed?"
4. **Secrets**: "If I `git clone` this repo, what secrets would I see?"
5. **Injection**: "What if someone sends `'; DROP TABLE users; --` as input?"

---

## Red Flags to Call Out

| Flag | Risk | Question |
|------|------|----------|
| String concatenation in queries | SQL Injection | "Can this input contain SQL?" |
| `eval()` or `new Function()` | Code Injection | "Why is dynamic code execution needed?" |
| `innerHTML` with user data | XSS | "What if the user includes `<script>`?" |
| Passwords in logs | Data Leak | "Who can see these logs?" |
| No rate limiting on auth | Brute Force | "What stops someone from trying every password?" |
| CORS: `*` | Security Bypass | "Should any website be able to call this API?" |
| JWT with no expiry | Token Theft | "What happens if this token is stolen?" |
| IDs in URLs | IDOR | "Can user A access user B's data by changing the ID?" |

---

## Security Checklist Before Deploy

1. [ ] All secrets in environment variables
2. [ ] HTTPS enforced
3. [ ] Input validation on all endpoints
4. [ ] SQL/NoSQL injection prevented (parameterized queries)
5. [ ] XSS prevented (output encoding)
6. [ ] CSRF protection enabled
7. [ ] Rate limiting on auth endpoints
8. [ ] Sensitive data excluded from responses
9. [ ] Authorization checks on every protected route
10. [ ] Security headers set (helmet.js or equivalent)

---

## Never Do This

| Action | Why |
|--------|-----|
| Store passwords in plaintext | One breach exposes all users |
| Put secrets in code | Git history is forever |
| Trust client-side validation only | Anyone can bypass the client |
| Return full database objects | Exposes internal fields |
| Log sensitive data | Logs get compromised too |
| Use `md5` or `sha1` for passwords | Cryptographically broken |
