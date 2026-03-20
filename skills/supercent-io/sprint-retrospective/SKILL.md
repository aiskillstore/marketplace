---
name: sprint-retrospective
description: Facilitate effective sprint retrospectives for continuous team improvement. Use when conducting team retrospectives, identifying improvements, or fostering team collaboration. Handles retrospective formats, action items, and facilitation techniques.
metadata:
  tags: retrospective, agile, scrum, team-improvement, facilitation
  platforms: Claude, ChatGPT, Gemini
---


# Sprint Retrospective


## When to use this skill

- **End of sprint**: at the end of each sprint
- **Project milestone**: after major releases
- **Team issues**: when an immediate retrospective is needed

## Instructions

### Step 1: Start-Stop-Continue

```markdown
## Retrospective Template: Start-Stop-Continue

### START (Start doing)
- Make daily standups shorter (within 5 minutes)
- Use a code review checklist
- Introduce pair programming

### STOP (Stop doing)
- Deploying on Friday afternoons (rollback risk)
- Overusing emergency meetings
- Adding features without documentation

### CONTINUE (Keep doing)
- Weekly tech sharing session
- Automated tests
- Transparent communication

### Action Items
1. [ ] Change standup time from 9:00 → 9:30 (Team Lead)
2. [ ] Write a code review checklist document (Developer A)
3. [ ] Announce the "no Friday deployments" rule (Team Lead)
```

### Step 2: Mad-Sad-Glad

```markdown
## Retrospective: Mad-Sad-Glad

### MAD (What made us mad)
- Urgent bugs after deployment (twice)
- Requirements changed frequently
- Unstable test environment

### SAD (What we wished went better)
- Not enough time for code reviews
- Documentation lagged behind
- Accumulating tech debt

### GLAD (What made us glad)
- New team members onboarded quickly
- CI/CD pipeline stabilized
- Positive customer feedback

### Action Items
- Strengthen the deployment checklist
- Improve the requirements change process
- Reserve documentation time every Friday
```

### Step 3: 4Ls (Liked-Learned-Lacked-Longed For)

```markdown
## Retrospective: 4Ls

### LIKED (What we liked)
- Great teamwork
- Successfully adopted a new tech stack

### LEARNED (What we learned)
- Standardize the local environment with Docker Compose
- Improve server state management with React Query

### LACKED (What we lacked)
- Performance testing
- Mobile support

### LONGED FOR (What we longed for)
- Better developer tools
- External training opportunities

### Action Items
- Automatically measure performance by introducing Lighthouse CI
- Write responsive design guidelines
```

## Output format

### Retrospective document

```markdown
# Sprint [N] Retrospective
**Date**: 2025-01-15
**Participants**: Team Member A, B, C, D
**Format**: Start-Stop-Continue

## What Went Well
- Completed all stories (Velocity: 25 points)
- 0 bugs
- Great team morale

## What Didn't Go Well
- Tech spike took longer than expected
- Rework due to design changes

## Action Items
1. [ ] Assign tech spikes to a dedicated sprint (Team Lead, ~01/20)
2. [ ] Introduce a pre-review process for designs (Designer, ~01/18)
3. [ ] Share the velocity chart (Scrum Master, weekly)

## Key Metrics
- Velocity: 25 points
- Bugs Found: 0
- Sprint Goal Achievement: 100%
```

## Constraints

### Required Rules (MUST)

1. **Safe Space**: a blame-free environment
2. **Action Items**: must be specific and actionable
3. **Follow-up**: check progress in the next retrospective

### Prohibited (MUST NOT)

1. **Personal attacks**: improve the process, not the person
2. **Too many actions**: limit to 2-3

## Best practices

1. **Time-box**: within 1 hour
2. **Rotate Facilitator**: team members take turns facilitating
3. **Celebrate Wins**: celebrate successes too

## References

- [Retrospective Formats](https://retromat.org/)
- [Agile Retrospectives](https://www.amazon.com/Agile-Retrospectives-Making-Teams-Great/dp/0977616649)

## Metadata

### Version
- **Current version**: 1.0.0
- **Last updated**: 2025-01-01
- **Supported platforms**: Claude, ChatGPT, Gemini

### Tags
`#retrospective` `#agile` `#scrum` `#team-improvement` `#project-management`

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
