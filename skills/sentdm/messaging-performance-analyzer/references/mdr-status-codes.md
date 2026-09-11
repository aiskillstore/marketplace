# MDR status & error codes — reference

Supporting reference for `messaging-performance-analyzer`. "MDR" is the human term for Sent's per-message status stream; the v3 surfaces are `GET /v3/messages/{id}` and `GET /v3/messages/{id}/activities`. The codes below are Sent's own normalized catalog as documented at docs.sent.dm — not raw provider codes.

Authoritative upstream sources (for the downstream provider codes that may appear in `error.details` after Sent normalization):

- WhatsApp: [Cloud API Error Codes](https://developers.facebook.com/docs/whatsapp/cloud-api/support/error-codes)
- SMS: TCR + carrier-specific reject reasons (T-Mobile, AT&T, Verizon each publish their own list)
- RCS: [RBM API errors](https://developers.google.com/business-communications/rcs-business-messaging/reference/rest)

## Table of contents

- [Message status lifecycle](#message-status-lifecycle)
- [Synchronous errors](#synchronous-errors-http-response-body)
- [Send-time per-message errors](#send-time-per-message-errors)
- [Webhook payload shape](#webhook-payload-shape)
- [Webhook event lifecycle](#webhook-event-lifecycle)
- [Provider-level codes](#provider-level-codes-referential-not-sent-normalized)
- [Counting rules](#counting-rules)
- [Source notes](#source-notes)

## Message status lifecycle

Sent normalizes channels into a shared delivery state machine. The latest status per `message_id` determines its current outcome, while an activity history supplies the evidence for transition counts. Do not backfill earlier stages from a latest-only record.

```
QUEUED -> ROUTED -> SENT -> DELIVERED -> READ   (WhatsApp & RCS only)
  |         |        |         |
FAILED   FAILED   FAILED    FAILED
```

| Status | Meaning |
|---|---|
| `QUEUED` | Accepted by Sent, waiting to dispatch. |
| `ROUTED` | Assigned to a carrier/provider path. |
| `SENT` | Dispatched to the upstream provider (carrier / WhatsApp Cloud API / RBM). |
| `DELIVERED` | Confirmed delivery to device. |
| `READ` | Recipient opened. WhatsApp + RCS only — SMS has no equivalent. |
| `FAILED` | Terminal failure; the per-message reason is in the `description` field. |
| `RECEIVED` | Inbound message from end user. |

A message can transition `SENT -> DELIVERED -> FAILED`; classify its terminal outcome from the final observed event while retaining the actual journey for transition analysis. `READ` is WhatsApp/RCS engagement, not an SMS delivery stage.

## Synchronous errors (HTTP response body)

These come back in the `error.code` field of the `POST /v3/messages` (or other mutation) response envelope. They abort the request — no message rows are created for the affected recipients.

### Authentication / account state

| Code | HTTP | Meaning |
|---|---|---|
| `AUTH_001` | 401 | Missing `x-api-key` header. |
| `AUTH_002` | 401 | Invalid / unrecognized API key. |
| `AUTH_004` | 403 | User role lacks permission for this operation. |
| `AUTH_005` | 403 | Account valid + setup complete but pending final activation by Sent. |
| `AUTH_006` | 403 | KYC not complete. Account in `SIGNED_UP`, `KYC_STARTED`, `WHITELISTED`, `ONBOARDING_STARTED`, or `KYC_RESUBMISSION_REQUESTED`. |
| `AUTH_007` | 403 | KYC done but no messaging channel configured. Account in `KYC_COMPLETED` or `MESSAGE_COMPLIANCE_COMPLETED`. |

Triage rule: if `AUTH_005/006/007` is producing all the failures, the fix is in onboarding, not messaging — escalate to `sender-profile-architect`.

### Validation

| Code | HTTP | Meaning |
|---|---|---|
| `VALIDATION_001` | 400 | Generic request validation; `error.details` is `{field: [messages]}`. |
| `VALIDATION_002` | 400 | Phone number not in E.164 (`+CCNNNNNNNNNN`). |
| `VALIDATION_003` | 400 | UUID malformed. |
| `VALIDATION_004` | 400 | Required field missing. |
| `VALIDATION_005` | 400 | Value out of range (e.g. `retry_count` 1-5, `timeout_seconds` 5-120). |
| `VALIDATION_006` | 400 | Invalid enum (case-sensitive). |
| `VALIDATION_007` | 400 | `Idempotency-Key` violates format (`^[a-zA-Z0-9_-]{1,255}$`). |

### Resource

| Code | HTTP | Meaning |
|---|---|---|
| `RESOURCE_001` | 404 | Contact not found. |
| `RESOURCE_002` | 404 | Template not found. |
| `RESOURCE_003` | 404 | Message not found. |
| `RESOURCE_004` | 404 | Customer not found. |
| `RESOURCE_005` | 404 | Organization not found. |
| `RESOURCE_006` | 404 | User not found. |
| `RESOURCE_007` | 409 | Resource already exists. |
| `RESOURCE_008` | 404 | Webhook not found. |

### Business logic (most operationally interesting)

| Code | HTTP | Meaning |
|---|---|---|
| `BUSINESS_001` | 422 | Cannot modify inherited contact (read-only from parent org / shared profile). |
| `BUSINESS_002` | 429 | Rate limit exceeded. |
| `BUSINESS_003` | 422 | Insufficient account balance. |
| `BUSINESS_004` | 422 | All recipients have `opt_out=true` — the entire batch is rejected synchronously. |
| `BUSINESS_005` | 422 | WhatsApp template not approved (still `PENDING` or `REJECTED`). |
| `BUSINESS_006` | 422 | Message can only be modified in `QUEUED` or `ACCEPTED` state. |
| `BUSINESS_007` | 422 | Channel not available for this contact (check the contact's `available_channels`). |
| `BUSINESS_008` | 422 | Operation exceeds account quota. |

Note the per-message vs batch distinction: `BUSINESS_004` aborts the whole call. `ERR_CONSENT_BLOCKED` (below) is the per-recipient equivalent — same root cause, different surface.

### Conflict / service / internal

| Code | HTTP | Meaning |
|---|---|---|
| `CONFLICT_001` | 409 | Concurrent idempotent request in flight; retry after a short delay. |
| `SERVICE_001` | 503 | Cache service unavailable. |
| `INTERNAL_001` | 500 | Unexpected internal server error. |
| `INTERNAL_002` | 500 | Database operation failed. |
| `INTERNAL_003` | 502 | External SMS / WhatsApp / RCS provider error. |
| `INTERNAL_004` | 504 | Internal timeout. |
| `INTERNAL_005` | 503 | Service temporarily unavailable (maintenance / overload). |

If you see `INTERNAL_003` dominating a cohort, the upstream provider is the proximate cause — but Sent surfaces the failure synchronously, so it counts as a request-time error, not a per-message FAILED.

## Send-time per-message errors

These do **not** appear in the HTTP response. The request returns 202 with `QUEUED`; the message later transitions to `FAILED` and the code is exposed in the `description` field of:

- `GET /v3/messages/{id}` when `status=FAILED`
- `GET /v3/messages/{id}/activities` on the FAILED activity row
- The `message.failed` webhook payload — but the webhook payload itself only carries `message_status=FAILED`, so you must fetch the message detail to see the code

| Code | Meaning |
|---|---|
| `ERR_CONSENT_BLOCKED` | Per-recipient consent block: contact has `opt_out=true` or is on a phone-channel suppression list. No provider call, no charge. The per-recipient cousin of `BUSINESS_004`. |
| `ERR_ROUTE_DENIED` | No active route could deliver to the requested channel/country combination. |
| `ERR_TEMPLATE_PARAMS_INVALID` | Required template variables missing, or a variable failed regex/type validation. |

A funnel where many messages reach `ROUTED` and then fail with `ERR_ROUTE_DENIED` is a routing-table / sender-profile problem, not a delivery problem. A spike in `ERR_TEMPLATE_PARAMS_INVALID` is a caller bug — hand off via `waba-template-author` or `template-builder-ui` to fix the call site.

## Webhook payload shape

The verified envelope is:

```json
{
  "field": "message",
  "sub_type": "message.delivered",
  "timestamp": "2026-01-15T10:35:00+00:00",
  "payload": {
    "account_id": "<UUID>",
    "message_id": "<UUID>",
    "message_status": "DELIVERED",
    "channel": "sms",
    "inbound_number": "+1...",
    "outbound_number": "+1...",
    "template_id": "<UUID>"
  }
}
```

- Top-level shape is fixed: `field`, `sub_type`, `timestamp`, `payload`.
- `sub_type` follows `<field>.<event>` (e.g. `message.queued`, `message.routed`, `message.sent`, `message.delivered`, `message.read`, `message.failed`).
- The payload carries identifiers and status — **not** the failure description. For FAILED, fetch `GET /v3/messages/{message_id}` to read `description`.

### Webhook health (config object)

Use the webhook record itself to distinguish "delivery is broken" from "ingestion is broken":

| Field | Meaning |
|---|---|
| `is_active` | Webhook accepts events. If false, nothing is fanned out. |
| `last_delivery_attempt_at` | When Sent last attempted POST to the customer's endpoint. |
| `last_successful_delivery_at` | When the customer's endpoint last returned 2xx. A growing gap between these two fields means the endpoint is failing, not the messages. |
| `consecutive_failures` | A non-zero, monotonically rising value is the canonical "your endpoint is down" signal. |
| `retry_count` | 1-5; default 3. |
| `timeout_seconds` | 5-120; default 30. |
| `event_types`, `event_filters` | Which events fan out. If `event_filters: {"message": ["delivered"]}` then `message.failed` will never reach the endpoint, which can read as "no failures" downstream. |

## Webhook event lifecycle

The verified per-message webhook sequence:

1. `message.queued`
2. `message.routed`
3. `message.sent`
4. `message.delivered`
5. `message.read` (WhatsApp / RCS only)

On failure at any stage: `message.failed` with `payload.message_status=FAILED`. The reason is in the message detail (`description`), not the webhook payload.

## Provider-level codes (referential, not Sent-normalized)

The codes below are downstream provider responses. They may appear inside Sent's `description` or `error.details` after the normalized Sent code, but they are **not** part of the Sent v3 enum.

### WhatsApp — Meta error codes (illustrative)

| Code | Meaning | Typical root cause |
|---|---|---|
| `131005` | Access denied | App lost permission; re-auth via `waba-embedded-signup`. |
| `131026` | Message undeliverable | Recipient not on WhatsApp / number invalid / blocked sender. |
| `131047` | Re-engagement message | 24h customer-service window expired; must send a template. |
| `131048` | Spam rate limit | Per-recipient or per-account quality dropped. |
| `131056` | Pair rate-limit | Too many messages to same recipient in short window. |
| `132000` | Template paused (Meta-side) | Template exceeded quality threshold. **Note:** Sent's own `templates.status` enum is `APPROVED` / `PENDING` / `REJECTED` only — there is no `PAUSED` in the Sent API surface; this code may still show up in the message `description`. |
| `132001` | Template does not exist | Wrong template name / language. |
| `133006` | Phone number not registered | Embedded Signup `/register` step skipped or failed. |
| `133016` | Account daily messaging limit reached | Tier exhausted for the 24h period. |

### SMS — carrier reject categories (illustrative)

Carriers don't share an enum; the categories you actually need to triage on:
- Carrier filter (per network — T-Mobile / AT&T / Verizon — same content can pass on one and fail on another)
- Throughput throttle
- Invalid / landline / unknown subscriber
- Opt-out (STOP keyword)
- Campaign suspended / brand rejected (TCR-side)
- No DLR returned

### RCS — RBM reject categories (illustrative)

- Capability mismatch (not RCS-capable, capability revoked)
- Agent state (not launched in this carrier, suspended)
- Quota / QPS
- Content rejected (rich card schema invalid, suggestion invalid)
- Suggestion timeout (UX signal, not a failure)
- No DLR returned

## Counting rules

- **Use Sent `message_id`** as the primary unit. Provider IDs (carrier message IDs, `wamid`, RBM `messageId`) are useful for escalation but are **not** in the v3 docs as join keys.
- **Use the latest observed event for the outcome** — a `FAILED` after `DELIVERED` is a terminal failure; a `READ` after `DELIVERED` is a delivered message with observed engagement.
- **Use only explicit history for transitions.** A latest-only `DELIVERED` record does not prove the export observed `QUEUED`, `ROUTED`, or `SENT`; render those transition denominators as unavailable.
- **Separate pending/deferred records** (`QUEUED`/`ROUTED`/`SENT` with no terminal status after the analysis window closes) from terminal rate denominators.
- **Group by channel and direction.** Keep missing or unsupported dimensions in `unknown` buckets so totals reconcile instead of silently excluding them.
- **Stop SMS at `DELIVERED`.** Calculate `READ` engagement only for WhatsApp and RCS.
- **Separate channel fan-out.** `POST /v3/messages` with `"channel": ["sms","whatsapp","rcs"]` creates one message per channel; each has its own `message_id` and its own lifecycle. Don't double-count at the recipient level unless the user explicitly asks for recipient-level rollup.
- **Honor a minimum cohort size** before drawing conclusions about small rate shifts. A working heuristic is ≥1,000 messages per cohort; below that, noise dominates. This is an analyst rule of thumb, not a Sent API rule.

## Source notes

- Sent lifecycle, error-envelope, template, message-activity, and webhook claims were last checked on 2026-08-09 against the [Sent v3 OpenAPI](https://api.sent.dm/swagger/v3/swagger.json), [message status guide](https://docs.sent.dm/llms/start/guides/message-status-tracking.txt), and [webhook event reference](https://docs.sent.dm/llms/start/webhooks/event-types.txt).
- Provider-code tables are referential aids sourced from the linked provider documentation; they are not Sent-normalized enums. SMS carriers do not publish one shared reject enum.
- The 1,000-message cohort threshold is an analyst heuristic, not a documented Sent API requirement.
- Provider identifiers such as carrier message IDs, WhatsApp `wamid`, and RCS message IDs are not documented Sent v3 join keys. Use Sent `message_id` and treat provider IDs as escalation context.
