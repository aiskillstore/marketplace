---
id: "csrf-protection"
title: "CSRF protection for browser sessions"
category: "security"
summary: "Protect browser-authenticated state mutations against requests initiated by another origin."
aliases: ["csrf","same site cookies","anti csrf token","cross site request forgery","origin validation","siteler arası istek sahteciliğine karşı koruma","oturum çerezi ve CSRF belirteci","farklı siteden gelen form isteği"]
decisions: [{"when":"Browser cookies authenticate state-changing requests","use":"Use framework CSRF protection or session-bound tokens, with safe HTTP methods and suitable cookie attributes.","tradeoff":"Cross-site integrations and token refresh need deliberate support."},{"when":"Authorization uses a non-ambient credential controlled by the client","use":"Verify that cookies or other ambient credentials cannot silently authenticate the same endpoint.","tradeoff":"CORS configuration and client storage risks still need separate review."}]
checks: ["Verify normal and expired-token submissions from the app work as expected.","Assert a request from an untrusted origin without valid proof cannot change state."]
sources: [{"title":"OWASP CSRF prevention","url":"https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html"},{"title":"RFC 9110 HTTP semantics","url":"https://www.rfc-editor.org/rfc/rfc9110"}]
---

<!-- Generated record title. -->
# CSRF protection for browser sessions

## Scenario

A web app uses a session cookie and exposes settings changes through browser forms and JSON endpoints.

## Failure modes

The browser can attach cookies to cross-site requests under some conditions. Read-only endpoints should not change state, and SameSite needs an explicit compatibility assessment.

## Explain it simply

Require proof that a change came from a legitimate session and an intended page of the application.

## Implementation guidance

Identify routes that change state and which credentials the browser can attach automatically. Apply the framework CSRF check to that state-changing path for both form and client-app variants. Choose suitable cookie attributes in addition to that guard. Test legitimate mutations through the real public route and verify that safe methods leave state as it was.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Browser cookies authenticate state-changing requests** Use framework CSRF protection or session-bound tokens, with safe HTTP methods and suitable cookie attributes. Cross-site integrations and token refresh need deliberate support.
- **Authorization uses a non-ambient credential controlled by the client** Verify that cookies or other ambient credentials cannot silently authenticate the same endpoint. CORS configuration and client storage risks still need separate review.

## Verification

- Verify normal and expired-token submissions from the app work as expected.
- Assert a request from an untrusted origin without valid proof cannot change state.

## Sources

- [OWASP CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [RFC 9110 HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110)

<!-- End generated record details. -->
