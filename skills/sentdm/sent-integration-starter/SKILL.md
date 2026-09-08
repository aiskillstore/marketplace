---
name: sent-integration-starter
description: Stands up a production-ready Sent v3 integration in an existing codebase — SDK selection and client construction, x-api-key configuration, idempotent sends, retry and rate-limit handling, the 46-code error catalog, sandbox verification, and a verified webhook receiver. Use when adding Sent to an app for the first time, choosing an SDK or framework wiring, handling 429 or 409 responses, deciding what to log, or hardening an integration before launch.
---

# Sent Integration Starter

Bring up a Sent integration in four stages: authenticate, send idempotently, receive verified events, then harden. Do not conflate them — most broken integrations pass stage one and skip stage three.

## Stage 1: client and credentials

Direct Sent v3 REST requests authenticate with the `x-api-key` header. An application proxy may accept `Authorization: Bearer` from its own callers, and the Sent MCP server uses client-managed OAuth, but neither changes the REST header sent to `api.sent.dm`. Organization keys may add `x-profile-id` to act for a child profile; a profile-scoped key that sends that header receives `403`.

| Language | Package | Client |
| --- | --- | --- |
| TypeScript | `@sentdm/sentdm` | `new SentDm()` |
| Python | `sentdm` (imports `sent_dm`) | `Sent()` or `AsyncSent()` |
| Go | `github.com/sentdm/sent-dm-go` | `sentdm.NewClient()` |
| Java | `dm.sent:sent-java` | `SentOkHttpClient.fromEnv()` |
| C# | `Sentdm` | `new SentClient()` |
| PHP | `sentdm/sent-dm-php` | `new SentDm\Client($apiKey)` |
| Ruby | `sentdm` | `Sentdm::Client.new` |

Every SDK except PHP reads `SENT_DM_API_KEY` automatically. Single-endpoint receiver samples read `SENT_DM_WEBHOOK_SECRET`; multi-tenant production receivers need a secret registry keyed by webhook id instead of one process-wide secret. Older documentation uses `SENT_API_KEY` and `SENT_WEBHOOK_SECRET` — treat those as aliases and standardize on the `SENT_DM_` names.

Choose the client lifecycle from the credential model. A single-account service with one server-managed key should reuse a long-lived client and its connection pool. A multi-tenant proxy that resolves a caller or profile credential per request should construct the client for that request and discard it, so tenant credentials cannot leak through shared state. Framework-specific wiring, the Ruby `messages.send_` naming quirk, and per-ecosystem background-work choices are in [references/sdk-and-frameworks.md](references/sdk-and-frameworks.md).

Validate configuration at boot and fail fast when the key is missing, rather than surfacing an auth error on the first customer send.

## Stage 2: idempotent sends

```json
{
  "to": ["+14155551234"],
  "template": {
    "name": "order_confirmation",
    "parameters": { "order_id": "12345" }
  },
  "sandbox": true
}
```

`to` is the only required field. Supply `template` or `text`, and omit `channel` to let automatic routing choose. Never write a `channel` array with several values expecting fallback — that broadcasts and multiplies charges. Channel decisions belong to `sent-routing-strategist`.

Send `Idempotency-Key` on every POST, PUT, and PATCH, derived deterministically from your own domain object (for example the order id plus the notification type) so a retry after a timeout cannot double-send. Keys are 1–255 characters of `[A-Za-z0-9_-]`, cached 24 hours per key per customer. A replay returns the cached body with `Idempotent-Replayed: true` and `X-Original-Request-Id`. A duplicate arriving while the original is still in flight waits up to five seconds and then fails `409 CONFLICT_001`; a `503 SERVICE_001` means the idempotency store was unavailable and the request was deliberately not executed.

`202` means accepted, not delivered. Persist the returned `message_id` values immediately with your own tenant, profile, and logical send identifiers. Webhook events carry the Sent message id and account data, but never your application's tenant identifier.

## Stage 3: verified webhook receiver

An integration without a receiver has no delivery truth. Register an endpoint, then verify every delivery: HMAC-SHA256 over `{x-webhook-id}.{x-webhook-timestamp}.{raw_body}`, keyed on the base64-decoded secret after stripping `whsec_`, compared in constant time, rejecting timestamps outside 300 seconds. No SDK ships a verifier in any language.

