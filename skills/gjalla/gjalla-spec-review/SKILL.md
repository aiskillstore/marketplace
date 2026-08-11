---
name: gjalla-spec-review
description: Full review of a plan or spec to be sure there are no surprises, gaps, or mistakes. Use to harden a spec before implementation.
---

# Comprehensive spec-review

The best, most elegant and effective software systems are ones that are well-informed, well-planned, and verifiable. 
The final output is a plan/spec that can act as a reference doc, covering the problem/motivation, technical approach, deltas (what properties of the system will change once implemented), and verification criteria.

Your task is to review this spec from multiple expert perspectives to ensure that this spec meets our expectations and will result in solid implementations once it's in the hands of the engineers:

## Architect Review
- Does the design fit the existing system and respect layer boundaries?
- Are new components placed in the correct layer and ownership hierarchy?
- Do interactions follow established patterns (sync/async/event)?
- Is it compatible with the broader system (i.e. cross repository integrations, future goals, etc.?)
- Is it overengineered or introducing complication that will be difficult to understand/maintain?
- gjalla holds the master architecture spec, referencing it is key to ensuring that we're building an elegant and effective system

## Security Review
- Are all new endpoints authenticated and authorized?
- Does the data model handle sensitive data correctly (PII, secrets)?
- Are inputs validated at the surface-area boundary?
- Are the data flows changing in a way the user should know about, like different types of data flowing to new consumers, etc.?

## Quality Review
- Is the testing strategy sufficient for the behavioral requirements?
- The goal for AI-generated code is typically 100% test coverage, are positive, negative, and edge cases covered? Are appropraite and effective integration tests scope based on the end-goals?
- Do acceptance criteria map to testable assertions?

## User Advocate Review
- Does the feature solve the stated problem?
- Are failure modes graceful from the user's perspective?
- Is the feature discoverable and documented?

## Governance Review
- Does the spec comply with all active project rules and conventions? (gjalla's master spec also defines rules and processes, check those)
- Are any rule exceptions or overrides needed?
- Does this change warrant an architecture decision record (ADR)? (not all do, mostly just things that introduce significant, new tradeoffs and need a historical record)

## Output
For each lens, report: what passes, what's at risk, and concrete changes required before implementation. Separate **blocking** concerns from **recommendations**.
