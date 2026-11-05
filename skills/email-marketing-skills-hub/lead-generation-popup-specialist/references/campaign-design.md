# Campaign design decisions

These are starting hypotheses, not empirical conversion promises.

## Match the offer to intent

- Ecommerce first visit: compare a useful buying guide or product benefit with an economically justified welcome offer. Confirm discount amount, exclusions, minimum spend, stacking, redemption limit, validity, and margin before publishing a coupon.
- Product comparison: offer a comparison guide, sizing help, or saved shortlist rather than an unrelated newsletter.
- B2B resource page: use a directly relevant checklist or template; ask for email first unless qualification is necessary. A demo request may justify company or role fields if someone uses them to route the inquiry.
- Services: make the next step concrete, such as requesting availability. Avoid promising response times the business has not approved.
- Content: articulate the actual newsletter topic and cadence. An inline form near useful content can be more appropriate than a blocking overlay.

## Triggers are not targeting

Eligibility answers who and where: page/path, device, traffic source, customer state, and exclusion groups. Triggers answer when: click, elapsed engaged time, scroll, page count, inactivity, or an available exit signal. Specify logical AND/OR behavior and evaluate interactions. A scroll percentage can fire immediately on short pages; a time delay includes idle time unless engagement is measured.

A starting experiment might compare a click-open invitation with a modest delayed popup after meaningful content engagement. Choose actual delay and cap from the site journey. Desktop exit signals do not translate directly to mobile; verify the platform's mobile mechanism rather than asserting a reliable mobile exit event.

Keep existing subscribers and converted visitors out of repeat acquisition asks when reliable, consent-appropriate state is available. Do not fingerprint people to force suppression. Exclude sensitive/account/checkout flows when interruption is inappropriate. Set a campaign priority to prevent overlapping overlays. Do not reopen a dismissed popup immediately. Treat cookie resets, private browsing, cross-device use, and storage restrictions as suppression limitations.

## Form and copy checklist

A form needs a real input, clear label, useful validation, an actionable submit control, and an honest success state. A button to another page is not a submitted lead. Test invalid email, empty input, duplicate submission, network timeout, integration failure, and retries. Do not show a delivered-resource claim if delivery failed.

Use truthful incentives and neutral choices. Never use fake countdowns, fabricated scarcity, disguised consent, preselected marketing permission, or shaming dismissal language. Confirm any genuine expiration in both popup and email. Separate resource fulfillment from optional additional marketing where required; consult current applicable rules rather than presenting generic copy as legal advice.

## Mobile and accessibility QA

Test a narrow viewport, zoom, landscape, virtual keyboard, long translations, keyboard-only use, visible focus, screen-reader labels, and a discoverable close action. For modal dialogs, check focus placement/containment and return focus on close. Avoid hiding essential content or covering controls. Test with the actual page, consent banner, navigation, and chat widget, not just a standalone editor preview. Consult current platform and search guidance before relying on intrusive interstitial behavior.

## Academy-informed workflow checks

The public [Academy guide directory](https://www.poptin.com/academy/guides/) provides practical workflows rather than experimental proof of uplift. The following applications were checked on 2026-11-04:

- [Ethical content gating](https://www.poptin.com/academy/guides/capture-more-high-intent-leads-with-an-ethical-content-gate-workflow/): reserve gates for substantial standalone resources, not ordinary introductory articles. Explain whether access is immediate, emailed, or conditional on confirmation, then test that exact path. Poptin's documented Content Gate prevents closing before conversion; disclose this behavior and prefer a dismissible popup or embedded form when visitors should be free to decline. Do not accidentally make essential page access conditional on signup.
- [Display-frequency workflow](https://www.poptin.com/academy/guides/improve-popup-conversions-without-annoying-visitors-a-smarter-display-frequency-workflow/): define first display, dismissal, conversion, and subsequent-page behavior as separate states. Begin with one useful audience distinction; adding many filters can starve delivery and obscure diagnosis. Audit actual transitions across pages instead of checking only the initial trigger.
