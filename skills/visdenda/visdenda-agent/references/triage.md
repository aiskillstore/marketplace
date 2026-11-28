# Triage a site before touching anything

> Part of the visdenda-agent skill. Back to https://visdenda.com/skills/visdenda-agent/SKILL.md.
> Read this when the task matches: Pick the one question that matters, read the judgment layer, then drill.

## Ask one question first

Do not start from a tool. Start from the user's question:

- "Why did traffic change?" → search performance and update timing.
- "What should I fix first?" → audit findings ranked by traffic.
- "Why is this page not indexed?" → index status and crawl evidence.
- "Are AI assistants using the site?" → AI crawler and AI Overview data.
- "What is the competitor doing?" → competitor changes and gaps.

If the request mixes questions, answer the highest-revenue one first and say what you deferred.

## Read the judgment layer

1. `list_sites` or `get_portfolio` — confirm the site exists, is verified, and see attention order.
2. `get_site_insights` — the front door. It returns ranked, evidence-backed insights and,
   separately, the types it could not evaluate.
3. Pick at most one primary insight type to pursue. For each insight keep:
   - `target` (page or query),
   - `evidence` numbers and window,
   - `impact.atStake` and `impact.method`,
   - `suggestedAction.kind` / `verifyWith`.

## Drill only where the insight points

- Audit fail → `diagnose_site` or `get_audit_findings` → `explain_finding`.
- GSC decline / CTR / cannibalization → `get_page_report` or `get_gsc_queries`.
- Index gap → `get_page_report`; use `audit_url` for a live canonical/robots check.
- Crawler gap → `get_crawler_gaps` for the path list and agents.
- Portfolio-level → `get_project_status` for runs, changes, radar and GSC snapshot together.

## Stop conditions

- No completed audit run → do not diagnose technical causes; run an audit first.
- GSC not bound or not evaluated → say so; do not convert missing data into "no problem".
- Coverage insufficient or a source truncated → qualify the conclusion.
- The user asked for a fix, not a report → finish with the action and its verification,
  not with a longer list.

## Hand-off

End with: what you observed, what you infer, what you recommend, how you will verify.
Keep the distinction visible. A well-scoped "not evaluated" is more useful than a confident guess.
