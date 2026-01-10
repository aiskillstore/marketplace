# ChatKit Backend Architecture

## Overview

This document describes the complete architecture for building a ChatKit backend using FastAPI, OpenAI Agents SDK, and MCP tools.

## Complete Backend Implementation

### 1. JWT Authentication Middleware

```python
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt
from config import settings

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        public_paths = ["/auth/", "/health", "/docs", "/openapi.json"]
        if request.method == "OPTIONS" or any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse({"detail": "Missing authorization header"}, status_code=401)

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return JSONResponse({"detail": "Invalid auth scheme"}, status_code=401)

            # Handle test tokens for development
            if settings.ENVIRONMENT == "development" and token.startswith("test-token-"):
                user_id = token.replace("test-token-", "")
                request.state.user_id = user_id
                return await call_next(request)

            # Decode JWT token
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("user_id")
            if not user_id:
                return JSONResponse({"detail": "Invalid token"}, status_code=401)

            request.state.user_id = user_id
        except Exception as e:
            return JSONResponse({"detail": str(e)}, status_code=401)

        return await call_next(request)
```

### 2. ChatKit Server Implementation

```python
from chatkit.server import ChatKitServer
from chatkit.store import Store
from chatkit.types import ThreadMetadata, UserMessageItem, Page, ErrorEvent
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from agents import Runner

class CustomChatKitStore(Store):
    """In-memory store for ChatKit thread persistence"""

    def __init__(self):
        self.threads = {}
        self.items = {}

    async def load_thread(self, thread_id: str, context) -> ThreadMetadata:
        if thread_id in self.threads:
            return self.threads[thread_id]
        return ThreadMetadata(
            id=thread_id,
            created_at=datetime.utcnow(),
            metadata={},
        )

    async def save_thread(self, thread: ThreadMetadata, context) -> None:
        self.threads[thread.id] = thread

    async def load_thread_items(self, thread_id: str, after: str | None, limit: int, order: str, context):
        items = self.items.get(thread_id, [])
        items.sort(key=lambda i: i.created_at, reverse=(order == "desc"))

        if after:
            after_index = next((i for i, item in enumerate(items) if item.id == after), -1)
            if after_index >= 0:
                items = items[after_index + 1:]

        has_more = len(items) > limit
        items = items[:limit]

        return Page(data=items, has_more=has_more, after=items[-1].id if items else None)

    async def add_thread_item(self, thread_id: str, item, context) -> None:
        if thread_id not in self.items:
            self.items[thread_id] = []
        self.items[thread_id].append(item)

    # ... implement other required methods ...


class MyChatKitServer(ChatKitServer):
    """ChatKit server with agent integration"""

    def __init__(self):
        store = CustomChatKitStore()
        super().__init__(store=store)

    async def respond(self, thread: ThreadMetadata, input: UserMessageItem, context) -> AsyncIterator:
        try:
            # Extract user_id from context (set by JWT middleware)
            user_id = getattr(context, 'user_id', None) or context.headers.get("X-User-ID")
            if not user_id:
                yield ErrorEvent(level='danger', message="Authentication required")
                return

            logger.info(f"ChatKit respond: user={user_id}, thread={thread.id}")

            # Add user message to thread
            await self.store.add_thread_item(thread.id, input, context)

            # Load conversation history
            items_page = await self.store.load_thread_items(
                thread.id, after=None, limit=30, order="desc", context=context
            )
            items = list(reversed(items_page.data))
            agent_input = await simple_to_agent_input(items)

            # Initialize MCP tools with user_id injection
            mcp_server = initialize_mcp_server()

            # Create wrapper functions that inject user_id
            def add_task_wrapper(title: str, description: str = None):
                return mcp_add_task(user_id=user_id, title=title, description=description)

            def list_tasks_wrapper(status: str = "all"):
                return mcp_list_tasks(user_id=user_id, status=status)

            def delete_task_wrapper(task_id: str):
                return mcp_delete_task(user_id=user_id, task_id=task_id)

            # ... create wrappers for all tools ...

            wrapped_tools = [
                add_task_wrapper,
                list_tasks_wrapper,
                delete_task_wrapper,
                # ... all wrapped tools ...
            ]

            # Create agent with wrapped tools
            task_agent = create_task_agent(tools=wrapped_tools)

            # Create agent context
            agent_context = AgentContext(
                thread=thread,
                store=self.store,
                request_context=context,
            )

            # Stream agent response
            result = Runner.run_streamed(
                task_agent.agent,
                agent_input,
                context=agent_context,
            )

            # Yield events
            async for event in stream_agent_response(agent_context, result):
                yield event

        except Exception as e:
            logger.error(f"Error in respond: {str(e)}", exc_info=True)
            yield ErrorEvent(level='danger', message=f"Error: {str(e)}")
```

