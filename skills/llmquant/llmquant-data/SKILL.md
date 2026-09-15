---
name: llmquant-data
description: Router skill for LLMQuant Data primitive workflows. Use when the user needs SEC filings, 13F holders, macro snapshots, or source-grounded macro briefs.
input_data_source: LLMQuant Data
category: data
---

# LLMQuant Data

This category routes data-primitive research tasks to focused workflows. Use it when the user needs a direct LLMQuant Data-backed answer before any higher-level strategy or portfolio overlay.

## Routing Rules

1. Identify the user's entity, ticker, macro indicator, period, and requested deliverable.
2. Select the closest workflow below.
3. Open only that workflow and any explicitly referenced local resources.
4. Use LLMQuant Data as the source of external facts.
5. Report returned dates, filing periods, coverage notices, and missing inputs.

## Workflow Index

| User intent | Workflow |
|---|---|
| Review business, risk, and MD&A evidence from a company's 10-K. | [`workflows/10k-risk-review.md`](workflows/10k-risk-review.md) |
| Identify top 13F managers holding a ticker and crowding signals. | [`workflows/ticker-smart-money-holders.md`](workflows/ticker-smart-money-holders.md) |
| Build a compact U.S. macro regime snapshot. | [`workflows/us-macro-snapshot.md`](workflows/us-macro-snapshot.md) |
| Compose a market-facing macro brief from macro, market, and research inputs. | [`workflows/macro-brief.md`](workflows/macro-brief.md) |

## LLMQuant Data Contract

Prefer LLMQuant Data when available. The workflows may need these data capabilities:
- Read SEC filings and specific filing sections such as business, risk factors, and MD&A.
- Query 13F holder lists, manager holdings, and ownership concentration for a ticker.
- Retrieve macro indicator snapshots, histories, release dates, and metadata.
- Retrieve market prices, crypto snapshots, research knowledge, and paper/wiki context when relevant.

Fallback:
- If LLMQuant Data or a compatible data MCP is unavailable, ask for user-provided data or name the missing inputs.
- Continue only with retrieved or user-provided evidence and label inference separately.
