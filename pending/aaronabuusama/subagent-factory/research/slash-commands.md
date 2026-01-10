# Claude Code: Slash Commands, Hooks, and Custom Tool Creation

## Research compiled: 2025-12-16

This document provides comprehensive guidance on extending Claude Code through slash commands, hooks, and custom MCP tools.

---

## Table of Contents

1. [Slash Commands](#slash-commands)
2. [Hooks System](#hooks-system)
3. [Custom MCP Tools](#custom-mcp-tools)
4. [Integration Patterns](#integration-patterns)

---

## Slash Commands

### Overview

Slash commands are custom Markdown-based prompts that extend Claude Code's capabilities. They can be project-scoped (shared with team) or user-scoped (personal).

### File Locations

- **Project commands**: `.claude/commands/` (version controlled, shared with team)
- **User commands**: `~/.claude/commands/` (personal, all projects)
- **MCP commands**: Dynamically discovered from MCP servers

### Command Structure

#### Basic File Format

```markdown
# .claude/commands/optimize.md
Analyze this code for performance issues and suggest optimizations.
```

**Usage**: `/optimize`

#### With Frontmatter Metadata

```markdown
---
description: Create a git commit
argument-hint: [message]
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
model: claude-3-5-haiku-20241022
disable-model-invocation: false
---

Create a git commit with message: $ARGUMENTS
```

### Frontmatter Fields Reference

| Field | Purpose | Default |
|-------|---------|---------|
| `description` | Brief command description shown in `/help` | First line of prompt |
| `allowed-tools` | Tools the command can use | Inherits from conversation |
| `argument-hint` | Expected arguments format | None |
| `model` | Specific model to use | Inherits from conversation |
| `disable-model-invocation` | Prevent Claude from auto-invoking | false |

### Arguments System

#### All Arguments: `$ARGUMENTS`

Captures everything passed to the command:

```markdown
# .claude/commands/fix-issue.md
Fix issue #$ARGUMENTS following our coding standards
```

```bash
/fix-issue 123 high-priority
# $ARGUMENTS = "123 high-priority"
```

#### Positional Arguments: `$1`, `$2`, etc.

```markdown
---
argument-hint: [pr-number] [priority] [assignee]
description: Review pull request
---

Review PR #$1 with priority $2 and assign to $3.
Focus on security, performance, and code style.
```

```bash
/review-pr 456 high alice
# $1 = "456", $2 = "high", $3 = "alice"
```

### Bash Command Execution

Use `!` prefix to execute bash commands before the slash command runs. Output is included in context.

**Important**: Must include `Bash` in `allowed-tools`.

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*)
description: Create a git commit
---

## Context

- Current git status: !`git status`
- Current git diff: !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your task

Based on the above changes, create a single git commit.
```

### File References

Include file contents using `@` prefix:

```markdown
# Single file reference
Review the implementation in @src/utils/helpers.js

# Multiple files
Compare @src/old-version.js with @src/new-version.js
```

### Namespacing

Organize commands into subdirectories:

```
.claude/commands/
├── optimize.md                  # /optimize
├── frontend/
│   └── component.md            # /component (project:frontend)
└── backend/
    └── test.md                 # /test (project:backend)
```

**Key behaviors**:
- Subdirectories appear in description but don't affect command name
- Project commands override user commands with the same name
- Different subdirectories can have identical command names (distinguished by label)

### SlashCommand Tool

Claude can programmatically execute slash commands using the `SlashCommand` tool.

**Enable**:
```markdown
# In CLAUDE.md
Run /write-unit-test when you are about to start writing tests.
```

**Disable globally**:
```bash
/permissions
# Add to deny: SlashCommand
```

**Disable specific command**:
```yaml
# In command frontmatter
disable-model-invocation: true
```

### Character Budget

- **Default**: 15,000 characters
- **Custom**: Set `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable
- **Includes**: Command name, arguments, and description

When exceeded, Claude sees only a subset of available commands.

### Creation Examples

#### Simple Command

```bash
mkdir -p .claude/commands
cat > .claude/commands/optimize.md << 'EOF'
Analyze this code for performance issues and suggest optimizations.
EOF
```

#### Command with Arguments

```bash
cat > .claude/commands/commit.md << 'EOF'
---
argument-hint: [message]
description: Create a git commit
---

Create a git commit with message: $ARGUMENTS
EOF
```

#### Command with Bash Execution

```bash
mkdir -p ~/.claude/commands
cat > ~/.claude/commands/security-review.md << 'EOF'
---
allowed-tools: Bash(git diff:*), Bash(grep:*)
description: Review code for security vulnerabilities
---

## Context

Latest changes: !`git diff HEAD`

## Task

Review for security vulnerabilities including:
- SQL injection risks
- XSS vulnerabilities
- Authentication bypasses
- Hardcoded secrets
EOF
```

---

## Hooks System

### Overview

Hooks inject custom logic at specific points in Claude Code's lifecycle. They run shell commands or LLM prompts in response to events.

### Configuration Location

Hooks are defined in settings files at three levels:

1. **Project shared**: `.claude/settings.json` (version controlled)
2. **Project local**: `.claude/settings.local.json` (gitignored)
3. **User global**: `~/.claude/settings.local.json`

### Hook Types

| Hook Type | Trigger Point |
|-----------|---------------|
| `SessionStart` | Session initialization |
| `UserPromptSubmit` | Before Claude processes user prompt |
| `PreToolUse` | After parameters created, before tool execution |
| `PostToolUse` | After tool completes successfully |
| `PermissionRequest` | When Claude requests tool permission |
| `Stop` | When Claude finishes responding |
| `SubagentStop` | When subagent completes |
| `PreCompact` | Before conversation compaction |
| `Notification` | When Claude sends notification |

### Configuration Format

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "your-command-here",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

### Matcher Patterns

**For PreToolUse and PostToolUse only**:

- `"Write"` - Exact tool name match (case-sensitive)
- `"Edit|Write"` - Multiple tools (pipe-separated)
- `"*"` - All tools
- `""` or omitted - All tools
- `"Write(*.py)"` - File pattern matching
- `"mcp__github__create_pull_request"` - MCP tool names

### Hook Types

#### Type: `command`

Executes a shell command:

```json
{
  "type": "command",
  "command": "npx prettier --write \"$file_path\""
}
```

#### Type: `prompt`

Sends prompt to LLM for evaluation:

```json
{
  "type": "prompt",
  "prompt": "Does this code follow our security guidelines?"
}
```

### Exit Codes

Hook scripts communicate results via exit codes:

- **0**: Success, allow operation
- **2**: Critical blocking error (PreToolUse only), stderr sent to Claude
- **Other**: Non-blocking error, stderr shown to user

### JSON Output Control

Hooks can return structured JSON for sophisticated control:

```json
{
  "continue": true,
  "decision": "block" | "approve" | undefined,
  "reason": "Explanation message",
  "suppressOutput": false,
  "stopReason": "Message shown when continue is false"
}
```

**Decision types**:

**PreToolUse**:
- `"approve"` - Bypasses permissions, shows reason to user
- `"block"` - Prevents execution, reason shown to Claude

**PostToolUse**:
- `"block"` - Provides automated feedback to Claude

**Stop**:
- `"block"` - Prevents stopping, forces continuation

### Environment Variables

Available in all hooks:

- `CLAUDE_PROJECT_DIR` - Absolute path to project root
- `CLAUDE_CODE_REMOTE` - `true` if web environment, `false` if local CLI
- `CLAUDE_ENV_FILE` - Path to environment file for setting session variables

### PreToolUse Examples

#### 1. Log Bash Commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '\"\\(.tool_input.command) - \\(.tool_input.description // \"No description\")\"' >> ~/.claude/bash-command-log.txt"
          }
        ]
      }
    ]
  }
}
```

#### 2. Block Dangerous Commands

```bash
#!/bin/bash
# .claude/hooks/pre-bash-firewall.sh

