# UML Modeling Foundations

Use this reference before choosing a diagram type. It converts the official UML semantic framing into practical modeling decisions.

## The Model Has A Subject, Viewpoint, And Purpose

Every UML model should answer three questions before any boxes or arrows are drawn:

- What is the subject being modeled?
- From whose viewpoint is it being modeled?
- What decision or understanding should the diagram support?

If these are unclear, the diagram will usually collect unrelated facts: interface states, service calls, resource conditions, network availability, and user choices all become peers even though they belong to different subjects.

Practical rule: write a one-line model frame before drawing.

Examples:

- `Subject: order. Viewpoint: business lifecycle. Purpose: show when it is draft, submitted, approved, fulfilled, or cancelled.`
- `Subject: authorization flow. Viewpoint: runtime interaction. Purpose: show which participants exchange authorization messages.`
- `Subject: integration feature. Viewpoint: implementation structure. Purpose: show modules/components and their dependencies.`

## The Diagram Must Be Self-Contained

A UML diagram is a standalone model. It should not require access to the prompt, chat, source files, ticket, or project history to be understood.

Do not put meta-information in the diagram:

- no references to the user request;
- no notes about why the diagram was created;
- no "current project" or "existing code" wording;
- no labels that only make sense to the author;
- no unexplained acronyms or project-local nicknames;
- no placeholders such as `unknown`, `same as above`, `TODO`, or `assumed`.

Instead, make the model explicit:

- name the subject in the title;
- show the system or element boundary;
- name actors, participants, external systems, and stores generically but clearly;
- include a legend only for abbreviations that are intentionally compressed;
- express constraints as domain constraints, not as modeling caveats.

Practical rule: after drafting, read the diagram as if you know nothing about the project. If a label needs the surrounding conversation to make sense, rewrite it or add the missing model element.

## UML Statements Are Selective

A UML diagram is not a complete copy of the system. It is a set of selected statements about the system.

Include an element only if it helps answer the diagram's question.

Exclude:

- facts that are true but irrelevant;
- implementation detail at the wrong abstraction level;
- events, actions, or states that belong to a different subject;
- labels copied from code when the audience needs conceptual behavior.

Practical rule: if removing an element does not change the answer, remove it or move it to a note/table.

## Structural And Behavioral Semantics Are Different

Structural semantics describe what exists and how it is related.

Use structural forms for:

- classifiers, classes, interfaces, data types;
- parts, ports, components, packages;
- runtime nodes, execution environments, deployed artifacts;
- dependencies, associations, generalization, realization, deployment.

Behavioral semantics describe what happens over time.

Use behavioral forms for:

- actions and activities;
- events and transitions;
- states and lifecycle constraints;
- interactions and messages;
- timing, ordering, concurrency, guards, effects.

Practical rule: if an arrow means "is related to", prefer a structure diagram. If an arrow means "then this happens", prefer a behavior or interaction diagram.

## Stable Conditions And Transient Executions Are Not The Same

A common UML design error is turning an action into a state or a state into an action.

Stable condition:

- can persist;
- can be observed over an interval;
- can constrain allowed behavior.

Examples:

- `Draft`
- `Approved`
- `Available`
- `Authorized`
- `In use`
- `Unavailable`

Transient execution:

- happens during a transition or workflow;
- has a beginning and an end;
- usually produces or checks a condition.

Examples:

- `Validate request`
- `Generate report`
- `Open connection`
- `Show dialog`
- `Call service`

Practical rule: in a state machine, use actions as transition effects, entry/exit/do behavior, or move them to an activity diagram.

## Diagram Types Are Grammars

Do not treat UML diagram types as interchangeable drawing styles. Each has a grammar:

- class diagram: classifiers and structural relationships;
- object diagram: instance snapshot;
- package diagram: namespaces and package dependencies;
- component diagram: software components and interfaces;
- composite structure diagram: internal parts, ports, and connectors;
- deployment diagram: nodes, execution environments, artifacts;
- profile diagram: stereotypes, tagged values, metaclass extensions;
- use case diagram: actors, goals, and subject boundary;
- activity diagram: actions, control flow, object flow, decisions, concurrency;
- state machine diagram: states, events, transitions, guards, effects;
- sequence diagram: lifelines and ordered messages;
- communication diagram: participant links and numbered messages;
- timing diagram: state/value changes over time;
- interaction overview diagram: control flow among interactions.

Practical rule: when a needed element does not belong to the selected grammar, either translate it correctly or split the diagram.

## One Primary Subject Per Diagram

Many bad diagrams fail because they mix subjects:

- client connection state;
- resource validity;
- user confirmation choice;
- external service availability;
- background job lifecycle;
- resource lock state.

These may interact, but they are not necessarily states of the same thing.

Practical rule: choose the primary subject, then model other concerns as:

- events;
- guards;
- transition effects;
- external actors/participants;
- constraints;
- notes;
- separate linked diagrams.

Example:

- For an order state machine, `service available` is usually a guard or external event, not a peer state of the order.
- For a connection state machine, `resource valid` is usually a guard/condition, not a connection state.

## Containment Must Mean Containment

Grouping is semantic, not decorative.

Use containment when:

- a composite state owns substates;
- a package owns packageable elements;
- a component owns internal parts;
- a system boundary owns use cases;
- a node contains deployed artifacts or execution environments.

Do not group only because items are visually related. If the group means "these are associated topics", use a note, legend, or separate section instead.

Practical rule: before adding a boundary box, ask what UML relationship the boundary represents.

## Guards, Events, Effects, And Conditions

For behavior diagrams, keep these roles distinct:

- event: something happens;
- guard: a condition that must be true;
- effect: action performed because the transition occurs;
- state/condition: a stable situation before or after behavior;
- decision: routing point in a workflow;
- message: communication between participants.

Bad state-machine label:

`Request valid and service available, fetch details and compare version`

Better state-machine split:

`Pending --> Verifying : service available / fetch details`

`Verifying --> Approved : version accepted / record approval`

`Verifying --> RevisionRequired : version rejected / request correction`

The exact shape may vary, but the semantic roles should not be collapsed into one long arrow.

## Abstraction Level Must Stay Consistent

Pick one abstraction level:

- conceptual: domain ideas and responsibilities;
- logical: modules, components, services, stateful concepts;
- implementation: classes, methods, APIs, storage objects;
- runtime: processes, devices, containers, deployed artifacts;
- physical: hardware, networks, physical nodes.

Mixing levels is allowed only when the diagram type is designed for that relation, such as deployment mapping artifacts to nodes.

Practical rule: if a diagram contains both `User requests approval` and `ApprovalDialogService.requestConfirmation()`, either lift the method label or split conceptual and implementation diagrams.

## Completeness Does Not Mean Exhaustiveness

A complete UML diagram includes the elements needed to understand the modeled question. It does not include every possible state, class, branch, field, or API call.

Completeness checks:

- Is the subject clear?
- Is the boundary clear?
- Are all shown relationships meaningful?
- Are important alternatives represented?
- Are impossible transitions omitted?
- Are assumptions explicit?
- Can the audience answer the original question without reading source code?

If the answer is yes, the model is complete enough.
