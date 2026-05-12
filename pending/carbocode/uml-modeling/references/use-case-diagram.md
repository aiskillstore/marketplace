# Use Case Diagram Deep Dive

Use a use case diagram to model external actors, user goals, and the subject boundary. It answers who gets value from the system and what goals are visible from outside.

## Use When

- The user needs requirements scope.
- Actor roles and external systems matter.
- The system boundary is unclear or disputed.
- Goal-level capabilities need to be named before detailing flows.

Avoid when the question is UI navigation, internal functions, class design, or step-by-step workflow.

## Core Modeling Elements

- Subject/system boundary.
- Actor.
- Use case.
- Association.
- Include, extend, actor generalization, use case generalization when justified.

## Expansion Questions

- What is the subject boundary?
- Is each actor external to that boundary?
- Is each use case a goal observable by an actor?
- Are external systems actors, neighboring systems, or inside the subject?
- Is included behavior mandatory and reused?
- Is extended behavior optional or conditional at an extension point?

## Design Moves

- Name actors as roles, not people, UI widgets, services, or classes.
- Name use cases with goal-level verb-object phrases.
- Draw the boundary whenever scope matters.
- Keep detailed steps out; put them in activity or sequence diagrams.
- Use include/extend sparingly because they add semantic load.

## Completeness Criteria

- The reader knows what is inside and outside the subject.
- Every use case is externally meaningful.
- Associations connect actors to goals, not actors to implementation.
- Include/extend/generalization have specific semantics, not decorative reuse.

## Common Mistakes And Repairs

- Menu map: rename to actor goals or replace with a navigation/activity diagram.
- Internal services as actors: move them inside the boundary or use component/sequence diagrams.
- Function list: lift functions to user goals.
- Overused include: keep only mandatory reusable behavior.
