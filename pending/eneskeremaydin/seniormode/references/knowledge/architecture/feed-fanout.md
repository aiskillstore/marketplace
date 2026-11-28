---
id: "feed-fanout"
title: "Timeline delivery and fan-out"
category: "architecture"
summary: "Balance write amplification, read latency and fan-out lag for a personalized feed."
aliases: ["fan out on write","fan out on read","activity feed","instagram akışı","timeline delivery","newsfeed fanout","celebrity followers","timeline materialization","takipçilerin ana sayfa akışı","gönderileri önceden hazırla","çok takipçili hesapların akışı"]
decisions: [{"when":"Followers are moderate and read latency dominates","use":"Materialize candidate post IDs asynchronously with idempotent inserts.","tradeoff":"Write cost scales with follower count and feeds can lag."},{"when":"Fan-out would be disproportionately large","use":"Merge high-fan-out publisher streams on read with per-user candidates.","tradeoff":"Reads cost more and require stable ordering and deduplication."}]
checks: ["Measure typical and high-fan-out publisher delivery lag separately.","Verify unfollow, deletion and replay without duplicate feed entries."]
sources: [{"title":"Raffi Krikorian’s Timelines at Scale talk on write-time fan-out","url":"https://www.infoq.com/presentations/Twitter-Timeline-Scalability/"},{"title":"Mike Cvet’s QCon talk on read-time timeline fan-in","url":"https://qconsf.com/sf2016/sf2016/presentation/how-we-learned-stop-worrying-and-love-fan.html"}]
related: ["cursor-pagination","transactional-outbox"]
---

<!-- Generated record title. -->
# Timeline delivery and fan-out

## Scenario

A forum offers a timeline of followed writers. Most writers have dozens of subscribers, while a few have millions.

## Failure modes

Large publishers can create queue backlogs and repeated inserts. Follow changes, deletions and privacy changes need semantics for already materialized entries.

## Explain it simply

Prepare busy readers’ lists ahead of time and merge posts from very large publishers when the list opens.

## Implementation guidance

Use measured burst posting and read load to place publishers on the materialize or merge path. Store materialized entries with a stable user/post identity so delivery retry is harmless, then merge both candidate streams under one stable ordering before slicing. Recheck deletion and authorization against a sufficiently fresh authoritative view before serving. Compare per-cohort backlog age and read tail latency with large-publisher bursts, and check for gaps or repeats when a publisher moves between paths.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Followers are moderate and read latency dominates** Materialize candidate post IDs asynchronously with idempotent inserts. Write cost scales with follower count and feeds can lag.
- **Fan-out would be disproportionately large** Merge high-fan-out publisher streams on read with per-user candidates. Reads cost more and require stable ordering and deduplication.

## Verification

- Measure typical and high-fan-out publisher delivery lag separately.
- Verify unfollow, deletion and replay without duplicate feed entries.

## Sources

- [Raffi Krikorian’s Timelines at Scale talk on write-time fan-out](https://www.infoq.com/presentations/Twitter-Timeline-Scalability/)
- [Mike Cvet’s QCon talk on read-time timeline fan-in](https://qconsf.com/sf2016/sf2016/presentation/how-we-learned-stop-worrying-and-love-fan.html)

## Related decisions

- [Stable cursor pagination](../backend/cursor-pagination.md)
- [Transactional outbox and reliable delivery](transactional-outbox.md)

<!-- End generated record details. -->
