# Eligibility, suppression and deliverability

## Separate the decision layers

1. **User authority:** may this agent make this change or send these messages?
2. **Audience eligibility:** do applicable rules and evidence permit this purpose for this recipient?
3. **Platform and mailbox rules:** does the account and message meet current sending requirements?
4. **Operational readiness:** are triggers, suppression, content, tests and rollback verified?

Passing one layer does not establish the others. Escalate unclear legal interpretations to a qualified reviewer; do not promise compliance.

## Permission evidence

Record origin, collection date, notice/version shown, affirmative action or documented assessed basis, channel, sender/brand, purpose and any expiry or withdrawal. Collect only evidence actually needed and respect retention constraints. A form submission or double-opt-in status by itself does not prove the notice covered this brand and purpose. Confirmations should not turn into promotional emails before eligibility is established.

Identify relevant jurisdictions and recipient types. US CAN-SPAM is not a worldwide consent rule. UK PECR treatment differs for corporate subscribers and individual subscribers; some sole traders and partnerships fall into the latter category. An exception such as soft opt-in has specific conditions, not a blanket existing-customer exemption. Do not generalize UK guidance to EU member states, Canada, Australia, or other markets. Retrieve their current official rules when relevant.

FTC guidance for US commercial email covers accurate sender information, truthful subjects, advertising identification, a valid postal address, accessible opt-out and timely honoring of requests. Commercial content in a supposed service message can change its treatment. The FTC describes a 10-business-day opt-out limit and a 30-day period during which the mechanism must function; stricter applicable requirements still control. Operationally suppress as soon as possible. [FTC guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)

UK decisions should use current [ICO guidance](https://ico.org.uk/for-organisations/advice-for-small-organisations/direct-marketing-and-data-protection/marketing-and-data-protection-in-detail/) and specific facts, not a label such as B2B. Keep the scope of permission and objections aligned with the actual campaign.

## Suppression handling

Preserve marketing opt-outs, complaints and hard-bounce suppressions across migrations and integrations. Do not delete suppression evidence merely to make a contact import succeed. Distinguish lawful minimal suppression retention from keeping an entire profile after a deletion request; refer unclear retention/deletion conflicts to the owner. Do not automatically re-subscribe after a new form submission without verifying valid new permission and applicable rules.

Check unsubscribe links end to end with synthetic contacts, including logged-out behavior, mobile, redirects, preference center and queued-message cancellation. Avoid authentication, payment or unnecessary data collection as an opt-out barrier. Scope a list-level unsubscribe as requested while honoring any brand-wide opt-out and required stop-all option.

## Mailbox requirements

For personal Gmail accounts, Google distinguishes all senders from bulk senders around 5,000 messages/day. Its guidance requires SPF or DKIM for all senders and SPF, DKIM and DMARC for bulk senders, along with infrastructure and formatting requirements. Bulk marketing/subscribed mail needs one-click unsubscribe and a visible body link. Verify current counting rules and eligibility instead of assuming a single campaign's volume determines bulk status. [Google guidelines](https://support.google.com/mail/answer/81126?hl=en)

One-click unsubscribe headers and the body unsubscribe link are different mechanisms; mailto alone does not meet Google's one-click requirement. [Google FAQ](https://support.google.com/mail/answer/14229414?hl=en)

Verify actual authentication results, domain alignment, provider reputation signals, unsubscribe behavior, bounce processing and sending limits. Recommend changes separately when they affect DNS/security or require privileges. Ramp volume according to observed reputation and provider guidance; do not invent a universal daily warmup schedule or guarantee inbox placement.
