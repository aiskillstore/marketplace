---
id: "offline-sync-conflicts"
title: "Offline synchronization and conflict resolution"
category: "architecture"
summary: "Design synchronization around missing connectivity, concurrent edits and explicit conflict semantics."
aliases: ["offline sync","local first","conflict resolution","delta sync","sync tombstones","çevrimdışı düzenleme","senkronizasyon çatışması","silinen kaydın geri gelmesi"]
decisions: [{"when":"A server can own synchronization and conflicts are rare","use":"Upload versioned mutations and resolve conflicting fields using an explicit merge or user choice.","tradeoff":"Clients need an outbox, cursor recovery and visible conflict state."},{"when":"Independent edits must converge automatically","use":"Use an established CRDT for compatible fields with schema and history management.","tradeoff":"Automatic merges can still conflict with domain invariants."}]
checks: ["Reconnect clients in both orders after conflicting edits and deletes.","Verify full resync after a cursor expires cannot resurrect deleted data."]
sources: [{"title":"Ink & Switch, local-first software","url":"https://www.inkandswitch.com/local-first/"},{"title":"Automerge architecture and conflicts","url":"https://automerge.org/docs/reference/documents/conflicts/"}]
---

<!-- Generated record title. -->
# Offline synchronization and conflict resolution

## Scenario

Two inspection tablets edit checklists offline and later reconnect in different orders. Deletions must not resurrect a checklist.

## Failure modes

Last-write-wins clocks can disagree. A cursored delta stream can skip changes after retention expiry, and purging tombstones too early resurrects data.

## Explain it simply

Keep local changes until they can sync, then merge them according to a rule users can understand.

## Implementation guidance

Give each client mutation an identity, a base revision and a scope. Persist the outcome long enough for retry, keep tombstones until clients can no longer resume from a cursor that precedes them, and return a fresh snapshot when that retention window expires. A merge choice for independent checklist fields does not necessarily apply to a deletion. Replay shuffled and repeated messages from two tablets and then reconnect a client that missed the tombstone window.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A server can own synchronization and conflicts are rare** Upload versioned mutations and resolve conflicting fields using an explicit merge or user choice. Clients need an outbox, cursor recovery and visible conflict state.
- **Independent edits must converge automatically** Use an established CRDT for compatible fields with schema and history management. Automatic merges can still conflict with domain invariants.

## Verification

- Reconnect clients in both orders after conflicting edits and deletes.
- Verify full resync after a cursor expires cannot resurrect deleted data.

## Sources

- [Ink & Switch, local-first software](https://www.inkandswitch.com/local-first/)
- [Automerge architecture and conflicts](https://automerge.org/docs/reference/documents/conflicts/)

<!-- End generated record details. -->
