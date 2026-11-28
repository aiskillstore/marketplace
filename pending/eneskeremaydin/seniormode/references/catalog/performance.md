# Performance and capacity

- [Streaming transforms with bounded memory](../knowledge/performance/bounded-memory-streaming.md) · Transform large input incrementally while bounding buffers and preserving failure semantics.
- [Cache stampede and prewarming](../knowledge/performance/cache-stampede.md) · Protect an expensive origin when a popular cache entry is missing or expires.
- [Profiling before performance optimization](../knowledge/performance/latency-profiling.md) · Use a reproducible profile to select optimizations that matter to a real bottleneck.
- [N+1 queries and bounded batching](../knowledge/performance/n-plus-one-queries.md) · Remove repeated per-item reads while bounding response size and preserving access rules.
- [Queue capacity and latency budgeting](../knowledge/performance/queue-capacity-planning.md) · Size queue and worker capacity using arrival rate, service rate and an explicit latency objective.
- [Virtual waiting rooms for traffic spikes](../knowledge/performance/virtual-waiting-room.md) · Meter entry to a scarce service while making fairness and failure behavior explicit.
