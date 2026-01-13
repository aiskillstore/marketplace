# Browser Automation Strategy

Use browser automation when curl fails on JavaScript-rendered documentation sites.

## Overview

Some documentation sites render content with JavaScript. When curl returns incomplete data, use browser automation to fetch the rendered content.

## Detection - When to Use Browser

```bash
# Check response size
SIZE=$(curl -s "https://docs.viperjuice.dev/docs" | wc -c)
if [ "$SIZE" -lt 1000 ]; then
  echo "Likely JS-rendered, use browser"
fi

# Check for JS framework markers
curl -s "https://docs.viperjuice.dev/docs" | grep -E "__NEXT_DATA__|__NUXT__|__remixContext"
```

### Signs You Need Browser

| Signal | Meaning |
|--------|---------|
| Response < 1KB | Only shell HTML returned |
| "Please enable JavaScript" | Explicit JS requirement |
| 403 Forbidden | May need real browser |
| `__NEXT_DATA__` in response | Next.js SSR/CSR |
| `window.__NUXT__` | Nuxt.js |
| Mostly CSS/fonts | JS builds content |

## IDE Browser Tools

See `browser-discovery` skill for detailed IDE-specific instructions.

### Priority Order

1. **Antigravity IDE**: `browser_subagent` (native)
2. **Cursor IDE**: `mcp__cursor__browser_*` (native)
3. **Cursor CLI**: `cursor-agent -p` (from Claude Code)
4. **Playwright (wrapper)**: `.claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py` (requires Chrome debugging)

## Playwright Wrapper Commands

### Prerequisites

```bash
# Launch Chrome with debugging
google-chrome --remote-debugging-port=9222

# Verify accessibility
curl -s http://localhost:9222/json/version
```

### Fetch Page

```bash
# Navigate to page
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py navigate "https://docs.viperjuice.dev/docs"

# Wait for JS rendering
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py wait --time 3

# Get accessibility snapshot
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py snapshot
```

### Extract Navigation

```bash
# 1. Navigate to homepage
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py navigate "https://docs.viperjuice.dev/docs"

# 2. Wait for JS to render
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py wait --time 3

# 3. Take snapshot (accessibility tree)
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py snapshot

# 4. Parse for navigation links (from snapshot output)

# 5. For each link:
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py navigate "$link_url"
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py wait --time 2
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py snapshot

# 6. Close when done
python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py close
```

## Registry Configuration

```json
{
  "js-rendered-docs": {
    "name": "JS Rendered Docs",
    "strategy": "browser_crawl",
    "browser": {
      "nav_selector": "nav.sidebar",
      "content_selector": "main",
      "wait_for": "nav",
      "js_required": true
    },
    "paths": {
      "homepage": "https://docs.viperjuice.dev/docs"
    }
  }
}
```

### Browser Config Options

| Option | Description |
|--------|-------------|
| `nav_selector` | CSS selector for navigation |
| `content_selector` | CSS selector for main content |
| `wait_for` | Element or time to wait |
| `js_required` | Skip curl, go straight to browser |

## Known JS-Rendered Sites

| Site | Framework | Notes |
|------|-----------|-------|
| antigravity.google | React | Full JS rendering |
| firebase.google.com | Angular | JS navigation |
| cloud.google.com/docs | Various | Partial JS |

## Advantages

- Works with any JS framework
- Gets fully rendered content
- Can handle complex navigation

## Disadvantages

- Slower than curl
- Requires browser setup
- May trigger rate limits
- More resource intensive

## Fallback Chain

1. Try curl first
2. If < 1KB or blocked → Try browser
3. If browser unavailable → Report as JS-required

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No browser tool available | Setup Playwright MCP or use Cursor |
| Page doesn't fully load | Increase wait time |
| Navigation not found | Try different selector |
| Rate limited | Add delays between requests |
