# Interaction Overview Diagram Deep Dive

Use an interaction overview diagram to model high-level control flow among interactions. It answers how several detailed interactions are sequenced or selected.

## Use When

- Multiple sequence/communication/timing diagrams exist and need navigation.
- The reader needs an overview of scenario branches.
- Each node can reference a separately defined interaction.

Avoid when a normal activity diagram with ordinary actions is enough.

## Core Modeling Elements

- Initial/final node.
- Decision/merge.
- Fork/join when high-level concurrent interactions exist.
- Interaction use/reference node.
- Control flow.

## Expansion Questions

- Is each major node an interaction, not a simple action?
- Which detailed interaction diagram does each node reference?
- Where are branches between scenarios?
- Are there reusable interactions?
- Would this be clearer as an activity diagram?

## Design Moves

- Name referenced interactions consistently.
- Keep the overview high-level.
- Put detailed messages in the referenced interaction diagrams.
- Use decisions for scenario selection.
- Avoid mixing low-level actions with interaction references.

## Completeness Criteria

- Every important node references or names a real interaction.
- The high-level path among scenarios is clear.
- Detail is delegated to separate interaction diagrams.
- The diagram adds navigation value beyond an activity diagram.

## Common Mistakes And Repairs

- Ordinary workflow: convert to activity diagram.
- Missing referenced interactions: create/note the detailed diagrams.
- Too much message detail: move it into sequence/communication diagrams.
- Inconsistent naming: align overview node names with referenced interaction titles.
