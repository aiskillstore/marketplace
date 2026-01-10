# TaskFlow MCP Server Patterns

## Overview

Patterns learned from building the TaskFlow MCP Server - an internal service that wraps REST APIs for AI agent consumption via stateless HTTP transport.

---

## Architecture: Internal MCP Server

```
┌─────────────┐     JWT      ┌──────────────┐    user_id     ┌────────────┐    JWT/token   ┌──────────┐
│   User      │────────────▶│  Chat Server │──────────────▶│ MCP Server │──────────────▶│ REST API │
│ (Browser)   │             │ (validates)  │  access_token  │ (no auth)  │               │          │
└─────────────┘             └──────────────┘                └────────────┘               └──────────┘
```

**Key Insight**: MCP server is an internal service. Auth is handled upstream by Chat Server.

---

## Stateless HTTP Transport Setup

### FastMCP Singleton (app.py)

```python
from mcp.server.fastmcp import FastMCP

def _create_mcp() -> FastMCP:
    return FastMCP(
        "taskflow_mcp",
        stateless_http=True,  # Stateless - no persistent sessions
        json_response=True,   # Pure JSON responses (no SSE streaming)
    )

mcp = _create_mcp()
```

### Server Entry Point (server.py)

**IMPORTANT**: Use FastMCP's `streamable_http_app()` directly. Do NOT wrap in additional Starlette app.

```python
from starlette.middleware.cors import CORSMiddleware
from .app import mcp

# Import tools to register decorators (side effects)
import taskflow_mcp.tools.tasks  # noqa: F401
import taskflow_mcp.tools.projects  # noqa: F401

# Use FastMCP's built-in app directly - it includes /mcp route and lifespan
_mcp_app = mcp.streamable_http_app()

# Only add CORS wrapper
streamable_http_app = CORSMiddleware(
    _mcp_app,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "taskflow_mcp.server:streamable_http_app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
```

### Anti-Pattern: Double Wrapping

```python
# DON'T DO THIS - causes session timeout issues
_starlette_app = Starlette(
    routes=[Mount("/", app=mcp.streamable_http_app())],
    lifespan=custom_lifespan,  # Conflicts with FastMCP's lifespan
)
```

---

## Three Authentication Modes

### Configuration

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TASKFLOW_")

    api_url: str = "http://localhost:8000"
    api_timeout: float = 30.0
    dev_mode: bool = False           # Dev mode bypass
    service_token: str | None = None  # M2M service token
```

### API Client Headers

```python
def _get_headers(self, user_id: str, access_token: str | None = None) -> dict:
    headers: dict[str, str] = {}

    if self.service_token:
        # Mode 1: Service-to-service (M2M)
        headers["Authorization"] = f"Bearer {self.service_token}"
        headers["X-User-ID"] = user_id
    elif access_token:
        # Mode 2: Forward user's JWT
        headers["Authorization"] = f"Bearer {access_token}"
    elif self.dev_mode:
        # Mode 3: Dev mode bypass
        headers["X-User-ID"] = user_id
        headers["X-Service"] = "taskflow-mcp"

    return headers
```

### When to Use Each Mode

| Mode | Config | Use Case |
|------|--------|----------|
| Dev | `DEV_MODE=true` on both services | Local development |
| Production | Pass `access_token` in tool params | User JWT forwarding |
| Service Token | `SERVICE_TOKEN=xxx` | Internal service calls |

---

## Input Models with Auth

### Base Model

```python
from pydantic import BaseModel, Field

class AuthenticatedInput(BaseModel):
    """Base model with auth fields for all tools."""
    user_id: str = Field(..., description="User ID performing the action")
    access_token: str | None = Field(
        None,
        description="JWT access token (required in production, optional in dev mode)"
    )
```

### Tool-Specific Models

```python
class AddTaskInput(AuthenticatedInput):
    project_id: int = Field(..., description="Project ID to add task to")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=2000, description="Task description")

class TaskIdInput(AuthenticatedInput):
    """Reusable for single-task operations."""
    task_id: int = Field(..., description="Task ID to operate on")

class ProgressInput(AuthenticatedInput):
    task_id: int = Field(..., description="Task ID")
    progress_percent: int = Field(..., ge=0, le=100, description="Progress (0-100)")
    note: str | None = Field(None, max_length=500, description="Progress note")
```

---

## Tool Response Patterns

### Success Response Helper

```python
def _format_task_result(task: dict, status: str) -> str:
    return json.dumps({
        "task_id": task.get("id"),
        "status": status,
        "title": task.get("title"),
    }, indent=2)
```

### Error Response Helper

```python
def _format_error(e: APIError, task_id: int | None = None) -> str:
    result = {
        "error": True,
        "message": e.detail or e.message,
        "status_code": e.status_code,
    }
    if task_id:
        result["task_id"] = task_id
    return json.dumps(result, indent=2)
```

### Tool Implementation Pattern

```python
@mcp.tool(
    name="taskflow_add_task",
    annotations={
        "title": "Add Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def taskflow_add_task(params: AddTaskInput, ctx: Context) -> str:
    """Create a new task in a project.

    Args:
        params: AddTaskInput with user_id, project_id, title, optional description

    Returns:
        JSON with task_id, status="created", and title
    """
    try:
        client = get_api_client()
        result = await client.create_task(
            user_id=params.user_id,
            project_id=params.project_id,
            title=params.title,
            description=params.description,
            access_token=params.access_token,
        )
        return _format_task_result(result, "created")
    except APIError as e:
        return _format_error(e)
    except Exception as e:
        return json.dumps({"error": True, "message": str(e)})
```

---

## Package Structure

```
packages/mcp-server/
├── src/taskflow_mcp/
│   ├── __init__.py         # Version
│   ├── app.py              # FastMCP singleton
│   ├── server.py           # Starlette + CORS (minimal)
│   ├── config.py           # Pydantic settings
│   ├── api_client.py       # httpx REST client
│   ├── models.py           # Input validation models
│   └── tools/
│       ├── __init__.py
│       ├── tasks.py        # Task tools
│       └── projects.py     # Project tools
├── tests/
│   └── test_models.py
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Dependencies

```toml
[project]
dependencies = [
    "mcp>=1.22.0",
    "httpx>=0.28.0",
    "pydantic>=2.12.0",
    "pydantic-settings>=2.0.0",
    "starlette>=0.45.0",
    "uvicorn>=0.34.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

## Common Issues & Fixes

### Issue: Session Timeout (ClosedResourceError)

**Symptom**: `Timed out while waiting for response. Waited 5.0 seconds.`

**Cause**: Double-wrapping FastMCP app in Starlette causes session management overhead.

**Fix**: Use `mcp.streamable_http_app()` directly without additional Starlette wrapper.

### Issue: 401 Not Authenticated

**Symptom**: API returns auth errors despite passing user_id.

**Cause**: REST API expects JWT, not X-User-ID header.

**Fix**:
1. Enable dev mode on both services, OR
2. Pass `access_token` parameter from Chat Server

### Issue: Tool Not Found

**Symptom**: MCP client can't find registered tools.

**Cause**: Tool modules not imported before `streamable_http_app()` is called.

**Fix**: Import tool modules at top of server.py (side effect imports).

---

## Testing Commands

```bash
# Run tests
cd packages/mcp-server
uv run pytest -v

# Start server
uv run python -m taskflow_mcp.server

# Test with MCP Inspector
npx @modelcontextprotocol/inspector http://localhost:8001/mcp
```

---

## Source

Learned from TaskFlow MCP Server implementation (005-mcp-server).
PHRs: `history/prompts/005-mcp-server/`
