---
id: "property-based-testing"
title: "Property-based tests for invariants"
category: "testing"
summary: "Explore input combinations with reproducible generators and meaningful invariants."
aliases: ["property based testing","fast check","generative testing","invariants","shrinking","özellik tabanlı test","rastgele girdilerle değişmezi doğrula","en küçük başarısız örneği bul"]
decisions: [{"when":"Behavioral invariants or a reference oracle are available","use":"Generate boundary-rich inputs, assert the properties and record reproducible failure seeds.","tradeoff":"Developers must choose strong properties and constrain test budgets."},{"when":"A narrow product rule has only a few meaningful cases","use":"Start with explicit examples including one failing case and a boundary.","tradeoff":"Examples are readable but explore fewer combinations."}]
checks: ["Introduce a deliberately broken implementation and verify a property fails.","Replay one reported failure from its seed and preserve it as a regression case."]
sources: [{"title":"fast-check documentation","url":"https://fast-check.dev/docs/introduction/"},{"title":"Hypothesis documentation","url":"https://hypothesis.readthedocs.io/"}]
related: ["music-shuffle"]
---

<!-- Generated record title. -->
# Property-based tests for invariants

## Scenario

A date range utility must normalize arbitrary ranges, merge overlaps and preserve coverage over a bounded interval.

## Failure modes

A property can be true for a broken trivial implementation. Unseeded failures are hard to reproduce and generators can avoid the edge of interest.

## Explain it simply

Check a rule that must hold for many inputs and save the smallest example when the rule fails.

## Worked example

For normalized date ranges, compare input and output coverage on a small discrete reference domain, check sorted nonoverlapping output, and require applying normalization twice to yield the same result. Generate empty, adjacent, nested and extreme ranges. Keep the minimized failure and its seed for replay and add a direct regression even if the generator changes.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Behavioral invariants or a reference oracle are available** Generate boundary-rich inputs, assert the properties and record reproducible failure seeds. Developers must choose strong properties and constrain test budgets.
- **A narrow product rule has only a few meaningful cases** Start with explicit examples including one failing case and a boundary. Examples are readable but explore fewer combinations.

## Verification

- Introduce a deliberately broken implementation and verify a property fails.
- Replay one reported failure from its seed and preserve it as a regression case.

## Sources

- [fast-check documentation](https://fast-check.dev/docs/introduction/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)

## Related decisions

- [Shuffle semantics and perceived variety](../product/music-shuffle.md)

<!-- End generated record details. -->
