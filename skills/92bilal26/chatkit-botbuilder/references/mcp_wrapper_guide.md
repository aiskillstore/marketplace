# MCP Tool Wrapper Guide

## Overview

MCP tool wrappers are the critical bridge between the OpenAI Agents SDK and your MCP tools. They automatically inject the `user_id` parameter, ensuring every tool call maintains user isolation.

## The Problem

### Without Wrappers

```python
# OpenAI Agent calls tool but doesn't pass user_id
agent.call_tool("add_task", {"title": "Buy milk"})

# MCP tool expects user_id as first parameter
def add_task(user_id: str, title: str):
    # ERROR: user_id is missing!
    pass
```

**Result:** Tasks created without user_id, breaking user isolation.

### With Wrappers

```python
# OpenAI Agent calls wrapper
agent.call_tool("add_task_wrapper", {"title": "Buy milk"})

# Wrapper automatically injects user_id
def add_task_wrapper(title: str):
    return add_task(user_id=user_id, title=title)  # user_id captured!

# MCP tool receives user_id
def add_task(user_id: str, title: str):
    # user_id available for database filtering
    pass
```

**Result:** Tasks created with correct user_id, isolation maintained.

## How Wrappers Work

### Closure Pattern

Wrapper functions capture `user_id` from the enclosing scope:

```python
async def respond(self, thread, input, context):
    # Extract user_id from context
    user_id = context.user_id

    # Wrapper functions capture user_id in closure
    def add_task_wrapper(title: str, description: str = None):
        """Wrapper captures user_id from enclosing scope"""
        return mcp_add_task(
            user_id=user_id,  # Captured from outer scope
            title=title,
            description=description
        )

    # Pass wrapper to agent
    agent = create_task_agent(tools=[add_task_wrapper, ...])

    # Agent calls wrapper with only {title, description}
    # Wrapper adds user_id before calling mcp_add_task
```

## Complete Wrapper Set

### 1. Add Task Wrapper

```python
def add_task_wrapper(title: str, description: str = None):
    """Add a task with automatic user isolation

    Args:
        title: Task title (required)
        description: Task description (optional)

    Returns:
        Created task with id and confirmation message
    """
    logger.info(f"add_task called for user {user_id}")
    return mcp_add_task(user_id=user_id, title=title, description=description)
```

### 2. List Tasks Wrapper

```python
def list_tasks_wrapper(status: str = "all"):
    """List tasks with automatic user isolation

    Args:
        status: Filter by status ('all', 'pending', 'completed')

    Returns:
        List of tasks for the user with counts and message
    """
    logger.info(f"list_tasks called for user {user_id}")
    return mcp_list_tasks(user_id=user_id, status=status)
```

### 3. Find Task By Name Wrapper

```python
def find_task_by_name_wrapper(name: str):
    """Find a task by name with automatic user isolation

    Args:
        name: Task name or partial name to search for

    Returns:
        Matching task with id, title, and description
    """
    logger.info(f"find_task_by_name called for user {user_id}")
    return mcp_find_task_by_name(user_id=user_id, name=name)
```

### 4. Complete Task Wrapper

```python
def complete_task_wrapper(task_id: str):
    """Mark a task as complete with automatic user isolation

    Args:
        task_id: ID of the task to mark complete

    Returns:
        Updated task with completion status
    """
    logger.info(f"complete_task called for user {user_id}")
    return mcp_complete_task(user_id=user_id, task_id=task_id)
```

### 5. Delete Task Wrapper

```python
def delete_task_wrapper(task_id: str):
    """Delete a task with automatic user isolation

    Args:
        task_id: ID of the task to delete

    Returns:
        Confirmation message
    """
    logger.info(f"delete_task called for user {user_id}")
    return mcp_delete_task(user_id=user_id, task_id=task_id)
```

### 6. Update Task Wrapper

```python
def update_task_wrapper(task_id: str, title: str = None, description: str = None):
    """Update a task with automatic user isolation

    Args:
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Updated task with new values
    """
    logger.info(f"update_task called for user {user_id}")
    return mcp_update_task(
        user_id=user_id,
        task_id=task_id,
        title=title,
        description=description
    )
```

