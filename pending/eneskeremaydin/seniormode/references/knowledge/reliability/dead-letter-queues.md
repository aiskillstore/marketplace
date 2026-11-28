---
id: "dead-letter-queues"
title: "Poison messages and dead-letter handling"
category: "reliability"
summary: "Isolate work that cannot complete while preserving diagnostics and controlled replay."
aliases: ["dead letter queue","poison message","redrive","dlq","retry exhaustion","işlenemeyen mesajları ayrı kuyruğa al","başarısız mesajı tekrar işleme","zehirli mesaj"]
decisions: [{"when":"A single message can block progress or exhaust retries","use":"Move failed work to a monitored dead-letter queue with reason, attempt and stable ID.","tradeoff":"Operators need a retention window and an intentional redrive workflow."},{"when":"Strict order prevents skipping work","use":"Pause that partition and resolve the blocking event before continuing, with bounded isolation.","tradeoff":"Throughput for that partition falls until the incident is handled."}]
checks: ["Deliver a persistent failure and verify unrelated work proceeds as intended.","Redrive an already applied event and verify the consumer does not repeat the effect."]
sources: [{"title":"Amazon SQS dead-letter queues","url":"https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html"},{"title":"RabbitMQ consumer acknowledgements and confirms","url":"https://www.rabbitmq.com/docs/confirms"}]
related: ["idempotent-consumer"]
---

<!-- Generated record title. -->
# Poison messages and dead-letter handling

## Scenario

An order worker encounters a malformed event. Retrying continuously blocks later orders in the same queue.

## Failure modes

A dead-letter queue without ownership loses work silently. Blind redrive repeats harm, and queue TTL can expire faster than investigation.

## Explain it simply

Move consistently failing work aside, retain enough information to fix it and replay only when it can succeed.

## Implementation guidance

Store a stable message ID, first-seen time, attempt count and sanitized reason. Set alerting and retention against a known owner’s response budget. Redrive a small verified cohort after a fix and keep its effects idempotent. Exercise restart during routing, a malformed event between valid work and a replay of a still-poisoned message.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A single message can block progress or exhaust retries** Move failed work to a monitored dead-letter queue with reason, attempt and stable ID. Operators need a retention window and an intentional redrive workflow.
- **Strict order prevents skipping work** Pause that partition and resolve the blocking event before continuing, with bounded isolation. Throughput for that partition falls until the incident is handled.

## Verification

- Deliver a persistent failure and verify unrelated work proceeds as intended.
- Redrive an already applied event and verify the consumer does not repeat the effect.

## Sources

- [Amazon SQS dead-letter queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [RabbitMQ consumer acknowledgements and confirms](https://www.rabbitmq.com/docs/confirms)

## Related decisions

- [Idempotent event consumers and inboxes](../backend/idempotent-consumer.md)

<!-- End generated record details. -->
