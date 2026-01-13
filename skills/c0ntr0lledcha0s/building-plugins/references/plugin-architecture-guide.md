# Plugin Architecture Guide

Comprehensive guide to designing well-structured Claude Code plugins.

## Table of Contents

1. [Architecture Principles](#architecture-principles)
2. [Component Composition](#component-composition)
3. [Design Patterns](#design-patterns)
4. [Scalability Considerations](#scalability-considerations)
5. [Best Practices](#best-practices)

## Architecture Principles

### 1. Single Responsibility

Each component (agent, skill, command, hook) should have one clear purpose.

**Good Example:**
```
code-review-plugin/
├── agents/
│   ├── security-reviewer.md    # Only security
│   └── style-reviewer.md       # Only code style
└── commands/
    ├── review-security.md      # Security check
    └── review-style.md         # Style check
```

**Bad Example:**
```
code-review-plugin/
├── agents/
│   └── do-everything.md        # Security, style, tests, docs
└── commands/
    └── review.md               # Does everything
```

### 2. Cohesion

Components within a plugin should work together toward a common goal.

**Good Example:** `git-workflow-plugin`
- All components support Git workflows
- Commands trigger Git operations
- Hooks enforce Git policies
- Skills provide Git expertise

**Bad Example:** `random-tools-plugin`
- Some Git commands
- Some Docker commands
- Random utility scripts
- No clear theme

### 3. Loose Coupling

Components should be independent and reusable.

**Good:**
- Commands can be used standalone
- Skills activate independently
- Agents don't depend on specific commands

**Bad:**
- Command only works if specific agent ran first
- Skill requires specific command to be called
- Hard-coded dependencies between components

### 4. Progressive Disclosure

Start simple, add complexity when needed.

**Plugin Evolution:**
```
v1.0.0: 1 command, basic functionality
v1.1.0: Add 1 skill for auto-invocation
v1.2.0: Add 1 agent for complex tasks
v2.0.0: Add hooks for automation
```

## Component Composition

### When to Use Each Component Type

#### Agents

**Use when:**
- Deep analysis required
- Complex multi-step tasks
- Needs isolated context
- Heavy computation

**Example:**
```yaml
---
name: code-security-auditor
description: Deep security analysis of codebases
---
```

#### Skills

**Use when:**
- Always-on expertise needed
- Context-aware assistance
- Background knowledge
- Auto-invocation desired

**Example:**
```yaml
---
name: reviewing-security
description: Expert at security reviews. Auto-invokes when reviewing code or analyzing security.
---
```

#### Commands

**Use when:**
- User-triggered workflow
- Parameterized input needed
- Explicit action required
- One-time operation

**Example:**
```yaml
---
description: Run security scan on specified file
argument-hint: [file-path]
---
```

#### Hooks

**Use when:**
- Event-driven automation
- Policy enforcement
- Pre/post tool validation
- Automatic checks

**Example:**
```json
{
  "type": "PreToolUse",
  "matchers": ["bash-commands"],
  "handler": {
    "type": "command",
    "command": "./hooks/scripts/validate-bash.sh"
  }
}
```

### Component Interaction Patterns

#### Pattern 1: Command → Agent

Command delegates complex work to agent:

```
User: /analyze-security myapp/
  ↓
Command: Invokes security-auditor agent
  ↓
Agent: Performs deep analysis
  ↓
Results: Returned to user
```

#### Pattern 2: Skill ↔ Command

Skill provides expertise when command runs:

```
User: /refactor mycode.ts
  ↓
Command: Starts refactoring
  ↓
Skill: Auto-invokes with refactoring expertise
  ↓
Combined: Command + Skill work together
```

#### Pattern 3: Hook → Validation

Hook validates before/after operations:

```
Claude: About to run Bash command
  ↓
Hook: PreToolUse validates command
  ↓
Safe? Yes → Execute | No → Block
```

## Design Patterns

### Pattern 1: Analyzer Pattern

**Purpose:** Analyze code/data and provide insights

**Structure:**
```
analyzer-plugin/
├── agents/
│   └── deep-analyzer.md        # Complex analysis
├── skills/
│   └── analyzing-code/         # Always-on expertise
└── commands/
    ├── analyze.md              # Quick analysis
    └── analyze-deep.md         # Triggers agent
```

**Use Cases:**
- Code quality analysis
- Security scanning
- Performance profiling
- Data analysis

### Pattern 2: Generator Pattern

**Purpose:** Generate code/files from templates

**Structure:**
```
generator-plugin/
├── skills/
│   └── generating-code/
│       ├── SKILL.md
│       └── assets/
│           ├── component.template
│           └── test.template
└── commands/
    ├── generate-component.md
    └── generate-test.md
```

**Use Cases:**
- Scaffolding new code
- Boilerplate generation
- Template-based creation

### Pattern 3: Workflow Pattern

**Purpose:** Automate multi-step processes

**Structure:**
```
workflow-plugin/
├── commands/
│   ├── step1-prepare.md
│   ├── step2-process.md
│   └── step3-finalize.md
├── hooks/
│   └── hooks.json              # Validate each step
└── scripts/
    └── workflow-helper.sh
```

**Use Cases:**
- Deployment workflows
- Release processes
- Testing pipelines

### Pattern 4: Integration Pattern

**Purpose:** Connect to external tools/services

**Structure:**
```
integration-plugin/
├── .mcp.json                   # External service config
├── commands/
│   ├── sync.md
│   └── query.md
└── agents/
    └── data-processor.md       # Process external data
```

**Use Cases:**
- API integrations
- Database connections
- Third-party services

## Scalability Considerations

### Small Plugin (1-3 Components)

**Structure:**
```
simple-plugin/
├── .claude-plugin/plugin.json
├── commands/
│   └── main-command.md
└── README.md
```

**Characteristics:**
- Single purpose
- Minimal complexity
- Easy to maintain

### Medium Plugin (4-10 Components)

**Structure:**
```
medium-plugin/
├── .claude-plugin/plugin.json
├── agents/
│   └── specialist.md
├── skills/
│   └── expertise/
├── commands/
│   ├── cmd1.md
│   └── cmd2.md
└── README.md
```

**Characteristics:**
- Moderate features
- Organized structure
- Clear component roles

### Large Plugin (10+ Components)

**Structure:**
```
large-plugin/
├── .claude-plugin/plugin.json
├── agents/
│   ├── analyzer.md
│   ├── generator.md
│   └── validator.md
├── skills/
│   ├── skill1/
│   ├── skill2/
│   └── skill3/
├── commands/
│   ├── category1/
│   │   ├── cmd1.md
│   │   └── cmd2.md
│   └── category2/
│       └── cmd3.md
├── hooks/
│   ├── hooks.json
│   └── scripts/
├── scripts/
│   └── utilities/
└── README.md
```

**Characteristics:**
- Namespace commands by category
- Group related components
- Comprehensive documentation
- Helper scripts organized

### Organizing Large Plugins

#### Namespaced Commands

Use directory structure for namespacing:

```
commands/
├── git/
│   ├── commit.md      → /plugin:git:commit
│   ├── push.md        → /plugin:git:push
│   └── rebase.md      → /plugin:git:rebase
└── github/
    ├── pr.md          → /plugin:github:pr
    └── issue.md       → /plugin:github:issue
```

#### Modular Skills

Separate skills by domain:

```
skills/
├── analyzing-git/
├── reviewing-code/
└── managing-issues/
```

#### Specialized Agents

One agent per major capability:

```
agents/
├── git-expert.md
├── code-reviewer.md
└── issue-manager.md
```

## Best Practices

### 1. Clear Naming

**Components:**
- Use descriptive names
- Follow conventions (gerunds for skills, verbs for commands)
- Be consistent across plugin

**Examples:**
```
# Good
analyzing-security    # Skill (gerund)
security-auditor      # Agent (noun)
scan-security         # Command (verb)

# Bad
security              # Too vague
doSecurity            # Wrong case
sec_scan              # Underscores
```

### 2. Comprehensive Documentation

**README.md Must Include:**
- Clear description of purpose
- Installation instructions
- Component list with descriptions
- Usage examples
- Configuration (if needed)
- Troubleshooting

**Component Documentation:**
- Each component describes its purpose
- Clear examples
- Parameter documentation
- Error handling

### 3. Version Management

**Semantic Versioning:**
```
1.0.0 → Initial release
1.1.0 → Added new command (minor)
1.1.1 → Fixed bug (patch)
2.0.0 → Removed deprecated agent (major)
```

**Update Both Files:**
- `plugin.json` version
- `marketplace.json` version (if in marketplace)

### 4. Security First

**Input Validation:**
```yaml
# In command
---
description: Process file
allowed-tools: Read, Bash
---

# Validate input
If $1 is empty or contains "..", reject it
```

**Tool Permissions:**
```yaml
# Minimal for read-only
allowed-tools: Read, Grep, Glob

# Only add Write/Bash when necessary
allowed-tools: Read, Write, Edit, Grep, Glob
```

**Secret Management:**
```json
// Use environment variables
{
  "mcpServers": {
    "api": {
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

### 5. Testing Strategy

**Test Each Component:**
- Agents: Manual invocation, edge cases
- Skills: Auto-invocation triggers
- Commands: All argument combinations
- Hooks: Event triggering

**Integration Tests:**
- Components working together
- End-to-end workflows
- Error scenarios

**Validation:**
```bash
# Always validate before releasing
python3 validate-plugin.py ./my-plugin/
```

### 6. Maintainability

**Code Organization:**
- Group related files
- Use consistent structure
- Clear file names

**Helper Scripts:**
- Place in `scripts/` directory
- Make executable
- Document usage

**Dependencies:**
- Document all requirements
- Pin versions
- Minimize external deps

## Anti-Patterns

### ❌ The Monolith

**Problem:** One massive component does everything

**Solution:** Break into focused components

### ❌ The Scattered Plugin

**Problem:** Unrelated components bundled together

**Solution:** Create separate plugins for different domains

### ❌ The Over-Abstracted

**Problem:** Too many layers, hard to understand

**Solution:** Simplify, reduce indirection

### ❌ The Undocumented

**Problem:** No README, unclear usage

**Solution:** Write comprehensive docs

### ❌ The Insecure

**Problem:** No input validation, dangerous operations

**Solution:** Validate inputs, restrict permissions

## Summary

Good plugin architecture:
- ✅ Clear single purpose
- ✅ Cohesive components
- ✅ Well-documented
- ✅ Secure by default
- ✅ Scalable structure
- ✅ Easy to maintain

Start simple, add features progressively, and always prioritize clarity and security.
