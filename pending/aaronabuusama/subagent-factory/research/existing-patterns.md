# Existing Patterns Research - Agent and Skill Structures

**Date**: 2025-12-16
**Research Focus**: Agent definitions, skill file structures, and effective patterns in the beads project and global skills

---

## Directory Structure Overview

### Project-Local Skills (`/Users/abuusama/projects/solidity/beads/skills/`)

```
skills/
├── beads/                          # Issue tracker skill
│   ├── SKILL.md                    # Main skill definition
│   └── references/                 # Supporting documentation
│       ├── BOUNDARIES.md
│       ├── CLI_REFERENCE.md
│       ├── DEPENDENCIES.md
│       ├── ISSUE_CREATION.md
│       ├── RESUMABILITY.md
│       ├── STATIC_DATA.md
│       └── WORKFLOWS.md
└── beads-expert/                   # Agent building expertise
    ├── SKILL.md                    # Quick reference
    ├── references/                 # Deep documentation
    │   ├── agent-mail.md
    │   ├── typescript-agents.md
    │   ├── go-codebase-map.md
    │   ├── gotchas.md
    │   ├── architecture.md
    │   ├── extension-patterns.md
    │   └── cli-complete.md
    ├── workflows/                  # Step-by-step guides
    │   ├── build-ts-agent.md
    │   ├── setup-agent-mail.md
    │   └── extend-database.md
    └── templates/                  # Reusable code
        ├── agent-mail-client.ts
        ├── autonomous-agent.ts
        └── jsonl-parser.ts
```

### Agent Definitions (`.claude-plugin/agents/`)

```
.claude-plugin/agents/
└── task-agent.md                   # Autonomous task-completion agent
```

### Global User Skills (`/Users/abuusama/.claude/skills/`)

Examples of well-structured skills:
- `create-skill/` - Meta-skill for creating skills
- `research/` - Multi-agent research orchestration
- `solidity-btt-tests/` - Solidity testing scaffolder
- `example-skill/` - Template/demonstration skill
- `whitepaper-generator/` - Technical documentation generator

---

## Frontmatter Patterns

### Standard YAML Frontmatter Structure

**Simple Skill** (SKILL.md only):
```yaml
---
name: skill-name
description: Clear description of what skill does and when to use it. Should match activation triggers.
---
```

**Advanced Skill** (with additional metadata):
```yaml
---
name: beads-expert
description: |
  Expert guidance for building autonomous AI agents using beads issue tracker.
  Covers Agent Mail multi-agent coordination, TypeScript integration patterns,
  Go codebase navigation, and CLI workflows. USE WHEN user says 'build agent',
  'typescript agent', 'agent mail', 'multi-agent coordination', 'autonomous agent',
  'beads agent', or asks how to build agents that use beads for task management.
---
```

**Agent Definition** (task-agent.md):
```yaml
---
description: Autonomous agent that finds and completes ready tasks
---
```

### Key Frontmatter Patterns

1. **Name field**: kebab-case matching directory name
2. **Description field**:
   - Clear purpose statement
   - Trigger phrases with "USE WHEN" convention
   - Tools/methods mentioned
   - 1-3 sentences optimal
3. **Multi-line descriptions**: Use YAML pipe `|` for long descriptions

---

## Skill Architecture Patterns

### Pattern 1: Simple Skill (Single File)

**Structure**: SKILL.md only
**Use case**: Focused capability, minimal dependencies, quick reference

**Example**: `whitepaper-generator/SKILL.md`
- Frontmatter with name and description
- "When to Activate This Skill" section
- Quick workflow steps
- Best practices
- Template references
- Integration notes

**Key characteristics**:
- Self-contained in one file
- Clear activation triggers
- Imperative/infinitive verb forms
- References to external resources via file paths

### Pattern 2: Complex Skill (Multi-File)

**Structure**:
```
skill-name/
├── SKILL.md              # Quick reference (always loaded)
├── CLAUDE.md             # Deep dive (loaded as needed) [OPTIONAL]
├── references/           # Supporting documentation
├── workflows/            # Step-by-step guides
├── templates/            # Code/file templates
└── assets/               # Helper files
```

**Use case**: Multi-step workflows, extensive context, multiple sub-components

