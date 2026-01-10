# Quick Create Workflow - Direct Agent Creation

Fast-path agent creation for experienced users. Minimal questions, maximum efficiency.

## When to Use This Workflow

- You know exactly what agent you need
- You're familiar with agent schema and patterns
- You want minimal interaction
- You can specify requirements upfront

## Prerequisites

- Clear understanding of agent's purpose
- Knowledge of required tools
- Idea of system prompt structure

## Workflow Steps

### Step 1: Gather Requirements

Answer these questions before starting:

1. **Agent name**: What should the agent be called? (kebab-case)
2. **Purpose**: What is the agent's single, clear responsibility?
3. **Trigger phrases**: When should it be invoked? (for description)
4. **Tools needed**: What tools does it need? (Read, Write, Bash, etc.)
5. **Model**: Which model? (sonnet, opus, haiku, inherit)
6. **Input/Output**: What does it receive and produce?

### Step 2: Determine File Location

**Project-level** (shared with team):
```bash
.claude/agents/[agent-name].md
```

**User-level** (personal):
```bash
~/.claude/agents/[agent-name].md
```

**Decision criteria**:
- Project-specific task? → Project-level
- Personal workflow? → User-level
- Team collaboration? → Project-level

### Step 3: Create Agent File

```bash
# Project-level
touch .claude/agents/agent-name.md

# User-level
touch ~/.claude/agents/agent-name.md
```

### Step 4: Write Frontmatter

Copy and customize:

```yaml
---
name: agent-name
description: |
  Clear description of what agent does. Use PROACTIVELY when [scenarios].
  Include trigger phrases: 'keyword1', 'keyword2', 'keyword3'.
tools: Read, Write, Bash, Grep, Glob
model: sonnet
---
```

**Tool selection guide**:

| Agent Type | Tools |
|------------|-------|
| Read-only reviewer | `Read, Grep, Glob` |
| Researcher | `Read, Grep, Glob, WebFetch, WebSearch` |
| Code writer | `Read, Write, Edit, Bash, Grep, Glob` |
| Full-stack | `Read, Write, Edit, Bash, Grep, Glob, WebFetch` |

### Step 5: Write System Prompt

Use this template structure:

```markdown
# [Agent Name]

You are [role/persona with expertise].

## Responsibilities

When invoked:
1. [Primary task]
2. [Secondary task]
3. [Result delivery]

## Workflow

### Step 1: [Action]
[Details]

### Step 2: [Action]
[Details]

### Step 3: [Action]
[Details]

## Checklist

- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

## Output Format

[Structured output specification]

## Examples

### Example 1: [Scenario]
**Input**: [Input example]
**Output**: [Expected output]

## Limitations

DO NOT:
- [Boundary 1]
- [Boundary 2]

DO:
- [Guideline 1]
- [Guideline 2]
```

### Step 6: Test Agent

**Method 1: Direct invocation**
```
Use the [agent-name] agent to [specific task with concrete input].
```

**Method 2: Realistic scenario**
```
[Describe realistic situation that should trigger agent]
```

**Verification checklist**:
- [ ] Agent is discovered (Claude recognizes it)
- [ ] Agent has correct tool access
- [ ] Agent follows workflow steps
- [ ] Agent produces expected output format
- [ ] Agent respects boundaries

### Step 7: Iterate Based on Failures

**Common issues**:

| Problem | Solution |
|---------|----------|
| Agent not recognized | Check file location, name in frontmatter matches filename |
| Tool access denied | Add tools to `tools` field or omit field to inherit all |
| Wrong output format | Add clearer output format specification with examples |
| Missing key steps | Add explicit workflow steps with details |
| Off-topic behavior | Add clearer boundaries (DO/DO NOT section) |

**Iteration process**:
1. Run test
2. Identify failure mode
3. Update prompt/config
4. Re-test
5. Repeat until working

## Quick Templates

### Template 1: Code Reviewer

```markdown
# .claude/agents/code-reviewer.md
---
name: code-reviewer
description: Reviews code for quality, security, and best practices. Use after code changes or before merging PRs.
tools: Read, Grep, Glob, Bash
model: sonnet
---

# Code Reviewer

You are a senior software engineer with expertise in code quality, security, and maintainability.

## Workflow

1. **Identify Changes**: Run `git diff --cached` or `git diff main`
2. **Analyze Files**: For each modified file, check against quality checklist
3. **Generate Report**: Provide findings by severity with code examples

## Quality Checklist

- [ ] Clear, descriptive naming
- [ ] Functions under 50 lines
- [ ] No code duplication
- [ ] Proper error handling
- [ ] Security best practices
- [ ] Test coverage

## Output Format

### Executive Summary
[2-3 sentences]

### Critical Issues
[List with file:line, code snippet, fix]

### Recommendations
[Prioritized actions]
```

### Template 2: Test Runner

