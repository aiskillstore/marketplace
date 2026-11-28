---
id: "batch-versus-streaming"
title: "Batch processing versus streaming"
category: "architecture"
summary: "Match processing cadence to business freshness, event order and recovery needs."
aliases: ["batch vs streaming","streaming architecture","event time","watermarks","late arrivals","toplu işleme","akış işleme","geç gelen olay verisi"]
decisions: [{"when":"Hourly or daily freshness meets the product need","use":"Use repeatable batches with source checkpoints and a bounded backfill process.","tradeoff":"Results lag and larger reruns can temporarily increase load."},{"when":"Timely incremental output is a requirement","use":"Use event-time windows and explicit late-event, checkpoint and replay semantics.","tradeoff":"Streaming state, ordering and operational cost increase."}]
checks: ["Replay late and duplicate events and verify aggregates remain consistent.","Compare end-to-end freshness and recovery cost under an interruption."]
sources: [{"title":"Apache Beam programming guide","url":"https://beam.apache.org/documentation/programming-guide/"},{"title":"Apache Kafka documentation","url":"https://kafka.apache.org/documentation/"}]
---

<!-- Generated record title. -->
# Batch processing versus streaming

## Scenario

An analytics dashboard currently refreshes daily and some users request an hourly view. Events arrive late from offline devices.

## Failure modes

A streaming system adds replay, ordering and state retention challenges. Processing-time windows can miscount late events and backfills must be reproducible.

## Explain it simply

Run periodic batches when they are fresh enough. Process events as they arrive only when the faster answer matters.

## Implementation guidance

Write the desired freshness as a measurable contract first, together with acceptable revision and event retention. A batch can replay from durable cutoffs with idempotent output keyed by window and dimension. For a continuous event-time product, distinguish late arrivals that reopen a window from events that should enter a correction or quarantine path. Run the same data in arrival order and ordered by event timestamp, then compare the final view after the agreed late-data bound.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Hourly or daily freshness meets the product need** Use repeatable batches with source checkpoints and a bounded backfill process. Results lag and larger reruns can temporarily increase load.
- **Timely incremental output is a requirement** Use event-time windows and explicit late-event, checkpoint and replay semantics. Streaming state, ordering and operational cost increase.

## Verification

- Replay late and duplicate events and verify aggregates remain consistent.
- Compare end-to-end freshness and recovery cost under an interruption.

## Sources

- [Apache Beam programming guide](https://beam.apache.org/documentation/programming-guide/)
- [Apache Kafka documentation](https://kafka.apache.org/documentation/)

<!-- End generated record details. -->
