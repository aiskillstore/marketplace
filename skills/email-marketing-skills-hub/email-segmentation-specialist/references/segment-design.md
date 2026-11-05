# Provider-neutral segment contract

## Data dictionary

Keep a canonical definition next to each provider mapping. Useful concepts include contact ID, channel eligibility with source/timestamp/scope, suppression reason, signup time/source, declared interests, event time, order status, lifecycle stage and last reliable engagement. Fields are optional until a segment needs them. Do not collect extra personal data merely to populate this schema.

Use UTC internally with an explicitly documented business time zone for calendar-day rules. Distinguish event occurrence from ingestion time. Deduplicate events on a stable event ID and contacts on a provider-authoritative identity; do not merge unrelated people because names resemble each other. Across duplicate records, preserve the most restrictive unresolved permission state until the authoritative history resolves the conflict.

For a rolling N-day rule evaluated at T, choose and document boundaries, for example T-N days <= event_time <= T. Future timestamps are data errors, not recent engagement. Null is unknown, not zero or false. An absent purchase history is not proof of no purchases when an integration is missing or incomplete.

## Example recipes, to adapt rather than install verbatim

- New subscribers: eligible AND signup within an agreed window AND no completed welcome flow. Exit on completion or expiration; distinguish new subscription from an old imported contact.
- Declared topic: eligible AND selected_interests contains topic. Multiple topics can overlap; campaign-level deduplication and frequency limits still apply. Missing values receive a relevant general option only within their signup promise.
- Engaged prospects: eligible AND not a verified current customer AND a reliable relevant action in the chosen window. Decide how to handle unknown customer state before counting.
- Post-purchase education: eligible for the intended message AND fulfilled eligible order AND no cancellation/refund requiring a different path. A receipt is transactional; promotional cross-sell needs separate marketing eligibility.
- Repeat/VIP customers: eligible AND an explicitly defined, verified purchase threshold. If using monetary value, document currency, refund treatment and period; do not make inferences about personal wealth.
- Lapsed customers: eligible AND verified prior purchase AND last qualifying purchase older than a business-cycle threshold. Recent support issues or active onboarding may warrant exclusion when data use is authorized.
- Re-engagement: eligible AND enough time and sending opportunity to observe low engagement AND no reliable activity in the chosen window. Missing telemetry is a review cohort. Never use a re-engagement campaign to evade an unsubscribe.

Choose exclusive lifecycle precedence when a single journey is needed, for example current customers before active prospects before new leads. Topic labels can remain overlapping. Record which message wins, where deduplication occurs, and whether a person can re-enter after completing a journey.

## Portable definition example

Segment: Education topic prospects
Goal: Send the promised how-to content.
Eligibility: verified email-marketing permission for this sender and purpose; no current suppression.
Audience: (declared topic includes education) AND (verified customer state equals prospect).
Null policy: unknown topic or customer state goes to review, not this audience.
Time/freshness: evaluate eligibility immediately before send; refresh customer data at the documented integration cadence.
Exit: topic removed, conversion to customer, permission revoked, suppression, or changed signup promise.
Overlap: topic audiences may overlap; one recipient per campaign plus account-wide frequency cap.
Measurement: unique downstream actions / delivered messages, with complaints and unsubscribes as guardrails. Define attribution window and event deduplication before comparing.

This is conceptual logic, not a supported API payload for any provider.
