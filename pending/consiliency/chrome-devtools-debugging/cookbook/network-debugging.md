# Network Debugging Cookbook

Patterns for debugging web application network requests using Chrome DevTools MCP.

## Basic Request Inspection

### List All API Requests

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network

# Get XHR and fetch requests (typical API calls)
api_calls = network.get_api_requests()
print(api_calls)
"
```

### Get Failed Requests

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network

# Get 4xx/5xx responses
failed = network.get_failed_requests()
print(failed)
"
```

### Get Slow Requests

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network

# Requests over 1 second
slow = network.get_slow_requests(threshold_ms=1000)
print(slow)
"
```

## Request Details

### Full Request/Response Headers

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network

# First, list requests to find the ID
requests = network.get_api_requests()
print(requests)

# Then get full details for a specific request
# details = network.get_network_request(request_id='123.456')
# print(details)
"
```

### Filter by Resource Type

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network

# Document loads
docs = network.list_network_requests(resource_types=['document'])
print('Documents:', docs)

# Scripts
scripts = network.list_network_requests(resource_types=['script'])
print('Scripts:', scripts)

# Images
images = network.list_network_requests(resource_types=['image'])
print('Images:', images)

# WebSocket connections
ws = network.list_network_requests(resource_types=['websocket'])
print('WebSockets:', ws)
"
```

## Authentication Debugging

### Capture Auth Flow

1. Start Chrome with remote debugging
2. Navigate to login page
3. Login manually
4. Inspect captured requests:

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network

# See auth-related requests
api_calls = network.get_api_requests()
print(api_calls)

# Look for:
# - /auth/login
# - /oauth/token
# - /api/session
# - Cookie/Authorization headers
"
```

### Check Auth Headers

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network, debug

# Get cookies
cookies = debug.evaluate_script('document.cookie')
print(f'Cookies: {cookies}')

# Check if auth token in localStorage
token = debug.evaluate_script('localStorage.getItem(\"authToken\") || localStorage.getItem(\"token\")')
print(f'Token: {token}')
"
```

## API Response Analysis

### Analyze JSON Responses

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network
import json

# Get API requests
api_calls = network.get_api_requests()
print('Recent API calls:')
print(api_calls)

# Get specific request details
# request = network.get_network_request(request_id='...')
# Response body available in request details
"
```

### Find Rate-Limited Requests

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network

# Look for 429 Too Many Requests
failed = network.get_failed_requests()
# Filter for 429 status codes
print(failed)
"
```

## Performance Debugging

### Identify Blocking Resources

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network

# Slow resources that might block rendering
slow = network.get_slow_requests(threshold_ms=500)
print('Slow resources (>500ms):')
print(slow)
"
```

### Check Cache Usage

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network

# Get all requests and check their cache status
# Cached requests typically show 'from disk cache' or 'from memory cache'
requests = network.list_network_requests(page_size=50)
print(requests)
"
```

## Combined Debugging

### Network + Console Correlation

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import console, network

# Get failed requests
print('=== Failed Network Requests ===')
failed = network.get_failed_requests()
print(failed)

# Get console errors that might relate to failed requests
print('\\n=== Console Errors ===')
errors = console.get_errors()
print(errors)
"
```

### Full Page Load Analysis

```bash
uv run python -c "
import sys; sys.path.insert(0, 'dev-tools')
from mcp_servers.chrome_devtools import network, navigation

# Navigate to fresh page load
navigation.navigate_page(url='https://example.com', ignore_cache=True)

# Wait for page to load
navigation.wait_for(text='Expected Content', timeout=10000)

# Analyze all requests
print('=== Documents ===')
print(network.list_network_requests(resource_types=['document']))

print('\\n=== API Calls ===')
print(network.get_api_requests())

print('\\n=== Failed Requests ===')
print(network.get_failed_requests())

print('\\n=== Slow Requests ===')
print(network.get_slow_requests(threshold_ms=1000))
"
```

## Common Network Issues

### CORS Failures

Request blocked by CORS - check:
- Response headers for `Access-Control-Allow-Origin`
- Preflight OPTIONS requests
- Missing credentials in request

### Mixed Content

HTTPS page loading HTTP resources - check:
- Scripts loaded over HTTP
- Images/fonts over HTTP
- WebSocket connections (ws:// vs wss://)

### Certificate Errors

SSL/TLS issues - check:
- Expired certificates
- Self-signed certificates in development
- Certificate chain issues

### Timeout Errors

Requests timing out - check:
- Server response times
- Network connectivity
- DNS resolution issues
