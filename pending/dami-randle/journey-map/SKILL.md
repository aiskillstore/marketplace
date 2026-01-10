---
name: journey-map
description: Create customer journey maps for user flows and workflows. Use when the user asks to "map the journey", "analyze user flow", "document the workflow", "trace the path", or needs to understand end-to-end user experiences.
---

# Journey Mapping Skill

Map customer journeys to understand end-to-end user experiences, identify pain points, and discover opportunities for improvement.

## When to Use

- Designing new features or flows
- Understanding existing user paths
- Identifying friction points
- Planning improvements
- Stakeholder communication
- Onboarding design

## Journey Map Components

### 1. User Context
- **Persona**: Who is the user?
- **Goal**: What are they trying to accomplish?
- **Trigger**: What initiated this journey?
- **Success**: How do they know they've succeeded?

### 2. Journey Phases

Typical phases to map:

| Phase | Description |
|-------|-------------|
| Awareness | User realizes they need something |
| Consideration | User evaluates options |
| Decision | User commits to action |
| Action | User completes the task |
| Retention | User returns or continues |

### 3. Touchpoint Analysis

For each step, document:
- **Action**: What the user does
- **Interface**: What they interact with
- **Thought**: What they're thinking
- **Emotion**: How they feel (frustrated, confident, confused)
- **Pain Point**: What causes friction
- **Opportunity**: How to improve

### 4. Emotion Curve

Map emotional state through the journey:
```
Delighted  ●───────────●
Satisfied      ●───●
Neutral            ●───●
Frustrated             ●───●
Abandoned                  ●
```

## Output Format

```markdown
## Customer Journey Map: [Journey Name]

### Context
- **Persona**: [User type]
- **Goal**: [What they want to achieve]
- **Trigger**: [What started this journey]

### Journey Overview

| Phase | Step | Action | Emotion | Pain Point |
|-------|------|--------|---------|------------|
| Awareness | 1 | ... | ... | ... |

### Detailed Steps

#### Step 1: [Name]
- **User Action**: What they do
- **System Response**: What happens
- **User Thought**: "What they're thinking"
- **Emotion**: [emoji + description]
- **Pain Points**: Issues encountered
- **Opportunities**: Ways to improve

### Emotion Curve
[Visual representation]

### Key Insights
1. [Critical finding]
2. [Opportunity identified]

### Recommendations
| Priority | Improvement | Impact |
|----------|-------------|--------|
| P0 | ... | High |
```

## Common Journeys for LogiDocs Certify

1. **First-Time User Onboarding**
2. **Upload Supplier Certificate**
3. **Create Product Checklist**
4. **Prepare for Audit**
5. **Track Expiring Documents**
6. **Invite Team Member**
7. **Generate Compliance Report**

## Integration

Works best with:
- `ux-expert` agent for journey analysis
- `ux-audit` skill for touchpoint evaluation
- Persona testing agents for validation
