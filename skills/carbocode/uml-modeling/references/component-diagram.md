# Component Diagram Deep Dive

Use a component diagram to model modular software units and their provided or required interfaces. It answers what software parts exist and how they depend on contracts.

## Use When

- The user needs logical software architecture.
- Components are replaceable, deployable, generated, reusable, or independently owned.
- Interfaces between presentation, integration client, service, storage adapter, authorization, or plugin components matter.

Avoid when the question is package namespace organization, class internals, or physical deployment.

## Core Modeling Elements

- Component.
- Provided interface.
- Required interface.
- Port when a component exposes several interaction points.
- Dependency, realization, assembly connector, delegation connector.

## Expansion Questions

- What makes each box a component rather than a package or class?
- Which interfaces are the real contracts?
- Which dependencies should be shown at component level?
- Which external systems should be components, actors, or deployment nodes?
- Are generated clients, adapters, or integration modules components in this view?

## Design Moves

- Name components by responsibility, not folder path.
- Show interfaces only where they explain coupling or replaceability.
- Keep class-level method detail out.
- Put external systems at the boundary and label the contract.
- Split logical component view from deployment view when nodes matter.

## Completeness Criteria

- Components have clear responsibilities.
- Provided/required interfaces are explicit where contracts matter.
- Dependencies are not merely call traces.
- The diagram can guide replacement, ownership, or integration decisions.

## Common Mistakes And Repairs

- Folders as components: use package diagram or rename by responsibility.
- No interfaces despite interface-focused intent: add provided/required contracts.
- Runtime hosts mixed in: move to deployment diagram.
- Too many low-level dependencies: lift to component-level relations.
