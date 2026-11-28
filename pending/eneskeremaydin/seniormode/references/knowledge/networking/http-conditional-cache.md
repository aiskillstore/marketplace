---
id: "http-conditional-cache"
title: "HTTP validators and cache freshness"
category: "networking"
summary: "Let clients validate cached representations while preserving authorization and variant boundaries."
aliases: ["etag","if none match","304 not modified","cache control","http cache","değişmediyse tekrar indirme","ETag ile HTTP önbellek","koşullu HTTP isteği"]
decisions: [{"when":"The response can be publicly shared","use":"Declare Cache-Control policy, vary by representation inputs and issue stable validators.","tradeoff":"Long freshness can delay changes unless versioned URLs or invalidation are available."},{"when":"The response is sensitive or user-specific","use":"Choose private caching or no-store according to policy and verify intermediaries match it.","tradeoff":"Fresh requests can cost additional bytes and work."}]
checks: ["Verify 304, 200 after change and the expected headers for two content variants.","Ensure separately authorized users never share a cached private response."]
sources: [{"title":"RFC 9111 HTTP caching","url":"https://www.rfc-editor.org/rfc/rfc9111"},{"title":"RFC 9110 HTTP semantics","url":"https://www.rfc-editor.org/rfc/rfc9110"}]
related: ["cache-invalidation"]
---

<!-- Generated record title. -->
# HTTP validators and cache freshness

## Scenario

A mobile client repeatedly downloads a large public catalog while private account details travel through the same gateway.

## Failure modes

Freshness directives and validators serve different purposes. A missing variant key can mix languages, encodings or users, and returning 304 cannot substitute for authorization.

## Explain it simply

Let the client ask whether its copy is still current without downloading it again.

## Implementation guidance

Pair a freshness policy with a validator appropriate for the representation. Evaluate authentication and tenant visibility before serving either a full response or a 304, and include representation inputs such as language or encoding in Vary when shared caching is allowed. For sensitive account data choose private or no-store as required. Test the same URL for different users and representations as well as a stale client validator after an update.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The response can be publicly shared** Declare Cache-Control policy, vary by representation inputs and issue stable validators. Long freshness can delay changes unless versioned URLs or invalidation are available.
- **The response is sensitive or user-specific** Choose private caching or no-store according to policy and verify intermediaries match it. Fresh requests can cost additional bytes and work.

## Verification

- Verify 304, 200 after change and the expected headers for two content variants.
- Ensure separately authorized users never share a cached private response.

## Sources

- [RFC 9111 HTTP caching](https://www.rfc-editor.org/rfc/rfc9111)
- [RFC 9110 HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110)

## Related decisions

- [Cache invalidation and freshness budgets](../data/cache-invalidation.md)

<!-- End generated record details. -->
