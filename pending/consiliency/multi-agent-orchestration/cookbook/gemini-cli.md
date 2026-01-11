# Gemini CLI Delegation

Delegate tasks to Google's Gemini CLI for large context, multimodal, and web search tasks.

## When to Use

- Large context processing (>100k tokens; see model-discovery for current limits)
- Multimodal tasks (images, video, audio)
- Tasks requiring web search/grounding
- Research tasks needing current information

## Prerequisites

### Authentication

**Subscription (Interactive):**
```bash
gemini
# Select Google OAuth when prompted
```

**API Key (Headless):**
```bash
export GEMINI_API_KEY="AI..."
```

### Check Installation

```bash
which gemini
gemini --version
```

## Delegation Commands

### Basic Query

```bash
gemini "your question or task here"
```

### With Specific Model

```bash
# Get current models first
python .claude/ai-dev-kit/skills/model-discovery/scripts/fetch_models.py --provider gemini

# Use a specific model
gemini --model gemini-3-pro "your task"
```

### Auto-Model Routing

Gemini CLI routes to the default model automatically when `--model` is omitted.
In the REPL, run `/model auto` to re-enable auto selection after pinning.

### Non-Interactive Mode

```bash
gemini -p "task description"
```

### With File Input

```bash
# Image analysis
gemini -p "Describe this image" --file screenshot.png

# Large document
gemini -p "Summarize this document" --file large-doc.pdf
```

### With Web Search

```bash
gemini -p "What are the latest updates to the React framework?" --search
```

## Key Flags

| Flag | Description |
|------|-------------|
| `--model` | Specify model (e.g., `gemini-3-pro`) |
| `-p "prompt"` | Non-interactive with prompt |
| `--file` | Attach file for analysis |
| `--search` | Enable web search grounding |
| `--output-format` | `text` or `json` |

## Example Delegations

### Large Codebase Analysis

```bash
gemini -p "Analyze this codebase structure and identify architectural patterns:

$(find src -name '*.ts' -exec cat {} \;)
"
```

### Image Analysis

```bash
gemini -p "Convert this UI mockup to React components" --file mockup.png
```

### Video Content Analysis

```bash
gemini -p "Summarize the key points from this tutorial video" --file tutorial.mp4
```

### Current Documentation Research

```bash
gemini -p "What are the current best practices for Next.js App Router in 2025?" --search
```

### Multi-File Comparison

```bash
gemini -p "Compare these two implementations and recommend which is better:

File 1:
$(cat implementation-a.ts)

File 2:
$(cat implementation-b.ts)
"
```

## Response Handling

Parse Gemini output and summarize:

```markdown
## Delegation Result

**Provider**: Google Gemini
**Task**: [task description]
**Status**: Success

### Key Findings
[Main points from analysis]

### Sources (if web search used)
[Referenced URLs]

### Details
[Full response]
```

## Context Window Usage

| Model | Input Limit | Output Limit |
|-------|-------------|--------------|
| gemini-3-flash-lite | See API output | See API output |
| gemini-3-pro | See API output | See API output |
| gemini-3-deep-think | See API output | See API output |

## Error Handling

| Error | Solution |
|-------|----------|
| "Authentication required" | Run `gemini` and complete OAuth |
| "File too large" | Split file or use streaming |
| "Model not found" | Check available models with model-discovery |
| "Quota exceeded" | Wait for reset or upgrade plan |

## Limitations

- Video analysis has duration limits
- Web search results may vary
- Output tokens limited compared to input
- Some file types not supported
