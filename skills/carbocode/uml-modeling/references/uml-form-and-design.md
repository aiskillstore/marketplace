# UML Form And Design Method

This reference is about designing the model, not about notation mechanics.

## The Modeling Contract

Every UML diagram should have a contract:

- **Subject**: the system, subsystem, object, interaction, deployment, or process being modeled.
- **Audience**: who must understand or use the diagram.
- **Question**: the one main question the diagram answers.
- **Viewpoint**: conceptual, logical, implementation, runtime, operational, physical.
- **Boundary**: what is inside and outside the model.
- **Level**: business/domain, architecture, design, code, runtime instance, infrastructure.
- **Time stance**: timeless structure, point-in-time snapshot, lifecycle over time, process flow, message order, physical deployment.

If any item is missing, fill it before drawing.

## UML Form Families

### Structural Form

Use structural form when the diagram says "these things exist and relate".

Good structural questions:

- What types or modules exist?
- What contains what?
- What depends on what?
- What interface does this component expose?
- Where is this artifact deployed?
- What runtime objects exist in this snapshot?

Bad structural diagram smells:

- arrows are actually temporal steps;
- classes/components are named as verbs;
- associations hide workflow order;
- implementation files are dumped without modeling purpose;
- composition is used for visual nesting rather than lifetime ownership.

### Behavioral Form

Use behavioral form when the diagram says "this happens or changes".

Good behavioral questions:

- Which states can this thing be in?
- Which event moves it from one state to another?
- What workflow path does the user/system follow?
- Which actions run in sequence, branch, or parallel?

Bad behavioral diagram smells:

- stable states and transient actions are mixed;
- decision diamonds replace actual states;
- states are verbs such as "send request";
- activity actions are nouns such as "Request approved";
- multiple unrelated lifecycle-bearing subjects appear in one state machine.

### Interaction Form

Use interaction form when the diagram says "participants communicate".

Good interaction questions:

- Which participant sends the message?
- Which participant receives it?
- What is the order?
- Which alternatives/loops/parallel sections exist?
- Is timing or ordering the main concern?

Bad interaction diagram smells:

- dependencies are shown as messages;
- object state lifecycle is modeled as messages only;
- sequence messages are labeled with business states;
- too many participants create a timeline nobody can read.

### Deployment/Operational Form

Use deployment form when the diagram says "this runs here".

Good operational questions:

- Which device/node hosts which execution environment?
- Which artifacts are deployed?
- Which protocols or communication paths exist?
- What external systems are physically or logically connected?

Bad deployment diagram smells:

- business classes appear as deployed artifacts;
- components are confused with nodes;
- runtime topology is mixed with code package dependencies.

## Abstraction Levels

Do not mix levels unless the diagram explicitly explains the mapping.

### Conceptual

Purpose: shared domain language.

Good elements: domain concepts, business actors, user goals, major states.

Avoid: code classes, database tables, APIs, internal service names.

### Logical/Design

Purpose: design responsibilities and collaborations.

Good elements: logical components, classes, interfaces, state machines, interaction protocols.

Avoid: physical servers unless deployment matters.

### Implementation

Purpose: code mapping and maintainability.

Good elements: modules, classes, packages, APIs, generated clients, files when meaningful.

Avoid: business-only wording that hides actual dependencies.

### Runtime

Purpose: actual objects/processes/messages at execution time.

Good elements: instances, lifelines, deployed artifacts, active runtime states.

Avoid: generic type diagrams unless showing type-instance mapping.

### Physical

Purpose: environment and infrastructure.

Good elements: devices, containers, VMs, client applications, networks, deployed artifacts.

Avoid: class internals.

## Grouping Rules

Group only when a real modeling relationship exists:

- package ownership;
- component internal structure;
- composite state/substate;
- deployment containment;
- system boundary;
- interaction frame;
- activity partition.

Do not group merely to make the layout tidy. If grouping is visual only, use a note or split the diagram.

## Naming Rules

Names reveal whether the diagram form is right.

- States: nouns/adjectives: `Draft`, `Approved`, `Logged in`, `Payment authorized`.
- Transitions/events: event phrases: `validity elapsed`, `user confirms request`, `approval received`.
- Transition actions: imperative effects after `/`: `/ release resource`, `/ record approval`.
- Activities/actions: verb phrases: `Fetch metadata`, `Validate request`, `Show confirmation dialog`.
- Use cases: user-goal verb phrases: `Search records`, `Submit order`.
- Classes/components: noun phrases: `ApprovalWorkflowService`, `RecordRepository`, `Integration Client`.
- Messages: operations/signals: `getStatus()`, `submitRequest()`, `availabilityChanged`.

If labels do not fit the expected grammatical form, reconsider the diagram type.

## Diagram Splitting Rules

Split one diagram into multiple diagrams when:

- it answers more than one main question;
- it mixes lifecycle and workflow;
- it mixes runtime messages with static architecture;
- it needs both user-facing and implementation-level language;
- line crossings cannot be fixed without distorting meaning;
- a legend becomes longer than the diagram.

Prefer a small scenario map plus several precise diagrams over one overloaded diagram.

## Completeness Without Clutter

Complete does not mean every possible element. Complete means enough to answer the chosen question without hidden assumptions.

A complete UML design includes:

- correct diagram type;
- explicit subject and boundary;
- all semantically necessary nodes;
- necessary relationships/events/guards/actions;
- no unrelated implementation detail;
- notes for non-obvious assumptions;
- legend if labels are compressed;
- consistency with adjacent diagrams.

## Repair Strategy

When a diagram feels wrong:

1. State what question it is trying to answer.
2. Identify the actual form it currently uses.
3. Identify the correct UML form.
4. List semantic violations.
5. Redesign the model inventory.
6. Draw the minimal correct diagram.
7. Add notation/layout details.

Do not rescue a wrong form by adding more arrows, notes, groups, or spacing.
