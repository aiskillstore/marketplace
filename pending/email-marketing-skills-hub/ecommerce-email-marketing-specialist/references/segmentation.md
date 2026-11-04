# Segmentation and eligibility

## Define the base universe first

`ELIGIBLE = verified_marketing_permission AND deliverable_address AND NOT unsubscribed AND NOT complaint AND NOT hard_bounce AND NOT suppression`

These are semantic fields, not claimed provider field names. Map to the actual data model and channel. Missing or contradictory consent/suppression evidence fails closed for sending. A customer can exist without being marketable. A suppression rule wins over a positive targeting rule.

Define the evaluation time/time zone, event windows (including boundaries), identity/deduplication rules, treatment of cancelled/refunded orders, currency normalization and data freshness before using revenue or purchase counts. Do not treat null order history as zero unless completeness has been established.

## Example segments (proposals, adapt to evidence)

- New eligible non-buyer: `ELIGIBLE AND confirmed_subscription_at within last 14 days AND completed_order_count = 0`, only when order history is complete.
- Engaged prospect: `ELIGIBLE AND completed_order_count = 0 AND (human_click within 60 days OR permitted_identified_site_activity within 30 days)`. Automated/bot clicks and privacy-inflated opens require filtering/qualification; do not rely on opens alone.
- Repeat customer: `ELIGIBLE AND qualifying_completed_orders >= 2`; define qualifying orders first.
- Category interest: `ELIGIBLE AND (declared_category_preference = X OR reliable_category_activity within W)`; avoid inferring sensitive traits from browsing/purchases.
- VIP: `ELIGIBLE AND verified_net_value >= merchant_selected_threshold`; separate high spend from high profitability. Derive thresholds from the merchant's distribution, not a fictional universal benchmark.
- At-risk: `ELIGIBLE AND previous_qualifying_purchase AND days_since_purchase > category_repurchase_window`; ensure a low-frequency category is not mislabeled dormant.
- Coupon claimant, unredeemed: `ELIGIBLE AND assigned_coupon EXISTS AND valid_now AND NOT redeemed AND NOT purchased_since_assignment`, with redemption sync proven. If unknown, avoid “you haven't used it” claims.

## Make segments implementable

For each deliver: name and purpose; Boolean inclusion/exclusion logic; source fields; window/time zone; expected freshness; estimated count only if observed; sample eligible/ineligible cases; refresh behavior; owner. Mark inferred data separately from declared preferences. Explain overlapping segments and choose exclusions or deduplication rather than sending multiple messages to the same identity.

Check boundary cases: unsubscribed VIP, pending confirmation, recent purchaser still in a cart flow, missing purchase data, duplicate email profiles, refunded-only customer, unavailable category, stale integration. Use anonymized fixtures and aggregate counts instead of exporting unnecessary personal records.
