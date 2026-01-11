# Chrome DevTools MCP Reference

Complete reference for Chrome DevTools MCP tools accessible via Python wrappers.

## Connection Options

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CHROME_DEVTOOLS_URL` | URL of Chrome with remote debugging | `http://127.0.0.1:9222` |
| `CHROME_DEVTOOLS_HEADLESS` | Run in headless mode | `true` |

### Client Configuration

```python
from mcp_servers.chrome_devtools.client import ChromeDevToolsClient

# Connect to existing Chrome
client = ChromeDevToolsClient(browser_url="http://127.0.0.1:9222")

# Auto-connect to Chrome 145+
client = ChromeDevToolsClient(auto_connect=True)

# Launch headless Chrome
client = ChromeDevToolsClient(headless=True)

# Custom profile directory
client = ChromeDevToolsClient(user_data_dir="/path/to/profile")
```

---

## Console Tools

### list_console_messages

Get console messages from the browser.

```python
from mcp_servers.chrome_devtools.console import list_console_messages

messages = list_console_messages(
    types=["error"],      # Optional: ["log", "warn", "error", "info", "debug", "dir", "table", "trace"]
    page_size=100,        # Optional: max messages to return
    page_idx=0,           # Optional: page number for pagination
    include_preserved=False  # Optional: include messages from previous navigations
)
```

**Returns:** Markdown-formatted response with message objects.

### get_console_message

Get details for a specific message.

```python
from mcp_servers.chrome_devtools.console import get_console_message

details = get_console_message(message_id="123")
```

**Returns:** Message object with additional `stackTrace` and `args` fields.

### Convenience Functions

```python
from mcp_servers.chrome_devtools.console import get_errors, get_warnings

errors = get_errors()    # Get only error-level messages
warnings = get_warnings()  # Get only warning-level messages
```

---

## Network Tools

### list_network_requests

List captured network requests.

```python
from mcp_servers.chrome_devtools.network import list_network_requests

requests = list_network_requests(
    resource_types=["xhr", "fetch"],  # Optional: ["xhr", "fetch", "document", "script", "stylesheet", "image", "font", "websocket"]
    page_size=100,        # Optional: max requests
    page_idx=0,           # Optional: page number for pagination
    include_preserved=False  # Optional: include requests from previous navigations
)
```

**Returns:** Markdown-formatted response with request objects.

### get_network_request

Get full request/response details.

```python
from mcp_servers.chrome_devtools.network import get_network_request

details = get_network_request(request_id="123.456")
```

**Returns:** Request object with headers, body, timing, etc.

### Convenience Functions

```python
from mcp_servers.chrome_devtools.network import (
    get_failed_requests,
    get_api_requests,
    get_slow_requests
)

failed = get_failed_requests()  # Get 4xx/5xx status requests
api_calls = get_api_requests()  # Get XHR/fetch requests
slow = get_slow_requests(threshold_ms=1000)  # Get slow requests
```

---

## Performance Tools

### start_trace

Start recording a performance trace.

```python
from mcp_servers.chrome_devtools.performance import start_trace

result = start_trace(
    reload=True,      # Reload page when starting trace (default: True)
    auto_stop=True    # Auto-stop after page load (default: True)
)
```

**Returns:** Markdown-formatted confirmation.

### stop_trace

Stop recording and get trace data.

```python
from mcp_servers.chrome_devtools.performance import stop_trace

trace = stop_trace()
```

**Returns:** Markdown-formatted trace summary.

### get_insights

Get available insight sets from the trace.

```python
from mcp_servers.chrome_devtools.performance import get_insights

insights = get_insights()
```

**Returns:** List of available insight sets and their insights.

### analyze_insight

Get AI-powered analysis of a specific insight.

```python
from mcp_servers.chrome_devtools.performance import analyze_insight

analysis = analyze_insight(
    insight_set_id="network",      # Required: ID from get_insights()
    insight_name="slow-requests"   # Required: insight name from get_insights()
)
```

**Returns:** Markdown-formatted AI analysis.

---

## Debug Tools

### evaluate_script

Execute JavaScript in browser context.

