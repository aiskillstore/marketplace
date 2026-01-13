# Agent Definition Schema - Complete Reference

This document provides comprehensive documentation for agent definition file structure, YAML frontmatter schema, and configuration options.

## File Structure

Agent definitions are Markdown files with YAML frontmatter followed by a system prompt:

```markdown
---
[YAML frontmatter]
---

[System prompt in Markdown]
```

**Critical insight**: The system prompt is the Markdown BODY, not a frontmatter field.

## File Locations

### Project-Level Agents
**Path**: `.claude/agents/`
**Scope**: Shared with team, version controlled
**Precedence**: Higher (overrides user-level agents)

### User-Level Agents
**Path**: `~/.claude/agents/`
**Scope**: Personal agents across all projects
**Precedence**: Lower (overridden by project-level)

### Naming Convention
**Format**: `agent-name.md` (kebab-case)
**Examples**: `code-reviewer.md`, `test-runner.md`, `security-auditor.md`

## YAML Frontmatter Fields

### name (REQUIRED)

**Type**: String
**Format**: kebab-case (lowercase with hyphens)
**Purpose**: Unique identifier for the agent

**Examples**:
```yaml
name: test-runner
name: code-reviewer
name: security-auditor
name: deployment-agent
```

**Rules**:
- Must be unique within scope (user or project)
- Use descriptive, action-oriented names
- Keep concise but clear

**Bad examples**:
```yaml
name: agent1              # Too generic
name: do_stuff           # Unclear purpose
name: CodeReviewer       # Wrong case
```

### description (REQUIRED)

**Type**: String (can be multi-line with `|`)
**Purpose**: Tells Claude when to invoke this agent (enables automatic delegation)

**Best practices**:
- Include trigger phrases and use cases
- Use "Use PROACTIVELY" or "MUST BE USED when" for automatic invocation
- Mention key capabilities
- 1-3 sentences optimal, up to 1024 characters

**Examples**:

Simple description:
```yaml
description: Run test suite, diagnose failures, propose fixes. Use after code changes.
```

Detailed description:
```yaml
description: |
  Expert security reviewer specializing in authentication and authorization.
  Use PROACTIVELY after any auth-related code changes. Analyzes for
  vulnerabilities, compliance issues, and security best practices.
  MUST BE USED before merging security-related PRs.
```

Trigger-rich description:
```yaml
description: |
  Researches technologies, libraries, APIs, and best practices.
  Use when evaluating new tools, investigating implementation approaches,
  or gathering technical information. Trigger phrases: "research",
  "investigate", "compare", "evaluate", "find information about".
```

**Trigger keywords**:
- "Use proactively"
- "MUST BE USED when"
- "Automatically invoke for"
- "Required before"
- "Trigger on"
- "Use when user says"

### tools (OPTIONAL)

**Type**: String (comma-separated list)
**Default**: Inherits all tools from main thread
**Purpose**: Restrict agent tool access (security scoping)

**Format**:
```yaml
tools: Read, Write, Edit, Bash, Grep, Glob
```

**Available tools**:
- `Read` - Read files
- `Write` - Create new files
- `Edit` - Modify existing files
- `Bash` - Execute shell commands
- `Grep` - Search file contents
- `Glob` - Find files by pattern
- `WebFetch` - Fetch web content
- `WebSearch` - Search the web
- MCP tools (e.g., `mcp__github__create_pull_request`)

**Tool inheritance behavior**:

**Omit field** (inherits all):
```yaml
---
name: flexible-agent
description: General-purpose agent
# tools field omitted - inherits everything including MCP tools
---
```

**Specify field** (explicit list):
```yaml
---
name: security-reviewer
description: Security-focused code review
tools: Read, Grep, Glob, Bash
# Only these 4 tools, no MCP tools
---
```

**Common configurations**:

Read-only agent:
```yaml
tools: Read, Grep, Glob
```

