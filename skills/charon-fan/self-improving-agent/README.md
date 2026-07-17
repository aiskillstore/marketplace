# Self-Improving Agent

A self-improvement system that captures learning artifacts from skill experiences and proposes validated updates.

## Overview

This agent captures reusable evidence from skill interactions. It implements a feedback loop with memory artifacts, self-correction proposals, and evolution markers. Durable skill or code changes still require validation or explicit approval.

## Key Features

- **Multi-Memory Architecture**: Semantic + Episodic + Working memory
- **Evidence-Gated Learning**: Captures reusable lessons from skill workflows
- **Pattern Extraction**: Converts experiences into reusable patterns
- **Self-Correction**: Fixes skill guidance when errors occur
- **Self-Validation**: Periodically verifies skill accuracy
- **Proposal Artifacts**: Writes proposed updates before durable skill changes
- **Confidence Tracking**: Measures pattern reliability over time
- **Human-in-the-Loop**: Collects feedback to validate improvements

## Memory System

Current Claude Code hook integration writes to:

```
~/.claude/memory/
├── semantic/       # Patterns, rules, best practices
├── episodic/       # Specific experiences and episodes
└── working/        # Current session context
```

## How It Works

```
Any Skill Completes
        ↓
Extract Experience → Identify Patterns → Write Proposals → Consolidate Memory
        ↓                     ↓                  ↓              ↓
   What happened?    What can we reuse?   Which proposals? Track metrics
```

## Installation

```bash
apb skills add ./skills/self-improving-agent --scope global --target all --link
```

## Hooks (Optional)

Wire hooks to capture errors and session-end signals:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit",
        "hooks": [
          { "type": "command", "command": "bash ${SKILLS_DIR}/self-improving-agent/hooks/pre-tool.sh \"$TOOL_NAME\" \"$TOOL_INPUT\"" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "bash ${SKILLS_DIR}/self-improving-agent/hooks/post-bash.sh \"$TOOL_OUTPUT\" \"$EXIT_CODE\"" }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "bash ${SKILLS_DIR}/self-improving-agent/hooks/session-end.sh" }
        ]
      }
    ]
  }
}
```

## Triggering

### Host-Supported Follow-up
When the host runtime supports hook follow-ups, this skill can be recorded or run after high-signal workflows such as:
- prd-planner
- code-reviewer
- debugger
- refactoring-specialist
- etc.

### Manual
```
"自我进化"
"self-improve"
"分析今天的经验"
"总结这次教训"
```

## Example Learning

### Episode
```yaml
Skill: debugger
Situation: Form submission doesn't refresh data
Root Cause: Empty callback function
Pattern: Always verify callbacks have implementations
Confidence: 0.95 → Proposals: debugger, prd-implementation-precheck
```

### Skill Update
```markdown
## Proposed Update (2025-01-11)

### Pattern Added
**Callback Verification**: Always verify that callback functions
passed as props are not empty and actually execute logic.

**Source**: Episode ep-2025-01-11-003 (3 occurrences)
**Action**: Propose adding to debugger checklist
```

## Research Basis

- [SimpleMem: Efficient Lifelong Memory](https://arxiv.org/html/2601.02553v1)
- [ACM Memory Mechanisms Survey](https://dl.acm.org/doi/10.1145/3748302)
- [Lifelong Learning of LLM Agents](https://arxiv.org/html/2501.07278v1)

## Templates

Reusable templates live in `skills/self-improving-agent/templates`:
- `pattern-template.md`
- `correction-template.md`
- `validation-template.md`

## License

MIT
