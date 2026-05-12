# State Machine Diagram Deep Dive

Use a state machine diagram to model the lifecycle or protocol of one stateful subject. It answers which states can persist and which events cause valid transitions.

## Use When

- The user needs lifecycle states, allowed transitions, modes, validity, authorization, availability, expiration, or protocol rules.
- Invalid transitions matter.
- Guards and transition effects explain behavior.
- Composite or concurrent state dimensions are needed.

Avoid when the user is describing a workflow across many responsibilities or a sequence of messages.

## Core Modeling Elements

- State.
- Initial and final pseudostate.
- Transition.
- Event/trigger.
- Guard.
- Effect.
- Composite state.
- Region, including orthogonal regions when independent dimensions are simultaneous.
- Entry, exit, and do behavior when state-tied behavior matters.

## Expansion Questions

- What is the single lifecycle-bearing subject?
- Can every state persist over time?
- What event triggers each transition?
- Is each condition a guard, state, or invariant?
- Is each action an effect, entry/exit/do behavior, or activity?
- Are multiple dimensions subordinate, orthogonal, separate diagrams, or an invariant table?
- Does the subject have a meaningful final state, or is it long-lived?

## Design Moves

- Name states as conditions or modes, usually nouns/adjectives.
- Name transitions as `event [guard] / effect`.
- Keep arrow labels short; move explanations to a legend or table.
- Use composite states only for real containment.
- Use orthogonal regions only when dimensions are active at the same time and independently transition.
- Model external concerns as events, guards, or effects unless they are states of the same subject.

## Completeness Criteria

- One subject owns the lifecycle.
- States are stable and mutually meaningful.
- Transitions are allowed behavior, not a workflow checklist.
- Guards and effects are separated.
- Cross-dimension constraints are modeled explicitly.

## Common Mistakes And Repairs

- Actions as states: move to transition effects or activity diagrams.
- Multiple subjects mixed: split by subject or convert external concerns to guards/events.
- Long transition prose: shorten label and add legend.
- Decorative grouping: replace with true composite state or remove group.
