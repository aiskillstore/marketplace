# Use Case Diagram Design

Use this reference for actor-goal modeling and system boundary diagrams.

## Purpose

A use case diagram models externally visible goals that actors pursue with a system.

It answers:

- Who interacts with the system?
- What goals do they have?
- What is inside the system boundary?
- Which external systems participate?

It does not model:

- UI navigation;
- click-by-click flow;
- internal services;
- function list implementation;
- class/package/component architecture.

## Actors

Actors are roles external to the system boundary.

Good actor names:

- `Authenticated user`
- `Operator`
- `Admin`
- `Payment provider`
- `External authorization service`
- `Mobile OS`

Bad actor names:

- `Login button`
- `AuthService`
- `Data table`
- `Dialog component`

## Use Cases

Use cases are user goals, usually verb-object phrases.

Good:

- `Search records`
- `Submit order`
- `Update profile`
- `Authenticate user`
- `Review document`

Bad:

- `Click update`
- `Call service`
- `Open dialog`
- `Validate form`

Those may be steps inside a use case, not use cases themselves.

## Boundary

Draw the system boundary when scope matters.

Questions:

- Is the authorization provider part of the system or an external actor?
- Is the persistence store inside the application boundary?
- Is the external service part of this system or outside it?

Different answers produce different diagrams. State the chosen boundary.

## Include, Extend, Generalization

Use sparingly.

- `include`: mandatory reused behavior needed by the base use case.
- `extend`: optional/conditional behavior that extends a base use case at extension points.
- actor generalization: specialized actor inherits participation of a general actor.
- use case generalization: specialized goal refines a general goal.

Do not use `include` merely to decompose every step. That turns a use case diagram into a flowchart.

## Review Checklist

- Are all actors outside the system?
- Are use cases user-observable goals?
- Is the boundary clear?
- Are include/extend/generalization used with correct semantics?
- Are internal implementation details absent?
- Would an activity diagram better explain the flow?

## Common Repairs

### Menu Map Mistaken For Use Case Diagram

Symptom: use cases are screen names or buttons.

Repair: rename to goals or use a navigation/activity diagram.

### Internal Functions As Use Cases

Symptom: `Validate data`, `Call service`, `Map response`.

Repair: move internal steps to activity/sequence diagrams.

### Missing Boundary

Symptom: service/provider boundaries are ambiguous.

Repair: draw boundary and classify external systems as actors or neighboring systems.
