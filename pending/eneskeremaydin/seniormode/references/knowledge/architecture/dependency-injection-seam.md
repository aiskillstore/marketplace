---
id: "dependency-injection-seam"
title: "Small dependency seams for testable policies"
category: "architecture"
summary: "Separate deterministic decisions from time, persistence and external calls where the distinction pays for itself."
aliases: ["dependency injection","testable policy","constructor injection","service boundary","interface design","bağımlılık enjeksiyonu","iş mantığına saat geçme","test edilebilir bağımlılık"]
decisions: [{"when":"A policy needs multiple environments or deterministic tests","use":"Make its relevant inputs explicit and keep transport and storage in adapters around the policy.","tradeoff":"The boundary has to remain narrow as callers evolve."},{"when":"Code is a short orchestrator for one stable dependency","use":"Keep ordinary direct calls and use a meaningful integration test.","tradeoff":"It is harder to trigger synthetic failure modes without a later seam."}]
checks: ["Verify the same rule through each public entry point.","Test the policy against a deterministic clock or fake only where needed."]
sources: [{"title":"Parnas, criteria for decomposing systems into modules","url":"https://john.cs.olemiss.edu/~hcc/csci658/notes/localcopy/Parnas_Criteria_Decomposing.pdf"},{"title":"Martin Fowler on dependency injection","url":"https://martinfowler.com/articles/injection.html"}]
---

<!-- Generated record title. -->
# Small dependency seams for testable policies

## Scenario

A renewal policy fetches the current time itself and performs database updates inside a formula used by two entry points.

## Failure modes

Framework-driven injection can hide dependencies. Splitting trivial code into layers creates work without making the policy easier to verify.

## Explain it simply

Pass the clock and storage boundary explicitly so the business rule can be checked on its own.

## Implementation guidance

Make renewal calculations accept time and subscription state as values and return a decision. Let the existing entry point call the clock, persist the result and manage transactions. Share the small policy between callers before introducing a container or generalized adapters. In tests, supply a clock value immediately before, at and after the expiration boundary, then keep one real integration test for persistence and failure handling.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A policy needs multiple environments or deterministic tests** Make its relevant inputs explicit and keep transport and storage in adapters around the policy. The boundary has to remain narrow as callers evolve.
- **Code is a short orchestrator for one stable dependency** Keep ordinary direct calls and use a meaningful integration test. It is harder to trigger synthetic failure modes without a later seam.

## Verification

- Verify the same rule through each public entry point.
- Test the policy against a deterministic clock or fake only where needed.

## Sources

- [Parnas, criteria for decomposing systems into modules](https://john.cs.olemiss.edu/~hcc/csci658/notes/localcopy/Parnas_Criteria_Decomposing.pdf)
- [Martin Fowler on dependency injection](https://martinfowler.com/articles/injection.html)

<!-- End generated record details. -->
