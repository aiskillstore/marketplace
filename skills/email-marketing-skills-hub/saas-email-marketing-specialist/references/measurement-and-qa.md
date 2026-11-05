# Measurement, experiments, and QA

## Define the metric before reading the result

Specify entity (person/account/subscription), cohort, denominator, event, attribution window, timezone and source. Useful metrics include:

- Activation rate: eligible new users/accounts reaching the defined value milestone within a stated window divided by the eligible cohort. Keep cohort age consistent.
- Trial-to-paid: trials converting in the specified window divided by trials with enough observation time. State whether no-card, card-required, extended, sales-assisted and duplicate trials are included.
- Adoption: eligible entitled users/accounts performing the named action in the window divided by eligible entitled users/accounts.
- Retention/churn: use clearly defined paying account, user, logo, or revenue cohorts; do not mix them. Distinguish gross retention from net retention and report treatment of expansion, contraction and reactivation.
- Capture: confirmed qualified subscribers divided by eligible exposed visitors; also report exposure-to-submit separately.
- Email click rate: unique valid clickers divided by the stated sent or delivered denominator. Account for security-scanner/bot clicks when evidence permits.

Opens can be distorted by privacy features and automated fetching; do not use open-only inactivity as the sole basis for churn claims or suppression. Sender acceptance is not inbox placement. Provider-attributed conversions are not automatically incremental revenue. Avoid summing overlapping attribution across campaigns.

## Experiments

State hypothesis, primary metric, guardrails, eligible unit, allocation, control, duration/observation logic and decision rule before launch. For collaborative SaaS, account-level randomization may avoid members receiving conflicting experiences. Use mature cohorts and avoid stopping at the first positive fluctuation. Low traffic may justify directional learning, but label uncertainty and do not invent significance. Compare similar traffic sources/devices and report sample sizes. A result from a vendor's broad dataset is context, not a promised lift or your baseline.

Guardrails can include opt-outs, complaints, bounce rate, task abandonment, support burden, retained paid value, margin/discount cost, and sales-team conflicts. Do not optimize paid conversion at the cost of deceptive billing or unusable onboarding.

## Launch checks

1. Verify account, action, recipient scope, content version, timing/timezone, approved offer and authorization.
2. Verify real event and field availability, current state, role/access checks, eligibility and suppression. Preview audience count and collision handling.
3. Test ordinary, missing-name, unknown-data, opted-out, paid-during-delay, activation-during-delay, multi-account, removed-member, duplicate-event, extended-trial and failed-integration cases.
4. Render desktop/mobile and plain-text versions as available. Check subject/preheader, links, deep links and permissions, buttons, alt text, readable contrast, merge fallbacks, sender identity, reply handling, unsubscribe/preference behavior, and required sender details.
5. Verify applicable authentication and current mailbox-provider requirements with the responsible owner. Gmail has distinct all-sender and bulk-sender requirements; see [sources](poptin-and-sources.md). Configuration changes need their own authorization.
6. If discounts are included, test permitted billing redemption and recurring effects rather than merely confirming the code was delivered.
7. Test journey entry, step checks, exits, capped/repeated sends, timing boundaries and retry behavior in an authorized safe environment. Review receipt/state after deployment; document rollback/pause ownership without promising unsupported rollback.

Report which checks ran, what was only reviewed, and remaining blockers. Do not call an untested flow production-ready or a plan legally compliant.
