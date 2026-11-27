---
id: "primary-failover"
title: "Stateful failover and split-brain prevention"
category: "reliability"
summary: "Restore a stateful service after failure while preventing concurrent leaders from applying conflicting updates."
aliases: ["failover","split brain","leader fencing","valorant server","yedek devralma","ana sunucu çökünce yedek devralsın","iki ana sunucu aynı anda yazıyor","oyun sunucusu devralma"]
decisions: [{"when":"Recovery time and confirmed-state loss are tightly bounded","use":"Replicate state with explicit acknowledgement rules and use a trusted lease or fencing epoch enforced by storage.","tradeoff":"Stronger guarantees add coordination and latency."},{"when":"Some recent noncritical state is disposable","use":"Restore from periodic checkpoints and communicate the recovery point.","tradeoff":"Recovery is simpler but the latest state may be missing."}]
checks: ["Partition old and new leaders and verify stale writes are rejected.","Measure recovery time and acknowledged data loss during failover drills."]
sources: [{"title":"Raft consensus paper","url":"https://raft.github.io/raft.pdf"},{"title":"PostgreSQL high availability and standby servers","url":"https://www.postgresql.org/docs/current/warm-standby.html"}]
related: ["disaster-recovery"]
---

<!-- Generated record title. -->
# Stateful failover and split-brain prevention

## Scenario

A co-op tournament server keeps a match's last confirmed state. If the active node disappears, players should reconnect without losing confirmed moves.

## Failure modes

A missing heartbeat means loss of reachability. The original leader can return while a new one writes. Async replication can lose updates that were acknowledged.

## Explain it simply

Keep a recoverable copy and ensure only the current leader can move the match forward.

## Implementation guidance

State which acknowledgements are durable under the replication mode. The storage path must enforce fencing or consensus ownership when leadership changes. Measure election and client recovery separately. Exercise a network split with both nodes running, then prove the former primary can rejoin without overwriting later acknowledged state.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Recovery time and confirmed-state loss are tightly bounded** Replicate state with explicit acknowledgement rules and use a trusted lease or fencing epoch enforced by storage. Stronger guarantees add coordination and latency.
- **Some recent noncritical state is disposable** Restore from periodic checkpoints and communicate the recovery point. Recovery is simpler but the latest state may be missing.

## Verification

- Partition old and new leaders and verify stale writes are rejected.
- Measure recovery time and acknowledged data loss during failover drills.

## Sources

- [Raft consensus paper](https://raft.github.io/raft.pdf)
- [PostgreSQL high availability and standby servers](https://www.postgresql.org/docs/current/warm-standby.html)

## Related decisions

- [Recovery objectives and restore verification](disaster-recovery.md)

<!-- End generated record details. -->
