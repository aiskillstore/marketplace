---
id: "progressive-enhancement"
title: "Progressive enhancement for essential actions"
category: "frontend"
summary: "Keep important user actions functional across limited networks, devices and script failures."
aliases: ["progressive enhancement","form fallback","server rendered forms","offline fallback","basic interaction","JavaScript olmadan form gönderme","temel işlev önce çalışsın","istemci kodu yüklenmeden işlem"]
decisions: [{"when":"A workflow can be expressed using native navigation or forms","use":"Provide a server-backed baseline and enhance the same endpoint with compatible client behavior.","tradeoff":"Some rich interactions need alternative, simpler flows."},{"when":"The interaction genuinely requires client-side state","use":"Provide an accessible status, error recovery and a clear fallback for unsupported contexts.","tradeoff":"A richer client raises the minimum runtime floor."}]
checks: ["Complete the essential flow without optional scripts.","Compare validation and duplicate submission behavior under slow and normal loads."]
sources: [{"title":"WHATWG constraint validation","url":"https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints"},{"title":"WHATWG HTML forms","url":"https://html.spec.whatwg.org/multipage/forms.html"}]
---

<!-- Generated record title. -->
# Progressive enhancement for essential actions

## Scenario

An appointment portal relies on a large bundle before a form can submit. Some visitors arrive with scripts blocked or delayed.

## Failure modes

Duplicating validation across enhanced and ordinary submissions can create incompatible semantics. Browser navigation and field retention can diverge.

## Explain it simply

Make the basic form work first, then improve it when scripting and network conditions allow.

## Implementation guidance

Build an ordinary form action, server validation and a result or redirect that works without a client application. Enhance the same contract to update inline and announce pending, error and success states. Preserve user-entered data on recoverable validation errors. Run the core flow with scripting disabled, then repeat on a slow connection where the server response completes before hydration.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A workflow can be expressed using native navigation or forms** Provide a server-backed baseline and enhance the same endpoint with compatible client behavior. Some rich interactions need alternative, simpler flows.
- **The interaction genuinely requires client-side state** Provide an accessible status, error recovery and a clear fallback for unsupported contexts. A richer client raises the minimum runtime floor.

## Verification

- Complete the essential flow without optional scripts.
- Compare validation and duplicate submission behavior under slow and normal loads.

## Sources

- [WHATWG constraint validation](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints)
- [WHATWG HTML forms](https://html.spec.whatwg.org/multipage/forms.html)

<!-- End generated record details. -->
