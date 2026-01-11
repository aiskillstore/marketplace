# BPS Trello Board Conventions

> Reference document for BPS AI Software Trello board conventions.
> This is a project-specific reference that complements the generic skill.

---

## Protected Cards (NEVER MOVE)

The **"Info"** list contains dashboard/header cards that must NEVER be touched:
- Weekly Completed, Frontend Completed, Backend Completed
- Worker/Function Completed, Aging WIP, Board Setup
- Any card with colored counter backgrounds

**Rule:** If a card is in the "Info" list, leave it alone.

---

## Required Custom Fields

When creating or completing cards, always set:

| Field | When | Example |
|-------|------|---------|
| **Project** | On creation | "Support App", "PairCoder" |
| **Stack** | On creation | "React", "Python", "Flask" |
| **Repo URL** | On creation | `https://github.com/org/repo` |
| **Effort** | On creation | XS, S, M, L, XL |
| **PR URL** | When PR created | `https://github.com/org/repo/pull/123` |

---

## Acceptance Criteria Workflow

**CRITICAL:** Always check all acceptance criteria before completing a task.

Use `ttask done` which auto-checks all items:

```bash
bpsai-pair ttask done TRELLO-XX --summary "What was done" --list "Deployed/Done"
```

**DO NOT** manually move cards to Done without checking acceptance criteria.

---

## PR URL Workflow

When creating a pull request:

1. Add PR URL to the Trello card:
   ```bash
   bpsai-pair ttask update TRELLO-XX --pr-url "https://github.com/org/repo/pull/123"
   ```

2. Include Trello link in PR description:
   ```markdown
   ## Related
   - Trello: https://trello.com/c/shortId
   ```

---

## Effort Sizing Guide

| Size | Time Estimate | Complexity Range |
|------|---------------|------------------|
| XS | < 1 hour | 0-10 |
| S | 1-4 hours | 11-25 |
| M | 4-8 hours (half to full day) | 26-50 |
| L | 1-2 days | 51-75 |
| XL | 3+ days | 76+ |

---

## Common Mistakes to Avoid

| Mistake | Correct Action |
|---------|----------------|
| Moving Info list cards | Never touch Info list cards |
| Leaving custom fields empty | Always set Project, Stack, Repo URL, Effort |
| Moving to Done without checking AC | Use `ttask done` to auto-check criteria |
| Not adding PR URL | Add PR URL when creating pull request |
| Using `task update --status done` only | Use `ttask done` first, then `task update` |
