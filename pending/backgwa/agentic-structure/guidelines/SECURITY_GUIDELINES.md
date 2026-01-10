# Security Guidelines

## Purpose and Mindset
Security is a core requirement when building software. Assume any project may be deployed to production and exposed to untrusted networks. Design and implement features with the expectation that inputs can be malicious and systems can be probed continuously.

## Core Principles
- Assume Exposure: Treat every endpoint, job, and integration as potentially reachable from outside the organization.
- Least Privilege: Grant the minimum permissions needed (runtime, database, cloud, CI).
- Secure by Default: Prefer safe defaults; require explicit opt-in for risky behavior.
- Defense in Depth: Use layered controls (validation, authz, rate limiting, monitoring).

## Application Philosophy
These guidelines are designed to be applied thoughtfully, not rigidly:

- **Strive to follow** - Aim to apply these principles consistently, but use judgment when exceptions are warranted
- **Apply incrementally** - Build good habits gradually; it's acceptable to apply these imperfectly at first and improve over time
- **Context matters** - Adapt guidelines to project size, team structure, and specific requirements
- **Progress over perfection** - Moving in the right direction is better than perfect adherence that delays delivery
- **Question and clarify** - When unsure, err on the side of asking or documenting your reasoning
- **Security always takes precedence** - If a guideline conflicts with efficiency or simplicity, choose security

## Secrets and Sensitive Configuration
Never hardcode secrets or sensitive values in source code, constants, or committed configuration.

### What counts as a secret
- API keys, tokens, client secrets
- Database credentials, connection strings with passwords
- Private keys, signing keys, encryption keys
- Session secrets, webhook secrets, OAuth secrets
- Internal service endpoints that reveal infrastructure details

### Required handling
- Store secrets in environment variables or a trusted secret manager (preferred).
- Ensure secrets are not included in public repositories, build artifacts, or client bundles.
- Use separate values per environment (dev/staging/prod) and rotate when exposure is suspected.
- Add repository hygiene: `.gitignore` local secret files; avoid committing `.env` files.

## Protecting Values: Hashing vs Encryption
Choose the correct protection mechanism based on whether you must recover the original value.

### Hashing (recommended for passwords and irreversible comparisons)
- Use hashing when you only need to verify a value, not recover it (e.g., passwords).
- Use salted, adaptive password hashing algorithms that resist brute-force attacks:
  - Prefer Argon2id (recommended), or bcrypt/scrypt when Argon2id is unavailable.
- Do not use fast general-purpose hashes (e.g., MD5, SHA-1, raw SHA-256) for passwords.
- Use constant-time comparisons where applicable to reduce timing leaks.

### Encryption (when you must decrypt)
- Use encryption only when the original value must be retrieved (e.g., stored access tokens).
- Prefer well-reviewed libraries and standard constructions (e.g., AES-GCM).
- Keep encryption keys out of source control and rotate keys on a schedule.

## Authentication and Authorization
### Prefer trusted libraries and managed solutions
For authentication flows and security-sensitive tooling, using vetted libraries and well-established providers is often safer than implementing from scratch.

### Implementation expectations
- Separate authentication (who you are) from authorization (what you can do).
- Enforce authorization checks server-side for every protected action (not only at UI level).
- Use short-lived tokens where possible; secure session storage; apply CSRF protections where relevant.
- Apply rate limiting and lockout/backoff strategies for credential-related endpoints.

## Rate Limiting and Abuse Prevention
Treat abuse resistance as a baseline production requirement, especially for public endpoints.

### Where to apply it
- Authentication flows (login, signup, password reset, OTP, email/phone verification)
- High-cost endpoints (search, exports, reports, AI/compute-heavy requests)
- Public APIs and webhooks (per token/API key, per tenant, per source)

### Recommended controls

#### Rate Limit Baselines (Autonomous Decision Guidance)
Apply rate limiting based on project context and threat model. Consider per-IP and per-identity limits (user, account, API key, tenant) with these general principles:

| Endpoint Type | Suggested Approach | Scope | Reasoning |
|--------------|-------------------|-------|-----------|
| Authentication (login, signup, password reset) | Stricter limits, few attempts per minute | Per IP address | Prevent brute force while allowing legitimate retries |
| High-cost operations (search, reports, AI) | Moderate limits based on resource costs | Per user/account | Balance usage with resource protection |
| Public APIs | Higher limits adjusted for use case | Per API key | Scale based on integration requirements |
| Public webhooks | Higher limits for event-driven systems | Per tenant | Adjust based on event volume patterns |

⚠️ **Autonomous application principles.** Every application has different needs:
- Adjust quotas based on observed legitimate usage and traffic patterns
- Consider resource costs and security risks
- Document your chosen limits and rationale

**Additional considerations when adjusting quotas:**
- Observed legitimate usage patterns
- Resource cost (CPU, memory, external API calls)
- Security risk level (auth endpoints need stricter limits)
- User tier (free vs paid accounts)

**Document chosen limits:**
- Add limits to API documentation
- Include limits in code comments near rate limiting logic
- Log when limits are adjusted and why

#### Additional Controls
- Return `429 Too Many Requests` with `Retry-After` header where applicable
- Avoid leaking whether an account exists in rate limit responses
- Add backoff/lockout for repeated failed authentication attempts
  - Example: After 5 failed attempts in 5 minutes, lock for 15 minutes
- Log and alert on anomalies (sudden spikes, distributed attacks)
- Set request size/time limits and concurrency caps to reduce DoS risk
  - Request body size: Example limits: 10MB for most endpoints, 100MB for file uploads. Adjust based on use case—document processing may need larger limits, mobile apps may need smaller.
  - Request timeout: Example timeouts: 30 seconds for API calls, 5 minutes for long operations. Adjust for network conditions and processing complexity.
- Consider bot mitigation for high-risk flows (device signals, proof-of-work, CAPTCHA) when appropriate

## File and Upload Security
Assume all uploads are untrusted. Validate, isolate, and minimize what you store and process.

### Validation and parsing
- Prefer strict allowlists for file types; validate using magic bytes/content sniffing (not only extensions).
- Enforce size limits, count limits, and timeouts; protect against zip bombs and decompression bombs.
- Sanitize filenames (or ignore them entirely) and generate server-side object names.
- Strip or normalize metadata when relevant (e.g., EXIF location data in images).

### Storage and delivery
- Store uploads outside the application runtime filesystem when possible (object storage); never serve directly from a writable directory.
- Prevent execution: ensure uploaded content is not treated as code (no “upload then execute” paths).
- Use safe response headers when serving files (e.g., `Content-Disposition: attachment` for untrusted types).
- Use signed URLs or authenticated download endpoints for private content; enforce authorization on every access.

### Malware and risky formats
- Scan uploads for malware where threat model requires it (especially documents and archives).
- Be cautious with complex parsers (PDF/Office/media). Prefer well-maintained libraries and run processing in isolated workers/sandboxes.

## Dependency and Supply Chain Safety
- Prefer widely adopted, actively maintained libraries for security-critical features.
- Pin dependency versions; review major upgrades; remove unused dependencies.
- Treat CI/CD and build pipelines as part of the attack surface (protect tokens and signing keys).

## Operational Safety (Production)
- Avoid leaking sensitive data in logs, errors, or analytics.
- Use HTTPS/TLS everywhere; validate certificates; restrict CORS appropriately.
- Monitor authentication anomalies and unexpected traffic patterns; define an incident response path.
