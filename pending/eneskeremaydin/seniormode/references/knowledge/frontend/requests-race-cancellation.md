---
id: "requests-race-cancellation"
title: "Cancelling stale frontend requests"
category: "frontend"
summary: "Keep visible data consistent when filters or input change faster than network responses arrive."
aliases: ["abort controller","search race","request cancellation","stale results","latest response wins","eski arama yanıtı yeni sonucu siliyor","önceki arama isteğini iptal et","cevaplar ters sırada geliyor"]
decisions: [{"when":"A new request supersedes the previous display state","use":"Cancel earlier fetches when possible and gate applied results by current request identity.","tradeoff":"The server may keep working after the browser cancels."},{"when":"Requests populate independent cached keys","use":"Preserve their separate results and show data scoped to the currently selected key.","tradeoff":"The cache needs size, retention and invalidation rules."}]
checks: ["Resolve two responses in reverse order and verify the screen matches current input.","Unmount or abort a request and verify errors and loading state remain consistent."]
sources: [{"title":"WHATWG Fetch standard","url":"https://fetch.spec.whatwg.org/"},{"title":"TanStack Query cancellation","url":"https://tanstack.com/query/latest/docs/framework/react/guides/query-cancellation"}]
---

<!-- Generated record title. -->
# Cancelling stale frontend requests

## Scenario

An operator types a search query and the earlier slow response arrives after the newer query's results.

## Failure modes

Cancellation is best effort and a response can resolve just before abort. Loading indicators may be cleared by a superseded request.

## Explain it simply

Ignore results that belong to an old query and cancel unnecessary work when the browser can.

## Implementation guidance

Keep a sequence number for the active request or scope cached results to an immutable query key containing the inputs that affect the response. Pass the cancellation signal to the network operation and compare identity before applying a result, error, or loading completion. Simulate selecting A, selecting B, and receiving A last despite abort. Verify that B keeps both its visible results and loading/error ownership.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A new request supersedes the previous display state** Cancel earlier fetches when possible and gate applied results by current request identity. The server may keep working after the browser cancels.
- **Requests populate independent cached keys** Preserve their separate results and show data scoped to the currently selected key. The cache needs size, retention and invalidation rules.

## Verification

- Resolve two responses in reverse order and verify the screen matches current input.
- Unmount or abort a request and verify errors and loading state remain consistent.

## Sources

- [WHATWG Fetch standard](https://fetch.spec.whatwg.org/)
- [TanStack Query cancellation](https://tanstack.com/query/latest/docs/framework/react/guides/query-cancellation)

<!-- End generated record details. -->
