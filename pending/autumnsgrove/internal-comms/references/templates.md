# Template Library

This guide provides an overview of all available templates and their use cases.

## Available Templates

All complete templates are located in the `examples/` directory:

### Status Report Template
**File**: `examples/status-report-template.md`

**Use for**:
- Weekly engineering updates
- Sprint summaries
- Project status reports
- Team progress tracking

**Key Sections**:
- Sprint progress and velocity
- Completed features/fixes
- Technical challenges
- Infrastructure updates
- Tech debt addressed
- Upcoming work
- Help needed

**Metrics to Include**:
- Sprint velocity
- Deployment frequency
- Incident count
- Response time
- Bug resolution time
- Test coverage
- Technical debt score

### Company Newsletter Template
**File**: `examples/newsletter-template.html`

**Use for**:
- Weekly/monthly company newsletters
- Culture building communications
- Milestone celebrations
- Employee engagement

**Recommended Sections**:
- Header with date and issue number
- Leadership message (monthly)
- Company updates and milestones
- Team spotlight or interview
- New team members
- Employee recognition
- Learning and development
- Upcoming events
- Fun section (photos, memes)
- Footer with links

### All-Hands Announcement Template
**File**: `examples/announcement-template.md`

**Use for**:
- Major company changes
- Strategic updates
- Policy changes
- Important wins or challenges
- Leadership changes