```markdown
# .claude/agents/test-runner.md
---
name: test-runner
description: Runs tests, diagnoses failures, proposes fixes. Use after code changes.
tools: Read, Edit, Bash, Grep, Glob
model: sonnet
---

# Test Runner

You are a test automation specialist skilled in debugging test failures.

## Workflow

1. **Run Tests**: Execute project test command
2. **Diagnose Failures**: For each failure, read test file and identify root cause
3. **Propose Fixes**: Provide specific code fixes with rationale
4. **Verify**: Re-run tests after fixes

## Output Format

### Test Results
- Total: [count]
- Passed: [count]
- Failed: [count]

### Failures
For each:
- **Test**: [name]
- **File**: [path:line]
- **Error**: [message]
- **Root Cause**: [analysis]
- **Fix**: [code with explanation]
```

### Template 3: Tech Researcher

```markdown
# .claude/agents/tech-researcher.md
---
name: tech-researcher
description: Researches technologies, libraries, frameworks. Use when evaluating options or investigating approaches.
tools: Read, Grep, Glob, WebFetch, WebSearch
model: sonnet
---

# Tech Researcher

You are a technology researcher skilled in evaluating frameworks and best practices.

## Workflow

1. **Gather Information**: Search documentation, repos, comparisons
2. **Analyze Options**: Evaluate against criteria (performance, security, maintenance)
3. **Provide Recommendation**: Comparison matrix with justified recommendation

## Output Format

# Research Report: [Topic]

## Executive Summary
[2-3 sentences with recommendation]

## Options Analyzed
For each:
- **Pros**: [list]
- **Cons**: [list]
- **Metrics**: [stars, last update, license]

## Comparison Matrix
[Table comparing options]

## Recommendation
[Primary recommendation with rationale]

## Next Steps
[Immediate actions]
```

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ Agent Creation Quick Reference                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 1. File Location                                            │
│    Project: .claude/agents/[name].md                        │
│    User:    ~/.claude/agents/[name].md                      │
│                                                             │
│ 2. Required Frontmatter                                     │
│    ---                                                      │
│    name: agent-name                                         │
│    description: What it does and when to use it             │
│    tools: Read, Write, Bash                                 │
│    model: sonnet                                            │
│    ---                                                      │
│                                                             │
│ 3. System Prompt Structure                                  │
│    - Identity (who agent is)                                │
│    - Responsibilities (what it does)                        │
│    - Workflow (how it does it)                              │
│    - Checklist (what to verify)                             │
│    - Output format (structure)                              │
│    - Examples (3-5 concrete)                                │
│    - Boundaries (DO/DON'T)                                  │
│                                                             │
│ 4. Tool Selection                                           │
│    Read-only:  Read, Grep, Glob                             │
│    Research:   + WebFetch, WebSearch                        │
│    Code write: + Write, Edit, Bash                          │
│                                                             │
│ 5. Test Invocation                                          │
│    "Use [agent-name] agent to [specific task]"             │
│                                                             │
│ 6. Iterate                                                  │
│    Test → Identify failure → Update → Re-test               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Next Steps After Creation

1. **Version control** (project agents):
   ```bash
   git add .claude/agents/agent-name.md
   git commit -m "Add [agent-name] agent"
   ```

2. **Document usage** (in CLAUDE.md or README):
   ```markdown
   ## Available Agents

   - **agent-name**: [Brief description and usage]
   ```

3. **Share with team** (if applicable):
   - Add to team documentation
   - Demo in team meeting
   - Gather feedback

4. **Monitor and improve**:
   - Track agent invocations
   - Note failure patterns
   - Refine prompts based on real usage

## Common Shortcuts

### Shortcut 1: Clone and Modify Existing Agent

```bash
# Copy existing agent
cp .claude/agents/code-reviewer.md .claude/agents/security-reviewer.md

# Edit to specialize
# - Change name
# - Update description
# - Adjust checklist
# - Refine boundaries
```

### Shortcut 2: Use Built-in Agent as Base

```markdown
# Start with general-purpose or explore behavior
# Add specialized checklist and boundaries
# Keep workflow simple, leverage agent's inherent capability
```

### Shortcut 3: Minimal Agent (Grows Over Time)

```yaml
---
name: simple-agent
description: Does [one thing]. Use when [scenario].
tools: Read, Write
---

You do [specific task].

When invoked:
1. [Step 1]
2. [Step 2]
3. Provide [output]
```

**Then iterate**: Add checklists, examples, boundaries as you discover needs.

## Time Estimates

- **Minimal agent** (basic reviewer): 5-10 minutes
- **Standard agent** (with checklist, examples): 15-20 minutes
- **Complex agent** (multiple workflows, detailed): 30-45 minutes

## Resources

For complete schema reference, see: `references/agent-schema.md`

For prompt patterns, see: `references/prompt-patterns.md`

For interactive creation, see: `workflows/interview-create.md`
