---
id: "lru-cache"
title: "LRU cache eviction and admission"
category: "data"
summary: "Choose an eviction policy by comparing access locality, memory cost and workload skew."
aliases: ["lru cache","least recently used","lfu","önbellek tahliyesi","linked list eviction","en uzun süredir kullanılmayanı sil","kapasite dolunca hangi kayıt silinir"]
decisions: [{"when":"Recent use predicts reuse and bounds are simple","use":"Use a bounded LRU with reliable recency updates and track bytes where entries vary in size.","tradeoff":"A one-time scan can still evict frequently used entries."},{"when":"Repeated frequency matters more than short-term recency","use":"Compare LFU or admission policies against replayed access traces.","tradeoff":"Additional state and aging logic increase implementation cost."}]
checks: ["Test hits, evictions, updates to existing keys and the exact capacity boundary.","Replay a scan-heavy trace and report hit rate and bytes alongside runtime."]
sources: [{"title":"Redis key eviction policies","url":"https://redis.io/docs/latest/develop/reference/eviction/"},{"title":"OpenJDK LinkedHashMap implementation","url":"https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/LinkedHashMap.java"}]
---

<!-- Generated record title. -->
# LRU cache eviction and admission

## Scenario

A local thumbnail decoder has a fixed memory budget. Recently viewed items are likely to be reopened, but a large scan can displace them.

## Failure modes

Entry count ignores object size and scans can evict the working set. Mutating the recency list and lookup table separately risks inconsistency.

## Explain it simply

When the cache fills up, remove the item that has gone unused longest if recent use predicts what comes next.

## Implementation guidance

Combine lookup and recency updates behind one synchronization boundary. If thumbnails vary greatly, account in decoded bytes and define what happens when a single item exceeds the cache budget. Update weight for replacement and remove entries until the total fits. Replay a hot working set followed by a one-off scan to compare hit rate and memory against a frequency or admission policy.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Recent use predicts reuse and bounds are simple** Use a bounded LRU with reliable recency updates and track bytes where entries vary in size. A one-time scan can still evict frequently used entries.
- **Repeated frequency matters more than short-term recency** Compare LFU or admission policies against replayed access traces. Additional state and aging logic increase implementation cost.

## Verification

- Test hits, evictions, updates to existing keys and the exact capacity boundary.
- Replay a scan-heavy trace and report hit rate and bytes alongside runtime.

## Sources

- [Redis key eviction policies](https://redis.io/docs/latest/develop/reference/eviction/)
- [OpenJDK LinkedHashMap implementation](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/LinkedHashMap.java)

<!-- End generated record details. -->
