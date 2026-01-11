---
name: waterfall-development
description: Enforces strict waterfall development workflow with phase gates. Use when (1) features.yml exists in project root, (2) user asks to implement/develop/build a feature, (3) user explicitly requests waterfall workflow. Creates features.yml if missing when invoked.
---

# Waterfall Development

Strict phase gate enforcement for waterfall workflow. Requires the `feature-file` skill for artifact management.

## Phases

Requirements → Design → Implementation → Testing → Complete

## Activation

| Condition | Action |
|-----------|--------|
| features.yml exists | Activate, validate gates |
| User invokes skill, no features.yml | Create features.yml via feature-file skill, then activate |
| No features.yml, not invoked | Do not activate |

## Workflow

1. Run `./scripts/validate-gates.py`
2. If errors: Print errors, STOP
3. Identify target feature and current phase
4. Block work that doesn't match current phase
5. Before phase transitions: Re-validate target phase gates

## Gates

See references/phase-gates.md for fix instructions.

| Gate | Transition | Criteria |
|------|------------|----------|
| G1 | → Design | Feature has ≥1 requirement |
| G2 | → Design | All requirements have descriptions |
| G3 | → Implementation | decisions field exists |
| G4 | → Testing | All requirements In-Progress or Complete |
| G5 | → Complete | All requirements Complete + tested-by + all tests passing |

## Agent Usage

Use sub-agents for verification tasks that require codebase exploration:

**Before Design phase**: Verify requirements are complete by examining codebase and user request for implicit requirements.

**Before Complete phase**: Verify test coverage by checking all requirements have corresponding tests and tested-by references.

## Error Handling

Gate failures print terse errors. No bypass mechanism.
