---
id: "bloom-filter"
title: "Bloom filters for negative lookups"
category: "algorithms"
summary: "Reduce expensive negative membership lookups without treating probabilistic positives as authoritative."
aliases: ["bloom filter","probabilistic membership","false positive","bloom filtresi","username lookup","üyelik filtresi","kullanıcı adı müsait mi","varlığı hızlı kontrol etme"]
decisions: [{"when":"Negatives dominate and the filter is current","use":"Use a sized Bloom filter before the authoritative store, and verify every positive there.","tradeoff":"Memory and false-positive rate trade off, and rollout must handle freshness."},{"when":"Deletions or strict lookup freshness dominate","use":"Use an exact index or a counting filter with reviewed deletion behavior.","tradeoff":"Exactness or delete support can increase storage and rebuild work."}]
checks: ["Assert every inserted key passes before relying on negative responses.","Measure false positives under expected load and force a write during a filter rebuild.","For a counting filter, replay a deletion and exercise counter saturation with colliding keys."]
sources: [{"title":"Bloom’s space/time trade-off paper","url":"https://pages.cs.wisc.edu/~markhill/restricted/cacm70_bloom.pdf"},{"title":"Redis Bloom filter documentation","url":"https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/"},{"title":"Fan et al., Summary Cache, Bloom filter counters","url":"https://www.cs.princeton.edu/courses/archive/spr05/cos598E/bib/p254-fan.pdf"}]
---

<!-- Generated record title. -->
# Bloom filters for negative lookups

## Scenario

A package mirror receives many requests for object keys it has never stored. An origin check is significantly more expensive than a memory lookup.

## Failure modes

Capacity overruns increase false positives. Deleting bits can break other members, and a lagging filter can incorrectly reject newly inserted origin records.

## Explain it simply

The filter can rule out many misses quickly. A possible match still needs the authoritative lookup.

## Implementation guidance

Put the filter before a costly, authoritative read and size it with expected distinct keys and a false-positive budget. A negative may bypass the store only while the filter is known to cover the authoritative set. During rebuild or update lag, fall through to that store. Populate a replacement from a consistent snapshot plus subsequent writes before swapping it in. For a counting filter, decrement only for an insertion confirmed by an exact source. Guard against duplicate deletes and counter saturation because either can hide a colliding key that still exists. Record origin reads avoided, fallback reads and observed false positives separately.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Negatives dominate and the filter is current** Use a sized Bloom filter before the authoritative store, and verify every positive there. Memory and false-positive rate trade off, and rollout must handle freshness.
- **Deletions or strict lookup freshness dominate** Use an exact index or a counting filter with reviewed deletion behavior. Exactness or delete support can increase storage and rebuild work.

## Verification

- Assert every inserted key passes before relying on negative responses.
- Measure false positives under expected load and force a write during a filter rebuild.
- For a counting filter, replay a deletion and exercise counter saturation with colliding keys.

## Sources

- [Bloom’s space/time trade-off paper](https://pages.cs.wisc.edu/~markhill/restricted/cacm70_bloom.pdf)
- [Redis Bloom filter documentation](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)
- [Fan et al., Summary Cache, Bloom filter counters](https://www.cs.princeton.edu/courses/archive/spr05/cos598E/bib/p254-fan.pdf)

<!-- End generated record details. -->
