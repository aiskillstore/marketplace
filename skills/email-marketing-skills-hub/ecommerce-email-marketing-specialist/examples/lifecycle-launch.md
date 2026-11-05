# Worked example: Cedar Cup welcome journey

**Fictional training scenario. Nothing here was sent or configured.** The brand, audience and offer below are scenario inputs, not claims about a real merchant. Semantic data names are not executable provider syntax. This shows an implementation handoff, not a universal recipe.

## Provided brief

Cedar Cup sells reusable ceramic mugs on Shopify and uses an existing email provider. The merchant wants a signup popup and three-email welcome series, with warm, concise copy. Approved incentive: 10% off a first order of full-price mugs, one use per new customer, no stacking, expires seven days after issue. No fixed campaign deadline. Keep the current email provider. Marketing permission must be confirmed before entry. All URLs, legal footer details and product specifics remain to be supplied.

## Recommendation and blockers

Keep the current email provider as the sending system. Evaluate its native form first. Poptin is a candidate if capture targeting or coupon delivery is a real gap, not a prerequisite. Account and integration testing would be needed before setting up that extra tool, not before suggesting it as an option.

Priority 1: prove subscription, purchase and coupon data. Priority 2: build the form and welcome draft. Priority 3: test and measure before increasing traffic. Do not launch until URLs, sender identity/footer, consent wording, checkout code enforcement, event fields and actual coupon expiry timezone are verified.

## Capture spec

Audience: new visitors not known to be subscribed or previous customers. Since anonymous visitor purchase history may be unavailable, checkout enforces new-customer eligibility; the popup never promises it can reliably recognize all previous buyers.

Proposed test: desktop/mobile popup after 20 seconds of engagement on collection/product pages, no checkout interruption; suppress after submission and apply a seven-day dismissal cap if supported. Keep an embedded footer option. Timing is a test hypothesis, not an existing setting.

Headline: “A warm welcome, with 10% off”

Body: “Join Cedar Cup emails for new arrivals and mug inspiration, plus 10% off your first order of full-price mugs.”

Field: “Email address”

CTA: “Send my welcome offer”

Permission text for review: “Sign up for Cedar Cup marketing emails. Unsubscribe anytime. Read our privacy notice.” Link the actual notice; verify the final consent mechanism for the merchant's policy and markets.

Terms: “New customers only. Full-price mugs only. One use per customer. Cannot be combined with other offers. Your code expires seven days after issue.”

Success: “Check your inbox to confirm your subscription. Your welcome offer follows confirmation.”

Error: “We couldn't save your signup. Please try again.”

Close: “Close signup form”

Coupon implementation: unique code created/validated by the store or a verified integration. Send the same assigned code across retries. If code assignment fails, hold the offer email and alert the owner; do not send a broken token or quietly substitute an unapproved discount.

## Segment and workflow

Entry: confirmed marketing subscription event AND marketable AND complete order history shows zero qualifying orders AND not previously entered this welcome offer. Missing order/consent data holds eligibility for review.

Semantic dedupe: stable contact ID + welcome-offer version. Exclude suppression/complaint/hard-bounce/unsubscribe at every send. Exit acquisition messages after any qualifying purchase. Exclude recipients in active cart recovery from overlapping welcome promotional reminders according to a verified precedence rule. These conditions must map to actual provider fields.

- Email 1: after confirmation and successful code assignment. Deliver offer.
- Email 2: two days after Email 1, if still eligible and not purchased. Product-selection help.
- Email 3: five days after code issuance, if still eligible, code unredeemed and valid. Exact expiration date/time is inserted from the coupon record, not calculated differently in each email.
- Re-entry: none for this welcome offer. Never re-enroll an unsubscribed person.

## Complete draft copy

Square-bracket fields are intentional unresolved draft values; they block production sending.

### Email 1

Subject: Your Cedar Cup welcome offer

Preheader: Take 10% off your first order of full-price mugs.

Hi there,

Welcome to Cedar Cup. We're glad you're here.

Your first-order code is [ASSIGNED_CODE]. Use it for 10% off full-price mugs before [EXACT_EXPIRY_WITH_TIME_ZONE].

Find a mug for your morning coffee, afternoon tea, or a quiet moment in between.

CTA: Find your mug → [VERIFIED_MUG_COLLECTION_URL]

New customers only. One use per customer. Full-price mugs only. Cannot be combined with other offers.

The Cedar Cup team

[VERIFIED_BUSINESS_IDENTITY_AND_REQUIRED_ADDRESS]
[WORKING_UNSUBSCRIBE_LINK]

### Email 2

Subject: What does your everyday mug look like?

Preheader: A simple place to start your search.

Hi there,

A favorite mug should fit the way you like to take a break.

Browse the collection and compare the listed dimensions and care information to find the one that suits your routine.

Your welcome code, [ASSIGNED_CODE], is available until [EXACT_EXPIRY_WITH_TIME_ZONE] if you'd like to use it.

CTA: Explore the mugs → [VERIFIED_MUG_COLLECTION_URL]

10% off a first order of full-price mugs. New customers only. One use per customer. Cannot be combined with other offers.

The Cedar Cup team

[VERIFIED_BUSINESS_IDENTITY_AND_REQUIRED_ADDRESS]
[WORKING_UNSUBSCRIBE_LINK]

Draft fact check: confirm the collection/product pages actually provide dimensions and care information; otherwise replace that sentence with verified helpful guidance.

### Email 3

Subject: A reminder about your welcome offer

Preheader: Your 10% code expires on [VERIFIED_EXPIRY_DATE].

Hi there,

If you've had your eye on a Cedar Cup mug, your welcome offer is still available.

Use [ASSIGNED_CODE] for 10% off your first order of full-price mugs before [EXACT_EXPIRY_WITH_TIME_ZONE].

CTA: Browse the collection → [VERIFIED_MUG_COLLECTION_URL]

New customers only. One use per customer. Cannot be combined with other offers.

The Cedar Cup team

[VERIFIED_BUSINESS_IDENTITY_AND_REQUIRED_ADDRESS]
[WORKING_UNSUBSCRIBE_LINK]

## Test cases and measurement

1. Unconfirmed subscriber: no marketing flow entry.
2. Confirmed eligible new subscriber: one valid code and one Email 1.
3. Duplicate confirmation event: no duplicate code or message.
4. Purchase during delay: no remaining acquisition emails.
5. Unsubscribe during delay: no further marketing.
6. Missing order data: held, not treated as zero orders.
7. Exhausted code pool: alert/hold; no broken offer email.
8. Existing customer reaches popup: checkout rejects ineligible code clearly; reassess targeting if common.
9. Mobile dismiss and keyboard navigation: test expected close/focus behavior.

Measure confirmed opt-ins per eligible unique exposed visitor, first orders within a predeclared seven-day attribution window, net contribution after discount and complaints/unsubscribes. Compare popup versus embedded-only control if traffic supports it. Do not claim incremental revenue without an appropriate holdout. All counts and results remain unknown until measured.
