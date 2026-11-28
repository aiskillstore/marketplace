---
id: "queue-capacity-planning"
title: "Queue capacity and latency budgeting"
category: "performance"
summary: "Size queue and worker capacity using arrival rate, service rate and an explicit latency objective."
aliases: ["queue capacity","little law","service rate","queue lag","latency budget","kuyruk kapasitesi hesaplama","iş gelme hızı ve işçi kapasitesi","kuyruk bekleme süresi"]
decisions: [{"when":"Demand spikes are short and completion can lag briefly","use":"Use a bounded queue and measure time-to-drain against expected bursts.","tradeoff":"Users may wait, and queue growth needs admission limits."},{"when":"Demand stays above safe service capacity","use":"Scale the measured bottleneck or reject/defer work within explicit service policies.","tradeoff":"Scaling the wrong stage leaves the bottleneck in place."}]
checks: ["Measure arrival, completion and age under a representative burst.","Verify predictable degradation and bounded storage during sustained overload."]
sources: [{"title":"Google SRE on handling overload","url":"https://sre.google/sre-book/handling-overload/"},{"title":"MIT Operations Research, distributional Little’s law","url":"https://dspace.mit.edu/entities/publication/19154c66-e8bf-47ec-8ba7-fbe4e0345ff3"}]
---

<!-- Generated record title. -->
# Queue capacity and latency budgeting

## Scenario

A file processing service drains 50 jobs per minute, yet during a promotion receives more than 80 for an extended period.

## Failure modes

An unlimited buffer turns overload into latency and memory growth. Mean service time misses tail impact and heterogeneous job sizes.

## Explain it simply

Set how much work can wait and track whether workers can keep up for the periods that matter.

## Worked example

A service accepting 80 jobs and completing 50 each minute grows its backlog by about 30 jobs a minute while those rates hold. Choose a cap from acceptable queueing time, deadlines and memory. Measure oldest-job age and service times by job class. Stop arrivals after a controlled burst and compare actual drain time and rejection behavior with the plan.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Demand spikes are short and completion can lag briefly** Use a bounded queue and measure time-to-drain against expected bursts. Users may wait, and queue growth needs admission limits.
- **Demand stays above safe service capacity** Scale the measured bottleneck or reject/defer work within explicit service policies. Scaling the wrong stage leaves the bottleneck in place.

## Verification

- Measure arrival, completion and age under a representative burst.
- Verify predictable degradation and bounded storage during sustained overload.

## Sources

- [Google SRE on handling overload](https://sre.google/sre-book/handling-overload/)
- [MIT Operations Research, distributional Little’s law](https://dspace.mit.edu/entities/publication/19154c66-e8bf-47ec-8ba7-fbe4e0345ff3)

<!-- End generated record details. -->
