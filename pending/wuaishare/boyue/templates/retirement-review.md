# Retirement Review

Use this template periodically or after major releases to remove complexity that no longer earns its ownership cost.

## Review scope

Repository / product / module / release:

## Evidence window

What usage, support, reliability, and maintenance evidence is being reviewed?

## Candidates

| Candidate | Current value | Ownership cost | Dependencies / users | Decision |
|---|---|---|---|---|
| | | | | Maintain / Simplify / Retire |

## Questions

### Features

- Which features have little or no meaningful use?
- Which workflows overlap or can be merged?

### Settings and feature flags

- Which settings exist only because defaults were never chosen?
- Which feature flags have become permanent?

### APIs and integrations

- Which public surfaces no longer justify compatibility cost?
- Which integrations are stale or rarely used?

### Dependencies and services

- Which dependencies can be removed or replaced with existing capabilities?
- Which services create more operational cost than value?

### Documentation and code

- Which documentation describes behavior that no longer exists?
- Which abstractions exist only for hypothetical future needs?

## Decisions

### Maintain

What evidence justifies continued ownership?

### Simplify

What can be reduced without losing meaningful value?

### Retire

What will be removed, how will users/data be migrated, and what is the rollback plan?

## Follow-up evidence

How will we verify that retirement or simplification improved the system?
