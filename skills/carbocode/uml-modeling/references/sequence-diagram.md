# Sequence Diagram Deep Dive

Use a sequence diagram to model ordered messages among participants over time. It answers who communicates with whom and in what order.

## Use When

- The user needs request/response behavior, service flow, authorization exchange, or coordination among participants.
- Ordering, alternatives, loops, or parallel sections matter.
- Runtime participants and their responsibilities need clarification.

Avoid when showing static dependencies, state inventory, class structure, or broad workflow without messages.

## Core Modeling Elements

- Lifeline.
- Message.
- Return message when clarifying information/control.
- Execution specification when useful.
- Combined fragment: alt, opt, loop, par, break, ref.
- Interaction use for referenced interactions.

## Expansion Questions

- Are lifelines runtime participants, roles, components, or external systems?
- Are messages actual communications?
- Which alternatives should be explicit?
- Which repeated behavior should be a loop?
- Does parallel behavior matter?
- Which return values clarify decisions?
- Is this too wide and better split?

## Design Moves

- Put the primary actor/initiator leftmost.
- Keep participants to the minimum set needed.
- Use business-level message names unless implementation detail is requested.
- Use `alt` for mutually exclusive branches and `opt` for optional behavior.
- Use `ref` when a repeated sub-interaction would clutter the diagram.
- Avoid showing every internal method call.

## Completeness Criteria

- Time order is readable top-to-bottom.
- Lifelines are meaningful participants.
- Alternatives and loops are not hidden in prose.
- Messages represent communication, not state labels or dependencies.
- The reader can trace responsibility and decision points.

## Common Mistakes And Repairs

- Packages as lifelines: use components/participants or switch to package diagram.
- Static dependency as message: use component/class/package diagram.
- Too many participants: split or lift abstraction.
- State changes as messages: use a state machine or timing diagram.
