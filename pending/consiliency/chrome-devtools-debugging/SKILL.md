---
name: chrome-devtools-debugging
description: Debug and analyze web applications using Chrome DevTools MCP. Use for console log inspection, network request monitoring, performance analysis, and debugging authenticated sessions. For basic browser automation (screenshots, form filling), use browser-discovery skill instead.
---

# Chrome DevTools Debugging

Debug web applications by connecting to Chrome's DevTools Protocol. This skill enables:
- **Console inspection**: View errors, warnings, and log messages
- **Network analysis**: Monitor XHR/fetch requests with full headers/body
- **Performance tracing**: Record and analyze performance traces
- **JavaScript evaluation**: Execute code in browser context
- **Authenticated session debugging**: Connect to existing logged-in browsers

## When to Use This Skill

| Use Case | This Skill | browser-discovery |
|----------|------------|-------------------|
| Console error inspection | Yes | No |
| Network request analysis | Yes | Limited |
| Performance tracing | Yes | No |
| Authenticated sessions | Yes | No |
| Screenshots | No | Yes |
| Form filling | No | Yes |
| Basic navigation | Limited | Yes |

## Setup Requirements

### Option 1: Connect to Existing Chrome (Recommended)

Start Chrome with remote debugging enabled:

```bash
# Linux
google-chrome --remote-debugging-port=9222

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

Set the environment variable:
```bash
export CHROME_DEVTOOLS_URL=http://127.0.0.1:9222
```

### Option 2: Chrome Auto-Connect (145+)

For Chrome 145+, enable remote debugging at `chrome://inspect/#remote-debugging`.

## Progressive Disclosure Pattern

This skill uses **progressive MCP disclosure** for token efficiency:

```
Chrome DevTools MCP Server
         |
         v
Python Wrappers (.claude/ai-dev-kit/dev-tools/mcp_servers/chrome_devtools/)
         |
         v
Claude executes Python via Bash (on-demand)
         |
         v
Results returned (tools NOT in system prompt)
```

**Benefits**: 98%+ token reduction vs loading all MCP tools in system prompt.

## Quick Examples

### Get Console Errors

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import console

errors = console.list_console_messages(types=['error'])
print(errors)
"
```

### List Network Requests

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network

requests = network.list_network_requests(resource_types=['xhr', 'fetch'])
print(requests)
"
```

### Execute JavaScript

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import debug

title = debug.evaluate_script('document.title')
print(f'Page title: {title}')
"
```

### Debug Authenticated Session

```bash
# 1. Log into the site manually in Chrome (started with --remote-debugging-port=9222)
# 2. Then analyze the authenticated state:

uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import navigation, network, debug

# List open tabs
pages = navigation.list_pages()
print(pages)

# Get auth tokens from localStorage
tokens = debug.evaluate_script('JSON.stringify(localStorage)')
print(f'localStorage: {tokens}')

# See recent API calls
api_calls = network.get_api_requests()
print(api_calls)
"
```

## Available Tool Modules

### console
- `list_console_messages(types, page_size, page_idx)` - Get console output
- `get_console_message(message_id)` - Get specific message details
- `get_errors()` - Convenience: get error messages only
- `get_warnings()` - Convenience: get warnings only

### network
- `list_network_requests(resource_types, page_size, page_idx)` - List requests
- `get_network_request(request_id)` - Get full request/response details
- `get_failed_requests()` - Convenience: get 4xx/5xx requests
- `get_api_requests()` - Convenience: get XHR/fetch requests
- `get_slow_requests(threshold_ms)` - Convenience: get slow requests

### performance
- `start_trace(reload, auto_stop)` - Start recording trace
- `stop_trace()` - Stop and get trace data
- `get_insights()` - Get available insight sets
- `analyze_insight(insight_set_id, insight_name)` - AI-powered insight analysis

### debug
- `evaluate_script(expression)` - Execute JavaScript

### navigation
- `navigate_page(url, nav_type, ignore_cache, timeout)` - Navigate page
- `list_pages()` - List all tabs
- `select_page(page_idx, bring_to_front)` - Switch to tab by index
- `new_page(url, timeout)` - Open new tab
- `close_page(page_idx)` - Close tab by index
- `wait_for(text, timeout)` - Wait for text on page

## Red Flags

- Chrome not started with `--remote-debugging-port=9222`
- `CHROME_DEVTOOLS_URL` environment variable not set
- Port 9222 blocked by firewall
- Trying to use for screenshots (use browser-discovery instead)
- MCP server not installed (`npx chrome-devtools-mcp@latest`)

## See Also

- [reference.md](reference.md) - Full API documentation
- [cookbook/console-debugging.md](cookbook/console-debugging.md) - Console debugging patterns
- [cookbook/network-debugging.md](cookbook/network-debugging.md) - Network analysis patterns
- `browser-discovery` skill - For screenshots, basic automation
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
