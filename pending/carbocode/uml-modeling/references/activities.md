# Activity Diagram Design

Use this reference for workflows, procedures, user journeys, business processes, algorithms, and operational runbooks.

## What An Activity Diagram Is For

An activity diagram models flow of control and/or objects among actions. It answers:

- What actions happen?
- In what order?
- Where does the flow branch or merge?
- What can happen concurrently?
- Which role/partition owns which action?
- What objects/data are produced or consumed?

## Action vs State

Activity nodes should be actions or control constructs.

Good action labels:

- `Start request`
- `Validate input`
- `Fetch metadata`
- `Compare version`
- `Show confirmation dialog`
- `Release resource lock`

Bad action labels:

- `Resource valid`
- `User authenticated`
- `Manual mode active`
- `Service unavailable`

Those are states/conditions and should be expressed as decision conditions, object states, notes, or a separate state machine.

## Flow Shape

A good activity usually has:

- trigger/start;
- major actions;
- decisions with guarded outgoing flows;
- merges where alternatives rejoin;
- fork/join only for real concurrency;
- stop or explicit continuation.

Do not start with a decision. Start with the event/action that makes the decision relevant.

## Decisions And Guards

Use decision nodes for questions. Label outgoing flows with guard-like answers.

Good:

- decision: `Input valid?`
- exits: `yes`, `no`

Avoid:

- decision: `if (resourceExpired && !serviceAvailable)`
- exits: raw code predicates.

Use process language unless the user asks for implementation traceability.

## Swimlanes / Partitions

Use partitions to show responsibility.

Good partitions:

- User
- Application
- Backend
- Data Store
- Payment Provider

Use internal service/class lanes only for implementation diagrams.

Do not create too many lanes. If more than five lanes are required, consider a sequence or component diagram.

## Object Flows

Use object nodes when data artifacts matter:

- `Request payload`
- `Generated report`
- `Checksum`
- `Authorization token`

Do not show every variable. Show data that changes decisions or crosses responsibilities.

## Concurrency

Use fork/join only when work is truly concurrent or independent.

Do not use fork merely to reduce vertical space.

## Activity Diagram Review Checklist

- The diagram describes a process, not a lifecycle.
- Node labels are verbs/actions.
- Decisions ask business/process questions.
- Guard labels are clear.
- Every branch has a terminal or rejoin.
- Lanes represent meaningful responsibility.
- Object flows are used only when data matters.
- No class/package/deployment relationships are hidden in the flow.

## Common Repairs

### Too Much Implementation Detail

Symptom: nodes are method names and booleans.

Repair: lift labels to user/system actions; add a traceability table after the diagram if needed.

### State Machine Hidden In Activity

Symptom: flow loops among `Draft`, `Approved`, `Archived`.

Repair: use a state machine for lifecycle and an activity diagram for processing procedures.

### Sequence Hidden In Activity

Symptom: lanes exchange many request/response actions.

Repair: use a sequence diagram if temporal messages are central.
