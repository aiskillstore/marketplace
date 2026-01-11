# MCP Testing Patterns

Patterns for testing MCP servers.

## Manual Test Script

```python
# test_server.py
import asyncio
from my_server.server import app

async def test_tools():
    tools = await app.list_tools()
    print(f"Available tools: {[t['name'] for t in tools]}")

    result = await app.call_tool("my_tool", {"query": "test"})
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_tools())
```

## pytest with Async

```python
import pytest
from my_server.tools import handle_search

@pytest.mark.asyncio
async def test_search_returns_results():
    result = await handle_search({"query": "test", "limit": 5})
    assert "content" in result
    assert len(result["content"]) > 0

@pytest.mark.asyncio
async def test_search_handles_empty():
    result = await handle_search({"query": "xyznonexistent123"})
    assert result["content"][0]["text"] == "No results found"
```
