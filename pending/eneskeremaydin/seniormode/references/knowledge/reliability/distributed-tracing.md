---
id: "distributed-tracing"
title: "Distributed tracing and sampling"
category: "reliability"
summary: "Connect a slow or failed user interaction to its upstream and downstream work with affordable trace coverage."
aliases: ["distributed tracing","trace context","spans","open telemetry","sampling latency","dağıtık izleme","isteğin servisler arasında izini sürme","gecikme hangi serviste başladı"]
decisions: [{"when":"Work spans independently observed components","use":"Propagate standard trace context and instrument defined boundaries with safe tags.","tradeoff":"Span collection and sampling add overhead and require retention controls."},{"when":"One local process is the only bottleneck","use":"Start with latency metrics and targeted profiling before adding cross-service tracing.","tradeoff":"Metrics show distribution but provide less detail for a single operation."}]
checks: ["Trace a request across a queued job and ensure privacy-sensitive inputs are absent.","Induce a tail-latency problem and verify sampled traces can show the cause."]
sources: [{"title":"W3C Trace Context","url":"https://www.w3.org/TR/trace-context/"},{"title":"OpenTelemetry tracing concepts","url":"https://opentelemetry.io/docs/concepts/signals/traces/"}]
---

<!-- Generated record title. -->
# Distributed tracing and sampling

## Scenario

A search path spans an API, a cache and a remote ranking worker. Tail latency sometimes rises while aggregate metrics look stable.

## Failure modes

Missing propagation breaks traces. Parent-only sampling can miss rare errors, and labels with user data can leak information.

## Explain it simply

Follow a request through the system and measure where its time was spent.

## Architecture notes

Propagate trace context across synchronous and queued stages, with spans where ownership or waiting changes. Keep sensitive search input out of attributes and cap cardinality. Choose sampling that keeps enough error traces to explain tail failures. Reproduce a downstream failure and verify context retention across handoff and retry.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Work spans independently observed components** Propagate standard trace context and instrument defined boundaries with safe tags. Span collection and sampling add overhead and require retention controls.
- **One local process is the only bottleneck** Start with latency metrics and targeted profiling before adding cross-service tracing. Metrics show distribution but provide less detail for a single operation.

## Verification

- Trace a request across a queued job and ensure privacy-sensitive inputs are absent.
- Induce a tail-latency problem and verify sampled traces can show the cause.

## Sources

- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [OpenTelemetry tracing concepts](https://opentelemetry.io/docs/concepts/signals/traces/)

<!-- End generated record details. -->
