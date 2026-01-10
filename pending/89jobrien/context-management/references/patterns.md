---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: context-management
---

# Context Management Patterns

## Session State Patterns

### File-Based Context

```markdown
# Session Context File Structure
.claude/
├── session-context.md      # Current session state
├── task-history.md         # Completed tasks
└── pending-decisions.md    # Items needing user input
```

### Context Handoff Pattern

When transitioning between agents or sessions:

1. **Summarize Current State**
   - What was accomplished
   - What's in progress
   - What's blocked

2. **Document Decisions**
   - Choices made and rationale
   - Alternatives considered
   - User preferences noted

3. **List Open Items**
   - Pending tasks
   - Questions for user
   - Dependencies

## Multi-Agent Coordination

### Filesystem Artifact Pattern

```python
# Each subagent writes to unique file
output_path = f"/tmp/agent_{task_id}_{timestamp}.md"

# Coordinator reads all artifacts
artifacts = glob.glob("/tmp/agent_*.md")
results = [read_file(f) for f in artifacts]
```

### Context Distribution

```yaml
# Shared context structure
shared_context:
  project_root: /path/to/project
  conventions:
    - Use TypeScript
    - Follow existing patterns
  constraints:
    - No breaking changes
    - Maintain backwards compatibility

agent_specific:
  code_reviewer:
    focus: security, performance
  test_writer:
    framework: pytest
    coverage_target: 80%
```

## Token Optimization

### Context Compression

- Summarize completed work
- Remove redundant information
- Reference files instead of including content
- Use bullet points over prose

### Progressive Loading

1. Load minimal context initially
2. Expand sections as needed
3. Unload completed task context

## Handoff Templates

### Task Completion Handoff

```markdown
## Completed: [Task Name]

### What Was Done
- [Action 1]
- [Action 2]

### Files Changed
- `path/to/file.ts` - [description]

### Decisions Made
- Chose X over Y because [reason]

### For Next Session
- [ ] Follow-up task 1
- [ ] Follow-up task 2
```

### Error/Block Handoff

```markdown
## Blocked: [Task Name]

### Attempted
- [Approach 1] - Failed because [reason]
- [Approach 2] - Partially worked but [issue]

### Current State
- [Description of where things stand]

### Need From User
- [ ] Decision on [question]
- [ ] Access to [resource]
```
