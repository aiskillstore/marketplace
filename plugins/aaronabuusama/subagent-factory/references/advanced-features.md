# Advanced Features - Hooks, Slash Commands, and MCP Integration

This document covers advanced agent integration patterns including hooks, slash commands, and MCP tool access.

## Hooks Integration

Hooks allow you to inject custom logic at specific points in agent execution.

### Hook Types Relevant to Agents

#### PreToolUse Hook

**Trigger**: After tool parameters created, before tool execution

**Use cases for agents**:
- Validate agent tool inputs before execution
- Modify tool parameters dynamically
- Block dangerous operations
- Log agent tool usage

**Example: Log Agent Tool Calls**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "jq -r '\"[\\(.timestamp)] Agent: \\(.tool_name) - \\(.tool_input | tostring)\"' >> .claude/agent-tool-log.txt"
        }]
      }
    ]
  }
}
```

#### PostToolUse Hook

**Trigger**: After tool completes successfully

**Use cases for agents**:
- Auto-format files created/edited by agents
- Run quality checks on agent outputs
- Send notifications on agent completions
- Archive agent results

**Example: Auto-Format Agent Outputs**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{
          "type": "command",
          "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
        }]
      }
    ]
  }
}
```

#### SubagentStop Hook

**Trigger**: When subagent completes

**Use cases**:
- Capture agent outputs for archival
- Send completion notifications
- Trigger downstream workflows
- Collect metrics on agent performance

**Example: Archive Agent Results**
```bash
#!/bin/bash
# .claude/hooks/subagent-stop-archive.sh

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
AGENT_ID=$(jq -r '.agent_id')
AGENT_TYPE=$(jq -r '.agent_type')

mkdir -p .claude/agent-results
jq '.' > ".claude/agent-results/${AGENT_TYPE}-${AGENT_ID}-${TIMESTAMP}.json"

echo "Agent ${AGENT_TYPE} results archived"
```

```json
{
  "hooks": {
    "SubagentStop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/subagent-stop-archive.sh"
      }]
    }]
  }
}
```

### Hook Configuration for Agents

**Location**: `.claude/settings.json` or `.claude/settings.local.json`

**Pattern**: Combine hooks with agent definitions for powerful workflows

**Example: Quality Gate for Code-Writing Agents**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write(*.go)|Edit(*.go)",
        "hooks": [
          {
            "type": "command",
            "command": "gofmt -w \"$file_path\""
          },
          {
            "type": "command",
            "command": ".claude/hooks/go-lint.sh"
          }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/bash
# .claude/hooks/go-lint.sh

FILE_PATH=$(jq -r '.tool_input.file_path')

# Run linter
golangci-lint run "$FILE_PATH" > /tmp/lint-output.txt 2>&1

if [ $? -ne 0 ]; then
    # Return blocking decision with feedback
    jq -n \
        --arg reason "$(cat /tmp/lint-output.txt)" \
        '{
            "decision": "block",
            "reason": ("Linting failed:\n" + $reason),
            "continue": true
        }'
    exit 0
fi

echo "Code quality checks passed"
exit 0
```

## Slash Commands for Agents

Slash commands can invoke agents or complement agent workflows.

### Pattern 1: Slash Command Invokes Agent

Create a slash command that triggers specific agent:

```markdown
<!-- .claude/commands/security-audit.md -->
---
description: Run comprehensive security audit
---

Use the security-auditor agent to perform a comprehensive security audit
of all authentication and authorization code in the codebase.

Focus on:
- OWASP Top 10 vulnerabilities
- Authentication bypasses
- Authorization issues
- Cryptographic weaknesses

Provide a detailed report with severity levels and specific fixes.
```

**Usage**: `/security-audit`

**Result**: Triggers security-auditor agent with predefined scope

### Pattern 2: Slash Command Provides Context to Agent

```markdown
<!-- .claude/commands/review-pr.md -->
---
argument-hint: [pr-number]
description: Review pull request with code-reviewer agent
allowed-tools: Bash(gh:*), Read
---

## Context

PR #$1 details: !`gh pr view $1`
PR #$1 diff: !`gh pr diff $1`
PR #$1 checks: !`gh pr checks $1`

## Task

Use the code-reviewer agent to review PR #$1.

Focus areas:
1. Code quality and maintainability
2. Security vulnerabilities
3. Performance implications
4. Test coverage

Provide structured review with:
- Executive summary
- Issues by severity
- Recommendations
```

**Usage**: `/review-pr 123`

**Result**: Gathers PR context, then invokes code-reviewer agent

### Pattern 3: Agent-Specific Commands

Create commands that configure agent parameters:

```markdown
<!-- .claude/commands/deep-security-audit.md -->
---
description: Deep security audit with opus model
---

