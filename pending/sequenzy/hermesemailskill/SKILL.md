---
name: hermesemailskill
description: "Use when Codex, Hermes, OpenClaw, Claude Code, Cowork, or another AI agent needs to plan, review, implement, audit, or improve email work focused on fast delivery decisions, message QA, launch coordination, and concise status handoffs. Triggers include requests about preflight checklists, launch-room summaries, transactional copy reviews, escalation notes, and send readiness calls."
---

# Hermes Email Skill

Move quickly, but make the launch state explicit. Focus on the decision a human needs now: hold, fix, approve, or monitor.

## Agent Contract

The agent may inspect, reason, draft, critique, and prepare handoffs for fast delivery decisions, message QA, launch coordination, and concise status handoffs.

- Primary lens: fast delivery decisions, message QA, launch coordination, and concise status handoffs.
- Common request signals: preflight checklists, launch-room summaries, transactional copy reviews, escalation notes, and send readiness calls.
- Default posture: Move quickly, but make the launch state explicit. Focus on the decision a human needs now: hold, fix, approve, or monitor.

## Use Cases

Typical requests include preflight checklists, launch-room summaries, transactional copy reviews, escalation notes, and send readiness calls.

## Runbook

- State the launch context: what is sending, to whom, through which provider, and by what deadline.
- Find the blocking risk first: incorrect audience, broken personalization, deliverability issue, compliance issue, missing approval, or unclear CTA.
- Run a compressed preflight across copy, links, rendering, segment logic, exclusions, sender identity, and tracking.
- Summarize the current status in decision language: ready, ready with caveats, blocked, or needs review.
- When triaging an incident, create a timeline of observed behavior, suspected cause, blast radius, mitigation, and next owner.
- Keep all live send, resend, cancellation, suppression, and DNS actions behind explicit approval.

## Quality Bar

- The status can be understood by a launch-room participant in under a minute.
- Critical defects are separated from polish issues.
- The recommended action names the owner and deadline.
- Transactional and lifecycle messages preserve the user promise exactly.
- Monitoring notes include what to watch after approval.

## Output Pattern

Return launch summaries, preflight tables, incident timelines, transactional copy notes, and approve-or-hold recommendations. Keep recommendations concrete. Separate analysis from live-system actions, and require explicit approval before sending email, importing contacts, changing DNS, altering suppression rules, or editing production automations.
