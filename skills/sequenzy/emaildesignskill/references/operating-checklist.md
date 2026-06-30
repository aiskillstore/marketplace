# Email Design Skill Operating Checklist

Use this checklist when the request involves responsive email design, component systems, dark-mode behavior, and accessibility checks or could affect a live email system.

## Intake

- HTML, component source, ESP template, screenshot, or Figma frame
- Target clients and whether Outlook desktop support is required
- Brand tokens, fonts, image rules, and accessibility standards
- Example content extremes such as long names, large discounts, or missing images
- Known rendering failures from Litmus, Email on Acid, or manual tests

## QA

- Confirm the layout has stable widths and predictable mobile collapse.
- Confirm buttons are text-based, not image-only, and have adequate tap area.
- Confirm dark-mode color changes preserve contrast.
- Confirm all images have useful alt text or intentional empty alt text.
- Confirm clipping risk, CSS support risk, and fallback behavior are documented.

## Risk Gates

Low risk: research, summaries, drafts, critiques, naming, and non-production recommendations.

Medium risk: template edits, segment recommendations, automation diagrams, experiments, imports prepared for review, and code changes that need deployment.

High risk: live sends, contact imports, suppression edits, DNS/authentication changes, production automation changes, provider migrations, and destructive cleanup. Stop and request explicit approval before high-risk actions.