Use the security-auditor agent with these settings:
- Model: opus (highest capability)
- Scope: Entire codebase
- Focus: Authentication, authorization, cryptography
- Thoroughness: Maximum (check all branches, all scenarios)

This will take longer but provide most comprehensive analysis.
```

## MCP Tool Access in Agents

Agents can use MCP tools when properly configured.

### MCP Tool Inheritance

**Omit tools field** - Agent inherits MCP tools:
```yaml
---
name: github-pr-creator
description: Creates GitHub PRs with proper formatting
# tools field omitted - inherits MCP tools
---
```

**Specify tools field** - MCP tools NOT inherited:
```yaml
---
name: code-reviewer
description: Reviews code for quality issues
tools: Read, Grep, Glob
# MCP tools NOT available
---
```

### Granting MCP Tools to Agents

**Method 1: Omit tools field (inherit all)**
```yaml
---
name: full-stack-agent
description: Complete feature implementation including PR creation
# Inherits all MCP tools from main thread
---
```

**Method 2: Explicitly list MCP tool**
```yaml
---
name: github-agent
description: GitHub-specific operations
tools: Read, Write, Bash, mcp__github__create_pull_request, mcp__github__create_issue
---
```

### MCP Tool Naming Pattern

MCP tools follow this pattern:
```
mcp__<server-name>__<tool-name>
```

**Examples**:
- `mcp__github__create_pull_request`
- `mcp__postgres__query`
- `mcp__slack__send_message`

### Example: Agent with GitHub MCP Integration

```markdown
# .claude/agents/pr-creator.md
---
name: pr-creator
description: Creates GitHub pull requests with proper formatting, labels, and reviewers
# Omit tools to inherit MCP tools
---

# PR Creator Agent

You create well-formatted GitHub pull requests.

## Workflow

### Step 1: Gather Changes
1. Run `git status` to see current branch
2. Run `git diff main` to see all changes
3. Run `git log --oneline main..HEAD` to see commit history

### Step 2: Analyze Changes
- Identify primary purpose of changes (feature, bugfix, refactor)
- Note files modified and their purpose
- Identify any breaking changes

### Step 3: Draft PR Content

**Title format**: `[type]: brief description`
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

**Body format**:
```markdown
## Summary
[What changed and why]

## Changes
- [Key change 1]
- [Key change 2]

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Notes
[Any additional context]
```

### Step 4: Create PR

Use the `mcp__github__create_pull_request` tool with:
- Title: Generated title
- Body: Generated body
- Base: main (or specified branch)
- Head: Current branch
- Labels: Appropriate labels based on changes
- Reviewers: Based on CODEOWNERS or specified

## Example Output

```
Created PR #456: feat: add user authentication
https://github.com/org/repo/pull/456

Labels: enhancement, security
Reviewers: @security-team, @backend-lead
```
```

### Discovering Available MCP Tools

**In agent prompt**:
```markdown
## Available MCP Tools

Check available MCP tools by examining the tool list provided to you.

Common MCP servers:
- GitHub: PR creation, issue management, code search
- PostgreSQL: Database queries and schema inspection
- Slack: Message sending, channel management
- Puppeteer: Browser automation and testing
```

**Via Claude**:
```
List all available MCP tools for agent integration
```

## Agent Coordination Patterns

### Pattern: Main Agent Orchestrates Subagents

```markdown
## Multi-Agent Workflow

Execute this pipeline:

### Phase 1: Analysis (Parallel)
Spawn 3 explore agents:
1. Security analysis of auth code
2. Performance analysis of database queries
3. Code quality analysis of business logic

### Phase 2: Implementation (Sequential)
Based on Phase 1 findings:
1. Use code-implementer agent to fix top 3 issues from each analysis
2. Use test-runner agent to verify fixes don't break tests
3. Use code-reviewer agent to review all fixes

### Phase 3: Delivery
1. Use pr-creator agent (with GitHub MCP) to create PR with findings and fixes
2. Use slack-notifier agent (with Slack MCP) to notify team
```

### Pattern: Agent Uses Hooks for Quality Gates

Combine agent with hooks to enforce standards:

**Agent definition**:
```yaml
---
name: feature-implementer
description: Implements features with automatic quality enforcement
tools: Read, Write, Edit, Bash, Grep, Glob
---
```

**Hook configuration**:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write(*.ts)|Edit(*.ts)",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$file_path\""
          },
          {
            "type": "command",
            "command": "npx eslint \"$file_path\" --fix"
          },
          {
            "type": "command",
            "command": ".claude/hooks/typescript-validate.sh"
          }
        ]
      }
    ]
  }
}
```

