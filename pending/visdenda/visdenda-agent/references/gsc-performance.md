# Search performance and opportunity analysis

> Part of the visdenda-agent skill. Back to https://visdenda.com/skills/visdenda-agent/SKILL.md.
> Read this when the task matches: Windows, declines, CTR gaps and cannibalization without inventing causality.

## Establish the window

GSC final data lags about 3 days. A "last 28 days" read ends roughly 3 days ago; say that
when you report it. `get_gsc_overview` / `get_gsc_queries` / `get_gsc_pages` use live GSC on
paid plans and have a daily live-read budget. On a free plan, use `get_gsc_monthly` for an
archived month instead of pretending the live window exists. Read the returned source and
`dataThrough`; never silently mix live and archive windows.

## Use the judgment layer first

`get_site_insights` already computes:

- `declining_page`: previous equal-length window vs current, clicks lost.
- `high_impressions_low_ctr`: impressions above the site median with CTR below the site median.
- `cannibalization`: one query with multiple pages, with revenue-page conflict flagged.

These are rule outputs, not verdicts. Treat `severity` as a starting order and read
`evidence` and `impact.method` before recommending anything.

## One-call answers

The server pre-computes four digests so you do not have to re-rank raw rows yourself:

- `get_gsc_quick_wins` — striking-distance queries (position 4-20, above-median impressions)
  with the page, CTR and potentialClicks measured against the site's own top-position CTR.
- `get_gsc_cannibalization` — queries split across competing pages: the leader's impression
  share and each page's position and clicks, ordered by clicks landing on non-leader pages.
- `get_gsc_weekly_report` — last 7 days vs the previous 7 in one read: totals with deltas,
  top-5 winning/losing pages, top-5 new/lost queries, top-3 quick wins and position movers.
  The report is co-occurrence data; never narrate a cause from it.
- `get_gsc_decay` — pages losing clicks across two equal windows (28/90d, vs previous or
  last year), labeled `decayed-content` (position held — a refresh is the actionable first
  step) or `ranking-drop` (position fell — a refresh will not fix it). Counts cover the
  full evaluated set even though steady rows stay out of the list.

All four are live GSC reads on paid plans and share the same daily live-read budget as
`get_gsc_overview` / `get_gsc_queries` / `get_gsc_pages` — one call counts as one upstream
read even when it fans out over several cached windows.

## Drill down

- Page-level story → `get_page_report` for search, sessions, AI fetches, index verdict,
  findings and CWV in one read.
- Query-level story → `get_gsc_queries` for clicks, impressions, CTR, position and deltas.
- Page list → `get_gsc_pages`; use the deltas to separate growth, decline and new pages.
- Monthly history → `get_gsc_monthly` for an archived month when live data is unavailable.

## Rules of evidence

- A CTR gap is relative to the site's own median, not a universal benchmark. Do not claim
  "the title is bad" from CTR alone; check position, query intent and the landing page.
- A decline is not automatically an algorithm update. Check `get_radar_updates` /
  `get_update_impact`, seasonality, tracking changes and page changes before naming a cause.
- Cannibalization means pages compete for the same query, not that one must be deleted.
  Check revenue role (the tool flags it), internal links and canonical signals.
- If GSC is not bound, free-plan live reads are unavailable, or the daily cap is reached,
  say which type was not evaluated. Do not estimate clicks from impressions as a substitute.

## Recommend and verify

For title/meta or content changes, the effect window is weeks, not minutes. State the
expected window (usually 28 days), then re-read the same window. Use `verify_fix` only for
rule rechecks, not for traffic outcomes. "No conclusion yet" is a valid result.
