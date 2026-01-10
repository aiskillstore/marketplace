---
name: playwright-browser
description: Control a Playwright browser via CLI - navigate, interact, and screenshot
version: 1.0.0
license: MIT
compatibility: opencode
---

## Overview

CLI tools for controlling a Playwright browser. Uses Playwright's accessibility tree for lightweight, efficient page interaction.

## Interactive Session Workflow

Start a persistent browser session and issue commands against it:

```bash
# Start session (opens visible browser window)
bun .opencode/skill/playwright-browser/session.js start

# Navigate to a site
bun .opencode/skill/playwright-browser/navigate.js https://duckduckgo.com

# Get page structure
bun .opencode/skill/playwright-browser/snapshot.js

# Type in search box and submit
bun .opencode/skill/playwright-browser/type.js "combobox:Search with DuckDuckGo" "github" --press Enter

# Click on a result
bun .opencode/skill/playwright-browser/click.js "link:GitHub"

# Take a screenshot
bun .opencode/skill/playwright-browser/screenshot.js --output result.png

# Stop session when done
bun .opencode/skill/playwright-browser/session.js stop
```

## Commands

### Session

Manage a persistent browser session for interactive use.

```bash
bun .opencode/skill/playwright-browser/session.js start
bun .opencode/skill/playwright-browser/session.js stop
bun .opencode/skill/playwright-browser/session.js status
```

**Options:**
- `--headless` - Run in headless mode (default: headed/visible)

**Examples:**
```bash
bun .opencode/skill/playwright-browser/session.js start
bun .opencode/skill/playwright-browser/session.js start --headless
bun .opencode/skill/playwright-browser/session.js status
bun .opencode/skill/playwright-browser/session.js stop
```

---

### Navigate

Navigate to a URL in the browser.

```bash
bun .opencode/skill/playwright-browser/navigate.js <url>
```

**Examples:**
```bash
bun .opencode/skill/playwright-browser/navigate.js https://example.com
```

---

### Snapshot

Get the accessibility tree of the current page.

```bash
bun .opencode/skill/playwright-browser/snapshot.js
```

Shows the page structure in a text format. Use this to find elements to interact with.

**Output format:**
```
- navigation:
  - link "About"
- search:
  - combobox "Search"
  - button "Submit"
```

---

### Type

Type text into an input element on the page.

```bash
bun .opencode/skill/playwright-browser/type.js <ref> <text> [--press Enter]
```

**Arguments:**
- `ref` - Element reference (role:name, text:content, or CSS selector)
- `text` - Text to type

**Options:**
- `--press <key>` - Press a key after typing (e.g., Enter, Tab)

**Examples:**
```bash
bun .opencode/skill/playwright-browser/type.js "combobox:Search" "hello" --press Enter
bun .opencode/skill/playwright-browser/type.js "input[name='q']" "search query"
```

---

### Click

Click an element on the page.

```bash
bun .opencode/skill/playwright-browser/click.js <ref>
```

**Arguments:**
- `ref` - Element reference (role:name, text:content, or CSS selector)

**Examples:**
```bash
bun .opencode/skill/playwright-browser/click.js "button:Submit"
bun .opencode/skill/playwright-browser/click.js "link:Sign in"
```

---

### Screenshot

Take a screenshot of the current page.

```bash
bun .opencode/skill/playwright-browser/screenshot.js [--output <path>] [--full]
```

**Options:**
- `--output <path>` - Output file path (default: screenshot.png)
- `--full` - Capture full page (scrolls entire page)

**Examples:**
```bash
bun .opencode/skill/playwright-browser/screenshot.js
bun .opencode/skill/playwright-browser/screenshot.js --output page.png
```

---

## Element References

Commands that interact with elements (`type`, `click`) accept flexible element references:

| Format | Example | Description |
|--------|---------|-------------|
| `role:name` | `combobox:Search` | Accessibility role and name |
| `text:content` | `text:Sign in` | Element containing text |
| CSS selector | `#login-btn` | Standard CSS selector |
| CSS selector | `input[name='q']` | Attribute selector |

**Recommended workflow:**
1. Use `snapshot` to see the accessibility tree
2. Find the element's role and name
3. Use `role:name` format for reliable interaction

## Error Recovery

Commands provide helpful error messages with suggestions:

- **Element not found**: "Element 'X' not found. Try: snapshot to see available elements"
- **Session issues**: Commands automatically start a session if none exists
- **Navigation failures**: "Navigation failed at URL. Try: navigate URL"

## Notes

- Browser data is stored in `.playwright-data/` in the project root
- The persistent context maintains cookies and localStorage between sessions
- Commands use `networkidle` wait for reliable page loading