**Result**: Every file agent writes is automatically formatted, linted, and validated

## Custom MCP Servers for Agents

### Use Case: Project-Specific Tools

Create custom MCP server with tools specifically for your agents:

```typescript
// beads-mcp-server/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server(
  { name: "beads-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// Tool: Get ready tasks
server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "get_ready_tasks",
      description: "Get unblocked tasks ready for implementation",
      inputSchema: {
        type: "object",
        properties: {
          priority: {
            type: "string",
            enum: ["P0", "P1", "P2", "P3", "P4"],
            description: "Minimum priority level"
          }
        }
      }
    }
  ]
}));

server.setRequestHandler("tools/call", async (request) => {
  if (request.params.name === "get_ready_tasks") {
    const { priority } = request.params.arguments || {};

    // Execute: bd ready --min-priority=P1
    const { execSync } = require('child_process');
    const output = execSync(`bd ready --min-priority=${priority || 'P4'}`, {
      encoding: 'utf-8'
    });

    return {
      content: [{
        type: "text",
        text: output
      }]
    };
  }

  throw new Error(`Unknown tool: ${request.params.name}`);
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Beads MCP server running");
}

main().catch(console.error);
```

**Register server**:
```bash
claude mcp add beads-server -s project -- node ./beads-mcp-server/index.js
```

**Use in agent**:
```yaml
---
name: task-worker
description: Finds and completes ready tasks
# Inherits mcp__beads-server__get_ready_tasks
---

When invoked:
1. Use `mcp__beads-server__get_ready_tasks` to find available work
2. Select highest priority task
3. Implement the task
4. Mark as complete
```

## Best Practices

### Hook Integration

1. **Log strategically** - Track important agent actions without noise
2. **Use PostToolUse for formatting** - Automatic cleanup of agent outputs
3. **Use PreToolUse for guards** - Prevent dangerous agent operations
4. **SubagentStop for metrics** - Track agent performance and outcomes

### Slash Command Integration

1. **Commands provide context** - Gather info before invoking agent
2. **Commands parameterize agents** - Customize agent behavior per invocation
3. **Commands chain workflows** - Orchestrate multiple agents
4. **Keep commands focused** - One command per agent/workflow

### MCP Tool Integration

1. **Explicit tool lists** - Specify exactly which MCP tools agent needs
2. **Document tools in prompt** - Tell agent what MCP tools are available
3. **Create project-specific MCPs** - Custom tools for your domain
4. **Test MCP tool access** - Verify agent can use MCP tools before deployment

### Agent Coordination

1. **Main agent orchestrates** - Don't have agents spawn other agents
2. **Use hooks for automation** - Automatic quality/formatting, not manual in agent
3. **Leverage MCP for integrations** - External services via MCP, not bash
4. **Summary protocol** - Subagents summarize for main agent

## Common Integration Patterns

### Pattern: Full Development Pipeline

```markdown
<!-- .claude/commands/full-feature.md -->
---
argument-hint: [feature-description]
description: Complete feature development pipeline
---

## Context
Feature: $ARGUMENTS
Current branch: !`git branch --show-current`
Recent commits: !`git log --oneline -5`

## Pipeline

### Phase 1: Planning
Use the tech-researcher agent to:
- Research implementation approaches
- Evaluate library options
- Identify potential challenges

### Phase 2: Implementation
Use the feature-implementer agent to:
- Create necessary files
- Implement core logic
- Add error handling
- Write inline documentation

### Phase 3: Testing
Use the test-runner agent to:
- Generate appropriate tests
- Verify implementation
- Check edge cases
- Ensure coverage

### Phase 4: Review
Use the code-reviewer agent to:
- Review implementation quality
- Check for issues
- Verify best practices

### Phase 5: Delivery
Use the pr-creator agent to:
- Create well-formatted PR
- Add appropriate labels
- Assign reviewers
- Link related issues
```

### Pattern: Quality Enforcement

**Hook-based automatic quality**:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "npx prettier --write \"$file_path\"" },
          { "type": "command", "command": ".claude/hooks/lint.sh" },
          { "type": "command", "command": ".claude/hooks/type-check.sh" }
        ]
      }
    ]
  }
}
```

**Agent focuses on logic, hooks handle quality**.

## Resources

For agent schema, see: `references/agent-schema.md`

For Task tool usage, see: `references/task-tool-reference.md`

For prompt patterns, see: `references/prompt-patterns.md`
