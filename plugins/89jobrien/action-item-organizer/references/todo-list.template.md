---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: action-item-organizer
---

# TO-DO List

**Project:** {{PROJECT_NAME}}
**Last Updated:** {{DATE}}
**Owner:** {{OWNER}}

---

## Quick Stats

| Status | Count |
|--------|-------|
| Active | {{N}} |
| Completed | {{N}} |
| Blocked | {{N}} |

---

## Active Tasks

### P0 - Critical (Do First)

- [ ] **{{TASK_TITLE}}** `{{LABEL}}`
  - Due: {{DATE}}
  - Context: {{BRIEF_CONTEXT}}
  - Blocked by: {{DEPENDENCY}} (if applicable)

### P1 - High Priority

- [ ] **{{TASK_TITLE}}** `{{LABEL}}`
  - Due: {{DATE}}
  - Context: {{BRIEF_CONTEXT}}

### P2 - Medium Priority

- [ ] **{{TASK_TITLE}}** `{{LABEL}}`
  - Context: {{BRIEF_CONTEXT}}

### P3 - Low Priority / Backlog

- [ ] **{{TASK_TITLE}}** `{{LABEL}}`
  - Context: {{BRIEF_CONTEXT}}

---

## In Progress

| Task | Started | Owner | Progress |
|------|---------|-------|----------|
| {{TASK}} | {{DATE}} | {{OWNER}} | {{N}}% |

---

## Blocked

| Task | Blocked By | Since | Action Needed |
|------|------------|-------|---------------|
| {{TASK}} | {{BLOCKER}} | {{DATE}} | {{ACTION}} |

---

## Completed

### {{WEEK_OR_SPRINT}}

- [x] ~~{{COMPLETED_TASK}}~~ `{{LABEL}}` - {{COMPLETION_DATE}}
- [x] ~~{{COMPLETED_TASK}}~~ `{{LABEL}}` - {{COMPLETION_DATE}}

### Previous

<details>
<summary>{{PREVIOUS_PERIOD}} ({{N}} tasks)</summary>

- [x] ~~{{TASK}}~~ - {{DATE}}
- [x] ~~{{TASK}}~~ - {{DATE}}

</details>

---

## Labels

| Label | Meaning |
|-------|---------|
| `bug` | Bug fix |
| `feature` | New feature |
| `refactor` | Code improvement |
| `docs` | Documentation |
| `test` | Testing |
| `infra` | Infrastructure |
| `security` | Security related |

---

## Notes

{{ADDITIONAL_CONTEXT_OR_DECISIONS}}

---

## Archive Format

When archiving completed tasks, move to:
`/docs/archive/todos-{{YYYY-MM}}.md`
