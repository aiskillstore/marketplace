---
id: "lease-fencing"
title: "Leases and fencing tokens"
category: "concurrency"
summary: "Protect shared state from a worker that continues after losing a lease or being replaced."
aliases: ["distributed lock","fencing token","expired lease","zombie worker","monotonic epoch","kilit süresi geçen eski işçi","süreli kilit ve sıra numarası","eski sahip yazmaya devam ediyor"]
decisions: [{"when":"The shared state can validate monotonic ownership","use":"Use leases for liveness and enforce fencing epochs at the write boundary.","tradeoff":"Every relevant writer needs to preserve the epoch check."},{"when":"Work is local or the shared resource cannot check epochs","use":"Use a transactional claim, idempotent effects or move coordination inside the authoritative store.","tradeoff":"Limits some distribution options but avoids unchecked shared authority."}]
checks: ["Pause the old worker past expiry, acquire a newer lease and reject the old write.","Test recovery after the winner's crash and verify epochs never move backward."]
sources: [{"title":"Google Chubby lock service paper","url":"https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/"},{"title":"etcd concurrency API reference","url":"https://etcd.io/docs/v3.6/dev-guide/api_concurrency_reference_v3/"}]
related: ["primary-failover"]
---

<!-- Generated record title. -->
# Leases and fencing tokens

## Scenario

A report worker obtains a thirty-second lease. A runtime pause lasts longer, then the old worker resumes while a new worker owns the task.

## Failure modes

A time-limited lock only controls eligibility at acquisition. A stale worker can still write if the resource does not verify authority.

## Explain it simply

Give each lease a newer number and have the storage layer reject work stamped with an older one.

## Implementation guidance

A worker should send a monotonically allocated epoch with each protected write, and the authoritative service must compare it to its last accepted epoch before mutating state. Verify that the sink can perform this check and persist it durably, otherwise choose a coordination/idempotency strategy the sink can enforce. Pause a worker past lease expiry, let its successor write, then resume the old worker and require a rejected stale write.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The shared state can validate monotonic ownership** Use leases for liveness and enforce fencing epochs at the write boundary. Every relevant writer needs to preserve the epoch check.
- **Work is local or the shared resource cannot check epochs** Use a transactional claim, idempotent effects or move coordination inside the authoritative store. Limits some distribution options but avoids unchecked shared authority.

## Verification

- Pause the old worker past expiry, acquire a newer lease and reject the old write.
- Test recovery after the winner's crash and verify epochs never move backward.

## Sources

- [Google Chubby lock service paper](https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/)
- [etcd concurrency API reference](https://etcd.io/docs/v3.6/dev-guide/api_concurrency_reference_v3/)

## Related decisions

- [Stateful failover and split-brain prevention](../reliability/primary-failover.md)

<!-- End generated record details. -->
