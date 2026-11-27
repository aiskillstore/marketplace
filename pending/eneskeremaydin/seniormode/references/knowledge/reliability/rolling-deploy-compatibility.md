---
id: "rolling-deploy-compatibility"
title: "Mixed-version deployment compatibility"
category: "reliability"
summary: "Plan deploys and rollbacks for a period when old and new code read and write the same data."
aliases: ["rolling deployment","version skew","backward compatible rollout","rollback compatibility","mixed versions","eski yeni sürümler birlikte çalışsın","kademeli dağıtım uyumluluğu","sürüm geri alma"]
decisions: [{"when":"Multiple versions will run during deploy","use":"Use expand, migrate and contract with tolerant readers and version-checked writers.","tradeoff":"The compatibility phase needs measured completion and temporary extra code."},{"when":"A genuinely isolated replacement is possible","use":"Deploy into versioned storage, quiesce writers and switch readers at a verified boundary.","tradeoff":"The cutover can introduce downtime or state synchronization cost."}]
checks: ["Run old and new writer-reader combinations against representative old and new data.","Practice rollback across every boundary where the change is advertised as reversible."]
sources: [{"title":"Stripe Engineering online migrations","url":"https://stripe.com/blog/online-migrations"},{"title":"Kubernetes deployments","url":"https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"}]
related: ["zero-downtime-migrations","api-versioning"]
---

<!-- Generated record title. -->
# Mixed-version deployment compatibility

## Scenario

A background worker starts writing a field before every old API instance has drained. A rollout may be paused for hours.

## Failure modes

New required fields or changed enum assumptions break old readers. Rollback after destructive migration can restore code that cannot read the data.

## Explain it simply

Make old and new versions compatible while they run side by side, then remove obsolete shapes after the rollout.

## Edge cases

Constrain writers to data understood by every current reader and keep new reading behavior compatible with both versions. Tie switching to verified readiness or data revision instead of an arbitrary time after deploy. Exercise old writer/new reader and new writer/old reader pairs. Pause the rollout with both versions active and verify the rollback still reads data they produced.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Multiple versions will run during deploy** Use expand, migrate and contract with tolerant readers and version-checked writers. The compatibility phase needs measured completion and temporary extra code.
- **A genuinely isolated replacement is possible** Deploy into versioned storage, quiesce writers and switch readers at a verified boundary. The cutover can introduce downtime or state synchronization cost.

## Verification

- Run old and new writer-reader combinations against representative old and new data.
- Practice rollback across every boundary where the change is advertised as reversible.

## Sources

- [Stripe Engineering online migrations](https://stripe.com/blog/online-migrations)
- [Kubernetes deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

## Related decisions

- [Expand-and-contract schema changes](../data/zero-downtime-migrations.md)
- [Evolving public API contracts](../backend/api-versioning.md)

<!-- End generated record details. -->