Research agent:
```yaml
tools: Read, Grep, Glob, WebFetch, WebSearch
```

Code writer:
```yaml
tools: Read, Write, Edit, Bash, Grep, Glob
```

Full-stack agent:
```yaml
tools: Read, Write, Edit, Bash, Grep, Glob, WebFetch, WebSearch
# Plus any needed MCP tools
```

**Security principle**: Grant minimum necessary tools for agent's purpose.

### model (OPTIONAL)

**Type**: String
**Default**: Inherits from main conversation
**Purpose**: Specify which Claude model to use

**Options**:
- `sonnet` - Claude Sonnet (balanced performance and speed)
- `opus` - Claude Opus (highest capability, complex reasoning)
- `haiku` - Claude Haiku (fastest, most efficient)
- `opusplan` - Hybrid (Opus for planning, Sonnet for execution)
- `inherit` - Use same model as parent agent

**Examples**:
```yaml
model: sonnet      # Default, balanced
model: opus        # Complex reasoning
model: haiku       # Fast searches
model: inherit     # Match parent
```

**Selection guidance**:
- **haiku**: Fast searches, simple tasks, token efficiency matters
- **sonnet**: Most tasks, balanced cost/performance
- **opus**: Complex analysis, critical decisions, highest quality
- **inherit**: Consistency with parent agent

### permissionMode (OPTIONAL)

**Type**: String
**Default**: Inherits from session
**Purpose**: Control tool permission behavior

**Values**:
- `default` - Prompt for permission on potentially dangerous operations
- `allowAll` - Allow all operations without prompting (YOLO mode)
- `denyAll` - Deny all tool usage
- Custom permission rules

**Examples**:
```yaml
permissionMode: default    # Standard behavior
permissionMode: allowAll   # Trusted automation
```

**Use with caution**: `allowAll` can make irreversible changes.

### skills (OPTIONAL)

**Type**: String (comma-separated list)
**Purpose**: Auto-load specific skills when agent is invoked

**Format**:
```yaml
skills: testing, debugging, security-analysis
```

**Use cases**:
- Agent needs specialized domain knowledge
- Reuse skill workflows within agent
- Consistent skill access across agents

**Example**:
```yaml
---
name: comprehensive-reviewer
description: Full code review with testing and security analysis
skills: security-analysis, testing-best-practices, code-quality
---
```

## Complete Schema Example

```yaml
---
name: security-auditor
description: |
  Expert security auditor for authentication and authorization code.
  Use PROACTIVELY after any auth-related changes. Analyzes for OWASP
  Top 10 vulnerabilities, compliance issues, and security best practices.
  MUST BE USED before merging security-critical PRs.
tools: Read, Grep, Glob, Bash
model: opus
permissionMode: default
skills: security-analysis, owasp-guidelines
---
```

## System Prompt (Markdown Body)

Everything after the frontmatter is the agent's system prompt.

### Essential Components

1. **Identity/Role Definition**
   ```markdown
   You are a senior security engineer with 15+ years of experience in
   authentication systems and vulnerability assessment.
   ```

2. **Responsibilities**
   ```markdown
   When invoked:
   1. Run git diff to see recent changes
   2. Focus exclusively on modified files
   3. Begin review immediately without asking questions
   ```

3. **Workflow Steps**
   ```markdown
   ## Workflow

   1. **Identify Changes**
      - Run `git diff --cached` or `git diff main`
      - Note all modified authentication/authorization files

   2. **Security Analysis**
      - Check each file against security checklist
      - Identify vulnerabilities by severity

   3. **Generate Report**
      - Provide findings with severity levels
      - Include code snippets and fixes
   ```

4. **Checklists**
   ```markdown
   ## Security Checklist

   - [ ] Input validation on all user-supplied data
   - [ ] Authentication checks before sensitive operations
   - [ ] No hardcoded secrets or API keys
   - [ ] SQL injection prevention (parameterized queries)
   - [ ] XSS prevention (output encoding)
   - [ ] CSRF protection on state-changing operations
   ```

