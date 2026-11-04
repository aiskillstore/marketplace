# Lifecycle automations

## Define a flow as a state machine

Specify: goal, identity scope, trigger/event version, entry filters, content, delays and time zone, checks immediately before each send, exits, re-entry, idempotency key, priority/caps, required data, fallback, owner, and conversion measurement. Event names below are conceptual examples, not claims about any platform.

Before a send recheck marketing eligibility, role, account membership, subscription/trial state, milestone completion, and conflicts relevant to that message. Exit when the goal is achieved, eligibility is lost, or the flow becomes irrelevant. Do not rely on entry filters alone. Use a bounded wait for data; on timeout follow a truthful neutral branch or hold the affected step. Missing events do not prove non-use when collection is unhealthy.

Deduplicate on stable event/user/account identifiers rather than email alone. Handle replayed webhooks and late/out-of-order events using event IDs, event time, and authoritative current state. Check unknown send outcomes before retries. Validate provider semantics for exit evaluation, filter timing, waits and concurrency; providers differ.

## Practical flows

### Subscriber nurture

Entry: verified eligible subscription for a defined topic. Deliver the promised resource/education, then demonstrate a relevant use case and an optional next step. Stop promotional nurture on opt-out; route conversion into the appropriate lifecycle state. Do not assume a download grants all-purpose marketing consent.

### Trial/freemium onboarding

Entry: verified creation/start event and eligible recipient. Define activation as a product-value milestone, not merely login. Branch on actual progress and role. Give one useful next action at a time. Stop a milestone reminder once completed, even if completion happens during a delay. Trial and freemium have different end conditions: never invent a freemium expiry.

### Trial ending and conversion

Use authoritative trial_end_at and account billing status; reschedule or cancel pending reminders after extensions or conversion. Communicate only verified consequences. Suppress paid accounts from upgrade-to-start messaging. A reminder may be promotional or service-related depending on actual content and context; do not label it transactional to avoid suppression. Separate legally/operationally necessary notices from optional marketing.

### Feature adoption and expansion

Entry: verified entitlement plus relevant use case, or approved expansion qualification. Target users capable of the action; send purchasing/seat/contract information only to an appropriate decision-maker. Do not infer willingness to buy from logins alone. Suppress during active support incidents when context makes a promotion inappropriate.

### Retention and renewal

Use reliable account health signals over a stated lookback, not a single unopened email. Account activity and an individual user's activity differ. Verify renewal/contract terms, ownership, and support context. Offer education or help before assuming a discount is warranted. Required contract notices belong to a validated operational workflow, not a marketing experiment.

### Cancellation and win-back

Distinguish cancellation scheduled at term end from access already ended, and voluntary from payment-related loss. Respect the user's stated reason and contact preferences. Never obstruct cancellation or imply access is gone when it remains. Recheck reactivation before every win-back send. An approved offer needs explicit terms; never promise restoration of deleted data or old pricing without verification.

### Payment failure boundary

Dunning is a billing/service process. Coordinate marketing suppression and avoid conflicting upsells, but do not change payment retries, subscription status, invoices, or collections policy as a side effect of an email marketing request. Use the authorized billing owner/system for operational actions.

## Collision hierarchy

Define a business-approved hierarchy, such as necessary service notices, relevant onboarding, then optional campaigns, while keeping service classification truthful. Frequency caps apply across optional campaigns/flows; shared accounts may need account-level coordination in addition to per-user caps. Document exceptions rather than assuming a provider cap includes all channels and systems.

## Poptin-specific implementation caveats

When Poptin is selected, consult the [Academy source notes](poptin-and-sources.md#poptin-academy-guidance-applied) before integration. Do not treat a contact upsert as a harmless draft: confirm replacement behavior and whether it sends confirmation mail or starts a live journey. Preserve tags/preferences and genuine subscription status. Verify how to stop messages already queued or in progress rather than assuming that disabling new entry cancels them.
