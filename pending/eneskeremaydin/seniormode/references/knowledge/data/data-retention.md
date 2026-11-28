---
id: "data-retention"
title: "End-to-end data retention and deletion"
category: "data"
summary: "Define where an entity's data lives and how authorized deletion propagates to derived copies."
aliases: ["data retention","personal data deletion","tombstone","data lifecycle","backup deletion","kayıt silme bütün kopyalara uygulansın","veri saklama süresi","silinen verinin yedekten dönmesi"]
decisions: [{"when":"Operational copies must stop serving deleted records","use":"Record the deletion durably, apply it to projections and verify acknowledgements or convergence.","tradeoff":"Propagation takes time and failures require a clear reconciliation path."},{"when":"Backup copies rotate under an approved retention policy","use":"Scope access, age out snapshots and replay applicable deletions after restoration.","tradeoff":"Recovery remains possible only within documented retention bounds."}]
checks: ["Trace a seeded record through each store and confirm authorized deletion propagates.","Restore a backup and verify previously deleted records do not reappear in production views."]
sources: [{"title":"Amazon S3 lifecycle expiration","url":"https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-expire-general-considerations.html"},{"title":"Google SRE on data integrity","url":"https://sre.google/sre-book/data-integrity/"}]
---

<!-- Generated record title. -->
# End-to-end data retention and deletion

## Scenario

A workspace administrator removes a project. Search, caches, background queues and backups may still contain associated data.

## Failure modes

Removing one row can leave replicas, exports or search entries. Immediate backup rewriting can conflict with recovery procedures and legal holds.

## Explain it simply

List the places that keep a copy, remove the live copies and document when recoverable backups age out.

## Implementation guidance

Assign deletion a stable request ID and inventory the authoritative rows, versions, derived views, queue payloads and export destinations touched by it. Record progress or the allowed expiration window per destination. When restoring snapshots, reapply deletions still required before opening access to restored data. Use a synthetic customer record to prove direct lookups, search and restored views all follow the policy, including the explicit exception for a legal hold.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Operational copies must stop serving deleted records** Record the deletion durably, apply it to projections and verify acknowledgements or convergence. Propagation takes time and failures require a clear reconciliation path.
- **Backup copies rotate under an approved retention policy** Scope access, age out snapshots and replay applicable deletions after restoration. Recovery remains possible only within documented retention bounds.

## Verification

- Trace a seeded record through each store and confirm authorized deletion propagates.
- Restore a backup and verify previously deleted records do not reappear in production views.

## Sources

- [Amazon S3 lifecycle expiration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-expire-general-considerations.html)
- [Google SRE on data integrity](https://sre.google/sre-book/data-integrity/)

<!-- End generated record details. -->
