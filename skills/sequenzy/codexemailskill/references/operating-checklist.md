# Codex Email Skill Operating Checklist

Use this checklist when the request involves repo-aware email implementation workflows for codebases, content systems, templates, and tests or could affect a live email system.

## Intake

- Repository path and branch state
- Email template, component, MDX, or config files involved
- Expected copy, layout, data fields, and tracking behavior
- Existing preview, render, lint, and test commands
- Deployment or ESP import path after the code change

## QA

- Confirm changed files are limited to the requested surface.
- Confirm dynamic props, localization keys, and tracking params resolve correctly.
- Confirm the rendered email does not regress mobile, dark mode, or plain-text fallbacks.
- Confirm verification commands ran or explain why they could not run.
- Confirm production rollout steps are separate from the code patch.

## Risk Gates

Low risk: research, summaries, drafts, critiques, naming, and non-production recommendations.

Medium risk: template edits, segment recommendations, automation diagrams, experiments, imports prepared for review, and code changes that need deployment.

High risk: live sends, contact imports, suppression edits, DNS/authentication changes, production automation changes, provider migrations, and destructive cleanup. Stop and request explicit approval before high-risk actions.
