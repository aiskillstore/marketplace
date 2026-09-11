---
name: messaging-performance-analyzer
description: Analyzes Sent message delivery, webhook, and activity data to explain funnel drop-offs, delivery failures, read-rate gaps, channel fallback, and suspicious performance changes. Use when a user says MDR, delivery report, message activity, webhook event, failed messages, low delivery rate, RCS fallback, WhatsApp read rate, SMS filtering, campaign performance, or asks why messages did not arrive.
---

<!--
- "MDR" is the human term for the Sent activities surface: GET /v3/messages/{id}/activities. There is no separate MDR endpoint.
- Lifecycle: QUEUED -> ROUTED -> SENT -> DELIVERED -> READ (WhatsApp/RCS only), with FAILED at any stage and RECEIVED for inbound.
- Sent exposes its own normalized error codes (AUTH_*, VALIDATION_*, RESOURCE_*, BUSINESS_*, CONFLICT_001, SERVICE_001, INTERNAL_*) on the HTTP envelope, plus send-time per-message codes (ERR_CONSENT_BLOCKED, ERR_ROUTE_DENIED, ERR_TEMPLATE_PARAMS_INVALID) on the message `description` field. See references/mdr-status-codes.md.
-->

# Messaging performance analyzer

## Overview

Use this skill to turn raw Sent message evidence into a concise diagnosis of what changed, where the funnel leaks, and what to fix first. Anchor every analysis to **Sent message IDs**, **message status**, **message activities**, and **webhook events** before interpreting carrier, WhatsApp, or RCS provider codes.

Sent’s v3 send endpoint accepts a template-based request and returns per-recipient `message_id` values for asynchronous tracking. Status is retrieved with `GET /v3/messages/{id}`, and detailed lifecycle evidence is retrieved with `GET /v3/messages/{id}/activities`. Webhook endpoints support event ingestion, event-type discovery, event history, test delivery, and secret rotation.

## When to use

Use this skill when the user asks why messages failed, why delivery or read rate dropped, whether fallback is working, whether a provider is filtering traffic, or how a campaign performed. Trigger on words such as “MDR,” “delivery report,” “webhook event,” “activities,” “status,” “failed,” “undelivered,” “read rate,” “fallback,” “filtering,” “throttling,” or “carrier reject.”

Do not use this skill to register 10DLC, design a Sender Profile, onboard RCS, or author WhatsApp templates. Hand those workflows to the related skills after the performance symptom is isolated.

## Evidence hierarchy

Start with Sent-owned evidence, then enrich it with provider context. This prevents overfitting to a carrier code that may be missing, stale, or normalized differently across channels.

| Evidence | Sent-verified path | Use it for |
|---|---|---|
| Send response | `POST /v3/messages` | Identify request ID, accepted recipients, channel fan-out, and Sent `message_id` values. |
| Current status | `GET /v3/messages/{id}` | Confirm the latest known lifecycle status and any error details exposed by the API. |
| Activity timeline | `GET /v3/messages/{id}/activities` | Reconstruct acceptance, routing, sending, delivery, read, and error transitions. |
| Webhook configuration | `GET /v3/webhooks`, `GET /v3/webhooks/event-types` | Confirm whether the customer subscribed to the events needed for analysis. |
| Webhook event history | `GET /v3/webhooks/{id}/events` | Compare delivered events against API status and customer ingestion logs. |
| Webhook connectivity | `POST /v3/webhooks/{id}/test` | Verify endpoint reachability before blaming delivery infrastructure. |

## Process

### 1. Pin the question before slicing the funnel

Restate the user’s exact question as a measurable comparison. “WhatsApp is bad” becomes “Did WhatsApp `DELIVERED` rate fall for order templates sent from profile A between Monday and Wednesday?” A precise question keeps the cohort stable and prevents mixed-channel averages from hiding the failure mode.

Capture these dimensions before calculating anything: profile or sender identity, template ID/name, channel, country, send window, recipient segment, and whether fallback or multi-channel broadcast was requested.

