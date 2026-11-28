# Indexing and crawler gaps

> Part of the visdenda-agent skill. Back to https://visdenda.com/skills/visdenda-agent/SKILL.md.
> Read this when the task matches: Unknown is not missing; a blocked or 404 path is a concrete task.

## Separate the three states

For every URL keep these apart:

- **Indexed**: Google returned a positive verdict (PASS or PARTIAL).
- **Not indexed / excluded**: a known verdict exists, but the page is not in the index.
- **Unknown**: no verdict has been obtained yet. This is not "missing". It often means the
  URL was never checked, or the check failed because of quota, 403 or timeout.

`get_site_insights` reports `index_coverage_gap` only for the first two. If it returns
`index_coverage_gap` in `notEvaluated`, ask for an index check instead of assuming health.

## Read the evidence

- `get_site_insights` — counts and per-page rows for known gaps.
- `get_page_report` — one URL across index verdict, findings, search and AI fetches.
- `audit_url` — live canonical self-reference, favicon and BreadcrumbList check for a single URL.
- `get_crawler_gaps` — paths AI/search crawlers requested that returned 404/410, plus paths
  blocked by robots or 403, and whether robots.txt / llms.txt / sitemap.xml were fetched.

## Decide the action

- 404/410 with real demand → create the page or redirect to the closest equivalent.
- Blocked by robots/403 → confirm intent before unblocking. Not every blocked path is a bug.
- Known not-indexed page that should rank → check canonical, noindex, internal links and
  sitemap inclusion; then request indexing when the cause is fixed.
- Excluded/duplicate → consolidate or fix the canonical; do not just resubmit.
- Unknown → run an index check; do not tell the user the page is missing.

## Boundaries

- Index checks have daily quotas. Do not loop them; use the returned quota and stop when it
  is exhausted.
- A sitemap is a discovery hint, not an indexing guarantee.
- GSC property binding matters: URL-prefix and domain properties are different resources.
  If the site is not bound, say so and ask for the binding.