COMMAND=$(jq -r '.tool_input.command')

# Block dangerous patterns
if echo "$COMMAND" | grep -qE "rm -rf|sudo rm|chmod 777|>/etc/"; then
    echo "BLOCKED: Dangerous command pattern detected" >&2
    exit 2
fi

exit 0
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/pre-bash-firewall.sh"
          }
        ]
      }
    ]
  }
}
```

#### 3. Require Tests Before PR

```bash
#!/bin/bash
# .claude/hooks/pre-pr-requires-tests.sh

# Run tests
npm test > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "Tests must pass before creating PR" >&2
    exit 2
fi

exit 0
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__github__create_pull_request",
        "hooks": [{
          "type": "command",
          "command": ".claude/hooks/pre-pr-requires-tests.sh"
        }]
      }
    ]
  }
}
```

#### 4. Modify Tool Input (v2.0.10+)

PreToolUse hooks can modify tool parameters before execution:

```bash
#!/bin/bash
# .claude/hooks/pre-write-add-header.sh

FILE_PATH=$(jq -r '.tool_input.file_path')

# Add header to content if it's a Python file
if [[ "$FILE_PATH" == *.py ]]; then
    CONTENT=$(jq -r '.tool_input.content')
    HEADER="# Generated by Claude Code\n# Date: $(date)\n\n"

    jq --arg content "$HEADER$CONTENT" '.tool_input.content = $content'
