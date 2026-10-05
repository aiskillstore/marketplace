# Security Rules

Apply defense in depth at every untrusted boundary. Security choices depend on the clients, data, threats, deployment, and installed versions; no single guard, JWT library, or validation pipe secures an application by itself.

## Establish the threat model

Identify trust boundaries, exposed transports, identities, tenants, sensitive data, privileged operations, outbound network access, uploaded content, webhook callers, proxies, and dependency versions. Preserve security controls already required by the repository or platform.

## Validate and bound input

- Define DTO or schema allow-lists for body, path, query, message, job, configuration, and webhook input.
- Reject or intentionally strip unknown fields; make coercion, nullability, defaults, and nested validation explicit.
- Bound body size, strings, arrays, pages, filters, files, decompression, regex work, and GraphQL depth/complexity.
- Use parameterized ORM/driver APIs. Validation is not a substitute for injection-safe queries.
- Validate according to business meaning as well as syntax, and re-check authorization after resolving the target resource.

Nest's `ValidationPipe` is one framework mechanism. Verify global and route-specific options because `transform`, `whitelist`, and `forbidNonWhitelisted` change behavior.

## Separate authentication and authorization

- Authentication establishes a principal; authorization decides whether that principal may perform this action on this resource.
- Use guards and route metadata for coarse policy, then enforce ownership, tenant, state, and field rules in the application operation or policy that has the required data.
- Default sensitive routes to denied when policy metadata or identity is missing.
- Test cross-tenant and horizontal privilege escalation, not only anonymous access.

JWT is one credential format, not a universal authentication architecture. When used, verify signature and allowed algorithm, issuer, audience, expiry/not-before, key selection, rotation, storage, and revocation/session policy. Do not accept algorithm choice from an untrusted token or build custom cryptography.

## Protect secrets and sessions

- Load secrets from the deployment's secret mechanism and validate required configuration at startup.
- Never commit, log, trace, return, or embed server secrets in client bundles.
- Rotate keys and credentials with an overlap plan.
- For browser cookies, deliberately configure `Secure`, `HttpOnly`, `SameSite`, domain/path, expiry, CSRF defense, and trusted origins.
- For bearer tokens, account for exfiltration, replay, audience, and client storage risk.

## Control output and browser exposure

Return explicit response DTOs or projections and allow-list fields. Do not serialize ORM entities with credentials, reset tokens, internal flags, or private relations.

Serialization controls data exposure; it is not universal XSS prevention. Encode output for its eventual HTML/URL/JavaScript context at the renderer. Sanitize only when intentionally accepting rich content, with a maintained context-appropriate sanitizer.

Configure CORS, proxy trust, security headers, redirects, and cache headers for the actual deployment. CORS is a browser policy, not authentication.

## Defend abusive and risky features

- Rate-limit by an appropriate identity, tenant, route cost, and trusted client IP. Use shared state when limits must span replicas and account for proxy configuration.
- Treat rate limiting as one abuse control, not complete DDoS protection.
- Verify webhook signatures over the required raw bytes, enforce freshness/replay policy, and rotate secrets.
- Restrict outbound URLs to prevent SSRF; validate scheme, resolved destination, redirects, and network ranges according to policy.
- Scan and isolate uploads, generate server-side names, bound size/type, and never trust the original filename or content type alone.
- Apply timeouts and resource bounds to expensive cryptography, parsing, queries, and external calls.

## Operate securely

Use structured audit events for privileged actions without placing secrets or unnecessary personal data in logs. Patch supported runtime and dependency versions, review advisories, minimize production privileges, and keep database/broker/cloud credentials scoped to the owning service.

## Verification gate

- Unit-test policies and ownership decisions.
- E2E-test unauthenticated, forbidden, cross-tenant, malformed, oversized, replayed, and rate-limited requests.
- Test response field allow-lists and log redaction.
- Scan dependencies and container artifacts in CI, then triage results rather than treating a scan as proof of safety.
- Perform focused manual or automated security testing for uploads, webhooks, outbound URLs, rich content, and privileged flows.

This reference owns disclosure and redaction requirements. [Error handling](error-handling.md) owns failure taxonomy and transport mapping; a mapper must satisfy these security rules rather than creating a separate disclosure policy.

Use current official guidance for [NestJS authentication](https://docs.nestjs.com/security/authentication), [authorization](https://docs.nestjs.com/security/authorization), [rate limiting](https://docs.nestjs.com/security/rate-limiting), [validation](https://docs.nestjs.com/techniques/validation), and [serialization](https://docs.nestjs.com/techniques/serialization), plus the OWASP [REST Security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html) and [Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) cheat sheets.
