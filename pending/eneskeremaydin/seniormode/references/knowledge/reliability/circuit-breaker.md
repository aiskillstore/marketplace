---
id: "circuit-breaker"
title: "Circuit breakers for dependency failure"
category: "reliability"
summary: "Constrain repeated attempts to a dependency whose health is below the service's tolerance."
aliases: ["circuit breaker","half open probe","dependency failure","fail fast","fallback","bağımlılık hata verince istekleri durdur","devre kesici","servis toparlanınca deneme isteği"]
decisions: [{"when":"Repeated dependency failure can exhaust caller resources","use":"Use per-operation breaker state with thresholds, timeouts and bounded half-open probes.","tradeoff":"Tuning is nontrivial and the fallback must preserve the product contract."},{"when":"Failures are rare or a bounded timeout is sufficient","use":"Prefer explicit deadlines and a small retry budget, observing recovery first.","tradeoff":"Fewer moving parts but callers still experience individual failures."}]
checks: ["Simulate failing and recovered dependencies and verify controlled half-open traffic.","Verify a breaker for one dependency leaves independent paths available."]
sources: [{"title":"Azure circuit breaker pattern","url":"https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker"},{"title":"AWS timeouts, retries and backoff with jitter","url":"https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/"}]
---

<!-- Generated record title. -->
# Circuit breakers for dependency failure

## Scenario

A checkout quote service calls a dependency that intermittently becomes unreachable. Thread pools saturate while failing calls wait.

## Failure modes

A global breaker can suppress healthy endpoints. Half-open probes can stampede, and an inappropriate fallback can misrepresent critical results.

## Explain it simply

Pause most calls while a dependency is failing and make a small controlled probe before accepting traffic again.

## Implementation guidance

Group operations by shared dependency and failure behavior. Define which outcomes count, how many half-open probes may run and what fallback remains truthful. If isolated incidents already fit a deadline and retry budget, verify that before introducing state. Fault one operation and confirm a healthy peer stays available during recovery.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Repeated dependency failure can exhaust caller resources** Use per-operation breaker state with thresholds, timeouts and bounded half-open probes. Tuning is nontrivial and the fallback must preserve the product contract.
- **Failures are rare or a bounded timeout is sufficient** Prefer explicit deadlines and a small retry budget, observing recovery first. Fewer moving parts but callers still experience individual failures.

## Verification

- Simulate failing and recovered dependencies and verify controlled half-open traffic.
- Verify a breaker for one dependency leaves independent paths available.

## Sources

- [Azure circuit breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
- [AWS timeouts, retries and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

<!-- End generated record details. -->
