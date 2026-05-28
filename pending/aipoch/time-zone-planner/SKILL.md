---
name: time-zone-planner
description: Plan cross-time-zone meeting windows for distributed teams, providing region-by-region local time mappings and tradeoff analysis for scheduling decisions.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Time Zone Planner

Structured cross-time-zone meeting planning for distributed teams.

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py
```

## When to Use

- Use this skill when planning meeting windows across multiple regions or time zones.
- Use this skill when comparing candidate windows and tradeoffs for distributed team scheduling.
- Do not use this skill for calendar booking, live availability checking, or travel/legal decisions.

## Workflow

1. Confirm the participant regions, meeting duration, preferred local-hour ranges, and any hard constraints.
2. Check whether the request is for a quick overlap recommendation or a full tradeoff analysis.
3. Use the packaged script for baseline scheduling output; for complex requests, provide a manual comparison table with stated assumptions.
4. Return suggested meeting windows, region-by-region local times, and the tradeoffs behind the recommendation.
5. If timezone details or availability constraints are missing, stop and request the minimum missing fields.

## Usage

```text
python scripts/main.py
# Input: {"regions": ["US", "EU", "Asia"], "duration": 60}
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `regions` | list[string] | Yes | — | Region set, e.g. `["US/Eastern", "Europe/London", "Asia/Shanghai"]` |
| `duration` | integer | Yes | — | Meeting duration in minutes |
| `preferred_hours` | object | No | — | Per-region preferred local hour ranges, e.g. `{"US/Eastern": [9, 17]}` |

**Region format:** Use IANA timezone names (e.g., `US/Eastern`, `Europe/London`, `Asia/Shanghai`) for precise mapping. Short aliases like `"US"` or `"EU"` are accepted but will be mapped to a representative timezone with a note.

## Region Alias Mapping

| Alias | Mapped To | Note |
|-------|-----------|------|
| `US` | `US/Eastern` | Representative only; specify sub-region for accuracy |
| `EU` | `Europe/London` | Representative only; specify country for accuracy |
| `Asia` | `Asia/Shanghai` | Representative only; specify city for accuracy |

## Output

- Suggested meeting windows by region
- Local-time mapping for each included region
- DST assumption notes when applicable
- Tradeoff summary for each candidate window

## Scope Boundaries

- This skill supports scheduling recommendations, not calendar booking.
- This skill does not validate current DST status from live internet sources.
- This skill does not decide business priority between teams without user-supplied rules.
- Manual confirmation is required before sending invites.

## Stress-Case Rules

For multi-constraint requests, always include these explicit blocks:

1. Assumptions
2. Hard Constraints
3. Recommended Window
4. Tradeoffs
5. Risks and Manual Checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate live calendar availability or confirmed participant agreement.

## Input Validation

This skill accepts: a list of participant regions and a meeting duration for cross-timezone scheduling recommendations.

If the request does not involve cross-timezone meeting planning — for example, asking to book calendar events, check live availability, make travel arrangements, or provide legal scheduling advice — do not proceed with the workflow. Instead respond:
> "time-zone-planner is designed to recommend meeting windows across time zones for distributed teams. Your request appears to be outside this scope. Please provide a region list and meeting duration, or use a more appropriate tool."

## References

- [references/guidelines.md](references/guidelines.md) — General time-zone planning notes
- [references/audit-reference.md](references/audit-reference.md) — Supported scope, audit commands, and fallback boundaries

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.
