# Performance and capacity

Measure the symptom from a representative workload through a real entry point. Choose the relevant metric, such as p95 latency, maximum memory, query count, or queue delay. Establish an observed baseline before changing the design.

Profile I/O, CPU, contention, and allocation independently as needed. Tackle the largest verified cost. Avoid caching state before defining acceptable staleness, invalidation, and rebuild behavior. Bound concurrent work and buffer sizes according to a measured budget.

Repeat the baseline after the change with the same workload and verify functional behavior. Include worst credible input where a rare tail dominates user experience.
