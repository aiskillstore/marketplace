# Email Deliverability Skill Operating Checklist

Use this checklist when the request involves inbox placement, authentication, sender reputation, complaint control, and remediation workflows or could affect a live email system.

## Intake

- Sending domains, envelope domains, tracking domains, and provider
- SPF, DKIM, DMARC, bounce, complaint, unsubscribe, open, click, and delivery trends
- Recent imports, list sources, reactivation sends, or volume changes
- Mailbox provider patterns such as Gmail, Outlook, Yahoo, Apple, or corporate filters
- Screenshots or exports from postmaster tools, ESP reports, and blocklist checks

## QA

- Confirm SPF, DKIM, and DMARC alignment are evaluated separately.
- Confirm complaint and bounce rates are segmented by source and campaign.
- Confirm high-risk sends are paused before reputation worsens.
- Confirm remediation steps have thresholds for continue, slow, or stop.
- Confirm DNS or suppression changes require explicit approval before execution.

## Risk Gates

Low risk: research, summaries, drafts, critiques, naming, and non-production recommendations.

Medium risk: template edits, segment recommendations, automation diagrams, experiments, imports prepared for review, and code changes that need deployment.

High risk: live sends, contact imports, suppression edits, DNS/authentication changes, production automation changes, provider migrations, and destructive cleanup. Stop and request explicit approval before high-risk actions.