fi
```

### PostToolUse Examples

#### 1. Auto-format TypeScript Files

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | { read file_path; if echo \"$file_path\" | grep -q '\\.ts$'; then npx prettier --write \"$file_path\"; fi; }"
          }
        ]
      }
    ]
  }
}
```

#### 2. Quality Checks with Feedback

```bash
#!/bin/bash
# .claude/hooks/post-edit-quality.sh

FILE_PATH=$(jq -r '.tool_input.file_path')

# Run linter
LINT_OUTPUT=$(npx eslint "$FILE_PATH" 2>&1)

if [ $? -ne 0 ]; then
    # Return blocking decision with feedback
    jq -n \
        --arg reason "Linting failed:\n$LINT_OUTPUT" \
        '{
            "decision": "block",
            "reason": $reason,
            "continue": true
        }'
    exit 0
fi

echo "Quality checks passed"
exit 0
```

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{
          "type": "command",
          "command": ".claude/hooks/post-edit-quality.sh"
        }]
      }
    ]
  }
}
```

#### 3. Convert Transcript to JSON

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "jq '.' > logs/chat.json"
        }]
      }
    ]
  }
}
```

### Other Hook Examples

#### SessionStart: Load Development Context

```bash
#!/bin/bash
# .claude/hooks/session-start.sh

{
    echo "## Recent Git Activity"
    git log --oneline -5
    echo ""
    echo "## Current Branch Status"
    git status
    echo ""
    echo "## Open Issues"
    gh issue list --limit 5
} > /tmp/session-context.txt

# Make context available to Claude
echo "Development context loaded. See /tmp/session-context.txt"
```

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/session-start.sh"
      }]
    }]
  }
}
```

#### Stop: Generate Completion Message

```bash
#!/bin/bash
# .claude/hooks/stop-completion.sh

# Generate completion message using AI
curl -s https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Generate a motivating completion message for a developer"}]
  }' | jq -r '.choices[0].message.content'
```

#### PreCompact: Backup Transcript

```bash
#!/bin/bash
# .claude/hooks/pre-compact-backup.sh

BACKUP_DIR="$CLAUDE_PROJECT_DIR/.claude/backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
cp "$CLAUDE_PROJECT_DIR/.claude/transcript.json" \
   "$BACKUP_DIR/transcript-$TIMESTAMP.json"

