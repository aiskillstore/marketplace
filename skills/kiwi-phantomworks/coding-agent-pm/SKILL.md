---
name: coding-agent-pm
description: Plan, assign, review, and verify coding-agent work with tight scope control and clear acceptance criteria.
version: 1.0.1
author: Bridge AI Labs
license: MIT
tags:
  - coding-agents
  - product-management
  - agent-workflows
  - code-review
---

# Coding Agent PM

Use this skill when a human is preparing, delegating, reviewing, or recovering implementation work done by Claude Code, Codex, OpenClaw, or another coding agent.

## Operating Loop

1. Define the shipped outcome in one sentence.
2. Set explicit scope: files or modules owned, files or modules excluded, and any destructive actions that are forbidden.
3. Capture the relevant context before implementation starts.
4. Write acceptance criteria that can be checked directly.
5. Require validation commands or manual checks before final delivery.
6. Review the diff before accepting the work.

## Assignment Rules

- Keep the task brief concrete and bounded.
- State whether the agent may edit files or should only inspect and plan.
- Give ownership boundaries for code changes.
- Tell the agent not to revert unrelated user work.
- Prefer existing project patterns over new abstractions.
- Require the final response to include changed files, checks run, results, and remaining risks.

## Review Rules

Prioritize findings in this order:

1. Behavioral bugs or regressions.
2. Missing acceptance criteria.
3. Missing tests or weak validation.
4. Scope drift and unrelated refactors.
5. Security, privacy, or destructive-command risk.

If the agent drifted, stop new edits and ask it to map each change back to the original acceptance criteria.

## Templates

Use the templates in `templates/` when a structured artifact is helpful:

- `pm-agent-brief.md`
- `task-plan-template.md`
- `prompt-snippets.md`
- `review-checklist.md`
- `first-week-agent-workflow-tracker.md`
