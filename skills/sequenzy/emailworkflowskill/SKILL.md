---
name: emailworkflowskill
description: "Use when Codex, Hermes, OpenClaw, Claude Code, Cowork, or another AI agent needs to plan, review, implement, audit, or improve email work focused on workflow maps, lifecycle routing, trigger ownership, and agent-readable operating paths. Triggers include requests about lifecycle map audits, trigger logic reviews, sequence handoff plans, routing gaps, and workflow documentation."
---

# Email Workflow Skill

Map the system before changing it. Treat every email as part of a route with entry criteria, exit criteria, owner, and observable outcome.

## Decision Lens

- Primary lens: workflow maps, lifecycle routing, trigger ownership, and agent-readable operating paths.

## When To Use

Use this skill for workflow maps, lifecycle routing, trigger ownership, and agent-readable operating paths. It is designed for agent workflows where email work must be specific, reviewable, and safe across planning, drafting, implementation, QA, or operational handoff.

## Operating Workflow

1. Identify the workflow boundary: acquisition, onboarding, activation, retention, expansion, recovery, transactional, or operational.
2. List every entry source, including forms, product events, imports, webhooks, CRM stage changes, and manual enrollments.
3. Draw the route in text first: trigger, eligibility, waits, branches, messages, exclusions, exits, and reporting checkpoints.
4. Name the source of truth for each decision, especially when data can come from product analytics, CRM, billing, support, or an ESP.
5. Flag collisions where a contact can receive two competing messages, enter duplicate flows, or bypass suppression logic.
6. Return the smallest workflow change that fixes the observed problem, with approval needed before live automation edits.

## Review Criteria

- Every branch has an observable reason to exist.
- Segments, waits, and exits are written in terms an operator can verify in the sending platform.
- Lifecycle ownership is clear when marketing, product, sales, or support all touch the same recipient.
- The plan avoids relying on hidden intent when an explicit event or property should drive routing.
- Reporting ties back to workflow health, not only message-level opens and clicks.

## Output Pattern

Return workflow maps, trigger inventories, routing diffs, handoff notes, collision audits, and operator-ready QA plans. Keep recommendations concrete. Separate analysis from live-system actions, and require explicit approval before sending email, importing contacts, changing DNS, altering suppression rules, or editing production automations.