**Example**: `beads-expert/`
- SKILL.md = Quick reference with essential commands
- references/ = Deep documentation by topic
- workflows/ = Specific task walkthroughs
- templates/ = Reusable TypeScript code

**Key characteristics**:
- Progressive disclosure (SKILL.md → references → workflows)
- Topic-based organization in references/
- Executable workflows with clear steps
- Template code with inline documentation

### Pattern 3: Skill with Workflows

**Structure**:
```
skill-name/
├── SKILL.md
└── workflows/
    ├── task-a.md
    ├── task-b.md
    └── task-c.md
```

**Use case**: Single domain with multiple distinct operations

**Example**: `example-skill/workflows/`
- `simple-task.md` - Basic single-step workflow
- `complex-task.md` - Multi-step with dependencies
- `parallel-task.md` - Agent orchestration

**Workflow file pattern**:
```markdown
# Workflow Name

## Trigger
[User phrases that activate this]

## Purpose
[What this workflow does]

## Workflow
1. Step 1
2. Step 2
3. Step 3

## Result
[What user gets]
```

---

## Agent Definition Patterns

### Agent File Structure (`.claude-plugin/agents/`)

**Location**: `.claude-plugin/agents/task-agent.md`

**Frontmatter**:
```yaml
---
description: Autonomous agent that finds and completes ready tasks
---
```

**Content Structure**:
1. **Purpose/Identity** - What the agent is and does
2. **Agent Workflow** - Step-by-step execution flow
3. **Important Guidelines** - Operational rules
4. **Available Tools** - MCP servers, CLI commands, etc.

**Example from task-agent.md**:
```markdown
---
description: Autonomous agent that finds and completes ready tasks
---

You are a task-completion agent for beads. Your goal is to find ready work and complete it autonomously.

# Agent Workflow

1. **Find Ready Work**
   - Use the `ready` MCP tool to get unblocked tasks
   - Prefer higher priority tasks (P0 > P1 > P2 > P3 > P4)

2. **Claim the Task**
   - Use the `show` tool to get full task details
   - Use the `update` tool to set status to `in_progress`

[... etc ...]

# Available Tools

Via beads MCP server:
- `ready` - Find unblocked tasks
- `show` - Get task details
[... etc ...]
```

**Key characteristics**:
- Clear mission statement
- Numbered workflow steps
- Tool/command references
- Operational guidelines
- Self-contained instructions

---

## Effective Content Patterns

### 1. Progressive Disclosure

**SKILL.md** (Quick Reference):
- Essential commands and patterns
- When to activate
- Key concepts (brief)
- References to deeper documentation

