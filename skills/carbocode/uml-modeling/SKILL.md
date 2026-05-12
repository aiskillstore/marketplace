---
name: uml-modeling
description: Design, critique, and revise UML diagrams from a modeling and communication perspective. Use when Codex is asked to create or improve UML; when the user asks for a graphical representation, diagram, schema, visual model, process map, state view, architecture view, or system representation of software/system behavior or structure; when the user does not explicitly choose UML but needs a model-like visual explanation; when Codex must autonomously choose the right UML diagram type or split across multiple UML diagrams. Use for reasoning about diagram form, abstraction level, boundaries, grouping, lifecycle/state design, behavior vs structure, interaction design, or diagnosing why a diagram feels wrong at the modeling level. This skill treats notation as the final representation, not as the core task.
---

# UML Modeling

## Purpose

Use this skill to design UML, not merely to emit diagram text. The goal is a model that is semantically correct, visually legible, audience-appropriate, and useful for the decision the user needs to make.

Also use this skill when the user asks generically for a graphical representation, schema, diagram, or visual explanation of a software/system concern and does not name UML. In that case, infer whether UML is appropriate and choose the UML diagram type autonomously.

Treat UML as a modeling language with forms of thought:

- structural form: what exists and how it is organized;
- behavioral form: what happens and how behavior is constrained;
- interaction form: who communicates with whom, in what order or timing;
- extension form: how the modeling language is tailored.

Only after the model is conceptually right should you choose a notation or documentation format.

## Non-Negotiable: Self-Contained UML, No Meta Leakage

Every UML diagram must stand on its own for an external reader who has no prior knowledge of the project, conversation, source files, or user request.

This is mandatory for every diagram:

- Do not include meta-information about the prompt, conversation, requester, repository, task history, uncertainty, or how the diagram was produced.
- Do not leak user-request wording into titles, notes, labels, legends, or diagram comments.
- Do not use labels that only make sense to someone who already knows the project.
- Do not rely on implicit context, hidden assumptions, unexplained acronyms, unnamed boundaries, or unnamed external systems.
- Do not write labels such as `as requested`, `current project`, `existing code`, `the user`, `this service`, `same as above`, `TODO`, `unknown`, or `assumed`.
- Make the modeled subject, scope, boundary, actors/participants, external systems, and important constraints explicit inside the model when they are needed for understanding.
- If a fact is necessary to understand the UML and cannot be inferred safely, ask for clarification before finalizing or use a neutral, explicit domain name such as `External Service`, `Authorization Provider`, or `Data Store`.

UML is not a transcript of the request. It is a standalone model of the subject.

## Knowledge Priority

Use the bundled references as the operational knowledge base:

1. Treat the reference files in this skill as the already-digested UML modeling guidance.
2. Prefer the specific diagram deep dive over the general catalog when working on one diagram type.
3. Prefer `modeling-foundations.md` when the problem is semantic: subject, viewpoint, state vs action, structure vs behavior, boundaries, or abstraction level.
4. Use external official UML material only when maintaining or updating this skill, or when the bundled references are insufficient for a specific unresolved semantic conflict.
5. Use notation/tool documentation only after the UML form is chosen.

Read references as needed:

- `references/modeling-foundations.md`: semantic foundations extracted from the official UML specification and converted into modeling rules.
- `references/uml-form-and-design.md`: modeling method and form principles.
- `references/diagram-design-catalog.md`: complete UML diagram catalog and selection guidance.
- `references/diagram-type-playbooks.md`: index of the per-diagram deep dives.
- `references/state-machines.md`: state machine design, lifecycle modeling, composite states, anti-patterns.
- `references/activities.md`: activity diagram design, control/object flow, decisions, partitions.
- `references/interactions.md`: sequence, communication, timing, and interaction overview design.
- `references/structure-diagrams.md`: class, object, package, component, composite structure, deployment, profile design.
- `references/use-cases.md`: actor-goal modeling and system boundaries.
- `references/review-rubric.md`: semantic review checklist and repair workflow.

For a specific diagram type, load only the matching deep dive:

- `references/class-diagram.md`
- `references/object-diagram.md`
- `references/package-diagram.md`
- `references/component-diagram.md`
- `references/composite-structure-diagram.md`
- `references/deployment-diagram.md`
- `references/profile-diagram.md`
- `references/use-case-diagram.md`
- `references/activity-diagram.md`
- `references/state-machine-diagram.md`
- `references/sequence-diagram.md`
- `references/communication-diagram.md`
- `references/timing-diagram.md`
- `references/interaction-overview-diagram.md`

## Mandatory Workflow

### 0. Recognize Implicit Diagram Requests

