---
name: migrate-to-sent
description: Plans and executes a migration from Twilio, Sinch, Infobip, Vonage, or MessageBird/Bird to Sent v3 — mapping send calls, status vocabularies, webhook signature schemes, opt-out stores, templates, and tenancy models, then cutting over safely with dual-run and rollback. Use when replacing an incumbent CPaaS provider, translating provider code or webhook handlers to Sent, or planning a phased cutover and its verification gates.
---

# Migrate to Sent

Every migration from a major CPaaS provider hits the same five translation problems. Work them in this order, because the first one silently doubles cost and is invisible in tests.

## 1. Ordered fallback becomes automatic routing

Incumbent platforms express cross-channel delivery through different caller-side arrays, failover objects, messaging-service features, or application-level priority configuration. Do not assume those shapes have a direct Sent request-field equivalent.

**Sent's `channel` array is a broadcast list.** Porting an ordered array produces one message and one charge per recipient-channel pair, which passes tests and multiplies production spend. The correct translation is automatic routing — omit `channel` or send `["sent"]` — which lets the platform select a route and reroute across up to three channel-and-provider pairs on the same `message_id`. Details belong to `sent-routing-strategist`; the migration rule is simply: **never port an ordered channel list.**

## 2. Status vocabularies do not line up

Incumbent statuses map onto Sent's, but Sent adds two states that have no equivalent and that break naive retry logic.

| Sent status | Closest incumbent analogue | Migration note |
| --- | --- | --- |
| `QUEUED` | Twilio `queued`, Sinch `QUEUED_ON_CHANNEL` | Accepted, not sent |
| `ROUTED` | no analogue | Route chosen; fires again on reroute |
| `SENT` | Twilio `sent`, Sinch `MESSAGE_SUBMIT` | Provider handoff only |
| `DELIVERED` | `delivered` everywhere | The first proof of handset receipt |
| `READ` | Twilio `read`, Sinch `READ` | WhatsApp and RCS only |
| `FAILED` | `failed`, `undelivered` | May still reroute; not necessarily final |
| `FILTERED` | Twilio error 21610 (opt-out) | **Policy gate. Never retry** |
| `BLOCKED` | account-level errors | **Account precondition.** Fix the account, then resend |
| `SCHEDULED` | no analogue | Quiet-hours parking; resumes automatically |

Two consequences for ported code. Handlers that treat every non-delivered terminal state as retryable will retry consent blocks, which is a compliance failure rather than a bug. And handlers keyed on numeric provider error codes — Twilio's `21610` is the classic — must be rewritten against Sent's string `error.code` families.

## 3. Webhook verification is a rewrite, not a port

No two providers sign the same way, and no Sent SDK ships a verifier.

| Provider | Scheme |
| --- | --- |
| Twilio | `X-Twilio-Signature`, base64 HMAC-**SHA1** over the full URL plus sorted POST parameters |
| Sinch | HMAC-SHA256 over `body.nonce.timestamp`, four `x-sinch-webhook-signature*` headers, or OAuth 2.0 |
| Infobip | Basic, HMAC-SHA256 over the raw body, or OAuth on a notification profile; **the header name is account-configured** |
| Vonage | JWT in `Authorization: Bearer`, or a legacy `sig` parameter |
| MessageBird/Bird | `messagebird-signature`, base64 HMAC-SHA256 over timestamp, URL, and a SHA-256 body hash |
| **Sent** | `x-webhook-signature: v1,{base64}`, HMAC-SHA256 over `{x-webhook-id}.{x-webhook-timestamp}.{raw_body}` |

Sent's key is the signing secret with `whsec_` stripped and the remainder base64-decoded, compared in constant time, with timestamps outside 300 seconds rejected. Because Sent provides no per-event id, dedupe keys must be derived from payload semantics. Build the receiver with `sent-webhook-engineer` rather than adapting the incumbent's verifier.

## 4. Opt-out stores must be reconciled, not migrated by copy

