# Simple Calculator Server Example

## Overview
Basic MCP server demonstrating simple arithmetic tools with proper structure and error handling.

## Complete Implementation

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

# Initialize server
app = Server("calculator-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="calculator_add",
            description="Add two numbers and return the result",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="calculator_multiply",
            description="Multiply two numbers and return the result",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Route tool calls to appropriate handlers"""
    if name == "calculator_add":
        return await handle_add(arguments)
    elif name == "calculator_multiply":
        return await handle_multiply(arguments)
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}",
            isError=True
        )]

async def handle_add(arguments: dict):
    """Add two numbers"""
    try:
        a = float(arguments["a"])
        b = float(arguments["b"])
        result = a + b
        return [TextContent(
            type="text",
            text=f"{a} + {b} = {result}"
        )]
    except (ValueError, KeyError) as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}",
            isError=True
        )]

async def handle_multiply(arguments: dict):
    """Multiply two numbers"""
    try:
        a = float(arguments["a"])
        b = float(arguments["b"])
        result = a * b
        return [TextContent(
            type="text",
            text=f"{a} × {b} = {result}"
        )]
    except (ValueError, KeyError) as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}",
            isError=True
        )]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing the Server

```bash
# Test with MCP inspector
npx @modelcontextprotocol/inspector python calculator_server.py
```

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": ["/absolute/path/to/calculator_server.py"]
    }
  }
}
```

## Key Takeaways
- Simple tool registration pattern
- Clear error handling
- Type conversion with validation
- Meaningful result messages
