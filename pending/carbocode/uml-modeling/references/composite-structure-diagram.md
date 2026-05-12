# Composite Structure Diagram Deep Dive

Use a composite structure diagram to model the internal parts, ports, and connectors of one structured classifier. It answers how something is built internally.

## Use When

- The user needs to see inside a component, class, subsystem, or collaboration.
- Ports and connectors explain behavior better than ordinary dependencies.
- Internal parts and their roles matter.

Avoid when there is no clear enclosing classifier, or when a class/component diagram is enough.

## Core Modeling Elements

- Structured classifier as the enclosing subject.
- Part/property.
- Port.
- Connector.
- Collaboration or collaboration use when roles matter.

## Expansion Questions

- What is the single enclosing classifier?
- Which parts are truly internal to it?
- Which ports are externally visible contact points?
- Which connectors represent internal communication or binding?
- Are parts typed by classifiers that should be defined elsewhere?

## Design Moves

- Draw the enclosing classifier boundary clearly.
- Put internal parts inside that boundary only when they are owned/contained.
- Use ports to show boundary roles, not decoration.
- Use connectors to show meaningful internal relationships.
- Keep package/module dependencies out of the internal view.

## Completeness Criteria

- The enclosing subject is explicit.
- All parts belong to the subject.
- Ports explain external interaction.
- Connectors explain internal collaboration.
- The diagram does not become a generic architecture map.

## Common Mistakes And Repairs

- Free-floating components: convert to component diagram.
- Decorative grouping: remove boundary or define the classifier it represents.
- Package dependencies inside: move to package/component diagram.
- Missing ports for boundary behavior: add only the ports that clarify responsibility.
