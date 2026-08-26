# Author Feature Issue

## When to use

Use this agent mode when the request is for a new capability or enhancement.

## When not to use

Do not use this agent mode for bugs, user stories centered on role narratives, or generic technical tasks.

## Required inputs

- Feature intent and value
- Scope and non-goals
- Success criteria

## Instructions

1. Confirm routed type is `Feature`.
2. Draft locally in `.tmp/FEATURE-<context>.md`.
3. Structure draft with:
   - Story/problem statement
   - Scope (in/out)
   - Functional requirements
   - Acceptance criteria
   - Dependencies/risks
4. Check that scope boundaries and non-goals are explicit.
5. Return draft summary for orchestrator review/publish flow.

Template fallback:
- `assets/issue-templates/feature.md`

## Expected output

- Draft file path in `.tmp/`
- Proposed title/body summary
- Feature-specific scope and acceptance summary

## Safety & constraints

Do not perform mutation directly; mutation stays in the orchestrator flow (`SKILL.md`).
