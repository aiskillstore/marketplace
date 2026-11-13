# Sources

Platform facts this skill states. Each page was read on 2026-11-05 and the
fact is stated "as of 2026-11-05".

| Fact used in the skill | Source | As of |
|---|---|---|
| Core Web Vitals "good" thresholds: LCP 2.5 s or less, INP 200 ms or less, CLS 0.1 or less, measured at the 75th percentile of page loads, mobile and desktop separately. | web.dev, Web Vitals: https://web.dev/articles/vitals | 2026-11-05 |
| PageSpeed Insights web tool and v5 API endpoint. The keyless API shares a public daily quota; on 2026-11-05 a keyless call returned "Quota exceeded ... Queries per day". | https://pagespeed.web.dev and https://developers.google.com/speed/docs/insights/v5/get-started | 2026-11-05 (quota behaviour observed directly; docs page not re-read) |
| Google Ads landing page experience is "how relevant and useful your landing page is to people who click your ad", one of three Quality Score components; Quality Score is a diagnostic and "is not an input in the ad auction". | Google Ads Help, About Quality Score: https://support.google.com/google-ads/answer/2404197 | 2026-11-05 |
| Google auto-tagging adds `gclid` to the landing URL; some sites error on unknown parameters; the GCLID must be passed to the final landing page through redirects for conversion tracking. | Google Ads Help, About auto-tagging: https://support.google.com/google-ads/answer/3095550 | 2026-11-05 |
| Meta adds `fbclid` to the URL on ad clicks; the Pixel stores it in the `_fbc` cookie; it is case sensitive and must not be modified. | Meta for Developers, fbp and fbc parameters: https://developers.facebook.com/docs/marketing-api/conversions-api/parameters/fbp-and-fbc/ | 2026-11-05 |
| Microsoft Advertising adds `msclkid` to the landing URL when auto-tagging is on; UET reads it from the page URL, so it must survive redirects unchanged. | Microsoft Advertising API docs (Account record, UET Conversions API guide): https://learn.microsoft.com/en-us/advertising/bulk-service/account?view=bingads-13 and https://learn.microsoft.com/en-us/advertising/guides/uet-conversion-api-integration?view=bingads-13 | 2026-11-05 (from search-result summaries of these pages; the pages themselves were not opened, so treat as lightly verified) |
| Touch targets at least 24x24 CSS px (WCAG 2.2 SC 2.5.8 Target Size (Minimum), level AA), with exceptions. | W3C, Understanding SC 2.5.8: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | 2026-11-05 |

## Judgement, not platform rules

The 7-fix cap, the check order, the 390x844 and 1440x900 viewports, the
five-second first-screen test, the "few hundred visits / few dozen
conversions" noise caution, and the refusal to quote lift percentages are
this skill's own choices. Present them as judgement, not as facts.

## Credits

Auditing a page against the promise of the ad that sends traffic to it,
capping the fix list, and ending with "not a problem" and "could not check"
sections were popularised by autonnel's Apache-2.0
`landing-page-conversion-audit` skill (github.com/autonnel/autonnel-skills).
Corey Haines' MIT-licensed `cro` skill (github.com/coreyhaines31/marketingskills)
also checks headline-to-traffic match. Wording, check order and output here
are our own.
