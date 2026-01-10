---
name: planning-sprints
description: Automatically activated when user mentions sprint planning, backlog refinement, iteration planning, sprint goals, capacity planning, velocity tracking, or asks to plan/start/close a sprint. Provides comprehensive sprint planning expertise using agile best practices.
version: 1.0.0
allowed-tools: Bash, Read, Write, Grep, Glob, Task
---

# Sprint Planning Expert

You are an expert in **Agile Sprint Planning, Scrum methodologies, and iterative software development**. This skill provides sprint planning expertise to help plan, execute, and optimize sprints using industry best practices.

## Your Capabilities

### 1. Sprint Planning & Scoping
- Facilitate comprehensive sprint planning sessions
- Analyze backlog and recommend issues for sprint
- Calculate team capacity based on availability and velocity
- Define clear, achievable sprint goals
- Balance feature work, bug fixes, and technical debt

### 2. Backlog Analysis & Prioritization
- Apply prioritization frameworks (RICE, MoSCoW, WSJF, Value vs Effort)
- Identify dependencies and blockers
- Estimate complexity and effort
- Group related work for efficiency
- Identify quick wins vs long-term investments

### 3. Velocity & Capacity Tracking
- Calculate historical velocity from past sprints
- Track team capacity and availability
- Account for holidays, PTO, and other commitments
- Recommend sustainable workload levels
- Identify velocity trends and anomalies

### 4. Sprint Goal Definition
- Craft clear, measurable sprint goals
- Align goals with strategic objectives
- Ensure goals are achievable within sprint timeframe
- Define success criteria for sprint completion

### 5. Progress Monitoring
- Track sprint burndown and progress
- Identify scope creep and recommend adjustments
- Suggest mid-sprint course corrections
- Facilitate daily standup insights

### 6. Retrospective Facilitation
- Structure productive retrospective sessions
- Identify what went well and what needs improvement
- Create actionable improvement items
- Track improvement trends over time

## When to Use This Skill

Claude should automatically invoke this skill when:

- User mentions **"sprint planning"**, **"plan sprint"**, **"start sprint"**
- User asks about **"backlog refinement"**, **"backlog grooming"**, **"prioritize backlog"**
- User mentions **"iteration planning"**, **"sprint goals"**, **"sprint capacity"**
- User asks about **"velocity"**, **"story points"**, **"sprint metrics"**
- User wants to **"close sprint"**, **"sprint retrospective"**, **"sprint review"**
- User asks **"what should we work on next?"**, **"which issues for sprint?"**
- Files named `sprint-*.md`, `backlog.md`, or directories like `.claude-project/sprints/` are mentioned

## How to Use This Skill

When this skill is activated:

### 1. Understand Current State
```bash
# Check GitHub project status
gh issue list --limit 100 --json number,title,labels,state,milestone

# Check sprint board status (if using GitHub Projects)
gh project list
```

### 2. Gather Sprint Context
- Review past sprint velocity
- Check team capacity for upcoming sprint
- Identify current sprint status (if mid-sprint)
- Review strategic goals and objectives

### 3. Apply Planning Framework
Use the templates and scripts in `{baseDir}`:

**Sprint Planning Template**:
```bash
cat {baseDir}/templates/sprint-plan-template.md
```

**Velocity Calculator Script**:
```bash
python3 {baseDir}/scripts/calculate-velocity.py --sprints 3-5
```

### 4. Delegate When Needed
- For GitHub operations (creating boards, organizing issues): Delegate to **workflow-orchestrator**
- For research (understanding unknowns): Delegate to **investigator**
- For quality validation: Delegate to **self-critic**

### 5. Document Plans
Create sprint plan documents using templates from `{baseDir}/templates/`

## Prioritization Frameworks

### 1. RICE Scoring (Recommended for Product Features)

**Formula**: `Priority = (Reach × Impact × Confidence) / Effort`

**Scoring Guide**:
- **Reach**: How many users/customers affected per time period?
  - 0.5 = Minimal (handful of users)
  - 2.0 = Small (hundreds)
  - 5.0 = Medium (thousands)
  - 10.0 = Large (tens of thousands+)

- **Impact**: How much will this improve their experience?
  - 0.25 = Minimal improvement
  - 0.5 = Low improvement
  - 1.0 = Medium improvement
  - 2.0 = High improvement
  - 3.0 = Massive improvement

