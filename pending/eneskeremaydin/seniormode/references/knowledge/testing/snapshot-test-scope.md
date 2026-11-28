---
id: "snapshot-test-scope"
title: "Focused snapshots for stable outputs"
category: "testing"
summary: "Use snapshot tests where reviewing the full stable output adds value and keep updates intentional."
aliases: ["snapshot test","golden file","approved output","snapshot drift","deterministic serialization","anlık görüntü testi","beklenen çıktı dosyası","testte değişken zaman damgası"]
decisions: [{"when":"The serialized output is a meaningful, stable interface","use":"Normalize incidental environment data and approve small, reviewed snapshots.","tradeoff":"A format change requires updating and reviewing the stored output."},{"when":"Only a few assertions describe the contract","use":"Use focused structural and behavioral assertions instead of storing an entire output.","tradeoff":"Unexpected layout changes outside those assertions require separate checks."}]
checks: ["Run on multiple working directories and assert deterministic normalized output.","Make a deliberate breaking change and confirm the test highlights it."]
sources: [{"title":"Jest snapshot testing","url":"https://jestjs.io/docs/snapshot-testing"},{"title":"Node.js test runner","url":"https://nodejs.org/api/test.html"}]
---

<!-- Generated record title. -->
# Focused snapshots for stable outputs

## Scenario

A CLI generates a structured project report whose layout and relative paths are part of its user contract.

## Failure modes

Timestamps, locale and temporary paths make snapshots noisy. Blind regeneration can accept real regressions. Broad snapshots may obscure the critical invariant.

## Explain it simply

Keep a reviewed reference output for stable details and add direct checks for the rules users depend on.

## Implementation guidance

Normalize temporary paths, clocks or locale only where incidental to the contract. Preserve structure and ordering that carry meaning. Pair compact snapshots with direct assertions on invariants a textual diff would hide. Try a harmless environment change that should preserve the snapshot and a required output change that should be caught before accepting updates.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The serialized output is a meaningful, stable interface** Normalize incidental environment data and approve small, reviewed snapshots. A format change requires updating and reviewing the stored output.
- **Only a few assertions describe the contract** Use focused structural and behavioral assertions instead of storing an entire output. Unexpected layout changes outside those assertions require separate checks.

## Verification

- Run on multiple working directories and assert deterministic normalized output.
- Make a deliberate breaking change and confirm the test highlights it.

## Sources

- [Jest snapshot testing](https://jestjs.io/docs/snapshot-testing)
- [Node.js test runner](https://nodejs.org/api/test.html)

<!-- End generated record details. -->
