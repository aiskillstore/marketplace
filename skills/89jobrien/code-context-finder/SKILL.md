---
name: code-context-finder
description: Automatically find relevant context from knowledge graph and code relationships
  while coding. Detects when context would be helpful (new files, unfamiliar code,
  architectural decisions) and surfaces related entities, prior decisions, and code
  dependencies.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Code Context Finder

## Overview

Find and surface relevant context while coding by combining knowledge graph search with code relationship analysis. Uses smart detection to identify when additional context would be helpful, then retrieves:

- **Knowledge graph entities**: Prior decisions, project context, related concepts
- **Code relationships**: Dependencies, imports, function calls, class hierarchies

## When to Use (Smart Detection)

This skill activates automatically when detecting:

| Trigger | What to Search |
|---------|----------------|
| Opening unfamiliar file | Knowledge graph for file/module context, code for imports/dependencies |
| Working on new feature | Prior decisions, related concepts, similar implementations |
| Debugging errors | Related issues, error patterns, affected components |
| Refactoring code | Dependent files, callers/callees, test coverage |
| Making architectural decisions | Past ADRs, related design docs, established patterns |
| Touching config/infra files | Related deployments, environment notes, past issues |

For detection triggers reference, load `references/detection_triggers.md`.

## Core Workflow

### 1. Detect Context Need

Identify triggers that suggest context would help:

```
Signals to watch:
- New/unfamiliar file opened
- Error messages mentioning unknown components
- Questions about "why" or "how" something works
- Changes to shared/core modules
- Architectural or design discussions
```

### 2. Search Knowledge Graph

Use MCP memory tools to find relevant entities:

```
# Search for related context
mcp__memory__search_nodes(query="<topic>")

# Open specific entities if known
mcp__memory__open_nodes(names=["entity1", "entity2"])

# View relationships
mcp__memory__read_graph()
```

**Search strategies:**

- Module/file names → project context
- Error types → past issues, solutions
- Feature names → prior decisions, rationale
- People names → ownership, expertise

### 3. Analyze Code Relationships

Find code-level context:

```python
# Find what imports this module
grep -r "from module import" --include="*.py"
grep -r "import module" --include="*.py"

# Find function callers
grep -r "function_name(" --include="*.py"

# Find class usages
grep -r "ClassName" --include="*.py"

# Find test coverage
find . -name "*test*.py" -exec grep -l "module_name" {} \;
```

For common search patterns, load `references/search_patterns.md`.

### 4. Synthesize Context

Present findings concisely:

```markdown
## Context Found

**Knowledge Graph:**
- [Entity]: Relevant observation
- [Decision]: Prior architectural choice

**Code Relationships:**
- Imported by: file1.py, file2.py
- Depends on: module_a, module_b
- Tests: test_module.py (5 tests)

**Suggested Actions:**
- Review [entity] before modifying
- Consider impact on [dependent files]
```

## Quick Reference

### Knowledge Graph Queries

| Intent | Query Pattern |
|--------|---------------|
| Find project context | `search_nodes("project-name")` |
| Find prior decisions | `search_nodes("decision")` or `search_nodes("<feature>")` |
| Find related concepts | `search_nodes("<concept>")` |
| Find people/owners | `search_nodes("<person-name>")` |
| Browse all | `read_graph()` |

### Code Relationship Queries

| Intent | Command |
|--------|---------|
| Find importers | `grep -r "from X import\|import X"` |
| Find callers | `grep -r "function("` |
| Find implementations | `grep -r "def function\|class Class"` |
| Find tests | `find -name "*test*" -exec grep -l "X"` |
| Find configs | `grep -r "X" *.json *.yaml *.toml` |

## Integration with Coding Workflow

### Before Making Changes

1. Check knowledge graph for context on module/feature
2. Find all files that import/depend on target
3. Locate relevant tests
4. Review prior decisions if architectural

### After Making Changes

1. Update knowledge graph if significant decision made
2. Note new patterns or learnings
3. Add observations to existing entities

### When Debugging

1. Search knowledge graph for similar errors
2. Find all code paths to affected component
3. Check for related issues/decisions
4. Document solution if novel

## Resources

### references/

- `detection_triggers.md` - Detailed trigger patterns for smart detection
- `search_patterns.md` - Common search patterns for code relationships

### scripts/

- `find_code_relationships.py` - Analyze imports, dependencies, and call graphs
