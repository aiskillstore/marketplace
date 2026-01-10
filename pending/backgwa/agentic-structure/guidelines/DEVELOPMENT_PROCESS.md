# Development Process

## Purpose
This document defines how we build software collaboratively in a way that is clear, safe, production-ready, and easy to maintain.

## Core Principles

### Application Philosophy
These guidelines are designed to be applied thoughtfully, not rigidly:

- **Strive to follow** - Aim to apply these principles consistently, but use judgment when exceptions are warranted
- **Apply incrementally** - Build good habits gradually; it's acceptable to apply these imperfectly at first and improve over time
- **Context matters** - Adapt guidelines to project size, team structure, and specific requirements
- **Progress over perfection** - Moving in the right direction is better than perfect adherence that delays delivery
- **Question and clarify** - When unsure, err on the side of asking or documenting your reasoning

### Core-First: Priority-Based Implementation
Implement in this priority order:

**Priority 1: Core Logic** (implement first)
- [ ] Business logic that defines feature behavior
- [ ] Data transformations and calculations
- [ ] API/function contracts (inputs, outputs, error cases)
- [ ] Backend endpoints before frontend UI

**Priority 2: Integration** (implement second)
- [ ] Connecting core logic to data sources
- [ ] Authentication and authorization checks
- [ ] Error handling and input validation

**Priority 3: Interface** (implement last)
- [ ] UI components and styling
- [ ] User-facing error messages
- [ ] Loading states and animations

**Action Protocol:**
When user provides feature request:
1. Identify components in each priority tier
2. Propose implementation order: "I'll implement [Priority 1 items] first, then [Priority 2], then [Priority 3]"
3. Wait for approval if user expectations differ

### Small Steps: Incremental Delivery Criteria
Each implementation step should meet these criteria:

**Small Steps Principle:**
- [ ] Completes one logical unit (function, component, endpoint, test suite)
- [ ] Can be validated independently (has observable behavior)
- [ ] Does not break existing functionality
- [ ] Passes all existing tests

**Consider splitting when:**
- Change spans many unrelated areas of codebase
- Mixed concerns (refactoring + new feature)
- Cannot validate without completing additional work

**Coherent changes may naturally span multiple files or significant lines:**
- Consistent refactoring across related components
- Complete feature with types + logic + tests
- Documentation or configuration updates

**When Breaking Down Work:**
1. Identify logical boundaries between sub-tasks
2. Propose step sequence to user
3. Implement one step at a time
4. Validate before proceeding to next step

### Continuous Validation: Verification Checkpoints

**After Each Implementation Step:**
- [ ] Code compiles/runs without syntax errors
- [ ] Existing tests still pass
- [ ] New functionality produces expected output for base case
- [ ] Error cases return expected errors (not crashes)

**Before Marking Step Complete:**
- [ ] Manual testing: Run/call the implemented code path
- [ ] Edge cases: Test with empty input, null, boundary values
- [ ] Integration: Verify connections to other modules work
- [ ] Output: Compare actual vs. expected behavior

**Validation Protocol:**
1. After completing implementation step, run all applicable checks above
2. If ANY check fails: Fix before proceeding
3. If unable to validate (missing tests, no run environment):
   - State what was implemented
   - State what validation was performed
   - State what validation is needed from user

### Other Principles
- **Clarity and safety**: Prefer explicit, safe approaches over clever or fragile shortcuts.
- **Correct and complete**: Fully meet the requirements with minimal complexity and predictable behavior.
- **Production readiness**: Assume changes may ship to production and be exposed to real users and real traffic.
- **Maintainability**: Make changes easy to extend, debug, and safely modify (both existing and new features).

## Collaboration Contract

### Decision Ownership
- **User owns**: Product decisions (scope, priorities, trade-offs, business logic)
- **Agent proposes**: Technical options, implementation approaches, architecture patterns
- **Shared decision**: When to deviate from existing patterns or introduce new dependencies

### When to Request User Approval
DO NOT proceed autonomously when ANY of these conditions are true:

**Architectural Impact:**
- [ ] Decision affects public API, database schema, or security model
- [ ] Decision introduces new dependencies (libraries, services, external APIs)
- [ ] Decision changes file organization or architectural patterns
- [ ] Decision requires environment configuration or deployment changes

**Implementation Options:**
- [ ] Multiple valid approaches exist with different trade-offs
- [ ] Decision breaks backward compatibility
- [ ] Decision impacts performance characteristics (caching, querying, processing)

**Scope Uncertainty:**
- [ ] Requirements are ambiguous (see DISCUSSION_GUIDELINES.md for ambiguity detection)
- [ ] Success criteria not clearly defined
- [ ] Feature boundaries unclear (MVP vs future enhancements)

**Action Protocol:**
1. Present 2-3 viable options with structured comparison (see DISCUSSION_GUIDELINES.md)
2. State your recommendation with reasoning
3. Wait for user selection before implementing

### When to Proceed Autonomously
You CAN proceed without asking when ALL of these are true:
- [ ] Implementation approach is obvious and follows existing patterns
- [ ] No architectural or schema changes required
- [ ] No new dependencies or breaking changes
- [ ] Requirements are clear and unambiguous
- [ ] Clear project context exists to support the decision

### Handling Disagreement
When there is disagreement:
1. Discuss trade-offs openly
2. Document the final choice and reasoning
3. Note rejected alternatives and why they were not chosen
4. Proceed with user's final decision

## Development Workflow
1. Clarify the request and plan
   - Confirm the user's intent and validate the requirements.
   - Create a step-by-step plan to solve the problem; avoid trying to finish everything at once.

2. Implement
   - Build the feature according to the plan and workflow rules.

3. Validate and get feedback
   - Verify the feature works and matches the user's requirements.
   - If issues are found, incorporate feedback and improve the implementation.

4. Wrap up
   - Review and improve final code quality.
   - Remove any code or tooling that was only needed during development.

## Maintainability Expectations
- Prefer small, local changes that minimize blast radius.
- Preserve backward compatibility unless the user explicitly agrees to breaking changes.
- Avoid unnecessary abstraction; only introduce patterns that will be reused.
- Keep naming and structure consistent with existing code.

## Handling Uncertainty
If any of the following is true, pause and ask:
- Multiple valid interpretations exist.
- A decision affects architecture, database schema, or public API.
- It changes security posture or introduces new dependencies.
- It could break backward compatibility or require migration.
