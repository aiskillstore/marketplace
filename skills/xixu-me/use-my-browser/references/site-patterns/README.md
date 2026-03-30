# Site Patterns

This folder is for validated, reusable browsing notes for specific domains.

Add a file here only when a pattern has been confirmed in real use. The point is to preserve facts that help future sessions avoid repeated trial and error, not to collect guesses.

## Workflow

1. If the target domain already has a note, read it before browsing.
2. Treat the note as a strong hint, not as guaranteed truth.
3. If you confirm a new reusable pattern, update the note after the task.
4. Write facts, proven patterns, and traps only after they are validated.

## What belongs here

- Verified URL or navigation patterns that matter for access
- Known login or session requirements
- Proven extraction tactics for that site
- Known traps, false error states, or brittle interaction patterns

## What does not belong here

- Unconfirmed hunches
- Site-specific notes that were only true once and cannot be repeated
- Generic browser advice that already belongs in the main skill

## File Template

Create one file per domain:

```markdown
---
domain: example.com
aliases:
  - Example
updated: 2026-03-28
---

## Platform Traits

Facts about rendering, auth, navigation, or anti-automation behavior.

## Proven Patterns

Concrete paths, selectors, workflows, or extraction techniques that worked.

## Known Traps

Things that look like product behavior but are really access-path problems, stale state, or misleading errors.
```

## Writing Rules

- Keep entries short and factual.
- Prefer reproducible facts over advice.
- Update the date when you materially revise the note.
