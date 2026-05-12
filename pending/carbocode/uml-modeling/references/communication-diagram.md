# Communication Diagram Deep Dive

Use a communication diagram to model collaborating participants and numbered messages across their links. It answers how participants are connected while still showing message order.

## Use When

- Collaboration topology matters more than vertical time layout.
- The same interaction is too wide or awkward as a sequence diagram.
- The reader needs to see object links and message ordering together.

Avoid when exact timing, activation, or vertical ordering is the main concern.

## Core Modeling Elements

- Participant/object.
- Link/connector.
- Numbered message.
- Condition or iteration marker when needed.

## Expansion Questions

- Are links real collaboration paths?
- Is message order simple enough to number clearly?
- Does topology explain the behavior better than a sequence diagram?
- Are participants runtime objects/roles, not packages?
- Which messages can be omitted without losing the collaboration story?

## Design Moves

- Arrange participants by collaboration structure.
- Number messages consistently.
- Keep message text short.
- Use conditions only where they change the collaboration.
- Prefer sequence diagram if numbering becomes hard to follow.

## Completeness Criteria

- The participant network is meaningful.
- Message order is understandable from numbering.
- Links are not arbitrary layout lines.
- The diagram emphasizes collaboration, not just flow.

## Common Mistakes And Repairs

- Complex numbering: switch to sequence diagram.
- Guessed links: remove or choose participants with known collaboration.
- Timing requirements hidden: use timing or sequence diagram.
- Static architecture disguised as collaboration: use component/class diagram.
