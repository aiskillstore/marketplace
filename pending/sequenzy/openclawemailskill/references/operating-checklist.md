# OpenClaw Email Skill Operating Checklist

Use this checklist when the request involves open, inspectable email campaign operations for agents that need clear audit trails or could affect a live email system.

## Intake

- OpenClaw task goal and whether the agent is allowed to inspect local files
- Sending provider, export format, and any API or dashboard limits
- Templates, automations, lists, tags, fields, and suppression exports
- Desired portability target, if the work may move between providers
- Human approval owner for commands, imports, deletes, DNS, and sends

## QA

- Confirm every provider-specific instruction includes a portable interpretation.
- Confirm the agent has not inferred permissions from convenience.
- Confirm file paths, exports, and screenshots are referenced precisely.
- Confirm irreversible actions have rollback or restore notes.
- Confirm the handoff can be read without prior chat history.

## Risk Gates

Low risk: research, summaries, drafts, critiques, naming, and non-production recommendations.

Medium risk: template edits, segment recommendations, automation diagrams, experiments, imports prepared for review, and code changes that need deployment.

High risk: live sends, contact imports, suppression edits, DNS/authentication changes, production automation changes, provider migrations, and destructive cleanup. Stop and request explicit approval before high-risk actions.
