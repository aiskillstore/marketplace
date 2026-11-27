---
id: "bounded-memory-streaming"
title: "Streaming transforms with bounded memory"
category: "performance"
summary: "Transform large input incrementally while bounding buffers and preserving failure semantics."
aliases: ["streaming parser","large file memory","incremental processing","stream backpressure","chunked parsing","belleğe almadan büyük dosya işleme","parça parça kayıt dönüştürme","bellek sınırında veri akışı"]
decisions: [{"when":"The transform can preserve limited state per chunk","use":"Use a streaming parser and backpressure-aware pipeline with an atomic final output.","tradeoff":"Chunk boundaries, resource cleanup and late errors need targeted tests."},{"when":"The transform needs a global ordering or aggregation","use":"Use external sort, bounded partitioning or a database-backed intermediate result.","tradeoff":"I/O and temporary storage increase to keep memory bounded."}]
checks: ["Process an input larger than available RAM and record memory peaks.","Inject a partial multibyte value, malformed record and output failure."]
sources: [{"title":"Node.js stream documentation","url":"https://nodejs.org/api/stream.html"},{"title":"Node.js streams and backpressure","url":"https://nodejs.org/en/learn/modules/backpressuring-in-streams"}]
---

<!-- Generated record title. -->
# Streaming transforms with bounded memory

## Scenario

An export utility reads a multi-gigabyte file on a machine with limited memory and produces a second file.

## Failure modes

Collecting all chunks in an array defeats streaming. Decoding independently at each chunk can split multibyte characters and a failed output may appear complete.

## Explain it simply

Read and write one manageable piece at a time, and only publish the finished result.

## Implementation guidance

Use a streaming decoder that carries partial multibyte state between chunks. Bound the largest individual record as well as buffer sizes. Let a slow sink backpressure the producer and publish the output only after the whole pipeline completes. Test split multibyte characters and an interrupted write under a small memory budget.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The transform can preserve limited state per chunk** Use a streaming parser and backpressure-aware pipeline with an atomic final output. Chunk boundaries, resource cleanup and late errors need targeted tests.
- **The transform needs a global ordering or aggregation** Use external sort, bounded partitioning or a database-backed intermediate result. I/O and temporary storage increase to keep memory bounded.

## Verification

- Process an input larger than available RAM and record memory peaks.
- Inject a partial multibyte value, malformed record and output failure.

## Sources

- [Node.js stream documentation](https://nodejs.org/api/stream.html)
- [Node.js streams and backpressure](https://nodejs.org/en/learn/modules/backpressuring-in-streams)

<!-- End generated record details. -->
