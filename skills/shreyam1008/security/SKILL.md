---
name: security
description: "Reviews and implements web security boundaries, authorization, output encoding, session protection, and secret handling. Use for security-sensitive changes or a requested security review."
---

# Security

Security is a default posture, not a feature you add later. Two rules underpin everything:

1. **Never trust input** — validate on the server, at the boundary, every time.
2. **Fail closed** — on any doubt (auth, config, verification), deny.

Lean on your framework's built-in protections first; only hand-roll when you understand the gap.

## Input validation

- Validate **on the server** — client validation is UX, not security.
- **Allowlist, not denylist**: accept known-good shapes (type, length, range, format, enum) and reject the rest. Use a schema validator (Zod, etc.).
- Validate *and* normalize (canonicalize) before checks to defeat encoding tricks.
- Bound everything: clamp numbers, cap string/array lengths, restrict file types/sizes.

## Output encoding — stop XSS

- **Encode on output**, contextually: HTML body, HTML attribute, JS, URL, and CSS each need different encoding.
- In React/Vue/Angular, default text binding auto-escapes — **the danger is the escape hatches**: `dangerouslySetInnerHTML`, `v-html`, `[innerHTML]`, `eval`, `Function`, injecting into `<script>`/`<style>`.
- Never put untrusted data into `javascript:`/`data:` URLs or DOM sink APIs without sanitizing.
- Sanitize rich/user HTML with a vetted library (DOMPurify) — don't regex it.
- Defense in depth: a strict **Content-Security-Policy** (avoid `unsafe-inline`/`unsafe-eval`).

## Injection (SQL/NoSQL/command/LDAP)

- **Parameterized queries / prepared statements only.** Never string-concatenate input into SQL or shell commands.
- Use safe APIs over shelling out; if you must, pass args as an array, never a constructed string.
- Apply least-privilege DB accounts.

## CSRF

- Use the framework's CSRF protection for cookie-authenticated state changes. If implementing tokens, validate a secret, unpredictable token bound to the session; per-request tokens are an option, not a universal requirement.
- Set cookies `SameSite=Lax`/`Strict`, `Secure`, `HttpOnly`.
- Validate request origin where appropriate and configure CORS with explicit trusted origins. CORS is not CSRF protection: browsers can send some cross-origin requests even when scripts cannot read the response.

## AuthN / AuthZ

- Don't roll your own crypto or auth — use a vetted provider/library.
- Passwords: use a maintained password-hashing implementation, preferably Argon2id (or scrypt where unavailable), with tuned work factors and per-user salt. Retain bcrypt for compatible legacy systems while accounting for its input-length limit. Never store plaintext or fast hashes.
- Enforce authorization on **every** request server-side (object-level too — don't trust IDs from the client → IDOR).
- Sessions: rotate on privilege change, expire, invalidate on logout; short-lived tokens + refresh.
- Use **constant-time comparison** for secrets/tokens/signatures.

## Secrets

- Never commit secrets, keys, tokens, `.env`, or DB URLs. Keep them in a secret manager / platform env.
- Never log secrets, bearer tokens, passwords, or full auth headers. Sanitize test fixtures.
- Rotate on exposure; scope keys to least privilege.

## Transport & headers

- HTTPS everywhere; **HSTS**. Set `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `X-Frame-Options`/`frame-ancestors`.
- Validate redirect targets (no open redirects); validate outbound URLs to prevent **SSRF** (block internal ranges/metadata endpoints).

## Dependencies & supply chain

- Pin + lock versions; run `npm audit`/Dependabot/SCA; update knowingly.
- Verify integrity (lockfile, SRI for third-party scripts); minimize third-party JS.

## Review checklist

- [ ] All external input validated server-side (allowlist) and bounded.
- [ ] Output encoded for its context; no unsafe HTML sinks with raw input.
- [ ] Parameterized queries everywhere; no shell string-building.
- [ ] AuthZ enforced per request incl. object ownership.
- [ ] CSRF protection + secure cookies on state-changing routes.
- [ ] No secrets in code/logs/fixtures; constant-time secret compares.
- [ ] Security headers + HTTPS/HSTS; redirects/outbound URLs validated.

## Reference

- OWASP: [CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html), [password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), Input Validation, XSS Prevention, SQL Injection, Auth, Secrets Management.
- MDN: CSP, `SameSite` cookies, Subresource Integrity.
