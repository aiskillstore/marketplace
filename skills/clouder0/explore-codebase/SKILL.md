---
name: explore-codebase
description: Pattern for efficiently exploring codebases using parallel subagents. Use when you need to understand code structure, find patterns, or gather context.
allowed-tools: Task, Read, Glob, Grep
---

# Explore Codebase Skill

Pattern for exploring codebases efficiently with parallel subagents.

## When to Load This Skill

- You need to understand parts of the codebase
- You're gathering context before making decisions
- You need to find patterns, conventions, or existing implementations

## Exploration Strategy

### For Quick Searches (Do Yourself)
```
Glob("**/*{keyword}*")
Grep(pattern="functionName", type="ts")
```
Use when looking for a specific thing.

### For Broad Understanding (Spawn Explorers)
Spawn parallel explorer subagents:
```
Task(
  subagent_type: "explorer",  # Custom dotagent agent (lowercase)
  model: "haiku",
  prompt: |
    Query: {specific question}
    Hints: {where to look}
    Scope: {limit if needed}

    Return structured YAML:
    - findings (location, relevance, summary)
    - patterns_observed
    - related_areas
    - gaps
)
```

Spawn multiple for different areas simultaneously.

**Note:** Use `"explorer"` (lowercase) for the custom dotagent agent defined in
`@.claude/agents/explorer.md`. The built-in `"Explore"` (capitalized) is a different
Claude Code agent with simpler behavior.

### Synthesize Results
Combine explorer outputs into coherent understanding:
- Common patterns across areas
- Integration points
- Constraints discovered
- Gaps to note

## Output Format

After exploration, summarize as:
```yaml
codebase_context:
  architecture_summary: string
  existing_patterns: [string]
  integration_points: [string]
  constraints: [string]
  gaps: [string]
```

## Principles

- **Parallel over sequential** - Spawn multiple explorers at once
- **Breadth over depth** - Explore broadly first
- **Structured output** - Always produce YAML summaries
- **Note gaps** - What you couldn't find matters
