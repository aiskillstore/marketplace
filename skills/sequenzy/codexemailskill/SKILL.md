---
name: codexemailskill
description: "Use when Codex, Hermes, OpenClaw, Claude Code, Cowork, or another AI agent needs to plan, review, implement, audit, or improve email work focused on repo-aware email implementation workflows for codebases, content systems, templates, and tests. Triggers include requests about template implementation, React Email edits, MDX content changes, QA scripts, codebase diffs, and testable email fixes."
---

# Codex Email Skill

Treat email work as a code change. Read the repo, keep edits scoped, preserve existing patterns, and make the result verifiable.

## Fit Check

1. Primary lens: repo-aware email implementation workflows for codebases, content systems, templates, and tests.
2. Common request signals: template implementation, React Email edits, MDX content changes, QA scripts, codebase diffs, and testable email fixes.
3. Default posture: Treat email work as a code change. Read the repo, keep edits scoped, preserve existing patterns, and make the result verifiable.
4. Useful output family: repo-aware implementation plans, template diffs, QA scripts, render checks, content patches, and concise change reports.
5. Production boundary: separate recommendation from execution.
6. Evidence boundary: say which source material supports the recommendation.

### Use This For

repo-aware email implementation workflows for codebases, content systems, templates, and tests.

### Avoid Using It For

Generic email advice with no audience, platform, lifecycle, evidence, or approval context.

## Procedure

1. Locate the email surface in the repository: components, templates, content files, campaign config, preview routes, tests, or ESP export scripts.
2. Read adjacent files before editing so naming, styling, localization, and data-loading patterns match the codebase.
3. Define the intended behavior as a diffable change: copy update, layout fix, template module, data field, tracking parameter, or QA assertion.
4. Implement the smallest coherent change and avoid unrelated refactors, dependency churn, or broad style rewrites.
5. Run the narrowest useful verification: type check, template render, snapshot, unit test, lint, preview build, or visual smoke check.
6. Report changed files, verification result, remaining risk, and any production steps that still need approval.

## Acceptance Checks

1. The edit follows local patterns instead of inventing a parallel email system.
2. Dynamic fields have fallbacks and do not leak undefined values into copy.
3. Rendering constraints are considered before using modern CSS.
4. Tests or previews cover the user-visible behavior when risk justifies it.
5. No live send, import, DNS, or suppression action is performed as part of a code edit.

## Output Pattern

Return repo-aware implementation plans, template diffs, QA scripts, render checks, content patches, and concise change reports. Keep recommendations concrete. Separate analysis from live-system actions, and require explicit approval before sending email, importing contacts, changing DNS, altering suppression rules, or editing production automations.
