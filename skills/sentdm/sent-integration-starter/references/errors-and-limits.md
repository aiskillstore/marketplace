# Error catalog, retries, idempotency, and rate limits

## Table of contents

- [Response envelope](#response-envelope)
- [Retry classification by family](#retry-classification-by-family)
- [AUTH codes](#auth-codes)
- [VALIDATION codes](#validation-codes)
- [RESOURCE codes](#resource-codes)
- [BUSINESS codes](#business-codes)
- [CONFLICT, SERVICE, and INTERNAL codes](#conflict-service-and-internal-codes)
- [Codes that behave differently on send](#codes-that-behave-differently-on-send)
- [Idempotency semantics](#idempotency-semantics)
- [Rate limits and pacing](#rate-limits-and-pacing)
- [Sandbox semantics](#sandbox-semantics)
- [Ambiguous send recovery](#ambiguous-send-recovery)

## Response envelope

Every response uses one shape:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_004",
    "message": "Request validation failed",
    "details": { "to": ["'to' must contain at least one recipient"] },
    "doc_url": "https://docs.sent.dm/reference/api/error-catalog"
  },
  "meta": {
    "request_id": "req_7X9zKp2jDw",
    "timestamp": "2026-03-14T09:21:44Z",
    "version": "v3"
  }
}
```

Branch on `error.code`, never on `error.message`. Read `error.details` for field-level validation feedback and log `meta.request_id` on every response so support can correlate.

## Retry classification by family

| Family | Count | Default handling |
| --- | --- | --- |
| `AUTH_` | 6 | Terminal. Stop immediately; do not loop |
| `VALIDATION_` | 8 | Terminal. Fix the request |
| `RESOURCE_` | 14 | Terminal; reconcile `RESOURCE_007` with the existing resource |
| `BUSINESS_` | 11 | Mostly terminal; `BUSINESS_002` backs off |
| `CONFLICT_` | 1 | Retry once after a short pause |
| `SERVICE_` | 1 | Retry with backoff |
| `INTERNAL_` | 5 | Retry with backoff |

The catalog contains 46 codes in total. Authentication failures deserve special care: ten consecutive failures lock the presented credential with a `429` and escalating lockout windows from one to sixty minutes, so a retry loop against a bad key extends its own outage. Stop and alert instead.

## AUTH codes

| Code | HTTP | Title | Retry |
| --- | --- | --- | --- |
| `AUTH_001` | 401 | User is not authenticated | never |
| `AUTH_002` | 401 | Invalid or missing API key | never |
| `AUTH_004` | 403 | Insufficient permissions | never |
| `AUTH_005` | 403 | Account not yet activated | never |
| `AUTH_006` | 403 | KYC verification not complete | never |
| `AUTH_007` | 403 | Channel setup not complete | never |

`AUTH_004` is also what a profile-scoped key receives when it sends `x-profile-id`. `AUTH_005`, `AUTH_006`, and `AUTH_007` are onboarding states rather than credential problems, so surface them to an operator instead of retrying.

## VALIDATION codes

| Code | HTTP | Title | Retry |
| --- | --- | --- | --- |
| `VALIDATION_001` | 400 | Request validation failed | never |
| `VALIDATION_002` | 400 | Invalid phone number format | never |
| `VALIDATION_003` | 400 | Invalid GUID format | never |
| `VALIDATION_004` | 400 | Required field is missing | never |
| `VALIDATION_005` | 400 | Field value out of valid range | never |
| `VALIDATION_006` | 400 | Invalid enum value | never |
| `VALIDATION_007` | 400 | Invalid Idempotency-Key format | never |
| `VALIDATION_008` | 400 | Invalid template variable value | never |

`VALIDATION_002` is prevented by normalizing recipients to E.164 before the call. `VALIDATION_006` is what an unsupported `channel` value returns. `VALIDATION_008` covers several distinct template-variable problems, so read the message rather than assuming one cause.

## RESOURCE codes

| Code | HTTP | Title | Retry |
| --- | --- | --- | --- |
| `RESOURCE_001` | 404 | Contact not found | never |
| `RESOURCE_002` | 404 | Template not found | never |
| `RESOURCE_003` | 404 | Message not found | never |
| `RESOURCE_004` | 404 | Customer not found | never |
| `RESOURCE_005` | 404 | Organization not found | never |
| `RESOURCE_006` | 404 | User not found | never |
| `RESOURCE_007` | 409 | Resource already exists | do not retry blindly |
| `RESOURCE_008` | 404 | Webhook not found | never |
| `RESOURCE_009` | 404 | Brand not found | never |
| `RESOURCE_010` | 404 | Campaign not found | never |
| `RESOURCE_011` | 404 | Batch not found | never |
| `RESOURCE_012` | 404 | Phone number not found | never |
| `RESOURCE_013` | 404 | Resource not found | never |
| `RESOURCE_014` | 404 | Profile not found | never |

`RESOURCE_014` also occurs when an organization passes its own identifier as a `profileId`, which must be a child profile. `RESOURCE_007` is the duplicate-creation signal, most visibly when inviting a user who already has access; read the existing resource and decide whether the requested state is already satisfied.

## BUSINESS codes

| Code | HTTP | Title | Retry |
| --- | --- | --- | --- |
| `BUSINESS_001` | 400 | Cannot modify inherited contact | never |
| `BUSINESS_002` | 429 | Rate limit exceeded | backoff |
| `BUSINESS_003` | 402 | Insufficient account balance | never |
| `BUSINESS_004` | 400 | Contact has opted out | never |
| `BUSINESS_005` | 400 | Template not approved | never |
| `BUSINESS_006` | 400 | Message cannot be modified in current state | never |
| `BUSINESS_007` | 400 | Channel not available | never |
| `BUSINESS_008` | 400 | Operation would exceed quota | never |
| `BUSINESS_010` | 400 | Webhook is inactive | never |
| `BUSINESS_012` | 400 | Template is not active on the requested channel | never |
| `BUSINESS_014` | 403 | Account is suspended | never |

`BUSINESS_001` is the inheritance boundary: a profile that inherits contacts cannot modify them. `BUSINESS_010` explains why a test delivery to a disabled webhook fails; re-enable it with `PATCH /v3/webhooks/{id}/toggle-status` or from the dashboard after fixing the receiver.

## CONFLICT, SERVICE, and INTERNAL codes

| Code | HTTP | Title | Retry |
| --- | --- | --- | --- |
| `CONFLICT_001` | 409 | Concurrent idempotent request | after delay |
| `SERVICE_001` | 503 | Cache service temporarily unavailable | backoff |
| `INTERNAL_001` | 500 | Unexpected internal server error | backoff |
| `INTERNAL_002` | 500 | Database operation failed | backoff |
| `INTERNAL_003` | 500 | External service error | backoff |
| `INTERNAL_004` | 504 | Timeout waiting for operation | backoff |
| `INTERNAL_005` | 503 | Service temporarily unavailable | backoff |

`SERVICE_001` is a deliberate safety response: the idempotency cache was unavailable, so the API refused to execute rather than risk a duplicate. Retrying the same request with the same key is correct.

## Codes that behave differently on send

Two documented request-level codes do not reject `POST /v3/messages`. Insufficient balance (`BUSINESS_003`, 402) and an opted-out contact (`BUSINESS_004`, 400) are catalogued as errors, but on send the request is accepted with `202` and the affected messages finalize as `BLOCKED` and `FILTERED` respectively. Client code that only inspects HTTP status will believe those sends succeeded.

The operational consequence is that balance and consent problems appear in delivery data rather than in error handling. Monitor blocked and filtered rates as first-class metrics alongside `4xx` and `5xx` counts.

Sent also records internal reason codes on a message for consent blocks, route denials, no-route-matched, and invalid template parameters. These are never returned in API responses or webhook payloads, so diagnosis uses the terminal status plus the channel value plus `GET /v3/messages/{id}/activities`.

## Idempotency semantics

`Idempotency-Key` applies to POST, PUT, and PATCH on `/v3/*` and is ignored on GET and DELETE. Values are 1 to 255 characters of `[A-Za-z0-9_-]`.

| Situation | Behavior |
| --- | --- |
| First successful request | Response cached for 24 hours per key per customer |
| Replay of a cached key | Cached body returned with `Idempotent-Replayed: true` and `X-Original-Request-Id` |
| Response larger than 5 MB | Not cached; a duplicate re-executes |
| Duplicate arrives while the original is in flight | Waits up to five seconds, then fails `409 CONFLICT_001` |
| Idempotency cache unavailable | `503 SERVICE_001`; the request was not executed |

Derive keys deterministically from your own domain objects — an order id plus a notification type, for example — rather than generating a random value per attempt, so that a retry after a network timeout collides with the original instead of creating a second send. Because caching is per customer, the same key used by two different customers is two independent operations.

## Rate limits and pacing

| Tier | Limit | Window | Applies to |
| --- | --- | --- | --- |
| Standard | 200 requests/minute | Sliding 60 seconds | Everything not listed below |
| Sensitive | 10 requests/minute | Fixed window | `POST /v3/webhooks/{id}/rotate-secret`, `POST /v3/webhooks/{id}/test` |

`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After` are present **only** on `429` responses. There is no way to read remaining quota preemptively, so pacing must be a design decision rather than an adaptive reaction.

For bulk work, batch up to 1,000 recipients per `POST /v3/messages` and pace at roughly one request per second, which keeps a large campaign inside the standard budget while leaving headroom for transactional traffic. Note that batching multiplies with channels: 1,000 recipients on two channels is 2,000 messages and 2,000 charges from a single request.

Rate-limit exposure follows the credential. A profile-scoped key has its own pool; an organization key acting through `x-profile-id` draws on the organization pool shared by every profile.

## Sandbox semantics

`"sandbox": true` runs authentication and validation and then stops. Nothing is persisted, queued, dispatched to a provider, or charged, and resource lookups do not occur — so a sandbox request will not tell you whether a template id exists. Malformed requests still return real `400` and `422` responses, which is what makes sandbox valuable in continuous integration.

The exception worth memorizing: `DELETE /v3/webhooks/{id}` ignores the flag and always deletes. Never use sandbox as a general dry-run guard for destructive calls.

## Ambiguous send recovery

When a send times out or the connection drops before a response arrives, the request may or may not have been accepted. Never blind-retry.

1. If the original carried an `Idempotency-Key`, retry with the **same** key. A cached success returns the original response with `Idempotent-Replayed: true`; a `409 CONFLICT_001` means the original is still in flight, so pause and retry once.
2. If no key was sent, search your own request and response records for a returned `message_id`. Sent exposes no reliable lookup by idempotency key or recipient that can prove an ambiguous request did not execute.
3. Escalate ambiguous no-key cases for an explicit duplicate-risk decision. Only send again when your application has sufficient evidence that nothing was accepted, and attach an idempotency key this time.

The same discipline applies to profile provisioning: a deterministic key derived from your provisioning record prevents a timeout from creating a second profile.