echo "Transcript backed up to $BACKUP_DIR/transcript-$TIMESTAMP.json"
```

### Hook Configuration Tips

1. **Start simple**: Begin with one hook solving a real pain point
2. **Use PostToolUse for formatters**: Immediate, visible feedback
3. **PreToolUse for guards**: Prevent dangerous operations
4. **Log strategically**: Track important events without noise
5. **Test timeout**: Default 60s may need adjustment for slow operations
6. **Review changes**: Use `/hooks` menu to activate hook modifications
7. **Parallel execution**: All matching hooks run simultaneously
8. **Deduplication**: Identical commands only run once

---

## Custom MCP Tools

### Overview

Model Context Protocol (MCP) is the standard for extending Claude Code with custom tools, resources, and prompts. Think of it as "USB-C for AI" - a universal connection standard.

### MCP Architecture

**Three layers**:

1. **Application Layer**: Your tool definitions (Tools, Resources, Prompts)
2. **Protocol Layer**: MCP message routing and capability negotiation
3. **Transport Layer**: Communication channel (stdio, HTTP/SSE)

### Configuration Files

MCP servers can be configured in:

1. **Project MCP**: `.mcp.json` (version controlled)
2. **Project local**: `.claude/settings.local.json` (gitignored)
3. **User global**: `~/.claude/settings.local.json`

### MCP CLI Commands

```bash
# Add server
claude mcp add [name] --scope user -- npx -y @modelcontextprotocol/server-filesystem ~/Documents

# List servers
claude mcp list

# Remove server
claude mcp remove [name]

# Test server
claude mcp get [name]
```

### Pre-built MCP Servers

Popular official servers:

```bash
# Filesystem access
claude mcp add filesystem -s user -- npx -y @modelcontextprotocol/server-filesystem ~/Documents ~/Projects

# GitHub
claude mcp add github -s user -e GITHUB_TOKEN=your-token -- npx -y @modelcontextprotocol/server-github

# PostgreSQL
claude mcp add postgres -s user -e DATABASE_URL=your-db-url -- npx -y @modelcontextprotocol/server-postgres

# Puppeteer (browser automation)
claude mcp add puppeteer -s user -- npx -y @modelcontextprotocol/server-puppeteer

# Slack
claude mcp add slack -s user -e SLACK_BOT_TOKEN=your-token -- npx -y @modelcontextprotocol/server-slack
```

### Tool Naming Convention

MCP tools are automatically prefixed:

```
mcp__plugin_<plugin-name>_<server-name>__<tool-name>
```

Example: `mcp__github__create_pull_request`

### Creating Custom MCP Server

#### 1. Project Setup

```bash
mkdir my-mcp-server
cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
```

#### 2. Basic Server Structure

```typescript
// index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Initialize server
const server = new Server(
  {
    name: "my-custom-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define a tool
server.setRequestHandler(
  "tools/list",
  async () => ({
    tools: [
      {
        name: "greet",
        description: "Greets a person by name",
        inputSchema: {
          type: "object",
          properties: {
            name: {
              type: "string",
              description: "Name of the person to greet",
            },
          },
          required: ["name"],
        },
      },
    ],
  })
);

// Tool request handler
server.setRequestHandler(
  "tools/call",
  async (request) => {
    if (request.params.name === "greet") {
      const { name } = request.params.arguments as { name: string };

      return {
        content: [
          {
            type: "text",
            text: `Hello, ${name}! Welcome to MCP.`,
          },
        ],
      };
    }

    throw new Error(`Unknown tool: ${request.params.name}`);
  }
);

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP Server running on stdio");
}

main().catch(console.error);
```

#### 3. Tool Definition with Zod Validation

```typescript
import { z } from "zod";

// Define input schema
const CalculateSchema = z.object({
  operation: z.enum(["add", "subtract", "multiply", "divide"]),
  a: z.number(),
  b: z.number(),
});

type CalculateInput = z.infer<typeof CalculateSchema>;

// Register tool
server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "calculate",
      description: "Performs basic arithmetic operations",
      inputSchema: {
        type: "object",
        properties: {
          operation: {
            type: "string",
            enum: ["add", "subtract", "multiply", "divide"],
            description: "Arithmetic operation to perform",
          },
          a: {
            type: "number",
            description: "First operand",
          },
          b: {
            type: "number",
            description: "Second operand",
          },
        },
        required: ["operation", "a", "b"],
      },
    },
  ],
}));

