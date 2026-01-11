# Agent Update Patterns

Common scenarios and solutions for updating Claude Code agents.

---

## Pattern Categories

1. [Performance Optimization](#performance-optimization)
2. [Security Hardening](#security-hardening)
3. [Capability Enhancement](#capability-enhancement)
4. [Documentation Improvement](#documentation-improvement)
5. [Schema Compliance](#schema-compliance)
6. [Scope Refinement](#scope-refinement)

---

## Performance Optimization

### Pattern: Over-Powered Model

**Problem**: Agent uses expensive model for simple tasks

**Symptoms**:
- Agent description mentions "simple", "quick", or "basic"
- Tasks are primarily search, grep, or read operations
- Using `opus` or `sonnet` when `haiku` would suffice

**Solution**:
```bash
/agent-builder:agents:update my-agent
> What to update? 3 (model)
> Select model: 1 (haiku)
```

**Example**:
```yaml
# Before
model: opus
description: Quick file searcher for finding imports

# After
model: haiku
description: Quick file searcher for finding imports
```

**Impact**: 30x faster, 95% cost reduction, same quality for simple tasks

---

### Pattern: Under-Powered Model

**Problem**: Agent struggles with complex reasoning

**Symptoms**:
- Agent produces incorrect or incomplete results
- Task requires deep analysis or complex logic
- Using `haiku` for advanced reasoning tasks

**Solution**:
```bash
/agent-builder:agents:update my-agent
> What to update? 3 (model)
> Select model: 2 (sonnet) or 3 (opus)
```

**Example**:
```yaml
# Before
model: haiku
description: Security auditor for identifying subtle vulnerabilities

# After
model: opus
description: Security auditor for identifying subtle vulnerabilities
```

**Impact**: Better accuracy, deeper analysis, worth the cost for critical tasks

---

## Security Hardening

### Pattern: Unnecessary Bash Access

**Problem**: Agent has Bash permissions but doesn't need them

**Symptoms**:
- `tools` includes `Bash`
- Agent body doesn't mention system commands
- Primary tasks are read, analysis, or generation
- No input validation documented

**Solution**:
```bash
/agent-builder:agents:enhance my-agent
# Reviews: "❌ Has Bash access without input validation"

/agent-builder:agents:update my-agent
> What to update? 2 (tools)
> Select preset: 1 (Read, Grep, Glob)
```

**Example**:
```yaml
# Before
tools: Read, Write, Edit, Grep, Glob, Bash

# After (if Bash not needed)
tools: Read, Write, Edit, Grep, Glob
```

**Impact**: Reduced attack surface, safer agent

---

### Pattern: Missing Input Validation

**Problem**: Agent has Bash but no validation documentation

**Symptoms**:
- `tools` includes `Bash`
- No mention of "validate", "sanitize", "escape" in agent body
- Processes user input directly

**Solution**:

Add validation section to agent body:

```markdown
## Input Validation

Before executing any commands:

1. **Validate file paths**: Ensure no path traversal (../)
2. **Sanitize arguments**: Remove shell metacharacters
3. **Whitelist commands**: Only allow specific commands
4. **Escape inputs**: Use proper quoting

Example:
\`\`\`python
# Bad
os.system(f"cat {user_input}")

# Good
import shlex
safe_path = shlex.quote(user_input)
os.system(f"cat {safe_path}")
\`\`\`
```

**Impact**: Prevents command injection attacks

---

### Pattern: Over-Permissioned Tools

**Problem**: Agent has both Write and Edit (redundant)

**Symptoms**:
- `tools` includes both `Write` and `Edit`
- Agent typically does one or the other, not both

**Solution**:
```yaml
# Before
tools: Read, Write, Edit, Grep, Glob

# After (choose one)
tools: Read, Edit, Grep, Glob    # For modifying existing files
# OR
tools: Read, Write, Grep, Glob   # For creating new files
```

**Guideline**:
- Use `Edit` for modifying existing files
- Use `Write` for creating new files
- Rarely need both

---

## Capability Enhancement

### Pattern: Missing Examples

**Problem**: Agent lacks concrete usage examples

**Symptoms**:
- Enhancement score flags: "❌ No examples provided"
- Users unsure how to invoke agent
- Abstract descriptions without specifics

**Solution**:

Add examples section to agent body:

```markdown
## Examples

### Example 1: Reviewing Pull Request

**Scenario**: User asks to review PR #123

**Invocation**:
\`\`\`
Task: Review PR #123 for security issues
Agent: security-reviewer
\`\`\`

**Process**:
1. Fetch PR diff
2. Analyze each changed file
3. Identify vulnerabilities
4. Generate report

**Output**: Structured security report with severity ratings

### Example 2: Quick Security Scan

**Scenario**: User asks to check a single file

**Invocation**:
\`\`\`
Task: Check auth.py for security issues
Agent: security-reviewer
\`\`\`

**Process**:
1. Read auth.py
2. Scan for common vulnerabilities
3. Report findings

**Output**: List of issues with line numbers
```

**Impact**: Better user understanding, clearer expectations

---

### Pattern: Missing Workflow

**Problem**: Agent doesn't document step-by-step process

**Symptoms**:
- Enhancement score flags: "⚠️ Missing workflow documentation"
- Unclear how agent approaches tasks
- No actionable steps

**Solution**:

Add workflow section:

```markdown
## Workflow

When invoked, I follow these steps:

1. **Gather Context**
   - Read all relevant files
   - Understand the codebase structure
   - Identify entry points

2. **Analyze Code**
   - Scan for security patterns
   - Check authentication flows
   - Review authorization logic
   - Examine data validation

3. **Identify Issues**
   - Categorize by severity (critical/high/medium/low)
   - Map to OWASP Top 10
   - Note affected files and lines

4. **Generate Report**
   - Structured findings
   - Remediation suggestions
   - Code examples
   - Priority ranking

5. **Provide Recommendations**
   - Quick fixes
   - Long-term improvements
   - Best practices to adopt
```

**Impact**: Users know what to expect, agent is more consistent

---

### Pattern: Vague Description

**Problem**: Description doesn't explain when to invoke

**Symptoms**:
- Description is generic: "Helps with coding tasks"
- Doesn't specify triggers or use cases
- Users don't know when to use this vs other agents

**Solution**:

Improve description with specifics:

```yaml
# Before
description: Code analysis agent

# After
description: Security-focused code analyzer for identifying vulnerabilities, insecure patterns, and OWASP Top 10 issues. Use when reviewing PRs, auditing authentication, or validating input handling.
```

**Template**:
```
description: [What it does] [What it specializes in]. Use when [scenario 1], [scenario 2], or [scenario 3].
```

**Impact**: Better auto-suggestion, clearer purpose

---

## Documentation Improvement

### Pattern: Missing Error Handling

**Problem**: Agent doesn't document error scenarios

**Symptoms**:
- No "Error Handling" or "Edge Cases" section
- Unclear what happens on failures
- Users surprised by agent behavior

**Solution**:

Add error handling section:

```markdown
## Error Handling

### File Not Found
If target file doesn't exist:
- Search for similar filenames
- Ask user to clarify path
- List available files in directory

### Invalid Syntax
If code contains syntax errors:
- Report syntax error with line number
- Suggest correction if obvious
- Ask user to fix before proceeding

### Permission Denied
If file is not readable:
- Report permission issue
- Suggest checking file permissions
- Provide command to fix: chmod +r file

### Large Files
If file exceeds reasonable size:
- Warn user about processing time
- Offer to sample/truncate
- Ask for confirmation before proceeding
```

**Impact**: Graceful degradation, better UX

---

### Pattern: No Best Practices

**Problem**: Agent lacks guidance on quality standards

**Symptoms**:
- Enhancement flags: "⚠️ Missing best practices section"
- Inconsistent output quality
- Doesn't follow coding standards

**Solution**:

Add best practices section:

```markdown
## Best Practices & Guidelines

### Code Quality Standards
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for functions
- Keep functions under 50 lines

### Security Standards
- Never hardcode secrets
- Always validate input
- Use parameterized queries
- Implement least privilege

### Reporting Standards
- Always include line numbers
- Provide code snippets for context
- Rate severity (critical/high/medium/low)
- Suggest concrete remediation

### Performance Standards
- Limit analysis to changed files when possible
- Cache results when appropriate
- Provide progress updates for long tasks
- Timeout after 2 minutes, ask to continue
```

**Impact**: Consistent, high-quality output

---

## Schema Compliance

### Pattern: Missing Required Fields

**Problem**: Agent YAML frontmatter incomplete

**Symptoms**:
- Validation fails with "Missing required field"
- Agent won't load or invoke

**Solution**:

Ensure all required fields present:

```yaml
---
name: my-agent           # REQUIRED
description: Brief desc  # REQUIRED
tools: Read, Grep, Glob  # Optional but recommended
model: sonnet            # Optional but recommended
---
```

**Check**:
```bash
python3 validate-agent.py my-agent.md
```

---

### Pattern: Invalid Naming

**Problem**: Agent name violates conventions

**Symptoms**:
- Name contains uppercase, underscores, or special chars
- Name exceeds 64 characters
- Validation fails

**Solution**:

Fix name to follow conventions:

```yaml
# Before (invalid)
name: MyAgent_V2
name: my_agent
name: my.agent

# After (valid)
name: my-agent
name: my-agent-v2
```

**Rules**:
- Lowercase only
- Hyphens allowed
- Numbers allowed
- Max 64 chars
- No underscores, spaces, or special chars

---

## Scope Refinement

### Pattern: Agent Too Broad

**Problem**: Agent tries to do too many things

**Symptoms**:
- Description lists 5+ different responsibilities
- Tools include everything
- Users confused about when to use it
- Overlaps with other agents

**Solution**:

Split into focused agents:

```yaml
# Before (too broad)
name: code-helper
description: Helps with coding, testing, documentation, refactoring, and deployment
tools: Read, Write, Edit, Grep, Glob, Bash, WebFetch, WebSearch

# After (focused)
name: code-reviewer
description: Analyzes code for bugs, security issues, and quality concerns. Use when reviewing PRs or auditing code.
tools: Read, Grep, Glob

name: test-runner
description: Executes test suites and reports failures. Use when validating code changes.
tools: Read, Grep, Bash

name: doc-writer
description: Generates technical documentation and API references. Use when documenting code.
tools: Read, Write, Grep, Glob
```

**Principle**: One agent, one clear purpose

---

### Pattern: Agent Too Narrow

**Problem**: Agent does one trivial thing

**Symptoms**:
- Could be accomplished in single tool call
- No specialized knowledge needed
- Overhead of agent invocation not justified

**Solution**:

Either:
1. Merge into broader agent with related tasks
2. Convert to a command instead of agent
3. Eliminate if redundant

```yaml
# Before (too narrow)
name: file-reader
description: Reads a file
tools: Read

# After (merge or eliminate)
# Just use Read tool directly, no agent needed
```

**Guideline**: Agents should provide specialized expertise or complex workflows

---

## Migration Patterns

### Pattern: Updating to New Tool Names

**Problem**: Agent uses deprecated tool names

**Solution**:
```yaml
# If tools were renamed (hypothetical example)
tools: OldTool, NewTool  # Update to new names
```

**Check**: Refer to migration-guide.md for version-specific changes

---

### Pattern: Schema Version Update

**Problem**: Agent uses outdated schema format

**Solution**: See [migration-guide.md](./migration-guide.md) for version-specific migration instructions

---

## Quick Reference

### Common Update Commands

```bash
# Update description
/agent-builder:agents:update my-agent
> 1 (description)

# Change tools
/agent-builder:agents:update my-agent
> 2 (tools)

# Change model
/agent-builder:agents:update my-agent
> 3 (model)

# Get recommendations
/agent-builder:agents:enhance my-agent

# Compare two agents
/agent-builder:agents:compare agent-a agent-b

# Audit all agents
/agent-builder:agents:audit
```

### Common Scripts

```bash
# Interactive update
python3 update-agent.py my-agent

# Quality analysis
python3 enhance-agent.py my-agent

# Validation only
python3 validate-agent.py my-agent.md
```

---

## Pattern Template

When documenting new patterns, use this template:

```markdown
### Pattern: [Pattern Name]

**Problem**: [What's wrong]

**Symptoms**:
- [Symptom 1]
- [Symptom 2]

**Solution**:
[How to fix]

**Example**:
[Before/after code]

**Impact**: [Benefits of fix]
```

---

## Related Resources

- [Migration Guide](./migration-guide.md) - Schema version migrations
- [Agent Checklist](../templates/agent-checklist.md) - Quality review checklist
- [SKILL.md](../SKILL.md) - Complete agent building guide
