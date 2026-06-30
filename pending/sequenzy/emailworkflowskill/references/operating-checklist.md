# Email Workflow Skill Operating Checklist

Use this checklist when the request involves workflow maps, lifecycle routing, trigger ownership, and agent-readable operating paths or could affect a live email system.

## Intake

- Current lifecycle stage definitions and who owns them
- Events, fields, lists, tags, and CRM stages that can enroll or suppress a contact
- Screenshots or exports of the existing workflow map
- Recent examples of contacts who received the wrong message or missed a message
- Any blackout windows, frequency caps, consent rules, or sales handoff rules

## QA

- Confirm every trigger has one source of truth and a named fallback.
- Confirm each wait step has a business reason and a maximum acceptable delay.
- Confirm exits prevent stale contacts from continuing through the wrong path.
- Confirm suppression and unsubscribe logic apply before message selection.
- Confirm reporting can show enrollment, branch split, drop-off, and conversion by path.

## Risk Gates

Low risk: research, summaries, drafts, critiques, naming, and non-production recommendations.

Medium risk: template edits, segment recommendations, automation diagrams, experiments, imports prepared for review, and code changes that need deployment.

High risk: live sends, contact imports, suppression edits, DNS/authentication changes, production automation changes, provider migrations, and destructive cleanup. Stop and request explicit approval before high-risk actions.
