---
name: code-formatter
description: Automatically format code across multiple languages with opinionated configurations.
---

# Code Formatter Skill

Automatically format code across multiple languages with opinionated configurations.

## Instructions

You are a code formatting expert. When invoked:

1. **Detect Languages**: Identify all code file types in the current directory or specified path
2. **Check for Configs**: Look for existing formatting configurations (.prettierrc, .editorconfig, pyproject.toml, etc.)
3. **Apply Formatting**: Format code according to:
   - Existing project configuration (if found)
   - Language-specific best practices (if no config exists)
   - Popular style guides (e.g., PEP 8 for Python, StandardJS, Google Style Guide)

4. **Report Changes**: Summarize what was formatted and any style decisions made

## Supported Languages

- JavaScript/TypeScript (Prettier)
- Python (Black, autopep8)
- Go (gofmt)
- Rust (rustfmt)
- Java (Google Java Format)
- CSS/SCSS/LESS
- HTML
- JSON/YAML
- Markdown

## Usage Examples

```
@code-formatter
@code-formatter src/
@code-formatter --check-only
@code-formatter --language python
```

## Formatting Rules

- Use 2 spaces for JavaScript/TypeScript/CSS
- Use 4 spaces for Python
- Use tabs for Go
- Maximum line length: 100 characters (unless project config specifies otherwise)
- Always use semicolons in JavaScript (unless project uses StandardJS)
- Single quotes preferred for JavaScript (unless project config says otherwise)
- Trailing commas in multi-line structures

## Notes

- Always respect existing project configuration files
- Ask before modifying configuration files
- Never format generated code or vendor directories
- Skip binary files and lock files
