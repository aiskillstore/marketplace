# Drip Campaign Skill Operating Checklist

Use this checklist when the request involves time-based nurture streams, branching logic, lead scoring hooks, and conversion analysis or could affect a live email system.

## Intake

- Entry source, segment, offer, and desired conversion
- Current sequence steps, delays, branches, and exit rules
- Message-level metrics by source and segment
- Lead scoring model, sales SLA, or qualification criteria
- Known objections, proof assets, and lifecycle constraints

## QA

- Confirm the first email acknowledges the entry context.
- Confirm delays match decision complexity and buying cycle.
- Confirm branches use observable behavior or data.
- Confirm handoff criteria are specific enough for another team to trust.
- Confirm sequence changes include a measurement plan.

## Risk Gates

Low risk: research, summaries, drafts, critiques, naming, and non-production recommendations.

Medium risk: template edits, segment recommendations, automation diagrams, experiments, imports prepared for review, and code changes that need deployment.

High risk: live sends, contact imports, suppression edits, DNS/authentication changes, production automation changes, provider migrations, and destructive cleanup. Stop and request explicit approval before high-risk actions.
