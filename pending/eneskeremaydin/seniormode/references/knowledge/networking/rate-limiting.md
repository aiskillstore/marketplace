---
id: "rate-limiting"
title: "Token-bucket rate limiting"
category: "networking"
summary: "Bound sustained requests and explicitly allow or reject bursts for a scoped resource."
aliases: ["token bucket","rate limiting","burst control","sms doğrulama","istek sınırlandırma","doğrulama kodu sınırı","dakika değişince çok istek","jeton kovası"]
decisions: [{"when":"Bursts are acceptable within a defined budget","use":"Implement a token bucket with atomic state and an authoritative clock at the coordination boundary.","tradeoff":"Distributed state adds latency and loss of the store needs a defined fallback."},{"when":"A strict sliding count is required","use":"Use an exact sliding-window log or choose a counter approximation only if the contract allows estimation.","tradeoff":"Exact logs can consume per-request storage."}]
checks: ["Consume a full idle burst across two replicas and verify elapsed-time refill without a window-boundary bonus.","Simulate the clock moving backward and verify each identity scope and the intended response when the limiter is unavailable."]
sources: [{"title":"RFC 3290 appendix A, traffic profiles and token buckets","url":"https://datatracker.ietf.org/doc/html/rfc3290#appendix-A"},{"title":"RFC 6585 additional HTTP status codes","url":"https://www.rfc-editor.org/rfc/rfc6585"}]
---

<!-- Generated record title. -->
# Token-bucket rate limiting

## Scenario

A support service sends verification messages. Account and network limits must work consistently across several application replicas.

## Failure modes

Aligned fixed windows allow boundary bursts. A shared counter can race. One client identity can map to many genuine users behind a network gateway.

## Explain it simply

Give each limit a small refillable allowance and reject requests only once that allowance is exhausted.

## Implementation guidance

Pick the resource and identity that must be protected before choosing a rate. At the coordination boundary, atomically compute elapsed time, refill up to burst capacity, and then debit the request if enough tokens remain. Use one time source for a shared bucket. If it moves backward, keep the stored time high-water mark and grant no refill until positive elapsed time returns. Evict an inactive bucket only once recreating it as full is equivalent to retaining it. Define failure behavior separately for each protected action, and use HTTP 429 for requests the limiter actually rejects.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Bursts are acceptable within a defined budget** Implement a token bucket with atomic state and an authoritative clock at the coordination boundary. Distributed state adds latency and loss of the store needs a defined fallback.
- **A strict sliding count is required** Use an exact sliding-window log or choose a counter approximation only if the contract allows estimation. Exact logs can consume per-request storage.

## Verification

- Consume a full idle burst across two replicas and verify elapsed-time refill without a window-boundary bonus.
- Simulate the clock moving backward and verify each identity scope and the intended response when the limiter is unavailable.

## Sources

- [RFC 3290 appendix A, traffic profiles and token buckets](https://datatracker.ietf.org/doc/html/rfc3290#appendix-A)
- [RFC 6585 additional HTTP status codes](https://www.rfc-editor.org/rfc/rfc6585)

<!-- End generated record details. -->
