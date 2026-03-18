---
name: task-estimation
description: Estimate software development tasks accurately using various techniques. Use when planning sprints, roadmaps, or project timelines. Handles story points, t-shirt sizing, planning poker, and estimation best practices.
metadata:
  tags: estimation, agile, sprint-planning, story-points, planning-poker
  platforms: Claude, ChatGPT, Gemini
---


# Task Estimation


## When to use this skill

- **Sprint Planning**: Decide what work to include in the sprint
- **Roadmap creation**: Build long-term plans
- **Resource planning**: Estimate team size and schedule

## Instructions

### Step 1: Story Points (relative estimation)

**Fibonacci sequence**: 1, 2, 3, 5, 8, 13, 21

```markdown
## Story Point guidelines

### 1 Point (Very Small)
- Example: text change, constant value update
- Time: 1-2 hours
- Complexity: very low
- Risk: none

### 2 Points (Small)
- Example: simple bug fix, add logging
- Time: 2-4 hours
- Complexity: low
- Risk: low

### 3 Points (Medium)
- Example: simple CRUD API endpoint
- Time: 4-8 hours
- Complexity: medium
- Risk: low

### 5 Points (Medium-Large)
- Example: complex form implementation, auth middleware
- Time: 1-2 days
- Complexity: medium
- Risk: medium

### 8 Points (Large)
- Example: new feature (frontend + backend)
- Time: 2-3 days
- Complexity: high
- Risk: medium

### 13 Points (Very Large)
- Example: payment system integration
- Time: 1 week
- Complexity: very high
- Risk: high
- **Recommended**: Split into smaller tasks

### 21+ Points (Epic)
- **Required**: Must be split into smaller stories
```

### Step 2: Planning Poker

**Process**:
1. Product Owner explains the story
2. Team asks questions
3. Everyone picks a card (1, 2, 3, 5, 8, 13)
4. Reveal simultaneously
5. Explain highest/lowest scores
6. Re-vote
7. Reach consensus

**Example**:
```
Story: "Users can upload a profile photo"

Member A: 3 points (simple frontend)
Member B: 5 points (image resizing needed)
Member C: 8 points (S3 upload, security considerations)

Discussion:
- Use an image processing library
- S3 is already set up
- File size validation needed

Re-vote → consensus on 5 points
```

### Step 3: T-Shirt Sizing (quick estimation)

```markdown
## T-Shirt sizes

- **XS**: 1-2 Story Points (within 1 hour)
- **S**: 2-3 Story Points (half day)
- **M**: 5 Story Points (1-2 days)
- **L**: 8 Story Points (1 week)
- **XL**: 13+ Story Points (needs splitting)

**When to use**:
- Initial backlog grooming
- Rough roadmap planning
- Quick prioritization
```

### Step 4: Consider risk and uncertainty

**Estimation adjustment**:
```typescript
interface TaskEstimate {
  baseEstimate: number;      // base estimate
  risk: 'low' | 'medium' | 'high';
  uncertainty: number;        // 0-1
  finalEstimate: number;      // adjusted estimate
}

function adjustEstimate(estimate: TaskEstimate): number {
  let buffer = 1.0;

  // risk buffer
  if (estimate.risk === 'medium') buffer *= 1.3;
  if (estimate.risk === 'high') buffer *= 1.5;

  // uncertainty buffer
  buffer *= (1 + estimate.uncertainty);

  return Math.ceil(estimate.baseEstimate * buffer);
}

// Example
const task = {
  baseEstimate: 5,
  risk: 'medium',
  uncertainty: 0.2  // 20% uncertainty
};

const final = adjustEstimate(task);  // 5 * 1.3 * 1.2 = 7.8 → 8 points
```

## Output format

### Estimation document template

```markdown
## Task: [Task Name]

### Description
[work description]

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### Estimation
- **Story Points**: 5
- **T-Shirt Size**: M
- **Estimated Time**: 1-2 days

### Breakdown
- Frontend UI: 2 points
- API Endpoint: 2 points
- Testing: 1 point

### Risks
- Uncertain API response time (medium risk)
- External library dependency (low risk)

### Dependencies
- User authentication must be completed first

### Notes
- Need to discuss design with UX team
```

## Constraints

### Required rules (MUST)

1. **Relative estimation**: Relative complexity instead of absolute time
2. **Team consensus**: Agreement from the whole team, not individuals
3. **Use historical data**: Plan based on velocity

### Prohibited (MUST NOT)

1. **Pressuring individuals**: Estimates are not promises
2. **Overly granular estimation**: Split anything 13+ points
3. **Turning estimates into deadlines**: estimate ≠ commitment

## Best practices

1. **Break Down**: Split big work into smaller pieces
2. **Reference Stories**: Reference similar past work
3. **Include buffer**: Prepare for the unexpected

## References

- [Scrum Guide](https://scrumguides.org/)
- [Planning Poker](https://www.planningpoker.com/)
- [Story Points](https://www.atlassian.com/agile/project-management/estimation)

## Metadata

### Version
- **Current version**: 1.0.0
- **Last updated**: 2025-01-01
- **Compatible platforms**: Claude, ChatGPT, Gemini

### Tags
`#estimation` `#agile` `#story-points` `#planning-poker` `#sprint-planning` `#project-management`

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
