# Interaction Diagram Design

Use this reference for sequence, communication, timing, and interaction overview diagrams.

## Interaction Family

Interaction diagrams model communication among participants. They are not general flowcharts and not static dependency diagrams.

Core question:

- Which participants interact, and how is the interaction constrained by order, links, or time?

## Sequence Diagrams

Use when message order over time is the main concern.

Good participants:

- User
- Client
- Authorization Service
- External Service
- Repository
- Worker

Good messages:

- `submitRequest()`
- `authorize()`
- `fetchStatus()`
- `processCommand()`
- `publishResult()`

Design rules:

- Keep participants to the minimum set needed.
- Time flows top to bottom.
- Put business alternatives in `alt`.
- Put optional behavior in `opt`.
- Put repeated behavior in `loop`.
- Put concurrent behavior in `par`.
- Activation bars are optional; use them only when they clarify control/responsibility.
- A return message should clarify returned information only when needed.

Smells:

- Lifelines are classes/packages rather than runtime participants.
- Messages are states such as `Request approved`.
- Sequence is used to show architecture dependencies.
- Too many participants create unreadable horizontal sprawl.

## Communication Diagrams

Use when collaboration topology matters more than vertical time.

Design rules:

- Show participants/objects as nodes.
- Show links/associations between participants.
- Number messages to show order.
- Use when the same interaction is hard to read as a wide sequence diagram.

Smells:

- message numbering becomes complex;
- time ordering is actually the main topic;
- links are guessed rather than meaningful.

## Timing Diagrams

Use when state/value changes over time are the subject.

Good topics:

- authorization validity over time;
- resource expiration windows;
- service availability and resource use over intervals;
- sensor/control state timing.

Design rules:

- Choose a time scale or relative intervals.
- Use lifelines for state/value tracks.
- Keep labels terse.
- Mark constraints/deadlines explicitly.

Smells:

- no real timing constraints;
- ordinary sequence messages would be clearer.

## Interaction Overview Diagrams

Use when a high-level activity-like flow coordinates multiple interactions.

Design rules:

- Nodes should reference interactions, not ordinary low-level actions.
- Use when there are several sequence diagrams and the reader needs navigation.

Smells:

- used instead of a simple activity diagram;
- nodes are not interactions.

## Choosing Between Interaction Types

| Need | Use |
| --- | --- |
| Exact ordered request/response | Sequence |
| Object collaboration topology | Communication |
| State/value over time | Timing |
| Overview across multiple interactions | Interaction overview |

## Review Checklist

- Are participants real interacting parties?
- Are messages actual communications?
- Is the ordering/timing/link concern clear?
- Are alternatives/loops/parallel sections modeled explicitly?
- Is lifecycle state kept out unless it is carried by messages or a timing track?
- Would a component/activity/state diagram answer the question better?
