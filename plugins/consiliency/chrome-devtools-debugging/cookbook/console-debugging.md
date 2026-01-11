# Console Debugging Cookbook

Patterns for debugging web application console output using Chrome DevTools MCP.

## Basic Error Inspection

### Get All Console Errors

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import console

errors = console.get_errors()
print(errors)
"
```

### Get All Warnings

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import console

warnings = console.get_warnings()
print(warnings)
"
```

### Filter by Message Type

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import console

# Get specific message types
messages = console.list_console_messages(types=['error', 'warn'])
print(messages)
"
```

## Error Analysis Patterns

### Find React Errors

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import console

errors = console.get_errors()
# Look for React-specific errors like:
# - Uncaught Error: Minified React error
# - Warning: Each child in a list should have a unique 'key' prop
# - Warning: Cannot update a component while rendering
print(errors)
"
```

### Find API Errors

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import console

# Errors often logged when API calls fail
errors = console.list_console_messages(types=['error'])
# Look for: fetch failed, NetworkError, 401, 403, 500
print(errors)
"
```

### Get Stack Traces

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import console

# Get error message with stack trace
errors = console.get_errors()
# Then get detailed info for a specific message
# details = console.get_console_message(message_id='123')
print(errors)
"
```

## Debugging Authenticated Sessions

### Check Auth State via Console

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import debug

# Check for auth-related console activity
# Often apps log auth state
storage = debug.evaluate_script('JSON.stringify(localStorage)')
print(f'localStorage: {storage}')

# Check for auth tokens
session = debug.evaluate_script('JSON.stringify(sessionStorage)')
print(f'sessionStorage: {session}')
"
```

### Monitor Console During Login

1. Open login page in Chrome (with `--remote-debugging-port=9222`)
2. Log in manually
3. Inspect console messages for errors:

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import console

# See what happened during login
messages = console.list_console_messages(page_size=50)
print(messages)
"
```

## Integration with Other Tools

### Console + Network Correlation

When you see a console error about a failed request, correlate with network:

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import console, network

# Get console errors
print('=== Console Errors ===')
errors = console.get_errors()
print(errors)

# Get failed network requests
print('\\n=== Failed Requests ===')
failed = network.get_failed_requests()
print(failed)
"
```

### Console + JavaScript Debugging

Extract error context using JavaScript evaluation:

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import debug

# Check application state
state = debug.evaluate_script('''
    window.__APP_STATE__ ||
    window.store?.getState?.() ||
    'No state found'
''')
print(f'App state: {state}')

# Check for error boundaries
error_boundary = debug.evaluate_script('''
    document.querySelector('[data-error-boundary]')?.textContent ||
    'No error boundary'
''')
print(f'Error boundary: {error_boundary}')
"
```

## Pagination for Large Logs

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import console

# Get first page
page1 = console.list_console_messages(page_size=20, page_idx=0)
print('Page 1:')
print(page1)

# Get second page
page2 = console.list_console_messages(page_size=20, page_idx=1)
print('\\nPage 2:')
print(page2)
"
```

## Common Error Patterns

### CORS Errors

Look for: `Access to XMLHttpRequest... has been blocked by CORS policy`

### Content Security Policy

Look for: `Refused to... because it violates the following Content Security Policy directive`

### Module Loading Errors

Look for: `Failed to load module script`, `SyntaxError: Unexpected token`

### Runtime Errors

Look for: `Uncaught TypeError`, `Uncaught ReferenceError`, `Uncaught SyntaxError`
