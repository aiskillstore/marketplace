---
id: "retry-backoff"
title: "Retry budgets, backoff and jitter"
category: "reliability"
summary: "Recover transient failures within a deadline without multiplying downstream load."
aliases: ["retry backoff","retry storm","exponential jitter","transient errors","retry budget","artan aralıklarla tekrar deneme","yeniden deneme fırtınası","rastgele bekleme","tekrar deneme bütçesi"]
decisions: [{"when":"The operation is safe to repeat within the request deadline","use":"Retry at one responsible layer with capped exponential backoff, jitter and an explicit attempt budget.","tradeoff":"Some transient failures will be surfaced when the budget runs out."},{"when":"A timeout may hide a completed non-idempotent side effect","use":"Use a stable operation key, check status, or surface a recoverable pending result.","tradeoff":"The workflow needs durable state and reconciliation."}]
checks: ["Inject transient and permanent errors and count total downstream calls.","Verify backoff does not extend the caller's deadline and handles cancellation."]
sources: [{"title":"AWS timeouts, retries and backoff with jitter","url":"https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/"},{"title":"AWS exponential backoff and jitter","url":"https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/"}]
---

<!-- Generated record title. -->
# Retry budgets, backoff and jitter

## Scenario

A dashboard calls a failing permissions service through two API layers. Each layer can retry independently while the user waits for one response.

## Failure modes

Nested retries multiply calls. Retrying deterministic errors wastes capacity, and synchronized attempts create another load spike. Side effects require reuse of logical identity.

## Explain it simply

Try short-lived failures again a limited number of times and spread the attempts out.

## Implementation guidance

Choose one retry owner and propagate its time or attempt budget down. Retry known transient errors with jitter and a cap, reuse the logical key for side effects and surface deterministic failures promptly. Record attempt count per user operation to catch multiplicative retries. Exercise a lost successful acknowledgement, synchronized callers and an outage longer than their deadline.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The operation is safe to repeat within the request deadline** Retry at one responsible layer with capped exponential backoff, jitter and an explicit attempt budget. Some transient failures will be surfaced when the budget runs out.
- **A timeout may hide a completed non-idempotent side effect** Use a stable operation key, check status, or surface a recoverable pending result. The workflow needs durable state and reconciliation.

## Verification

- Inject transient and permanent errors and count total downstream calls.
- Verify backoff does not extend the caller's deadline and handles cancellation.

## Sources

- [AWS timeouts, retries and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [AWS exponential backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)

<!-- End generated record details. -->
