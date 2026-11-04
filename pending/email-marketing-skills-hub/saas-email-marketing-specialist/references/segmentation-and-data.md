# Segmentation and data contracts

## Separate people and accounts

Use stable user_id, account_id, membership/role, and relevant subscription_id where available. One person may belong to several workspaces. Specify which account each message concerns and prevent data leakage across memberships. Never deduplicate all members of a company into one recipient blindly; select based on purpose and authority. Billing owner is not synonymous with creator or most-active user.

## Minimal data dictionary

For every required field/event record source of truth, type, timezone, update cadence, allowed values, unknown behavior, and test evidence. Examples:

- marketing_status and topic_status: explicit eligible/ineligible/unknown values; last update and scope.
- account_status: trial, free, paid, cancelled, ended; do not collapse scheduled cancellation into ended.
- trial_end_at: authoritative timestamp, nullable for non-trial plans.
- activated_at: verified milestone timestamp per user or account, as defined.
- role and entitlement: current membership/access permissions.
- last_meaningful_action_at: defined value-bearing action, not email open.
- event_id, occurred_at, received_at, schema_version: replay, order, latency, and schema checks.

Avoid transferring raw sensitive product content, credentials, payment details, or unnecessary customer-level data into marketing tools. Prefer coarse purpose-specific flags and aggregates. Consent in one system may not sync automatically to another.

## Boolean segment examples

The following are pseudocode, not executable provider syntax. Set project-specific intervals and thresholds from the actual business/data. NULL and UNKNOWN are not FALSE.

Trial activation candidates:

marketing_eligible(user, topic) = TRUE
AND active_membership(user, account) = TRUE
AND account.status = 'trial'
AND account.trial_end_at > now
AND activation_observable(account) = TRUE
AND activation_completed(account) = FALSE
AND user.role IN allowed_action_roles
AND NOT suppressed(user)

If tracking is unknown, do not include the user in the "not activated" assertion. A neutral educational message may be possible if independently eligible and not claiming missing progress.

Expansion candidates:

marketing_eligible(user, topic) = TRUE
AND account.status = 'paid'
AND user.role IN approved_buying_roles
AND verified_need(account, defined_window) = TRUE
AND upgrade_eligible(account) = TRUE
AND NOT active_sales_conflict(account)
AND NOT suppressed(user)

Re-engagement candidates:

marketing_eligible(user, topic) = TRUE
AND meaningful_activity_observable = TRUE
AND last_meaningful_action_at < now - project_lookback
AND NOT current_critical_support_case
AND NOT suppressed(user)

A missing last-action timestamp enters only when reliable account history establishes no activity. Specify how the lookback relates to product cadence, seasonality, seat role, and account tenure.

## Consent, exclusions, overlap

Keep global/channel/topic opt-outs, complaints, hard bounces, legal restrictions, and role/access exclusions distinct. Unknown permission is excluded from permission-based marketing until resolved. Never infer marketing eligibility merely from being imported, invited, signed up, paying, or having opened a message.

Preview segment counts and anonymized examples before launch. Test AND/OR precedence, boundary timestamps, nulls, stale membership, multiple accounts, overlapping flows, conversions during delays, and suppression updates. Explain mutual exclusion or priority rather than letting segment overlap multiply sends.