5. **Examples**
   ```markdown
   ## Example Findings Format

   **HIGH SEVERITY: SQL Injection Risk**
   File: auth/login.go:45
   Issue: Direct string concatenation in SQL query
   Code: `query := "SELECT * FROM users WHERE email = '" + email + "'"`
   Fix: Use parameterized queries: `db.Query("SELECT * FROM users WHERE email = ?", email)`
   ```

6. **Output Format**
   ```markdown
   ## Output Format

   Always provide:
   1. Executive Summary (2-3 sentences)
   2. Findings by Severity (Critical, High, Medium, Low)
   3. Recommendations (prioritized action items)
   4. Additional Notes (context, assumptions)
   ```

7. **Boundaries**
   ```markdown
   ## Limitations

   DO NOT:
   - Modify code without explicit approval
   - Run destructive commands (rm, drop, delete)
   - Access production credentials or databases
   - Make external API calls unless necessary for research

   DO:
   - Be thorough but pragmatic
   - Provide specific, actionable feedback
   - Include code examples in recommendations
   - Prioritize issues by severity
   ```

### System Prompt Best Practices

1. **Start with identity** - Set persona and expertise
2. **Define workflow** - Clear step-by-step process
3. **Provide checklists** - Concrete items to verify
4. **Include examples** - Show desired output format
5. **Set boundaries** - Clear DO/DO NOT guidelines
6. **Specify format** - Structured output expectations
7. **Be imperative** - "Run tests", not "Tests should be run"
8. **Add context** - Explain why rules matter

### Prompt Engineering Principles

**Right altitude**: Not too prescriptive (brittle), not too vague (unhelpful)

**Signal-to-noise**: Minimal set of high-signal information that maximizes desired outcome

**Progressive examples**: 3-5 diverse examples showing patterns

**Chain of thought**: Encourage step-by-step reasoning

**XML structure** (optional): Use tags for clarity
```markdown
<instructions>
[Task instructions]
</instructions>

<context>
[Background information]
</context>

<examples>
[Sample inputs/outputs]
</examples>
```

## Validation Requirements

A valid agent definition must:

1. Be located in `.claude/agents/` directory
2. Use `.md` extension with kebab-case naming
3. Have valid YAML frontmatter with `---` delimiters
4. Include required fields: `name`, `description`
5. Use correct data types for all fields
6. Include system prompt (Markdown body)

## File Template

```markdown
# .claude/agents/agent-name.md
---
name: agent-name
description: Clear description with trigger phrases. Use when [scenarios].
tools: Read, Write, Bash, Grep, Glob
model: sonnet
permissionMode: default
skills: relevant-skill
---

# Agent Name

You are [role/persona with expertise].

## Responsibilities

When invoked:
1. [Primary task]
2. [Secondary task]
3. [Output generation]

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
Input: [Input example]
Output: [Expected output]

## Limitations

DO NOT:
- [Boundary 1]
- [Boundary 2]

DO:
- [Guideline 1]
- [Guideline 2]
```

## Common Pitfalls

1. **System prompt in frontmatter**: System prompt goes in Markdown body, not YAML
2. **Wrong name format**: Use kebab-case, not camelCase or snake_case
3. **Vague description**: Include specific trigger phrases and use cases
4. **Over-permissive tools**: Don't inherit all tools unless necessary
5. **Missing examples**: Include 3-5 concrete examples
6. **No boundaries**: Define clear DO/DO NOT guidelines
7. **Declarative language**: Use imperative ("Run tests", not "Tests are run")
8. **Generic role**: Be specific ("security engineer" not "helpful assistant")

## Resources

For prompt engineering best practices, see: `references/prompt-patterns.md`

For Task tool integration, see: `references/task-tool-reference.md`

For advanced features, see: `references/advanced-features.md`
