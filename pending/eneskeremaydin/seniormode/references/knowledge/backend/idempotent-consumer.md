---
id: "idempotent-consumer"
title: "Idempotent event consumers and inboxes"
category: "backend"
summary: "Apply broker messages in a recoverable way when multiple deliveries are possible."
aliases: ["consumer deduplication","processed event IDs","inbox pattern","duplicate event","idempotent consumer","aynı olay iki kez işlendi","tüketicide tekrarları önleme","işlenmiş olay kimliği"]
decisions: [{"when":"The effect and deduplication record share a database","use":"Record the event ID and apply the effect in one transaction with a unique constraint.","tradeoff":"Deduplication state grows and needs retention tied to replay policy."},{"when":"The downstream system owns the effect","use":"Pass a stable idempotency key to the downstream API and reconcile ambiguous outcomes.","tradeoff":"The external provider's key lifetime and error semantics constrain recovery."}]
checks: ["Kill a worker after committing the effect but before acknowledging the message.","Deliver one event to two workers and verify one durable effect.","Replay an old dead-letter delivery at the retention boundary and verify the declared behavior."]
sources: [{"title":"RabbitMQ consumer acknowledgements and confirms","url":"https://www.rabbitmq.com/docs/confirms"},{"title":"Stripe idempotent requests","url":"https://docs.stripe.com/api/idempotent_requests"},{"title":"PostgreSQL constraints","url":"https://www.postgresql.org/docs/current/ddl-constraints.html"}]
---

<!-- Generated record title. -->
# Idempotent event consumers and inboxes

## Scenario

A badge service receives event records from a broker. Redelivery after a process crash must not award the same badge twice.

## Failure modes

A transient in-memory seen set disappears on restart. Marking as processed before the application transaction succeeds can drop legitimate work.

## Explain it simply

Keep a durable receipt for the events already applied so a repeat delivery changes nothing.

## Implementation guidance

Scope the identity to the event stream and the consumer effect when the same event can legitimately drive several consumers. In a database transaction, insert the processed marker and write the effect together. Acknowledge only after commit. Keep markers through the supported replay window, including dead-letter replays and operator backfills. Define an explicit recovery route for older deliveries before dropping these markers. If the effect is outside that transaction, send the existing identity to a provider with idempotency support and retain an explicit pending state for ambiguous replies. Once the provider key can expire, resolve pending outcomes against its authoritative state before issuing another effect.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The effect and deduplication record share a database** Record the event ID and apply the effect in one transaction with a unique constraint. Deduplication state grows and needs retention tied to replay policy.
- **The downstream system owns the effect** Pass a stable idempotency key to the downstream API and reconcile ambiguous outcomes. The external provider's key lifetime and error semantics constrain recovery.

## Verification

- Kill a worker after committing the effect but before acknowledging the message.
- Deliver one event to two workers and verify one durable effect.
- Replay an old dead-letter delivery at the retention boundary and verify the declared behavior.

## Sources

- [RabbitMQ consumer acknowledgements and confirms](https://www.rabbitmq.com/docs/confirms)
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests)
- [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)

<!-- End generated record details. -->
