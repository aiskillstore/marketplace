---
id: "read-your-writes"
title: "Replica lag and read-your-writes"
category: "data"
summary: "Choose a read routing strategy that makes a user's own successful writes visible when required."
aliases: ["replication lag","read your writes","replica stale read","veritabanı replikasyonu","profile photo","değişiklikten sonra eski kayıt görünüyor","replika gecikmesi","kendi yazdığını okuma","profil güncellendi eski fotoğraf"]
decisions: [{"when":"A subset of reads needs guaranteed freshness","use":"Read from the primary or a replica known to have reached the write position.","tradeoff":"Primary load or waiting time increases only for gated reads."},{"when":"Stale reads are acceptable with a clear product contract","use":"Read replicas with a staleness budget and monitor lag, falling back when it exceeds policy.","tradeoff":"Users may briefly see an older value."}]
checks: ["Pause replay and assert critical read-after-write returns the committed value.","Test cross-device reads, failover and fallback under extended lag."]
sources: [{"title":"PostgreSQL high availability and standby servers","url":"https://www.postgresql.org/docs/current/warm-standby.html"},{"title":"Jepsen consistency model documentation","url":"https://jepsen.io/consistency/models/read-your-writes"}]
---

<!-- Generated record title. -->
# Replica lag and read-your-writes

## Scenario

A customer changes their shipping address and refreshes immediately. Analytics queries can tolerate lag, but the checkout preview cannot.

## Failure modes

A fixed time window is weaker than tracking a commit position when lag exceeds the estimate. Session-only state can diverge across devices.

## Explain it simply

After you save a change, send your next reads somewhere that has already seen that change.

## Implementation guidance

Choose a consistency path per user operation. After an address change, route the follow-up checkout read to the primary or use a commit position token and serve only replicas that have replayed it, with bounded wait and primary fallback. Decide how another device retrieves an updated position or uses a source read. With an artificially lagging replica, prove that the preview reflects the new address while analytics can remain within its allowed staleness.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A subset of reads needs guaranteed freshness** Read from the primary or a replica known to have reached the write position. Primary load or waiting time increases only for gated reads.
- **Stale reads are acceptable with a clear product contract** Read replicas with a staleness budget and monitor lag, falling back when it exceeds policy. Users may briefly see an older value.

## Verification

- Pause replay and assert critical read-after-write returns the committed value.
- Test cross-device reads, failover and fallback under extended lag.

## Sources

- [PostgreSQL high availability and standby servers](https://www.postgresql.org/docs/current/warm-standby.html)
- [Jepsen consistency model documentation](https://jepsen.io/consistency/models/read-your-writes)

<!-- End generated record details. -->
