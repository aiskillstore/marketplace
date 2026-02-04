---
name: agentic-browser
description: |
  Browser automation for AI agents via inference.sh.
  Navigate web pages, interact with elements using @e refs, take screenshots.
  Capabilities: web scraping, form filling, clicking, typing, JavaScript execution.
  Use for: web automation, data extraction, testing, agent browsing, research.
  Triggers: browser, web automation, scrape, navigate, click, fill form, screenshot,
  browse web, playwright, headless browser, web agent, surf internet
allowed-tools: Bash(infsh *)
---

# Agentic Browser

Browser automation for AI agents via [inference.sh](https://inference.sh).

## Quick Start

```bash
curl -fsSL https://cli.inference.sh | sh && infsh login

# Open a page and get interactive elements
infsh app run agentic-browser --function open --input '{"url": "https://example.com"}' --session new
```

## Core Workflow

Every browser automation follows this pattern:

1. **Open**: Navigate to URL, get element refs
2. **Snapshot**: Re-fetch elements after DOM changes
3. **Interact**: Use `@e` refs to click, fill, etc.
4. **Re-snapshot**: After navigation, get fresh refs

```bash
# Start session
RESULT=$(infsh app run agentic-browser --function open --session new --input '{
  "url": "https://example.com/login"
}')
SESSION_ID=$(echo $RESULT | jq -r '.session_id')

# Elements returned like: @e1 [input] "Email", @e2 [input] "Password", @e3 [button] "Sign In"

# Fill form
infsh app run agentic-browser --function interact --session $SESSION_ID --input '{
  "action": "fill", "ref": "@e1", "text": "user@example.com"
}'

infsh app run agentic-browser --function interact --session $SESSION_ID --input '{
  "action": "fill", "ref": "@e2", "text": "password123"
}'

# Click submit
infsh app run agentic-browser --function interact --session $SESSION_ID --input '{
  "action": "click", "ref": "@e3"
}'

# Close when done
infsh app run agentic-browser --function close --session $SESSION_ID --input '{}'
```

## Functions

### open

Navigate to URL and configure browser. Returns page snapshot with `@e` refs.

```bash
infsh app run agentic-browser --function open --session new --input '{
  "url": "https://example.com",
  "width": 1280,
  "height": 720,
  "user_agent": "Mozilla/5.0..."
}'
```

**Returns:**
- `url`: Current page URL
- `title`: Page title
- `elements`: List of interactive elements with `@e` refs
- `screenshot`: Page screenshot (for vision agents)

### snapshot

Re-fetch page state after DOM changes. Always call after clicks that navigate.

```bash
infsh app run agentic-browser --function snapshot --session $SESSION_ID --input '{}'
```

### interact

Interact with elements using `@e` refs from snapshot.

| Action | Description | Required Fields |
|--------|-------------|-----------------|
| `click` | Click element | `ref` |
| `fill` | Clear and type text | `ref`, `text` |
| `type` | Type text (no clear) | `text` |
| `press` | Press key | `text` (e.g., "Enter") |
| `select` | Select dropdown | `ref`, `text` |
| `hover` | Hover over element | `ref` |
| `scroll` | Scroll page | `direction` (up/down) |
| `back` | Go back in history | - |
| `wait` | Wait milliseconds | `wait_ms` |

```bash
# Click
infsh app run agentic-browser --function interact --session $SESSION_ID --input '{
  "action": "click", "ref": "@e5"
}'

# Fill input
infsh app run agentic-browser --function interact --session $SESSION_ID --input '{
  "action": "fill", "ref": "@e1", "text": "hello@example.com"
}'

# Press Enter
infsh app run agentic-browser --function interact --session $SESSION_ID --input '{
  "action": "press", "text": "Enter"
}'

# Scroll down
infsh app run agentic-browser --function interact --session $SESSION_ID --input '{
  "action": "scroll", "direction": "down"
}'
```

### screenshot

Take page screenshot.

```bash
infsh app run agentic-browser --function screenshot --session $SESSION_ID --input '{
  "full_page": true
}'
```

### execute

Run JavaScript on the page.

```bash
infsh app run agentic-browser --function execute --session $SESSION_ID --input '{
  "code": "document.title"
}'
```

### close

Close browser session.

```bash
infsh app run agentic-browser --function close --session $SESSION_ID --input '{}'
```

## Element Refs

Elements are returned with `@e` refs like:

```
@e1 [a] "Home" href="/"
@e2 [input type="text"] placeholder="Search"
@e3 [button] "Submit"
@e4 [select] "Choose option"
```

**Important:** Refs are invalidated after navigation. Always re-snapshot after:
- Clicking links/buttons that navigate
- Form submissions
- Dynamic content loading

## Examples

### Form Submission

```bash
SESSION=$(infsh app run agentic-browser --function open --session new --input '{
  "url": "https://example.com/contact"
}' | jq -r '.session_id')

# Get elements: @e1 [input] "Name", @e2 [input] "Email", @e3 [textarea] "Message", @e4 [button] "Send"

infsh app run agentic-browser --function interact --session $SESSION --input '{"action": "fill", "ref": "@e1", "text": "John Doe"}'
infsh app run agentic-browser --function interact --session $SESSION --input '{"action": "fill", "ref": "@e2", "text": "john@example.com"}'
infsh app run agentic-browser --function interact --session $SESSION --input '{"action": "fill", "ref": "@e3", "text": "Hello!"}'
infsh app run agentic-browser --function interact --session $SESSION --input '{"action": "click", "ref": "@e4"}'

# Check result
infsh app run agentic-browser --function snapshot --session $SESSION --input '{}'

infsh app run agentic-browser --function close --session $SESSION --input '{}'
```

### Search and Extract

```bash
SESSION=$(infsh app run agentic-browser --function open --session new --input '{
  "url": "https://google.com"
}' | jq -r '.session_id')

# Fill search box and submit
infsh app run agentic-browser --function interact --session $SESSION --input '{"action": "fill", "ref": "@e1", "text": "weather today"}'
infsh app run agentic-browser --function interact --session $SESSION --input '{"action": "press", "text": "Enter"}'
infsh app run agentic-browser --function interact --session $SESSION --input '{"action": "wait", "wait_ms": 2000}'

# Get results page
infsh app run agentic-browser --function snapshot --session $SESSION --input '{}'

infsh app run agentic-browser --function close --session $SESSION --input '{}'
```

### Extract Data with JavaScript

```bash
infsh app run agentic-browser --function execute --session $SESSION --input '{
  "code": "Array.from(document.querySelectorAll(\"h2\")).map(h => h.textContent)"
}'
```

## Sessions

Browser state persists within a session. Always:
1. Start with `--session new` on first call
2. Use returned `session_id` for subsequent calls
3. Close session when done

## Related Skills

```bash
# Web search (for research + browse)
npx skills add inference-sh/skills@web-search

# LLM models (analyze extracted content)
npx skills add inference-sh/skills@llm-models
```

## Documentation

- [inference.sh Sessions](https://inference.sh/docs/extend/sessions) - Session management
- [Multi-function Apps](https://inference.sh/docs/extend/multi-function-apps) - How functions work
