# MCP Tool Patterns

Extended patterns for MCP tool implementation.

## Tool with Validation

```python
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=100)

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search":
        # Pydantic validates and parses
        params = SearchInput(**arguments)
        results = await search(params.query, params.limit)
        return {"content": [{"type": "text", "text": json.dumps(results)}]}
```

## Tool with Error Handling

```python
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "fetch_data":
            data = await fetch_data(arguments["url"])
            return {"content": [{"type": "text", "text": data}]}
    except httpx.HTTPStatusError as e:
        return {
            "content": [{"type": "text", "text": f"HTTP error: {e.response.status_code}"}],
            "isError": True
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }
```

## Multiple Tool Registration

```python
TOOLS = {
    "list_items": {
        "description": "List all items",
        "schema": {"type": "object", "properties": {}},
        "handler": handle_list_items
    },
    "get_item": {
        "description": "Get specific item",
        "schema": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"]
        },
        "handler": handle_get_item
    },
    "create_item": {
        "description": "Create new item",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "data": {"type": "object"}
            },
            "required": ["name"]
        },
        "handler": handle_create_item
    }
}

@app.list_tools()
async def list_tools():
    return [
        {"name": name, "description": t["description"], "inputSchema": t["schema"]}
        for name, t in TOOLS.items()
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name not in TOOLS:
        raise ValueError(f"Unknown tool: {name}")
    return await TOOLS[name]["handler"](arguments)
```
