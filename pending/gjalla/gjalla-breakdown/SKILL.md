---
name: gjalla-breakdown
description: Break a feature spec into intentional waves and bite-sized tasks grouped by dependency. Use after a spec is written to prepare for easy-to-track implementation.
---

# Wave-Based Task Breakdown

Break the feature into sized, dependency-ordered task waves. This makes it easier to keep track of progress as we build so we ensure that we're on track to build what the user expects:

## Process
1. **Read the spec**: Identify all behavioral requirements and technical changes from the agent plan or gjalla spec.
2. **Identify tasks**: Each task should touch 1-2 files and produce a small, reviewable diff that's verifiable.
3. **Map dependencies**: Which tasks must complete before others can start?
4. **Group into waves**: Tasks within a wave can be done in parallel; waves are sequential.

## Task Format
Waves of work comprise groups of tasks:
- **ID**: W1-T1, W1-T2, W2-T1, etc.
- **Description**: One-line summary of what changes.
- **Files**: Exact file paths that will be modified or created.
- **Depends On**: Task IDs this depends on (within same wave = none).
- **Acceptance**: How to verify this task is done.

## Principles
- Waves help you group tasks into logical/modular sections so you can put them in an intuitive order. For instance, data model changes might need to come first so the rest of the waves have the foundation they need to build on.
- The waves and tasks should have a place to mark once complete so that we can easily see our status as we implement.
- Make sure that docs, verification, tests, etc are included in your breakdown.

To avoid overload, try to keep the total task count under 20 for a single spec; split larger features into multiple specs.