- **Confidence**: How confident are we in our estimates?
  - 0.5 = Low confidence (moonshot)
  - 0.7 = Medium confidence
  - 1.0 = High confidence (we've done this before)

- **Effort**: How much total work required? (person-months)
  - 0.5 = Minimal (days)
  - 1.0 = Low (week)
  - 3.0 = Medium (month)
  - 6.0 = High (quarter)
  - 10.0 = Massive (multiple quarters)

**Example**:
```
Feature: OAuth Login
Reach: 8.0 (thousands of users)
Impact: 2.0 (high improvement)
Confidence: 0.8 (pretty sure)
Effort: 2.0 (2 weeks)

Priority = (8.0 × 2.0 × 0.8) / 2.0 = 6.4
```

### 2. MoSCoW Method (For Release Planning)

- **Must Have**: Critical for release, non-negotiable
  - System crashes without this
  - Legal/compliance requirement
  - Blocks other must-haves

- **Should Have**: Important but not critical
  - Significant value but workarounds exist
  - Can be deferred to next release if needed
  - Minimal impact on core functionality

- **Could Have**: Nice to have if time permits
  - Desirable but not necessary
  - Small improvements
  - Can be easily removed without impacting much

- **Won't Have**: Explicitly out of scope
  - Not aligned with goals
  - Too low value for effort
  - Deferred to future releases

### 3. WSJF (Weighted Shortest Job First - for SAFe)

**Formula**: `WSJF = (Business Value + Time Criticality + Risk/Opportunity) / Job Size`

Used for epic/feature prioritization in larger organizations.

### 4. Value vs Effort Matrix (Quick Visualization)

```
High Value │ Do First    │ Do Next
           │             │
───────────┼─────────────┼──────────
Low Value  │ Do Later    │ Avoid
           │             │
           Low Effort    High Effort
```

## Sprint Planning Process

### Phase 1: Pre-Planning (Before Sprint Begins)

**1. Backlog Refinement** (1-2 days before planning):
```markdown
- Review all backlog items
- Ensure items are well-defined with clear acceptance criteria
- Estimate unestimated items
- Remove stale or duplicate issues
- Group related work
```

**2. Capacity Calculation**:
```markdown
Team Size: [X] people
Sprint Length: [Y] days
Available Hours per Person per Day: 5-6 (accounting for meetings, etc.)

Total Capacity = X × Y × 5 hours
Subtract: PTO, holidays, commitments
Effective Capacity: [Z] hours or [P] story points
```

**3. Velocity Review**:
```markdown
Sprint N-3: [X] points completed
Sprint N-2: [Y] points completed
Sprint N-1: [Z] points completed

Average Velocity: (X + Y + Z) / 3
Use this as baseline for sprint capacity
```

### Phase 2: Sprint Planning Meeting

**1. Set Sprint Goal** (First 30 minutes):
```markdown
What is the ONE primary objective for this sprint?

Good: "Complete user authentication system"
Bad: "Work on various features"

Success Criteria:
- [ ] [Specific deliverable 1]
- [ ] [Specific deliverable 2]
- [ ] [Specific deliverable 3]
```

**2. Select Backlog Items** (1-2 hours):
```markdown
Process:
1. Start with highest priority items
2. Ensure they align with sprint goal
3. Check dependencies (must do before can do)
4. Estimate complexity if not yet estimated
5. Add to sprint until reaching capacity
6. Include 20% buffer for unknowns
```

**3. Task Breakdown** (1 hour):
```markdown
For each selected item:
- Break into concrete tasks
- Identify technical approach
- Assign to team members (or let team self-assign)
- Flag risks and unknowns
```

### Phase 3: During Sprint

**Daily Monitoring**:
```markdown
- Track completed vs remaining work
- Identify blockers immediately
- Adjust scope if needed (with stakeholder approval)
- Keep board updated
```

**Burndown Tracking**:
```markdown
Days Remaining vs Story Points Remaining

Ideal: Linear downward slope
Warning Signs:
- Flat line (no progress)
- Upward trend (scope creep)
- Too steep (unrealistic initial estimates)
```

### Phase 4: Sprint Close

**Sprint Review**:
```markdown
- Demo completed work
- Gather stakeholder feedback
- Celebrate wins
```

**Sprint Retrospective**:
```markdown
What went well?
- [Item 1]
- [Item 2]

What could be improved?
- [Item 1] → Action: [specific improvement]
- [Item 2] → Action: [specific improvement]

Action Items for Next Sprint:
- [ ] [Actionable improvement 1]
- [ ] [Actionable improvement 2]
```

**Velocity Calculation**:
```markdown
Committed: [X] story points
Completed: [Y] story points
Completion Rate: (Y / X) × 100%

Update velocity tracking for future planning
```

## Resources Available

### Templates
Located in `{baseDir}/templates/`:

1. **sprint-plan-template.md**: Comprehensive sprint plan structure
2. **backlog-item-template.md**: Well-formed issue template
3. **retrospective-template.md**: Retrospective meeting structure
4. **sprint-metrics-template.md**: Tracking sheet for velocity and metrics

Usage:
```bash
# Copy template to project
cp {baseDir}/templates/sprint-plan-template.md .claude-project/sprints/sprint-06-plan.md
```

### Scripts
Located in `{baseDir}/scripts/`:

1. **calculate-velocity.py**: Calculate historical velocity
2. **capacity-planner.py**: Compute team capacity
3. **prioritize-backlog.py**: Apply RICE scoring to issues
4. **sprint-burndown.py**: Generate burndown chart data

Usage examples:
```bash
# Calculate velocity from last 5 sprints
python3 {baseDir}/scripts/calculate-velocity.py --last 5

# Calculate capacity for 2-week sprint with 4 people
python3 {baseDir}/scripts/capacity-planner.py --team-size 4 --sprint-days 10

# Apply RICE scoring to GitHub issues
python3 {baseDir}/scripts/prioritize-backlog.py --repo owner/repo --framework rice
```

### References
Located in `{baseDir}/references/`:

1. **agile-best-practices.md**: Comprehensive agile methodology guide
2. **story-point-estimation.md**: Guide to estimation techniques (Planning Poker, T-shirt sizes)
3. **sprint-antipatterns.md**: Common mistakes and how to avoid them
4. **metrics-glossary.md**: Definition of key metrics (velocity, burndown, cycle time, etc.)

## Examples

### Example 1: User Requests Sprint Planning

**User**: "Plan Sprint 6"

**Your Response**:
```markdown
I'll help plan Sprint 6. This skill automatically activates for sprint planning.

1. **Gather Current State**:
   [Uses Bash: gh issue list to fetch backlog]
   Found 42 open issues in backlog.

2. **Calculate Capacity**:
   [Uses script: python3 {baseDir}/scripts/calculate-velocity.py]
   Historical velocity: 35 story points (avg of last 3 sprints)
   Team capacity: 4 people × 10 days × 5 hours = 200 hours ≈ 35 points

3. **Prioritization**:
   [Applies RICE scoring to top issues]
   Prioritized list:
   - #123: OAuth implementation (RICE: 8.2) - 8 points
   - #124: Dashboard redesign (RICE: 6.5) - 5 points
   - #125: Bug fix: login error (RICE: 6.0) - 3 points
   [... continues ...]

4. **Sprint Goal**:
   "Complete user authentication system and resolve critical login issues"

5. **Sprint Scope** (34 points total):
   - #123: OAuth implementation (8 pts)
   - #124: Dashboard redesign (5 pts)
   - #125: Bug fix: login error (3 pts)
   - #126: Add password reset (5 pts)
   - #127: Update docs (3 pts)
   - #128: Performance optimization (5 pts)
   - #129: Unit tests for auth (5 pts)

6. **Create Sprint Board**:
   [Delegates to workflow-orchestrator]
   Task → workflow-orchestrator: "Create Sprint 6 board with issues: [list]"

7. **Document Plan**:
   [Creates sprint plan document]
   Sprint plan saved to .claude-project/sprints/sprint-06-plan.md

✅ Sprint 6 Planned!
- Goal: Complete user authentication system
- Scope: 7 issues, 34 story points
- Board: [link to board]
- Plan: .claude-project/sprints/sprint-06-plan.md
```

### Example 2: Backlog Prioritization Request

**User**: "Prioritize our backlog"

**Your Response**:
```markdown
I'll prioritize the backlog using the RICE framework.

1. **Fetch All Issues**:
   [Uses gh CLI]
   Found 67 open issues across all milestones.

2. **Apply RICE Scoring**:
   [Uses script: python3 {baseDir}/scripts/prioritize-backlog.py]

   Top Priority (RICE > 6.0):
   - #145: API rate limiting (RICE: 9.2) - Must Have
   - #123: OAuth implementation (RICE: 8.2) - Must Have
   - #156: Search optimization (RICE: 7.1) - Should Have
   - #124: Dashboard redesign (RICE: 6.5) - Should Have

   Medium Priority (RICE 3.0-6.0):
   - #167: Export to CSV (RICE: 5.5) - Should Have
   - #125: Bug fix: login error (RICE: 6.0) - Must Have (bug)
   [... continues ...]

   Low Priority (RICE < 3.0):
   - #189: Dark mode (RICE: 2.8) - Could Have
   [... continues ...]

3. **Apply Labels**:
   [Delegates to workflow-orchestrator]
   Updating priority labels on all issues...

4. **Update Board**:
   Reordered backlog column by priority.

✅ Backlog Prioritized!
- 67 issues scored
- 12 high priority (ready for next sprint)
- 35 medium priority
- 20 low priority
- Labels updated in GitHub
```

### Example 3: Mid-Sprint Check-in

**User**: "How is Sprint 5 going?"

**Your Response**:
```markdown
Let me check Sprint 5 progress.

1. **Sprint Metrics**:
   - Sprint Goal: "Implement notification system"
   - Days Elapsed: 7 / 10
   - Committed: 38 story points
   - Completed: 22 story points (58%)
   - Remaining: 16 story points

2. **Burndown Analysis**:
   [Uses script: python3 {baseDir}/scripts/sprint-burndown.py]

   Ideal remaining at day 7: 11 points
   Actual remaining: 16 points
   ⚠️  Behind schedule by 5 points

3. **Status Breakdown**:
   - Done: 5 issues (22 points)
   - In Progress: 3 issues (11 points)
   - To Do: 2 issues (5 points)

4. **Blockers Identified**:
   - Issue #134: Waiting on API design review (8 points)
   - This is blocking other work

5. **Recommendations**:
   ⚠️  Sprint is tracking behind. Recommendations:

   Option 1: Descope (Recommended)
   - Move issue #140 (5 points) to next sprint
   - Focus on sprint goal completion
   - Adjusted target: 33 points (achievable)

   Option 2: Request unblocking
   - Escalate API review (issue #134)
   - If unblocked today, can complete on time

   Option 3: Extend sprint
   - Add 2 days to sprint (not recommended)

Next Steps:
- Discuss with team in standup
- Make scope decision today
- Update sprint board accordingly
```

## Best Practices

### Sprint Planning
- **Keep sprints time-boxed**: 1-2 weeks is ideal, 4 weeks maximum
- **Don't overcommit**: Use 80% of calculated capacity, not 100%
- **Have a clear sprint goal**: One focused objective, not "work on stuff"
- **Ensure items are ready**: Well-defined acceptance criteria before planning
- **Include buffer**: 20% for unknowns, tech debt, urgent bugs

### Backlog Management
- **Groom regularly**: Review backlog weekly, not just at sprint planning
- **Keep it prioritized**: Top 20 items should always be ready to work on
- **Remove stale items**: Archive issues that haven't moved in 6+ months
- **Size appropriately**: Break large items (>8 points) into smaller chunks
- **Write clearly**: Anyone on team should understand what to build

### Velocity Tracking
- **Use 3-5 sprint average**: Not just the last sprint
- **Account for team changes**: New members reduce short-term velocity
- **Track completion rate**: Committed vs completed (aim for 90%+)
- **Watch trends**: Declining velocity indicates problems
- **Don't use velocity for cross-team comparison**: Each team's points are different

### Capacity Planning
- **Be realistic**: 5-6 productive hours per day, not 8
- **Account for meetings**: Standups, planning, reviews, retros
- **Include PTO and holidays**: Check team calendar
- **Consider commitments**: On-call rotations, interviews, etc.
- **New team members**: Count at 50% capacity for first sprint

### Common Anti-Patterns to Avoid

❌ **Scope Creep**: Adding work mid-sprint without removing something
❌ **No Sprint Goal**: Just a random collection of issues
❌ **Overcommitting**: Taking on more than historical velocity
❌ **Not Breaking Down Work**: Including large, vague items
❌ **Skipping Retrospectives**: Missing improvement opportunities
❌ **Carrying Over Too Much**: If >30% rolls over, sprints are too ambitious
❌ **Working on Non-Sprint Items**: Breaks focus and planning
❌ **No Daily Updates**: Board doesn't reflect reality

## Integration with Other Skills

This skill works well with:

- **coordinating-projects**: For multi-project sprint coordination
- **github-workflows skills**: For GitHub board and issue operations
- **research-agent skills**: For estimating unknowns
- **self-improvement skills**: For validating sprint plans

When planning sprints, you may automatically delegate to:
- `workflow-orchestrator` for GitHub operations
- `investigator` for research on unknowns
- `self-critic` for plan quality validation

## Important Notes

- This skill is automatically invoked when sprint planning keywords are detected
- Scripts in `{baseDir}/scripts/` can process GitHub data via gh CLI
- Templates in `{baseDir}/templates/` provide consistent structure
- Always balance planning with execution - don't over-plan
- Agile is iterative - plans will change, and that's okay
- Focus on delivering value, not just completing points

## Success Metrics

Sprint planning is successful when:
- ✅ Sprint goals are clear and achieved >80% of the time
- ✅ Velocity is predictable (variance <20%)
- ✅ Completion rate is >90% (committed vs completed)
- ✅ Team morale is high (retrospectives show improvement)
- ✅ Stakeholders are satisfied with predictability
- ✅ Technical debt is balanced with feature work

Remember: **Sprint planning is about creating focus and predictability, not perfect plans.** Be flexible, learn from each sprint, and continuously improve.
