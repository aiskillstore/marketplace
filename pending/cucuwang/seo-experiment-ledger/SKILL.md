---
name: seo-experiment-ledger
description: Use when maintaining a measured search experiment with one exact query, one target page, comparable observations, and a scheduled review
---

# SEO Experiment Ledger

Use geoptimize's SEO ledger to run a controlled page experiment. This workflow remains separate from content-readiness scoring and makes no ranking promise.

## Workflow

1. Run `geo seo status <repository>` and inspect all three JSON files in `data/seo`.
2. Record a fixed Search Console observation with `geo seo record`. Preserve the exact query, target page, country, device, search type, and complete date window.
3. Review a `monitoring` query only when `nextReviewDate` is due. Supply a comparable post-action observation to `geo seo review`.
4. Run `geo seo select <repository>`. Work on the returned query only. If there is no candidate, report the ledger state and stop.
5. Describe who searched, what they needed, and one information gap on the target page.
6. Make one focused page change that addresses the gap. Link to the visitor's likely next question or action when helpful.
7. Run the site's normal checks and a geoptimize build audit. Commit the page change and baseline ledger files without starting the monitoring period.
8. Deploy the page and read the public result back. Then run `geo seo start` with the verified publication date and the completed change. Commit the ledger update and report the next review date without predicting the result.

## Boundaries

- Do not collect Google result pages with a custom scraper.
- Do not interpret `position: null` and zero impressions as proof that a page is absent from the index.
- Do not modify another query while one is `monitoring`.
- Do not change `noindex`, canonicals, redirects, or major site structure without a separate review of the exact scope.
- Do not overwrite earlier observations.
- Do not output or commit credentials, tokens, cookies, or service-account keys.
- Do not describe a geoptimize score increase as ranking evidence.
