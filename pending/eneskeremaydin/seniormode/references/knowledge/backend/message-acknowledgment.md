---
id: "message-acknowledgment"
title: "Durable message delivery and acknowledgments"
category: "backend"
summary: "Track durable messages across disconnection, acknowledgement loss and repeated delivery."
aliases: ["ack","message queue","offline message delivery","teslim onayı","redelivery","telefon kapalı mesaj nerede bekler","mesaj teslim onayı","kuyrukta tekrar teslim"]
decisions: [{"when":"A durable update must survive disconnection","use":"Store pending messages and acknowledge only after the consumer records the effect.","tradeoff":"State must be retained, and redelivery is a normal case."},{"when":"Updates are replaceable snapshots with latest-state semantics","use":"Use a versioned snapshot or a coalesced notification plus readback.","tradeoff":"Intermediate events may be skipped by design."}]
checks: ["Lose an acknowledgement and verify the consumer effect still occurs once.","Reorder deliveries across a reconnect and verify documented ordering semantics."]
sources: [{"title":"RabbitMQ consumer acknowledgements and confirms","url":"https://www.rabbitmq.com/docs/confirms"},{"title":"Apache Kafka documentation","url":"https://kafka.apache.org/documentation/"}]
related: ["idempotent-consumer","retry-backoff"]
---

<!-- Generated record title. -->
# Durable message delivery and acknowledgments

## Scenario

A field tablet reconnects after hours offline. An order update must remain available until the tablet records it durably.

## Failure modes

Acknowledging before persistence loses updates on crash. Retrying after an acknowledgement is lost can duplicate side effects. Redelivery can change order.

## Explain it simply

Keep an update until the device confirms it saved it, and recognize repeats by their ID.

## Implementation guidance

Decide whether the tablet must see every update or simply converge to the latest order state. For required events, persist applied state and the stable event identity together before acknowledging. Use idempotent handlers for redelivery and a stated conflict or ordering rule. If a durable snapshot satisfies the product, a reconnect may fetch authoritative state rather than maintaining every transient notification. Test an acknowledgement lost after commit and a client whose resume window expired.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A durable update must survive disconnection** Store pending messages and acknowledge only after the consumer records the effect. State must be retained, and redelivery is a normal case.
- **Updates are replaceable snapshots with latest-state semantics** Use a versioned snapshot or a coalesced notification plus readback. Intermediate events may be skipped by design.

## Verification

- Lose an acknowledgement and verify the consumer effect still occurs once.
- Reorder deliveries across a reconnect and verify documented ordering semantics.

## Sources

- [RabbitMQ consumer acknowledgements and confirms](https://www.rabbitmq.com/docs/confirms)
- [Apache Kafka documentation](https://kafka.apache.org/documentation/)

## Related decisions

- [Idempotent event consumers and inboxes](idempotent-consumer.md)
- [Retry budgets, backoff and jitter](../reliability/retry-backoff.md)

<!-- End generated record details. -->
