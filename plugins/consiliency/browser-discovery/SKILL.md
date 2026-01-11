---
name: browser-discovery
description: "Browser automation for documentation discovery. Use when curl fails on JS-rendered sites, when detecting available browser tools, or when configuring browser-based documentation collection."
---

# Browser Discovery Skill

Detect and use browser automation tools for documentation discovery when static fetching fails.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PREFERRED_TOOL | auto | `auto`, `antigravity`, `cursor`, `playwright` |
| WAIT_TIMEOUT | 3 | Seconds to wait for JS rendering |
| MAX_PAGES | 50 | Maximum pages to discover per site |

## Instructions

**MANDATORY** - Follow the Workflow steps below when browser automation is needed.

- Always try curl first unless `js_required: true` is set
- Detect available browser tools before attempting automation
- Prefer accessibility snapshots over screenshots for link extraction

## Quick Decision Tree

```
Do you need browser automation?
│
├─ Curl returns full content? ──────────► NO - Use curl (docs-fetch-url)
│
├─ Curl returns <1KB or 403? ───────────► YES - Continue below
│
Which browser tool to use?
│
├─ browser_subagent available? ─────────► antigravity-browser.md
│
├─ In Cursor IDE? ──────────────────────► cursor-browser.md
│
├─ Chrome debugging on :9222? ──────────► playwright-browser.md (wrapper)
│
└─ No browser tool? ────────────────────► See "No Browser Available" section
```

## Red Flags - STOP and Reconsider

If you're about to:
- Use browser automation when curl would work
- Skip tool detection and assume a specific tool exists
- Take screenshots when snapshot would provide structured data
- Navigate without waiting for JS rendering

**STOP** -> Check the appropriate cookbook -> Then proceed

## Workflow

1. [ ] **CHECKPOINT**: Verify browser automation is actually needed
   - Curl response < 1KB?
   - Curl gets 403 Forbidden?
   - `js_required: true` in config?
2. [ ] Detect available browser tools (priority order)
3. [ ] Select best available tool
4. [ ] **CHECKPOINT**: Read the cookbook for selected tool
5. [ ] Execute browser-based discovery
6. [ ] Parse results and return structured data

## Tool Detection Priority

| Priority | Tool | Detection | Best For |
|----------|------|-----------|----------|
| 1 | Antigravity `browser_subagent` | Tool in tool list | Zero-config native |
| 2 | Cursor MCP (in-IDE) | `mcp__cursor__browser_*` | In Cursor IDE |
| 3 | Cursor CLI | `which cursor-agent` | Delegation from CLI |
| 4 | Playwright (wrapper) | `curl localhost:9222/json/version` | Full automation |

## Cookbook

### Antigravity Browser
- IF: `browser_subagent` tool available
- THEN: Read `cookbook/antigravity-browser.md`

### Cursor Browser
- IF: In Cursor IDE or `cursor-agent` available
- THEN: Read `cookbook/cursor-browser.md`

### Playwright Browser
- IF: Chrome debugging accessible at localhost:9222
- THEN: Read `cookbook/playwright-browser.md`

## When Browser Is Needed

Signs that a site requires browser automation:
- Curl response < 1KB (JS-rendered content)
- Response contains "please enable javascript"
- Framework markers: `__NEXT_DATA__`, `window.__remixContext`, `window.__NUXT__`
- Only CSS/font resources returned (no text content)

## No Browser Available

If no browser tool is detected:

```
No browser automation tool detected.

Setup options:
1. Antigravity IDE: Built-in (zero config)
2. Cursor: cursor-agent available when installed
3. Claude Code: Launch Chrome with debugging:
   google-chrome --remote-debugging-port=9222

   Then use the Playwright wrapper:
   python3 .claude/ai-dev-kit/dev-tools/mcp/wrappers/playwright_wrapper.py navigate "https://..."
```

## Output

Return discovered pages as structured data:

```json
{
  "pages": [
    {"url": "...", "title": "...", "section": "..."}
  ],
  "nav_structure": "sidebar | tabs | accordion",
  "js_required": true
}
```
