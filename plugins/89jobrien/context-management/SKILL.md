---
name: context-management
description: Context management specialist for multi-agent workflows and long-running
  tasks. Use when coordinating multiple agents, preserving context across sessions,
  or managing complex project state. Focuses on context compression and distribution.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Context Management

This skill manages context across multi-agent workflows and long-running tasks, ensuring coherent state preservation and efficient context distribution.

## When to Use This Skill

- When coordinating multiple agents in a workflow
- When preserving context across sessions
- When managing long-running projects
- When compressing context for efficiency
- When distributing context to specific agents
- When creating context checkpoints

## What This Skill Does

1. **Context Capture**: Extracts key decisions and rationale
2. **Context Distribution**: Prepares relevant context for each agent
3. **Memory Management**: Stores critical project decisions
4. **Context Compression**: Reduces context size while preserving key information
5. **Context Indexing**: Creates indexes for quick retrieval
6. **State Preservation**: Maintains coherent state across sessions

## How to Use

### Manage Context

```
Capture the key context from this conversation
```

```
Prepare context for the next agent in this workflow
```

### Specific Tasks

```
Create a context checkpoint for this project milestone
```

## Context Formats

### Quick Context (< 500 tokens)

- Current task and immediate goals
- Recent decisions affecting current work
- Active blockers or dependencies

### Full Context (< 2000 tokens)

- Project architecture overview
- Key design decisions
- Integration points and APIs
- Active work streams

### Archived Context

- Historical decisions with rationale
- Resolved issues and solutions
- Pattern library
- Performance benchmarks

## Best Practices

### Context Management

1. **Relevance Over Completeness**: Include only what's needed
2. **Key Decisions**: Capture rationale, not just outcomes
3. **Compression**: Reduce context while preserving meaning
4. **Indexing**: Create searchable context indexes
5. **Checkpoints**: Save context at major milestones

## Reference Files

- **`references/patterns.md`** - Context management patterns, handoff templates, and multi-agent coordination

## Related Use Cases

- Multi-agent coordination
- Long-running project management
- Context preservation across sessions
- Workflow state management
- Project knowledge management