## Integration in ChatKit Server

```python
class MyChatKitServer(ChatKitServer):
    async def respond(self, thread, input, context):
        # Extract user_id
        user_id = getattr(context, 'user_id', None)

        # Import original MCP tools
        from mcp.tools import (
            add_task as mcp_add_task,
            list_tasks as mcp_list_tasks,
            delete_task as mcp_delete_task,
            complete_task as mcp_complete_task,
            update_task as mcp_update_task,
            find_task_by_name as mcp_find_task_by_name,
        )

        # Create wrappers with closure capturing user_id
        def add_task_wrapper(title: str, description: str = None):
            return mcp_add_task(user_id=user_id, title=title, description=description)

        def list_tasks_wrapper(status: str = "all"):
            return mcp_list_tasks(user_id=user_id, status=status)

        def delete_task_wrapper(task_id: str):
            return mcp_delete_task(user_id=user_id, task_id=task_id)

        def complete_task_wrapper(task_id: str):
            return mcp_complete_task(user_id=user_id, task_id=task_id)

        def update_task_wrapper(task_id: str, title: str = None, description: str = None):
            return mcp_update_task(user_id=user_id, task_id=task_id, title=title, description=description)

        def find_task_by_name_wrapper(name: str):
            return mcp_find_task_by_name(user_id=user_id, name=name)

        # Register wrapped tools with agent
        wrapped_tools = [
            add_task_wrapper,
            list_tasks_wrapper,
            delete_task_wrapper,
            complete_task_wrapper,
            update_task_wrapper,
            find_task_by_name_wrapper,
        ]

        # Create agent with wrapped tools
        task_agent = create_task_agent(tools=wrapped_tools)

        # Rest of the respond() implementation...
```

## Why Wrappers Are Necessary

### Reason 1: OpenAI Agent SDK Design

The official OpenAI Agents SDK is domain-agnostic. It:
- Doesn't know about your authentication
- Doesn't know about your user context
- Calls tools with only the parameters from the user's message

### Reason 2: MCP Tool Signature

Your MCP tools expect `user_id`:

```python
def add_task(user_id: str, title: str, description: Optional[str] = None):
    # Always expects user_id as first parameter for isolation
    pass
```

### Reason 3: Context Propagation

User ID needs to be available from the HTTP request all the way to the database query:

```
Request Header (Authorization: Bearer <JWT>)
    ↓
JWT Middleware (extract user_id)
    ↓
ChatKit Server (capture user_id in wrapper closure)
    ↓
Agent Tool Call (wrapper injects user_id)
    ↓
MCP Tool (receives and uses user_id)
    ↓
Database Query (filters by user_id)
```

## Creating Wrappers Programmatically

### Pattern 1: Manual Wrapper Creation (Recommended)

Most straightforward and explicit:

```python
def add_task_wrapper(title: str, description: str = None):
    return mcp_add_task(user_id=user_id, title=title, description=description)
```

### Pattern 2: Using functools.partial

```python
from functools import partial

add_task_wrapper = partial(mcp_add_task, user_id=user_id)
```

**Note:** functools.partial doesn't work well with agent SDK tool introspection.

### Pattern 3: Dynamic Wrapper Factory

```python
def create_wrapper(tool_func, user_id):
    def wrapper(*args, **kwargs):
        kwargs['user_id'] = user_id
        return tool_func(*args, **kwargs)
    return wrapper

add_task_wrapper = create_wrapper(mcp_add_task, user_id)
```

**Best practice:** Use manual wrapper creation for clarity.

## Testing Wrappers

### Unit Test Example

