---
id: "latency-profiling"
title: "Profiling before performance optimization"
category: "performance"
summary: "Use a reproducible profile to select optimizations that matter to a real bottleneck."
aliases: ["profiling","performance measurement","flamegraph","latency regression","cpu hotspot","performans sorununu ölçerek bulma","gecikmenin kaynağını ölç","işlemci profili"]
decisions: [{"when":"A representative slow workload can be reproduced","use":"Measure an end-to-end baseline, then profile CPU, allocation or blocked time as appropriate.","tradeoff":"Profiles have overhead and need representative data."},{"when":"The issue occurs only intermittently in a running service","use":"Add narrowly scoped latency and dependency signals before high-overhead profiling.","tradeoff":"The first measurements may reveal only where to investigate next."}]
checks: ["Compare before and after under the same dataset and environment.","Verify correctness, tail latency and resource trade-offs did not regress."]
sources: [{"title":"Node.js guide to profiling applications","url":"https://nodejs.org/en/learn/getting-started/profiling"},{"title":"Brendan Gregg’s USE Method","url":"https://www.brendangregg.com/usemethod.html"}]
---

<!-- Generated record title. -->
# Profiling before performance optimization

## Scenario

A command line import tool is perceived as slow, but elapsed time could come from I/O, parsing or contention.

## Failure modes

Microbenchmarks of the wrong function can improve a metric without changing user latency. Cold-start and warm-state behavior may differ.

## Explain it simply

Find where the operation spends time before changing how it works, then measure the whole task again.

## When not to use

Start with the slow workflow and split elapsed time into parsing, storage, dependency waits and local work. A CPU profile is a poor fit for throughput stalls with idle CPU. Measure waiting and queue occupancy first. Record representative workload, warm-up, cache state and resource usage, then compare the end-to-end latency and memory after tuning.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A representative slow workload can be reproduced** Measure an end-to-end baseline, then profile CPU, allocation or blocked time as appropriate. Profiles have overhead and need representative data.
- **The issue occurs only intermittently in a running service** Add narrowly scoped latency and dependency signals before high-overhead profiling. The first measurements may reveal only where to investigate next.

## Verification

- Compare before and after under the same dataset and environment.
- Verify correctness, tail latency and resource trade-offs did not regress.

## Sources

- [Node.js guide to profiling applications](https://nodejs.org/en/learn/getting-started/profiling)
- [Brendan Gregg’s USE Method](https://www.brendangregg.com/usemethod.html)

<!-- End generated record details. -->
