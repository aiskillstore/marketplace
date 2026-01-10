---
name: scenario-testing
description: This skill should be used when writing tests, validating features, or needing to verify code works. Triggers on "write tests", "add test coverage", "validate feature", "integration test", "end-to-end", "e2e test", "mock", "unit test". Enforces scenario-driven testing with real dependencies in .scratch/ directory.
---

# Scenario-Driven Testing for AI Code Generation

## Core Principle

**The Iron Law**: "NO FEATURE IS VALIDATED UNTIL A SCENARIO PASSES WITH REAL DEPENDENCIES"

Mocks create false confidence. Only scenarios exercising real systems validate that code works.

## The Truth Hierarchy

1. **Scenario tests** (real system, real data) = **truth**
2. **Unit tests** (isolated) = human comfort only
3. **Mocks** = lies hiding bugs

As stated in the principle: "A test that uses mocks is not testing your system. It's testing your assumptions about how dependencies behave."

## When to Use This Skill

- Validating new functionality
- Before declaring work complete
- When tempted to use mocks
- After fixing bugs requiring verification
- Any time you need to prove code works

## Required Practices

### 1. Write Scenarios in `.scratch/`

- Use any language appropriate to the task
- Exercise the real system end-to-end
- Zero mocks allowed
- Must be in `.gitignore` (never commit)

### 2. Promote Patterns to `scenarios.jsonl`

- Extract recurring scenarios as documented specifications
- One JSON line per scenario
- Include: name, description, given/when/then, validates
- This file IS committed

### 3. Use Real Dependencies

External APIs must hit actual services (sandbox/test mode acceptable). Mocking any dependency invalidates the scenario.

### 4. Independence Requirement

Each scenario must run standalone without depending on prior executions. This enables:
- Parallel execution
- Prevents hidden ordering dependencies
- Reliable CI/CD integration

## What Makes a Scenario Invalid

A scenario is invalid if it:
- Contains any mocks whatsoever
- Uses fake data instead of real storage
- Depends on another scenario running first
- Never actually executed to verify it passes

## Common Violations to Avoid

Reject these rationalizations:

- **"Just a quick unit test..."** - Unit tests don't validate features
- **"Too simple for end-to-end..."** - Integration breaks simple things
- **"I'll mock for speed..."** - Speed doesn't matter if tests lie
- **"I don't have API credentials..."** - Ask your human partner for real ones

## Definition of Done

A feature is complete only when:

1. ✅ A scenario in `.scratch/` passes with zero mocks
2. ✅ Real dependencies are exercised
3. ✅ `.scratch/` remains in `.gitignore`
4. ✅ Robust patterns extracted to `scenarios.jsonl`

## Example Workflow

1. **Write scenario** - Create `.scratch/test-user-registration.py`
2. **Use real dependencies** - Hit real database, real auth service (test mode)
3. **Run and verify** - Execute scenario, confirm it passes
4. **Extract pattern** - Document in `scenarios.jsonl`
5. **Keep .scratch ignored** - Never commit scratch scenarios

## Why This Matters

- **Unit tests** verify isolated logic
- **Integration tests** verify components work together
- **Scenario tests** verify the system actually works

Only scenario tests prove your feature delivers value to users.
