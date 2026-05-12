# Package Diagram Deep Dive

Use a package diagram to model namespace, module, and dependency organization. It answers how model elements or code areas are grouped and how those groups depend on one another.

## Use When

- The user needs architecture layering, modular boundaries, or dependency direction.
- Generated code, handwritten code, features, libraries, or domains need separation.
- Package import/access or package-level dependency is the meaningful relation.

Avoid when replaceable software components, runtime nodes, or class internals are the main concern.

## Core Modeling Elements

- Package or model.
- Packageable element when needed.
- Dependency, import, access.
- Package merge only when intentionally modeling merged package content.
- Constraint or note for layering rules.

## Expansion Questions

- Are packages namespaces, features, layers, ownership areas, or build modules?
- Which dependencies are allowed?
- Which dependencies are forbidden?
- Are there generated packages that should remain isolated?
- Is the diagram conceptual, logical, or implementation-level?

## Design Moves

- Arrange packages by dependency direction or layer.
- Avoid nesting unless containment is real namespace ownership.
- Use notes for architecture rules such as "UI must not depend on infrastructure".
- Keep class detail out unless a representative element clarifies package purpose.

## Completeness Criteria

- Every package is a real namespace/module boundary.
- Dependencies are directional and justified.
- The reader can infer allowed coupling.
- The diagram does not pretend packages are runtime components.

## Common Mistakes And Repairs

- Decorative folders: remove or convert to real package dependencies.
- Runtime communication shown as dependency: consider component, deployment, or sequence diagram.
- Too much nesting: flatten unless the namespace hierarchy matters.
- Component concerns hidden in packages: switch to component diagram.
