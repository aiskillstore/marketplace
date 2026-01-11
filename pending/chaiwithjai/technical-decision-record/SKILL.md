---
name: technical-decision-record
description: Use when making technical decisions, choosing technologies, or documenting architectural choices. Creates ADRs (Architecture Decision Records).
---

<framework_overview>
## What This Is

A structured approach to documenting technical decisions using ADRs (Architecture Decision Records). Ensures decisions are traceable, well-reasoned, and understood by the team.

## When to Use

- Choosing between technologies or frameworks
- Making architectural changes
- Selecting third-party services
- Changing established patterns
- Any decision you'd want to reference later
</framework_overview>

<principles>
## Core Philosophy

### 1. DECISIONS ARE IMMUTABLE HISTORY
Once made, an ADR is never modified—only superseded. This preserves the reasoning at the time, even if context changes later.

### 2. CONTEXT OVER CONCLUSION
The "why" is more valuable than the "what." Future readers need to understand the constraints, options, and trade-offs that led to the decision.

### 3. BIAS TOWARD REVERSIBILITY
Prefer decisions that can be changed later. Document the reversal cost for irreversible choices.

### 4. EXPLICIT OVER IMPLICIT
If it wasn't written down, it wasn't decided. Verbal agreements don't count as architectural decisions.

### 5. TEAM OVER INDIVIDUAL
Decisions should be reviewed by affected parties. Surprise decisions create resistance.
</principles>

<process>
## The Process

### Step 1: Define the Problem
What are we deciding? Be specific.
- "Which database for user data" not "database stuff"
- Include the trigger: what prompted this decision?

### Step 2: List Constraints
What limits our options?
- Technical: performance, scalability, existing stack
- Business: budget, timeline, team skills
- Compliance: security, regulatory, data residency

### Step 3: Enumerate Options
List 2-4 real options. For each:
- Brief description
- Pros (what it does well)
- Cons (what it does poorly)
- Estimated cost/effort

### Step 4: Make the Decision
Choose one option. State it clearly.
- "We will use [X]"
- Include who made the decision and when

### Step 5: Document Consequences
What follows from this decision?
- Positive: benefits we expect
- Negative: costs we accept
- Risks: what could go wrong
- Reversibility: how hard to change later
</process>

<templates>
## ADR Template

```markdown
# ADR-[NUMBER]: [TITLE]

**Status**: [Proposed | Accepted | Superseded by ADR-X]
**Date**: [YYYY-MM-DD]
**Deciders**: [Names]

## Context

[What is the issue? What prompted this decision?]

## Constraints

- [Constraint 1]
- [Constraint 2]
- [Constraint 3]

## Options Considered

### Option 1: [Name]
[Description]
- Pros: [...]
- Cons: [...]

### Option 2: [Name]
[Description]
- Pros: [...]
- Cons: [...]

### Option 3: [Name]
[Description]
- Pros: [...]
- Cons: [...]

## Decision

We will use **[Option X]**.

[Reasoning: Why this option over others?]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Cost 1]
- [Cost 2]

### Risks
- [Risk 1]: [Mitigation]
- [Risk 2]: [Mitigation]

### Reversibility
[Easy | Moderate | Difficult | Irreversible]
[Explanation of what reversal would require]
```
</templates>

<anti-patterns>
## Common Mistakes

### 1. DECIDING WITHOUT OPTIONS
Making a decision without exploring alternatives is not a decision—it's a default.

Why it's wrong: You can't justify a choice without knowing what you chose against.
Instead: Always list at least 2 options, even if one is "do nothing."

### 2. BIKESHEDDING
Spending more time on reversible decisions than irreversible ones.

Why it's wrong: Time spent on low-stakes decisions is time not spent on high-stakes ones.
Instead: Match deliberation time to reversibility. Irreversible = more process.

### 3. HIDDEN STAKEHOLDERS
Making decisions that affect teams without involving them.

Why it's wrong: Creates surprise, resistance, and rework.
Instead: List affected parties in "Deciders" and get explicit sign-off.

### 4. REVISION INSTEAD OF SUPERSESSION
Editing old ADRs when context changes.

Why it's wrong: Loses the historical record of why decisions were made.
Instead: Create a new ADR that supersedes the old one, referencing the original.
</anti-patterns>

<intake>
What technical decision are you working on?

1. **What's being decided?**
   - Technology choice
   - Architectural pattern
   - Third-party service
   - Process change
   - Other: ___

2. **What triggered this decision?**
   - New requirement
   - Performance issue
   - Technical debt
   - Team change
   - Other: ___

3. **How reversible should this be?**
   - Easy to change (experiment)
   - Moderate effort to change
   - Significant investment
   - Hard to reverse (commit carefully)

I'll help you structure the ADR based on your answers.
</intake>