### 3. FastAPI Endpoint

```python
from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session

router = APIRouter()
chatkit_server = MyChatKitServer()

@router.post("/api/v1/chatkit")
async def chatkit_protocol_endpoint(
    request: Request,
    db_session: Session = Depends(get_session)
):
    """ChatKit protocol endpoint"""
    try:
        # Extract user_id from auth middleware
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            user_id = request.headers.get("X-User-ID")

        logger.info(f"ChatKit protocol request from user: {user_id}")

        # Get request body
        body = await request.body()

        # Create context with user_id
        context = type('Context', (), {
            'user_id': user_id,
            'request': request,
            'db_session': db_session
        })()

        # Process through ChatKit server
        result = await chatkit_server.process(body, context)

        # Handle streaming responses
        from chatkit.server import StreamingResult
        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")

        # Handle regular responses
        if hasattr(result, 'json'):
            return Response(content=result.json, media_type="application/json")

        return JSONResponse(result)

    except Exception as e:
        logger.error(f"ChatKit protocol error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

### 4. MCP Tool Registration

```python
from mcp.tools import add_task, list_tasks, delete_task, complete_task, update_task, find_task_by_name

class MCPServer:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name: str, tool) -> None:
        self.tools[name] = tool

    def get_tools(self):
        return self.tools

def initialize_mcp_server() -> MCPServer:
    mcp_server = MCPServer()

    mcp_server.register_tool("add_task", add_task)
    mcp_server.register_tool("list_tasks", list_tasks)
    mcp_server.register_tool("find_task_by_name", find_task_by_name)
    mcp_server.register_tool("complete_task", complete_task)
    mcp_server.register_tool("delete_task", delete_task)
    mcp_server.register_tool("update_task", update_task)

    logger.info(f"Registered tools: {list(mcp_server.get_tools().keys())}")
    return mcp_server
```

## Key Architecture Principles

### 1. User Isolation Through Three Levels

**Middleware Level:**
- JWT validation ensures only authenticated users
- Extract user_id from token → request.state.user_id

**Tool Level:**
- Wrapper functions capture user_id from context closure
- Automatically inject user_id into every tool call
- Prevents accidental user_id omissions

**Database Level:**
- All queries filter by user_id
- Enforces data isolation at storage layer

### 2. Context Propagation

```
Request Headers (Authorization: Bearer <JWT>)
    ↓
JWT Middleware (extract user_id)
    ↓
request.state.user_id = user_id
    ↓
ChatKit Endpoint (create context object)
    ↓
context.user_id = user_id
    ↓
MyChatKitServer.respond(context)
    ↓
Wrapper functions capture user_id
    ↓
Tool calls include user_id
```

### 3. Tool Wrapper Pattern

Why wrappers are necessary:

1. **OpenAI Agents SDK** calls tools without domain context
2. **MCP Tools** expect user_id as first parameter
3. **Wrappers bridge** this gap by capturing user_id in closure

```python
# Without wrapper: user_id not available
agent.call_tool("add_task", {"title": "Buy milk"})  # Missing user_id!

# With wrapper: user_id automatically injected
agent.call_tool("add_task_wrapper", {"title": "Buy milk"})
    ↓
def add_task_wrapper(title):
    return add_task(user_id=user_id, title=title)  # user_id captured!
```

## Implementation Checklist

- [ ] JWT middleware configured in FastAPI app
- [ ] CustomChatKitStore implemented with all required methods
- [ ] MyChatKitServer extends ChatKitServer correctly
- [ ] Tool wrappers capture and inject user_id
- [ ] ChatKit endpoint registered in router
- [ ] Router included in FastAPI app
- [ ] MCP tools registered with MCPServer
- [ ] Agent context includes user_id
- [ ] Streaming response handled correctly
- [ ] Error handling yields ErrorEvent

## Testing the Backend

```bash
# Test ChatKit endpoint
curl -X POST http://localhost:8000/api/v1/chatkit \
  -H "Authorization: Bearer test-token-user-123" \
  -H "Content-Type: application/json" \
  -d '{...chatkit protocol payload...}'

# Check logs for user_id extraction
# Check database for tasks created with correct user_id
```
