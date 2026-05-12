# Structure Diagram Design

Use this reference for class, object, package, component, composite structure, deployment, and profile diagrams.

## Structural Modeling Principle

A structure diagram says what exists and how it is related at a chosen abstraction level. It does not show temporal order.

If arrows mean "then this happens", use behavior/interaction diagrams instead.

## Class Diagrams

Model classifiers and structural relationships.

Include:

- classes/interfaces/data types/enumerations;
- relevant attributes/operations;
- associations with multiplicities when important;
- generalization/realization;
- dependencies where they communicate meaningful design coupling.

Avoid:

- dumping every method from code;
- using composition for any "has-a" reference;
- mixing data tables, services, UI components, and infrastructure at random levels.

Relationship guidance:

- Generalization: subtype/supertype.
- Realization: implements/specifies contract.
- Association: structural relationship.
- Aggregation: weak whole-part; use sparingly.
- Composition: strong ownership/lifetime dependency.
- Dependency: uses/depends on without structural link.

## Object Diagrams

Model one concrete snapshot.

Use to clarify:

- example object graph;
- specific values/slots;
- concrete runtime case.

Do not generalize from an object diagram; pair with a class diagram if type-level structure matters.

## Package Diagrams

Model namespaces, modules, and dependency boundaries.

Use to show:

- generated vs handwritten code;
- feature modules;
- layered architecture;
- dependency direction.

Avoid using packages as decorative folders around classes. The package dependency should carry design meaning.

## Component Diagrams

Model modular software units and interfaces.

Use to show:

- client application, integration client, service component, storage adapter, external service adapter;
- provided/required interfaces;
- replaceability and deployment-oriented components.

Avoid:

- class-level detail;
- runtime hardware nodes;
- package-only organization with no component responsibility.

## Composite Structure Diagrams

Model internal structure of a classifier/component.

Use when:

- ports/connectors matter;
- internal parts collaborate;
- the enclosing classifier is important.

Avoid when ordinary component/class diagrams are enough.

## Deployment Diagrams

Model runtime nodes and deployed artifacts.

Include:

- devices;
- execution environments;
- application artifacts;
- backend/server nodes;
- communication paths/protocols.

Avoid:

- class internals;
- generic "service boxes" with no runtime location.

## Profile Diagrams

Model extensions to UML itself.

Use when defining:

- stereotypes;
- tagged values;
- constraints;
- domain-specific modeling conventions.

Avoid when simply applying labels in an ordinary diagram.

## Structural Review Checklist

- Is the diagram timeless/structural rather than procedural?
- Is there one abstraction level?
- Do relationships mean what their notation says?
- Are containment/grouping relationships semantic?
- Are names nouns or classifier/component/node names?
- Are dependencies directional and justified?
- Would an activity/sequence/state diagram better answer the question?

## Common Repairs

### Component Diagram That Is Really A Package Diagram

Symptom: boxes are folders/namespaces; no interfaces or runtime responsibility.

Repair: use package diagram or add true component responsibilities and interfaces.

### Class Diagram That Is Really A Workflow

Symptom: arrows read as "calls then calls then calls".

Repair: use sequence/activity diagram for behavior; keep class diagram for stable types.

### Deployment Diagram That Is Really A Component Diagram

Symptom: no physical/runtime nodes, only logical services.

Repair: either add nodes/environments/artifacts or switch to component diagram.
