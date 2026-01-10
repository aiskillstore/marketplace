---
name: firefox-browser
description: Control the user's Firefox browser with their logins and cookies intact. Use when you need to browse websites as the user, interact with authenticated pages, fill forms, click buttons, take screenshots, or get page content. (user)
allowed-tools: Bash, Read, Write
---

# Firefox Browser Agent Bridge

Control the user's actual Firefox browser session via WebSocket. This uses their real browser with existing logins and cookies - **not** a headless browser.

## Quick Start

```bash
# 0. If Firefox isn't running, start it first
nohup firefox &>/dev/null &

# 1. Check connection
browser ping

# 2. See what tabs are open
browser listTabs '{}'

# 3. Start a new session (recommended)
browser newSession '{"url": "https://example.com"}'

# 4. Read the page with interactable elements marked
browser getContent '{"format": "annotated"}'
```

## Client Usage

```bash
browser <action> '<json_params>'
```

## Actions Reference

### Session & Tab Management

| Action | Description | Key Params |
|--------|-------------|------------|
| `listTabs` | List all open tabs across windows | - |
| `newSession` | Create new tab to work in | `url` (optional) |
| `setActiveTab` | Switch which tab agent works on | `tabId`, `focus` |
| `getActiveTab` | Get current tab info | - |

### Navigation & Page Info

| Action | Description | Key Params |
|--------|-------------|------------|
| `navigate` | Go to URL in current tab | `url`, `wait`, `newTab` |
| `getContent` | Get page content | `format`: `annotated`, `text`, `html` |
| `getInteractables` | List clickable elements and inputs | `selector` (optional scope) |
| `screenshot` | Capture visible area as PNG | `filename` (optional) |

### Interaction

| Action | Description | Key Params |
|--------|-------------|------------|
| `click` | Click element | `selector`, `text`, or `x`/`y` coords |
| `type` | Type into focused/selected input | `selector`, `text`, `submit`, `clear` |
| `fillForm` | Fill form fields (inputs, textareas, selects) | `fields[]` array with selector/value |
| `waitFor` | Wait for element/text | `selector`, `text`, `timeout` |

#### fillForm - The Right Way to Fill Forms

**IMPORTANT:** There is no `fill` command. Use `fillForm` with a `fields` array:

```bash
# Fill a single field
browser fillForm '{"fields": [{"selector": "#email", "value": "test@example.com"}]}'

# Fill multiple fields at once (text inputs, textareas, AND select dropdowns)
browser fillForm '{"fields": [
  {"selector": "#name", "value": "John Doe"},
  {"selector": "#email", "value": "john@example.com"},
  {"selector": "#subject", "value": "support"},
  {"selector": "#message", "value": "Hello world"}
]}'
```

Works with: `<input>`, `<textarea>`, `<select>`, checkboxes, radio buttons.

### Control Flow

| Action | Description | Key Params |
|--------|-------------|------------|
| `fork` | Duplicate tab into multiple paths | `paths[]` with name + commands |
| `killFork` | Close a fork | `fork` (name) |
| `listForks` | List active forks | - |
| `tryUntil` | Try alternatives until one succeeds | `alternatives[]`, `timeout` |
| `parallel` | Run commands on multiple URLs | `branches[]` with url + commands |

### Authentication

| Action | Description | Key Params |
|--------|-------------|------------|
| `getAuthContext` | Detect login pages, available accounts | - |
| `requestAuth` | Request user approval for auth | `reason` |
| `configureAuth` | Set auth preferences | `authMode`, `setSiteRule`, `domain` |

---

## Recommended Workflow

### 1. Start by Inspecting Available Tabs

```bash
browser listTabs '{}'
```

Returns:
```json
{
  "activeTabId": 123,
  "windows": [
    {
      "windowId": 1,
      "focused": true,
      "tabs": [
        {"tabId": 123, "url": "https://...", "title": "...", "active": true}
      ]
    }
  ],
  "totalTabs": 5
}
```

### 2. Start Fresh or Pick Existing Tab

```bash
# Start fresh
browser newSession '{"url": "https://amazon.com"}'

# Or switch to existing tab
browser setActiveTab '{"tabId": 456}'
```