```python
def test_add_task_wrapper():
    """Test that wrapper injects user_id"""
    user_id = "test-user-123"

    def mcp_add_task(user_id, title, description=None):
        return {"task_id": "1", "user_id": user_id, "title": title}

    def add_task_wrapper(title, description=None):
        return mcp_add_task(user_id=user_id, title=title, description=description)

    result = add_task_wrapper("Buy milk")

    assert result["user_id"] == "test-user-123"
    assert result["title"] == "Buy milk"
    print("✓ Wrapper correctly injects user_id")
```

### Integration Test Example

```python
async def test_chatkit_respects_user_isolation():
    """Test that ChatKit tool calls maintain user isolation"""
    # Setup
    user_1_id = "user-1"
    user_2_id = "user-2"

    # User 1 creates task
    response_1 = await chatkit_server.respond(
        thread=thread_1,
        input=UserMessageItem(content="Create task 'Buy milk'"),
        context=create_context(user_id=user_1_id)
    )

    # User 2 lists tasks
    response_2 = await chatkit_server.respond(
        thread=thread_2,
        input=UserMessageItem(content="List all tasks"),
        context=create_context(user_id=user_2_id)
    )

    # Verify user 2 cannot see user 1's tasks
    assert "Buy milk" not in response_2
    print("✓ User isolation maintained")
```

## Debugging Wrapper Issues

### Issue 1: "user_id not defined" Error

**Problem:**
```python
def add_task_wrapper(title):
    return mcp_add_task(user_id=user_id, ...)  # NameError: user_id not defined
```

**Solution:**
Ensure wrapper is defined inside the function that has `user_id` in scope:

```python
async def respond(self, thread, input, context):
    user_id = context.user_id  # Define here

    def add_task_wrapper(title):  # Define wrapper here
        return mcp_add_task(user_id=user_id, ...)  # Now user_id is accessible
```

### Issue 2: Wrapper Not Called by Agent

**Problem:**
Agent doesn't call the wrapper function.

**Symptoms:**
- User message has no effect
- No tool calls in logs
- Tool response missing from chat

**Solution:**
- Check agent instructions mention the tool
- Verify wrapper function is in tools list
- Check function signature matches expected parameters
- Add logging to verify agent sees the wrapper

### Issue 3: Wrong User ID in Tasks

**Problem:**
Tasks created with wrong user_id.

**Symptoms:**
- User A creates task, appears for User B
- User isolation broken

**Cause:**
Wrapper not properly capturing user_id.

**Solution:**
```python
# WRONG: Wrapper defined outside respond()
def add_task_wrapper(title):  # user_id not in scope
    return mcp_add_task(user_id=user_id, ...)

# RIGHT: Wrapper defined inside respond()
async def respond(self, thread, input, context):
    user_id = context.user_id

    def add_task_wrapper(title):  # user_id captured in closure
        return mcp_add_task(user_id=user_id, ...)
```

## Performance Considerations

### Wrapper Overhead

- **Minimal**: Wrappers are just function calls with parameter injection
- **No database queries**: Only passes parameters through
- **No serialization**: Works with native Python objects

### Optimization Tips

1. **Create wrappers once per request** - Don't recreate in loops
2. **Import tools at top of file** - Not inside wrapper
3. **Use logging sparingly** - Log only important events
4. **Cache agent if possible** - Don't recreate for every message

```python
# Good: Create wrappers once per respond()
async def respond(self, thread, input, context):
    user_id = context.user_id

    # Create wrappers once
    def add_task_wrapper(title):
        return mcp_add_task(user_id=user_id, title=title)

    tools = [add_task_wrapper, ...]  # Use once per request
    agent = create_task_agent(tools=tools)

    # Use agent for this single request
```

## Checklist for Wrapper Implementation

- [ ] Wrappers defined inside respond() method
- [ ] user_id extracted from context before defining wrappers
- [ ] All MCP tools wrapped with user_id injection
- [ ] Wrappers have clear docstrings
- [ ] Wrapper parameter names match MCP tool names
- [ ] Wrapper signatures match what agent expects
- [ ] Wrappers passed to create_task_agent()
- [ ] Logging added to trace tool calls
- [ ] User isolation verified in tests
- [ ] Performance acceptable (< 100ms overhead)
