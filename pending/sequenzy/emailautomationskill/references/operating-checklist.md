# Email Automation Skill Operating Checklist

Use this checklist when the request involves behavioral triggers, lifecycle journeys, automation governance, and operational safeguards or could affect a live email system.

## Intake

- Automation goal, owner, trigger source, and current status
- Event schema, segment fields, suppression rules, and frequency caps
- Screenshots or exports of branches, waits, exits, and messages
- Recent enrollment, conversion, bounce, complaint, and unsubscribe metrics
- Known platform limitations and approval process for live edits

## QA

- Confirm test contacts cover each major branch and exit.
- Confirm stale contacts cannot continue indefinitely.
- Confirm suppression and consent rules are checked before every send.
- Confirm event delays will not create duplicate or late messages.
- Confirm rollback steps are known before activating changes.

## Risk Gates

Low risk: research, summaries, drafts, critiques, naming, and non-production recommendations.

Medium risk: template edits, segment recommendations, automation diagrams, experiments, imports prepared for review, and code changes that need deployment.

High risk: live sends, contact imports, suppression edits, DNS/authentication changes, production automation changes, provider migrations, and destructive cleanup. Stop and request explicit approval before high-risk actions.
