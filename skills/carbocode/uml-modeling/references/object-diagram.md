# Object Diagram Deep Dive

Use an object diagram to model one concrete snapshot of instances and links. It answers what a particular runtime or example case looks like at one moment.

## Use When

- A class diagram is abstract and the user needs an example.
- A specific object graph, configuration, cache, session, or data case must be explained.
- Slot values and links clarify multiplicity, ownership, or optionality.

Avoid when describing all possible structures, process flow, or message order.

## Core Modeling Elements

- Object or instance, often named as `instanceName: Classifier`.
- Slot/value for relevant attributes.
- Link between instances.
- Optional note describing the scenario or timestamp.

## Expansion Questions

- What exact scenario or moment does this snapshot represent?
- Which instances are relevant to the point being explained?
- Which values must be shown to understand the case?
- Which links demonstrate a rule from the class model?
- Is this snapshot valid according to the intended class diagram?

## Design Moves

- State the scenario in the title or note.
- Keep only values that explain the example.
- Use object names when identity matters; use anonymous instances when it does not.
- Pair with a class diagram when readers need the general rule behind the snapshot.

## Completeness Criteria

- The moment/scenario is explicit.
- All shown links are concrete instance links, not type-level associations.
- Slot values are selected, not exhaustive dumps.
- The diagram does not pretend to be a complete type model.

## Common Mistakes And Repairs

- Types drawn as instances: convert to a class diagram.
- Missing context: add a scenario note.
- Too many values: keep only decision-relevant slots.
- Hidden workflow: use activity or sequence diagram for behavior.
