# Capture, forms and coupons

Use [public popup benchmarks](popup-benchmarks.md) when users ask for comparative performance or research-backed test ideas. Keep the source’s metric definitions and limitations attached to any numerical comparison.

For multi-page display behavior and source-specific messaging, consult [Academy workflows](academy-workflows.md).

## Design the capture experience

Define page/audience eligibility, device behavior, trigger, frequency cap, suppression after signup/dismissal, and success/error states. Check coexistence with cookie banners, chat and other overlays. Prefer a small number of high-intent surfaces over stacked interruptions. Preserve a visible dismiss control, keyboard/focus behavior, readable contrast and usable mobile layout; test rather than asserting accessibility compliance.

Possible hypotheses, not product defaults: embedded footer form always available; delayed popup after engagement; desktop exit intent if supported; mobile scroll/delay rather than assuming cursor-based exit intent works on phones. Verify the specific product's device behavior.

Collect only needed fields. Usually email plus an optional preference is enough to start. Record source/form version, signup time and consent evidence as supported and required. Describe the messages subscribers will receive and link the actual privacy notice. Do not preselect consent or label imported records subscribed without evidence. Apply confirmed/double opt-in if required by the merchant's market, policy or provider; pending contacts remain out of marketing flows.

Ensure success-state copy matches the verified opt-in setup: say to confirm by email only when that confirmation message will actually be sent.

Deliver form copy with: headline, value proposition, fields/labels, permission wording, CTA, privacy link, close label, error text and success message. A request for coupon delivery is not necessarily consent to ongoing promotional email; make the distinction clear and use the actual account's subscription rules.

## Offer economics and controls

Before recommending an incentive, compare no-discount value (early access, useful guide, relevant updates), shipping perks and discounts against margin and customer expectations. Do not commit an unapproved amount.

Define fixed versus unique code; eligible items/customers; minimum spend; discount amount/type; stacking; maximum redemptions; expiry/time zone; distribution; exhaustion behavior; revocation and reporting. The store's checkout validates redemption. Displaying a code in a popup does not prove it exists in the commerce platform.

For unique codes, verify that the same subscriber receives a consistent valid code across popup and email, retries do not consume extra codes, and codes are not leaked in public URLs or logs. Test duplicate signup, pool exhaustion, expiry, stacking and a real checkout preview/test mode before release. Never assume a coupon generator can create native discounts for every platform.

## End-to-end data proof

With an authorized test identity: submit form → verify consent/subscription state → confirm correct list/tag/property → verify intended automation entry → verify exactly one delivery → test code eligibility → verify unsubscribe suppression. Check what happens if connector delivery is delayed or fails. Do not claim “connected” based only on an integration badge.

Evaluate signup rate among eligible unique visitors, confirmed subscribers, first-order conversion, discount cost, complaints and net contribution. A bigger list with lower quality is not automatically success.
