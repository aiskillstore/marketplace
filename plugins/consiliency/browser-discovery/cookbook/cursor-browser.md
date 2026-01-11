# Cursor Browser Tools

Guide for using Cursor IDE's browser automation capabilities.

## Two Access Methods

### 1. In-IDE: MCP Browser Tools

When running inside Cursor IDE, browser tools are available natively.

**Detection:** Check for `mcp__cursor__browser_navigate` in tool list.

**Available Tools:**

| Tool | Purpose |
|------|---------|
| `mcp__cursor__browser_navigate` | Navigate to URL |
| `mcp__cursor__browser_click` | Click element |
| `mcp__cursor__browser_type` | Type in input |
| `mcp__cursor__browser_scroll` | Scroll page |
| `mcp__cursor__browser_screenshot` | Take screenshot |
| `mcp__cursor__browser_console` | Get console output |
| `mcp__cursor__browser_network` | Get network traffic |

**Invocation:** Use `@browser` command or direct tool calls.

### 2. CLI: cursor-agent

When delegating from Claude Code or other CLIs.

**Detection:**

```bash
which cursor-agent
```

**Basic Usage:**

```bash
cursor-agent -p "Your task description here" --output-format text
```

## Key Flags

| Flag | Purpose |
|------|---------|
| `-p "task"` | Non-interactive mode with task prompt |
| `--output-format text` | Get parseable text output |
| `--model "model"` | Specify model (optional) |

## Documentation Discovery via CLI

```bash
cursor-agent -p "Navigate to ${homepage} using the browser.
Wait for the page to fully load.
Find all documentation navigation links.
Return a JSON array of objects with: url, title, section." \
  --output-format text
```

## Link Extraction Workflow (In-IDE)

```
1. mcp__cursor__browser_navigate(url: homepage)
2. mcp__cursor__browser_scroll(direction: "down", amount: 500)
3. mcp__cursor__browser_screenshot()
4. Parse screenshot/DOM for navigation links
```

## MCP Configuration Sharing

Any MCP servers configured in Cursor work with the CLI too. This means:
- Shared tool access
- Same authentication
- Consistent behavior

## Best Practices

1. **Prefer CLI delegation** from Claude Code for complex browser tasks
2. **Use text output format** for machine-parseable results
3. **Combine with existing MCP tools** when in-IDE
4. **Handle timeouts** - browser operations can be slow

## Error Handling

If cursor-agent fails:
1. Verify Cursor is installed: `which cursor-agent`
2. Check if Cursor background process is running
3. Try with simpler task description
4. Fall back to Playwright MCP
