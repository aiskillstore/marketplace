---
name: Security Gate
description: Verify security considerations were addressed before shipping. Issues result in WARNINGS that strongly recommend fixing.
---

# Gate 2: Security Review

> "Security isn't a feature you add later. It's a foundation you build on."

## Purpose

This gate catches common security vulnerabilities before they reach production. Issues don't BLOCK, but generate strong WARNINGS.

## Gate Status

- **PASS** — No security issues found
- **WARNING** — Issues found that should be fixed before production
- **CRITICAL WARNING** — Severe issues that really should block

---

## Gate Questions

### Question 1: Input Entry Points
> "Where does user input enter this feature?"

**Looking for:**
- Awareness of all input sources (forms, URLs, headers, etc.)
- Understanding that ALL input is untrusted
- Identification of data flow

**Follow-up if input exists:**
> "How is that input validated before it's used?"

### Question 2: Data Access
> "What data does this feature access? Who should be able to access it?"

**Looking for:**
- Understanding of data sensitivity
- Awareness of authorization requirements
- Knowledge of who can see what

**Follow-up:**
> "How do you verify the requesting user is allowed to access this data?"

### Question 3: Secrets and Exposure
> "Are there any secrets, tokens, or sensitive data involved? Where are they stored?"

**Looking for:**
- Secrets in environment variables, not code
- No sensitive data in logs
- No tokens in URLs or client-side storage (unless necessary)

---

## Security Checklist

Review the code for these common issues:

### Input Handling
- [ ] All user input validated server-side
- [ ] Input length limits enforced
- [ ] Special characters handled (SQL, HTML, shell)
- [ ] File uploads validated (type, size, content)

### Authentication & Authorization
- [ ] Protected routes require authentication
- [ ] Users can only access their own data
- [ ] Admin routes check admin role
- [ ] Tokens have reasonable expiration

### Data Exposure
- [ ] API responses don't include unnecessary fields
- [ ] Errors don't expose internal details
- [ ] Logs don't contain passwords/tokens
- [ ] No sensitive data in URLs

### Common Vulnerabilities
- [ ] No SQL string concatenation
- [ ] No `eval()` or `new Function()` with user input
- [ ] No `innerHTML` with unsanitized user input
- [ ] No hardcoded secrets in code

---

## Response Templates

### If PASS

```
✅ SECURITY GATE: PASSED

Security considerations addressed:
- Input validation: ✓
- Authorization checks: ✓
- No exposed secrets: ✓

Moving to the next gate...
```

### If WARNING

```
⚠️ SECURITY GATE: WARNING

I found [X] security considerations to address:

**Issue 1: [Title]**
Location: `file.ts:42`
Risk: [What could go wrong]
Question: "What stops a malicious user from [attack scenario]?"

**Issue 2: [Title]**
Location: `file.ts:88`
Risk: [What could go wrong]
Suggestion: [Direction to fix, not the answer]

These should be fixed before this goes to production.
Would you like to address them now?
```

### If CRITICAL WARNING

```
🚨 SECURITY GATE: CRITICAL WARNING

This needs attention before proceeding:

**CRITICAL: [Issue]**
Location: `file.ts:42`
Risk: [Severity explanation - data breach, account takeover, etc.]

This is the kind of vulnerability that makes news headlines.
Let's fix this before anything else.
```

---

## Common Vulnerabilities to Check

### SQL Injection
```
❌ db.query(`SELECT * FROM users WHERE id = ${userId}`);
✅ db.query('SELECT * FROM users WHERE id = ?', [userId]);
```

### Cross-Site Scripting (XSS)
```
❌ element.innerHTML = userInput;
✅ element.textContent = userInput;
```

### Insecure Direct Object Reference (IDOR)
```
❌ // Anyone can access any user's data
   app.get('/users/:id', (req, res) => {
     const user = await User.findById(req.params.id);
     res.json(user);
   });

✅ // Check ownership
   app.get('/users/:id', (req, res) => {
     const user = await User.findById(req.params.id);
     if (user.id !== req.user.id) throw new ForbiddenError();
     res.json(user);
   });
```

### Hardcoded Secrets
```
❌ const apiKey = 'sk-live-abc123';
✅ const apiKey = process.env.API_KEY;
```

---

## Socratic Security Questions

Instead of pointing out the fix, ask:

1. "What stops user A from accessing user B's data by changing the ID?"
2. "If I send `<script>alert('XSS')</script>` as my name, what happens?"
3. "What if someone sends 10MB of data to this endpoint?"
4. "If I cloned this repo, what secrets would I see?"
5. "What happens if someone guesses another user's token?"

---

## Risk Level Guide

| Issue | Risk Level | Action |
|-------|------------|--------|
| SQL injection possible | CRITICAL | Must fix |
| No rate limiting on auth | HIGH | Should fix |
| Missing authorization check | HIGH | Should fix |
| XSS possible | HIGH | Should fix |
| Verbose error messages | MEDIUM | Recommend fix |
| Missing input validation | MEDIUM | Recommend fix |
| No CSRF protection | MEDIUM | Recommend fix |
| CORS too permissive | LOW | Note for review |
