# Playwright Browser (via Wrapper)

Guide for using Playwright in Claude Code via the Python wrapper (Progressive Disclosure pattern).

## Prerequisites

1. **Chrome with debugging enabled**:
   ```bash
   google-chrome --remote-debugging-port=9222
   ```

2. **Verify accessibility**:
   ```bash
   curl -s http://localhost:9222/json/version
   ```

## Why Wrapper Instead of MCP?

**Progressive Disclosure**: Instead of loading Playwright tools into context at startup (wasting tokens), the wrapper spawns the MCP server on-demand:

- **Before**: `.mcp.json` loads 22+ Playwright tools at startup (~2000 tokens)
- **After**: Wrapper invoked only when needed (0 tokens until used)

## Wrapper Location

```
.claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py
```

## Detection

Check if Chrome debugging is accessible:

```bash
curl -s "http://localhost:9222/json/version" > /dev/null 2>&1 && echo "Chrome ready" || echo "Chrome not ready"
```

## Available Commands

| Command | Purpose |
|---------|---------|
| `navigate <url>` | Navigate to URL |
| `snapshot` | Get accessibility tree (preferred) |
| `click --ref <ref> --element <desc>` | Click element |
| `type --ref <ref> --element <desc> --text <text>` | Type text |
| `wait --time <seconds>` | Wait for time |
| `wait --text <text>` | Wait for text to appear |
| `evaluate <js>` | Execute JavaScript |
| `screenshot` | Take screenshot |
| `close` | Close browser page |

## Documentation Discovery Workflow

```bash
# 1. Navigate to homepage
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py navigate "https://docs.viperjuice.dev"

# 2. Wait for JS rendering
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py wait --time 3

# 3. Get accessibility tree (structured data)
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py snapshot

# 4. Parse snapshot for navigation links (in your code)

# 5. For each discovered page:
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py navigate "https://docs.viperjuice.dev/page1"
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py wait --time 2
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py snapshot

# 6. Close browser when done
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py close
```

## Snapshot vs Screenshot

**Prefer `snapshot`** over screenshots for link extraction:
- Provides structured accessibility data
- Contains text and link targets
- Easier to parse programmatically
- Lower token usage

**Use screenshots** when:
- Visual layout matters
- Debugging rendering issues
- Content is in canvas/images

## Link Extraction Example

```bash
# Get snapshot with structured data
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py snapshot

# Snapshot returns accessibility tree with:
# - role: "link"
# - name: "link text"
# - ref: element reference for clicking
```

## JavaScript Evaluation

For complex extraction, use `evaluate`:

```bash
# Get all navigation links as JSON
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py evaluate "JSON.stringify(Array.from(document.querySelectorAll('nav a')).map(a => ({url: a.href, title: a.textContent.trim()})))"
```

## Handling Dynamic Content

```bash
# 1. Navigate to page
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py navigate "https://docs.viperjuice.dev"

# 2. Wait for initial render
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py wait --time 2

# 3. If content loads dynamically, wait for specific text:
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py wait --text "Documentation"

# 4. Then snapshot or extract
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py snapshot
```

## Python API

You can also use the wrapper as a Python module:

```python
from dev_tools.mcp.wrappers import PlaywrightWrapper

pw = PlaywrightWrapper()

# Navigate and wait
pw.navigate("https://docs.viperjuice.dev")
pw.wait_for(time_seconds=3)

# Get snapshot
snapshot = pw.snapshot()

# Evaluate JavaScript
links = pw.evaluate("JSON.stringify(Array.from(document.querySelectorAll('a')).map(a => a.href))")

# Close when done
pw.close()
```

## Connection Pooling

The wrapper uses connection pooling:
- First call spawns the MCP server
- Subsequent calls reuse the connection
- Server auto-terminates after 60s idle

This means:
- No startup overhead on repeated calls
- No resource leaks from abandoned sessions
- Clean context (no tools loaded at startup)

## Best Practices

1. **Always wait after navigation** - JS sites need time to render
2. **Prefer snapshot over screenshot** - structured data is easier to parse
3. **Close browser when done** - prevents resource leaks
4. **Use evaluate for complex extraction** - full JS access

## Error Handling

If Playwright fails:

1. **Check Chrome debugging**:
   ```bash
   curl -s http://localhost:9222/json/version
   ```

2. **Ensure Chrome is running with debugging**:
   ```bash
   google-chrome --remote-debugging-port=9222
   ```

3. **Check wrapper output for errors**:
   ```bash
   python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py navigate "https://docs.viperjuice.dev" 2>&1
   ```

4. **Verify npx can download Playwright MCP**:
   ```bash
   npx -y @playwright/mcp@latest --help
   ```

## WSL2 Notes

If running in WSL2:
1. Run Chrome in Windows with `--remote-debugging-port=9222`
2. Access via `http://$(hostname).local:9222` or find Windows IP
3. Or use X11 forwarding to run Chrome in WSL
