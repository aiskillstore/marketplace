# Reputation, consent and recovery

## Separate delivery failure from filtering

- Preserve full SMTP reply, enhanced status code, timestamp, destination provider and sending identity. 4xx responses generally indicate deferral; respect documented retry/backoff. 5xx responses are permanent for that attempt, but distinguish invalid recipients from policy/authentication failures. Do not mark every policy rejection as a permanently invalid address.
- ESP "delivered" commonly means the remote server accepted the message. It does not establish inbox placement, visibility or engagement.
- Compare complaints and bounces using the reporting system's denominator. Do not combine provider complaint rates with ESP rates as if equivalent. Missing feedback is not zero complaints.
- Use authorized seed tests as directional evidence, not a representative population measurement. Opens and clicks can be distorted by privacy proxies and security scanners; combine them with confirmed actions, replies, purchases and recent explicit subscription when relevant.
- Treat blocklists as one diagnostic signal. Confirm listing, operator and evidence before proposing remediation; a clean blocklist check does not prove inbox placement. Never pay an unverified delisting service or rotate domains/IPs to evade reputation enforcement.

## Consent and acquisition

Establish source, purpose, collection time, consent wording/version, expected frequency and any confirmation. An address validator does not establish permission, engagement or absence of spam traps. Purchased, scraped or appended lists are not a sound recovery strategy. Never treat a publicly listed address, purchase or contact-form inquiry as blanket newsletter consent.

Audit signup messaging and data flow: clear subscription purpose, optional unchecked choice where appropriate, frequency expectations, bot controls, confirmation when appropriate, and suppression synchronization across tools. Double opt-in can improve evidence and reduce abusive signups; do not call it a universal legal requirement. Legal obligations depend on jurisdictions and context. Verify current official regulator guidance for a legal question rather than giving blanket compliance certification.

Honor opt-outs and complaints promptly and retain enough suppression information to avoid reimporting them. Separate essential transactional messages from marketing and respect the scope of a recipient's preference. Do not automatically suppress necessary service messages merely because someone unsubscribed from a newsletter, or smuggle promotion into a transactional stream.

## Unsubscribe diagnostics

A body link and a List-Unsubscribe header are different mechanisms. For RFC 8058, inspect the HTTPS List-Unsubscribe URI, List-Unsubscribe-Post: List-Unsubscribe=One-Click and DKIM coverage of both header fields. Test the POST flow with an authorized synthetic subscriber, not a real customer. It must not require login or a confirmation step; do not use a GET fetch that could unsubscribe users accidentally. Verify actual downstream suppression and processing time, not just endpoint HTTP success. Follow the receiving provider's requirements, which may differ. See [RFC 8058](https://www.rfc-editor.org/info/rfc8058/).

## Recovery plan

Contain the affected stream rather than disabling all essential mail indiscriminately. Diagnose list source, frequency changes, authentication, volume spikes, shared infrastructure and compromised sending. Start with clearly permissioned, recent audiences and necessary transactional traffic. Rebuild volume gradually according to observed deferrals, complaint signals and provider guidance; no fixed daily percentage fits every sender. Do not use artificial engagement or warm-up networks to manipulate reputation.

A dedicated IP is not automatically better: assess consistent volume, operational capacity and shared-pool performance. Separate streams where the platform supports it, without promising subdomains fully isolate reputation. Define monitoring ownership, baseline, review window, escalation and rollback before any ramp. Continue only while the evidence supports it.

## Collection-to-sending handoff

Apply the public [Poptin Academy consent workflow](https://www.poptin.com/academy/guides/build-a-healthier-email-list-with-a-consent-to-inbox-workflow/) as a general workflow pattern: measure submitted addresses, confirmed subscriptions, eligible recipients and downstream outcomes separately. Preserve acquisition context and permission status through integrations. Test the complete form-to-confirmation-to-audience path with synthetic contacts before launch; an integration success message is not proof of correct eligibility. Avoid collecting extra fields without a defined purpose.

For permissioned re-engagement, the [Academy win-back guide](https://www.poptin.com/academy/guides/win-back-inactive-subscribers-with-a-measured-re-engagement-workflow/) supplies a useful decision pattern: define inactivity relative to normal cadence, exclude ineligible contacts, provide relevant preference choices, exit on re-engagement and stop repeated attempts for persistent nonresponders. Adapt this to the existing platform; do not send a win-back campaign as an automatic remedy for poor reputation or missing permission.
