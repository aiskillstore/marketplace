# Claude Code Configuration Research

Comprehensive research on Claude Code configuration options, settings, YAML frontmatter schemas, and agent definitions.

---

## Table of Contents

1. [CLAUDE.md Files](#claudemd-files)
2. [Agent Configuration with YAML Frontmatter](#agent-configuration-with-yaml-frontmatter)
3. [Skills Configuration with YAML Frontmatter](#skills-configuration-with-yaml-frontmatter)
4. [Settings.json Configuration](#settingsjson-configuration)
5. [.claude Directory Structure](#claude-directory-structure)
6. [Model Selection](#model-selection)
7. [Tool Permissions](#tool-permissions)
8. [Configuration Hierarchy and Precedence](#configuration-hierarchy-and-precedence)
9. [Practical Examples](#practical-examples)

---

## CLAUDE.md Files

### Purpose
CLAUDE.md files serve as persistent memory and rule books for Claude Code projects. They are automatically loaded into Claude's context at the start of every conversation, functioning as system prompts that eliminate the need to repeatedly explain basic project information.

### File Locations and Hierarchy

Claude Code supports hierarchical CLAUDE.md files with specific precedence rules:

| Location | Scope | Precedence |
|----------|-------|------------|
| `~/.claude/CLAUDE.md` | Global (all projects) | Lowest |
| `/path/to/project/CLAUDE.md` | Project-level | High |
| `/path/to/project/subdir/CLAUDE.md` | Directory-specific | Highest (most nested wins) |

**Key behavior:** Claude Code looks at all CLAUDE.md files in the hierarchy and prioritizes the most specific (most nested) when relevant.

### What to Include

CLAUDE.md files should document:

- **Common bash commands** - Project-specific scripts and utilities
- **Code style guidelines** - Formatting, naming conventions, patterns
- **Testing instructions** - How to run tests, test structure
- **Repository conventions** - Branch naming, merge vs. rebase policies
- **Developer environment setup** - Version managers (pyenv, nvm), compiler requirements
- **Project-specific warnings** - Known issues, unexpected behaviors
- **Core utilities** - Key tools and how to use them
- **Architecture overview** - High-level system design
- **Build instructions** - How to compile, bundle, deploy

### Format and Best Practices

**No Required Format:** CLAUDE.md uses plain Markdown with no required structure. However, best practices recommend:

- **Keep it concise** - Treat it as quick-reference documentation
- **Human-readable** - Both humans and Claude need to understand it quickly
- **Problem-driven** - Each addition should solve a real problem encountered, not theoretical concerns
- **Avoid sensitive data** - No API keys, credentials, database strings, or security vulnerabilities (especially if committed to version control)
- **Use clear sections** - Organize with Markdown headers for easy navigation

### Creating and Editing

```bash
# Initialize a basic CLAUDE.md
claude /init

# Edit memory files directly
claude /memory
```

### Example CLAUDE.md Structure

```markdown
# Project Name

## Overview
Brief description of what this project does.

## Key Commands
- `./scripts/test.sh` - Run tests (respects .test-skip)
- `make build` - Build the project
- `make deploy` - Deploy to staging

## Architecture
- `cmd/` - CLI commands
- `internal/` - Core packages
- `pkg/` - Public libraries

## Development Workflow
1. Create feature branch from main
2. Run tests with `./scripts/test.sh`
3. Submit PR for review

## Known Issues
- Test suite has long compilation time (~180s)
- Some tests in .test-skip due to GitHub issues #355, #356
```

---

## Agent Configuration with YAML Frontmatter

### What are Agents?

Agents (also called sub-agents) are specialized Claude instances defined as Markdown files with YAML frontmatter. They enable delegation of specific tasks to focused, context-specific Claude sessions.

### Storage Locations

| Location | Scope | Precedence |
|----------|-------|-----------|
| `~/.claude/agents/` | User-level (all projects) | Lower |
| `.claude/agents/` | Project-level | Higher (overrides user-level) |

**Conflict Resolution:** When agent names conflict, project-level agents take precedence over user-level agents.

### YAML Frontmatter Schema

```yaml
---
name: agent-name                    # REQUIRED: Agent identifier (kebab-case)
description: Description text       # REQUIRED: What this agent does and when to use it
tools: tool1, tool2, tool3         # OPTIONAL: Comma-separated tool list
model: sonnet                       # OPTIONAL: Model alias or 'inherit'
permissionMode: default             # OPTIONAL: Permission mode
skills: skill1, skill2              # OPTIONAL: Skills to auto-load
---
```

### Field Specifications

#### name (REQUIRED)
- **Format:** kebab-case (lowercase with hyphens)
- **Examples:** `test-runner`, `code-reviewer`, `deployment-agent`
- **Validation:** Must be unique within scope

#### description (REQUIRED)
- **Purpose:** Tells Claude when to invoke this agent
- **Best Practice:** Include trigger phrases and use cases
- **Example:** "Run test suite, diagnose failures, and fix them while preserving test intent. Use PROACTIVELY after code changes."

#### tools (OPTIONAL)
- **Format:** Comma-separated list
- **Default:** Inherits all tools from main thread (including MCP tools)
- **Common Tools:** Read, Edit, Write, Grep, Glob, Bash, WebSearch, WebFetch
- **Example:** `tools: Read, Edit, Bash, Grep`

**Tool Inheritance Behavior:**
- If `tools` field is **omitted**: Agent inherits ALL tools from main thread
- If `tools` field is **specified**: Agent only has access to listed tools

#### model (OPTIONAL)
- **Options:**
  - `sonnet` - Claude Sonnet (balanced performance)
  - `opus` - Claude Opus (highest capability)
  - `haiku` - Claude Haiku (fastest, most efficient)
  - `opusplan` - Hybrid: Opus for planning, Sonnet for execution
  - `inherit` - Use same model as main conversation
- **Default:** Uses default subagent model (typically `sonnet`)

#### permissionMode (OPTIONAL)
- **Purpose:** Controls tool permission behavior
- **Values:** `default`, `allowAll`, `denyAll`, etc.
- **Default:** Inherits from main session

#### skills (OPTIONAL)
- **Format:** Comma-separated skill names
- **Purpose:** Auto-load specific skills when agent is invoked
- **Example:** `skills: testing, debugging`

### Complete Agent Example

```markdown
# .claude/agents/test-runner.md
---
name: test-runner
description: Run test suite, diagnose failures, and fix them while preserving test intent. Use PROACTIVELY after code changes.
tools: Read, Edit, Write, Grep, Glob, Bash
model: sonnet
---

# Test Runner Agent

## Responsibilities
1. Execute test suite using project-specific test commands
2. Diagnose test failures with detailed analysis
3. Propose minimal fixes with evidence (stack traces, diffs)
4. Preserve original test intent while fixing issues

## Workflow
1. Run tests: `./scripts/test.sh` or equivalent
2. For failures:
   - Reproduce the failure
   - Isolate root cause
   - Propose minimal fix
   - Provide evidence (stack traces, diffs)
3. Re-run tests to verify fix

## Output Format
Always provide:
- Test command used
- Test results summary
- Failure analysis (if applicable)
- Proposed fix with rationale
```

### Validation Requirements

To be valid, an agent file must:

1. **Be located in** `.claude/agents/` directory (absolute requirement)
2. **Use kebab-case naming** (e.g., `my-specialist-agent.md`)
3. **Have valid YAML frontmatter** with required fields
4. **Conform to Claude Code agent specification**

---

## Skills Configuration with YAML Frontmatter

### What are Skills?

Skills are reusable capability modules that extend Claude's knowledge with specialized domain expertise, workflows, or tool integrations. They differ from agents in that they enhance the current conversation rather than spawning a new one.

### Storage Locations

| Location | Scope |
|----------|-------|
| `~/.claude/skills/` | User-level (all projects) |
| `.claude/skills/` | Project-level |

### Directory Structure

```
skill-name/
├── SKILL.md           # REQUIRED: Skill definition
├── CLAUDE.md          # OPTIONAL: Extended context
├── reference.md       # OPTIONAL: Reference documentation
├── examples.md        # OPTIONAL: Usage examples
├── workflows/         # OPTIONAL: Workflow documents
│   └── workflow.md
├── scripts/           # OPTIONAL: Helper scripts
│   └── helper.py
└── templates/         # OPTIONAL: Templates
    └── template.txt
```

### SKILL.md YAML Frontmatter Schema

```yaml
---
name: skill-name                    # REQUIRED: Skill identifier (kebab-case)
description: Description text       # REQUIRED: What skill does and when to use it
version: 1.0.0                      # OPTIONAL: Version tracking
allowed-tools: "Bash, Read"         # OPTIONAL: Tool restrictions (community use, not officially documented)
dependencies: package1, package2    # OPTIONAL: Required software (community use, not officially documented)
---
```

### Field Specifications

#### name (REQUIRED)
- **Format:** kebab-case (lowercase with hyphens)
- **Max Length:** 64 characters
- **Character Set:** Lowercase letters, numbers, hyphens only
- **Examples:** `prompting`, `create-skill`, `opentui-components`

#### description (REQUIRED)
- **Max Length:** 1024 characters
- **Purpose:** Enables Claude to discover when to use this skill
- **Best Practice:** Include both what the skill does AND when Claude should use it
- **Good Example:** "Multi-source comprehensive research using perplexity-researcher, claude-researcher, and gemini-researcher agents. USE WHEN user says 'do research', 'find information about', 'investigate', or 'analyze trends'."

#### version (OPTIONAL)
- **Purpose:** Track skill iterations and updates
- **Format:** Semantic versioning (e.g., `1.0.0`, `2.1.3`)
- **Use Case:** Useful for skill maintenance and evolution tracking

#### allowed-tools (OPTIONAL)
- **Status:** Community usage, not officially documented by Anthropic
- **Format:** Comma-separated string
- **Example:** `"Bash, Read, Write, Grep"`
- **Note:** May not be part of official schema

#### dependencies (OPTIONAL)
- **Status:** Community usage, not officially documented by Anthropic
- **Purpose:** Document required software packages
- **Example:** `"node >= 18, pnpm, docker"`

### Official vs. Community Fields

**Officially Documented (Anthropic 2025):**
- `name` (required)
- `description` (required)

**Community Usage (not officially documented):**
- `version`
- `allowed-tools`
- `dependencies`

### SKILL.md Structure Template

```markdown
---
name: my-skill-name
description: Brief overview of what this skill does and when to use it
version: 1.0.0
---

# Skill Name

## When to Activate This Skill
- Trigger condition 1
- User phrase examples
- Specific use cases

## Core Capability
[Main content describing what the skill does]

## Key Components
- Component 1
- Component 2

## Examples
[Concrete usage examples]

## Supplementary Resources
For detailed context: `read ${PAI_DIR}/skills/[skill-name]/CLAUDE.md`
```

### Skill Discovery Mechanism

At startup:
1. Claude loads **name** and **description** from all SKILL.md frontmatter into system prompt
2. Files are read **on-demand** - Claude uses Bash/Read tools to access SKILL.md content when needed
3. This enables lightweight skill discovery without loading full content upfront

### Best Practices

1. **Keep SKILL.md concise** - Under 5,000 words to avoid context window overload
2. **Description is critical** - This is how Claude discovers when to use your skill
3. **Progressive disclosure** - SKILL.md = quick reference, CLAUDE.md = deep dive
4. **Clear activation triggers** - User should understand when skill applies
5. **Self-contained** - Skill should work independently

---

## Settings.json Configuration

### File Locations and Hierarchy

Claude Code uses a hierarchical settings system with three levels:

| Location | Scope | Precedence | Version Control |
|----------|-------|------------|-----------------|
| `~/.claude/settings.json` | User (all projects) | Lowest | No |
| `.claude/settings.json` | Project (shared) | Middle | Yes (shared with team) |
| `.claude/settings.local.json` | Project (personal) | Highest | No (personal preferences) |

**Merging Behavior:** Settings arrays are merged rather than replaced, allowing project-level configuration to extend user-level configuration.

### Configuration Precedence Order

Claude Code loads configuration from multiple sources in this order (highest precedence first):

1. **CLI flags** - `--allowedTools`, `--disallowedTools`, `--model`, etc.
2. **Environment variables** - `ANTHROPIC_MODEL`, etc.
3. **Project local settings** - `.claude/settings.local.json`
4. **Project settings** - `.claude/settings.json`
5. **User settings** - `~/.claude/settings.json`

### Common Settings Fields

While the complete schema isn't fully documented in search results, common settings include:

```json
{
  "model": "sonnet",
  "allowedTools": ["Read", "Write", "Bash", "Grep", "Glob"],
  "disallowedTools": [],
  "permissionMode": "default",
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["/path/to/server.js"]
    }
  }
}
```

### Permission Modes

Permission modes provide global control over tool usage:

- **default** - Prompt for permission on potentially dangerous operations
- **allowAll** - Allow all operations without prompting (YOLO mode)
- **denyAll** - Deny all tool usage
- **custom** - Use fine-grained permission rules

---

## .claude Directory Structure

### Complete Directory Layout

```
.claude/
├── settings.json              # Project settings (committed)
├── settings.local.json        # Personal settings (not committed)
├── CLAUDE.md                  # Project context (deprecated location)
├── agents/                    # Agent definitions
│   ├── agent-name.md
│   └── another-agent.md
├── skills/                    # Skill modules
│   ├── skill-name/
│   │   ├── SKILL.md
│   │   ├── CLAUDE.md
│   │   └── reference.md
│   └── another-skill/
│       └── SKILL.md
├── commands/                  # Custom slash commands
│   ├── debug.md
│   └── analyze.md
└── test-strategy.md          # Optional project documentation
```

### Directory Purposes

#### agents/
Contains agent definition files (Markdown with YAML frontmatter). Each agent represents a specialized Claude instance for specific tasks.

#### skills/
Contains skill modules. Each skill is a directory with at minimum a SKILL.md file defining a reusable capability.

#### commands/
Contains custom slash command templates. These become available through the slash commands menu when you type `/`.

**Usage:** Store prompt templates for repeated workflows (debugging loops, log analysis, etc.)

**Benefit:** Commands can be checked into git to share with team

**Example:**
```markdown
# .claude/commands/debug.md
---
name: debug
description: Debug a failing test
---

Run the test suite and analyze any failures:
1. Execute `./scripts/test.sh`
2. For each failure, show the stack trace
3. Identify the root cause
4. Suggest a fix
```

### .gitignore Recommendations

```gitignore
# Personal settings - don't commit
.claude/settings.local.json

# Temporary files
.claude/tmp/
.claude/cache/
```

**Commit to version control:**
- `.claude/settings.json` - Shared project settings
- `.claude/agents/` - Team agents
- `.claude/skills/` - Team skills
- `.claude/commands/` - Shared commands

**Don't commit:**
- `.claude/settings.local.json` - Personal preferences
- Any temporary or cache files

---

## Model Selection

### Model Aliases

Claude Code provides convenient aliases for model selection:

| Alias | Model | Use Case |
|-------|-------|----------|
| `sonnet` | Claude Sonnet | Balanced performance and speed |
| `opus` | Claude Opus | Maximum capability, complex reasoning |
| `haiku` | Claude Haiku | Fastest, most efficient |
| `opusplan` | Hybrid | Opus for planning, Sonnet for execution |

### Model Configuration Methods

Listed in order of priority (highest first):

1. **During session** - `/model <alias|name>` command
2. **At startup** - `claude --model <alias|name>` CLI flag
3. **Environment variable** - `ANTHROPIC_MODEL=<alias|name>`
4. **Settings file** - `model` field in settings.json

### Switching Models Mid-Session

```bash
# Interactive menu
/model

# Direct selection
/model opus
/model sonnet
/model haiku
```

**Benefit:** Works immediately without restarting terminal

### opusplan Hybrid Model

The `opusplan` alias provides automated hybrid behavior:
- **Plan mode:** Uses Opus for complex reasoning and architecture decisions
- **Execution mode:** Automatically switches to Sonnet for code generation and implementation

**Use Case:** Optimal for complex projects requiring strategic planning and efficient implementation

---

## Tool Permissions

### Default Permission Behavior

By default, Claude Code requires permission for actions that could modify your system:
- Writing files
- Executing bash commands
- Using MCP tools
- Web operations

When attempting these actions, Claude pauses and prompts for approval.

### Tool Categories

Claude Code recognizes four main tool types:

1. **Bash Commands** - Shell command execution
2. **Read and Edit** - File system operations
3. **Web Fetch** - Network requests
4. **MCP Tools** - Model Context Protocol integrations

### Configuring Permissions

#### /permissions Command

```bash
# Interactive permission management
/permissions

# Add tools to allowlist
/permissions allow Bash Write

# Remove tools from allowlist
/permissions deny WebFetch
```

#### CLI Flags

```bash
# Allow specific tools for session
claude --allowedTools Read,Write,Bash

# Deny specific tools for session
claude --disallowedTools WebFetch,WebSearch

# YOLO mode - skip all permission checks (use with caution!)
claude --dangerously-skip-permissions
```

#### Settings Files

```json
{
  "allowedTools": ["Read", "Write", "Grep", "Glob", "Bash"],
  "disallowedTools": ["WebFetch"],
  "permissionMode": "default"
}
```

### Permission Modes

- **default** - Ask for permission on potentially dangerous operations
- **allowAll** - Bypass all permission checks (YOLO mode)
- **denyAll** - Deny all tool usage
- **custom** - Fine-grained permission rules

### YOLO Mode (--dangerously-skip-permissions)

**What it does:** Bypasses all permission checks, allowing Claude Code to execute all operations without prompts

**When to use:**
- Trusted local development environments
- Controlled environments like CI/CD pipelines
- When you fully trust the operations being performed

**Warning:** Use with extreme caution. This mode can make irreversible changes to your system.

### SDK Permission Handling (canUseTool callback)

For programmatic control, the SDK provides a `canUseTool` callback:

```typescript
const decision = await canUseTool(toolName, inputParameters);
// Returns: allow or deny
```

**Fires when:**
- Hooks and permission rules don't cover the operation
- Not in acceptEdits mode
- Would normally show a permission prompt to user

---

## Configuration Hierarchy and Precedence

### Loading Order (Highest to Lowest Precedence)

1. **CLI Flags**
   - `--model`
   - `--allowedTools`
   - `--disallowedTools`
   - `--dangerously-skip-permissions`

2. **Environment Variables**
   - `ANTHROPIC_MODEL`
   - Other env vars

3. **Project Local Settings**
   - `.claude/settings.local.json`
   - Not committed to version control
   - Personal preferences

4. **Project Settings**
   - `.claude/settings.json`
   - Committed to version control
   - Shared with team

5. **User Settings**
   - `~/.claude/settings.json`
   - Global user preferences

6. **System Defaults**
   - Built-in Claude Code defaults

### CLAUDE.md Hierarchy

For CLAUDE.md files specifically:

1. **Most Nested Directory** - `/project/subdir/nested/CLAUDE.md`
2. **Parent Directories** - `/project/subdir/CLAUDE.md`
3. **Project Root** - `/project/CLAUDE.md`
4. **Global User** - `~/.claude/CLAUDE.md`

**Key Behavior:** All CLAUDE.md files in the hierarchy are read, but the most specific (most nested) takes precedence when there are conflicts.

### Settings Merging Behavior

**Arrays:** Merged (extended) rather than replaced
```json
// User settings
{ "allowedTools": ["Read", "Write"] }

// Project settings
{ "allowedTools": ["Bash", "Grep"] }

// Effective settings
{ "allowedTools": ["Read", "Write", "Bash", "Grep"] }
```

**Scalar values:** Replaced (higher precedence wins)
```json
// User settings
{ "model": "sonnet" }

// Project settings
{ "model": "opus" }

// Effective settings
{ "model": "opus" }
```

---

## Practical Examples

### Example 1: Project-Specific Test Runner Agent

```markdown
# .claude/agents/test-runner.md
---
name: test-runner
description: Execute project test suite, diagnose failures, and propose fixes. Use after code changes.
tools: Read, Edit, Write, Bash, Grep, Glob
model: sonnet
---

# Test Runner Agent

## Workflow
1. Run project test script: `./scripts/test.sh`
2. For failures:
   - Read test files with `Read` tool
   - Identify root cause
   - Propose minimal fix
   - Verify fix with re-run

## Test Script Details
- Uses `.test-skip` to skip known broken tests
- 3-minute timeout for large test suites
- Compilation takes ~180s, execution ~4s

## Output Format
Provide:
- Test command used
- Pass/fail summary
- Stack traces for failures
- Proposed fix with rationale
```

### Example 2: Research Skill with Multiple Agents

```markdown
# .claude/skills/research/SKILL.md
---
name: research
description: Multi-source comprehensive research using perplexity-researcher, claude-researcher, and gemini-researcher agents. USE WHEN user says 'do research', 'investigate', 'find information about', or 'analyze trends'.
version: 2.0.0
---

# Research Skill

## When to Activate
- User says: "do research on X"
- User says: "investigate topic Y"
- User says: "find information about Z"
- User needs current events or recent information

## Research Modes

### Quick Research (3 agents)
Fast research for straightforward queries.

### Standard Research (9 agents)
Balanced depth and speed for most queries.

### Extensive Research (24 agents)
Deep research with creative analysis for complex topics.

## Workflow
1. Determine research mode based on query complexity
2. Spawn parallel research agents
3. Aggregate findings
4. Synthesize coherent report

## Output Format
- Executive summary
- Key findings (bulleted)
- Detailed analysis per topic
- Sources with URLs
```

### Example 3: Project Settings Configuration

```json
// .claude/settings.json (committed)
{
  "model": "sonnet",
  "allowedTools": [
    "Read",
    "Write",
    "Edit",
    "Grep",
    "Glob",
    "Bash"
  ],
  "mcpServers": {
    "docker": {
      "command": "docker-mcp-server",
      "args": []
    }
  }
}
```

```json
// .claude/settings.local.json (not committed)
{
  "model": "opus",
  "allowedTools": [
    "WebSearch",
    "WebFetch"
  ]
}
```

**Effective configuration:**
- Model: `opus` (from settings.local.json)
- Allowed Tools: `Read, Write, Edit, Grep, Glob, Bash, WebSearch, WebFetch` (merged)
- MCP Servers: docker (from settings.json)

### Example 4: Custom Slash Command

```markdown
# .claude/commands/analyze-logs.md
---
name: analyze-logs
description: Analyze application logs for errors and patterns
---

# Log Analysis Command

Analyze recent application logs:

1. Read last 1000 lines from `/var/log/app.log`
2. Identify error patterns using regex
3. Group errors by type
4. Provide frequency count for each error type
5. Suggest potential root causes
6. Recommend fixes for top 3 most frequent errors

Output in table format with columns:
- Error Type
- Count
- First Seen
- Last Seen
- Suggested Fix
```

Usage: Type `/analyze-logs` in Claude Code to run this command.

### Example 5: CLAUDE.md with Project Context

```markdown
# Beads - Distributed Issue Tracker

## Overview
Beads is a Git-based issue tracker designed for AI agent workflows with human oversight.

## Critical Instructions

### Testing Strategy
ALWAYS use `./scripts/test.sh` instead of `go test` directly:
- Automatically skips broken tests from `.test-skip`
- Uses appropriate timeout (3m default)
- Consistent with CI/CD pipeline

### Known Issues
- Test compilation takes ~180s (cmd/bd package has 41,696 LOC)
- Some tests skipped: see GitHub issues #355, #356

## Key Commands
- `bd ready` - Show available work
- `bd show <id>` - Issue details
- `bd create --title="..." --type=task` - Create issue
- `bd close <id>` - Mark complete
- `bd sync` - Sync with remote

## Architecture
- `cmd/bd/` - CLI commands (Go)
- `internal/` - Core packages
- `integrations/` - MCP server, plugins

## Agent Workflow
You are the Refinery agent for this rig. Coordinate roughnecks:
1. Check inbox: `town inbox`
2. Review work: `bd ready`
3. Assign tasks to roughnecks via `town spawn`
4. Monitor progress
5. Report to Mayor

## Build/Test
```bash
./scripts/test.sh          # Run full test suite
./scripts/test.sh -v       # Verbose output
make build                 # Build binary
```
```

---

## Resources and References

### Official Documentation

- [Using CLAUDE.MD files: Customizing Claude Code for your codebase](https://claude.com/blog/using-claude-md-files)
- [Claude Code settings - Claude Docs](https://docs.claude.com/en/docs/claude-code/settings)
- [Model configuration - Claude Code Docs](https://code.claude.com/docs/en/model-config)
- [Subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
- [Agent Skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [Skill authoring best practices - Claude Docs](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Handling Permissions - Claude Docs](https://code.claude.com/docs/en/sdk/sdk-permissions)

### Community Resources

- [Claude Code Configuration Guide | ClaudeLog](https://claudelog.com/configuration/)
- [Cooking with Claude Code: The Complete Guide - Sid Bharath](https://www.siddharthbharath.com/claude-code-the-complete-guide/)
- [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Step-by-Step Guide: Prepare Your Codebase for Claude Code | Medium](https://medium.com/@dan.avila7/step-by-step-guide-prepare-your-codebase-for-claude-code-3e14262566e9)
- [Claude Code: Part 2 - CLAUDE.md Configuration Files | Luiz Tanure](https://www.letanure.dev/blog/2025-07-31--claude-code-part-2-claude-md-configuration)
- [Shipyard | Claude Code CLI Cheatsheet](https://shipyard.build/blog/claude-code-cheat-sheet/)
- [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [Inside Claude Code Skills: Structure, prompts, invocation | Mikhail Shilkov](https://mikhail.io/2025/10/claude-code-skills/)
- [GitHub - anthropics/skills: Public repository for Skills](https://github.com/anthropics/skills)
- [How to create custom Skills | Claude Help Center](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Building Skills for Claude Code | Claude](https://claude.com/blog/building-skills-for-claude-code)
- [Permission Model in Claude Code](https://skywork.ai/blog/permission-model-claude-code-vs-code-jetbrains-cli/)
- [Claude Code Permissions | Steve Kinney](https://stevekinney.com/courses/ai-development/claude-code-permissions)

### Anthropic Engineering Articles

- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

---

## Key Takeaways

1. **CLAUDE.md files** are automatically loaded context that act as persistent project memory
2. **Agents** (.claude/agents/) are specialized Claude instances with YAML frontmatter configuration
3. **Skills** (.claude/skills/) are reusable capability modules with progressive disclosure
4. **Settings hierarchy** goes: CLI flags > env vars > local settings > project settings > user settings
5. **Frontmatter fields** for agents and skills have REQUIRED (name, description) and OPTIONAL (tools, model, etc.) properties
6. **Model selection** can be controlled via /model command, CLI flags, env vars, or settings files
7. **Tool permissions** default to conservative (ask before dangerous operations) but can be configured at multiple levels
8. **Configuration merging** extends arrays but replaces scalar values based on precedence

---

**Last Updated:** 2025-12-16
**Research Scope:** Claude Code configuration, agents, skills, settings, and YAML schemas
