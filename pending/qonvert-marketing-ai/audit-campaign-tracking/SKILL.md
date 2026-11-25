---
name: audit-campaign-tracking
description: Inspect supplied campaign links and plan a test for UTM tags and ad click identifiers. Use when traffic is unattributed or a user asks where source, medium, campaign, gclid, or yclid are lost.
---

# Audit campaign tracking

Ask for a few example links with sensitive parameter values removed, the originating channels, and the destination report. If the issue involves orders, identify the last stage with reliable evidence: link, landing page, analytics event, CRM or order record.

1. From the supplied link, extract only the relevant query parameters. Check presence, empty values, duplicates and agreed naming conventions for `utm_source`, `utm_medium` and `utm_campaign`. Use `utm_content` and `utm_term` when the team's reporting needs them.
2. Treat `gclid`, `gbraid`, `wbraid` and `yclid` as click identifiers. Advertising systems can add identifiers at click time. A sample without an identifier leaves live click tracking unverified. Use provider-generated values for real checks.
3. Put every observation under confirmed in the sample, confirmed by a test, or needs evidence. Recommend the next check at the earliest unverified stage. A complete test traces an approved click or test visit through redirects, the landing page and the relevant conversion record, with values redacted in the report.
4. Return a short table with the sample label, observation, implication and next check. If useful, give one corrected example using a placeholder domain and synthetic UTM values. Obtain approval before opening links with sensitive values or editing live campaigns.

For platform behavior, see [GA4 campaign URL parameters](https://support.google.com/analytics/answer/10917952) and [Metrica source tags](https://yandex.com/support/metrica/en/general/source-tags).
