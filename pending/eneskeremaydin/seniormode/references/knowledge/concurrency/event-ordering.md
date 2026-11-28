---
id: "event-ordering"
title: "Event ordering and versioned consumers"
category: "concurrency"
summary: "Preserve the ordering boundary that matters to correctness while allowing unrelated work to proceed."
aliases: ["out of order events","versioned events","partition key","event sequence","causal order","olaylar ters sırayla geliyor","eski olay yeni kaydı eziyor","varlık bazında olay sırası"]
decisions: [{"when":"Each event replaces the full state relevant to the consumer","use":"Apply a snapshot only if its source version is newer than the stored version.","tradeoff":"Intermediate versions may be skipped, so each accepted snapshot must carry complete replacement state."},{"when":"Each mutation depends on earlier mutations for the same entity","use":"Partition by entity and verify the expected next event before applying the mutation.","tradeoff":"Hot entities can become local bottlenecks and missing events need bounded recovery."}]
checks: ["Deliver destination snapshots 42 then 41 and verify that version 42 remains visible.","Deliver dependent deltas 42 then 41 and verify the consumer recovers the gap and applies both once in order."]
sources: [{"title":"Apache Kafka introduction, keyed partitions and read order","url":"https://kafka.apache.org/43/getting-started/introduction/"},{"title":"Lamport, Time, Clocks and Ordering","url":"https://lamport.azurewebsites.net/pubs/time-clocks.pdf"}]
---

<!-- Generated record title. -->
# Event ordering and versioned consumers

## Scenario

A customer updates a shipping destination twice. Delivery retries may complete the older event after the newer one.

## Failure modes

Global ordering limits throughput. Broker delivery order alone cannot protect parallel handlers, and clocks are weak sequence numbers.

## Explain it simply

Give each account's changes an order and let unrelated accounts be processed independently.

## Implementation guidance

Assign each full shipping destination snapshot a source version. Compare and advance that version in the same transaction as the state change, so snapshot 41 cannot overwrite snapshot 42. For an order-sensitive delta stream, such as reserve then release, advance state only when the delta matches the expected next source position. Use a contiguous sequence or an explicit predecessor if the producer legitimately skips version numbers. On a gap, hold the delta and recover through replay or an authoritative snapshot. Define a bounded escalation path when recovery fails. Reordering commutative operations can be safe, while a retried increment still needs deduplication. Test concurrent handlers and a restart while a gap is pending.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Each event replaces the full state relevant to the consumer** Apply a snapshot only if its source version is newer than the stored version. Intermediate versions may be skipped, so each accepted snapshot must carry complete replacement state.
- **Each mutation depends on earlier mutations for the same entity** Partition by entity and verify the expected next event before applying the mutation. Hot entities can become local bottlenecks and missing events need bounded recovery.

## Verification

- Deliver destination snapshots 42 then 41 and verify that version 42 remains visible.
- Deliver dependent deltas 42 then 41 and verify the consumer recovers the gap and applies both once in order.

## Sources

- [Apache Kafka introduction, keyed partitions and read order](https://kafka.apache.org/43/getting-started/introduction/)
- [Lamport, Time, Clocks and Ordering](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)

<!-- End generated record details. -->