Acknowledge with `200` before doing work, and deduplicate on `{message_id}:{message_status}` for outbound events and `message_id` for inbound. Ten consecutive failed deliveries disable the endpoint. Full mechanics belong to `sent-webhook-engineer`; treat a verified, fast-acknowledging, deduplicating receiver as a launch requirement here.

## Stage 4: harden

### Retry policy by response class

| Response | Retry | How |
| --- | --- | --- |
| `2xx` | No | Success |
| `400`, `422` `VALIDATION_*` | No | Fix the request |
| `401`, `403` `AUTH_*` | No | Stop immediately; ten consecutive auth failures lock the credential with escalating lockouts |
| `404` `RESOURCE_*` | No | The referenced object does not exist |
| `409 CONFLICT_001` | Yes, once, after a pause | A concurrent duplicate is in flight |
| `429` | Yes | Honor `Retry-After`; jittered backoff |
| `5xx`, `503 SERVICE_001` | Yes | Exponential backoff with jitter and a ceiling |
| Timeout with no response | Retry safely only with evidence | Reuse the same `Idempotency-Key`; without one, there is no reliable API lookup by key or recipient, so do not automate a resend |

The standard limit is 200 requests per minute on a sliding window. `POST /v3/webhooks/{id}/rotate-secret` and `POST /v3/webhooks/{id}/test` are limited to 10 per minute. Rate-limit headers appear **only** on `429` responses, so pacing must be designed rather than measured — batch up to 1,000 recipients per request and pace at roughly one request per second for bulk work.

### Error handling

Errors arrive as `{success, data, error: {code, message, details, doc_url}, meta: {request_id, timestamp, version}}`. Branch on the `error.code` prefix family (`AUTH_`, `VALIDATION_`, `RESOURCE_`, `BUSINESS_`, `CONFLICT_`, `SERVICE_`, `INTERNAL_`) rather than on message text or on individual codes. The full 46-code catalog with retry classification is in [references/errors-and-limits.md](references/errors-and-limits.md).

Two codes are counterintuitive: `BUSINESS_003` and `BUSINESS_004` are documented as request-level errors, but on `POST /v3/messages` the request is accepted with `202` and the affected messages finalize as `BLOCKED` and `FILTERED`. Insufficient balance therefore does not fail the send call.

### Observability

Log `meta.request_id` on every response, success or failure — it is the correlation handle for support. Record the mapping from your logical send to the returned `message_id` values, and keep an append-only event history so a reroute's sequence remains auditable. Never log the API key, the webhook signing secret, `payment_details`, or raw recipient message content beyond your retention policy.

### Launch checklist

- [ ] Credentials load from the environment; nothing is committed, and separate keys exist per environment.
- [ ] Client lifecycle matches credential scope: shared for one server-managed key, per request for tenant-supplied credentials.
- [ ] `Idempotency-Key` on every mutating call, derived deterministically.
- [ ] Retry policy distinguishes retryable from terminal by error family.
- [ ] Bulk paths pace against 200 requests per minute and batch to at most 1,000 recipients.
- [ ] Webhook receiver verifies signature and timestamp, returns `200` fast, and dedupes.
- [ ] Receiver returns non-2xx on genuine failure so Sent retries.
- [ ] `message_id` to tenant mapping is persisted before sending.
- [ ] `request_id` is logged; secrets and card data are not.
- [ ] Sandbox smoke test passes, then a real send reaches `DELIVERED`.
- [ ] Alerting covers webhook `consecutive_failures`, `429` volume, and filtered or blocked rates.

## Verification

Run the local preflight, which needs no credentials and no network:

```bash
python3 scripts/preflight.py --self-test
```

Then verify a real path with `"sandbox": true`, which authenticates and validates without executing, and finally with one live send confirmed to `DELIVERED` through the receiver.

## Boundaries

Use `sent-webhook-engineer` for receiver depth, `sent-routing-strategist` for channel choice, `sent-messaging` for a confirmed one-off send, `sent-two-way-messaging` for inbound and consent, `sent-profile-provisioning` for multi-tenant provisioning, and `migrate-to-sent` when replacing another CPaaS provider.
