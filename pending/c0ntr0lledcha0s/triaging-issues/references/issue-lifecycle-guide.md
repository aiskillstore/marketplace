# Issue Lifecycle Guide

## Issue States

```
Created → Triaged → Ready → In Progress → In Review → Done
                     ↓           ↓
                  Blocked     On Hold
```

## State Definitions

| State | Description | Entry Criteria | Exit Criteria |
|-------|-------------|----------------|---------------|
| Created | New issue submitted | Issue opened | Triage complete |
| Triaged | Analyzed and categorized | Labels assigned | Requirements clear |
| Ready | Ready for development | Acceptance criteria defined | Work started |
| In Progress | Being worked on | Assigned to developer | PR submitted |
| In Review | PR under review | PR opened | PR approved |
| Done | Completed | PR merged | Issue closed |
| Blocked | Cannot proceed | Dependency identified | Blocker resolved |
| On Hold | Paused | External factor | Factor resolved |

## Triage Process

1. **Read** - Understand the issue content
2. **Classify** - Determine type (bug/feature/enhancement)
3. **Prioritize** - Assess urgency and impact
4. **Duplicate Check** - Search for similar issues
5. **Validate** - Verify claims in codebase
6. **Label** - Apply type, priority, scope labels
7. **Assign** - Route to appropriate owner
8. **Respond** - Provide triage summary

## Required Labels

Every triaged issue needs:
- **Type**: bug, enhancement, feature, documentation, refactor, chore
- **Priority**: priority:high, priority:medium, priority:low

## Relationship Types

- **Parent**: Epic this issue belongs to
- **Blocked by**: Issues that must complete first
- **Related**: Issues with similar scope

## Closure Criteria

Issues should only be closed when:
- PR merged (for code changes)
- Documentation updated (for doc issues)
- Confirmed by reporter (for bugs)
- All acceptance criteria met
