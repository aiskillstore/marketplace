# State Machine Diagram Design

Use this reference when modeling lifecycle, modes, protocols, availability, validity, authorization, expiration, or any condition-based behavior of one subject.

## What A State Machine Is For

A state machine models the lifecycle of one stateful subject. It answers:

- What stable states can the subject be in?
- Which events can occur in each state?
- Which transitions are allowed?
- Which guards constrain transitions?
- Which effects happen on transitions?
- Which states contain substates?

The subject must be explicit: e.g. "order", "user session", "background job", "authorization grant", "resource lock".

## State vs Action

Use a state for a condition that can persist.

Good states:

- `Not installed`
- `Installed`
- `Valid`
- `Expired`
- `In use`
- `Authorized`
- `Waiting for user confirmation`
- `Processing` only if the system can remain there asynchronously.

Bad states:

- `Run validation`
- `Validate request`
- `Show popup`
- `Release lock`
- `Compare versions`

Those are usually transition effects or activities.

## Transition Form

Preferred semantic form:

`source --> target : event [guard] / effect`

Examples:

- `Valid --> Expired : validity elapsed / mark unavailable`
- `Expired --> Valid : renewal accepted / extend validity`
- `Active --> Invalid : validation failed / clear availability`
- `Pending --> Active : activation completed [resource valid] / save timestamp`

Rules:

- Event: what happened.
- Guard: condition that must be true.
- Effect: what the system does during the transition.
- Do not put long explanations on arrows; use short labels and a legend.

## Composite States

Use a composite state when a state has internal lifecycle detail.

Good examples:

- `Active` containing `Valid`, `Expired`, `Invalid`.
- `Authorized` containing `Grant valid`, `Refreshing grant`.
- `In use` containing `Locked`, `Reading`, `Releasing` if those substates matter.

Avoid composite states when:

- the grouping is decorative;
- the substates are not exclusive;
- the inner states belong to a different subject.

## Orthogonal Regions

Orthogonal/concurrent regions are for simultaneous independent state dimensions of the same subject.

Use only if:

- two state dimensions are active at the same time;
- each dimension can transition independently;
- the audience can understand the combined model cleanly;
- the audience needs to see both dimensions in one model.

If the combined model becomes hard to read, split into two state machines plus a short invariant table.

Example invariant table:

| Resource validity | Resource use | Allowed? |
| --- | --- | --- |
| Valid | In use | yes |
| Valid | Not in use | yes |
| Expired | In use | no |
| Expired | Not in use | yes |

## Modeling "In Use"

Model "in use" carefully.

Questions:

- Is "in use" a state of the same subject?
- Is it exclusive with "not in use"?
- Can it only happen while another state, such as `Valid`, is true?

If "in use" is subordinate to `Valid`, put it inside `Valid` or express an invariant.

If "validity" and "use" are truly independent dimensions, use orthogonal regions or split diagrams.

Do not force "in use" into the diagram only because the interface has a toggle. The state subject is the modeled resource, not the control that changes it.

## Entry, Exit, Do

Use sparingly:

- `entry / acquire resource`
- `exit / release resource`
- `do / monitor validity`

Use entry/exit/do when the action is tied to being in the state, not to a specific transition.

## Initial And Final States

- Initial pseudostate should lead to exactly the initial state selection path.
- Avoid multiple initial arrows unless the notation/tool supports them and the guards are clear. A choice pseudostate may be clearer.
- Final state is optional. Many application state machines are long-lived and do not need a final state.

## State Machine Review Checklist

- The subject is one lifecycle-bearing thing.
- Every state is a stable condition.
- Every transition has an event, not just a condition.
- Guards are conditions, not effects.
- Effects are actions, not states.
- Composite states have real containment.
- No workflow steps are masquerading as states.
- No unrelated subjects are mixed in.
- Diagram labels are short enough to read.
- Invariants are stated if the model has cross-state constraints.

## Common Repairs

### Workflow Mistaken For State Machine

Symptom: states are verbs.

Repair: convert to activity diagram or transform verbs into transition effects.

### Multiple Subjects In One State Machine

Symptom: states include `User clicked`, `Service reachable`, `Resource valid`, `Dialog open`.

Repair: pick one subject and move the rest to guards/effects, or split diagrams.

### In-Use And Validity Collision

Symptom: `Valid`, `Expired`, `Reachable`, `Unreachable`, `In use` all appear as peer states.

Repair:

- choose subject;
- make `Valid/Expired` validity states;
- make `In use/Not in use` subordinate, orthogonal, or separate;
- make network availability a guard/external condition unless the subject is connection.
