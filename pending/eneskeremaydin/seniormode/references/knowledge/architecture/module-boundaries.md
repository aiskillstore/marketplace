---
id: "module-boundaries"
title: "Module boundaries around business rules"
category: "architecture"
summary: "Put stable policies in testable modules where real responsibilities and callers justify the boundary."
aliases: ["module design","separation of concerns","service extraction","business logic placement","modular monolith","iş kurallarını modüle ayırma","aynı iş kuralı iki yerde","servis çıkarmak","duplicated eligibility check","two routes share eligibility rules","iki rotada tekrarlanan uygunluk kuralı"]
decisions: [{"when":"The policy is reused or needs independent tests","use":"Extract a focused module with explicit dependencies and preserve public entry points.","tradeoff":"The boundary needs a small stable contract and useful tests."},{"when":"Only one simple path uses the rule","use":"Keep the logic close to the caller or use a nearby pure function.","tradeoff":"A later second caller may justify extracting the policy."}]
checks: ["Verify normal feature entry points maintain existing behavior after moving the rule.","Test independent policy choices without booting unrelated services."]
sources: [{"title":"Parnas, criteria for decomposing systems into modules","url":"https://john.cs.olemiss.edu/~hcc/csci658/notes/localcopy/Parnas_Criteria_Decomposing.pdf"},{"title":"Martin Fowler, Monolith First","url":"https://martinfowler.com/bliki/MonolithFirst.html"}]
---

<!-- Generated record title. -->
# Module boundaries around business rules

## Scenario

Two handlers reorder items using competing copies of the same policy. A small standalone component now needs the same rule.

## Failure modes

Splitting code by line count can introduce indirection without resolving ownership. Making a network service from a local pure policy adds failure modes.

## Explain it simply

Give the shared rule one clear home while letting each caller handle its own inputs and outputs.

## Implementation guidance

Give one reusable operation a name from the domain, such as ordering line items, and let the two callers keep transport-specific parsing and responses. Move only the stable rules and inject genuine variability, such as time, instead of generalizing every branch. When there is one small path, a local pure helper can make the rule testable. Keep endpoint contract tests alongside direct policy tests as callers migrate.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The policy is reused or needs independent tests** Extract a focused module with explicit dependencies and preserve public entry points. The boundary needs a small stable contract and useful tests.
- **Only one simple path uses the rule** Keep the logic close to the caller or use a nearby pure function. A later second caller may justify extracting the policy.

## Verification

- Verify normal feature entry points maintain existing behavior after moving the rule.
- Test independent policy choices without booting unrelated services.

## Sources

- [Parnas, criteria for decomposing systems into modules](https://john.cs.olemiss.edu/~hcc/csci658/notes/localcopy/Parnas_Criteria_Decomposing.pdf)
- [Martin Fowler, Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)

<!-- End generated record details. -->