// Implement handler
server.setRequestHandler("tools/call", async (request) => {
  if (request.params.name === "calculate") {
    const validated = CalculateSchema.parse(request.params.arguments);

    let result: number;
    switch (validated.operation) {
      case "add":
        result = validated.a + validated.b;
        break;
      case "subtract":
        result = validated.a - validated.b;
        break;
      case "multiply":
        result = validated.a * validated.b;
        break;
      case "divide":
        if (validated.b === 0) {
          return {
            content: [
              { type: "text", text: "Error: Division by zero" }
            ],
            isError: true,
          };
        }
        result = validated.a / validated.b;
        break;
    }

    return {
      content: [
        {
          type: "text",
          text: `${validated.a} ${validated.operation} ${validated.b} = ${result}`,
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${request.params.name}`);
});
```

#### 4. External API Integration Example

```typescript
// Google Calendar integration
server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "get_calendar_events",
      description: "Fetches upcoming calendar events",
      inputSchema: {
        type: "object",
        properties: {
          date: {
            type: "string",
            description: "Date in YYYY-MM-DD format",
          },
        },
        required: ["date"],
      },
    },
  ],
}));

server.setRequestHandler("tools/call", async (request) => {
  if (request.params.name === "get_calendar_events") {
    const { date } = request.params.arguments as { date: string };

    try {
      // Authenticate and fetch from Google Calendar API
      const auth = new google.auth.GoogleAuth({
        credentials: JSON.parse(process.env.GOOGLE_CREDENTIALS),
        scopes: ['https://www.googleapis.com/auth/calendar.readonly'],
      });

      const calendar = google.calendar({ version: 'v3', auth });

      const response = await calendar.events.list({
        calendarId: 'primary',
        timeMin: new Date(date).toISOString(),
        timeMax: new Date(date + 'T23:59:59').toISOString(),
        singleEvents: true,
        orderBy: 'startTime',
      });

      const events = response.data.items || [];

      if (events.length === 0) {
        return {
          content: [{ type: "text", text: "No events found for this date." }],
        };
      }

      const eventList = events
        .map(event => `- ${event.summary} at ${event.start.dateTime}`)
        .join('\n');

      return {
        content: [
          {
            type: "text",
            text: `Events on ${date}:\n${eventList}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          { type: "text", text: `Error fetching calendar: ${error.message}` }
        ],
        isError: true,
      };
    }
  }
});
```

#### 5. Resources (Read-only Data)

```typescript
// Expose resources
server.setRequestHandler("resources/list", async () => ({
  resources: [
    {
      uri: "config://settings",
      name: "Application Settings",
      description: "Current application configuration",
      mimeType: "application/json",
    },
  ],
}));

server.setRequestHandler("resources/read", async (request) => {
  if (request.params.uri === "config://settings") {
    const settings = {
      theme: "dark",
      notifications: true,
      apiUrl: "https://api.example.com",
    };

    return {
      contents: [
        {
          uri: request.params.uri,
          mimeType: "application/json",
          text: JSON.stringify(settings, null, 2),
        },
      ],
    };
  }

  throw new Error(`Unknown resource: ${request.params.uri}`);
});
```

#### 6. Prompts (Reusable Templates)

```typescript
// Define prompts
server.setRequestHandler("prompts/list", async () => ({
  prompts: [
    {
      name: "code_review",
      description: "Review code for quality and security",
      arguments: [
        {
          name: "language",
          description: "Programming language",
          required: true,
        },
      ],
    },
  ],
}));

server.setRequestHandler("prompts/get", async (request) => {
  if (request.params.name === "code_review") {
    const { language } = request.params.arguments || {};

    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `Review this ${language} code for:\n- Security vulnerabilities\n- Performance issues\n- Code quality\n- Best practices`,
          },
        },
      ],
    };
  }

  throw new Error(`Unknown prompt: ${request.params.name}`);
});
```

### Building and Running

#### 1. Build TypeScript

```bash
# package.json
{
  "name": "my-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "my-mcp-server": "./build/index.js"
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch"
  }
}
```

```bash
npm run build
```

#### 2. Add to Claude Code

```bash
# Local development
claude mcp add my-server -s user -- node /path/to/my-mcp-server/build/index.js