Every provider keeps its own suppression list — Twilio Advanced Opt-Out, Infobip Blocklist, Sinch OPT_IN/OPT_OUT events. Sent enforces consent at the platform level before events reach the application, stores it as `opt_out` on the contact, and applies it **channel-agnostically**: a `STOP` on SMS suppresses WhatsApp and RCS too.

Reconciliation rules: export the incumbent's suppression list before cutover, treat any opt-out on any incumbent channel as a global Sent opt-out, and never clear `opt_out` to "clean up" migrated data. Sent's ten default keywords are `STOP`, `CANCEL`, `UNSUBSCRIBE`, `QUIT`, `END`, `START`, `UNSTOP`, `SUBSCRIBE`, `HELP`, `INFO`, matched only when the entire trimmed body equals the keyword — so incumbent-specific keywords need custom keyword entries. Rewrite any incumbent keyword matcher as an exact local consent mirror and audit mechanism; the matcher must not write consent to Sent again. Consent semantics belong to `sent-two-way-messaging`.

## 5. Templates and tenancy are re-registered, not transferred

WhatsApp templates live with the WABA, so the migration question is whether the WABA moves. Positional placeholders (`{{1}}`, `{{2}}`) become **named** parameters in Sent, which means every call site that passed an ordered array must pass a named map. Approval is asynchronous and arrives as a `templates` webhook event, so build the template inventory before cutover rather than during it.

Tenancy maps as follows, with the boundary decision owned by `sender-profile-architect` and the API work by `sent-profile-provisioning`:

| Incumbent construct | Sent equivalent |
| --- | --- |
| Twilio subaccount | Sender Profile |
| Twilio Messaging Service | routing plus profile configuration, not a caller-side pool |
| Infobip Application or Entity | Sender Profile |
| Sinch Conversation API app | Sender Profile |
| Provider API credential per tenant | Profile-scoped API key, or organization key with `x-profile-id` |

## Migration sequence

1. **Inventory** every send call site, webhook handler, status branch, template, suppression list, and credential. Use `scripts/inventory_scan.py` to find them mechanically.
2. **Map** each item using [references/provider-mapping.md](references/provider-mapping.md), flagging ordered-fallback arrays and numeric error codes as required rewrites.
3. **Stand up Sent in parallel**: credentials, one webhook per environment, verified receiver, templates re-registered and approved.
4. **Prove equivalence in sandbox** with `"sandbox": true`, then with a small live cohort confirmed to `DELIVERED`.
5. **Dual-run** with a traffic split, comparing delivery rates, latency, and cost per message on the same message classes.
6. **Cut over** by message class — lowest-risk transactional first, marketing last — keeping the incumbent receiver live.
7. **Decommission** only after a full billing cycle of clean data, then revoke incumbent credentials.

Sequencing detail, verification gates, and rollback triggers are in [references/cutover-playbook.md](references/cutover-playbook.md).

## Mistakes that survive testing

- Porting an ordered channel array. Doubles cost, never errors.
- Treating `FILTERED` as retryable. Compliance exposure.
- Reusing the incumbent's signature verifier. Every delivery returns 401.
- Assuming `202` means delivered. Sent acknowledges acceptance only.
- Keeping positional template placeholders. Parameters silently mismatch.
- Retrying on `401`. Ten consecutive auth failures lock the credential with escalating lockout.
- Omitting `Idempotency-Key` during dual-run. A timeout retry sends twice.
- Sending `x-profile-id` with a profile-scoped key. Returns `403`.
- Copying an incumbent's `Authorization: Bearer` pattern. Sent authenticates with `x-api-key`.

## Boundaries

This skill owns provider mapping and line-by-line migration planning. Hand the resulting Sent client and resilience work to `sent-integration-starter`, channel semantics to `sent-routing-strategist`, receiver construction to `sent-webhook-engineer`, WhatsApp onboarding to `waba-embedded-signup`, and US campaign registration to `sms-10dlc-registration`.
