---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: code-context-finder
---

# Detection Triggers Reference

Detailed patterns for smart context detection while coding.

## File-Based Triggers

### New/Unfamiliar Files

**Signals:**

- First time opening a file in session
- File in unfamiliar directory/module
- File with complex imports or dependencies

**Context to retrieve:**

- Knowledge graph: module purpose, related decisions
- Code: imports, dependents, tests

### Core/Shared Modules

**Signals:**

- File in `core/`, `shared/`, `common/`, `utils/` directories
- File imported by 5+ other files
- File with `__init__.py` exports

**Context to retrieve:**

- All importers (impact analysis)
- Related tests
- Prior changes/decisions

### Configuration Files

**Signals:**

- `.env`, `.yaml`, `.json`, `.toml` config files
- `settings.py`, `config.py`
- CI/CD files (`.github/`, `Dockerfile`)

**Context to retrieve:**

- Knowledge graph: deployment notes, environment specifics
- Related infrastructure decisions

## Action-Based Triggers

### Making Changes

**Signals:**

- Edit tool invoked on file
- Multiple files being modified
- Refactoring patterns detected (rename, move, extract)

**Context to retrieve:**

- Dependent files
- Test coverage
- Prior decisions on module

### Debugging

**Signals:**

- Error messages in conversation
- Stack traces
- "why", "broken", "failing" in user message

**Context to retrieve:**

- Knowledge graph: similar errors, past issues
- Error handling patterns in codebase
- Related components

### Architectural Discussion

**Signals:**

- Keywords: "should we", "design", "architecture", "pattern"
- Mentions of trade-offs or alternatives
- New feature planning

**Context to retrieve:**

- Knowledge graph: ADRs, design decisions
- Similar implementations
- Established patterns

## Keyword Triggers

### High-Priority Keywords

| Keyword | Context to Search |
|---------|-------------------|
| `migrate`, `migration` | Past migrations, schema changes |
| `deprecate`, `remove` | Dependents, usage patterns |
| `security`, `auth` | Security decisions, auth patterns |
| `performance`, `optimize` | Benchmarks, past optimizations |
| `test`, `coverage` | Test files, coverage reports |

### Module/Feature Keywords

When user mentions specific modules or features:

1. Search knowledge graph for entity
2. Find related files in codebase
3. Locate tests for that module

## Context Freshness

### Always Fetch Fresh

- Dependent file lists (code changes frequently)
- Test file locations
- Import relationships

### Cache-Friendly

- Knowledge graph entities (update less frequently)
- Architecture decisions (stable)
- Project conventions

## Integration Points

### IDE Events (if available)

- File opened → check familiarity
- File saved → check for architectural changes
- Error diagnostics → search for similar issues

### Conversation Patterns

- Question about unfamiliar code → fetch context
- Request to modify shared code → impact analysis
- Debugging session → search past issues
