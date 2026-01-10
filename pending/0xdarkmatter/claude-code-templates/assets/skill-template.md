---
name: skill-name
description: "Brief description of what this skill does. Triggers on: keyword1, keyword2, keyword3."
compatibility: "Requirements (e.g., Python 3.10+, Node.js, specific CLI tools)"
allowed-tools: "Bash Read Write"
depends-on: []
related-skills: []
---

# Skill Name

One-line description of what this skill enables.

## Quick Reference

| Task | Command |
|------|---------|
| [Task 1] | `command1 args` |
| [Task 2] | `command2 args` |
| [Task 3] | `command3 args` |

## Basic Usage

```bash
# Example 1: [Description]
command example

# Example 2: [Description]
command example
```

## Common Patterns

### Pattern 1: [Name]

```bash
# Description of when to use this
command with options
```

### Pattern 2: [Name]

```bash
# Description of when to use this
command with options
```

## When to Use

- [Scenario 1: e.g., Processing large JSON files]
- [Scenario 2: e.g., Batch transformations]
- [Scenario 3: e.g., Data extraction]

## Troubleshooting

| Issue | Solution |
|-------|----------|
| [Problem 1] | [Solution 1] |
| [Problem 2] | [Solution 2] |

## Additional Resources

- `./references/advanced-patterns.md` - Detailed patterns
- `./references/configuration.md` - Configuration options

---

**See Also:** [related-skill-1], [related-skill-2]

<!--
AGENTSKILLS.IO SPECIFICATION
=============================
This template follows the open standard at https://agentskills.io/specification

REQUIRED FIELDS:
- name: 1-64 chars, lowercase alphanumeric + hyphens, must match directory name
- description: 1-1024 chars, include trigger keywords for discovery

OPTIONAL FIELDS (per spec):
- license: License applied to the skill
- compatibility: Max 500 chars, environment requirements
- metadata: Key-value mapping for additional properties
- allowed-tools: Space-delimited pre-approved tools (experimental)

EXTENSIONS (via metadata convention):
- depends-on: Prerequisite skills that should be loaded first
- related-skills: Complementary skills for cross-reference

DIRECTORY STRUCTURE:
skills/your-skill/
├── SKILL.md           # Required, <500 lines per spec
├── references/        # On-demand detailed docs
│   └── advanced.md
├── scripts/           # Executable helpers
│   └── helper.sh
└── assets/            # Static resources
    └── template.txt

GUIDELINES:
- SKILL.md under 500 lines (guideline, can exceed if needed)
- Instructions under 5000 tokens for efficient loading
- Use relative paths one level deep from SKILL.md
- Name must match parent directory exactly

USAGE:
1. Create directory: mkdir -p ~/.claude/skills/your-skill
2. Copy this file to ~/.claude/skills/your-skill/SKILL.md
3. Replace all [placeholders] with your content
4. Ensure directory name matches the `name` field
5. Test by mentioning trigger keywords in a conversation

TIPS:
- Description MUST include trigger keywords for agent discovery
- Keep SKILL.md lean - use references/ for detailed patterns
- Use tables for quick scanning
- Include troubleshooting for common issues

PROMPT CACHING OPTIMIZATION:
Claude Code benefits from prompt caching (90% token cost reduction on cache hits).
See: https://platform.claude.com/docs/en/build-with-claude/prompt-caching

For cache efficiency:
- Put stable, reusable content at the TOP of files
- Large reference files (>1024 tokens) benefit most from caching
- Structure references/ files with static content first, examples last
- Avoid mixing frequently-changing content with static patterns
- SKILL.md is loaded first, references/ loaded on-demand (cache-friendly)

Cache thresholds (minimum tokens to cache):
- Claude Sonnet/Opus: 1024 tokens
- Claude Haiku 3: 2048 tokens
- Claude Haiku 4.5/Opus 4.5: 4096 tokens

When NOT to optimize for caching:
- Small skills under 1024 tokens (won't cache anyway)
- Highly dynamic content that changes per-request
- One-time reference lookups
-->