# Published package
claude mcp add my-server -s user -- npx -y my-published-mcp-server

# With environment variables
claude mcp add my-server -s user -e API_KEY=secret -- node /path/to/server/index.js
```

#### 3. Debug with Inspector

```bash
npm install -g @modelcontextprotocol/inspector
npx @modelcontextprotocol/inspector node /path/to/build/index.js
```

This opens a visual inspector to test tools, resources, and prompts.

### Transport Options

#### stdio (Local Development)

```typescript
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const transport = new StdioServerTransport();
await server.connect(transport);
```

**Use for**: Local file system access, databases, local services

#### HTTP/SSE (Production)

```typescript
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

const transport = new SSEServerTransport("/messages", response);
await server.connect(transport);
```

**Use for**: Production deployments, remote services, web APIs

### Token Management

**Output limits**:
- Warning threshold: 10,000 tokens
- Default maximum: 25,000 tokens
- Custom maximum: Set `MAX_MCP_OUTPUT_TOKENS` environment variable

```bash
export MAX_MCP_OUTPUT_TOKENS=50000
```

### Error Handling Best Practices

```typescript
server.setRequestHandler("tools/call", async (request) => {
  try {
    // Tool logic
    return {
      content: [{ type: "text", text: result }],
    };
  } catch (error) {
    console.error(`Tool error: ${error.message}`);

    return {
      content: [
        {
          type: "text",
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});
```

### MCP vs Slash Commands vs Hooks

| Feature | MCP Tools | Slash Commands | Hooks |
|---------|-----------|----------------|-------|
| **Complexity** | High | Low | Medium |
| **Setup** | TypeScript project | Markdown file | JSON config |
| **External APIs** | Yes | Via bash only | Via bash only |
| **Stateful** | Yes | No | No |
| **Reusable** | Across projects | Across projects | Across projects |
| **Best for** | External integrations | Prompt templates | Workflow automation |

---

## Integration Patterns

### Pattern 1: Slash Command + Hook

Create a slash command that triggers post-execution validation:

```markdown
<!-- .claude/commands/deploy.md -->
---
allowed-tools: Bash(docker:*), Bash(kubectl:*)
description: Deploy to production
---

Deploy the application to production environment.
```

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash(kubectl apply:*)",
        "hooks": [{
          "type": "command",
          "command": ".claude/hooks/post-deploy-verify.sh"
        }]
      }
    ]
  }
}
```

### Pattern 2: MCP Tool + PreToolUse Guard

Protect expensive MCP operations with confirmation:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__aws__terminate_instance",
        "hooks": [{
          "type": "prompt",
          "prompt": "Are you absolutely sure you want to terminate this instance? This cannot be undone."
        }]
      }
    ]
  }
}
```

### Pattern 3: Slash Command Calls MCP Tool

```markdown
<!-- .claude/commands/analyze-db.md -->
---
description: Analyze database performance
allowed-tools: mcp__postgres__query
---

Use the PostgreSQL MCP tool to:
1. Check slow query log
2. Analyze table sizes
3. Identify missing indexes
4. Suggest optimizations
```

### Pattern 4: Hook-Driven Slash Command

SessionStart hook that recommends slash commands:

```bash
#!/bin/bash
# .claude/hooks/session-recommend.sh

# Check if there are failing tests
if ! npm test > /dev/null 2>&1; then
    echo "Tests are failing. Consider running /fix-tests"
fi

# Check if branch is behind
if git status | grep -q "behind"; then
    echo "Branch is behind origin. Consider running /sync-branch"
