---
id: "optimistic-concurrency"
title: "Optimistic concurrency and version checks"
category: "concurrency"
summary: "Detect conflicting edits using a version check and explicit conflict handling at the write boundary."
aliases: ["optimistic locking","lost update","etag if match","version column","compare and swap","aynı kaydı iki kişi düzenliyor","sürüm numarasıyla çakışma kontrolü","kayıp güncelleme","editor saves overwrite each other","concurrent forms stale edits","iki düzenleme ekranı birbirinin kaydını eziyor"]
decisions: [{"when":"Uncontended changes are common and clients can reconcile","use":"Use a version predicate or If-Match atomically and return conflict with current state.","tradeoff":"Conflicts are visible and require an intentional UX."},{"when":"Contentions are expected on an exact inventory transition","use":"Use a short transaction with a guarded update or lock and bounded retry.","tradeoff":"Coordination trades throughput for clear state ownership."}]
checks: ["Interleave two edits and verify the second sees a conflict.","Verify the version changes only on successful updates and that stale deletion is handled."]
sources: [{"title":"RFC 9110 HTTP semantics","url":"https://www.rfc-editor.org/rfc/rfc9110"},{"title":"PostgreSQL explicit locking","url":"https://www.postgresql.org/docs/current/explicit-locking.html"}]
---

<!-- Generated record title. -->
# Optimistic concurrency and version checks

## Scenario

Two editors open the same catalog item. One updates its title while the other changes a note based on an older version.

## Failure modes

A check in application memory can race across replicas. Retrying a stale edit blindly can overwrite fields that the user did not mean to change.

## Explain it simply

Save only if the record still has the version you edited, then show the conflicting change when necessary.

## Implementation guidance

Read a version with the record and include it in an atomic update predicate. With HTTP conditional updates, expose a strong validator suitable for If-Match and handle a mismatch without pretending the update succeeded. Render the current values so the caller may deliberately merge disjoint fields. Simulate two sessions reading version 1 before either writes, then make the second save report conflict instead of replaying a stale whole object.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Uncontended changes are common and clients can reconcile** Use a version predicate or If-Match atomically and return conflict with current state. Conflicts are visible and require an intentional UX.
- **Contentions are expected on an exact inventory transition** Use a short transaction with a guarded update or lock and bounded retry. Coordination trades throughput for clear state ownership.

## Verification

- Interleave two edits and verify the second sees a conflict.
- Verify the version changes only on successful updates and that stale deletion is handled.

## Sources

- [RFC 9110 HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [PostgreSQL explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html)

<!-- End generated record details. -->
