# Cursor Agent Delegation

Delegate tasks to Cursor's agent CLI for quick IDE edits and code generation.

## When to Use

- Quick file edits in IDE context
- Simple code generation
- Rename/refactor operations
- Tasks benefiting from IDE integration

## Prerequisites

### Authentication

```bash
cursor-agent login
```

### Check Installation

```bash
which cursor-agent
cursor-agent --version
```

## Delegation Commands

### Basic Task

```bash
cursor-agent -p "your task description"
```

### With Specific Output Format

```bash
cursor-agent -p "task" --output-format text
```

### With Model Selection

```bash
cursor-agent -p "task" --model "model-name"
```

## Key Flags

| Flag | Description |
|------|-------------|
| `-p "prompt"` | Non-interactive with prompt |
| `--output-format` | `text` or `json` |
| `--model` | Specify model |
| `--cwd` | Set working directory |

## Example Delegations

### Quick File Edit

```bash
cursor-agent -p "Add TypeScript types to the function in src/utils/helpers.ts"
```

### Simple Code Generation

```bash
cursor-agent -p "Create a React component for a login form with email and password fields"
```

### Rename/Refactor

```bash
cursor-agent -p "Rename the function 'getData' to 'fetchUserData' across all files"
```

### Add Documentation

```bash
cursor-agent -p "Add JSDoc comments to all exported functions in src/api/client.ts"
```

### Browser Automation (Cursor has MCP browser tools)

```bash
cursor-agent -p "Navigate to ${url} using the browser.
Wait for the page to load.
Find all navigation links and return them as JSON."
```

## Response Handling

Parse Cursor output and summarize:

```markdown
## Delegation Result

**Provider**: Cursor Agent
**Task**: [task description]
**Status**: Success

### Changes Made
- [file1.ts]: Added types
- [file2.ts]: Updated imports

### Summary
[Brief description of changes]
```

## MCP Tools Available

When running in Cursor, these MCP tools may be available:

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Navigate to URL |
| `browser_click` | Click element |
| `browser_type` | Type in input |
| `browser_screenshot` | Take screenshot |

## Error Handling

| Error | Solution |
|-------|----------|
| "Not logged in" | Run `cursor-agent login` |
| "File not found" | Check working directory with `--cwd` |
| "Connection refused" | Ensure Cursor is running |

## Limitations

- Requires Cursor to be installed
- Best for quick, focused tasks
- May not have full project context
- Browser tools require MCP configuration
