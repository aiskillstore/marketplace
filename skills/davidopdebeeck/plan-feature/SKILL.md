---
name: plan-feature
description: Plan a new feature with analysis, design, and implementation steps. Use when the user asks to plan a feature or run /plan-feature.
---

# Feature Planning

Plan and structure new features with thorough analysis, design considerations, and actionable implementation steps.

## Instructions

When this skill is invoked:

1. **Gather Requirements**
   - Identify the feature name and high-level goal
   - Ask clarifying questions if requirements are ambiguous
   - Determine acceptance criteria for the feature

2. **Analyze Existing Codebase**
   - Search for related existing functionality
   - Identify patterns and conventions in the codebase
   - Find integration points where the feature will connect

3. **Design the Solution**
   - Determine affected modules (lobby, session, api, ui)
   - Identify required changes per architectural layer
   - Consider edge cases and error handling
   - Note any external dependencies or constraints

4. **Create Implementation Plan**
   - Break down into atomic, testable tasks
   - Order tasks by dependencies
   - Write the plan to the todo list using TodoWrite

5. **Save Plan to File**
   - Create `.claude/plans/` directory if it doesn't exist
   - Generate a slug from the feature name (e.g., "Custom Voting Decks" → `custom-voting-decks.md`)
   - Write the plan to `.claude/plans/<feature-slug>.md` using the Output Format below
   - This creates a persistent record of the plan for reference

6. **Present for Approval**
   - Summarize the approach
   - Highlight key design decisions
   - Present the task breakdown
   - Reference the saved plan file location
   - Wait for user approval before implementing

## Task Breakdown Structure

### Backend Tasks (if applicable)

```
[ ] Define API contract (Commands/Events/Queries in api module)
[ ] Implement domain logic (aggregates, entities, value objects)
[ ] Create command/query handlers
[ ] Update read model projections
[ ] Add usecase tests for handlers
[ ] Add integration tests
```

### Frontend Tasks (if applicable)

```
[ ] Design component structure
[ ] Implement state management (stores/hooks)
[ ] Create UI components
[ ] Wire up API integration
[ ] Add component tests
```

### Cross-Cutting Tasks

```
[ ] Update shared types/contracts
[ ] Add documentation if needed
[ ] Verify build passes
[ ] Run full test suite
```

## Analysis Guidelines

### Questions to Answer

1. **What problem does this solve?** - Clear user value
2. **Who is affected?** - Which users/roles
3. **What are the boundaries?** - What's in/out of scope
4. **What could go wrong?** - Failure modes and mitigations
5. **How will we know it works?** - Testability criteria

### Architecture Considerations

**Domain Layer**:
- New aggregates or entities needed?
- Changes to existing aggregate behavior?
- New domain events?

**Application Layer**:
- New commands or queries?
- Handler orchestration complexity?
- Transaction boundaries?

**Adapter Layer**:
- API endpoint changes?
- Persistence schema updates?
- External service integrations?

**UI Layer**:
- New pages or components?
- State management approach?
- User interaction flows?

## File Naming Convention

Plans are saved to `.claude/plans/<feature-slug>.md` where:
- Feature slug is derived from the feature name
- Convert to lowercase
- Replace spaces and special characters with hyphens
- Remove consecutive hyphens

Examples:
- "Custom Voting Decks" → `custom-voting-decks.md`
- "Add User Authentication" → `add-user-authentication.md`
- "Fix Timer Bug" → `fix-timer-bug.md`

## Output Format

Write the plan to the file using this structure:

```markdown
# Feature: [Name]

> **Created**: [YYYY-MM-DD]
> **Status**: Draft | Approved | In Progress | Completed

## Summary
[1-2 sentence description of what this feature does]

## Affected Modules
- [ ] api (contracts)
- [ ] guessimate-lobby
- [ ] guessimate-session
- [ ] guessimate-ui

## Key Design Decisions
1. [Decision 1 with rationale]
2. [Decision 2 with rationale]

## Implementation Tasks
[Numbered list of specific, actionable tasks]

## Risks & Considerations
- [Risk 1]
- [Risk 2]

## Open Questions
- [Question needing user input]
```

## Example

For a feature request like "Add ability to customize voting deck", the plan would be saved to `.claude/plans/custom-voting-decks.md`:

```markdown
# Feature: Custom Voting Decks

> **Created**: 2026-01-02
> **Status**: Draft

## Summary
Allow lobby owners to create and select custom card decks for estimation sessions instead of using only the default Fibonacci sequence.

## Affected Modules
- [x] api (new commands/events for deck management)
- [x] guessimate-lobby (deck storage in lobby aggregate)
- [ ] guessimate-session (use selected deck)
- [x] guessimate-ui (deck configuration UI)

## Key Design Decisions
1. Store custom decks at lobby level (not user level) - simpler model, decks tied to where they're used
2. Provide preset templates (Fibonacci, T-shirt, Powers of 2) - quick setup for common cases
3. Validate deck has 2-15 cards - reasonable constraints

## Implementation Tasks
1. Add Deck value object with validation to api module
2. Add CreateCustomDeckCommand and DeckCreatedEvent to api
3. Implement deck storage in LobbyAggregate
4. Create DeckSelectionComponent in UI
5. Add deck preview functionality
6. Update session creation to use selected deck
7. Add usecase tests for deck commands
8. Add integration test for full flow

## Risks & Considerations
- Migration: existing lobbies need default deck assigned
- UI complexity: deck editor could become complex

## Open Questions
- Should decks be shareable between lobbies?
```
