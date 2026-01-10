# Provider Capability Matrix

Detailed routing guidance for task delegation across AI providers.

## Provider Comparison

| Capability | Claude | OpenAI | Gemini | Cursor | OpenCode | Ollama |
|------------|--------|--------|--------|--------|----------|--------|
| Complex reasoning | Excellent | Very Good | Very Good | Good | Variable | Variable |
| Code generation | Excellent | Excellent | Very Good | Excellent | Variable | Good |
| Large context | 200k | 128k | 2M | 128k | Variable | Variable |
| Multimodal (images) | Yes | Yes | Yes | Yes | Variable | Some models |
| Multimodal (video) | No | No | Yes | No | Variable | No |
| Web search | Via tools | Via tools | Native | No | Variable | No |
| Sandboxed execution | No | Yes | No | No | Variable | No |
| Offline/Private | No | No | No | No | Variable | Yes |
| IDE integration | CLI | CLI | CLI | Native | CLI | CLI |
| Cost | $$ | $$ | $ | Subscription | Variable | Free |

## Task Routing Decision Tree

```
START
  │
  ├─ Needs conversation history? ─────────────────► KEEP IN CLAUDE
  │
  ├─ Needs sandboxed execution? ──────────────────► OpenAI/Codex
  │
  ├─ Large context (>100k tokens)? ───────────────► Gemini
  │
  ├─ Multimodal (video)? ─────────────────────────► Gemini
  │
  ├─ Needs web search/grounding? ─────────────────► Gemini
  │
  ├─ Quick IDE edit? ─────────────────────────────► Cursor
  │
  ├─ Need provider-agnostic fallback? ────────────► OpenCode
  │
  ├─ Privacy required / Offline? ─────────────────► Ollama
  │
  └─ General coding / reasoning ──────────────────► Claude (default)
```

## Detailed Task-to-Provider Mapping

### Complex Reasoning Tasks

| Task | Best Provider | Why |
|------|---------------|-----|
| Architecture design | Claude | Multi-file context, deep reasoning |
| Code review | Claude | Nuanced understanding |
| Bug investigation | Claude | Can trace through codebase |
| Security analysis | Claude/OpenAI | OpenAI for sandboxed testing |

### Code Generation Tasks

| Task | Best Provider | Why |
|------|---------------|-----|
| New feature implementation | Claude | Understands project context |
| Quick function generation | Cursor | Fast, IDE-integrated |
| Boilerplate generation | Cursor | Speed over reasoning |
| Algorithm implementation | Claude/OpenAI | Strong reasoning needed |

### Large Context Tasks

| Task | Best Provider | Why |
|------|---------------|-----|
| Analyze large codebase | Gemini | 2M context window |
| Process long documents | Gemini | Context capacity |
| Compare multiple files | Claude/Gemini | Both handle well |

### Multimodal Tasks

| Task | Best Provider | Why |
|------|---------------|-----|
| Analyze screenshot | Gemini/Claude | Both support images |
| Process video content | Gemini | Only option with video |
| Diagram to code | Gemini/Claude | Vision capabilities |

### Web/Research Tasks

| Task | Best Provider | Why |
|------|---------------|-----|
| Current documentation | Gemini | Native web grounding |
| API research | Gemini | Can search and verify |
| Fact verification | Gemini | Grounded responses |

### Security-Sensitive Tasks

| Task | Best Provider | Why |
|------|---------------|-----|
| Run untrusted code | OpenAI/Codex | Sandboxed environment |
| Test exploits (authorized) | OpenAI/Codex | Isolated execution |
| Dependency auditing | Claude | Analysis without execution |

### Privacy/Offline Tasks

| Task | Best Provider | Why |
|------|---------------|-----|
| Process sensitive data | Ollama | Stays local |
| Air-gapped environment | Ollama | No network needed |
| Cost-free experimentation | Ollama | No API costs |

## Authentication Patterns

### Subscription Auth (Interactive)

| Provider | Setup Command |
|----------|---------------|
| Claude | Ensure `ANTHROPIC_API_KEY` is NOT set |
| OpenAI/Codex | `codex login` (browser OAuth) |
| Gemini | `gemini` then select Google OAuth |
| Cursor | `cursor-agent login` |
| OpenCode | `opencode auth` |

### API Key Auth (Headless/CI)

| Provider | Environment Variable |
|----------|---------------------|
| Claude | `ANTHROPIC_API_KEY` |
| OpenAI/Codex | `OPENAI_API_KEY` or `CODEX_API_KEY` |
| Gemini | `GEMINI_API_KEY` |
| Cursor | `CURSOR_API_KEY` |
| OpenCode | `OPENCODE_API_KEY` |

## Fallback Strategy

When primary provider is unavailable:

1. **Check availability**: Run `cost-status.sh`
2. **Route intelligently**: Use `route-task.py --dry-run`
3. **Automatic fallback**: Router selects next available
4. **Manual override**: Use `--agent` flag to force provider

## Cost Considerations

| Provider | Cost Model | Best For |
|----------|------------|----------|
| Claude | Per token | Complex tasks worth the cost |
| OpenAI | Per token | Sandboxed execution |
| Gemini | Per token (cheaper) | High-volume, large context |
| Cursor | Subscription | Unlimited quick edits |
| OpenCode | Variable | Provider-agnostic fallback |
| Ollama | Free (local compute) | Experimentation, privacy |

## When to NOT Delegate

Keep the task in Claude Code when:
- User expects you to maintain conversation context
- Task requires access to previous messages
- Multiple back-and-forth iterations expected
- Security-sensitive context shouldn't leave conversation
- Task is simple enough that delegation overhead isn't worth it
