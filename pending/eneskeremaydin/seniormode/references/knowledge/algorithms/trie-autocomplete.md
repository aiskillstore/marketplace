---
id: "trie-autocomplete"
title: "Prefix search with a trie"
category: "algorithms"
summary: "Deliver common prefix suggestions without scanning the whole dictionary per keystroke."
aliases: ["autocomplete","trie","prefix search","otomatik tamamlama","search suggestions","yazarken arama önerisi","harf ön eki","otomatik tamamlayan arama kutusu"]
decisions: [{"when":"Prefix queries dominate and rankings refresh predictably","use":"Index prefixes in a trie and cache bounded top suggestions at selected nodes.","tradeoff":"Precomputation increases memory and refresh work."},{"when":"The dictionary is small or updates are easy to batch","use":"Use a sorted normalized array with lower-bound prefix search.","tradeoff":"High-fan-out prefixes may need an additional bounded ranking step."}]
checks: ["Compare results against a full scan on accented, mixed-case and empty prefixes.","Test changed rankings and ensure the result count remains bounded."]
sources: [{"title":"Princeton Algorithms trie implementation","url":"https://algs4.cs.princeton.edu/52trie/TrieST.java.html"},{"title":"Python bisect documentation","url":"https://docs.python.org/3/library/bisect.html"}]
---

<!-- Generated record title. -->
# Prefix search with a trie

## Scenario

A support console offers issue labels as the operator types a few letters. The set is stable enough to refresh scores every minute.

## Failure modes

A trie can use more memory than a sorted array. Unicode normalization, ranking drift and prefixes with huge candidate sets need explicit handling.

## Explain it simply

Follow the typed letters down a tree and return a short list prepared for that prefix.

## Implementation guidance

Choose one normalization and use it for writes, lookups and prefix boundaries while keeping the original display label. With a sorted array, lower-bound search finds the beginning of the run, and prefix verification stops the scan. Cache bounded candidate lists only at nodes or prefixes that justify the extra memory, and define how score changes invalidate them. As a fixture, query composed and decomposed accented labels and verify the result limit and deterministic ties.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Prefix queries dominate and rankings refresh predictably** Index prefixes in a trie and cache bounded top suggestions at selected nodes. Precomputation increases memory and refresh work.
- **The dictionary is small or updates are easy to batch** Use a sorted normalized array with lower-bound prefix search. High-fan-out prefixes may need an additional bounded ranking step.

## Verification

- Compare results against a full scan on accented, mixed-case and empty prefixes.
- Test changed rankings and ensure the result count remains bounded.

## Sources

- [Princeton Algorithms trie implementation](https://algs4.cs.princeton.edu/52trie/TrieST.java.html)
- [Python bisect documentation](https://docs.python.org/3/library/bisect.html)

<!-- End generated record details. -->
