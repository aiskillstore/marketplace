---
id: "count-min-sketch"
title: "Count-Min Sketch for approximate frequency"
category: "algorithms"
summary: "Estimate high-volume event counts within bounded memory while preserving ranking semantics."
aliases: ["count min sketch","heavy hitters","trending hashtags","yaklaşık sayaç","top k","popüler etiket sayımı","yaklaşık frekans","yükselen başlıklara sayaç"]
decisions: [{"when":"There are many keys and estimates are acceptable","use":"Use independently seeded rows and the minimum tracked count with a bounded candidate list.","tradeoff":"Counts can overestimate and windowing consumes additional memory."},{"when":"Accurate billable or regulatory counts are required","use":"Use exact counters in a durable store or compute exact aggregates from the event log.","tradeoff":"Storage and processing grow with cardinality."}]
checks: ["Compare estimates with exact counts, including colliding rare keys.","Test whether a sudden burst is visible after the window advances."]
sources: [{"title":"Count-Min Sketch original paper","url":"https://www.cs.ox.ac.uk/people/graham.cormode/pubs/html/CormodeMuthukrishnan04CMJalg.html"},{"title":"Redis Count-Min Sketch documentation","url":"https://redis.io/docs/latest/develop/data-types/probabilistic/count-min-sketch/"}]
---

<!-- Generated record title. -->
# Count-Min Sketch for approximate frequency

## Scenario

An event collector wants fast indicators of surging error labels. The set of labels is large and must fit inside a fixed memory budget.

## Failure modes

Collisions overestimate frequencies for nonnegative updates. The sketch cannot enumerate the keys by itself and historical volume can conceal changes in recent activity.

## Explain it simply

Use a small shared table for rough counts and keep a short list of labels worth checking more closely.

## Implementation guidance

Hash each nonnegative update once per row and use the minimum corresponding counter as the query estimate. Keep candidates in a separate bounded heavy-hitter structure or stream of labels since the counters cannot reconstruct keys. Configure a time window explicitly for surge detection so an old popular label does not mask a new spike. Compare the sketch and its candidate selection against exact aggregates on a replay that includes collisions and overdue window rotations.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **There are many keys and estimates are acceptable** Use independently seeded rows and the minimum tracked count with a bounded candidate list. Counts can overestimate and windowing consumes additional memory.
- **Accurate billable or regulatory counts are required** Use exact counters in a durable store or compute exact aggregates from the event log. Storage and processing grow with cardinality.

## Verification

- Compare estimates with exact counts, including colliding rare keys.
- Test whether a sudden burst is visible after the window advances.

## Sources

- [Count-Min Sketch original paper](https://www.cs.ox.ac.uk/people/graham.cormode/pubs/html/CormodeMuthukrishnan04CMJalg.html)
- [Redis Count-Min Sketch documentation](https://redis.io/docs/latest/develop/data-types/probabilistic/count-min-sketch/)

<!-- End generated record details. -->
