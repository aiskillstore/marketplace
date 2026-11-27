---
id: "webhook-verification"
title: "Authenticating and processing webhooks"
category: "security"
summary: "Accept external events only after verifying source authenticity and preserving idempotent delivery semantics."
aliases: ["verify webhook signature","signed webhook","replay protection","raw request body","webhook authenticity","webhook imzasını doğrula","ham istek gövdesi","bildirim tekrarını önleme"]
decisions: [{"when":"Provider signing supports timestamped signatures","use":"Use the provider's official verifier on raw bytes and enforce documented replay bounds.","tradeoff":"Clock drift and secret rotation must remain compatible."},{"when":"A provider lacks acceptable signing","use":"Use a trusted restricted integration channel or reconcile through authenticated polling.","tradeoff":"Polling increases latency and cannot rely on immediate push delivery."}]
checks: ["Test valid delivery, changed body, expired signature and repeated authenticated event.","Rotate the signing secret and verify the documented overlap and unfamiliar-key behavior."]
sources: [{"title":"Stripe webhooks and signature verification","url":"https://docs.stripe.com/webhooks"},{"title":"GitHub webhook delivery validation","url":"https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries"}]
---

<!-- Generated record title. -->
# Authenticating and processing webhooks

## Scenario

A shipping provider notifies the warehouse when a package clears customs. The provider retries callbacks until acknowledged.

## Failure modes

Parsing the body before verification can change signed bytes. Valid events can be delivered more than once or out of order, and unsafe logging may expose secrets.

## Explain it simply

Verify who sent the message before acting, then remember which delivery has already been applied.

## Implementation guidance

Pass the exact request bytes to the provider verifier before acting. Enforce the provider’s freshness policy, then record a stable event or delivery identity at the durability boundary. Acknowledge after the durable acceptance if processing runs out of band. Test secret rotation, tampered content, duplicate valid delivery and an older valid event arriving after newer state.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Provider signing supports timestamped signatures** Use the provider's official verifier on raw bytes and enforce documented replay bounds. Clock drift and secret rotation must remain compatible.
- **A provider lacks acceptable signing** Use a trusted restricted integration channel or reconcile through authenticated polling. Polling increases latency and cannot rely on immediate push delivery.

## Verification

- Test valid delivery, changed body, expired signature and repeated authenticated event.
- Rotate the signing secret and verify the documented overlap and unfamiliar-key behavior.

## Sources

- [Stripe webhooks and signature verification](https://docs.stripe.com/webhooks)
- [GitHub webhook delivery validation](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)

<!-- End generated record details. -->
