---
name: visdenda-agent
description: "Analyze a site's SEO with Search Console and crawl evidence: declining pages, low-CTR queries, cannibalization, indexing gaps, technical findings and AI-crawler blind spots, then fix and re-verify. Use when the user asks why organic traffic changed, what to fix first, why a page is not indexed, or whether AI assistants can read the site. Requires a scoped Visdenda API key."
license: CC-BY-4.0
compatibility: Requires an MCP client with Streamable HTTP and a Bearer token.
metadata:
  version: "2026-11-22.2"
---

# visdenda-agent

> Let an AI agent read Visdenda's judgment layer, drill into the evidence, fix the site,
> and verify the fix. Full endpoint reference: https://visdenda.com/docs/api (live from
> https://visdenda.com/openapi.json). MCP alternative: https://visdenda.com/docs/mcp (same key, read-only by
> default; write tools need explicit confirmation).

## When to use

The user's own site needs SEO analysis, a fix decision, or a verified outcome: search
performance, indexing, technical findings, content decay, AI-crawler visibility, or a
competitor gap. Use this skill when the answer must be tied to evidence rather than a checklist.

## Do not use

- Do not use it on a site the key cannot access, or a competitor as if it were an owned site.
- Do not run a paid research call before the user has seen and accepted the estimate.
- Do not claim a ranking factor, citation rate or traffic outcome the tool did not return.

## Auth

- Header: `Authorization: Bearer <YOUR_API_KEY>` (admin-issued; plaintext shown once).
- Scopes: `radar:read` (updates), `rules:read` (rules), `audit:read` (runs, findings, GSC,
  opportunities, insights, effect checks), `sites:read` (competitor reads), `sites:write`
  (onboard, verify), `audits:write` (run audits, import sitemaps, verify fixes),
  `keywords:write`, `monitoring:write`, `research:read` / `research:write`
  (SERP and AI-visibility research).
- Missing key and insufficient scope both answer 401; do not retry without a new key.

## Start here

1. `list_sites` or `get_portfolio` — confirm the site and its verify state.
2. `get_site_insights` — the judgment layer. Read `sources` and `notEvaluated` before the list.
3. Pick one insight; drill with the tool in `suggestedAction.tool` or the matching reference.
4. Fix only after explaining the evidence; then verify with the tool named in `verifyWith`.
5. Report: observation → inference → recommendation → impact → verification → not evaluated.

## Example

"What should I fix first on example.com?"

1. `get_site_insights` → take one `declining_page` insight and read its `evidence`,
   window and `impact` before touching anything else.
2. `get_page_report` for that page → the search, audit, index and AI-fetch facts behind it.
3. `get_radar_updates` → say whether a Search update is in flight before naming a cause.
4. Report observation → inference → recommendation → verification. One question, one primary
   insight; do not stack a second insight until the first is answered.

## Page-level loop

- `fetch_page` — raw facts for one URL (title, meta, canonical, headings, JSON-LD, words).
- `check_url` — per-rule verdicts for up to 5 URLs on one site; no history diff.
- `get_rule` — what one rule checks, where it comes from, and whether it is still active.
- Every tool result carries cost/quota/retryable/next-actions/evidence in its metadata; read it
  before retrying instead of guessing the budget.
- Every result also carries `artifactUrl` when the deployment has a public origin: a 30-day
  read-only page with the same summary, evidence references and payload. Give that link to a
  human instead of re-describing the result.

## Proposal loop

- `propose_fix` — when a change needs a human decision, write a pending proposal with a title,
  summary, rationale and 1–20 concrete changes. It needs `audits:write` and never edits the site.
- A person approves or rejects it in the console. Approval authorizes the change; it does not
  execute it — apply the change yourself, then verify with `verify_fix`.
- `list_proposals` — read the decision, including any rejection note, before proposing again.
  Expired proposals are reported as expired; an identical pending proposal is deduplicated.

## References

- [Triage a site before touching anything](https://visdenda.com/skills/visdenda-agent/references/triage.md) — Pick the one question that matters, read the judgment layer, then drill.
- [Search performance and opportunity analysis](https://visdenda.com/skills/visdenda-agent/references/gsc-performance.md) — Windows, declines, CTR gaps and cannibalization without inventing causality.
- [Technical audit: from finding to verified fix](https://visdenda.com/skills/visdenda-agent/references/technical-audit.md) — Explain the finding, fix the page, re-check the rule, then decide what else changes.
- [Indexing and crawler gaps](https://visdenda.com/skills/visdenda-agent/references/indexing-and-crawl.md) — Unknown is not missing; a blocked or 404 path is a concrete task.
- [AI search: crawlers, referrals and AI Overviews](https://visdenda.com/skills/visdenda-agent/references/ai-search.md) — Read what AI bots actually did; do not treat an empty sample as absence.
- [Competitors and SERP research](https://visdenda.com/skills/visdenda-agent/references/competitors-and-serp.md) — Turn competitor changes into coverage gaps, not copycat pages; price research before buying.
- [Prioritize, report and hand back](https://visdenda.com/skills/visdenda-agent/references/prioritization-and-reporting.md) — Use server-side ranks and evidence; separate observation, inference and recommendation.
- [Data contracts: freshness, missing data and quotas](https://visdenda.com/skills/visdenda-agent/references/data-contracts.md) — What each source can and cannot prove; how to avoid turning absence into zero.

## Non-negotiables

- Fails before passes; attach `evidenceKey` (audit) or the insight `id` and `evidence` (insights).
- `na`, empty and `notEvaluated` are results, not zeros. Say which source was unavailable.
- Use the server's ranking; if you re-rank, state the formula and inputs.
- Write actions need user confirmation, a unique idempotency key, and the smallest scope.
- Respect 429 and `Retry-After`; failed reads do not count against the quota.
