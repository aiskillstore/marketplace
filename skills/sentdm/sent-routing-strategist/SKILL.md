---
name: sent-routing-strategist
description: Decides how a Sent message should reach the recipient — automatic routing versus a pinned channel, what the channel array actually does, how fallback and reroute work, and why a message ended as FAILED, FILTERED, BLOCKED, or channel "auto". Use when choosing the channel field, expecting WhatsApp-to-SMS fallback, debugging an unexpected route or duplicate charges from multiple channels, or interpreting message status and activity evidence.
---

# Sent Routing Strategist

Routing is where the most expensive Sent misconceptions live. Two facts govern almost every decision:

1. **The `channel` array is a broadcast list, not a preference order.** `["whatsapp", "sms"]` with two recipients creates four messages and four charges. There is no `fallback` field and no ordered-preference syntax.
2. **Automatic routing is the fallback mechanism.** Omit `channel`, or send `["sent"]`, and the platform selects a route, then reroutes across up to three distinct channel-and-provider pairs when a route-level failure occurs.

## Decide the channel value

| Intent | Correct value | Reason |
| --- | --- | --- |
| Reach the recipient however works best | omit `channel` or `["sent"]` | Enables route selection and reroute |
| Guarantee one specific channel | `["sms"]`, `["whatsapp"]`, or `["rcs"]` | Pinning restricts matching to that channel and never crosses channels |
| Deliberately deliver the same content on several channels | `["whatsapp", "sms"]` | Broadcast; expect one message and one charge per pair |
| "Try RCS, fall back to SMS" | omit `channel` or `["sent"]` | An ordered array would broadcast; automatic routing performs the fallback |

Any value outside `sent`, `sms`, `whatsapp`, and `rcs` returns `400`. When a user asks for ordered fallback, name the misconception explicitly before writing code, because the failure mode is duplicate delivery and duplicate cost rather than an error.

## What a pinned channel gives up

Pinning restricts route matching to the named channel. Rules without a channel constraint still match and resolve to the pinned channel, so pinning does not require channel-specific rules to exist. A pinned send never crosses to a different channel, though same-channel provider hops remain possible when a rule permits them. If no route exists on the pinned channel, the message ends `FAILED` with no route matched — it does not silently fall back.

Pin when a compliance, contractual, or content constraint requires a specific channel. Otherwise prefer automatic routing.

## Reading the outcome

`POST /v3/messages` returns `202` with per-recipient `message_id` values. For automatic routing, the echoed per-recipient channel is not a resolved route and is never updated afterward. Resolve the truth from evidence:

| Question | Evidence |
| --- | --- |
| Which route was actually attempted | `message.routed` event, or `channel` on `GET /v3/messages/{id}` after routing |
| Did the recipient's device receive it | `message.delivered` |
| What sequence of routes was tried | `GET /v3/messages/{id}/activities` |
| Why did it stop | Terminal status plus channel value |

## Terminal status interpretation

| Status | Meaning | Correct response |
| --- | --- | --- |
| `FAILED` | A route attempt failed; automatic routing may still enqueue another attempt | Inspect the latest message state and activities before treating it as final |
| `FILTERED` | Policy gate — consent block or route denial | Never retry; a consent block is a compliance stop |
| `BLOCKED` | Account precondition — balance, onboarding quota, unapproved template | Fix the account condition, then send again |
| `SCHEDULED` | Parked by quiet-hours policy | Wait; it re-enters the pipeline automatically |

An outcome whose `channel` is `auto` means the message ended before any route was attempted. The causes are no matching route, invalid template parameters, a consent block, or an account precondition. Account preconditions do not reject the send request: it is accepted with `202` and the affected messages surface as `BLOCKED`.

Sent records internal send-time reason codes on the message for these cases, but does not return them in API responses or webhooks, so diagnosis relies on the status-and-channel combination plus the activity history. The mapping from observable evidence to root cause is tabulated in [references/routing-diagnosis.md](references/routing-diagnosis.md).

## Reroute behavior

A failed route is retried only when the terminal failure signals a route or carrier problem another route might overcome: undeliverable by this route, provider service unavailable, provider timeout, or transport error. Every other failure stays `FAILED`.

Reroute reuses the **same `message_id`** and re-runs the pipeline, so `message.queued` and `message.routed` fire again, consent gates re-apply on every attempt, and already-attempted routes are excluded. The ceiling is three distinct channel-and-provider pairs across the initial send and all reroutes.

The WhatsApp-to-SMS behavior customers ask about is a specific case of this: a WhatsApp message accepted and then failed for a recipient-side reason reroutes and records a recipient-scoped rule that WhatsApp is not deliverable for that number, so subsequent automatic sends skip WhatsApp for that recipient. It requires automatic routing; a pinned WhatsApp send cannot produce it.

## How automatic routing selects a route

Routes come from platform-maintained rules evaluated at send time against recipient attributes (country, number prefix, exact number, carrier, number type, ported state), sender, template attributes, channel, and whether the destination is international. Ordering is: exact-recipient rules first, then account-scoped before global, then match specificity, then rule priority, then longer number prefix, then the older rule. Inactive, deleted, expired, and below-threshold rules are excluded. Candidates whose template has an explicit non-approved review status on that channel are dropped, while a channel with no recorded review is not blocked. The first surviving candidate wins and the rest remain available as fallback routes.

There is no fixed channel preference order, so never promise "RCS first, then WhatsApp, then SMS." Read [references/routing-model.md](references/routing-model.md) before making any claim about why a specific route was chosen.

## Cost and volume consequences

Because broadcast multiplies messages by recipients, review any multi-channel array against expected spend before sending. A 1,000-recipient send with two channels is 2,000 messages. The per-request recipient ceiling is 1,000, and documented pacing pairs full batches with roughly one request per second to stay inside the 200-requests-per-minute budget.

RCS today carries text plus up to four suggestion chips, mapped from template buttons, and every outbound RCS message receives an appended STOP chip. Do not design an RCS-pinned flow that depends on rich cards, carousels, or media.

## Boundaries

Use `sent-messaging` to execute a single send with confirmation, `sent-two-way-messaging` for consent and inbound keyword semantics, `messaging-performance-analyzer` for aggregate delivery-rate regressions, and `sent-webhook-engineer` for receiving and deduplicating the events this skill teaches you to read.
