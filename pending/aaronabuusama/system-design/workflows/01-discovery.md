# Phase 1: Discovery

**Goal:** Understand the problem space before proposing any solutions.

## Entry Questions

Start every discovery with these questions. Do not proceed until answered:

### 1. The Problem
- "What problem are you trying to solve?"
- "Who experiences this problem? How painful is it?"
- "What happens if this doesn't get built?"

### 2. The Actors
- "Who/what interacts with this system?"
- "Which of these are humans vs other systems?"
- "Who is the PRIMARY user? (there can only be one)"

### 3. The Constraints
- "What technical constraints exist?" (existing systems, team skills, budget)
- "What are the non-negotiables?"
- "What's the timeline pressure?"

### 4. Success Criteria
- "What does success look like in 3 months? 12 months?"
- "How will you know if the architecture is working?"
- "What would make you regret this design?"

## Probing Deeper

Once basics are answered, challenge assumptions:

| If they say... | Ask... |
|----------------|--------|
| "Users need to..." | "How do you know? Have you validated this?" |
| "It must be real-time" | "What's the actual latency requirement in ms?" |
| "We need microservices" | "What problem does that solve that a monolith doesn't?" |
| "It should be scalable" | "To what scale? What's your current/projected load?" |
| "Keep it simple" | "Simple for whom? Users? Developers? Operators?" |

## Red Flags to Surface

Watch for and explicitly call out:

- **Vague requirements** - "flexible", "scalable", "modern"
- **Solution-first thinking** - jumping to tech before understanding problem
- **Missing actors** - who maintains it? who pays for it?
- **Assumed constraints** - "we have to use X" (really?)
- **No failure modes discussed** - what happens when things go wrong?

## Discovery Outputs

Before moving to Phase 2, you should have:

```markdown
## Problem Statement
[1-2 sentences capturing the core problem]

## Primary Actor
[Who is this system primarily serving?]

## Secondary Actors
- [List other actors]

## Key Constraints
- [Non-negotiables]
- [Technical constraints]
- [Timeline/resource constraints]

## Success Criteria
- [Measurable outcomes]

## Open Questions
- [Things still unclear that need research/validation]
```

## Transition to Phase 2

When discovery is complete:

1. Summarize what you've learned back to the user
2. Confirm they agree with the summary
3. Ask: "Ready to start modeling the domain?"

Then: `read ./workflows/02-modeling.md`
