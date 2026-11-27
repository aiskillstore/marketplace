---
id: "disaster-recovery"
title: "Recovery objectives and restore verification"
category: "reliability"
summary: "Align backups and failover with stated recovery-point and recovery-time objectives."
aliases: ["disaster recovery","rpo","rto","backup restore","restore drill","yedekten geri yükleme tatbikatı","kabul edilebilir veri kaybı","kurtarma süresi hedefi"]
decisions: [{"when":"The acceptable recovery point is similar to backup cadence","use":"Use tested snapshots with a documented restore order and separate access controls.","tradeoff":"Snapshots leave a gap between backups."},{"when":"A narrow recovery point or short outage is required","use":"Add point-in-time recovery or managed standby and run regular failover drills.","tradeoff":"Storage, coordination and operational overhead grow."}]
checks: ["Restore into isolation and check representative records and permission paths.","Measure elapsed time and lost acknowledged changes against the stated objectives."]
sources: [{"title":"PostgreSQL backup and restore","url":"https://www.postgresql.org/docs/current/backup.html"},{"title":"Google SRE on data integrity","url":"https://sre.google/sre-book/data-integrity/"}]
---

<!-- Generated record title. -->
# Recovery objectives and restore verification

## Scenario

A grants database is backed up each night. A failed primary could interrupt the submission deadline and lose changes accepted earlier that day.

## Failure modes

A backup success notification does not prove restorability. Missing credentials, corrupt restores and dependencies outside the backup can lengthen recovery.

## Explain it simply

Decide how much data and time you can afford to lose, then rehearse restoring a representative system.

## Verification details

Derive backup frequency and recovery mechanics from tolerable data loss and duration. Inventory credentials, keys, configuration and external dependencies required for reopening. Restore a representative snapshot to isolation, check record integrity and accept a new submission end to end. Measure time from declaration and identify the last recoverable write.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The acceptable recovery point is similar to backup cadence** Use tested snapshots with a documented restore order and separate access controls. Snapshots leave a gap between backups.
- **A narrow recovery point or short outage is required** Add point-in-time recovery or managed standby and run regular failover drills. Storage, coordination and operational overhead grow.

## Verification

- Restore into isolation and check representative records and permission paths.
- Measure elapsed time and lost acknowledged changes against the stated objectives.

## Sources

- [PostgreSQL backup and restore](https://www.postgresql.org/docs/current/backup.html)
- [Google SRE on data integrity](https://sre.google/sre-book/data-integrity/)

<!-- End generated record details. -->
