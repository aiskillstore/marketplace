---
id: "index-freshness"
title: "Search index freshness and recoverability"
category: "data"
summary: "Manage search as a derived view with measurable lag and a repeatable rebuild path."
aliases: ["search indexing lag","index rebuild","read model","projection lag","reindex","arama indeksi güncel değil","arama indeksini yeniden oluşturma","silinen içerik aramada görünüyor"]
decisions: [{"when":"Low lag is acceptable and changes can be replayed","use":"Publish durable versioned changes, apply idempotently and rebuild into a versioned index before switching.","tradeoff":"Additional lag, monitoring and storage are expected."},{"when":"Strong freshness is required for a subset of records","use":"Confirm critical membership or access against the source and use an appropriate exact lookup.","tradeoff":"Authoritative checks add latency, particularly after a broad search."}]
checks: ["Drop and replay changes and verify the rebuilt index equals the expected projection.","Switch indexes under writes and confirm deletions and authorization are preserved."]
sources: [{"title":"Elastic index aliases","url":"https://www.elastic.co/guide/en/elasticsearch/reference/current/aliases.html"},{"title":"AWS transactional outbox pattern","url":"https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html"}]
---

<!-- Generated record title. -->
# Search index freshness and recoverability

## Scenario

A job board updates postings in its primary store and asynchronously indexes them for keyword search.

## Failure modes

Lost events leave records stale. Rebuilding in-place can show partial results, and opening access before deletion events finish can expose removed entries.

## Explain it simply

Keep the main record authoritative and make it possible to rebuild search without losing or exposing entries.

## Implementation guidance

Give every indexed change a stable document ID and source version, including deletes. Build replacement indexes from a snapshot and replay changes after that snapshot until caught up before an atomic read-alias switch. Guard sensitive reads against authoritative access when staleness is unacceptable. Measure source-to-query lag by operation type and verify that a late old update cannot resurrect a record deleted just before cutover.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Low lag is acceptable and changes can be replayed** Publish durable versioned changes, apply idempotently and rebuild into a versioned index before switching. Additional lag, monitoring and storage are expected.
- **Strong freshness is required for a subset of records** Confirm critical membership or access against the source and use an appropriate exact lookup. Authoritative checks add latency, particularly after a broad search.

## Verification

- Drop and replay changes and verify the rebuilt index equals the expected projection.
- Switch indexes under writes and confirm deletions and authorization are preserved.

## Sources

- [Elastic index aliases](https://www.elastic.co/guide/en/elasticsearch/reference/current/aliases.html)
- [AWS transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

<!-- End generated record details. -->
