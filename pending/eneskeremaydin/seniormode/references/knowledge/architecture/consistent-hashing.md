---
id: "consistent-hashing"
title: "Sharding and consistent hashing"
category: "architecture"
summary: "Assign keys to changing storage or worker sets while limiting unnecessary movement."
aliases: ["consistent hashing","virtual nodes","hash ring","resharding","tutarlı hash dağıtımı","sunucu ekleyince kayıtları taşıma","tutarlı karma","yeniden bölümleme"]
decisions: [{"when":"The worker set changes frequently","use":"Use a consistent hash ring or rendezvous hashing with agreed membership and controlled handoff.","tradeoff":"Rebalancing still needs migration and monitoring for skew."},{"when":"The partition count is stable and transparent routing is valuable","use":"Use fixed virtual partitions and an explicit assignment table.","tradeoff":"A coordinator maintains assignments, but moving one partition is predictable."}]
checks: ["Measure moved-key fraction and imbalance after membership changes.","Check staged handoff and retries during a partition transfer."]
sources: [{"title":"Amazon Dynamo paper","url":"https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf"},{"title":"Apache Kafka documentation","url":"https://kafka.apache.org/documentation/"}]
---

<!-- Generated record title. -->
# Sharding and consistent hashing

## Scenario

A messaging service partitions conversation work. New workers are added before seasonal bursts without moving most conversations.

## Failure modes

Modulo routing changes many assignments when the worker count changes. A single hot key remains hot, and uncoordinated metadata updates can route writes twice.

## Explain it simply

Put the partitions on a shared map so adding a worker moves only the keys it should take over.

## Implementation guidance

Agree on the key encoding, hash and membership revision before moving data. Use a shared partition map or virtual nodes to reduce uneven movement, with destination readiness and a fenced owner change before switching writes. Hashing redistributes keys, so treat a single high-volume conversation separately instead of expecting topology changes to split its work. Test both removed and added members, and measure key movement and load skew on a representative distribution.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The worker set changes frequently** Use a consistent hash ring or rendezvous hashing with agreed membership and controlled handoff. Rebalancing still needs migration and monitoring for skew.
- **The partition count is stable and transparent routing is valuable** Use fixed virtual partitions and an explicit assignment table. A coordinator maintains assignments, but moving one partition is predictable.

## Verification

- Measure moved-key fraction and imbalance after membership changes.
- Check staged handoff and retries during a partition transfer.

## Sources

- [Amazon Dynamo paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Apache Kafka documentation](https://kafka.apache.org/documentation/)

<!-- End generated record details. -->
