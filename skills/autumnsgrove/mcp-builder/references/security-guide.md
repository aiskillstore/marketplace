# MCP Security Best Practices

## Authentication Methods

### 1. No Authentication (Development Only)
```python
# No auth configuration needed
# WARNING: Only use for local development!
```

**Use case**: Local testing, proof of concept
**Security level**: None
**Recommendation**: Never use in production

### 2. API Key Authentication
```python
# Server side: Validate API key
async def authenticate_request(api_key: str):
    if api_key != os.getenv("MCP_API_KEY"):
        raise ValueError("Invalid API key")
```

**Use case**: Simple authentication for internal services
**Security level**: Medium
**Best practices**:
- Store keys in environment variables
- Rotate keys regularly
- Use HTTPS for transmission

### 3. OAuth 2.0 Flow
```python
# Server configuration
{
    "oauth": {
        "authorizationUrl": "https://provider.com/oauth/authorize",
        "tokenUrl": "https://provider.com/oauth/token",
        "clientId": "your-client-id",
        "scopes": ["read", "write"]
    }
}
```

**Use case**: Third-party integrations, user-facing applications
**Security level**: High
**Best practices**:
- Use authorization code flow for web apps
- Implement PKCE for mobile/SPA apps
- Store tokens securely

### 4. Bearer Token
```python
# Client sends token in Authorization header
headers = {
    "Authorization": f"Bearer {token}"
}
```

**Use case**: API-to-API communication
**Security level**: High (if tokens are JWT with validation)
**Best practices**:
- Validate token signature
- Check expiration
- Verify claims

## Security Implementation Examples

### API Key Authentication
```python
import os
from functools import wraps

# Load API key from environment
VALID_API_KEY = os.getenv("MCP_API_KEY")

def require_auth(func):
    """Decorator to require API key authentication"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # In production, API key would come from request headers
        # For stdio transport, use environment variable
        if not VALID_API_KEY:
            raise ValueError("Server not configured with API key")
        return await func(*args, **kwargs)
    return wrapper

@app.call_tool()
@require_auth
async def call_tool(name: str, arguments: dict):
    """Protected tool handler"""
    # Tool logic here
    pass
```

### OAuth 2.0 Example (HTTP Transport)
```python
from aiohttp import web
import jwt

class OAuthMCPServer:
    def __init__(self):
        self.app = web.Application()
        self.app.router.add_post('/mcp', self.handle_mcp_request)

    async def verify_token(self, request):
        """Verify OAuth bearer token"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise web.HTTPUnauthorized(text="Missing or invalid token")

        token = auth_header[7:]  # Remove 'Bearer ' prefix

        try:
            # Verify JWT token
            payload = jwt.decode(
                token,
                os.getenv('JWT_SECRET'),
                algorithms=['HS256']
            )
            return payload
        except jwt.InvalidTokenError:
            raise web.HTTPUnauthorized(text="Invalid token")

    async def handle_mcp_request(self, request):
        """Handle authenticated MCP request"""
        # Verify authentication
        user_info = await self.verify_token(request)

        # Parse MCP request
        mcp_request = await request.json()

        # Process request with user context
        response = await self.process_mcp_request(mcp_request, user_info)

        return web.json_response(response)
```

## Input Validation

### URL Validation
```python
import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """Validate URL is safe"""
    parsed = urlparse(url)

    # Check scheme
    if parsed.scheme not in ['http', 'https']:
        raise ValidationError("Only HTTP/HTTPS URLs allowed")

    # Block local/private IPs
    if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
        raise ValidationError("Local URLs not allowed")

    return True
```

### SQL Injection Prevention
```python
def sanitize_sql(query: str) -> str:
    """Basic SQL injection prevention"""
    dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER']
    query_upper = query.upper()

    for keyword in dangerous_keywords:
        if keyword in query_upper:
            raise ValidationError(f"Dangerous SQL keyword: {keyword}")

    return query
```

## Rate Limiting

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests: int, time_window: timedelta):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        now = datetime.now()
        cutoff = now - self.time_window

        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]

        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False

        # Record request
        self.requests[client_id].append(now)
        return True

# Usage
rate_limiter = RateLimiter(max_requests=100, time_window=timedelta(minutes=1))

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    client_id = get_client_id()  # From auth context

    if not rate_limiter.is_allowed(client_id):
        return [TextContent(
            type="text",
            text="Rate limit exceeded. Please try again later.",
            isError=True
        )]

    return await execute_tool(name, arguments)
```

## Secrets Management

### Environment Variables
```python
import os

# ✅ Good: Environment variables
API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate required secrets
if not API_KEY or not DATABASE_URL:
    raise ValueError("Missing required environment variables")
```

### Secrets File (Gitignored)
```python
from pathlib import Path
import json

def load_secrets():
    secrets_path = Path.home() / ".mcp" / "secrets.json"
    with open(secrets_path) as f:
        return json.load(f)

# ❌ Bad: Hardcoded secrets
API_KEY = "sk-1234567890abcdef"  # NEVER DO THIS!
```

## Production Security Hardening

```python
import secrets
import hashlib
from functools import wraps

# Generate secure tokens
def generate_api_key():
    return secrets.token_urlsafe(32)

# Hash sensitive data
def hash_password(password: str) -> str:
    salt = secrets.token_bytes(32)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex() + hashed.hex()

# Verify hashed data
def verify_password(password: str, hashed: str) -> bool:
    salt = bytes.fromhex(hashed[:64])
    stored_hash = bytes.fromhex(hashed[64:])
    new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return secrets.compare_digest(stored_hash, new_hash)

# Require HTTPS in production
def require_https(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        if request.scheme != 'https' and os.getenv('ENVIRONMENT') == 'production':
            raise web.HTTPBadRequest(text="HTTPS required")
        return await func(request, *args, **kwargs)
    return wrapper
```

## Security Checklist

- [ ] Always use HTTPS for production servers
- [ ] Store credentials in environment variables or secrets management
- [ ] Implement rate limiting to prevent abuse
- [ ] Use short-lived tokens with refresh mechanism
- [ ] Log authentication attempts for audit trails
- [ ] Validate all user inputs
- [ ] Use parameterized queries for database access
- [ ] Implement CORS properly for HTTP servers
- [ ] Keep dependencies updated
- [ ] Regularly rotate credentials
