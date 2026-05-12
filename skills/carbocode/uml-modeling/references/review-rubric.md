# UML Review Rubric

Use this reference when reviewing, repairing, or replacing a UML diagram.

## Review Order

1. Identify the diagram's intended question.
2. Identify the current diagram type.
3. Decide whether the diagram type is appropriate.
4. Check semantic correctness.
5. Check abstraction level.
6. Check self-containment and absence of meta leakage.
7. Check boundaries and ownership.
8. Check visual form.
9. Check notation and layout last.

Do not begin with spacing, arrow shape, or notation details unless the user explicitly asks only for a notation fix.

## Severity Levels

### Critical

The diagram is the wrong UML type or misrepresents the system.

Examples:

- state machine used for a procedure;
- use case diagram full of internal methods;
- deployment diagram showing classes but no nodes;
- composition used where there is no lifecycle ownership.
- diagram cannot be understood without knowing the prompt, chat, repository, or project-specific context.

### Major

The type is plausible but semantics are wrong or confusing.

Examples:

- actions represented as states;
- sequence messages are not communications;
- activity decisions have unclear guards;
- component interfaces are missing where interface contracts are the point.
- titles, notes, labels, or legends leak request wording, task history, or implementation process.
- important actors, boundaries, external systems, acronyms, or constraints are left implicit.

### Minor

The model is basically correct but visual/wording choices reduce readability.

Examples:

- arrow labels too long;
- avoidable line crossings;
- inconsistent naming;
- missing legend for compressed labels.

## Universal Checklist

- What question does this diagram answer?
- Who is the intended reader?
- What is the subject?
- What is the system boundary?
- What abstraction level is used?
- Can an external reader understand the diagram without the surrounding request?
- Does any label leak prompt wording, conversation context, task history, or project-local shorthand?
- Are acronyms, external systems, and important constraints explicit enough?
- Are all elements at that level?
- Are relationships semantically correct?
- Are labels grammatically appropriate to the diagram type?
- Is anything present only because it exists in code?
- Could two smaller diagrams answer better?

## Type-Specific Red Flags

### State Machine

- More than one lifecycle-bearing subject.
- States named as verbs.
- Transitions named as conditions only, with no event.
- Effects modeled as target states.
- interface, connection, resource, and authorization states mixed as peers without a clear subject.

### Activity

- Nodes are states/nouns.
- Starts with a decision.
- Guard labels are raw code.
- Forks do not represent true concurrency.
- No stop/continuation on terminal paths.

### Sequence

- Lifelines are packages instead of participants.
- Messages are states or dependencies.
- Alternative/loop behavior hidden in prose.
- Too many participants.

### Class

- Every code method dumped into classes.
- Multiplicities missing where relationship cardinality matters.
- Composition used for simple references.
- Temporal flow shown with associations.

### Component

- Components are just folders.
- No provided/required interfaces where interface design is central.
- Class internals are shown at component level.

### Deployment

- No runtime nodes.
- Artifacts/components not mapped to execution environments.
- Logical architecture confused with physical topology.

### Use Case

- Use cases are buttons/screens/functions.
- Internal services are actors.
- Boundary unclear.
- `include` and `extend` used for ordinary sequence of steps.

## Repair Patterns

### Replace The Diagram Type

Use when the form is fundamentally wrong.

Example:

- User asks for state diagram but wants processing procedure -> create activity diagram and explain why.
- User asks for class diagram but wants service calls -> create sequence or component diagram.

### Split The Diagram

Use when two valid questions are mixed.

Example:

- Order lifecycle -> state machine.
- Order submission procedure -> activity diagram.
- Service calls during submission -> sequence diagram.

### Lift Or Lower Abstraction

Use when labels mix business and implementation levels.

Example:

- replace `ApprovalDialogService.requestConfirmation()` with `Request user confirmation` in process-level diagrams;
- keep method names only in implementation sequence diagrams.

### Convert Actions To Transition Effects

Use when a state machine has action-states.

Example:

- `Validate request` becomes transition `submit [request valid] / record submission`.

### Convert States To Decision Conditions

Use when an activity diagram has state-nodes.

Example:

- `Order approved` becomes decision `Order approved?`.

## Visual Quality Checklist

- Diagram title names the modeled subject, not the user's request.
- Labels are short.
- Notes explain domain constraints, not request context or production history.
- Groups represent real semantic containment.
- Crossings are minimized by model organization.
- Legend exists if labels are compressed.
- Diagram is split if it needs excessive spacing.

## Final Response Pattern For Reviews

When reviewing a UML diagram, answer in this order:

1. Verdict on diagram type.
2. Main semantic issues.
3. Proposed model shape.
4. Corrected diagram or next edit.
5. Missing domain facts that must be clarified before the diagram can stand alone.
