---
id: "payment-idempotency"
title: "Idempotent payments and retry identity"
category: "concurrency"
summary: "Preserve one durable financial effect per payment intent despite timeouts, retries and concurrent submissions."
aliases: ["idempotency key","double charge","duplicate payment","çift ödeme","payment retry","ödeme isteği zaman aşımı","iki kere para çekilmesi","aynı tahsilatı tekrar deneme","çift tahsilat"]
decisions: [{"when":"The provider supports a durable idempotency key","use":"Reuse the same scoped intent key and persist outcomes under a unique constraint.","tradeoff":"The record needs retention rules and a recovery path for unknown outcomes."},{"when":"External outcome and local state can diverge","use":"Track pending states and reconcile provider confirmations via independently validated events.","tradeoff":"Operations must handle eventual confirmation and manual escalation for ambiguity."}]
checks: ["Race identical requests and assert one processor effect through recorded counters.","Retry after a timeout and reject key reuse for a different payload or caller.","Simulate provider acceptance followed by a lost reply and key expiry, and verify reconciliation without a second charge."]
sources: [{"title":"Stripe idempotent requests","url":"https://docs.stripe.com/api/idempotent_requests"},{"title":"PostgreSQL constraints","url":"https://www.postgresql.org/docs/current/ddl-constraints.html"}]
related: ["idempotent-consumer","transactional-outbox"]
---

<!-- Generated record title. -->
# Idempotent payments and retry identity

## Scenario

A ticket purchase call reaches the processor but the phone loses connectivity before receiving the response. The client attempts the same purchase again.

## Failure modes

Disabling a button cannot stop network retries. Keys detached from the account or payload can replay the wrong result. A crash between local and external writes needs reconciliation.

## Explain it simply

Give each payment intent a stable receipt number so repeating the same request does not charge twice.

## Implementation guidance

Create an intent once per logical checkout and persist a unique (account, intent) key with a hash of the material request fields. Replays for the same key and fields should expose the known result or pending state. Changed inputs need a new intent or a conflict. Pass the same key to the provider, record its reference when available and learn the provider's retry horizon and outcome semantics. Stripe's API v1 can reuse even a recorded server-error response and can treat an expired key as a new request. Keep the local record through the reconciliation and retried-client window. For an unresolved outcome beyond the provider's safe retry window, query the provider by known reference or move the intent to manual reconciliation before accepting a new charge.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The provider supports a durable idempotency key** Reuse the same scoped intent key and persist outcomes under a unique constraint. The record needs retention rules and a recovery path for unknown outcomes.
- **External outcome and local state can diverge** Track pending states and reconcile provider confirmations via independently validated events. Operations must handle eventual confirmation and manual escalation for ambiguity.

## Verification

- Race identical requests and assert one processor effect through recorded counters.
- Retry after a timeout and reject key reuse for a different payload or caller.
- Simulate provider acceptance followed by a lost reply and key expiry, and verify reconciliation without a second charge.

## Sources

- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests)
- [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)

## Related decisions

- [Idempotent event consumers and inboxes](../backend/idempotent-consumer.md)
- [Transactional outbox and reliable delivery](../architecture/transactional-outbox.md)

<!-- End generated record details. -->