Recognize intent categories, not exact phrases. Treat a request as a possible UML modeling request even when the word "UML" is absent if the user asks to:

- create a diagram, schema, graphical representation, or visual model;
- represent states, modes, lifecycle, availability, validity, or expiration;
- explain a flow, process, procedure, algorithm, or sequence of steps;
- draw architecture, topology, modules, components, packages, or deployment;
- map relationships, dependencies, ownership, containment, or interfaces;
- visualize interactions, messages, timing, actors, or responsibilities.

Apply this recognition regardless of the user's language. Do not rely on locale-specific phrase matching.

Use UML when the subject is software, architecture, state, workflow, interaction, deployment, domain structure, or system behavior. If the user asks for a purely decorative image, infographic, chart, or non-model visual, do not force UML.

When UML is appropriate and the user did not specify a type, choose the type yourself. Ask a clarification only when two materially different interpretations would produce different, risky models.

### 1. Frame The Modeling Problem

Before drawing, identify:

- the diagram's audience: developer, architect, analyst, product owner, tester, operator;
- the question the diagram must answer;
- the subject being modeled;
- the boundary of the system or element;
- the abstraction level: conceptual, logical, implementation, runtime, physical;
- whether the model describes structure, behavior, interaction, or deployment.

If the user asks for a diagram type that does not match the intent, say so briefly and choose the correct type. If the user did not name a type, do not ask them to choose one unless the modeling subject is ambiguous.

### 2. Choose The UML Form Autonomously

Choose one primary diagram type. Do not blend diagram types just to include everything.

Use this quick decision tree:

- "What are the types/modules/components/nodes and relationships?" -> structure diagram.
- "What is the lifecycle of one thing?" -> state machine diagram.
- "What steps happen in a workflow?" -> activity diagram.
- "What messages happen over time?" -> sequence diagram.
- "What user goals exist at the system boundary?" -> use case diagram.
- "Where does software run?" -> deployment diagram.
- "How do runtime instances look at one moment?" -> object diagram.
- "How should UML be extended for this domain?" -> profile diagram.

Use more than one UML diagram only when the user is really asking more than one modeling question. For example, a stateful subsystem may need a state machine for lifecycle and a sequence diagram for external calls, but those should be separate diagrams with separate purposes.

### 3. Model Semantics Before Layout

Draft the semantic inventory first:

- elements;
- relationships;
- events and transitions;
- actions/activities;
- actors and system boundary;
- messages and ordering;
- nodes/artifacts;
- constraints and notes.

Then remove anything that does not answer the diagram's main question.

### 4. Design The Form

Apply visual/form rules:

- the diagram must be understandable without the surrounding chat, documentation, or source files;
- one diagram, one main question;
- one abstraction level per diagram;
- group by semantic containment, not decoration;
- prefer fewer stronger labels over many long labels;
- place stable/static things before dynamic annotations;
- avoid crossing lines by reorganizing responsibility, not only by spacing;
- use notes for explanation, not to compensate for wrong modeling;
- use legends for compressed labels;
- split when the diagram needs two different grammars.

### 5. Validate Against UML Semantics

Use the relevant checklist from `references/review-rubric.md`.

Examples:

- In a state machine, a state is a condition that can persist. "Validate request" is normally an activity/action, not a state.
- In an activity diagram, nodes are actions and control/object flows. "Order approved" is normally a state/condition, not an action.
- In a use case diagram, use cases are user goals, not buttons, pages, or internal functions.
- In a sequence diagram, messages are ordered interactions, not dependencies.
- In a class diagram, composition implies strong whole-part lifetime ownership, not just "has a reference".

### 6. Notation Last

Only after the model is correct, choose notation:

- a textual diagram notation when the repository or user asks for one;
- Markdown tables or prose when UML would overcomplicate;
- a split set of diagrams when one notation surface would distort the model.

Notation is subordinate to modeling. If a requested notation pushes the model into a wrong shape, change the notation, split the diagram, or explicitly tell the user that the requested representation is distorting the UML form.

## When Fixing A Bad Diagram

Use this order:

1. Identify the intended question.
2. Identify the actual diagram type and the diagram type it should be.
3. Name the semantic errors first.
4. Redesign the model form.
5. Only then repair notation/layout.

Do not keep polishing a diagram that is the wrong UML type.

## Completion Standard

A finished UML answer should usually include:

- the chosen UML diagram type and why;
- the diagram;
- a short legend only if labels were intentionally compressed;
- explicit model boundaries and domain constraints needed to understand the diagram;
- a note when a requested diagram type was changed for semantic correctness.

For documentation edits, preserve the surrounding language and style, but improve the modeling quality even if that means replacing the diagram rather than tweaking it.
