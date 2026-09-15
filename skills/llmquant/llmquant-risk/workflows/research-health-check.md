---
name: Research Health Check
description: Audit a user's research workspace for stale profiles, thesis drift, orphan themes, missing alerts, and outdated evidence using LLMQuant Data.
input_data_source: LLMQuant Data
pack: research
---

# Research Health Check

## Purpose

Generate a workspace diagnostic that tells the user what research needs attention now: stale profiles, triggered theses, drifted assumptions, orphan themes, and unmonitored high-risk positions.

## Input Data Source

Use **LLMQuant Data** for profile, thesis, theme, alert, market, fundamental, and event evidence.

## Data Needed

Required LLMQuant Data inputs:
- research health report data for stored health reports.
- research profile inventory, thesis inventory, and theme inventory for workspace inventory.
- equity market snapshot data, company fundamentals data, and equity event radar data for current drift checks.
- research profile refresh capability when the user asks to fix stale profiles.

## Workflow

1. Load the latest health report or generate a fresh one if requested.
2. Group issues by stale profile, thesis trigger, thesis drift, orphan item, and missing monitor.
3. Rank recommendations by urgency and actionability.
4. When asked to fix issues, refresh or update only the items the user authorizes.
5. Re-run the health summary after actions when possible.

## Output Format

1. **Overall Score**: 0-100, band, report date.
2. **Issue Counts**: stale, drifted, triggered, orphaned, missing monitor.
3. **Top Actions**: ticker, action, reason, required tool.
4. **Detailed Findings**: grouped by category.
5. **Data Used**.

## Guardrails

- Do not mutate profiles, theses, or alerts unless the user asks for changes.
- Do not mark a thesis as safe if required monitoring data is unavailable.
- Keep report date prominent.
