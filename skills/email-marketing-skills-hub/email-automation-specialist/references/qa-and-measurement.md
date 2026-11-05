# QA, experiments and reporting

## Test matrix

Record input, expected behavior, observed behavior, evidence, and pass/block status. At minimum exercise:

- Eligible new contact enters once and receives the correct version with fallback personalization.
- Unsubscribed, complaint, hard-bounced and unknown-permission contacts are excluded.
- Opt-out after enrollment prevents later marketing, including queued steps where supported.
- Conversion, renewal, purchase or reply exits the relevant sequence before another reminder.
- Duplicate and replayed events do not cause additional sends; simultaneous workers preserve idempotency.
- Late events, stale consent updates and out-of-order conversion events cannot reopen a completed journey.
- Required event fields absent, malformed timezone, and missing personalization fail safely.
- Existing contacts/backfill, overlapping journeys and frequency caps produce expected volume.
- A timed-out send remains unknown until reconciled; a replay does not duplicate it.
- Quiet hours, local-time fallback and daylight-saving transitions are respected.
- Discount validity, URL destination, tracking parameters, HTML/plain text, mobile layout and accessibility are checked.
- One-click and body opt-outs work on synthetic addresses; suppression propagates to every sending system.

Use synthetic fixtures and approved seed addresses. A test send is an external communication, not a free exception to authorization. Do not export a production contact list to a new service just to test it.

## Measurement definitions

Define the conversion event and observation window before deployment. For a journey, report unique eligible entrants, recipients attempted, provider-accepted sends, delivery when supported, bounces, deduplicated clicks, conversions and exits. Specify numerator and denominator for each rate; acceptance or delivery is not inbox placement.

Report complaint/unsubscribe counts and rates with provider definitions. Do not impose a generic success benchmark across businesses. Choose alert/stop thresholds from the provider's current requirements, historical baseline and approved risk tolerance; specify who can pause and what happens to pending messages.

Apple Mail Privacy Protection downloads remote content independently of engagement, limiting open-based interpretation. Avoid using opens alone for branches, reactivation or experiment winners. Treat clicks as imperfect too: security scanners and bots can follow links. Prefer verified downstream actions and provider-supported bot filtering. [Apple explanation](https://www.apple.com/legal/privacy/data/en/mail-privacy-protection/)

## Experiments

State hypothesis, randomization unit, allocation, primary outcome, minimum detectable effect or decision threshold, observation window, sample-size assumptions and guardrails before starting. Keep holdouts stable across the journey; account-level randomization may be needed when several users share an account. Avoid changing multiple variables if the goal is to identify a specific cause.

Compare conversion rates using equivalent eligible cohorts and exposure windows. Do not call a variant a winner from tiny samples or repeated unplanned peeking. Report uncertainty and practical effect, not just statistical significance. A holdout supports incremental impact only when assignment and contamination controls are credible. Platform-attributed revenue without a control is not proven lift; deduct refunds and cancellations consistently when applicable.

## Launch and recovery report

Include version and account, actual vs expected audience count, authorization reference, QA evidence, unresolved exceptions, activation/backfill behavior, monitoring owner, stopping thresholds, and rollback controls. If live work was not authorized or access is missing, deliver a build-ready plan and explicitly label live verification outstanding.