```python
from mcp_servers.chrome_devtools.debug import evaluate_script

# Simple expression
title = evaluate_script("document.title")

# Get current URL
url = evaluate_script("window.location.href")

# Complex code
items = evaluate_script("""
    Array.from(document.querySelectorAll('.item')).map(el => ({
        id: el.dataset.id,
        name: el.textContent.trim()
    }))
""")

# Get localStorage
storage = evaluate_script("JSON.stringify(localStorage)")
```

**Note:** Expressions are automatically wrapped in arrow functions as required by the MCP tool. Async expressions are supported.

---

## Navigation Tools

### navigate_page

Navigate the current page.

```python
from mcp_servers.chrome_devtools.navigation import navigate_page

# Navigate to URL
result = navigate_page(url="https://app.example.com/dashboard")

# Reload page
result = navigate_page(nav_type="reload")

# Go back in history
result = navigate_page(nav_type="back")

# Go forward
result = navigate_page(nav_type="forward")

# Navigate with options
result = navigate_page(
    url="https://example.com",
    nav_type="url",         # "url", "back", "forward", "reload"
    ignore_cache=True,      # Bypass cache
    timeout=30000           # Timeout in ms
)
```

### list_pages

List all open tabs.

```python
from mcp_servers.chrome_devtools.navigation import list_pages

pages = list_pages()
```

**Returns:** Markdown-formatted list of tabs with indices.

### select_page

Switch to a different tab by index.

```python
from mcp_servers.chrome_devtools.navigation import select_page

select_page(
    page_idx=1,             # 0-based tab index
    bring_to_front=True     # Optional: bring browser window to front
)
```

### new_page

Open a new tab and navigate to URL.

```python
from mcp_servers.chrome_devtools.navigation import new_page

page = new_page(
    url="https://example.com",  # Required: URL to open
    timeout=30000               # Optional: timeout in ms
)
```

### close_page

Close a tab by index.

```python
from mcp_servers.chrome_devtools.navigation import close_page

close_page(page_idx=1)  # Close tab at index 1
```

### wait_for

Wait for text to appear on the page.

```python
from mcp_servers.chrome_devtools.navigation import wait_for

wait_for(
    text="Dashboard",    # Required: text to wait for
    timeout=10000        # Optional: timeout in ms
)
```

---

## MCP Tools Reference

The Python wrappers call these underlying MCP tools:

| Category | Tool | Python Wrapper |
|----------|------|----------------|
| **Console** | `list_console_messages` | `console.list_console_messages(types, page_size, page_idx)` |
| | `get_console_message` | `console.get_console_message(message_id)` |
| **Network** | `list_network_requests` | `network.list_network_requests(resource_types, page_size, page_idx)` |
| | `get_network_request` | `network.get_network_request(request_id)` |
| **Performance** | `performance_start_trace` | `performance.start_trace(reload, auto_stop)` |
| | `performance_stop_trace` | `performance.stop_trace()` |
| | `performance_get_insights` | `performance.get_insights()` |
| | `performance_analyze_insight` | `performance.analyze_insight(insight_set_id, insight_name)` |
| **Debug** | `evaluate_script` | `debug.evaluate_script(expression)` |
| **Navigation** | `navigate_page` | `navigation.navigate_page(url, nav_type, ignore_cache, timeout)` |
| | `list_pages` | `navigation.list_pages()` |
| | `select_page` | `navigation.select_page(page_idx, bring_to_front)` |
| | `new_page` | `navigation.new_page(url, timeout)` |
| | `close_page` | `navigation.close_page(page_idx)` |
| | `wait_for` | `navigation.wait_for(text, timeout)` |

---

## Error Handling

```python
from mcp_servers.chrome_devtools.client import get_client

try:
    client = get_client()
    result = client.call_tool("list_console_messages", {})
except TimeoutError:
    print("MCP server not responding - is Chrome running?")
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
```

---

## Troubleshooting

### Chrome Not Connecting
1. Verify Chrome is running with `--remote-debugging-port=9222`
2. Check `CHROME_DEVTOOLS_URL` environment variable
3. Ensure port 9222 is not blocked by firewall

### MCP Server Issues
1. Verify Node.js is installed: `node --version`
2. Try manual MCP server start: `npx chrome-devtools-mcp@latest --browserUrl http://127.0.0.1:9222`
3. Check for error output in stderr

### Tools Not Returning Data
1. Ensure page is loaded before querying console/network
2. For performance traces, wait for trace recording to complete
3. Check that the page has the expected content
