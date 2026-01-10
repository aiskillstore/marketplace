# Research Manifest for subagent-factory Skill

## User Requirements Summary

**Skill Name:** subagent-factory
**Location:** Project `.claude/skills/` (local)
**Structure:** Complex with subdirectories (SKILL.md + references/ + workflows/)

### Purpose
Create specialized Claude Code agents on-the-fly for particular codebases or task sets.

### Target Audience
AI agents that create agent definition files with:
- Correct frontmatter
- Operating guidance
- Advanced/obscure features (slash commands, hooks)
- Effective prompt engineering

### Content Focus (All Equally Weighted)
- Frontmatter & configuration
- Prompt engineering
- Task decomposition
- Slash commands & custom tools

### Use Cases to Address
- Code analysis agents (reviewers, debuggers, refactorers)
- Research agents (documentation searchers, codebase explorers)
- Task execution agents (implementers, testers, deployers)

### Style
Both modes:
- Quick mode (direct instructions)
- Detailed interview mode (interactive)

### Anti-patterns
Minimal - focus on positive guidance

### Templates
No templates - focus on principles

---

## Research Files

| File | Topic | Size | Lines |
|------|-------|------|-------|
| `task-tool.md` | Task tool, subagent types, parameters, execution patterns | 43KB | 1635 |
| `configuration.md` | Configuration, frontmatter schema, settings | 29KB | 936 |
| `slash-commands.md` | Slash commands, hooks, MCP tools | 32KB | 1488 |
| `prompt-engineering.md` | Anthropic prompt engineering best practices | 24KB | 610 |
| `existing-patterns.md` | Patterns from existing skills in codebase | 17KB | 601 |

**Total research:** ~145KB, 5270 lines

---

## Research Agent Summaries

### Task Tool Research (task-tool.md)
The Task tool is Claude Code's most powerful delegation mechanism with **3 built-in agent types** (general-purpose/Sonnet, plan/Sonnet, explore/Haiku) and support for custom agents via Markdown configs. Key parameters: `subagent_type`, `prompt`, `model`, and `tools` (`run_in_background` proposed but not implemented). **Parallel execution** auto-manages up to 10 concurrent tasks with dynamic queuing (3-5x faster). Best practices: focused single-responsibility agents, explicit tool scoping for security, detailed prompts with checklists/examples, balance token costs (~20k per agent).

### Configuration Research (configuration.md)
Complete coverage of Claude Code configuration including SKILL.md YAML frontmatter schema (`name`, `description`, `tools`, `model`, `permissionMode`, `skills`), settings.json structure for global/project settings, agent definition files in `.claude/agents/`, and settings hierarchy (user < project < project local). Key insight: system prompt is Markdown body, NOT frontmatter.

### Slash Commands Research (slash-commands.md)
Three extensibility mechanisms: **Slash commands** (Markdown files with YAML frontmatter, arguments `$ARGUMENTS`/`$1`/`$2`, bash `!`, file refs `@`). **Hooks** (JSON config for PreToolUse/PostToolUse/SessionStart etc, exit codes 0/2, JSON output control). **MCP tools** (TypeScript SDK, Zod validation, external APIs). Pattern: combine all three for powerful workflows.

### Prompt Engineering Research (prompt-engineering.md)
Anthropic's best practices: be clear and direct, use structured sections, provide examples (multishot), use XML tags for structure, give Claude room to think, prefill responses for format control, chain prompts for complex tasks. Agent-specific: define identity/role first, provide concrete checklists, include examples, set clear boundaries, specify output format.

### Existing Patterns Research (existing-patterns.md)
Analysis of existing skills (research, whitepaper-generator, create-skill, beads-expert). Key patterns: progressive disclosure (SKILL.md navigates, references/ has depth), clear trigger phrases in descriptions, workflow directories for multi-step processes, templates for code generation. Best skill: beads-expert uses references/, workflows/, templates/ structure effectively.

---

## Skill Structure Plan

```
.claude/skills/subagent-factory/
├── SKILL.md                           # Navigation + quick reference (~150 lines)
├── references/
│   ├── agent-schema.md               # Complete frontmatter schema
│   ├── task-tool.md                  # Task tool parameters & usage
│   ├── prompt-patterns.md            # Effective prompt patterns
│   └── advanced-features.md          # Hooks, slash commands, MCP
├── workflows/
│   ├── quick-create.md               # Quick mode: direct creation
│   └── interview-create.md           # Detailed mode: interactive
└── research/                          # This research (not part of final skill)
```

---

## Final Skill Creation Prompt

The skill creation agent should:

1. **Read all research files** to understand the full context
2. **Create SKILL.md** (~150 lines) with:
   - Clear activation triggers for agent creation
   - Quick reference for agent frontmatter
   - Navigation to references/workflows
   - Both quick and interview modes
3. **Create references/** with deep documentation extracted from research
4. **Create workflows/** with step-by-step procedures
5. **Follow create-skill quality rubric** (target 80%+ score)
6. **Use progressive disclosure** - SKILL.md navigates, depth in references

Key content to include:
- Agent definition file schema (from configuration.md)
- Task tool parameters (from task-tool.md)
- Prompt engineering patterns (from prompt-engineering.md)
- Hook/slash command integration (from slash-commands.md)
- Good vs bad examples (synthesized from all)
