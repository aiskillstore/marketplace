# Defensive software security

- [Object-level authorization and tenancy](../knowledge/security/authorization-object-scope.md) · Enforce read and write permissions at the boundary for every object backed by user-controlled identifiers.
- [Content Security Policy for browser applications](../knowledge/security/content-security-policy.md) · Roll out browser content restrictions that reflect real dependencies and expose blocked resource usage.
- [Random sources for tokens and product choices](../knowledge/security/cryptographic-randomness.md) · Select randomness according to whether predictability or bias creates a material requirement.
- [CSRF protection for browser sessions](../knowledge/security/csrf-protection.md) · Protect browser-authenticated state mutations against requests initiated by another origin.
- [Parameterized database queries](../knowledge/security/parameterized-queries.md) · Preserve the separation between executable query structure and untrusted data.
- [Defensive file ingest for user uploads](../knowledge/security/safe-file-ingest.md) · Treat uploaded files as untrusted data throughout storage, validation and serving.
- [Secret storage, rotation and observability](../knowledge/security/secret-lifecycle.md) · Limit exposure of credentials and practice safe rotation without avoidable downtime.
- [Authenticating and processing webhooks](../knowledge/security/webhook-verification.md) · Accept external events only after verifying source authenticity and preserving idempotent delivery semantics.
