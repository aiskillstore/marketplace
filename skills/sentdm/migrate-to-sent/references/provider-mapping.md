# Provider-to-Sent mapping reference

## Table of contents

- [How to use this reference](#how-to-use-this-reference)
- [Sent target contract](#sent-target-contract)
- [Twilio](#twilio)
- [Sinch](#sinch)
- [Infobip](#infobip)
- [Vonage](#vonage)
- [MessageBird and Bird](#messagebird-and-bird)
- [Cross-provider concept table](#cross-provider-concept-table)
- [Status mapping](#status-mapping)
- [Webhook signature comparison](#webhook-signature-comparison)
- [Error handling translation](#error-handling-translation)

## How to use this reference

Read the Sent target contract first, then only the section for the incumbent. Each provider section lists the send call, the fallback construct, the webhook scheme, the suppression store, the tenancy construct, and the specific rewrites that testing will not catch.

Verify any header name or field against the incumbent's current documentation before writing customer-facing text; several of these platforms have renamed products and headers.

## Sent target contract

```json
{
  "to": ["+14155551234"],
  "template": {
    "name": "order_confirmation",
    "parameters": { "order_id": "12345", "eta": "Friday" }
  },
  "sandbox": false
}
```

`POST /v3/messages` returns `202` with `data.recipients[]`, each carrying a `message_id`. Only `to` is required; supply `template` or `text`; omit `channel` for automatic routing. Authentication is `x-api-key`, optionally with `x-profile-id` on an organization key. Template parameters are a **named** map, not positional.

For automatic routing the echoed per-recipient channel is not a resolved route and is never updated later. Read the real route from `message.routed`, from `GET /v3/messages/{id}` after routing, or from `GET /v3/messages/{id}/activities`.

## Twilio

| Concept | Twilio | Sent |
| --- | --- | --- |
| Send | `POST /2010-04-01/Accounts/{sid}/Messages.json`, form-encoded | `POST /v3/messages`, JSON |
| Auth | Basic auth with Account SID and auth token | `x-api-key` header |
| Recipient | `To`, with a `whatsapp:` prefix for WhatsApp | `to` array plus the `channel` array |
| Sender | `From` or `MessagingServiceSid` | Profile configuration and routing |
| Content | `Body`, or `ContentSid` with positional variables | `text`, or `template` with named parameters |
| Fallback | Messaging Service features such as Fallback to Long Code | Automatic routing with reroute |
| Status callback | `StatusCallback` per message | Account-level webhook subscription |
| Suppression | Advanced Opt-Out | Platform consent with `opt_out` on the contact |
| Tenancy | Subaccount | Sender Profile |
| Idempotency | Not offered on message create | `Idempotency-Key` header |

Rewrites that testing will not catch: positional `{{1}}` variables become named parameters; numeric error codes such as `21610` for an opted-out recipient become string `error.code` families, and that particular case does not even fail the request — the send is accepted and the message finalizes as `FILTERED`; a per-message `StatusCallback` URL has no equivalent, so status routing moves into the subscription's `event_filters`.

Use this skill for line-by-line translation, then use `sent-integration-starter` to harden the resulting client lifecycle, retries, and observability.

## Sinch

| Concept | Sinch Conversation API | Sent |
| --- | --- | --- |
| Send | `POST /v1/projects/{id}/messages:send` with a channel-priority order | `POST /v3/messages` with automatic routing |
| App model | Conversation API app with configured channels | Sender Profile |
| Webhooks | Up to five per app, created with `triggers[]` | Account-level subscription with `event_types` and `event_filters` |
| Callback auth | OAuth 2.0, or HMAC-SHA256 over `body.nonce.timestamp` | HMAC-SHA256 over `{webhook_id}.{timestamp}.{raw_body}` |
| Consent | `OPT_IN` and `OPT_OUT` trigger events | Platform-enforced consent, applied before the event |
| Delivery reports | Typically three callbacks per message | One event per transition, plus repeats on reroute |

Sinch's trigger catalog is far broader than Sent's two event families, so a handler switching over twenty-plus trigger types collapses to branching on `field` and `event`. Sinch's channel-priority ordering is the ordered-fallback pattern that must become automatic routing.

## Infobip

| Concept | Infobip | Sent |
| --- | --- | --- |
| Send | Channel-specific endpoints, or Conversations | `POST /v3/messages` |
| Sender strategy | Resource Associations and Sending Strategies such as sticky sender | Platform routing rules |
| Webhooks | Subscription plus a notification profile | Webhook registration |
| Webhook auth | Basic, HMAC-SHA256 over the raw body, or OAuth, optionally mTLS; **header name is account-configured** | Fixed `x-webhook-signature` scheme |
| Suppression | Blocklist, also called Do Not Contact | `opt_out` on the contact |
| Tenancy | Applications and Entities | Sender Profiles |

Because Infobip's signing header name comes from account settings, an existing verifier is not portable and its header constant must not be reused. Sending Strategies have no caller-side equivalent: sticky-sender behavior is a platform routing concern in Sent, not a request parameter.

## Vonage

| Concept | Vonage Messages API v1 | Sent |
| --- | --- | --- |
| Send | Per-channel body with `message_type`, `channel`, `to`, `from` | Uniform `POST /v3/messages` |
| Fallback | `failover` array of complete alternative messages | Automatic routing with reroute |
| Webhook auth | JWT in `Authorization: Bearer`, or legacy `sig` parameter | HMAC signature headers |
| Credentials | Application id with a private key | API key |

Vonage's `failover` array is the most explicit ordered-fallback construct of the five, and it is the one most often ported directly into Sent's `channel` array. It must not be. Note also that Vonage's JWT bearer pattern tempts engineers to authenticate to Sent with `Authorization: Bearer`; Sent uses `x-api-key`.

## MessageBird and Bird

| Concept | MessageBird/Bird | Sent |
| --- | --- | --- |
| Send | Conversations API, or channel APIs | `POST /v3/messages` |
| Fallback | Explicit `fallback` object naming a secondary channel | Automatic routing with reroute |
| Webhook auth | `messagebird-signature`, base64 HMAC-SHA256 over timestamp, URL, and a SHA-256 body hash, with `messagebird-request-timestamp` | HMAC-SHA256 over `{webhook_id}.{timestamp}.{raw_body}` |
| Suppression | Platform suppression list | `opt_out` on the contact |

MessageBird's signature covers a hash of the body rather than the body itself, so a verifier ported to Sent will fail every delivery even though both use HMAC-SHA256. Treat the legacy MessageBird header names as legacy and confirm current Bird names before asserting them.

## Cross-provider concept table

| Concept | Twilio | Sinch | Infobip | Vonage | Bird | Sent |
| --- | --- | --- | --- | --- | --- | --- |
| Ordered fallback | Messaging Service features | channel priority | sending strategies | `failover` array | `fallback` object | **automatic routing only** |
| Tenancy | subaccount | Conversation app | Application/Entity | application | workspace | Sender Profile |
| Template variables | positional | per-channel | per-channel | per-channel | per-channel | **named map** |
| Consent store | Advanced Opt-Out | OPT_IN/OPT_OUT events | Blocklist | application-side | suppression list | `opt_out`, channel-agnostic |
| Idempotency | Verify current send contract | Verify current send contract | Verify current send contract | Verify current send contract | Verify current send contract | `Idempotency-Key` |
| Webhook scope | per message or service | per app, up to five | per subscription | per application | per workspace | per account, filtered |

## Status mapping

| Sent | Twilio | Sinch | Note |
| --- | --- | --- | --- |
| `QUEUED` | `queued`, `accepted` | `QUEUED_ON_CHANNEL` | Accepted only |
| `ROUTED` | — | — | No incumbent analogue; repeats on reroute |
| `SENT` | `sent` | `MESSAGE_SUBMIT` | Provider handoff |
| `DELIVERED` | `delivered` | `DELIVERED` | Handset confirmation |
| `READ` | `read` | `READ` | WhatsApp and RCS only |
| `FAILED` | `failed`, `undelivered` | `FAILURE` | May reroute; not necessarily final |
| `FILTERED` | error 21610 behavior | opt-out enforcement | Policy gate; never retry |
| `BLOCKED` | account errors | account errors | Account precondition |
| `SCHEDULED` | — | — | Quiet-hours parking |

The two states with no analogue, `FILTERED` and `BLOCKED`, are exactly the two that ported retry logic mishandles.

## Webhook signature comparison

| Provider | Algorithm | Signed content | Header |
| --- | --- | --- | --- |
| Twilio | HMAC-SHA1 | full URL plus sorted POST parameters | `X-Twilio-Signature` |
| Sinch | HMAC-SHA256 | `body.nonce.timestamp` | `x-sinch-webhook-signature` plus nonce, timestamp, algorithm |
| Infobip | HMAC-SHA256 | raw body | account-configured |
| Vonage | JWT, or MD5/HMAC over sorted parameters | token claims, or parameters | `Authorization`, or `sig` |
| Bird | HMAC-SHA256 | timestamp, URL, SHA-256 of body | `messagebird-signature` |
| **Sent** | HMAC-SHA256 | `{webhook_id}.{timestamp}.{raw_body}` | `x-webhook-signature` as `v1,{base64}` |

Among the compared schemes, Sent includes the endpoint id in the signed content and expects a `v1,` version prefix. No listed provider's verifier is reusable as-is, and no Sent SDK ships one, so plan the receiver as new code with its own tests.

## Error handling translation

| Incumbent pattern | Sent replacement |
| --- | --- |
| Numeric error codes in a switch statement | String `error.code` with prefix families |
| Retry on any non-delivered status | Retry only `429`, `5xx`, `SERVICE_001`, and `CONFLICT_001` once |
| Opt-out surfaced as a send error | Send accepted with `202`; message finalizes as `FILTERED` |
| Insufficient balance surfaced as a send error | Send accepted with `202`; message finalizes as `BLOCKED` |
| Per-request quota headers | Headers only on `429`; pace by design |
| Provider-side deduplication assumptions | Supply a deterministic `Idempotency-Key` |

Consent and balance problems moving out of the error path and into delivery data is the structural change that most often surprises a migrating team: monitor filtered and blocked rates as first-class metrics.
