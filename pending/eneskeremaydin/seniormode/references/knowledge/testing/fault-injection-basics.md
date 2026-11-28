---
id: "fault-injection-basics"
title: "Controlled fault injection and recovery tests"
category: "testing"
summary: "Verify documented rollback and recovery behavior with bounded fault scenarios in test environments."
aliases: ["fault injection","recovery test","simulate timeout","chaos test","dependency outage","hata enjeksiyonu ile kurtarma testi","bağımlılık kesintisini canlandır","işlem ortasında hata testi"]
decisions: [{"when":"A decision has identifiable side-effect boundaries","use":"Inject failures around those boundaries in a controlled integration test and replay recovery.","tradeoff":"Fixtures must represent durable state and actual retries."},{"when":"A system must withstand infrastructure-level disruption","use":"Use a scoped nonproduction resilience exercise with explicit abort conditions and baseline monitoring.","tradeoff":"Complex drills are slower and harder to diagnose."}]
checks: ["Check interrupted work resumes, rolls back or enters a documented pending state.","Verify a successful replay preserves the invariant and yields a usable operator signal."]
sources: [{"title":"AWS Well-Architected resilience testing","url":"https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/test-reliability.html"},{"title":"Google SRE on data integrity","url":"https://sre.google/sre-book/data-integrity/"}]
---

<!-- Generated record title. -->
# Controlled fault injection and recovery tests

## Scenario

A worker reserves inventory, then calls a simulated dependency that can fail at multiple points. Each stage should have an observable outcome after restart.

## Failure modes

Tests that only throw before the operation skip ambiguous post-commit failures. Large uncontrolled failures can obscure the expected invariant.

## Explain it simply

Rehearse one failure at a time and check that the system can recover without leaving half-finished work.

## Verification details

Map the durability boundaries between inventory and external calls. Inject one failure immediately before and immediately after each boundary, restart the handler and observe what can be safely replayed or must stay pending. A committed provider effect with a lost acknowledgement is a different case from failure before any effect. Start with bounded fixture experiments with observable invariants.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A decision has identifiable side-effect boundaries** Inject failures around those boundaries in a controlled integration test and replay recovery. Fixtures must represent durable state and actual retries.
- **A system must withstand infrastructure-level disruption** Use a scoped nonproduction resilience exercise with explicit abort conditions and baseline monitoring. Complex drills are slower and harder to diagnose.

## Verification

- Check interrupted work resumes, rolls back or enters a documented pending state.
- Verify a successful replay preserves the invariant and yields a usable operator signal.

## Sources

- [AWS Well-Architected resilience testing](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/test-reliability.html)
- [Google SRE on data integrity](https://sre.google/sre-book/data-integrity/)

<!-- End generated record details. -->