**references/** (Deep Dive):
- Comprehensive methodology
- Advanced patterns
- Edge cases and gotchas
- Complete examples

**Pattern observed in `beads/SKILL.md`**:
```markdown
## Core Operations
[Brief examples with essential flags]

For complete CLI reference with all flags and examples, read: [references/CLI_REFERENCE.md]
```

### 2. Trigger Phrase Documentation

**Best practice from observed skills**:
- Include explicit "USE WHEN" in description
- List natural language phrases
- Cover variations and synonyms
- Make triggers discoverable

**Example from `research/SKILL.md`**:
```yaml
description: ... USE WHEN user says 'do research', 'quick research', 'extensive research', 'find information about', 'investigate', 'analyze trends', 'current events', or any research-related request.
```

### 3. Executable Instructions

**Imperative form** (verb-first):
- "Create directory structure"
- "Update SKILL.md frontmatter"
- "Test activation triggers"

**NOT declarative**:
- "The directory structure is created" ❌
- "SKILL.md frontmatter should be updated" ❌

**Example from `create-skill/SKILL.md`**:
```markdown
### Step 3: Create Directory Structure

```bash
# Simple skill
${PAI_DIR}/skills/[skill-name]/
└── SKILL.md
```

### 4. Self-Check Patterns

**Pattern**: Include decision criteria and validation questions

**Example from `beads/SKILL.md`**:
```markdown
### Test Yourself: bd or TodoWrite?

Ask these questions to decide:

**Choose bd if:**
- ❓ "Will I need this context in 2 weeks?" → Yes = bd
- ❓ "Could conversation history get compacted?" → Yes = bd
[... etc ...]
```

### 5. Template and Reference Patterns

**Pattern**: Point to concrete examples and templates

**Example from `solidity-btt-tests/SKILL.md`**:
```markdown
For comprehensive methodology, patterns, and examples:
```
read ~/.claude/skills/solidity-btt-tests/CLAUDE.md
```

For templates:
```
ls ~/.claude/skills/solidity-btt-tests/templates/
```
```

### 6. Integration Documentation

**Pattern**: Explicitly document how skill works with other skills

**Example from `whitepaper-generator/SKILL.md`**:
```markdown
## Integration with Other Skills

- **research**: For competitive analysis and background research
- **fabric**: Use `extract_wisdom` pattern for analyzing existing whitepapers
- **solidity-btt-tests**: Reference when documenting smart contract testing
```

---

## Template Patterns

### TypeScript Agent Template Structure

**Location**: `beads-expert/templates/autonomous-agent.ts`

**Key sections**:
1. **File header** - Purpose, usage, environment variables
2. **Types** - Interface definitions
3. **Client classes** - BeadsClient, AgentMailClient
4. **Base agent class** - Abstract class with common functionality
5. **Example implementation** - Concrete agent extending base
6. **Main entry point** - Initialization and execution

**Pattern highlights**:
- Abstract `executeWork()` method for customization
- Built-in Agent Mail integration
- Discovery tracking
- Error handling and cleanup
- Logging and observability

### Markdown Workflow Template

**Location**: `example-skill/workflows/simple-task.md`

**Structure**:
```markdown
# Workflow Name

## Trigger
[Activation phrases]

## Purpose
[What this accomplishes]

## Workflow
[Numbered steps]

## Example
[Concrete demonstration]

## Pattern Demonstrated
[Key learnings]

## When to Use
[Use cases]

## Template
[Reusable structure]

## Notes
[Additional context]
```

---

## Naming Conventions

### Skill Names
- **Format**: lowercase-with-hyphens
- **Descriptive**: `create-skill`, `solidity-btt-tests`, `whitepaper-generator`
- **NOT generic**: `text-processing` ❌ → `fabric-patterns` ✅
- **Action or domain focused**: `research`, `beads-expert`

### File Names
- **SKILL.md**: Always uppercase, primary skill definition
- **CLAUDE.md**: Uppercase, comprehensive context (optional)
- **references/**: Lowercase or uppercase, descriptive
  - `CLI_REFERENCE.md` (uppercase)
  - `agent-mail.md` (lowercase)
- **workflows/**: Kebab-case
  - `build-ts-agent.md`
  - `setup-agent-mail.md`
- **templates/**: Match target language conventions
  - `autonomous-agent.ts`
  - `agent-mail-client.ts`

### Directory Names
- **references/**: Supporting documentation
- **workflows/**: Step-by-step guides
- **templates/**: Reusable code/files
- **assets/**: Helper files, images, etc.

---

## Best Practices Observed

### 1. Context Inheritance
✅ Skills inherit global context automatically
✅ Reference global context, don't duplicate
✅ Keep skills self-contained but not isolated

### 2. Clear Activation
✅ Explicit trigger phrases in description
✅ "When to Activate This Skill" section
✅ Natural language routing
❌ Don't require exact phrase matching

### 3. Structured Organization
✅ One skill per domain/topic
✅ Multiple workflows within skill
✅ Progressive disclosure via file structure
❌ Don't create skills for one-off tasks

### 4. Documentation Quality
✅ Executable instructions (imperative)
✅ Concrete examples and templates
✅ Self-check questions for users
✅ Integration documentation
❌ Don't duplicate knowledge across skills

### 5. Code Templates
✅ Inline documentation in templates
✅ Clear customization points
✅ Working example implementations
✅ Environment variable documentation

---

## Anti-Patterns to Avoid

### ❌ Skill Creation Anti-Patterns
1. **Too granular**: Creating skills for single commands
2. **Too generic**: Vague names like "text-processing"
3. **Duplication**: Copying context that exists elsewhere
4. **No triggers**: Missing activation phrases
5. **Monolithic**: Everything in one file when complexity warrants structure

### ❌ Documentation Anti-Patterns
1. **Declarative**: "The file is created" vs "Create the file"
2. **Incomplete examples**: Code snippets without context
3. **Hidden structure**: References without explaining organization
4. **No integration**: Skills exist in isolation
5. **Missing self-checks**: No validation questions

### ❌ Template Anti-Patterns
1. **Over-abstraction**: Too generic to be useful
2. **Under-documentation**: No usage instructions
3. **Hard-coded values**: No configuration options
4. **No examples**: Abstract without concrete demonstration

---

## Key Learnings for Subagent Factory

### 1. Agent Definition Structure
- Use `.claude-plugin/agents/` for agent definitions
- Simple YAML frontmatter with description
- Clear workflow steps
- Tool availability documentation
- Self-contained mission statement

### 2. Template Code Organization
- Create `templates/` directory for reusable code
- Include TypeScript templates for agents
- Document environment variables
- Provide abstract base classes
- Include working example implementations

### 3. Skill vs Agent Distinction
- **Skills**: Domain knowledge, workflows, patterns (in `.claude/skills/`)
- **Agents**: Autonomous executors with specific missions (in `.claude-plugin/agents/`)
- Skills can include agent-building knowledge (like `beads-expert`)
- Agents reference skills but execute independently

### 4. Progressive Disclosure Pattern
```
SKILL.md (quick reference)
  → references/ (deep dives by topic)
    → workflows/ (step-by-step execution)
      → templates/ (reusable code)
```

### 5. Documentation Layers
1. **Frontmatter**: Name, description, triggers
2. **Quick reference**: Essential commands, when to use
3. **Deep reference**: Comprehensive methodology
4. **Workflows**: Executable step-by-step guides
5. **Templates**: Copy-paste starting points

### 6. Effective Trigger Documentation
Include in description:
- "USE WHEN user says..."
- List natural language phrases
- Cover domain-specific terminology
- Enable intent matching

### 7. Self-Service Design
- Include self-check questions
- Provide decision trees
- Reference related skills
- Document integration points
- Make skills discoverable

---

## Recommended Structure for Subagent Factory

Based on observed patterns, the subagent-factory skill should have:

```
subagent-factory/
├── SKILL.md                        # Quick reference
│   ├── Frontmatter with triggers
│   ├── When to activate
│   ├── Quick workflow
│   └── References to deeper docs
├── references/                     # Deep documentation
│   ├── agent-patterns.md           # Common agent architectures
│   ├── skill-integration.md        # How agents use skills
│   └── coordination-patterns.md    # Multi-agent coordination
├── workflows/                      # Step-by-step guides
│   ├── create-simple-agent.md
│   ├── create-complex-agent.md
│   └── create-multi-agent-system.md
└── templates/                      # Reusable code
    ├── simple-agent.md             # Agent definition template
    ├── autonomous-agent.ts         # TypeScript template
    └── skill-wrapper.md            # Skill-based agent template
```

### Activation Triggers
```yaml
description: Factory for creating and deploying autonomous subagents. Generates agent definitions, TypeScript implementations, and skill integrations. USE WHEN user says 'create agent', 'build subagent', 'spawn agent', 'agent factory', 'make autonomous agent', or needs to delegate work to specialized agents.
```

---

## References

### Files Analyzed
- `/Users/abuusama/projects/solidity/beads/.claude-plugin/agents/task-agent.md`
- `/Users/abuusama/projects/solidity/beads/skills/beads/SKILL.md`
- `/Users/abuusama/projects/solidity/beads/skills/beads-expert/SKILL.md`
- `/Users/abuusama/projects/solidity/beads/skills/beads-expert/templates/autonomous-agent.ts`
- `/Users/abuusama/.claude/skills/create-skill/SKILL.md`
- `/Users/abuusama/.claude/skills/example-skill/SKILL.md`
- `/Users/abuusama/.claude/skills/research/SKILL.md`
- `/Users/abuusama/.claude/skills/solidity-btt-tests/SKILL.md`
- `/Users/abuusama/.claude/skills/whitepaper-generator/SKILL.md`

### Pattern Sources
- Skills-as-Containers architecture (PAI v1.2.0)
- Anthropic skill standards
- Beads project conventions
- User global skill patterns