fi
```

### Pattern 5: Complete Development Workflow

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/session-load-context.sh"
      }]
    }],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": ".claude/hooks/pre-edit-backup.sh"
        }]
      },
      {
        "matcher": "Bash(git push:*)",
        "hooks": [{
          "type": "command",
          "command": ".claude/hooks/pre-push-tests.sh"
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$file_path\""
          },
          {
            "type": "command",
            "command": ".claude/hooks/post-edit-lint.sh"
          }
        ]
      }
    ],
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/stop-summary.sh"
      }]
    }]
  }
}
```

---

## Best Practices Summary

### Slash Commands

1. Use clear, descriptive names
2. Provide `argument-hint` for commands with parameters
3. Leverage `!` for contextual bash execution
4. Use `@` for file references
5. Set `disable-model-invocation: true` for manual-only commands
6. Keep commands focused and single-purpose
7. Document complex commands in frontmatter

### Hooks

1. Start with one simple hook
2. Use PreToolUse for guards, PostToolUse for cleanup
3. Return exit code 2 for blocking errors
4. Use JSON output for sophisticated control
5. Keep hooks fast (60s timeout)
6. Log strategically
7. Test hooks thoroughly before production
8. Use `/hooks` menu to review and activate changes

### MCP Tools

1. Validate inputs with Zod schemas
2. Handle errors gracefully
3. Return structured error responses
4. Keep tool descriptions clear
5. Use stdio for local, HTTP for remote
6. Monitor token output limits
7. Debug with MCP inspector
8. Version your server package

### Integration

1. Combine patterns for powerful workflows
2. Use hooks to enhance slash commands
3. Guard expensive operations with PreToolUse
4. Automate formatting and quality with PostToolUse
5. Load context with SessionStart
6. Generate summaries with Stop hooks

---

## Resources

### Official Documentation

- [Claude Code Slash Commands](https://code.claude.com/docs/en/slash-commands)
- [Claude Code Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks)
- [Model Context Protocol Docs](https://docs.anthropic.com/en/docs/claude-code/mcp)

### Repositories

- [claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) - Comprehensive hook examples
- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) - Community commands and workflows
- [wshobson/commands](https://github.com/wshobson/commands) - Production-ready slash commands
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) - Official MCP SDK

### Guides & Tutorials

- [Building Custom MCP Servers (FreeCodeCamp)](https://www.freecodecamp.org/news/how-to-build-a-custom-mcp-server-with-typescript-a-handbook-for-developers/)
- [Claude Code Power User Customization](https://claude.com/blog/how-to-configure-hooks)
- [Shipyard Claude Code Cheatsheet](https://shipyard.build/blog/claude-code-cheat-sheet/)

### Tools

- [MCP Inspector](https://www.npmjs.com/package/@modelcontextprotocol/inspector) - Visual debugging for MCP servers
- [GitButler Claude Code Hooks](https://docs.gitbutler.com/features/ai-integration/claude-code-hooks) - Integration examples

---

## Appendix: Quick Reference

### Slash Command Template

```markdown
---
description: Brief description
argument-hint: [arg1] [arg2]
allowed-tools: Bash(git:*), Read
model: claude-3-5-sonnet-20241022
---

## Context

Current status: !`git status`

## Task

$ARGUMENTS

## Requirements

- Requirement 1
- Requirement 2
```

### Hook Configuration Template

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "ToolName",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/pre-tool-script.sh",
            "timeout": 60
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "ToolName",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/post-tool-script.sh"
          }
        ]
      }
    ]
  }
}
```

### MCP Server Template

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new Server(
  {
    name: "my-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "my_tool",
      description: "Tool description",
      inputSchema: {
        type: "object",
        properties: {
          param: {
            type: "string",
            description: "Parameter description",
          },
        },
        required: ["param"],
      },
    },
  ],
}));

server.setRequestHandler("tools/call", async (request) => {
  if (request.params.name === "my_tool") {
    const { param } = request.params.arguments as { param: string };

    return {
      content: [
        {
          type: "text",
          text: `Result: ${param}`,
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${request.params.name}`);
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Server running");
}

main().catch(console.error);
```

---

*Research compiled: 2025-12-16*
*Claude Code: Extending with slash commands, hooks, and custom MCP tools*
