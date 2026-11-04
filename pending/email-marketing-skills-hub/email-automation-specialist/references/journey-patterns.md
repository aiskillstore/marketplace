# Journey design and orchestration

Treat these as starting hypotheses. Timing and message counts depend on buying cycle, audience expectations, jurisdiction, capacity, and prior results; there is no universal winning cadence.

## Useful lifecycle patterns

- **Welcome:** entry after appropriate subscription/confirmation; fulfill the promised resource or benefit, orient the subscriber, then offer one relevant next action. Stop or branch when the goal is achieved. Submission of a support form is not newsletter consent.
- **SaaS onboarding:** entry from a verified account event; branch by observed activation steps, not guessed intent. Teach the next unfinished task; stop redundant reminders after completion. Do not mix promotional upsells into essential security or account-service mail without reassessing classification.
- **Lead nurture:** align educational content to an expressed need; stop or route after a reply, booked meeting, disqualification, or active sales handoff. Define ownership so automated messages do not contradict a person handling the relationship.
- **Cart or checkout recovery:** verify event identity, item availability, permission, and purchase status immediately before sending. Distinguish browsing from checkout intent. Exclude completed/cancelled orders and do not promise stock, prices, or discounts that were not verified.
- **Post-purchase:** distinguish receipts and delivery notices from promotional cross-sells. Branch for cancellation, refund, service issue, or fulfillment delay; avoid asking for a review before product delivery or resolved support.
- **Retention/replenishment:** choose intervals from real product use or contract dates; stop when reordered or opted out. Do not infer health or other sensitive circumstances from product behavior for personalization.
- **Reactivation:** use a documented eligible audience and meaningful inactivity signals. Keep a bounded sequence and sunset policy. A past purchase, stale import, or lack of an unsubscribe is not automatically sufficient permission.
- **Renewal/expiry:** use the system of record for dates and account state. Exit immediately after renewal; separate required notices from optional promotions and avoid false urgency.

## Event contract

For each event specify: canonical name/version, source of truth, stable event ID, user/account identity, occurred-at and received-at timestamps, timezone, required attributes, consent reference, retention needs, and schema-validation behavior. Quarantine missing or invalid required fields rather than guessing.

Document delayed and replayed events. State whether entry is once per person, once per order, once per lifecycle stage, or repeatable after a cooldown. Re-entry must not restart an already-completed welcome series after an innocuous profile update.

## State and ordering

Use a durable idempotency key scoped to recipient, journey version, step and qualifying event. Enforce it atomically in a real implementation; an in-memory check is insufficient under concurrent workers. Record pending, accepted, confirmed-failed, and unknown states. Provider acceptance is not delivery.

Event-ID deduplication alone cannot catch two integrations assigning different IDs to the same business transition. Define an additional semantic identity where the domain supports it, such as account + subscription + renewal cycle, order + event type + state version, or person + first confirmed subscription. Preserve legitimate repeated actions; do not collapse every event from the same contact. Use the authoritative transition/version and a durable atomic uniqueness rule, and test both duplicate IDs and different IDs describing the same transition.

Evaluate current suppression and completion state just before enqueue and again as close to send time as the provider permits. Handle unsubscribe/cancellation race conditions and document unavoidable queue latency. A source-of-truth opt-out must not be overwritten by a stale subscribe event.

Handle identity merges without joining different people by guesswork. Preserve restrictive consent and suppression until ownership and scope are resolved; deduplicate contacts using verified platform identity rules, not arbitrary email normalization that can merge distinct addresses.

Set global and journey-level caps, priority, quiet hours, local timezone fallback, and maximum event age. For example, when welcome education overlaps a time-sensitive renewal notice, give a required renewal/service notice its separate approved operational path; defer optional welcome marketing under the shared marketing cap. If both messages are promotional, propose renewal relevance as the higher priority and reschedule or skip the welcome step within its expiry window. Confirm that priority with the owner rather than treating it as universal, and never use a service label to evade marketing suppression.

Specify whether delays run from original event, entry, or previous step. Test daylight-saving transitions; do not translate a local-time schedule using a permanent UTC offset.

## Failure and release controls

Separate historical backfill from new-event traffic. Estimate audience and worst-case send volume before activation. Use an authorized small cohort; compare actual eligibility to expected counts. Define who may pause, what stops new enrollment, how queued mail is stopped, and whether rollback restores configuration or also changes contact state. Rollback cannot recall messages already sent.

For retryable confirmed failures, use provider-documented backoff, limits, and a dead-letter path. Never replay an entire flow to recover one uncertain step. Preserve audit records without exporting unnecessary personal data.
