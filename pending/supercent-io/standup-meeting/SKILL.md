---
name: standup-meeting
description: Conduct effective daily standup meetings for agile teams. Use when facilitating standups, tracking blockers, or improving team synchronization. Handles standup format, time management, and blocker resolution.
metadata:
  tags: standup, daily-scrum, agile, team-sync, blockers
  platforms: Claude, ChatGPT, Gemini
---


# Standup Meeting


## When to use this skill

- **Daily**: same time, same place
- **During a sprint**: when team sync is needed
- **Remote teams**: async standup

## Instructions

### Step 1: 3 Questions Format

```markdown
## Daily Standup Template

**Date**: 2025-01-15
**Time**: 9:30 AM
**Duration**: 15 minutes

### Team Member A
- **Yesterday**:
  - Completed user authentication API (#123)
  - 2 code reviews
- **Today**:
  - Implement JWT refresh token (#124)
  - Write unit tests
- **Blockers**:
  - Need Redis setup docs (ask Team Member B for help)

### Team Member B
- **Yesterday**:
  - Frontend form validation (#125)
- **Today**:
  - Implement profile page UI (#126)
- **Blockers**: None

### Team Member C
- **Yesterday**:
  - Database migration (#127)
  - Performance testing
- **Today**:
  - Index optimization (#128)
- **Blockers**:
  - Need production DB access (urgent)

### Action Items
1. [ ] Team Member B shares Redis docs with Team Member A (Today 10:00)
2. [ ] Team lead requests DB access for Team Member C (Today)
```

### Step 2: Walking the Board (Board-Based)

```markdown
## Standup: Walking the Board

**Sprint Goal**: Complete user authentication system

### In Progress
- #123: User Login API (Team Member A, 80% done)
- #124: Refresh Token (Team Member A, planned)
- #125: Form Validation (Team Member B, 90% done)

### Blocked
- #127: DB Migration (Team Member C)
  - **Blocker**: Access needed
  - **Owner**: Team Lead
  - **ETA**: This afternoon

### Ready for Review
- #122: Password Reset (Team Member D)
  - Need reviewer

### Done
- #120: Email Service Integration
- #121: User Registration

### Sprint Progress
- **Completed**: 12 points
- **Remaining**: 13 points
- **On Track**: Yes ✅
```

### Step 3: Async Standup (Remote Teams)

**Slack template**:
```markdown
[Daily Update - 2025-01-15]

**Yesterday**
- Completed user authentication flow
- Fixed bug in password validation

**Today**
- Implementing JWT refresh tokens
- Writing unit tests

**Blockers**
- None

**Sprint Progress**
- 8/13 story points completed
```

## Output format

### Standup Minutes

```markdown
# Daily Standup - 2025-01-15

**Attendees**: 5/5
**Duration**: 12 minutes
**Sprint**: Sprint 10 (Day 3/10)

## Summary
- Stories Completed: 2 (5 points)
- Stories In Progress: 3 (8 points)
- Blockers: 1 (DB access permission)

## Individual Updates
[Refer to the 3 Questions format above]

## Action Items
1. Team lead: Request DB access (High priority)
2. Team Member B: Share Redis docs
3. Team Member D: Assign reviewer for PR #122

## Notes
- Sprint goal on track
- Team morale: High
```

## Constraints

### Required Rules (MUST)

1. **Time-boxed**: within 15 minutes
2. **Same time**: consistent time every day
3. **Everyone participates**: every team member gives an update

### Prohibited (MUST NOT)

1. **Problem Solving**: Do not solve problems in the standup
2. **Status Report**: Not a status report to management
3. **Late Start**: Start on time

## Best practices

1. **Stand Up**: Actually stand up (keep it short)
2. **Parking Lot**: Deep discussion goes to a separate time
3. **Visualize**: Run it while looking at the board

## References

- [Scrum Guide - Daily Scrum](https://scrumguides.org/)
- [15 Minute Stand-up](https://www.mountaingoatsoftware.com/agile/scrum/meetings/daily-scrum)

## Metadata

### Version
- **Current version**: 1.0.0
- **Last updated**: 2025-01-01
- **Supported platforms**: Claude, ChatGPT, Gemini

### Tags
`#standup` `#daily-scrum` `#agile` `#team-sync` `#project-management`

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