**Example.** If a user says “RCS fallback stopped working,” define the cohort as sends that omitted `channel` or used `channel: ["sent"]`, then compare the selected `payload.channel` and message activities. Analyze any explicit multi-channel arrays separately as broadcasts.

### 2. Build cohorts from Sent message IDs

Use Sent `message_id` as the primary unit. A v3 send can create separate messages for each recipient and channel pair when multiple channels are specified. Count each Sent message once in a terminal-outcome rollup, then add recipient-level or campaign-level rollups only after deduplication.

Distinguish an activity history from a latest-status snapshot. A history can prove the transitions it contains. A snapshot such as `status=DELIVERED` proves only the observed current outcome; it does not prove that the export also observed `QUEUED`, `ROUTED`, or `SENT`. Report unavailable transition denominators as `N/A`, not zero, and never synthesize missing transitions.

Do not use provider IDs such as WhatsApp `wamid`, SMS carrier IDs, or RCS message IDs as the primary join key unless the exported evidence lacks Sent IDs. Provider IDs are useful for escalation, but the Sent API and dashboard track status by Sent message ID.

### 3. Normalize lifecycle stages to Sent’s documented statuses

Use Sent’s documented delivery lifecycle as the first-pass funnel: `QUEUED`, `ROUTED`, `SENT`, and `DELIVERED`. Treat `READ` as a separate engagement measure for WhatsApp and RCS, never as an SMS delivery requirement. Keep terminal failures, deferred/in-flight messages, inbound `RECEIVED` messages, and malformed/unknown records in separate buckets using only fields present in the evidence.

| Stage | Interpretation | Common diagnostic question |
|---|---|---|
| `QUEUED` | Sent accepted the request for processing. | Is the backlog growing or did the request never route? |
| `ROUTED` | Sent selected a channel/provider path. | Did routing choose the expected channel or fallback path? |
| `SENT` | The message left Sent/provider processing toward the destination network. | Are provider accepts high but downstream delivery low? |
| `DELIVERED` | Delivery was confirmed where supported. | Did the destination network confirm receipt? |
| `READ` | WhatsApp/RCS engagement receipt was observed where available. | Did users open the message after delivery? |
| Error/failure | A terminal or recoverable error occurred. | Is the root cause compliance, payload, throughput, opt-out, or provider outage? |

### 4. Check webhook health before diagnosing delivery

A drop in dashboard activity or customer-side events can be a webhook ingestion problem, not a delivery problem. Confirm webhook existence, active status, event subscriptions, recent event history, and test delivery. Rotate secrets only when the user explicitly asks or when a credential compromise is suspected, because rotation immediately invalidates the old secret.

**Example.** If Sent status shows `DELIVERED` but the customer database shows “no delivery callbacks,” inspect `/v3/webhooks/{id}/events` and the customer’s endpoint logs. If Sent has events but the endpoint returned failures, the fix is webhook handling, not campaign routing.

### 5. Split by channel before naming a root cause

SMS, WhatsApp, and RCS fail differently. Do not average them together unless the user explicitly asked for a blended KPI. Compare each channel’s funnel and then compare the aggregate.

| Channel | First cuts | Typical next evidence |
|---|---|---|
| SMS | Country, sender/profile, 10DLC campaign, opt-out, carrier family | Compliance status, brand/campaign readiness, opt-out logs, throughput patterns. |
| WhatsApp | Template, language, category, recipient country, quality/tier symptoms | Template status, read receipts, conversation window, Meta-side errors if present. |
| RCS | Agent readiness, automatic routing, pinned-channel failures, text/suggestion-chip rendering | Sent RCS setup status, selected route, and exact activity/error details. |

### 6. Quantify impact before recommending fixes

Report raw counts and rates together. A 40% failure rate over 15 messages is a different decision than a 4% failure rate over 150,000 messages. Reconcile the global totals with every channel × direction group, retaining explicit `unknown` groups instead of silently dropping incomplete dimensions. Include exclusions such as pending messages, test traffic, sandbox sends, retries, and duplicate channel fan-out.

A practical analysis table should include: sent count, latest status distribution, failure count, failure-rate delta versus baseline, top exact error strings/codes, first observed timestamp, affected templates, affected countries, and affected profiles.

