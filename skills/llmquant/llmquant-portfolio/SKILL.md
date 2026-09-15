---
name: llmquant-portfolio
description: Router skill for LLMQuant portfolio workflows. Use when the user needs company profiles, thesis tracking, theme research, watchlist monitoring, or alert management.
input_data_source: LLMQuant Data
category: portfolio
---

# LLMQuant Portfolio

This category routes persistent research workspace and portfolio-management workflows.

## Routing Rules

1. Identify the portfolio object: company profile, thesis, theme, watchlist, or alert.
2. Select the closest workflow below.
3. Open only the selected workflow.
4. Use LLMQuant Data for research profiles, prices, filings, ownership, events, watchlists, alerts, and portfolio context.
5. Report last updated dates, evidence dates, stale notices, and missing workspace objects.

## Workflow Index

| User intent | Workflow |
|---|---|
| Build or refresh a persistent company research profile. | [`workflows/company-profile.md`](workflows/company-profile.md) |
| Turn buy logic into a monitored thesis with sell conditions. | [`workflows/investment-thesis-tracker.md`](workflows/investment-thesis-tracker.md) |
| Track thematic equity baskets and related events. | [`workflows/theme-research.md`](workflows/theme-research.md) |
| Monitor watchlists for price, IV, event, and activity changes. | [`workflows/watchlist-monitor.md`](workflows/watchlist-monitor.md) |
| Create and manage measurable market alerts. | [`workflows/alert-manager.md`](workflows/alert-manager.md) |

## LLMQuant Data Contract

Prefer LLMQuant Data when available. The workflows may need these data capabilities:
- Retrieve, create, or update research profiles, thesis trackers, theme baskets, watchlists, alerts, and portfolio context.
- Retrieve prices, filings, ownership, events, macro context, option context, and latest evidence for tracked names.
- Capture trigger conditions, sell rules, stale evidence, thesis drift, and unresolved data gaps.

Fallback:
- If workspace storage is unavailable, produce the profile, thesis, watchlist, or alert specification as structured output ready for later ingestion.
