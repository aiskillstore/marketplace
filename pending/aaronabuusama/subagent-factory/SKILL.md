---
name: subagent-factory
description: Create specialized Claude Code agents on-the-fly. Guides through agent definition file creation with proper frontmatter, effective prompts, and tool scoping. USE WHEN user says 'create agent', 'new subagent', 'make an agent for', 'build agent', 'spawn agent', or wants to define custom agents for specific tasks.
---

# Subagent Factory

Factory for creating specialized Claude Code agents. Generates agent definition files with proper configuration, effective system prompts, and appropriate tool access.

## When to Activate This Skill

- User says: "create agent", "new subagent", "build agent"
- User wants: Custom agents for specific tasks
- User needs: Agent definition files, system prompts, tool configuration
- User asks: How to make specialized agents, how to delegate work

## Two Creation Modes

### Quick Mode (Direct Creation)
Fast path for experienced users. Minimal questions, direct file generation.

**Use when**: You know exactly what agent you need.

See: `workflows/quick-create.md`

### Interview Mode (Guided Creation)
Interactive workflow with questions and customization at each step.

**Use when**: Exploring agent design, learning the process, or creating complex agents.

See: `workflows/interview-create.md`

## Quick Reference: Agent Schema

### Required Frontmatter Fields

```yaml
---
name: agent-name                    # REQUIRED: kebab-case identifier
description: When to use this agent # REQUIRED: natural language triggers
---
```

### Optional Frontmatter Fields

```yaml
tools: Read, Write, Bash           # Comma-separated, omit to inherit all
model: sonnet                      # sonnet|opus|haiku|inherit
permissionMode: default            # Permission handling mode
skills: skill-name                 # Auto-load skills
```

### System Prompt (Markdown Body)

The Markdown content after frontmatter is the agent's system prompt.

**Key elements**:
1. Identity/role definition
2. Clear responsibilities
3. Step-by-step workflow
4. Concrete checklists
5. Output format specification
6. Boundaries (DO/DO NOT)

## Core Principles

### 1. Single Responsibility
Each agent should have ONE clear purpose, not multiple loosely-related tasks.

### 2. Right Altitude
Not too prescriptive (brittle if-else logic), not too vague (unhelpful platitudes). Give clear guidance that lets the agent think.

### 3. Explicit Tool Scoping
Grant minimum necessary tools. Read-only agents don't need Write. Reviewers don't need Bash.

### 4. Progressive Examples
Include 3-5 concrete examples showing desired behavior patterns.

### 5. Actionable Instructions
Use imperative form: "Run tests", "Analyze code", "Generate report" (not "The tests are run").

## Navigation

### Deep Documentation
- `references/agent-schema.md` - Complete frontmatter reference
- `references/task-tool-reference.md` - Task tool parameters and usage
- `references/prompt-patterns.md` - Effective prompt engineering patterns
- `references/advanced-features.md` - Hooks, slash commands, MCP integration

### Workflows
- `workflows/quick-create.md` - Fast agent creation steps
- `workflows/interview-create.md` - Interactive guided creation

## Agent Types by Tool Access

### Read-Only Agents (Reviewers, Auditors)
```yaml
tools: Read, Grep, Glob
```
**Use for**: Code review, security audits, compliance checks

### Research Agents (Analysts)
```yaml
tools: Read, Grep, Glob, WebFetch, WebSearch, Write (if need to save research)
```
**Use for**: Technology research, documentation lookup, best practices

### Code Writers (Implementers)
```yaml
tools: Read, Write, Edit, Bash, Grep, Glob
```
**Use for**: Feature implementation, bug fixes, refactoring

### Full-Stack Agents (End-to-End)
```yaml
tools: Read, Write, Edit, Bash, Grep, Glob, WebFetch
# Plus MCP tools as needed
```
**Use for**: Complete feature delivery, integration work

## Common Agent Patterns

### Security Reviewer
**Purpose**: Analyze code for vulnerabilities
**Tools**: Read, Grep, Glob
**Key checklist**: Input validation, authentication, secrets, SQL injection, XSS, CSRF

### Test Runner
**Purpose**: Execute tests, diagnose failures, propose fixes
**Tools**: Read, Edit, Write, Bash, Grep, Glob
**Key workflow**: Run tests → Diagnose failures → Propose fixes → Verify

### Tech Researcher
**Purpose**: Investigate technologies, APIs, best practices
**Tools**: Read, Grep, Glob, WebFetch, WebSearch
**Key output**: Comparison matrix, recommendation with rationale, next steps

### Code Implementer
**Purpose**: Build features following specifications
**Tools**: Read, Write, Edit, Bash, Grep, Glob
**Key workflow**: Understand requirements → Design → Implement → Test → Document

## File Location

Agent definitions go in:
- **Project-level**: `.claude/agents/` (version controlled, team-shared)
- **User-level**: `~/.claude/agents/` (personal agents)

**Precedence**: Project agents override user agents with same name.

## Task Tool Integration

Agents are invoked via the Task tool:

```
Use the security-reviewer agent to analyze the authentication module for vulnerabilities.
```

**Built-in agent types**:
- `general-purpose` - Full tools, Sonnet model
- `explore` - Read-only, Haiku model (fast searches)
- `plan` - Research and analysis during planning

**Custom agents**: Reference by name from `.claude/agents/`

**Parallel execution**: Up to 10 concurrent agents (automatic queuing for more)

## Key Insights

1. **System prompt is Markdown body, NOT frontmatter** - Common mistake
2. **Tool inheritance** - Omit `tools` field to inherit all; specify to restrict
3. **Model selection** - Use `haiku` for fast searches, `sonnet` for balanced work, `opus` for complex reasoning
4. **Token overhead** - Each agent spawn costs ~20k tokens; balance parallelization
5. **Context isolation** - Each agent has independent context window (prevents cross-contamination)

## Quick Start

**Simple example**:
```markdown
# .claude/agents/test-runner.md
---
name: test-runner
description: Run tests, diagnose failures, propose fixes. Use after code changes.
tools: Read, Edit, Bash, Grep
model: sonnet
---

You are a test automation specialist.

## Workflow
1. Run test suite using project test command
2. If failures: capture output, read test files, diagnose root cause
3. Propose minimal fix with rationale
4. Re-run to verify

## Output Format
- Test results summary
- Failure analysis (if any)
- Proposed fixes with evidence
```

For detailed examples and patterns, see reference documentation.

## Next Steps

1. Choose creation mode (quick or interview)
2. Define agent purpose and responsibilities
3. Select appropriate tools
4. Write effective system prompt
5. Test with realistic scenarios
6. Iterate based on failures

Start with `workflows/quick-create.md` for direct creation or `workflows/interview-create.md` for guided process.
