# Sources

Every platform or legal rule in this skill traces to a page below. All were
read on 2026-11-05; the rule stated is "as of 2026-11-05". Providers change
these pages without notice, so re-check before telling a user a rule is
current.

## Mailbox providers

| Rule used in the skill | Source | As of |
|---|---|---|
| All Gmail senders need SPF or DKIM, PTR, TLS, RFC 5322 format, spam rate under 0.3%. Bulk senders also need SPF and DKIM, DMARC (`p=none` allowed), From alignment with SPF or DKIM, one-click unsubscribe for marketing mail. Target spam rate under 0.10%, never 0.30%. DKIM keys 1024 bits or more. Bulk threshold worded as "5,000 or more" and "more than 5,000" per day to personal Gmail. | Google, Email sender guidelines: https://support.google.com/a/answer/81126 | 2026-11-05 |
| Primary domain and subdomains count together toward 5,000; bulk status is permanent; unsubscribes recommended within 48 hours; enforcement ramp-up with temporary and permanent rejections from November 2025; one-click required only for marketing and promotional mail, and recipients decide what is promotional; missing one-click is not auto-rejected but removes mitigation; rules don't apply to mail sent to Google Workspace accounts. | Google, Email sender guidelines FAQ: https://support.google.com/a/answer/14229414 | 2026-11-05 |
| Google Workspace default DKIM selector is `google`; 2048-bit keys recommended where the DNS host supports them. | Google Workspace, Set up DKIM: https://knowledge.workspace.google.com/admin/security/set-up-dkim (old URL support.google.com/a/answer/174124 redirects here) | 2026-11-05 |
| Workspace sending limit 2,000/day per paid user (1,500 via mail merge), 500 on trial accounts, rolling 24 hours. | Google Workspace, Gmail sending limits: https://knowledge.workspace.google.com/admin/gmail/gmail-sending-limits-in-google-workspace (old URL support.google.com/a/answer/166852) | 2026-11-05 |
| Postmaster Tools for Gmail spam rate and reputation. | https://postmaster.google.com | 2026-11-05 (not opened; product URL only) |
| Yahoo: all senders SPF or DKIM, valid forward and reverse DNS, spam rate under 0.3%. Bulk senders: SPF and DKIM, DMARC at least `p=none` that passes, relaxed alignment acceptable, one-click `List-Unsubscribe` (RFC 8058 POST highly recommended, mailto acceptable), visible unsubscribe link, honor unsubscribes within 2 days. No volume threshold on the page. | Yahoo Sender Hub, Best practices: https://senders.yahooinc.com/best-practices/ | 2026-11-05 |
| Outlook.com (outlook.com, hotmail.com, live.com): domains sending more than 5,000/day need SPF pass, DKIM pass, DMARC at least `p=none` aligned with SPF or DKIM; rejection with `550 5.7.515` from 5 May 2025 (the post's 29 April update; an older paragraph in the same post still mentions Junk routing). | Microsoft Defender for Office 365 blog, 2 April 2025: https://techcommunity.microsoft.com/blog/microsoftdefenderforoffice365blog/strengthening-email-ecosystem-outlook%E2%80%99s-new-requirements-for-high%E2%80%90volume-senders/4399730 | 2026-11-05 |

## Standards

| Rule | Source | As of |
|---|---|---|
| SPF: one record, 10 DNS-lookup limit, multiple records are a permanent error. | RFC 7208: https://www.rfc-editor.org/rfc/rfc7208 | 2026-11-05 (well-known; sections 4.5 and 4.6.4 not re-read today) |
| DKIM signatures and selectors. | RFC 6376: https://www.rfc-editor.org/rfc/rfc6376 | 2026-11-05 (not re-read today) |
| DMARC is now RFC 9989 (Standards Track, May 2026), obsoleting RFC 7489 and RFC 9091; records still start `v=DMARC1`. | RFC 9989: https://www.rfc-editor.org/rfc/rfc9989.html | 2026-11-05 (title, date and obsoletes confirmed; record-compatibility point from secondary write-ups) |
| `List-Unsubscribe` header; one-click POST. | RFC 2369 https://www.rfc-editor.org/rfc/rfc2369 and RFC 8058 https://www.rfc-editor.org/rfc/rfc8058 | 2026-11-05 (cited via Google and Yahoo pages) |

## Law and industry positions

| Rule | Source | As of |
|---|---|---|
| CAN-SPAM applies to B2B email; truthful headers, honest subject, ad disclosure, valid postal address, clear opt-out, honor within 10 business days, opt-out working for 30 days; per-email penalties (page gives $53,088 as of its January 2024 adjustment). | US FTC, CAN-SPAM Act compliance guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business | 2026-11-05 |
| UK PECR: corporate bodies (companies, LLPs, Scottish partnerships, government) can be emailed without consent; sole traders and some partnerships treated as individuals; don't disguise identity; give a valid opt-out address; guidance under review. | UK ICO, Electronic mail marketing: https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/electronic-and-telephone-marketing/electronic-mail-marketing/ | 2026-11-05 |
| Deceptive delivery methods for cold email are abusive; bypassing volume limits, avoiding filters, masking sending domains and simulating engagement are "not acceptable in any manner"; a lookalike domain is defined as one that resembles a legitimate domain but is unrelated. | M3AAWG Position on Cold Email, November 2025 v1.0: https://www.m3aawg.org/sites/default/files/doc_files/m3aawg_position_on_cold_email.2025_0.pdf | 2026-11-05 |
| Germany and Canada stricter for B2B cold email. | Not verified against a primary source in this draft. The skill only says rules differ and to check; it does not state either country's rule. | unverified |

## Not from a primary source

These are this skill's own defaults or common practice, and the skill labels
them that way: the stop-rule numbers, the ramp guidance, word counts, the
"no link in email 1" and open-tracking advice, follow-up spacing, and the
90-day freshness window for signals.

## Credits

The idea of reviewing deliverability in order of what decides placement
(authentication, then reputation, then content), and of labelling each claim
by where it comes from, was popularised by Maya-Beth Finotti's MIT-licensed
`cold-email-deliverability` skill (github.com/mbfinotti/sales-skills). The
idea that "no signal found" is a valid research outcome also appears in
Corey Haines' MIT-licensed `cold-email` skill
(github.com/coreyhaines31/marketingskills). Wording and structure here are
our own.
