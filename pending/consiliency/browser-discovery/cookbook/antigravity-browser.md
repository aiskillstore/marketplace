# Antigravity Browser Subagent

Guide for using Antigravity IDE's native browser subagent.

## Detection

Check if `browser_subagent` tool is available in the tool list.

## Tool Parameters

```
browser_subagent(
  TaskName: string,   # Short identifier for the task
  Task: string        # Natural language description
)
```

## Capabilities

- Navigate to URLs
- Click elements
- Scroll pages
- Type in inputs
- DOM capture and parsing
- Screenshots
- Console log capture
- Video recording

## Architecture

```
Language Server → MCP Server → Chrome Extension → CDP commands
```

## Documentation Discovery Example

```
Use tool: browser_subagent
TaskName: "discover-docs-pages"
Task: "Navigate to https://docs.viperjuice.dev. Wait for the page to fully load.
Find all documentation navigation links (sidebar, top nav, table of contents).
Return a JSON object with:
- pages: array of {url, title, section} for each documentation page
- nav_structure: description of how navigation is organized"
```

## Link Extraction Example

```
Use tool: browser_subagent
TaskName: "extract-nav-links"
Task: "Navigate to ${homepage}. Wait for JavaScript to render.
Click on any collapsed navigation sections to expand them.
Extract all links from the sidebar navigation.
Return a JSON array of {url, title, section}."
```

## Configuration (Optional)

Antigravity supports allowlist/denylist for URL restrictions:
- Runs in isolated Chrome profile
- No persistent cookies between tasks
- Each task gets fresh browser state

## Best Practices

1. **Be explicit about waiting**: "Wait for the page to fully load"
2. **Specify output format**: "Return a JSON object with..."
3. **Handle dynamic content**: "Click to expand collapsed sections"
4. **Set scope**: "Only extract links from the sidebar"

## Error Handling

If browser_subagent fails:
1. Check if URL is accessible
2. Verify Chrome extension is installed
3. Try with simpler task description
4. Fall back to Playwright MCP if available
