---
name: multi-agent-orchestration
description: "Orchestrate tasks across multiple AI providers (Claude, OpenAI, Gemini, Cursor, OpenCode, Ollama). Use when delegating tasks to specialized providers, routing based on capabilities, or implementing fallback strategies."
---

# Multi-Agent Orchestration Skill

Route and delegate tasks to the most appropriate AI provider based on task characteristics and provider capabilities.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| ENABLED_CLAUDE | true | Enable Claude Code as provider |
| ENABLED_OPENAI | true | Enable OpenAI/Codex as provider |
| ENABLED_GEMINI | true | Enable Gemini as provider |
| ENABLED_CURSOR | true | Enable Cursor as provider |
| ENABLED_OPENCODE | true | Enable OpenCode as provider |
| ENABLED_OLLAMA | true | Enable local Ollama as provider |
| DEFAULT_PROVIDER | claude | Fallback when routing is uncertain |
| CHECK_COST_STATUS | true | Check usage before delegating |

## Instructions

**MANDATORY** - Follow the Workflow steps below in order. Do not skip steps.

- Before delegating, understand the task characteristics
- Use the model-discovery skill for current model names
- Check cost/usage status before high-volume delegation

## Quick Decision Tree

```
What type of task is this?
│
├─ Needs conversation history? ─────────► Keep in Claude (no delegation)
│
├─ Needs sandboxed execution? ──────────► OpenAI/Codex
│
├─ Large context (>100k tokens)? ───────► Gemini
│
├─ Multimodal (images/video)? ──────────► Gemini
│
├─ Needs web search? ───────────────────► Gemini
│
├─ Quick IDE edit? ─────────────────────► Cursor
│
├─ Privacy required / offline? ─────────► Ollama
│
├─ Provider-agnostic fallback? ─────────► OpenCode
│
└─ General reasoning / coding? ─────────► Claude (default)
```

## Red Flags - STOP and Reconsider

If you're about to:
- Delegate without checking provider availability
- Use hardcoded model names (use model-discovery skill instead)
- Send sensitive data to a provider without user consent
- Delegate a task that requires your conversation history
- Skip the routing decision and guess which provider

**STOP** -> Read the appropriate cookbook file -> Check provider status -> Then proceed

## Workflow

1. [ ] Analyze the task: What capabilities are required?
2. [ ] **CHECKPOINT**: Consult `reference/provider-matrix.md` for routing decision
3. [ ] Check provider availability: Run provider-check and cost-status if CHECK_COST_STATUS is true
4. [ ] Read the appropriate cookbook file for the selected provider
5. [ ] **CHECKPOINT**: Confirm API key / auth is configured
6. [ ] Execute delegation with proper context
7. [ ] Parse and summarize results for the user

## Cookbook

### Claude Code (Orchestrator)
- IF: Task requires complex reasoning, multi-file analysis, or conversation history
- THEN: Keep task in Claude Code (you are the orchestrator)
- WHY: Best for architecture decisions, complex refactoring

### OpenAI / Codex
- IF: Task needs sandboxed execution OR security-sensitive operations
- THEN: Read and execute `cookbook/openai-codex.md`
- REQUIRES: `OPENAI_API_KEY` or Codex subscription

### Google Gemini
- IF: Task involves large context (>100k tokens), multimodal (images/video), OR web search
- THEN: Read and execute `cookbook/gemini-cli.md`
- REQUIRES: `GEMINI_API_KEY` or Gemini subscription

### Cursor
- IF: Task is quick IDE edits, simple codegen, or rename/refactor
- THEN: Read and execute `cookbook/cursor-agent.md`
- REQUIRES: Cursor installed and configured

### OpenCode
- IF: Need provider-agnostic execution or a fallback CLI
- THEN: Read and execute `cookbook/opencode-cli.md`
- REQUIRES: OpenCode CLI installed and configured

### Ollama (Local)
- IF: Task needs privacy, offline operation, or cost-free inference
- THEN: Read and execute `cookbook/ollama-local.md`
- REQUIRES: Ollama running with models pulled

## Model Names

**Do not hardcode model version numbers** - they become stale quickly.

For current model names, use the `model-discovery` skill:
```bash
python .claude/ai-dev-kit/skills/model-discovery/scripts/fetch_models.py
```

Or read: `.claude/ai-dev-kit/skills/model-discovery/SKILL.md`

## Quick Reference

| Task Type | Primary | Fallback |
|-----------|---------|----------|
| Complex reasoning | Claude | OpenAI |
| Sandboxed execution | OpenAI | Cursor |
| Large context (>100k) | Gemini | Claude |
| Multimodal | Gemini | Claude |
| Quick codegen | Cursor | Claude |
| Web search | Gemini | (web tools) |
| Privacy/offline | Ollama | Claude |

See `reference/provider-matrix.md` for detailed routing guidance.

## Tool Discovery

Orchestration tools are available in `.claude/ai-dev-kit/dev-tools/orchestration/`:

```bash
# Check provider status and usage
.claude/ai-dev-kit/dev-tools/orchestration/monitoring/cost-status.sh

# Check CLI availability (optional apply)
.claude/ai-dev-kit/dev-tools/orchestration/monitoring/provider-check.py

# Intelligent task routing
.claude/ai-dev-kit/dev-tools/orchestration/routing/route-task.py "your task"

# Direct provider execution
.claude/ai-dev-kit/dev-tools/orchestration/providers/claude-code/spawn.sh "task"
.claude/ai-dev-kit/dev-tools/orchestration/providers/codex/execute.sh "task"
.claude/ai-dev-kit/dev-tools/orchestration/providers/gemini/query.sh "task"
.claude/ai-dev-kit/dev-tools/orchestration/providers/cursor/agent.sh "task"
.claude/ai-dev-kit/dev-tools/orchestration/providers/opencode/execute.sh "task"
.claude/ai-dev-kit/dev-tools/orchestration/providers/ollama/query.sh "task"
```

## Output

Delegation results should be:
1. Parsed from provider's response format
2. Summarized for the user
3. Integrated back into the conversation context

```markdown
## Delegation Result

**Provider**: [provider name]
**Task**: [brief description]
**Status**: Success / Partial / Failed

### Summary
[Key findings or outputs]

### Details
[Full response if relevant]
```
