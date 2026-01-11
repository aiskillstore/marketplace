# Database Query Server Example

## Overview
MCP server providing safe database query access with read-only operations and proper security controls.

## Complete Implementation

```python
import sqlite3
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json
import asyncio

app = Server("database-server")

# Initialize database connection
conn = sqlite3.connect('app.db')
conn.row_factory = sqlite3.Row  # Enable column access by name

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="execute_query",
            description="Execute read-only SQL query on the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 1000
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_schema",
            description="Get database schema information for tables",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Optional: specific table name to inspect"
                    }
                }
            }
        ),
        Tool(
            name="table_stats",
            description="Get statistics about a database table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to analyze"
                    }
                },
                "required": ["table_name"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "execute_query":
        return await handle_execute_query(arguments)
    elif name == "get_schema":
        return await handle_get_schema(arguments)
    elif name == "table_stats":
        return await handle_table_stats(arguments)
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}",
            isError=True
        )]

async def handle_execute_query(arguments: dict):
    """Execute read-only SQL query"""
    query = arguments["query"]
    limit = arguments.get("limit", 100)

    # Security: Only allow SELECT queries
    if not query.strip().upper().startswith("SELECT"):
        return [TextContent(
            type="text",
            text="Error: Only SELECT queries are allowed for security reasons",
            isError=True
        )]

    # Additional security: Check for dangerous keywords
    dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']
    query_upper = query.upper()
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return [TextContent(
                type="text",
                text=f"Error: Query contains forbidden keyword: {keyword}",
                isError=True
            )]

    try:
        cursor = conn.cursor()
        cursor.execute(f"{query} LIMIT {limit}")
        rows = cursor.fetchall()

        # Convert to list of dicts
        results = [dict(row) for row in rows]

        if not results:
            return [TextContent(
                type="text",
                text="Query executed successfully but returned no results"
            )]

        # Format results
        result_text = f"Found {len(results)} result(s):\n\n"
        result_text += json.dumps(results, indent=2, default=str)

        return [TextContent(type="text", text=result_text)]

    except sqlite3.Error as e:
        return [TextContent(
            type="text",
            text=f"Database error: {str(e)}",
            isError=True
        )]

async def handle_get_schema(arguments: dict):
    """Get database schema information"""
    table_name = arguments.get("table_name")

    try:
        cursor = conn.cursor()

        if table_name:
            # Get specific table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            if not columns:
                return [TextContent(
                    type="text",
                    text=f"Table '{table_name}' not found",
                    isError=True
                )]

            schema = {
                "table": table_name,
                "columns": [
                    {
                        "name": col["name"],
                        "type": col["type"],
                        "nullable": not col["notnull"],
                        "default": col["dflt_value"],
                        "primary_key": bool(col["pk"])
                    }
                    for col in columns
                ]
            }
        else:
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            schema = {"tables": tables}

        return [TextContent(
            type="text",
            text=json.dumps(schema, indent=2)
        )]

    except sqlite3.Error as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}",
            isError=True
        )]

async def handle_table_stats(arguments: dict):
    """Get statistics about a table"""
    table_name = arguments["table_name"]

    try:
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        if not cursor.fetchone():
            return [TextContent(
                type="text",
                text=f"Table '{table_name}' not found",
                isError=True
            )]

        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]

        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        stats = {
            "table_name": table_name,
            "row_count": row_count,
            "column_count": len(columns),
            "columns": [col["name"] for col in columns]
        }

        return [TextContent(
            type="text",
            text=f"Table Statistics:\n{json.dumps(stats, indent=2)}"
        )]

    except sqlite3.Error as e:
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
    try:
        asyncio.run(main())
    finally:
        conn.close()
```

## Security Features
- **Read-only access**: Only SELECT queries allowed
- **Keyword filtering**: Blocks dangerous SQL keywords
- **Query limits**: Maximum result count enforced
- **Parameterized where possible**: Uses parameterized queries for metadata

## Usage Examples

```
"Show me the database schema"
"Query the users table"
"Get stats for the orders table"
"Find all users where status is active"
```

## Production Considerations
- Add connection pooling for concurrent queries
- Implement query timeout limits
- Add more sophisticated SQL parsing/validation
- Consider using prepared statements
- Implement audit logging
