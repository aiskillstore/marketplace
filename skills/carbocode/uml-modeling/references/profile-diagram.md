# Profile Diagram Deep Dive

Use a profile diagram to model extensions to UML itself. It answers how a domain-specific modeling vocabulary is defined.

## Use When

- The user needs stereotypes, tagged values, and constraints.
- A team wants a formal modeling convention.
- Domain concepts must extend UML metaclasses consistently.

Avoid when the user only wants to label a few boxes in one diagram.

## Core Modeling Elements

- Profile.
- Stereotype.
- Metaclass extension.
- Tagged value/property.
- Constraint.
- Package import/apply relationship when showing usage context.

## Expansion Questions

- What domain vocabulary needs formal semantics?
- Which UML metaclass can each stereotype extend?
- Which tagged values are required or optional?
- What constraints prevent misuse?
- Is this definition reusable across diagrams?

## Design Moves

- Keep profile definition separate from diagrams that apply the profile.
- Define each stereotype against the narrowest useful metaclass.
- Use tagged values for domain data, not styling.
- Write constraints when stereotypes imply rules the notation cannot enforce visually.

## Completeness Criteria

- Each stereotype has a clear base metaclass.
- Tagged values have meaning and type.
- Constraints express real modeling rules.
- The profile supports repeatable modeling, not one-off annotation.

## Common Mistakes And Repairs

- Stereotype as decoration: replace with ordinary label or note.
- Extending the wrong metaclass: choose the UML element being specialized.
- Too many tags: keep only properties needed for modeling decisions.
- Missing constraints: add rules that explain how the stereotype may be used.
