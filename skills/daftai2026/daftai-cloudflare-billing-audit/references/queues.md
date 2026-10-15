# Queues

Default scope is offline, read-only source review; do not query a live account. Use runtime metrics only if the user separately supplies redacted evidence. Count operations per message, retry, fan-out and cross-service hop; queue binding presence alone is not a finding.

## Meter and message-size boundary

- **Unit:** each write, read, or delete operation is counted once per 64 KB chunk of message data; Cloudflare defines KB as 1,000 bytes and notes about 100 bytes of internal metadata per message. A message over one chunk rounds up to multiple chunks.
- **Scope:** operations are counted per message, not per batch. Typical delivered-and-consumed work includes write + read + delete; each retry adds a read per applicable chunk, an expired unread message incurs write + delete, and a DLQ write adds a write per chunk. Queue egress/bandwidth is not the message-operation meter. Runtime throughput limits are separate from billable operations.
- Official basis: [Queues pricing](https://developers.cloudflare.com/queues/platform/pricing/) (CF-DOC-QUEUES-PRICING). Checked 2026-10-12. No rate or monetary estimate is fixed here.

## CF-QUEUES-SELF-REENQUEUE-LOOP — autonomous queue cycle
- Risk conditions: consumer or event handler enqueues another job that can reach the same consumer indefinitely, or forms an R2 → Queue → Worker → R2 cycle. A successful `ack()` can end delivery of one message while the consumer publishes a distinct follow-on message; `max_retries` bounds failed delivery/retry of a message, not a success-path chain of newly sent messages (inference from the documented send and acknowledgement semantics).
- Check: draw producer/consumer graph; distinguish each message's delivery attempts from new messages created by a consumer; trace send/ack/failure/DLQ paths; verify event filters, root-job budget, progress checkpoint and terminal condition. Check that the business-job budget is not reset merely because a new message ID is generated.
- Mitigation and trade-off: carry a bounded job/depth/remaining-work budget across newly sent messages, add stable event-ID deduplication, explicit stop condition and progress checkpoints; isolate input/output event sources. This may delay or abandon downstream work; pausing can grow backlog.
- Blind spots: a reported Workers/Queues loop does not prove the same success-path pattern in another project. The distinction between `max_retries` and a new successful message chain is an inference from official API semantics, not a Cloudflare statement that a given application loops.
- Evidence: caseId goteap-workers-queues-loop; guideId layercache-cloudflare-cost-guard-skill; official sourceIds CF-DOC-QUEUES-PRICING, CF-DOC-QUEUES-LIMITS (related pages CF-DOC-QUEUES-RETRIES and CF-DOC-QUEUES-PRODUCERS). Checked 2026-10-12.

## CF-QUEUES-RETRY-FANOUT — repeated operations after failure
- Risk conditions: retries can repeat permanent failures, each attempt fans out, or the DLQ path re-enqueues failures.
- Check: retry count, backoff, per-message calls, batch size, concurrency, visibility timeout and DLQ consumer chain.
- Mitigation and trade-off: use bounded attempts/backoff, idempotency, DLQ with terminal handling, batch/concurrency ceilings and message-age deadlines. Lower throughput can increase latency/backlog.
- Blind spots: the cited Billflare loop report does not establish a retry-specific mechanism; this rule comes from official queue billing semantics and guide advice.
- Evidence: guideIds sarmaasis-cloudflare-under-five-dollars, layercache-cloudflare-cost-guard-skill; official sourceIds CF-DOC-QUEUES-PRICING, CF-DOC-QUEUES-LIMITS.
