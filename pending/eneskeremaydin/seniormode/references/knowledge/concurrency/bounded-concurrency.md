---
id: "bounded-concurrency"
title: "Bounded concurrency and backpressure"
category: "concurrency"
summary: "Bound in-flight work and queue growth when producers are faster than downstream resources."
aliases: ["bounded concurrency","worker pool","backpressure","parallel uploads","concurrency limit","eşzamanlı işi sınırla","iş kuyruğu şişiyor","paralel işlerin sınırı","geri basınç"]
decisions: [{"when":"The workload can be slowed or rejected upstream","use":"Bound both concurrently active tasks and waiting work, and propagate backpressure or explicit rejection.","tradeoff":"Burst latency increases or requests must be retried by clients."},{"when":"Work requires durable delayed processing","use":"Use a durable queue with concurrency limits and a separate admission policy.","tradeoff":"Operations need observable lag, storage limits and retry handling."}]
checks: ["Send work faster than it completes and assert memory and queue growth remain bounded.","Verify cancelled and failed tasks release their capacity exactly once."]
sources: [{"title":"Google SRE on handling overload","url":"https://sre.google/sre-book/handling-overload/"},{"title":"Node.js streams and backpressure","url":"https://nodejs.org/en/learn/modules/backpressuring-in-streams"}]
---

<!-- Generated record title. -->
# Bounded concurrency and backpressure

## Scenario

An import endpoint processes thousands of large files using a host with a finite memory and connection pool.

## Failure modes

Unrestricted fan-out allocates memory before downstream capacity exists. A fixed worker pool still fails if the waiting queue is unbounded.

## Explain it simply

Process a manageable batch at a time and slow incoming work before the queue grows beyond capacity.

## Implementation guidance

Estimate the budget from simultaneous downstream connections, task memory and worst-case input size. Acquire capacity before opening a file or allocating its full buffer, bound queued work as well as active tasks, and release capacity in a finally path. When the queue fills, backpressure or reject explicitly instead of growing latency silently. Stress with a stalled consumer and cancelled requests, and assert high-water active/queued counts and cleanup.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The workload can be slowed or rejected upstream** Bound both concurrently active tasks and waiting work, and propagate backpressure or explicit rejection. Burst latency increases or requests must be retried by clients.
- **Work requires durable delayed processing** Use a durable queue with concurrency limits and a separate admission policy. Operations need observable lag, storage limits and retry handling.

## Verification

- Send work faster than it completes and assert memory and queue growth remain bounded.
- Verify cancelled and failed tasks release their capacity exactly once.

## Sources

- [Google SRE on handling overload](https://sre.google/sre-book/handling-overload/)
- [Node.js streams and backpressure](https://nodejs.org/en/learn/modules/backpressuring-in-streams)

<!-- End generated record details. -->
