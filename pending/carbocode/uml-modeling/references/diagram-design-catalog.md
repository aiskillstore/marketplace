# UML Diagram Design Catalog

Baseline: OMG UML 2.5.1. Use this catalog to choose the right diagram form before choosing notation.

## UML Diagram Families

UML diagrams are commonly grouped into:

- structure diagrams;
- behavior diagrams;
- interaction diagrams, which are a behavior subfamily focused on communication.

Do not treat this as only a list of shapes. Each diagram type has a different modeling grammar.

## Structure Diagrams

### Class Diagram

Purpose: model classifiers, their features, and structural relationships.

Use when:

- explaining a domain model;
- designing APIs/classes/interfaces;
- showing associations, multiplicities, generalization, realization, dependencies;
- explaining data-bearing and behavior-bearing types.

Avoid when:

- the question is message order;
- the question is process flow;
- the question is runtime topology.

Design test:

- Can every box be understood as a type/classifier?
- Are relationships structural, not temporal?
- Are multiplicities meaningful and not decorative?

### Object Diagram

Purpose: show a concrete snapshot of instances and links.

Use when:

- explaining an example runtime configuration;
- showing values/slots for a specific case;
- debugging a confusing class model by grounding it in an instance.

Avoid when:

- describing all possible structures;
- documenting a workflow.

Design test:

- Are elements instances rather than types?
- Is the point in time clear?

### Package Diagram

Purpose: show namespace/module organization and dependencies.

Use when:

- explaining architecture layering;
- showing import/access/dependency among packages;
- separating generated code, domain code, UI code, infrastructure.

Avoid when:

- components/interfaces or runtime nodes are the main issue.

Design test:

- Are groups namespaces/modules?
- Are dependencies directional and meaningful?

### Component Diagram

Purpose: show modular software parts and provided/required interfaces.

Use when:

- describing services, libraries, clients, adapters, plugins;
- explaining replaceable/deployable software components;
- showing interface contracts among parts.

Avoid when:

- modeling classes inside the component;
- modeling physical servers and devices.

Design test:

- Are boxes cohesive software components?
- Are interfaces explicit where they matter?
- Are dependencies at component level, not class-call level?

### Composite Structure Diagram

Purpose: show internal parts, ports, connectors, and collaborations inside a structured classifier.

Use when:

- showing what is inside a component/classifier;
- modeling ports/connectors;
- explaining internal collaboration structure.

Avoid when:

- a normal component diagram or class diagram is sufficient.

Design test:

- Is there a clear enclosing structured classifier?
- Are parts internal to it?

### Deployment Diagram

Purpose: show runtime nodes, execution environments, deployed artifacts, and communication paths.

Use when:

- explaining client/server deployment;
- showing devices, servers, containers, runtimes;
- mapping artifacts to nodes.

Avoid when:

- the concern is class/module relationships.

Design test:

- Are nodes physical or execution environments?
- Are artifacts deployed to nodes?

### Profile Diagram

Purpose: define UML extensions using stereotypes, tagged values, and constraints.

Use when:

- creating a modeling language extension;
- documenting stereotypes for a domain;
- defining tool/profile conventions.

Avoid when:

- simply tagging boxes in one diagram.

Design test:

- Are stereotypes and metaclass extensions central?

## Behavior Diagrams

### Use Case Diagram

Purpose: show actors, user goals, and system boundary.

Use when:

- scoping requirements;
- explaining who gets value from the system;
- showing externally visible system capabilities.

Avoid when:

- modeling screens, buttons, internal functions, or procedural flow.

Design test:

- Is each use case a user goal?
- Is the system boundary explicit?

### Activity Diagram

Purpose: show workflow/control/object flow.

Use when:

- modeling user journey or business process;
- showing branching logic;
- explaining operational procedure;
- documenting algorithms or flows with decisions/forks/joins.

Avoid when:

- the subject is lifecycle states of one entity;
- ordered messages between participants are the main concern.

Design test:

- Are nodes actions?
- Are decision outputs guarded?
- Are partitions meaningful roles?

### State Machine Diagram

Purpose: show lifecycle/protocol of one stateful subject.

Use when:

- modeling resource lifecycle, authorization state, order state, connection mode, protocol state;
- showing allowed transitions and guards;
- distinguishing stable conditions from transition actions.

Avoid when:

- modeling a workflow involving many independent subjects;
- modeling one-time procedural steps.

Design test:

- Is there one subject?
- Are states persistent conditions?
- Are arrows triggered by events?

## Interaction Diagrams

### Sequence Diagram

Purpose: show ordered messages over time.

Use when:

- explaining request/response flow;
- documenting request/response, authorization, or integration sequences;
- showing alternatives/loops in participant communication.

Avoid when:

- showing static dependencies or lifecycle states.

Design test:

- Does time flow top-to-bottom?
- Are messages actual communications?

### Communication Diagram

Purpose: show collaborating objects/parts and numbered messages across links.

Use when:

- object network is more important than vertical time layout;
- sequence diagram is too linear but collaboration links matter.

Avoid when:

- detailed ordering/timing is central.

Design test:

- Are links meaningful structural connections?
- Are messages numbered enough to understand order?

### Timing Diagram

Purpose: show state/value changes along a time axis.

Use when:

- timing constraints matter;
- showing state/value changes of one or more lifelines over time;
- comparing parallel time-dependent behavior.

Avoid when:

- only ordinary message order is needed.

Design test:

- Is time the main dimension?
- Are states/values legible across intervals?

### Interaction Overview Diagram

Purpose: show high-level flow among interactions.

Use when:

- several detailed sequence/interaction diagrams need a control-flow overview;
- each node references another interaction.

Avoid when:

- a normal activity diagram with simple actions is enough.

Design test:

- Are nodes interactions or references to interactions, not ordinary actions?

## Selection Anti-Patterns

- Use case diagram used as a menu map.
- State machine used as a workflow checklist.
- Activity diagram used as a state inventory.
- Class diagram used as a deployment diagram.
- Component diagram used as a package dependency graph without interfaces.
- Sequence diagram used to show static dependency.
- One diagram combining class, sequence, state, and deployment concerns.

## Choosing Between Similar Forms

| If You Are Unsure Between | Choose This When | Otherwise |
| --- | --- | --- |
| State vs Activity | One entity has a lifecycle with allowed states. | Activity if many actions/branches form a process. |
| Sequence vs Activity | Participant message order matters. | Activity if actions/decisions matter more than who sends messages. |
| Component vs Package | Runtime/replaceable software parts and interfaces matter. | Package if namespaces/modules and dependencies matter. |
| Component vs Deployment | Software parts matter. | Deployment if nodes/devices/execution environments matter. |
| Class vs Object | Types and possible relationships matter. | Object if concrete instance snapshot matters. |
| Sequence vs Communication | Time order is primary. | Communication if object links/collaboration topology is primary. |
