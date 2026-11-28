---
id: "binary-search"
title: "Binary search and boundary conditions"
category: "algorithms"
summary: "Find a position in ordered data while making the boundary and duplicate semantics explicit."
aliases: ["binary search","sorted lookup","lower bound","ikili arama","binary search overflow","sıralı listede arananı bulma","sıralı dizide ilk eşleşme"]
decisions: [{"when":"The input is ordered and random access is cheap","use":"Use a half-open lower-bound search with an explicit monotone predicate.","tradeoff":"The index must retain a compatible ordering and comparison rule."},{"when":"There are very few items or no stable ordering","use":"Measure a linear scan or build an index only when repeated searches justify it.","tradeoff":"A scan is simple but grows linearly with input size."}]
checks: ["Test empty, singleton, equal timestamps and keys beyond both ends.","Compare search results with a linear oracle across randomized ordered inputs."]
sources: [{"title":"C++ working draft binary search","url":"https://eel.is/c++draft/alg.binary.search"},{"title":"Python bisect documentation","url":"https://docs.python.org/3/library/bisect.html"}]
---

<!-- Generated record title. -->
# Binary search and boundary conditions

## Scenario

An export tool seeks the first event at or after a requested timestamp in an immutable sorted index. Many events have identical timestamps.

## Failure modes

Unstable ordering invalidates the invariant. Inclusive/exclusive bounds can loop on adjacent elements and overflow-prone midpoints can fail in fixed-width arithmetic.

## Explain it simply

Each comparison rules out half the remaining positions until the first eligible event is found.

## Implementation guidance

Keep a half-open interval [lo, hi) and define the result as the first index whose predicate is true, or the length when every element fails. For duplicates [10, 20, 20, 35], a lower bound of 20 returns index 1 and an upper bound returns index 3. For fixed-width integers, compute the midpoint from lo and the difference hi - lo. Compare both bounds with a linear oracle on empty input, all-equal values, and a target just beyond the largest value.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The input is ordered and random access is cheap** Use a half-open lower-bound search with an explicit monotone predicate. The index must retain a compatible ordering and comparison rule.
- **There are very few items or no stable ordering** Measure a linear scan or build an index only when repeated searches justify it. A scan is simple but grows linearly with input size.

## Verification

- Test empty, singleton, equal timestamps and keys beyond both ends.
- Compare search results with a linear oracle across randomized ordered inputs.

## Sources

- [C++ working draft binary search](https://eel.is/c++draft/alg.binary.search)
- [Python bisect documentation](https://docs.python.org/3/library/bisect.html)

<!-- End generated record details. -->
