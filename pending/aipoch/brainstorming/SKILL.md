---
name: brainstorming
description: Creative exploration and brainstorming; use it when you need to clarify goals/constraints, explore multiple options, and converge on a direction before implementation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have a vague idea and need to clarify goals, scope, and constraints before committing to a plan.
- You want to generate multiple solution directions for a problem and compare trade-offs.
- You need to break down a complex problem into smaller, actionable parts.
- You’re stuck and need alternative approaches, assumptions to challenge, or fresh angles.
- You want to converge from many ideas into a prioritized shortlist and define next steps.

## Key Features

- Goal and boundary clarification (objectives, constraints, success criteria).
- Structured ideation to produce multiple distinct options.
- Problem decomposition into components, subproblems, and decision points.
- Evaluation and convergence (trade-offs, risks, feasibility, impact).
- Actionable next steps (experiments, prototypes, questions to validate).
- Reference workflow support via `references/brainstorming-workflow.md`.

## Dependencies

- None

## Example Usage

### Prompt
```text
I want to build a feature that helps users learn faster in our app, but I’m not sure what exactly to build.
Constraints: 2-week implementation, no new backend services, must work on mobile.
Goal: increase weekly retention.
Please brainstorm options, compare them, and recommend a direction with next steps.
```

### Expected Output Structure (Runnable Template)
```markdown
## 1) Clarify Goals & Boundaries
- Primary goal: increase weekly retention
- Constraints: 2-week build, no new backend services, mobile-first
- Success metrics: retention uplift, feature adoption, session frequency

## 2) Generate Options (Diverge)
1. **Spaced repetition reminders**
   - What it is: ...
   - Why it helps: ...
2. **Daily micro-challenges**
   - What it is: ...
   - Why it helps: ...
3. **Progress-based streaks + milestones**
   - What it is: ...
   - Why it helps: ...
4. **Personalized review queue (client-side)**
   - What it is: ...
   - Why it helps: ...

## 3) Compare & Evaluate
| Option | Effort | Risk | Expected impact | Notes |
|---|---:|---:|---:|---|
| Spaced repetition reminders | Medium | Low | Medium | ... |
| Daily micro-challenges | Medium | Medium | High | ... |
| Streaks + milestones | Low | Low | Medium | ... |
| Client-side review queue | Medium | Medium | Medium | ... |

## 4) Converge on a Recommendation
- Recommended direction: **Daily micro-challenges**
- Rationale: ...
- Key assumptions to validate: ...

## 5) Next Steps
- Prototype: ...
- Instrumentation: ...
- A/B test plan: ...
- Open questions: ...
```

## Implementation Details

- **Workflow**: Follow the structured process described in `references/brainstorming-workflow.md`:
  1. Clarify goals, constraints, and success criteria.
  2. Diverge: generate multiple distinct options (avoid premature convergence).
  3. Decompose: break options into components and required decisions.
  4. Evaluate: compare trade-offs (impact, effort, risk, feasibility).
  5. Converge: select a direction and define concrete next steps.

- **Core parameters to capture**
  - **Goal**: what outcome to optimize (e.g., retention, cost, latency, satisfaction).
  - **Constraints**: time, budget, platform, compliance, dependencies.
  - **Evaluation criteria**: impact, effort, risk, reversibility, time-to-value.
  - **Assumptions**: what must be true for the chosen direction to work.
  - **Next-step artifacts**: shortlist, decision rationale, experiment plan, open questions.