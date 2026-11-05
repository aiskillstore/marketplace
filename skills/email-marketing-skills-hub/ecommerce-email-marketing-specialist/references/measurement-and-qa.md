# Measurement and launch QA

For funnel diagnosis and experiment records, consult [Academy workflows](academy-workflows.md).

## Measurement definitions

Attach a numerator, denominator, time window, currency and data source to every rate. Do not compare different attribution windows as if equivalent.

- Capture rate: unique valid signups / eligible unique exposed visitors (state whether confirmation is required).
- Click rate: unique qualified clickers / delivered emails; identify bot filtering limits.
- Order rate: distinct attributed purchasers / delivered recipients, with attribution rule stated.
- Revenue per recipient: qualifying attributed net revenue / delivered recipients; define refunds/tax/shipping treatment.
- Complaint and unsubscribe rates: provider-defined numerator and denominator, recorded explicitly.
- Incremental contribution: treatment versus randomized holdout result after relevant product/fulfillment/discount costs, with uncertainty and measurement window.

Provider-attributed revenue is not necessarily incremental revenue. Opens can be distorted by privacy systems and scanners; do not select a revenue campaign winner on opens alone. If counts are small, say inconclusive instead of declaring a winner.

For external popup comparisons, use the definitions and limitations in [public popup benchmarks](popup-benchmarks.md). Never substitute a vendor population summary for the merchant’s own baseline or experiment.

## Experiment specification

Write a testable hypothesis, one main treatment difference, randomization unit (usually person), primary metric, guardrails, allocation, practical minimum effect, planned sample/window and stopping rule before launch. Prevent cross-treatment duplicates and coupon contamination. Keep a control/holdout when feasible. Do not repeatedly peek and stop at a convenient result. Report uncertainty; if power cannot be assessed, call it an exploratory test. Check discount cost and adverse effects even when top-line revenue rises.

## Preflight gates

**Audience:** consent status, suppression, dedupe, region, segment counts/freshness, excludes recent purchasers where needed, overlap with live flows/campaigns.

**Offer:** price/inventory true, coupon valid in checkout, terms/minimum/stacking/expiry/time zone agree across all surfaces, discount authorized.

**Content:** truthful claims, approved version, correct From/reply-to and identity, merge fallbacks, verified links, no draft placeholders, readable mobile rendering, image alt text, plain-text usability, unsubscribe works.

**Infrastructure:** verify sender authentication/domain alignment and current applicable mailbox-provider requirements. Confirm SPF/DKIM/DMARC configuration with the authorized owner rather than changing DNS without permission. Check provider volume/reputation limits and one-click unsubscribe where required. Do not guarantee inbox placement.

**Flows:** test eligible/ineligible entry, purchase during wait, unsubscribe during wait, duplicate event, missing product/coupon, retry behavior, timezone and out-of-stock paths. Use draft/test mode and explicitly authorized test recipients; a test email is still a send.

**Release:** confirm account, recipients, final copy/version, dates/time zone and authorization. Record state/object ID and provider response. After release verify expected state and monitor agreed delivery/error and complaint signals. Propose a pause threshold appropriate to history/provider rules; do not invent a universal safe complaint level or silently change live state outside authorization.

## Analysis output

Lead with observed result and decision, then evidence, uncertainty, likely explanations, next test and owner. Separate correlation from causal evidence. State missing data that could reverse the conclusion. Prefer a small justified next step over a laundry list.
