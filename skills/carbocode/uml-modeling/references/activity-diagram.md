# Activity Diagram Deep Dive

Use an activity diagram to model workflow, control flow, object flow, decisions, and concurrency. It answers what actions happen and how the flow moves.

## Use When

- The user needs a procedure, business process, algorithm, user journey, or operational flow.
- Decisions, branches, merges, forks, joins, and responsibilities matter.
- Data artifacts moving through the process are important.

Avoid when the subject is the lifecycle of one thing or ordered messages among participants.

## Core Modeling Elements

- Action.
- Control flow.
- Object flow.
- Decision and merge.
- Fork and join.
- Initial and final nodes.
- Activity partition.
- Object node.

## Expansion Questions

- What event or action starts the activity?
- Are node labels actions, not states?
- Which decisions need explicit guards?
- Which branches rejoin and which terminate?
- Is concurrency real, or just visual parallelism?
- Which responsibilities deserve partitions?
- Which data objects affect later decisions?

## Design Moves

- Use verb phrases for action nodes.
- Put stable conditions on guards, object states, or notes, not as action nodes.
- Label outgoing decision flows with short guarded answers.
- Use partitions for responsibility, not visual sorting.
- Use object nodes only for data that affects behavior or crosses responsibilities.
- Keep raw code predicates out unless the audience is implementation-level.

## Completeness Criteria

- Flow has a clear trigger/start.
- Every branch is guarded and either rejoins or ends intentionally.
- Forks and joins represent real concurrency.
- Partitions are few and meaningful.
- The process can be followed without source code.

## Common Mistakes And Repairs

- State machine hidden in activity: convert stable lifecycle conditions to a state machine.
- Sequence hidden in activity: switch to sequence when request/response messages are central.
- Starts with a decision: add the action/event that makes the decision relevant.
- Raw boolean labels: rewrite as process-level guards.
