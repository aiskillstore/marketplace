---
id: "form-validation-boundaries"
title: "Form validation and error feedback"
category: "frontend"
summary: "Give immediate form feedback and enforce authoritative validation at the server boundary."
aliases: ["form validation","client server validation","field errors","validation api","accessible errors","form doğrulama","aynı kullanıcı adı form hatası","sunucuda alan doğrulama"]
decisions: [{"when":"Input mistakes are local and cheaply detectable","use":"Use native constraints or client checks and surface field-level messages with accessible links.","tradeoff":"Client feedback is a convenience and must agree with server semantics."},{"when":"The rule depends on current stored data","use":"Validate atomically on the server and return a stable error code tied to the relevant field or form.","tradeoff":"Clients must keep entered values, handle outdated state and present the error in context."}]
checks: ["Submit invalid and race-prone input directly to the server endpoint.","Verify users can discover errors, fix them and retain unrelated field values."]
sources: [{"title":"WHATWG constraint validation","url":"https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints"},{"title":"W3C Web Content Accessibility Guidelines 2.2","url":"https://www.w3.org/TR/WCAG22/"}]
---

<!-- Generated record title. -->
# Form validation and error feedback

## Scenario

A membership form checks required details locally while the server enforces account uniqueness and allowed transitions.

## Failure modes

Client validation can be bypassed. Server errors attached in the wrong order can confuse screen reader and keyboard users.

## Explain it simply

Let the page catch easy mistakes quickly while the server checks the rules that determine whether a submission can succeed.

## Implementation guidance

Use the client to show immediate, accessible field feedback but enforce uniqueness, permissions and allowed state transitions at the server boundary. Map stable server error codes back to their field or form and preserve input on recoverable failures. On a duplicate registration race, require one successful account and an understandable error from the other submission. Exercise both the native keyboard path and a submission without enhancement.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Input mistakes are local and cheaply detectable** Use native constraints or client checks and surface field-level messages with accessible links. Client feedback is a convenience and must agree with server semantics.
- **The rule depends on current stored data** Validate atomically on the server and return a stable error code tied to the relevant field or form. Clients must keep entered values, handle outdated state and present the error in context.

## Verification

- Submit invalid and race-prone input directly to the server endpoint.
- Verify users can discover errors, fix them and retain unrelated field values.

## Sources

- [WHATWG constraint validation](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints)
- [W3C Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)

<!-- End generated record details. -->
