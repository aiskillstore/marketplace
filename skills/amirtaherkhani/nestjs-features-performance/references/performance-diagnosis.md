# Performance Diagnosis

Optimize the dominant constraint under a representative workload.

## Define the experiment

Record:

- route/message/job and payload distribution;
- concurrency and arrival pattern;
- warm-up and test duration;
- data volume and cache state;
- p50/p95/p99 latency, throughput, and errors;
- CPU, event-loop delay/utilization, heap, GC, and RSS;
- database query/pool/lock metrics;
- external dependency spans;
- queue depth, age, and processing duration.

Change one major variable at a time. Compare the same workload and environment.

## Event loop and CPU

Node.js serves many clients with a small number of threads. A long synchronous callback delays unrelated requests and can become a denial-of-service vector when input controls its cost.

Inspect for:

- synchronous filesystem/crypto/compression calls in request paths;
- large JSON parse/stringify or validation;
- unbounded loops, regex backtracking, sorting, and transformations;
- image/PDF/media processing;
- expensive logging or stack creation;
- synchronous password hashing or encryption misuse.

Remedies:

- bound input and algorithmic work;
- use asynchronous APIs for I/O;
- stream or partition large work where appropriate;
- move CPU-heavy work to a pooled worker thread or separate worker process;
- queue work when the result may be asynchronous and durable.

Worker threads help CPU-intensive JavaScript; they usually do not improve ordinary asynchronous I/O. Use a pool instead of spawning one worker per request.

## Provider scope

Singleton is the default and preferred scope. Request-scoped providers are recreated for every request, and scope bubbles to their consumers.

Measure before using request scope broadly. Prefer explicit principals/context or an existing request-context mechanism when it keeps the graph singleton-safe. Never store per-request data in singleton fields.

## Framework loading and lifecycle

Do not present lazy-loaded modules or lifecycle hooks as generic performance optimizations.

- Lifecycle hooks coordinate initialization and shutdown correctness. Keep startup work bounded and observable, but optimize it only when startup measurements and deployment requirements identify a problem.
- Nest lazy-loading support is useful for niche, optional dependency graphs. It adds wiring and first-use complexity and does not automatically reduce steady-state request latency or memory.
- Dynamic imports, deferred initialization, and lazy modules can shift cost to the first request. Measure cold start, first-use latency, readiness, memory, and failure behavior before and after.
- Avoid discovering dependencies at runtime merely to defer construction; preserve explicit provider contracts and verify the installed NestJS API.

## Database

Database latency often dominates framework overhead.

Check:

- N+1 query patterns;
- missing or unused indexes for real predicates/order;
- unbounded results and offset pagination at large depth;
- overfetching wide rows/relations;
- pool waits, leaked connections, and mismatched pool size;
- long transactions and lock contention;
- read-then-write races and missing constraints;
- repeated counts/aggregations on hot paths.

Use query plans and production-like data. An index accelerates some reads while adding write/storage cost; do not add one from column names alone.

Keep external network calls outside database transactions whenever correctness permits.

## External calls

- Set a deadline/timeout for every dependency call.
- Reuse connections/agents according to the client library.
- Propagate cancellation where supported.
- Retry only transient, safe operations within a total time budget.
- Bound concurrency to protect both systems.
- Use circuit breaking or load shedding only with explicit recovery behavior.

Parallelize independent calls only when it reduces latency without overwhelming downstream capacity.

## Memory and payloads

Look for retained request data, unbounded maps/listeners, large buffers, ORM relation graphs, and full in-memory exports.

Use heap snapshots/allocation profiling to identify retainers. Stream or page large data; remove listeners/timers; bound caches. Increasing the heap may delay failure but does not repair a leak.

## Caching

Cache only after identifying repeated expensive work and acceptable staleness. Measure hit ratio, load time, eviction, memory, and origin impact.

Protect against stampedes with single-flight/locking, early refresh, or jittered TTL where appropriate. Include tenant, locale, permissions, and representation in keys when they change the result.

## Express versus Fastify

Fastify can improve HTTP-layer throughput, but application latency may be dominated by database or network work. Before migration:

1. profile and isolate HTTP adapter overhead;
2. inventory Express-specific middleware and response APIs;
3. benchmark representative routes, validation, serialization, and logging;
4. run all transport/e2e tests;
5. verify deployment binding and proxy behavior.

Do not quote generic framework benchmarks as proof for this application.

## Logging and observability overhead

Use structured logs with appropriate levels and redaction. Avoid serializing complete bodies, ORM entities, buffers, or stack traces on every successful request. Sample high-volume traces deliberately while retaining errors and critical transactions.

## Result format

```text
Baseline: workload + p95/p99 + throughput + errors
Bottleneck: evidence and dominant span/resource
Change: one intervention
Result: same metrics after change
Correctness: tests and failure behavior
Capacity: new saturation point and next limiting dependency
```

See Node.js guidance on [event-loop safety](https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop) and [worker threads](https://nodejs.org/api/worker_threads.html), plus NestJS guidance on [injection scope](https://docs.nestjs.com/fundamentals/injection-scopes) and [Fastify](https://docs.nestjs.com/techniques/performance).
