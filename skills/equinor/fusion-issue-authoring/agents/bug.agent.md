# Author Bug Issue

## When to use

Use this agent mode when the request is about broken behavior, regressions, crashes, or unexpected results.

## When not to use

Do not use this agent mode for feature requests, user stories, or generic enablement tasks.

## Required inputs

- Bug context (observed behavior, expected behavior, impact)
- Reproduction information (if available)
- Environment context

## Instructions

1. Confirm routed type is `Bug`.
2. Draft locally in `.tmp/BUG-<context>.md`.
3. Structure draft with:
   - Description
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment
   - Impact
4. Validate the draft has enough reproduction detail for triage.
5. Return the draft summary for orchestrator review/publish flow.

Template fallback:
- `assets/issue-templates/bug.md`

## Expected output

- Draft file path in `.tmp/`
- Proposed title/body summary
- Bug-specific triage notes (repro clarity + impact)

## Safety & constraints

Do not perform mutation directly; mutation stays in the orchestrator flow (`SKILL.md`).
