---
id: "transactional-outbox"
title: "Transactional outbox and reliable delivery"
category: "architecture"
summary: "Publish domain changes without a race between a database transaction and a separate message broker."
aliases: ["transactional outbox","dual write","database event publishing","outbox pattern","cdc","veritabanı işlemi sonrası olay bildirimi","işlem kaydedildi mesaj gönderilemedi","işlemsel outbox","missing order delivery notification","event lost after order save","sipariş kaydedildi bildirim gitmedi","commit succeeded event not emitted"]
decisions: [{"when":"The primary database supports local transactions","use":"Store the domain change and an outbox row together; relay with a stable event ID.","tradeoff":"Delivery is typically at least once and cleanup needs retention limits."},{"when":"Consumer state and event already share a transactional log","use":"Use the existing transaction or observed change stream with documented replay offsets.","tradeoff":"The log's ordering and recovery guarantees become part of the design."}]
checks: ["Crash between commit, publish and relay acknowledgement and assert eventual delivery.","Retry relay processing and verify a consumer applies the stable event ID once."]
sources: [{"title":"AWS transactional outbox pattern","url":"https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html"},{"title":"PostgreSQL transaction tutorial","url":"https://www.postgresql.org/docs/current/tutorial-transactions.html"}]
related: ["idempotent-consumer"]
---

<!-- Generated record title. -->
# Transactional outbox and reliable delivery

## Scenario

A library records a returned item and informs a notification service. Crashing after committing the return must not silently skip the notification.

## Failure modes

Publishing before commit can expose rolled-back state. Publishing after commit can be skipped on crash. Relay retries can deliver the same event twice.

## Explain it simply

Save the state change and the message-to-send in one transaction, then let a worker deliver it safely.

## Implementation guidance

Write a small, versioned event envelope with a stable ID beside the domain update in one transaction. Relay only committed rows, checkpoint after publish acknowledgement, and expect replay if the process dies between the two. The consumer must make recording the event ID and applying its local effect part of the same transaction, or pass a stable idempotency key to the outside system. Keep retention long enough for recovery and measure lag against the age of the oldest unpublished row.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The primary database supports local transactions** Store the domain change and an outbox row together; relay with a stable event ID. Delivery is typically at least once and cleanup needs retention limits.
- **Consumer state and event already share a transactional log** Use the existing transaction or observed change stream with documented replay offsets. The log's ordering and recovery guarantees become part of the design.

## Verification

- Crash between commit, publish and relay acknowledgement and assert eventual delivery.
- Retry relay processing and verify a consumer applies the stable event ID once.

## Sources

- [AWS transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- [PostgreSQL transaction tutorial](https://www.postgresql.org/docs/current/tutorial-transactions.html)

## Related decisions

- [Idempotent event consumers and inboxes](../backend/idempotent-consumer.md)

<!-- End generated record details. -->
