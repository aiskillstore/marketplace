---
enact: "2.0.0"
name: "enact/docs/guide"
version: "1.0.0"
description: "LLM guide for creating, publishing, and running Enact tools"
license: "MIT"

tags:
  - documentation
  - guide
  - llm
  - tutorial

authors:
  - name: "Enact Protocol"

annotations:
  title: "Enact Tool Creation Guide"
  readOnlyHint: true

inputSchema:
  type: object
  properties:
    topic:
      type: string
      description: "Specific topic to learn about"
      enum:
        - "overview"
        - "creating"
        - "commands"
        - "languages"
        - "secrets"
        - "publishing"
        - "all"
      default: "all"
---

# Enact LLM Guide

Enact: Containerized tools with structured I/O for AI agents.

## Commands

```bash
enact run ./tool --input "key=value"      # Run local tool
enact run ./tool --args '{"key":"value"}' # Run with JSON
enact run author/tool --input "x=y"       # Run installed tool
enact install author/tool                 # Install to project
enact install author/tool -g              # Install globally
enact search "query"                      # Find tools
enact sign ./tool && enact publish ./tool # Publish
```

## Tool Structure

```
my-tool/
├── enact.md    # Required: YAML frontmatter + docs
└── main.py     # Your code (any language)
```

## enact.md Template

```yaml
---
enact: "2.0.0"
name: "namespace/category/tool-name"
version: "1.0.0"
description: "What it does"
from: "python:3.12-slim"
build: "pip install requests pandas"
command: "python /workspace/main.py ${input}"
timeout: "30s"

inputSchema:
  type: object
  properties:
    input:
      type: string
      description: "Input description"
  required: [input]

outputSchema:
  type: object
  properties:
    result:
      type: string

env:
  API_KEY:
    description: "API key"
    secret: true
  LOG_LEVEL:
    description: "Log level"
    default: "info"

tags: [category, keywords]
---

# Tool Name

Documentation here.
```

## Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | `namespace/category/tool` |
| `description` | Yes | What it does |
| `command` | No* | Shell command with `${param}` substitution |
| `from` | No | Docker image (default: `alpine:latest`) |
| `build` | No | Build commands (string or array), cached |
| `inputSchema` | No | JSON Schema for inputs |
| `outputSchema` | No | JSON Schema for outputs |
| `env` | No | Environment vars (`secret: true` for keyring) |
| `timeout` | No | Max runtime (default: `30s`) |
| `version` | No | Semver version |
| `tags` | No | Discovery keywords |

*Tools without `command` are LLM instruction tools (markdown interpreted by AI).

## Examples by Language

### Python
```yaml
from: "python:3.12-slim"
build: "pip install pandas"
command: "python /workspace/main.py ${input}"
```

### Node.js
```yaml
from: "node:20-alpine"
build: "npm install"
command: "node /workspace/index.js ${input}"
```

### Rust
```yaml
from: "rust:1.83-slim"
build: "rustc /workspace/main.rs -o /workspace/app"
command: "/workspace/app ${input}"
```

### Go
```yaml
from: "golang:1.22-alpine"
build: "go build -o /workspace/app /workspace/main.go"
command: "/workspace/app ${input}"
```

### Shell (no build)
```yaml
command: "echo 'Hello ${name}'"
```

## Source Code Pattern

Always output JSON matching `outputSchema`:

```python
#!/usr/bin/env python3
import sys, json

input_val = sys.argv[1]
result = {"result": input_val.upper()}
print(json.dumps(result))
```

## Secrets

```yaml
env:
  API_KEY:
    description: "API key"
    secret: true  # Stored in OS keyring, not .env
```

User sets: `enact env set API_KEY --secret --namespace myorg/tools`

Access in code via environment variable: `os.environ['API_KEY']`

## Two Tool Types

1. **Container tools** (has `command`): Runs in Docker, deterministic
2. **Instruction tools** (no `command`): Markdown body interpreted by LLM

## Workflow

```bash
# 1. Create
mkdir my-tool && cd my-tool
# Create enact.md + source files

# 2. Test
enact run . --input "test=value"

# 3. Publish
enact auth login
enact sign .
enact publish .
```

## Checklist

- [ ] `name`: namespace/category/tool format
- [ ] `description`: clear, searchable
- [ ] `inputSchema`: validates inputs
- [ ] `outputSchema`: documents output
- [ ] `from`: pinned image version (not `latest`)
- [ ] `build`: installs dependencies
- [ ] `command`: uses `${param}` for inputs
- [ ] Source outputs valid JSON
