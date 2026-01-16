---
name: baoyu-gemini-web
description: Image generation skill using Gemini Web. Generates images from text prompts via Google Gemini. Also supports text generation. Use as the image generation backend for other skills like cover-image, xhs-images, article-illustrator.
---

# Gemini Web Client

## Quick start

```bash
npx -y bun scripts/main.ts "Hello, Gemini"
npx -y bun scripts/main.ts --prompt "Explain quantum computing"
npx -y bun scripts/main.ts --prompt "A cute cat" --image cat.png
npx -y bun scripts/main.ts --promptfiles system.md content.md --image out.png
```

## Commands

### Text generation

```bash
# Simple prompt (positional)
npx -y bun scripts/main.ts "Your prompt here"

# Explicit prompt flag
npx -y bun scripts/main.ts --prompt "Your prompt here"
npx -y bun scripts/main.ts -p "Your prompt here"

# With model selection
npx -y bun scripts/main.ts -p "Hello" -m gemini-2.5-pro

# Pipe from stdin
echo "Summarize this" | npx -y bun scripts/main.ts
```

### Image generation

```bash
# Generate image with default path (./generated.png)
npx -y bun scripts/main.ts --prompt "A sunset over mountains" --image

# Generate image with custom path
npx -y bun scripts/main.ts --prompt "A cute robot" --image robot.png

# Shorthand
npx -y bun scripts/main.ts "A dragon" --image=dragon.png
```

### Output formats

```bash
# Plain text (default)
npx -y bun scripts/main.ts "Hello"

# JSON output
npx -y bun scripts/main.ts "Hello" --json
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--prompt <text>` | `-p` | Prompt text |
| `--promptfiles <files...>` | | Read prompt from files (concatenated in order) |
| `--model <id>` | `-m` | Model: gemini-3-pro (default), gemini-2.5-pro, gemini-2.5-flash |
| `--image [path]` | | Generate image, save to path (default: generated.png) |
| `--json` | | Output as JSON |
| `--login` | | Refresh cookies only, then exit |
| `--cookie-path <path>` | | Custom cookie file path |
| `--profile-dir <path>` | | Chrome profile directory |
| `--help` | `-h` | Show help |

## Models

- `gemini-3-pro` - Default, latest model
- `gemini-2.5-pro` - Previous generation pro
- `gemini-2.5-flash` - Fast, lightweight

## Authentication

First run opens Chrome to authenticate with Google. Cookies are cached for subsequent runs.

```bash
# Force cookie refresh
npx -y bun scripts/main.ts --login
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `GEMINI_WEB_DATA_DIR` | Data directory |
| `GEMINI_WEB_COOKIE_PATH` | Cookie file path |
| `GEMINI_WEB_CHROME_PROFILE_DIR` | Chrome profile directory |
| `GEMINI_WEB_CHROME_PATH` | Chrome executable path |

## Examples

### Generate text response
```bash
npx -y bun scripts/main.ts "What is the capital of France?"
```

### Generate image
```bash
npx -y bun scripts/main.ts "A photorealistic image of a golden retriever puppy" --image puppy.png
```

### Get JSON output for parsing
```bash
npx -y bun scripts/main.ts "Hello" --json | jq '.text'
```

### Generate image from prompt files
```bash
# Concatenate system.md + content.md as prompt
npx -y bun scripts/main.ts --promptfiles system.md content.md --image output.png
```
