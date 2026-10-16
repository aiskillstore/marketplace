# R2 and Workers KV

Default scope is offline, read-only source review; do not query a live account. Use runtime metrics only if the user separately supplies redacted evidence. Distinguish storage operation, retrieval, data volume and duration. A storage binding alone is not a risk finding.

## CF-R2-OPERATION-AMPLIFICATION — repeated replication, metadata or event cycles
- Risk conditions: replication lacks a delay/bound, hot paths repeatedly list/head objects, or R2 notification → Queue/Worker → R2 write forms a cycle.
- Check: call chain for put/get/list/head, replication interval, notification filters, prefixes and whether output objects trigger input events.
- Mitigation and trade-off: set replication cadence, filter events, separate input/output prefixes, deduplicate, batch and cache. Caching may be stale; filtering can skip needed events.
- Blind spots: an R2 event loop is not implied by every event binding; no external traffic or bill should be assumed without evidence.
- Evidence: caseId lucianghinda-r2-replication; guideIds sarmaasis-cloudflare-under-five-dollars, davezfr-four-layer-cost-protection; official sourceIds CF-DOC-R2-PRICING, CF-DOC-R2-METRICS.

## CF-KV-HOTPATH-OPERATIONS — many-key reads/writes or listings
- Risk conditions: a public/hot route repeatedly reads/writes/deletes/lists keys, including misses, without cache, key-count bound or quota; or a shared quota/counter relies on a KV read-modify-write as if it were an atomic global reservation.
- Check: route → get/put/delete/list; estimate calls per request, key cardinality, retries and storage lifecycle. Listing all keys on a request path merits review. For shared counters, check concurrency and consistency semantics: KV is eventually consistent and does not provide atomic multi-operation transactions; concurrent same-key writes can overwrite one another. Verify any stronger quota authority covers all relevant callers and actually reserves/updates atomically.
- Mitigation and trade-off: cache, reduce writes, avoid hot-path listing, bound key batches and add per-user quotas. If a strict shared bound is needed, use a verified transactional/serialized coordinator (for example one Durable Object per quota identity) and account for its own requests/storage and per-key throughput; do not imply KV alone enforces that bound. Cache can serve stale values, and a central coordinator can reject legitimate work or become a bottleneck; sharding keys does not create an aggregate spend limit.
- Blind spots: the cited Billflare case set has no KV-specific incident precedent; the quota warning is a documented product-consistency boundary, not an observed user failure. Source code alone may not establish that every ingress shares the same quota authority or that an external side effect is transactional with its reservation.
- Evidence: guideIds sarmaasis-cloudflare-under-five-dollars, cf-usage-guard; official sourceIds CF-DOC-KV-PRICING, CF-DOC-KV-FAQ (related page CF-DOC-KV-CONSISTENCY and KV writes), CF-DOC-DO-BASE (related page CF-DOC-DO-STORAGE). Checked 2026-10-12.
