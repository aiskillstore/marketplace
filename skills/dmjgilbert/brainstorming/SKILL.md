---
name: brainstorming
description: Transform rough ideas into detailed designs through structured dialogue. Use before implementation to refine requirements.
---

# Brainstorming & Design Refinement

Transform rough ideas into validated designs through structured Socratic dialogue before any implementation begins.

## When to Use

- Starting a new feature with unclear requirements
- Exploring solution approaches
- Refining vague ideas into concrete plans
- Before writing any implementation code

## The Workflow

### Phase 1: Understanding

1. Review existing project context (files, docs, patterns)
2. Ask clarifying questions **sequentially** - one per message
3. Use multiple-choice when feasible (easier to answer)
4. Focus on:
   - What is the purpose/goal?
   - What are the constraints?
   - What does success look like?
   - Who/what is affected?

**Key rule:** One question at a time - avoid overwhelming

### Phase 2: Exploring Options

1. Present 2-3 different approaches
2. Lead with your recommended approach
3. Explain trade-offs for each:

```markdown
## Option A: [Name] (Recommended)

**Approach:** [Description]
**Pros:** [Benefits]
**Cons:** [Drawbacks]
**Best when:** [Use case]

## Option B: [Name]

**Approach:** [Description]
**Pros:** [Benefits]
**Cons:** [Drawbacks]
**Best when:** [Use case]
```

4. Discuss conversationally, not prescriptively
5. Be open to hybrid approaches

### Phase 3: Design Presentation

1. Break design into digestible sections (200-300 words each)
2. Validate incrementally after each section
3. Cover:
   - Architecture overview
   - Key components
   - Data flow
   - Error handling
   - Testing approach
4. Remain open to revisions

## Key Principles

### YAGNI (You Aren't Gonna Need It)

Ruthlessly eliminate speculative features:

| Ask                              | If No →       |
| -------------------------------- | ------------- |
| Is this required for MVP?        | Cut it        |
| Does the user need this now?     | Defer it      |
| Are we guessing at requirements? | Clarify first |

### One Question at a Time

```markdown
# Bad

What's the user flow? And what data do we need? Also, what about error handling?

# Good

What happens when a user clicks the submit button?
[Wait for answer]
What data needs to be sent to the server?
[Wait for answer]
```

### Explore Before Committing

Don't jump to the first solution. Consider:

- What's the simplest approach?
- What's the ideal approach (no constraints)?
- What could go wrong?
- How would this be solved differently in 5 years?

## Output: Design Document

After validation, produce:

```markdown
# Design: [Feature Name]

## Goal

[One sentence]

## Approach

[2-3 paragraphs]

## Components

- [Component 1]: [Purpose]
- [Component 2]: [Purpose]

## Data Flow

[Diagram or description]

## Error Handling

[Strategy]

## Testing Plan

[Approach]

## Open Questions

[If any remain]
```

## Post-Design

1. Save design to `docs/plans/YYYY-MM-DD-[feature].md`
2. Commit the design document
3. Transition to implementation using writing-plans skill
