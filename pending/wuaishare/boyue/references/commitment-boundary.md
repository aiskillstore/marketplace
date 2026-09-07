# Commitment Boundary

The Commitment Boundary separates **what could be built** from **what deserves investment now**.

> **Option ≠ Commitment**

AI-assisted development can cheaply create options: ideas, prototype screens, technical approaches, experimental branches, or even complete patches. Do not let the existence of an implementation become evidence that the work deserves product priority.

## Trigger conditions

Run a Commitment check when work introduces meaningful new scope, such as:

- a new product feature or module;
- a new external integration;
- a new platform or supported workflow;
- a substantial new dependency;
- an architecture direction that changes future choices;
- a “while we are here” addition that was not required by the original task.

## Questions

1. What user or system problem does this solve?
2. What evidence supports solving it now?
3. Is the option aligned with the current product or project goal?
4. Is there a simpler alternative?
5. What happens if the work is delayed?
6. Does the option create long-lived ownership surface?

## Three outcomes

### COMMIT

Choose when evidence supports investing now.

A commitment means the organization is intentionally spending attention, design capacity, implementation capacity, and future roadmap space.

### DEFER

Choose when an option may have value but should not consume current commitment capacity.

Every DEFER should record a **revisit trigger**, for example:

- three independent paying customers request the same workflow;
- a dependency reaches a required capability;
- usage exceeds a measured threshold;
- a prerequisite architecture migration is complete.

Avoid “maybe later” without a trigger. That only creates backlog debt.

### DISCARD

Choose when evidence indicates that the option should stop consuming attention.

Discarding is not failure. It protects capacity for higher-value work.

## Useful artifacts

- [PRFAQ](../templates/prfaq.md)
- [Decision Record](../templates/decision-record.md)
- [Non-goals](../templates/non-goals.md)
- [Option Map](../templates/option-map.md)

## Anti-patterns

- “The agent already wrote it, so merge it.”
- “Our competitor has it, so we need it.”
- “It only takes an hour, so there is no downside.”
- Treating every brainstorm item as a backlog item.
- Using arbitrary deletion quotas instead of evidence.
