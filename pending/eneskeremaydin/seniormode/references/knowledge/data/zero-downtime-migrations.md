---
id: "zero-downtime-migrations"
title: "Expand-and-contract schema changes"
category: "data"
summary: "Evolve persistent schemas while applications and backfills continue to work."
aliases: ["schema migration","zero downtime migration","backfill","expand contract","database rollout","veritabanı şemasını kesintisiz değiştirme","eski kolon yeni kolon geçişi","canlı veriyi geriye dönük doldurma","legacy app still running during column migration","old reader new database column","eski sürüm çalışırken yeni sütuna geçiş"]
decisions: [{"when":"Persistent data must remain live across a mixed rollout","use":"Add compatible fields, deploy compatible readers and writers, backfill in restartable batches and verify before contract.","tradeoff":"Temporary complexity buys a reversible migration phase."},{"when":"The table is small and downtime is explicitly acceptable","use":"Use a short planned maintenance migration with a tested snapshot and rollback.","tradeoff":"Users need clear outage expectations and operational timing."}]
checks: ["Trigger concurrent writes during a resumed backfill and verify newer values survive.","Run read and write paths for old data and new data before destructive cleanup."]
sources: [{"title":"PostgreSQL modifying tables","url":"https://www.postgresql.org/docs/current/ddl-alter.html"},{"title":"Stripe Engineering online migrations","url":"https://stripe.com/blog/online-migrations"}]
related: ["rolling-deploy-compatibility"]
---

<!-- Generated record title. -->
# Expand-and-contract schema changes

## Scenario

An order system splits a free-text address into columns. Older workers need time to deploy and existing records must be transformed in batches.

## Failure modes

A table rewrite can hold locks. A backfill can overwrite recent app writes, and destructive cleanup invalidates rollback assumptions.

## Explain it simply

Add the replacement shape, move and verify existing data, switch traffic, then retire the old shape.

## Implementation guidance

Expand with a compatible field, deploy writers that preserve both representations as needed, then backfill in small restartable batches. Guard each backfill write against changes since the row was read. Compare old and new representations before switching reads, and remove the old field only after the rollback window and old consumers are gone. Rehearse aborting late in the rollout while an older worker is still running.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Persistent data must remain live across a mixed rollout** Add compatible fields, deploy compatible readers and writers, backfill in restartable batches and verify before contract. Temporary complexity buys a reversible migration phase.
- **The table is small and downtime is explicitly acceptable** Use a short planned maintenance migration with a tested snapshot and rollback. Users need clear outage expectations and operational timing.

## Verification

- Trigger concurrent writes during a resumed backfill and verify newer values survive.
- Run read and write paths for old data and new data before destructive cleanup.

## Sources

- [PostgreSQL modifying tables](https://www.postgresql.org/docs/current/ddl-alter.html)
- [Stripe Engineering online migrations](https://stripe.com/blog/online-migrations)

## Related decisions

- [Mixed-version deployment compatibility](../reliability/rolling-deploy-compatibility.md)

<!-- End generated record details. -->
