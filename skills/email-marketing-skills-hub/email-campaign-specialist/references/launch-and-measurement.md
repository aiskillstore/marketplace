# Launch review and measurement

## Launch gates

- Verify account/workspace, sender identity, reply address and required authentication status. Inspect before changing DNS or other security-sensitive settings; those changes are a separate authorized action. Do not promise inbox placement from authentication alone.
- Write inclusion and exclusion logic explicitly, including AND/OR grouping. Reconcile the raw audience with suppressions and deduplication. Confirm whether the final audience is frozen now or reevaluated at send time.
- Check the offer, landing page, destination domain, redirects, tracking parameters and any availability/deadline. Do not put personal or sensitive subscriber data into tracking URLs. Use campaign-level UTMs when appropriate.
- Verify merge syntax and missing-field fallbacks with representative records. Review subject, preview text, body, buttons, alt text, readable contrast, mobile display and plain text. Do not rely on image-only essential information.
- Confirm applicable unsubscribe and sender-identification controls. Legal requirements depend on jurisdiction and campaign type: verify current authoritative requirements when giving compliance advice; a checklist does not certify compliance.
- Check preference handling, complaint/bounce suppressions, recent sends, overlapping campaigns and existing automations. Decide whether recipients can reasonably receive both messages.
- Verify exact timezone and dated schedule, not merely “tomorrow morning.” Confirm daylight-saving behavior when relevant.
- Use authorized test recipients and inspect rendered output, links and actual received headers when possible. Record what could not be tested.
- Present remaining blockers distinctly. Lack of a platform feature can be handled with an honest manual handoff or external analysis, not a fabricated control.

## Experiment design

Choose a hypothesis and a business-relevant primary metric before sending. Randomize nonoverlapping eligible recipients if the platform supports it; preserve comparable timing and eligibility. Change one meaningful element when isolating cause. Define the analysis window, sample-size constraints and decision rule in advance. Small samples produce directional evidence, not a guaranteed winner. Avoid early winner selection from repeated peeking. If an experiment is not randomized, describe the comparison as observational.

Open-rate changes alone are weak evidence because privacy protections and image fetching can distort opens. Clicks can include automated security scanning. Prefer verified conversion events or qualified engagement where available. Do not resend to all “non-openers” without considering unreliable opens, fatigue, eligibility and the need for separate authorization.

## Reconcile metrics before interpreting

Use the provider's definitions and label yours. Distinguish unique recipients from total events. Common normalized metrics:

- Unique click rate = unique recipients clicking / delivered messages.
- Conversion rate per delivered = unique converting recipients / delivered messages.
- Click-to-conversion rate = unique converters among clickers / unique clicking recipients, only when the cohorts and attribution agree.
- Revenue per delivered = attributable revenue / delivered messages, with currency, refunds treatment and attribution window stated.
- Unsubscribe rate = unsubscribes / delivered messages, unless the provider defines another denominator.

A zero denominator means unavailable, not 0%. Missing data is not zero. Check that unique recipients do not exceed their relevant cohort, investigate conflicts rather than silently correcting them, and keep attempted, accepted, sent, delivered and bounced counts separate. Delivery does not establish inbox placement. Compare like-for-like time windows and audiences; distinguish observed attribution from incremental causal lift. Include unsubscribe, complaint, failure and bounce guardrails alongside revenue or clicks.

Prioritize the likely bottleneck: eligibility/data, dispatch failure, click quality, landing-page action, or offer relevance. Give one concrete next experiment with its expected learning; do not recommend new tooling solely because performance is weak.
