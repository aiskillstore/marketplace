# MCP Builder - Model Context Protocol Server Development

Comprehensive guide for building Model Context Protocol (MCP) servers with support for tools, resources, prompts, and authentication.

## What is MCP?

Model Context Protocol (MCP) is an open standard created by Anthropic that enables AI assistants like Claude to securely connect to external data sources and tools. Think of it as a universal adapter that allows Claude to interact with any system, API, or data source through a standardized interface.

**Key Benefits:**
- **Standardization**: One protocol for all integrations
- **Security**: Built-in authentication and permission controls
- **Flexibility**: Support for tools, resources, and prompts
- **Scalability**: Designed for production workloads
- **Modularity**: Create reusable MCP servers for different domains

## Installation

Create your MCP server project:

```bash
# Create project directory
mkdir my-mcp-server
cd my-mcp-server

# Initialize Python project
uv init
uv add mcp

# Create server file
touch server.py
```

## What's Included

### SKILL.md
Comprehensive guide covering MCP architecture, protocol specification, server implementation workflows, tool/resource/prompt development, authentication methods, best practices, and common pitfalls.

### examples/
- `simple-calculator-server.md` - Basic arithmetic tools
- `rest-api-wrapper.md` - GitHub API integration
- `database-server.md` - Safe database query access
- `resource-server.md` - Static and dynamic resources

### references/
- `protocol-specification.md` - Complete protocol details and message formats
- `tool-schemas.md` - Comprehensive schema patterns and validation
- `security-guide.md` - Authentication, authorization, input validation
- `testing-debugging.md` - Unit tests, integration tests, MCP inspector
- `production-deployment.md` - Production configuration, monitoring, scaling

## Quick Start

### Minimal Working Server

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

