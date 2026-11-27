---
id: "content-security-policy"
title: "Content Security Policy for browser applications"
category: "security"
summary: "Roll out browser content restrictions that reflect real dependencies and expose blocked resource usage."
aliases: ["csp","script policy","nonce","report only csp","browser defense in depth","içerik güvenliği politikası","tarayıcı betiklerini sınırla","CSP rapor modu"]
decisions: [{"when":"An application can inventory and control most resources","use":"Use a narrowly scoped policy with nonces or hashes where appropriate and monitor report-only results before enforcement.","tradeoff":"Changing libraries can require policy and test updates."},{"when":"Legacy pages must be migrated gradually","use":"Deploy policy per route and prioritize removing dependencies that need broad permissions.","tradeoff":"Coverage differences need a documented rollout and monitoring plan."}]
checks: ["Test primary workflows under the enforced response headers.","Confirm violations are observable and report handling avoids retaining sensitive URLs."]
sources: [{"title":"W3C Content Security Policy Level 3","url":"https://www.w3.org/TR/CSP3/"},{"title":"OWASP Content Security Policy","url":"https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html"}]
---

<!-- Generated record title. -->
# Content Security Policy for browser applications

## Scenario

An application embeds a limited set of script and frame providers, then wants to restrict unexpected page resources.

## Failure modes

Overbroad source expressions weaken protection. Enforcing a strict policy without inventory can silently break production pages.

## Explain it simply

Choose which resources the browser is allowed to run and first check how the policy affects existing pages.

## Implementation guidance

Inventory actual script, style, frame and fetch dependencies before tightening the policy. Review report-only data where appropriate, then verify authenticated pages under actual enforcement. Use per-response nonces for approved inline scripts or hashes for stable inline code. Remove dependencies asking for broad directives when possible instead of making them defaults.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **An application can inventory and control most resources** Use a narrowly scoped policy with nonces or hashes where appropriate and monitor report-only results before enforcement. Changing libraries can require policy and test updates.
- **Legacy pages must be migrated gradually** Deploy policy per route and prioritize removing dependencies that need broad permissions. Coverage differences need a documented rollout and monitoring plan.

## Verification

- Test primary workflows under the enforced response headers.
- Confirm violations are observable and report handling avoids retaining sensitive URLs.

## Sources

- [W3C Content Security Policy Level 3](https://www.w3.org/TR/CSP3/)
- [OWASP Content Security Policy](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)

<!-- End generated record details. -->
