# Sent channel routing model

## Table of contents

- [Channel vocabulary](#channel-vocabulary)
- [Broadcast semantics](#broadcast-semantics)
- [Route selection pipeline](#route-selection-pipeline)
- [Pinned-channel behavior](#pinned-channel-behavior)
- [Send-time fallback across candidates](#send-time-fallback-across-candidates)
- [Reroute after delivery failure](#reroute-after-delivery-failure)
- [Where each channel value surfaces](#where-each-channel-value-surfaces)
- [Status lifecycle](#status-lifecycle)
- [Channel capability limits](#channel-capability-limits)

## Channel vocabulary

| Value | Meaning |
| --- | --- |
| `sent` | Automatic routing. The default when `channel` is omitted or supplied as an empty array |
| `sms` | Pin to SMS |
| `whatsapp` | Pin to WhatsApp |
| `rcs` | Pin to RCS |
| `auto` | Internal placeholder for an unresolved automatic route. Appears in responses and events, never as an input |

Any other value returns `400`. Treat `auto` as read-only diagnostic output and never display it to an end user as a channel name.

## Broadcast semantics

The `channel` array enumerates channels to send on, not an order of preference. The number of messages created is `len(to) × len(channel)`, each with its own `message_id`, its own lifecycle, and its own charge.

```json
{
  "to": ["+14155551234", "+14155555678"],
  "channel": ["whatsapp", "sms"],
  "template": { "name": "order_confirmation", "parameters": { "order_id": "12345" } }
}
```

That request creates four messages. The `202` response enumerates all four in `data.recipients[]`.

There is no `fallback` field, no priority weighting, and no way to express "try this, then that" through the array. Ordered arrays or explicit failover objects are common on incumbent platforms, which makes porting them into Sent's channel array a high-risk migration defect.

## Route selection pipeline

For automatic routing, the platform evaluates its maintained routing rules at send time. Rules can constrain on:

- recipient attributes: country, number prefix, exact number, carrier, number type, and ported state;
- the sender;
- template attributes: id, name, and category;
- channel;
- whether the destination is international.

Candidates are ordered by:

1. exact-recipient rules ahead of everything else;
2. account-scoped rules ahead of global rules;
3. match specificity;
4. explicit rule priority;
5. longer number prefix;
6. older rule as the final tie-break.

Exclusions applied before selection: inactive, deleted, or expired rules; rules whose own minimum match threshold is not met; and candidates on a channel where the template carries an explicit non-approved review status such as rejected, pending, or paused. A channel with **no** recorded per-channel review is not excluded — absence of review is not disapproval.

The first surviving candidate becomes the attempted route, the message moves to `ROUTED`, and `message.routed` fires. Remaining candidates stay available as fallback routes for that message.

Two consequences worth stating to users. There is no fixed cross-channel preference order, so any claim like "RCS is tried first" is unsupported. And because rules are platform-maintained rather than caller-supplied, an application cannot express routing preference through the API; it can only choose automatic routing or pin a channel.

## Pinned-channel behavior

Pinning narrows candidate matching to the named channel. Rules that carry no channel constraint still match and resolve to the pinned channel, so pinning works even without channel-specific rules.

A pinned message never crosses to a different channel. Same-channel provider hops remain possible when the matched rule permits them, which means a pinned SMS message can still be retried through a different provider. If no route matches on the pinned channel, the message ends `FAILED` with no route matched rather than falling back.

Pin for a hard requirement: a compliance rule that mandates a channel, a contract that prices a channel, or content that only renders on one channel. Prefer automatic routing everywhere else.

## Send-time fallback across candidates

Fallback at send time walks the candidate list rather than the caller's array. When a candidate route carries a DENY decision that permits fallback, evaluation moves to the next candidate. When a DENY does not permit fallback — including the case where every candidate is denied — the message finalizes as `FILTERED` and the record carries the denied route's channel.

This is why `FILTERED` must never be retried blindly. The gate is a policy decision, most often consent, and repeating the send reproduces the same outcome while risking a compliance violation.

## Reroute after delivery failure

Reroute happens only when a terminal failure indicates a route or carrier problem that another route might overcome:

| Failure signal | Reroutes |
| --- | --- |
| Undeliverable by this route | Yes |
| Provider service unavailable | Yes |
| Provider timeout | Yes |
| Transport error | Yes |
| Recipient-side rejection on WhatsApp after acceptance | Yes, and records a recipient-scoped rule that WhatsApp is not deliverable for that number |
| Invalid content or template parameters | No |
| Consent block | No |
| Account precondition | No |
| Any other failure | No |

Mechanics that affect application code: the reroute reuses the same `message_id`, re-runs the pipeline so `QUEUED` and `ROUTED` transitions and their webhooks fire again, excludes already-attempted routes, re-applies consent gates on every attempt, and stops at a ceiling of three distinct channel-and-provider pairs across the initial send and all reroutes.

Therefore a `message.failed` event is not proof of final failure. Treat a message as finally failed only when its stored state remains failed and no further events arrive, and make the status projection idempotent so repeated `queued` and `routed` events do not double-count.

## Where each channel value surfaces

| Surface | Automatic routing | Pinned channel |
| --- | --- | --- |
| `202` response `data.recipients[].channel` | Not a resolved route, and never updated later | The pinned channel |
| `message.queued`, `message.routed`, `message.scheduled` | `sent` | The pinned channel |
| Terminal events after a route was attempted | The attempted route's channel | The pinned channel |
| Terminal events for a message that ended before routing | `auto` | `auto` |
| `GET /v3/messages/{id}` before routing | `auto` | The pinned channel |
| `GET /v3/messages/{id}` after routing | The attempted route's channel | The pinned channel |

The practical rule: never treat the send response as routing evidence. Resolve routes from `message.routed`, from `GET /v3/messages/{id}` after routing, or from the activity history.

## Status lifecycle

| Status | Final for the logical message | Meaning |
| --- | --- | --- |
| `QUEUED` | No | Accepted into the pipeline |
| `SCHEDULED` | No | Parked by quiet-hours policy; re-enters the pipeline automatically |
| `ROUTED` | No | A channel and provider were selected |
| `SENT` | No | Handed to the provider |
| `DELIVERED` | Yes | Confirmed at the handset |
| `READ` | Yes | Read by the recipient; WhatsApp and RCS only |
| `FAILED` | Not always | One attempt failed; a newer automatic reroute may follow on the same message id |
| `FILTERED` | Yes | Policy gate: consent block or route denial |
| `BLOCKED` | Yes | Account precondition: balance, onboarding quota, unapproved template |
| `RECEIVED` | — | Inbound message |

`FILTERED` and `BLOCKED` are not carrier failures. Feeding them into retry logic produces either a compliance problem or a retry loop that cannot succeed until an account action is taken.

## Channel capability limits

RCS currently supports text plus up to four suggestion chips, mapped from template buttons, with rich cards, carousels, and media on the roadmap. Every outbound RCS message receives an appended STOP chip, so an RCS surface always exposes an opt-out affordance the application did not author.

`READ` reaches only WhatsApp and RCS; its absence on SMS is expected. Inbound support differs by channel as well — SMS inbound depends on an MO-capable provider and a supported number type, so alphanumeric sender IDs never receive replies. Route consent and inbound questions to the two-way messaging skill.