### 3. Read Page with Annotated Format (Recommended)

```bash
browser getContent '{"format": "annotated"}'
```

Returns content with interactive elements marked inline:
```
Product Name Here
$4.99
[button: "Add to cart" | selector: #add-btn]
[input:text: "search" | value: "" | selector: #search-box]
[link: "View details" | href: /product/123 | selector: a.details-link]
```

This shows **what's clickable** and **where it is in context**.

### 4. Interact Using Selectors

```bash
# Click using selector from annotated output
browser click '{"selector": "#add-btn"}'

# Or by text (prefers visible elements)
browser click '{"text": "Add to cart"}'

# Type into input
browser type '{"selector": "#search-box", "text": "query", "submit": true}'
```

---

## Fork: Speculative Parallel Execution

When you're not sure which path is right, fork the tab and try both:

```bash
# Create forks
browser fork '{
  "paths": [
    {
      "name": "google-auth",
      "commands": [{"action": "click", "params": {"text": "Sign in with Google"}}]
    },
    {
      "name": "email-auth",
      "commands": [{"action": "click", "params": {"text": "Sign in with Email"}}]
    }
  ]
}'
```

Returns:
```json
{
  "forked": true,
  "sourceTabId": 123,
  "forks": [
    {"name": "google-auth", "tabId": 456, "url": "...", "commandResults": [...]},
    {"name": "email-auth", "tabId": 789, "url": "...", "commandResults": [...]}
  ]
}
```

Work on specific fork:
```bash
browser getContent '{"format": "annotated", "fork": "google-auth"}'
browser click '{"text": "Continue", "fork": "google-auth"}'
```

Kill the wrong path:
```bash
browser killFork '{"fork": "email-auth"}'
```

---

## TryUntil: Handle Uncertain UI

When the exact button varies (cookie banners, A/B tests):

```bash
browser tryUntil '{
  "alternatives": [
    {"action": "click", "params": {"selector": "#accept-cookies"}},
    {"action": "click", "params": {"text": "Accept All"}},
    {"action": "click", "params": {"selector": ".cookie-dismiss"}}
  ],
  "timeout": 3000
}'
```

Tries each until one succeeds.

---

## Parallel: Multiple URLs at Once

Compare prices across sites:

```bash
browser parallel '{
  "branches": [
    {"url": "https://amazon.com/product", "commands": [{"action": "getContent", "params": {"format": "text"}}]},
    {"url": "https://walmart.com/product", "commands": [{"action": "getContent", "params": {"format": "text"}}]}
  ]
}'
```

---

## Authentication

The bridge detects auth pages and leverages existing browser sessions:

```bash
# Check if on login page
browser getAuthContext '{}'

# Returns available accounts, OAuth options, etc.
```

---

## Isolated Sessions (for Parallel Execution)

When running multiple tasks in parallel, use `tabId` to avoid conflicts:

```bash
# 1. Create isolated session - get a unique tabId
browser newSession '{"url": "https://example.com"}'
# Returns: {"tabId": 15, "url": "...", "windowId": 1}

# 2. Use that tabId in ALL subsequent commands
browser navigate '{"url": "https://example.com/page", "tabId": 15}'
browser getContent '{"format": "annotated", "tabId": 15}'
browser click '{"selector": "#btn", "tabId": 15}'
browser type '{"selector": "#input", "text": "hello", "tabId": 15}'
```

This lets multiple agents work in parallel without stepping on each other.

## Tips

1. **Start with `listTabs`** to see what's open
2. **Use `newSession`** for a clean start
3. **Use `tabId`** for parallel/isolated execution
4. **Use `annotated` format** - shows content + clickable elements together
5. **Use selectors from annotated output** - more reliable than text matching
6. **Fork when uncertain** - try multiple paths, kill the wrong ones

## Troubleshooting

1. **Firefox not running?** Start it: `nohup firefox &>/dev/null &`
2. **Check connection**: `browser ping`
3. **Connection refused?** The extension may need to be reloaded in `about:debugging`
4. **Element not found?** Use `browser getContent '{"format": "annotated"}'` to see what's on the page