app = Server("my-mcp-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="my_tool",
            description="Description of what this tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                },
                "required": ["param"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "my_tool":
        param = arguments["param"]
        result = f"Processed: {param}"
        return [TextContent(type="text", text=result)]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### Testing Your Server

```bash
# Test with MCP inspector
npx @modelcontextprotocol/inspector python server.py
```

### Claude Desktop Integration

Edit `claude_desktop_config.json`:
- macOS: `~/Library/Application Support/Claude/`
- Windows: `%APPDATA%\Claude/`
- Linux: `~/.config/Claude/`

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"],
      "env": {"API_KEY": "your-key"}
    }
  }
}
```

## Core Components

### 1. Tools: Exposing Functions Claude Can Call

Tools are the primary way to give Claude new capabilities. Each tool is a function that Claude can invoke with specific arguments.

**Key Principles:**
- **Clear naming**: Use descriptive, action-oriented names (e.g., `search_database`, not `db_query`)
- **Comprehensive descriptions**: Explain what the tool does, when to use it, and what it returns
- **Strong schemas**: Use JSON Schema to validate inputs and guide Claude
- **Error handling**: Return clear error messages when things go wrong

**Example:**
```python
Tool(
    name="search_customer_by_email",
    description="""
    Search for customers by email address. Returns customer profile including:
    - Contact information
    - Order history
    - Account status
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "format": "email",
                "description": "Customer email address"
            }
        },
        "required": ["email"]
    }
)
```

For complete schema design patterns, see `references/tool-schemas.md`.

### 2. Resources: Providing Data/Documentation Access

Resources allow Claude to access files, documentation, or structured data. Unlike tools (which perform actions), resources provide information.

**Resource Types:**
- **Static**: Fixed content (e.g., documentation files)
- **Dynamic**: Generated on-demand (e.g., database queries)
- **Templates**: Parameterized resources (e.g., user profiles)

### 3. Prompts: Reusable Prompt Templates

Prompts are pre-defined message templates that users can invoke to standardize common workflows.

### 4. Authentication Methods

MCP supports multiple authentication methods:
- **No Authentication** (development only)
- **API Key Authentication** (simple, medium security)
- **OAuth 2.0** (third-party, high security)
- **Bearer Token** (API-to-API, high security)

For complete security implementation, see `references/security-guide.md`.

## Architecture Overview

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   Claude    │ ←──MCP──→ │ MCP Server  │ ←──────→ │ External API │
│  (Client)   │         │  (Your Code) │         │  Database    │
└─────────────┘         └─────────────┘         └──────────────┘
```

**Components:**
- **Client**: Claude Desktop, Claude Code, or custom applications
- **Server**: Your MCP implementation (Python, TypeScript, etc.)
- **Transport**: Communication channel (stdio, HTTP, SSE)
- **Protocol**: Standardized message format (JSON-RPC 2.0)

## Server Implementation Workflow

### Phase 1: Project Setup
Create project directory and initialize dependencies

### Phase 2: Basic Server Structure
Implement minimal working server with one tool

### Phase 3: Tool Registration and Handlers
Add multiple tools with proper input schemas

### Phase 4: Resource Implementation
Add static and dynamic resource support

### Phase 5: Error Handling and Testing
Implement comprehensive error handling and test with MCP inspector

### Phase 6: Claude Desktop Integration
Configure Claude Desktop to use your server

For detailed step-by-step instructions, see `SKILL.md`.

## Best Practices

### Tool Schema Design

**Use descriptive names:**
```python
# ✅ Good
"search_customer_by_email"
"calculate_shipping_cost"

# ❌ Bad
"search"
"calc"
```

**Provide comprehensive descriptions:**
```python
# ✅ Good
description="""
Search for customers by email address. Returns customer profile including:
- Contact information
- Order history
- Account status
"""

# ❌ Bad
description="Search customers"
```

**Use enums for fixed options:**
```python
# ✅ Good
"status": {
    "type": "string",
    "enum": ["pending", "approved", "rejected"],
    "description": "Application status"
}
```

### Error Handling

```python
async def call_tool(name: str, arguments: dict):
    try:
        return await execute_tool(name, arguments)
    except ValueError as e:
        return [TextContent(type="text", text=f"Invalid input: {str(e)}", isError=True)]
    except Exception as e:
        logger.exception("Unexpected error")
        return [TextContent(type="text", text=f"Error: {type(e).__name__}", isError=True)]
```

### Security Considerations

```python
# Input validation
def validate_url(url: str) -> bool:
    if urlparse(url).scheme not in ['http', 'https']:
        raise ValidationError("Only HTTP/HTTPS URLs allowed")

# Secrets management
API_KEY = os.getenv("API_KEY")  # ✅ Good
# API_KEY = "sk-1234"  # ❌ Bad - Never hardcode!
```

## Common Pitfalls

### Schema Validation Errors
```python
# ❌ Bad: No validation
async def handle_create_user(arguments: dict):
    username = arguments["username"]  # Will crash if missing!

# ✅ Good: Validate inputs
async def handle_create_user(arguments: dict):
    if "username" not in arguments:
        return [TextContent(type="text", text="Error: username required", isError=True)]
    username = arguments["username"]
```

### Authentication Issues
```python
# ❌ Bad: Hardcoded API key
API_KEY = "sk-1234567890abcdef"

# ✅ Good: Environment variables
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable required")
```

### Transport Configuration
```python
# ❌ Bad: Relative path
{
  "command": "python",
  "args": ["server.py"]  # Won't work!
}

# ✅ Good: Absolute path
{
  "command": "python",
  "args": ["/Users/username/projects/mcp-server/server.py"]
}
```

## Use Cases

### Creating Custom MCP Servers
Build specialized servers for your APIs, databases, or internal tools.

### Integrating External APIs with Claude
Wrap REST APIs to make them accessible to Claude.

### Building Tool Servers for Specialized Domains
Create domain-specific toolsets (finance, healthcare, engineering).

### Creating Resource Providers for Documentation
Provide Claude with access to your documentation or knowledge base.

## Documentation

See `SKILL.md` for comprehensive documentation, detailed workflows, and advanced techniques.

## External Resources

- MCP Specification: https://modelcontextprotocol.io/
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- MCP Inspector: https://github.com/modelcontextprotocol/inspector
- Claude Desktop: https://claude.ai/download

## Requirements

- Python 3.10+
- mcp (Python SDK)
- asyncio support
- Claude Desktop or compatible MCP client
