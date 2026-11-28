# Data contracts: freshness, missing data and quotas

> Part of the visdenda-agent skill. Back to https://visdenda.com/skills/visdenda-agent/SKILL.md.
> Read this when the task matches: What each source can and cannot prove; how to avoid turning absence into zero.

## Source semantics

- **GSC**: final data lags about 3 days. Live reads need a paid plan and the daily live-read
  budget; otherwise use `get_gsc_monthly` for an archived month. Archived data is monthly,
  not daily.
- **Audit**: findings belong to a completed run. `pass`/`warn`/`fail`/`na` are different;
  `na` means the rule could not be evaluated on that page. `evidenceKey` points to stored evidence.
- **Index**: a verdict may be indexed, partial, not-indexed, excluded or unknown. Unknown is
  "not checked / check failed", never "missing".
- **Probe / AI traffic**: only sites with the probe installed have data. No probe → `na`,
  not zero. Counts are lower bounds when the read reports truncation.
- **GA4**: sessions/engagement may be a 7-day snapshot even when the request is 28/30 days.
  Read the returned source and window.

## Missing data rules

- `na` + reason is a valid answer. Report it verbatim; do not substitute zero, an empty array
  or a guess.
- An empty insight list means no rule fired, not that the site is healthy. Always read
  `notEvaluated` and `sources`.
- If one source is unavailable, continue with the others and label the gap. Do not fail the
  whole analysis because GSC or the probe is missing.
- Truncated results are lower bounds. Say "at least N" when `truncated` is true.

## Quotas and cost

- Read tools are free but rate-limited; respect `429` and `Retry-After`.
- `audit_url`, `get_site_fingerprint` and `get_site_i18n` perform network fetches and have a
  daily network budget.
- GSC live reads have a separate daily budget. When it is exhausted, fall back to archived data
  or mark the type not evaluated.
- Research tools that call a paid provider require `estimate_research_cost` first; report the
  estimate and wait for confirmation. Cached results should be reused, not re-purchased.

## Writes

`run_audit`, `import_sitemap` and `verify_fix` need `audits:write` plus `confirm:true` and a
unique idempotency key. Without confirmation they return a dry-run preview and change nothing.
Reusing a key within 24 hours returns the first result. Never set `confirm:true` on the user's
behalf without asking.

## Evidence hygiene

Quote the tool's window, source and method. Keep observation, inference and recommendation
separate. If you cannot name the tool call and field that produced a number, do not use it.
