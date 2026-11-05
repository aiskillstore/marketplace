# Lifecycle automations

For cross-flow side effects, property updates and stopping semantics, consult [Academy workflows](academy-workflows.md).

## Required flow specification

For each flow provide:
1. Purpose and owning system; separate transactional and promotional messages.
2. Verified event name/schema, identity matching and timestamp source.
3. Entry eligibility: marketing permission and suppression status, event conditions, applicable audience.
4. Delay with explicit anchor and time-zone/quiet-hours handling where applicable.
5. Each step's eligibility check, branch, copy/CTA and data fallback.
6. Exit conditions checked before every send, not just on entry.
7. Re-entry/cooldown, deduplication key and overlap precedence.
8. Missing/late events, connector failure, out-of-stock and coupon exhaustion behavior.
9. Test identities, expected outcomes, monitoring and pause/rollback owner.

Never treat an anonymous browse or cart event as a known address. Validate event coverage and consent before claiming a recovery flow is implementable. Provider-specific names and template syntax must be verified; semantic event labels in plans are not executable API payloads.

Unknown purchase tracking blocks purchase-dependent claims, branches and acquisition reminders. It need not block an otherwise eligible, purchase-neutral welcome series designed to be useful to both buyers and non-buyers. State that limitation explicitly.

## Starting patterns to adapt

**Welcome:** trigger confirmed eligible subscription, once per newly eligible person; fulfill any approved signup promise promptly; follow with useful orientation and a relevant purchase guide. Example proposal: at entry, +2 days, +5 days. Recheck purchase and coupon redemption before promotional reminders. A purchaser can exit the acquisition path and enter an appropriately scoped customer path.

**Cart/checkout recovery:** require identifiable eligible contact and a reliable qualifying event. Example proposal: +2 hours help/reminder, +24 hours objection resolution; optional later incentive only if approved and commercially justified. Exit on corresponding order/purchase, unsubscribe, invalid cart or suppression. Distinguish added-to-cart from checkout-started events; do not claim they are interchangeable. Recheck stock and price. Define cart/session dedupe and how new activity resets a timer.

**Browse recovery:** require permission, identity and supported product-view tracking. Exclude cart/checkout recovery, purchase and recent equivalent messages. Keep the message useful without exposing a creepy browsing history. No tracking means no event-driven browse promise.

**Post-purchase:** anchor product education to order/delivery events as appropriate, not an arbitrary instant upsell. Separate order receipts from marketing. Suppress promotional steps for cancellations/refunds or unresolved issues when reliable data exists. Request reviews only after enough time to use the product; never condition a benefit on a positive review.

**Replenishment:** derive timing from product consumption or observed repeat orders; exclude durable goods and subscriptions already replenishing automatically. Exit/reset on repurchase. If no reliable consumption evidence exists, label timing a hypothesis.

**Win-back:** start after a category-specific inactivity interval and only for eligible contacts. Try useful newness or preference-setting before a blanket discount. Limit attempts and define sunset/suppression handling. Do not reactivate unsubscribed contacts.

## Collision control

Choose explicit precedence within promotional messaging. One possible proposal: cart recovery before general promotional campaign; new purchaser exits pre-purchase reminders; service-critical transactional messages remain independently managed. Set a store-wide promotional pressure policy and verify the platform can enforce it across flows/campaigns. If not, design exclusion segments or manual scheduling checks rather than claiming a global cap exists.
