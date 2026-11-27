---
id: "operational-transformation"
title: "Concurrent text editing and position transforms"
category: "concurrency"
summary: "Preserve concurrent editing intent by applying versioned positions and explicit conflict rules."
aliases: ["operational transformation","ot","realtime editing","google docs","eşzamanlı belge düzenleme","eşzamanlı ortak metin düzenleme","aynı belgeye aynı anda yazma","metin ekleme konumunu kaydırma"]
decisions: [{"when":"A central authority can sequence operations","use":"Adopt vetted operational transformation or a versioned operation model with defined rebasing.","tradeoff":"The algorithm and undo semantics are intricate across concurrent operations."},{"when":"Independent peers must converge after offline work","use":"Choose a tested sequence CRDT and define compaction and permission boundaries.","tradeoff":"Metadata, retention and migration typically require more storage."}]
checks: ["Apply edits in permitted reorderings and compare final replicas.","Test overlapping deletes, duplicate operation IDs and reconnect with a stale revision."]
sources: [{"title":"Ellis and Gibbs, concurrency control in groupware","url":"https://www.lri.fr/~mbl/ENS/CSCW/2015/papers/Ellis-SIGMOD89.pdf"},{"title":"Automerge architecture and conflicts","url":"https://automerge.org/docs/reference/documents/conflicts/"}]
---

<!-- Generated record title. -->
# Concurrent text editing and position transforms

## Scenario

Two volunteers edit a wiki heading offline for a few seconds. Each records a short text insertion at a position from the same starting revision.

## Failure modes

Last-write-wins whole documents can lose text. Position transforms must handle deletes and reorderings; naive ad hoc shifting can diverge.

## Explain it simply

Send what changed and where. If someone edited earlier in the text, adjust the position before applying the next edit.

## Implementation guidance

Record exact operation coordinates, author identity, deterministic tie rules and the base document revision. When rebasing inserts and deletes, use the transform rules of a vetted engine rather than shifting indexes one case at a time. A transport that delivers notifications in a different order must still converge to one valid document. Test simultaneous inserts at the same position, overlapping deletion and insertion, duplicate delivery, and a reconnect after operation history compaction.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A central authority can sequence operations** Adopt vetted operational transformation or a versioned operation model with defined rebasing. The algorithm and undo semantics are intricate across concurrent operations.
- **Independent peers must converge after offline work** Choose a tested sequence CRDT and define compaction and permission boundaries. Metadata, retention and migration typically require more storage.

## Verification

- Apply edits in permitted reorderings and compare final replicas.
- Test overlapping deletes, duplicate operation IDs and reconnect with a stale revision.

## Sources

- [Ellis and Gibbs, concurrency control in groupware](https://www.lri.fr/~mbl/ENS/CSCW/2015/papers/Ellis-SIGMOD89.pdf)
- [Automerge architecture and conflicts](https://automerge.org/docs/reference/documents/conflicts/)

<!-- End generated record details. -->
