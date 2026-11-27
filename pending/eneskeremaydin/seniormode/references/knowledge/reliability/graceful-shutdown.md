---
id: "graceful-shutdown"
title: "Graceful shutdown and work draining"
category: "reliability"
summary: "Stop accepting new work, finish safe in-flight operations and leave unfinished work recoverable."
aliases: ["graceful shutdown","sigterm","connection draining","rolling shutdown","stop accepting traffic","kapanırken aktif istekleri bitirme","zarif durdurma","dağıtım sırasında işi bırakma"]
decisions: [{"when":"The platform gives a timed shutdown grace period","use":"Mark unready, drain requests, honor cancellation and requeue work before deadline.","tradeoff":"Long operations may still need checkpoints and idempotency."},{"when":"Fast abrupt termination is expected under failures","use":"Design durable boundaries and recovery independent of shutdown hooks.","tradeoff":"More persistent state is needed, even though planned drains can reduce interruption."}]
checks: ["Terminate during a request and during durable processing, then verify behavior on restart.","Assert deadline expiration leaves no indefinitely held lease."]
sources: [{"title":"Kubernetes pod lifecycle and termination","url":"https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/"},{"title":"Node.js process signal events","url":"https://nodejs.org/api/process.html#signal-events"}]
---

<!-- Generated record title. -->
# Graceful shutdown and work draining

## Scenario

A service receives a deployment termination signal while a long upload and queued jobs are running.

## Failure modes

An unregister step can race incoming traffic. Termination during an acknowledged but uncommitted stage can lose work or cause duplicate processing.

## Explain it simply

Stop admitting new work, finish what fits in the shutdown window and leave the rest ready to resume.

## Implementation guidance

Mark the instance unready, stop admitting work and let in-flight requests reach their durable boundary until a deadline. Reschedule work that cannot finish and make the next attempt safe. Close shared resources after workers stop using them. Rehearse termination with accepted, committing and queued operations, then repeat with an abrupt kill.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The platform gives a timed shutdown grace period** Mark unready, drain requests, honor cancellation and requeue work before deadline. Long operations may still need checkpoints and idempotency.
- **Fast abrupt termination is expected under failures** Design durable boundaries and recovery independent of shutdown hooks. More persistent state is needed, even though planned drains can reduce interruption.

## Verification

- Terminate during a request and during durable processing, then verify behavior on restart.
- Assert deadline expiration leaves no indefinitely held lease.

## Sources

- [Kubernetes pod lifecycle and termination](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Node.js process signal events](https://nodejs.org/api/process.html#signal-events)

<!-- End generated record details. -->
