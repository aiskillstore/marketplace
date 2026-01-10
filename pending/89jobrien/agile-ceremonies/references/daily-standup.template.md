---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: agile-ceremonies
---

# Daily Standup Template

**Date:** {{DATE}}
**Sprint:** {{SPRINT_NUMBER}}
**Team:** {{TEAM_NAME}}

---

## Status Update Format

### Individual Update

```markdown
## {{NAME}}

### Yesterday
- {{COMPLETED_TASK_1}}
- {{COMPLETED_TASK_2}}

### Today
- {{PLANNED_TASK_1}}
- {{PLANNED_TASK_2}}

### Blockers
- {{BLOCKER_1}} (need: {{WHAT_NEEDED}})
- None
```

---

## Team Standup Template

```markdown
# Standup - {{DATE}}

## Team Status

| Member | Yesterday | Today | Blockers |
|--------|-----------|-------|----------|
| {{NAME}} | {{COMPLETED}} | {{PLANNED}} | {{BLOCKER}} |

## Key Updates

### Completed
- [x] {{MAJOR_COMPLETION}}

### In Progress
- [ ] {{ACTIVE_WORK}} ({{PERCENT}}%)

### Blocked
- [ ] {{BLOCKED_ITEM}} - Waiting on: {{DEPENDENCY}}

## Action Items

| Item | Owner | Due |
|------|-------|-----|
| {{ACTION}} | {{OWNER}} | {{DATE}} |

## Notes

{{ADDITIONAL_CONTEXT}}
```

---

## Async Standup (Slack/Discord)

```markdown
**Standup - {{DATE}}**

✅ **Done:**
• {{COMPLETED_1}}
• {{COMPLETED_2}}

🔄 **Today:**
• {{PLANNED_1}}
• {{PLANNED_2}}

🚧 **Blockers:**
• {{BLOCKER}} (need help from @{{PERSON}})
```

---

## Sprint Progress Template

```markdown
# Sprint {{NUMBER}} Progress

**Period:** {{START_DATE}} - {{END_DATE}}
**Day:** {{DAY_NUMBER}} of {{TOTAL_DAYS}}

## Burndown

| Day | Planned | Actual | Remaining |
|-----|---------|--------|-----------|
| {{N}} | {{PTS}} | {{PTS}} | {{PTS}} |

## Story Status

| Story | Points | Status | Owner |
|-------|--------|--------|-------|
| {{STORY_ID}}: {{TITLE}} | {{PTS}} | {{STATUS}} | {{OWNER}} |

### Status Legend
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔵 In Review
- ⚫ Blocked

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| {{RISK}} | {{HIGH/MED/LOW}} | {{ACTION}} |

## Decisions Needed

- [ ] {{DECISION_1}}
- [ ] {{DECISION_2}}
```

---

## Weekly Summary Template

```markdown
# Week {{NUMBER}} Summary

**Period:** {{START}} - {{END}}

## Accomplishments

### Shipped
- {{FEATURE_1}}
- {{FEATURE_2}}

### Progress
- {{WIP_1}} ({{PERCENT}}%)

## Metrics

| Metric | This Week | Last Week | Trend |
|--------|-----------|-----------|-------|
| Velocity | {{PTS}} | {{PTS}} | {{↑/↓}} |
| Bugs Fixed | {{N}} | {{N}} | {{↑/↓}} |
| PRs Merged | {{N}} | {{N}} | {{↑/↓}} |

## Learnings

- {{LEARNING_1}}
- {{LEARNING_2}}

## Next Week Focus

1. {{PRIORITY_1}}
2. {{PRIORITY_2}}
```

---

## Quality Checklist

- [ ] Updates are specific and measurable
- [ ] Blockers include what's needed to unblock
- [ ] Action items have owners and dates
- [ ] Progress is quantified where possible
- [ ] Risks are identified proactively
