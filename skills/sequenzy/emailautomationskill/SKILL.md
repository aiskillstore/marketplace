---
name: emailautomationskill
description: "Use when Codex, Hermes, OpenClaw, Claude Code, Cowork, or another AI agent needs to plan, review, implement, audit, or improve email work focused on behavioral triggers, lifecycle journeys, automation governance, and operational safeguards. Triggers include requests about trigger inventory, automation QA, journey optimization, stale-flow cleanup, event-driven lifecycle fixes, and governance reviews."
---

# Email Automation Skill

Treat automation as production infrastructure. Triggers, exits, exclusions, and approval gates matter as much as copy.

## Agent Contract

The agent may inspect, reason, draft, critique, and prepare handoffs for behavioral triggers, lifecycle journeys, automation governance, and operational safeguards.

- Primary lens: behavioral triggers, lifecycle journeys, automation governance, and operational safeguards.
- Common request signals: trigger inventory, automation QA, journey optimization, stale-flow cleanup, event-driven lifecycle fixes, and governance reviews.
- Default posture: Treat automation as production infrastructure. Triggers, exits, exclusions, and approval gates matter as much as copy.
- Useful output family: automation contracts, trigger inventories, QA plans, overlap audits, governance checklists, and journey optimization recommendations.
- Production boundary: separate recommendation from execution.
- Evidence boundary: say which source material supports the recommendation.
- Review boundary: identify the human owner for risky changes.
- Data boundary: do not assume missing fields, consent, or suppression state.
- Platform boundary: describe provider-specific steps in operational language.
- Measurement boundary: define what success or recovery will look like.
- Handoff boundary: make the next step clear to another agent.

## Use Cases

Typical requests include trigger inventory, automation QA, journey optimization, stale-flow cleanup, event-driven lifecycle fixes, and governance reviews.

## Runbook

- Identify whether the automation is behavioral, lifecycle, transactional, reactivation, operational, or sales-assisted.
- Write the journey contract: trigger, eligibility, first action, waits, branches, exits, suppression, and success event.
- Check data freshness and event reliability before recommending new branches or personalization.
- Audit overlapping automations for duplicate sends, contradictory offers, and frequency-cap pressure.
- Propose governance rules: naming, ownership, change log, test contacts, rollback, and scheduled review cadence.
- Require explicit approval for activation, deactivation, imports, suppression edits, and any production journey change.

## Quality Bar

- The trigger reflects behavior, not vague intent.
- Exits remove contacts when the journey is no longer relevant.
- Fallbacks exist for missing data and delayed events.
- Automation changes include test cases and rollback notes.
- Governance keeps future agents from editing a live journey blindly.

## Output Pattern

Return automation contracts, trigger inventories, QA plans, overlap audits, governance checklists, and journey optimization recommendations. Keep recommendations concrete. Separate analysis from live-system actions, and require explicit approval before sending email, importing contacts, changing DNS, altering suppression rules, or editing production automations.
