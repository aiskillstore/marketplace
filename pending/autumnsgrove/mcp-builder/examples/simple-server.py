#!/usr/bin/env python3
"""
Simple MCP Server Example

A basic Model Context Protocol server demonstrating:
- Tool registration and implementation
- Input validation using JSON Schema
- Error handling
- Basic arithmetic operations

This server provides three calculator tools: add, subtract, and multiply.
Perfect for learning MCP fundamentals.

Usage:
    python simple-server.py

Configuration (Claude Desktop):
    {
        "mcpServers": {
            "calculator": {
                "command": "python",
                "args": ["/absolute/path/to/simple-server.py"]
            }
        }
    }
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio
import logging
import sys

# Configure logging (use stderr for stdio transport)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("simple-calculator-server")

@app.list_tools()
async def list_tools():
    """
    Register available tools with their schemas.

    Returns a list of Tool objects that Claude can call.
    Each tool has:
    - name: Unique identifier for the tool
    - description: What the tool does (helps Claude decide when to use it)
    - inputSchema: JSON Schema defining expected parameters
    """
    logger.info("Listing available tools")

    return [
        Tool(
            name="calculator_add",
            description="Add two numbers together. Returns the sum of a + b.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number to add"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number to add"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="calculator_subtract",
            description="Subtract one number from another. Returns the result of a - b.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "Number to subtract from"
                    },
                    "b": {
                        "type": "number",
                        "description": "Number to subtract"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="calculator_multiply",
            description="Multiply two numbers together. Returns the product of a * b.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number to multiply"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number to multiply"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="calculator_divide",
            description="Divide one number by another. Returns the result of a / b. Returns error if dividing by zero.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "Number to be divided (numerator)"
                    },
                    "b": {
                        "type": "number",
                        "description": "Number to divide by (denominator)"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="calculator_power",
            description="Raise a number to a power. Returns the result of base ** exponent.",
            inputSchema={
                "type": "object",
                "properties": {
                    "base": {
                        "type": "number",
                        "description": "The base number"
                    },
                    "exponent": {
                        "type": "number",
                        "description": "The exponent to raise the base to"
                    }
                },
                "required": ["base", "exponent"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """
    Handle tool execution.

    This is the main handler that routes tool calls to specific implementations.
    It receives:
    - name: The tool name from the list above
    - arguments: Dictionary matching the inputSchema

    Returns a list of TextContent objects with the result.
    """
    logger.info(f"Tool called: {name}")
    logger.debug(f"Arguments: {arguments}")

    try:
        # Route to appropriate handler based on tool name
        if name == "calculator_add":
            return await handle_add(arguments)
        elif name == "calculator_subtract":
            return await handle_subtract(arguments)
        elif name == "calculator_multiply":
            return await handle_multiply(arguments)
        elif name == "calculator_divide":
            return await handle_divide(arguments)
        elif name == "calculator_power":
            return await handle_power(arguments)
        else:
            # Unknown tool (should never happen if list_tools is correct)
            logger.error(f"Unknown tool requested: {name}")
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'",
                isError=True
            )]

    except Exception as e:
        # Catch any unexpected errors
        logger.exception(f"Error executing tool {name}")
        return [TextContent(
            type="text",
            text=f"Internal error: {str(e)}",
            isError=True
        )]

# Tool Implementation Functions

async def handle_add(arguments: dict):
    """
    Add two numbers.

    Args:
        arguments: Dict with 'a' and 'b' keys (both numbers)

    Returns:
        List containing TextContent with the result
    """
    a = arguments["a"]
    b = arguments["b"]
    result = a + b

    logger.info(f"Addition: {a} + {b} = {result}")

    return [TextContent(
        type="text",
        text=f"{a} + {b} = {result}"
    )]

async def handle_subtract(arguments: dict):
    """
    Subtract one number from another.

    Args:
        arguments: Dict with 'a' and 'b' keys (both numbers)

    Returns:
        List containing TextContent with the result
    """
    a = arguments["a"]
    b = arguments["b"]
    result = a - b

    logger.info(f"Subtraction: {a} - {b} = {result}")

    return [TextContent(
        type="text",
        text=f"{a} - {b} = {result}"
    )]

async def handle_multiply(arguments: dict):
    """
    Multiply two numbers.

    Args:
        arguments: Dict with 'a' and 'b' keys (both numbers)

    Returns:
        List containing TextContent with the result
    """
    a = arguments["a"]
    b = arguments["b"]
    result = a * b

    logger.info(f"Multiplication: {a} * {b} = {result}")

    return [TextContent(
        type="text",
        text=f"{a} * {b} = {result}"
    )]

async def handle_divide(arguments: dict):
    """
    Divide one number by another.

    Args:
        arguments: Dict with 'a' and 'b' keys (both numbers)

    Returns:
        List containing TextContent with the result or error
    """
    a = arguments["a"]
    b = arguments["b"]

    # Check for division by zero
    if b == 0:
        logger.warning(f"Division by zero attempted: {a} / {b}")
        return [TextContent(
            type="text",
            text="Error: Cannot divide by zero",
            isError=True
        )]

    result = a / b

    logger.info(f"Division: {a} / {b} = {result}")

    return [TextContent(
        type="text",
        text=f"{a} / {b} = {result}"
    )]

async def handle_power(arguments: dict):
    """
    Raise a number to a power.

    Args:
        arguments: Dict with 'base' and 'exponent' keys (both numbers)

    Returns:
        List containing TextContent with the result
    """
    base = arguments["base"]
    exponent = arguments["exponent"]

    try:
        result = base ** exponent
        logger.info(f"Power: {base} ** {exponent} = {result}")

        return [TextContent(
            type="text",
            text=f"{base} ** {exponent} = {result}"
        )]
    except OverflowError:
        # Handle cases where result is too large
        logger.error(f"Overflow in power calculation: {base} ** {exponent}")
        return [TextContent(
            type="text",
            text=f"Error: Result too large for {base} ** {exponent}",
            isError=True
        )]

async def main():
    """
    Main entry point for the MCP server.

    Sets up stdio transport and runs the server.
    The server will:
    1. Listen for MCP requests on stdin
    2. Send MCP responses on stdout
    3. Log to stderr (doesn't interfere with stdio transport)
    """
    logger.info("Starting Simple Calculator MCP Server")
    logger.info(f"Server name: {app.name}")

    try:
        # Create stdio transport (reads from stdin, writes to stdout)
        async with stdio_server() as (read_stream, write_stream):
            logger.info("STDIO transport initialized")

            # Run the MCP server
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.exception("Server error")
        raise

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