### 7. Convert the diagnosis into the next action

End with one primary diagnosis, one confidence level, and the next verification step. Avoid long lists of generic fixes. Tie every recommendation to observed evidence.

**Example.** “The largest leak is after `ROUTED` for SMS traffic on profile `support-us`, starting at 14:10 UTC. WhatsApp and RCS cohorts are stable. The affected traffic uses the same order-update template and a US A2P route. Verify the Sent brand/campaign status and opt-out handling next; if compliant, escalate the exact message IDs and activity timestamps.”

## Common rationalizations to avoid

Do not infer delivery failure from missing customer-side webhooks until Sent webhook event history and endpoint responses are checked. Webhook ingestion failures often mimic delivery failures.

Do not label a campaign “carrier filtered” from a small sample without comparing baseline, country, sender/profile, and template. Filtering is a conclusion after cohort isolation, not a synonym for “failed.”

Do not treat `READ` as a universal stage. Sent documents read receipts for WhatsApp and RCS; SMS generally does not support read receipts.

Do not mistake broadcast for fallback. Omitted `channel` or `["sent"]` enables automatic routing; one explicit channel pins delivery; multiple explicit values create separate messages. Count every returned `message_id` once and report the selected channel.

## Verification checklist

- [ ] The analysis uses Sent `message_id` values as the primary unit.
- [ ] The cohort is pinned by time window, profile/sender identity, template, channel, and recipient segment.
- [ ] Status math uses the latest known status per Sent message ID.
- [ ] Transition math uses observed activity histories and never backfills stages from a latest-only status.
- [ ] Pending or in-flight messages are either excluded or reported separately.
- [ ] SMS delivery analysis stops at `DELIVERED`; WhatsApp/RCS `READ` is labeled engagement.
- [ ] Global and channel × direction totals reconcile, including malformed and explicit `unknown` buckets.
- [ ] Webhook configuration, event history, and endpoint test results are checked when the symptom is missing callbacks.
- [ ] Channel-specific failures are split before aggregate rates are reported.
- [ ] Provider or carrier codes are quoted exactly as observed and not invented from a lookup table.
- [ ] The final recommendation names one next verification step and the evidence that justifies it.

## Related skills

Use `sms-10dlc-registration` when the leak points to US A2P SMS compliance, brand registration, campaign registration, or opt-in/opt-out evidence.

Use `rcs-agent-onboarding` when the symptom points to RCS agent approval, launch readiness, capability gaps, or fallback design rather than live delivery analytics.

Use `sender-profile-architect` when the issue is tenant/profile isolation, webhook routing, credential scoping, or multi-brand sender design.

Use `waba-template-author` or `template-builder-ui` when the root cause is WhatsApp template category, review status, template payload structure, or authoring workflow.

Use the `sent` skill for shared Sent terminology and routing.

## Bundled references and scripts

| File | Type | Purpose |
|---|---|---|
| `references/mdr-status-codes.md` | Lookup table | Normalize observed SMS, WhatsApp, and RCS provider errors without putting long code dictionaries in the skill body. |
| `references/performance-diagnosis-playbook.md` | Worked examples | Decision tree for which signal to investigate first, channel-specific diagnostic patterns, cross-skill handoff matrix, and escalation criteria. |
| `scripts/analyze_mdr_funnel.py` | Validation script | Reads an MDR export (CSV or JSON), groups channel × direction outcomes, separates delivery transitions from engagement, and retains malformed/unknown rows. Run from the skill root: `python scripts/analyze_mdr_funnel.py path/to/mdr.csv` (use `--threshold N`, `--show-errors`, or `--format json`). Exit `0` means no observed transition breach, `2` means bad input/no usable cohort, and `3` means an observed breach. JSON uses `null` where a denominator is unavailable; text uses `N/A`. |
| `scripts/fixtures/good.json` | Fixture | Synthetic healthy-funnel MDR export. |
| `scripts/fixtures/bad.json` | Fixture | Synthetic MDR export with deliberate >50% SENT→DELIVERED drop. |
