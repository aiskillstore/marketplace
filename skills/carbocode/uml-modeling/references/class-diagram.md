# Class Diagram Deep Dive

Use a class diagram to model classifiers and stable structural relationships. It answers what kinds of things exist, what features they expose, and how those types relate.

## Use When

- The user needs a domain model, API model, implementation type model, or contract view.
- Relationships such as association, generalization, realization, dependency, and composition matter.
- Multiplicity, ownership, or type responsibility is important.

Avoid when the question is message order, workflow, lifecycle, or runtime topology.

## Core Modeling Elements

- Classifier: class, interface, data type, enumeration, signal.
- Feature: attribute, operation, property.
- Relationship: association, generalization, realization, dependency, aggregation, composition.
- Detail: multiplicity, role names, constraints, notes.

## Expansion Questions

- What abstraction level is this: conceptual domain, logical service model, implementation classes, generated types, persistence model?
- Does every box represent a type/classifier at that level?
- Which relationships need multiplicity to remove ambiguity?
- Does a whole-part relation imply lifetime ownership, or only reference/use?
- Are interfaces central enough to model explicitly?
- Are operations needed, or would responsibilities be clearer?

## Design Moves

- Prefer nouns for classifiers and verb phrases for operations.
- Show only attributes/operations that affect the diagram's purpose.
- Use the weakest correct relationship: dependency before association, association before composition.
- Add multiplicity when cardinality affects design, validation, or ownership.
- Split domain, persistence, UI, and integration classes unless the relation between those levels is the point.

## Completeness Criteria

- The viewpoint and abstraction level are clear.
- Every relationship means what its UML relationship says.
- Multiplicity is present where the reader needs cardinality.
- Inheritance represents substitutability or specialization, not code reuse alone.
- Composition is used only for strong whole-part lifetime ownership.

## Common Mistakes And Repairs

- Method dump: remove low-value operations and keep only behavior relevant to the question.
- Workflow arrows: replace with sequence or activity diagram.
- Overused composition: downgrade to association or dependency.
- Mixed levels: split into conceptual and implementation diagrams.
