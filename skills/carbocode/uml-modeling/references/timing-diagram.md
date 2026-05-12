# Timing Diagram Deep Dive

Use a timing diagram to model state or value changes over a time axis. It answers how conditions evolve over intervals and where timing constraints apply.

## Use When

- Time, duration, deadlines, validity windows, authorization validity, or expiry intervals matter.
- Several lifelines need comparison over time.
- State/value changes are more important than messages.

Avoid when ordinary message ordering or workflow is enough.

## Core Modeling Elements

- Lifeline.
- State or value track.
- Time axis.
- Event marker.
- Duration or time constraint.
- Message when causal communication matters.

## Expansion Questions

- What time scale or relative interval matters?
- Which state/value tracks are essential?
- Which deadlines, expirations, or validity windows constrain behavior?
- Which events cause changes?
- Does the audience need exact timing or only ordering?

## Design Moves

- Keep the number of tracks small.
- Label intervals with states/values, not actions.
- Mark constraints directly on the time axis.
- Use sequence diagrams when messages dominate.
- Use state machine diagrams when valid transitions matter more than elapsed time.

## Completeness Criteria

- Time is the primary dimension.
- Each track has clear states or values.
- Constraints are visible.
- Causal events are shown when they explain changes.

## Common Mistakes And Repairs

- No timing constraint: use sequence or state machine diagram.
- Too many lifelines: split by concern.
- Actions as intervals: convert to states/values or use activity diagram.
- Hidden lifecycle rules: pair with a state machine.