**Standard Structure**:
- Clear subject line
- TL;DR summary
- Context and background
- The announcement (what's changing)
- Why this matters
- What happens next (timeline)
- Action items (if any)
- FAQ section
- Contact for questions

### Team Sprint Update Template
**File**: `examples/team-update-template.md`

**Use for**:
- End of sprint summaries
- Team retrospectives
- Regular team syncs
- Cross-team updates

**Standard Structure**:
- Sprint/period summary
- Wins and accomplishments
- Key metrics
- Learnings and retrospective items
- Upcoming work
- Team health and morale
- Shout-outs and recognition

## Additional Template Patterns

### Product Team Monthly Update

**Structure**:
```markdown
# Product Team Monthly Update - [Month Year]

## Executive Summary
[2-3 sentences on biggest impact this month]

## Product Metrics
| Metric | This Month | Last Month | Change |
|--------|-----------|------------|--------|
| Active Users | X | Y | +Z% |
| Feature Adoption | X% | Y% | +Z% |
| User Satisfaction | X | Y | +Z |

## Feature Launches
### [Feature Name]
- **Launched**: [Date]
- **Adoption**: [X% of users]
- **Impact**: [Key outcome]
- **Feedback**: [Summary]

## User Research & Feedback
- [Key finding from research]
- [Notable user feedback theme]
- [Data-driven insight]

## Roadmap Progress
✅ Completed: [Features completed this month]
🔄 In Progress: [Current focus]
📅 Upcoming: [Next month priorities]

## Challenges
- [Challenge and how we're addressing it]

## Next Month Focus
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]
```

### Policy Change Communication

**Template**:
```markdown
# [Policy Name] Update

## TL;DR
- **What's Changing**: [One sentence]
- **Effective Date**: [Date]
- **Action Required**: [Yes/No and what]

## Background
[Why this policy exists and why it's changing]

## What's Changing
### Before
[Previous policy clearly stated]

### After
[New policy clearly stated]

### What's Staying the Same
[Important continuities]

## Who This Affects
[Specific teams, roles, or all employees]

## What You Need to Do
1. [Specific action with deadline]
2. [Specific action with deadline]

## Timeline
- **[Date]**: This announcement
- **[Date]**: Information sessions
- **[Date]**: Policy goes into effect
- **[Date]**: Check-in on adoption

## Resources
- [Link to full policy documentation]
- [Link to FAQ]
- [Link to training or guide]

## FAQ
### [Common Question 1]
[Clear answer]

### [Common Question 2]
[Clear answer]

## Questions?
Contact [person/team] at [contact method]

---
*Last updated: [Date]*
```

### Incident Post-Mortem

**Template**:
```markdown
# Post-Mortem: [Incident Name]

**Date**: [Incident date]
**Duration**: [Total time]
**Severity**: [P0/P1/P2]
**Author**: [Name]

## Executive Summary
[2-3 sentences on what happened, impact, and resolution]

## Impact
- **Users Affected**: [Number or percentage]
- **Services Affected**: [List]
- **Business Impact**: [Revenue, reputation, etc.]
- **Duration**: [Time to detection + resolution]

## Timeline (all times in PT)
- **[HH:MM]** - Initial symptoms detected
- **[HH:MM]** - Incident declared
- **[HH:MM]** - Root cause identified
- **[HH:MM]** - Fix deployed
- **[HH:MM]** - Services restored
- **[HH:MM]** - Incident closed

## Root Cause
[Technical explanation of what caused the incident]

## Detection
- **How we detected it**: [Monitoring alert/User report]
- **Time to detection**: [Duration]
- **What worked well**: [Effective monitoring/alerting]
- **What could improve**: [Detection gaps]

## Response
- **Time to mitigation**: [Duration]
- **What worked well**: [Effective processes]
- **What could improve**: [Response gaps]

## Resolution
[Explanation of how the incident was resolved]

## Action Items
| Action | Owner | Priority | Due Date | Status |
|--------|-------|----------|----------|--------|
| [Action] | @name | P0/P1/P2 | YYYY-MM-DD | Open/Complete |

## Lessons Learned
### What Went Well
- [Thing that helped resolve incident]
- [Effective process or tool]

### What Didn't Go Well
- [Gap or issue in response]
- [Tool or process that hindered response]

### Where We Got Lucky
- [Things that prevented worse outcome]

## Prevention
[Changes to prevent similar incidents]

---
*Follow-up review scheduled for: [Date]*
```

### Employee Recognition

**Template**:
```markdown
# 🌟 Team Recognition: [Person/Team Name]

## The Win
[Specific achievement or contribution]

## The Impact
[How this helped the company, team, or customers]

## Why This Matters
[Connect to company values or goals]

## The Team
[Credit everyone involved, with specific contributions]

## What They Said
> "[Quote from team member about the experience]"
> — [Team Member Name]

## Congratulations!
[Personalized message of appreciation]

---
Have someone to recognize? Share in #wins or nominate them for [recognition program].
```

### Cross-Team Collaboration Update

**Template**:
```markdown
# Cross-Team Update: [Project/Initiative Name]

**Teams Involved**: [List all teams]
**Project Lead**: [Name]
**Status**: 🟢 On Track / 🟡 At Risk / 🔴 Off Track

## Project Overview
[Brief description and goals]

## This Week's Progress
- [Key accomplishment involving multiple teams]
- [Integration completed]
- [Decision made]

## Team Contributions
### [Team 1]
- [Specific contribution]
- **Next**: [What they're doing next]

### [Team 2]
- [Specific contribution]
- **Next**: [What they're doing next]

## Dependencies & Handoffs
- [Team A] needs [deliverable] from [Team B] by [date]
- [Status of dependency]

## Blockers
- [Cross-team blocker and proposed resolution]

## Upcoming Milestones
- **[Date]**: [Milestone]
- **[Date]**: [Milestone]

## How to Stay Involved
- **Slack**: #project-name
- **Doc**: [Link to project doc]
- **Meetings**: [Schedule and calendar link]
```

### OKR Progress Report

**Template**:
```markdown
# OKR Progress Report - [Quarter] [Year]

**Team**: [Team Name]
**Reporting Period**: [Dates]

## Objective 1: [Objective Statement]
**Owner**: [Name]
**Overall Progress**: [0-100%] 🟢/🟡/🔴

### Key Result 1.1: [Measurable outcome]
- **Target**: [Target value]
- **Current**: [Current value]
- **Progress**: [X%]
- **Status**: 🟢 On track
- **Commentary**: [What's driving progress or what's blocking]

### Key Result 1.2: [Measurable outcome]
- **Target**: [Target value]
- **Current**: [Current value]
- **Progress**: [X%]
- **Status**: 🟡 At risk
- **Commentary**: [What's driving progress or what's blocking]

## Objective 2: [Objective Statement]
[Repeat structure]

## Key Wins This Period
- [Significant achievement toward OKRs]
- [Unexpected win]

## Challenges & Adjustments
- [Challenge faced and how we're adapting]
- [OKR adjustment if needed and rationale]

## Focus for Next Period
1. [Top priority to move OKRs forward]
2. [Second priority]

## Help Needed
- [Specific request from other teams or leadership]

---
**Confidence Level**: [High/Medium/Low] we'll hit our targets this quarter
```
