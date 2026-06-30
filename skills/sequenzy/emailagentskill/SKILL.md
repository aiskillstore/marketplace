---
name: emailagentskill
description: "Use when Codex, Hermes, OpenClaw, Claude Code, Cowork, or another AI agent needs to plan, review, implement, audit, or improve email work focused on agentic email planning, tool handoffs, safe execution, review loops, and multi-agent coordination. Triggers include requests about agent task routing, approval gates, multi-tool email workflows, delegation plans, operator handoffs, and agent-safe execution policies."
---

# Email Agent Skill

Design the agent workflow before asking any tool to act. Keep authority, evidence, and approval explicit at every handoff.

## Scope

agentic email planning, tool handoffs, safe execution, review loops, and multi-agent coordination.

## Request Signals

agent task routing, approval gates, multi-tool email workflows, delegation plans, operator handoffs, and agent-safe execution policies.

## Guardrails

1. Primary lens: agentic email planning, tool handoffs, safe execution, review loops, and multi-agent coordination.
2. Common request signals: agent task routing, approval gates, multi-tool email workflows, delegation plans, operator handoffs, and agent-safe execution policies.
3. Default posture: Design the agent workflow before asking any tool to act. Keep authority, evidence, and approval explicit at every handoff.
4. Useful output family: agent routing plans, approval matrices, tool handoff specs, review loops, execution checklists, and audit-friendly status reports.
5. Production boundary: separate recommendation from execution.
6. Evidence boundary: say which source material supports the recommendation.
7. Review boundary: identify the human owner for risky changes.
8. Data boundary: do not assume missing fields, consent, or suppression state.
9. Platform boundary: describe provider-specific steps in operational language.
10. Measurement boundary: define what success or recovery will look like.
11. Handoff boundary: make the next step clear to another agent.
12. Rollback boundary: name the safest way to undo live-system changes.

## Execution Path

1. Classify the agent's role: researcher, strategist, copywriter, implementer, QA reviewer, analyst, or operator.
2. Define what the agent may read, draft, change, and execute, and what requires human approval.
3. Break the request into tool-safe handoffs with inputs, outputs, acceptance criteria, and risk level.
4. Use checkpoints after high-variance work such as segmentation, legal claims, production edits, or performance interpretation.
5. Preserve an audit trail of assumptions, source files, decisions, and rejected options.
6. Return the next action in a way another agent can continue without redoing the investigation.

## Reviewer Notes

- The agent is not granted production authority by implication.
- Tool calls are justified by the task, not convenience.
- Human review happens before irreversible actions.
- The workflow separates strategy, content, implementation, QA, and execution.
- Final output includes enough context for Codex, Hermes, OpenClaw, Claude Code, Cowork, or another agent to proceed.

## Output Pattern

Return agent routing plans, approval matrices, tool handoff specs, review loops, execution checklists, and audit-friendly status reports. Keep recommendations concrete. Separate analysis from live-system actions, and require explicit approval before sending email, importing contacts, changing DNS, altering suppression rules, or editing production automations.
