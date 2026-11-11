# Design plan template

```markdown
# <Outcome>

Written against: <commit or unavailable>

## Evidence chain

- Surface: `<path, route, or rendered state>`
- Problem: <direct observation>
- Design evidence: `<documentation, style, token, component, pattern, or rendered surface>`
- Owner: `<path or surface>`
- Scope and affected surfaces: `<paths or surfaces>`
- Uncertainty: <none, or what requires validation>

## Design decision

<State the appropriately scoped change and why it resolves the root problem.>

## Reuse

- `<token, variable, component, variant, or composition>`
- Exemplar: `<path>`

If a new primitive is required, state why the existing system cannot express the decision, where the primitive belongs, and which consumers should share it.

## Changes

1. `<exact path or surface>`
   - Change: <implementation-ready behavior or structure>
   - Preserve: <valid behavior or identity>
   - Verify: <observable result>

## Scope

- Inherit: <consumers that receive the change>
- Verify: <consumers that may be affected>
- Exclude: <valid exceptions and unrelated work>

## Validation

- Product: <task and expected outcome>
- Interface: <relevant routes, states, content extremes, interactions, and viewports>
- System: <confirm appropriate reuse and absence of an unintended parallel pattern>
- Repository: `<exact check command>` → <expected result>

## Stop conditions

- Stop if <a key assumption fails, ownership changes, or scope must widen>.

## Design documentation

- After acceptance and validation: <exact decision to record and its destination, or none>
```
