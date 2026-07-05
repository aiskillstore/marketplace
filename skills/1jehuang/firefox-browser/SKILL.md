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
| `type` | Type into input | `selector`, `text`, `submit`, `clear` |
| `fillForm` | Fill multiple fields | `fields[]` with selector/value pairs |
| `waitFor` | Wait for element/text | `selector`, `text`, `timeout` |
| `scroll` | Scroll the page | `y`/`x`, `selector`, `position` |
| `evaluate` | Execute JavaScript and return result | `script` |

### Control Flow

| Action | Description | Key Params |
|--------|-------------|------------|
| `fork` | Duplicate tab into multiple paths | `paths[]` with name + commands |
| `killFork` | Close a fork | `fork` (name) |
| `listForks` | List active forks | - |
| `tryUntil` | Try alternatives until one succeeds | `alternatives[]`, `timeout` |
| `parallel` | Run commands on multiple URLs | `branches[]` with url + commands |

### Authentication & Vault

| Action | Description | Key Params |
|--------|-------------|------------|
| `autoLogin` | Auto-fill credentials from Bitwarden vault and optionally submit | `domain`, `submit` (default false) |
| `vaultStatus` | Check vault lock state and credential count | - |
| `vaultSync` | Re-sync vault from Bitwarden server via API key | - |
| `getAuthContext` | Detect login pages, available accounts | - |
| `requestAuth` | Request user approval for auth | `reason` |

---

## Rich Text Editors (ProseMirror, Lexical, Slate, etc.)

The `type` and `fillForm` actions automatically handle rich text editors (ProseMirror, Lexical/Reddit, Draft.js, Tiptap, Slate, CKEditor, Quill). They use `document.execCommand("insertText")` in the page world, which works with any `contenteditable`-based editor.

```bash
# Works on any rich text editor — ProseMirror, Lexical, etc.
browser type '{"selector": "div[contenteditable=true]", "text": "Hello world!"}'
# Response includes richEditor: true when execCommand path was used

# Clear existing content and replace
browser type '{"selector": ".ProseMirror", "text": "New content", "clear": true}'

# Fill multiple rich text fields in a form
browser fillForm '{"fields": [
  {"selector": "#title", "value": "My Title"},
  {"selector": "#body .ProseMirror", "value": "Article body text"}
]}'
```

No special handling needed — just use `type` or `fillForm` as normal. Falls back to `textContent` assignment if `execCommand` isn't available.

---


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

## Authentication (Autonomous Login)

The bridge integrates with a Bitwarden vault (via bronzewarden) for fully autonomous credential fill. No human interaction needed.

### Auto-Login Flow

```bash
# 1. Navigate to the site
browser navigate '{"url": "https://github.com"}'

# 2. Auto-fill credentials (looks up domain in vault, fills form)
browser autoLogin '{"domain": "github.com", "submit": false}'
# Returns: {"filled": true, "maskedUsername": "j***1", "matchedUri": "https://github.com/"}

# 3. Or auto-fill AND submit in one step
browser autoLogin '{"domain": "github.com", "submit": true}'
```

### Vault Management

```bash
# Check vault status
browser vaultStatus '{}'
# Returns: {"locked": false, "entries": 322}

# Re-sync vault from server (if credentials were updated)
browser vaultSync '{}'
# Returns: {"synced": true, "entries": 322}
```

### How It Works
- Credentials are stored in Bitwarden and decrypted locally by the native host
- The `autoLogin` action sends credentials directly to the extension via the native messaging channel (never over WebSocket)
- Vault is auto-unlocked at host startup using a master password from the system keyring

### Legacy Auth Detection

```bash
# Detect login pages and available accounts
browser getAuthContext '{}'
```

---

## Evaluate: Run JavaScript and Get Results

Execute arbitrary JavaScript in the page context and get the result back:

```bash
# Get page title
browser evaluate '{"script": "return document.title"}'
# Returns: {"result": "My Page Title", "type": "string"}

# Count elements
browser evaluate '{"script": "return document.querySelectorAll(\"input\").length"}'
# Returns: {"result": 5, "type": "number"}

# Get form values
browser evaluate '{"script": "return document.querySelector(\"#email\").value"}'
# Returns: {"result": "user@example.com", "type": "string"}

# Complex queries
browser evaluate '{"script": "return Array.from(document.querySelectorAll(\"input:checked\")).map(el => el.value)"}'
# Returns: {"result": ["option1", "option3"], "type": "object"}
```

### Page World Evaluation

By default, `evaluate` runs in the content script's isolated world. To access page-level JavaScript variables (e.g., framework state, global objects set by the page), use `pageWorld: true`:

```bash
# Access page-level globals (React state, editor instances, app data)
browser evaluate '{"script": "return window.__NEXT_DATA__", "pageWorld": true}'

# Interact with ProseMirror/Lexical internals
browser evaluate '{"script": "return Object.keys(window.__prosemirrorViews || {})", "pageWorld": true}'

# Call page-level functions
browser evaluate '{"script": "return window.myApp.getState()", "pageWorld": true}'
```

**Note:** Use `return` to get a value back. The script runs with full DOM access. Use `pageWorld: true` when you need to access variables set by the page's own JavaScript.

---

## Scroll: Navigate Long Pages

Scroll the page by pixels, to elements, or to positions:

```bash
# Scroll down 500 pixels
browser scroll '{"y": 500}'

# Scroll up 300 pixels
browser scroll '{"y": -300}'

# Scroll element into view
browser scroll '{"selector": "#section-5"}'

# Scroll to top/bottom
browser scroll '{"position": "top"}'
browser scroll '{"position": "bottom"}'

# Smooth scrolling
browser scroll '{"y": 500, "behavior": "smooth"}'

# Scroll to absolute position
browser scroll '{"scrollTo": {"x": 0, "y": 1000}}'
```

---

## Form State in Annotated Content

The `getContent` annotated format now shows form element states:

```bash
browser getContent '{"format": "annotated"}'
```

Output includes checked/selected states:
```
[input:radio: "Option A" | checked: true | selector: #opt-a]
[input:radio: "Option B" | checked: false | selector: #opt-b]
[input:checkbox: "Remember me" | checked: true | selector: #remember]
[select: "Country" | selected: "United States" | selector: #country]
[input:text: "Email" | value: "user@example.com" | selector: #email]
```

This is useful for verifying form state without screenshots.

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
