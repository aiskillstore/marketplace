#!/usr/bin/env python3
"""
Resource-Focused MCP Server Example

A Model Context Protocol server demonstrating comprehensive resource handling:
- Static resources (file system access)
- Dynamic resources (generated on-demand)
- Template resources (parameterized URIs)
- Resource metadata and discovery
- Resource caching and updates
- Multiple resource types (text, JSON, markdown)

This server provides access to:
- Documentation files
- Configuration data
- System logs
- Database schemas
- API specifications

Resources are read-only data that Claude can access. Unlike tools (which perform actions),
resources provide information for Claude to read and understand.

Usage:
    python resource-server.py

Configuration (Claude Desktop):
    {
        "mcpServers": {
            "resource-server": {
                "command": "python",
                "args": ["/absolute/path/to/resource-server.py"],
                "env": {
                    "DOCS_PATH": "/path/to/documentation",
                    "LOGS_PATH": "/path/to/logs"
                }
            }
        }
    }
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    ResourceContents,
    TextResourceContents,
    Tool,
    TextContent
)
import asyncio
import logging
import sys
import os
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Configuration
DOCS_PATH = os.getenv("DOCS_PATH", "./docs")
LOGS_PATH = os.getenv("LOGS_PATH", "./logs")
CONFIG_PATH = os.getenv("CONFIG_PATH", "./config")

# Initialize server
app = Server("resource-server")

# In-memory database schema (example data)
DATABASE_SCHEMAS = {
    "users": {
        "table": "users",
        "columns": [
            {"name": "id", "type": "INTEGER", "primary_key": True},
            {"name": "username", "type": "VARCHAR(50)", "unique": True},
            {"name": "email", "type": "VARCHAR(100)", "unique": True},
            {"name": "created_at", "type": "TIMESTAMP"}
        ]
    },
    "posts": {
        "table": "posts",
        "columns": [
            {"name": "id", "type": "INTEGER", "primary_key": True},
            {"name": "user_id", "type": "INTEGER", "foreign_key": "users.id"},
            {"name": "title", "type": "VARCHAR(200)"},
            {"name": "content", "type": "TEXT"},
            {"name": "created_at", "type": "TIMESTAMP"}
        ]
    },
    "comments": {
        "table": "comments",
        "columns": [
            {"name": "id", "type": "INTEGER", "primary_key": True},
            {"name": "post_id", "type": "INTEGER", "foreign_key": "posts.id"},
            {"name": "user_id", "type": "INTEGER", "foreign_key": "users.id"},
            {"name": "content", "type": "TEXT"},
            {"name": "created_at", "type": "TIMESTAMP"}
        ]
    }
}

# API specifications (example data)
API_ENDPOINTS = {
    "users": {
        "GET /api/users": {
            "description": "List all users",
            "parameters": {
                "page": {"type": "integer", "default": 1},
                "limit": {"type": "integer", "default": 10}
            },
            "response": {
                "type": "object",
                "properties": {
                    "users": {"type": "array"},
                    "total": {"type": "integer"}
                }
            }
        },
        "GET /api/users/:id": {
            "description": "Get user by ID",
            "parameters": {
                "id": {"type": "integer", "required": True}
            },
            "response": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "username": {"type": "string"},
                    "email": {"type": "string"}
                }
            }
        },
        "POST /api/users": {
            "description": "Create new user",
            "body": {
                "username": {"type": "string", "required": True},
                "email": {"type": "string", "required": True}
            },
            "response": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "message": {"type": "string"}
                }
            }
        }
    }
}

@app.list_resources()
async def list_resources():
    """
    List all available resources.

    Resources are organized into categories:
    - file:// - Static files from the file system
    - docs:// - Documentation files
    - schema:// - Database schemas
    - api:// - API endpoint specifications
    - logs:// - System logs
    - config:// - Configuration files
    - dynamic:// - Dynamically generated resources
    """
    logger.info("Listing available resources")

    resources: List[Resource] = []

    # 1. Documentation files (if DOCS_PATH exists)
    if os.path.exists(DOCS_PATH):
        doc_files = glob.glob(f"{DOCS_PATH}/**/*.md", recursive=True)
        for filepath in doc_files:
            rel_path = os.path.relpath(filepath, DOCS_PATH)
            uri = f"docs://{rel_path}"
            resources.append(Resource(
                uri=uri,
                name=f"Documentation: {rel_path}",
                description=f"Markdown documentation file: {rel_path}",
                mimeType="text/markdown"
            ))

    # 2. Database schemas
    for table_name in DATABASE_SCHEMAS.keys():
        uri = f"schema://database/{table_name}"
        resources.append(Resource(
            uri=uri,
            name=f"Schema: {table_name}",
            description=f"Database schema for {table_name} table",
            mimeType="application/json"
        ))

    # 3. API endpoint specifications
    for category in API_ENDPOINTS.keys():
        uri = f"api://spec/{category}"
        resources.append(Resource(
            uri=uri,
            name=f"API Spec: {category}",
            description=f"API endpoint specifications for {category}",
            mimeType="application/json"
        ))

    # 4. Log files (if LOGS_PATH exists)
    if os.path.exists(LOGS_PATH):
        log_files = glob.glob(f"{LOGS_PATH}/*.log")
        for filepath in sorted(log_files, key=os.path.getmtime, reverse=True)[:10]:
            filename = os.path.basename(filepath)
            uri = f"logs://{filename}"
            resources.append(Resource(
                uri=uri,
                name=f"Log: {filename}",
                description=f"System log file: {filename}",
                mimeType="text/plain"
            ))

    # 5. Configuration files
    config_resources = [
        Resource(
            uri="config://server",
            name="Server Configuration",
            description="Current server configuration and environment variables",
            mimeType="application/json"
        ),
        Resource(
            uri="config://database",
            name="Database Configuration",
            description="Database connection and settings",
            mimeType="application/json"
        )
    ]
    resources.extend(config_resources)

    # 6. Dynamic resources
    dynamic_resources = [
        Resource(
            uri="dynamic://system/status",
            name="System Status",
            description="Current system status and metrics",
            mimeType="application/json"
        ),
        Resource(
            uri="dynamic://stats/requests",
            name="Request Statistics",
            description="Server request statistics",
            mimeType="application/json"
        )
    ]
    resources.extend(dynamic_resources)

    # 7. Template resources (these accept parameters)
    template_resources = [
        Resource(
            uri="template://schema/{table_name}",
            name="Database Schema Template",
            description="Get schema for any table by name. Replace {table_name} with actual table name.",
            mimeType="application/json"
        ),
        Resource(
            uri="template://api/{category}",
            name="API Specification Template",
            description="Get API specs for a category. Replace {category} with actual category name.",
            mimeType="application/json"
        )
    ]
    resources.extend(template_resources)

    logger.info(f"Listed {len(resources)} resources")
    return resources

@app.read_resource()
async def read_resource(uri: str):
    """
    Read and return resource content based on URI scheme.

    Supported URI schemes:
    - docs:// - Documentation files
    - schema:// - Database schemas
    - api:// - API specifications
    - logs:// - Log files
    - config:// - Configuration data
    - dynamic:// - Dynamically generated content
    - file:// - Direct file access
    """
    logger.info(f"Reading resource: {uri}")

    try:
        # Documentation files
        if uri.startswith("docs://"):
            return await read_documentation_resource(uri)

        # Database schemas
        elif uri.startswith("schema://"):
            return await read_schema_resource(uri)

        # API specifications
        elif uri.startswith("api://"):
            return await read_api_resource(uri)

        # Log files
        elif uri.startswith("logs://"):
            return await read_log_resource(uri)

        # Configuration
        elif uri.startswith("config://"):
            return await read_config_resource(uri)

        # Dynamic resources
        elif uri.startswith("dynamic://"):
            return await read_dynamic_resource(uri)

        # Direct file access
        elif uri.startswith("file://"):
            return await read_file_resource(uri)

        # Template resources (with parameters)
        elif uri.startswith("template://"):
            raise ValueError(
                "Template URIs must be resolved with actual parameters. "
                f"Example: replace {{table_name}} in {uri} with an actual table name."
            )

        else:
            raise ValueError(f"Unknown URI scheme: {uri}")

    except FileNotFoundError as e:
        logger.error(f"Resource not found: {uri}")
        raise ValueError(f"Resource not found: {uri}") from e
    except Exception as e:
        logger.exception(f"Error reading resource {uri}")
        raise

async def read_documentation_resource(uri: str) -> ResourceContents:
    """Read documentation file"""
    # Extract path from URI (remove docs:// prefix)
    rel_path = uri[7:]
    filepath = os.path.join(DOCS_PATH, rel_path)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Documentation file not found: {rel_path}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    logger.debug(f"Read documentation: {rel_path} ({len(content)} bytes)")

    return ResourceContents(
        contents=[
            TextResourceContents(
                uri=uri,
                mimeType="text/markdown",
                text=content
            )
        ]
    )

async def read_schema_resource(uri: str) -> ResourceContents:
    """Read database schema"""
    # Extract table name from URI: schema://database/table_name
    match = re.match(r"schema://database/(\w+)", uri)
    if not match:
        raise ValueError(f"Invalid schema URI format: {uri}")

    table_name = match.group(1)

    if table_name not in DATABASE_SCHEMAS:
        raise ValueError(f"Unknown table: {table_name}")

    schema = DATABASE_SCHEMAS[table_name]

    # Format schema as readable text
    formatted_schema = format_database_schema(schema)

    return ResourceContents(
        contents=[
            TextResourceContents(
                uri=uri,
                mimeType="application/json",
                text=json.dumps(schema, indent=2)
            ),
            TextResourceContents(
                uri=f"{uri}#formatted",
                mimeType="text/plain",
                text=formatted_schema
            )
        ]
    )

def format_database_schema(schema: dict) -> str:
    """Format database schema as readable text"""
    lines = [f"Table: {schema['table']}", ""]

    for col in schema['columns']:
        line = f"  {col['name']}: {col['type']}"
        if col.get('primary_key'):
            line += " [PRIMARY KEY]"
        if col.get('unique'):
            line += " [UNIQUE]"
        if col.get('foreign_key'):
            line += f" [FOREIGN KEY -> {col['foreign_key']}]"
        lines.append(line)

    return "\n".join(lines)

async def read_api_resource(uri: str) -> ResourceContents:
    """Read API specification"""
    # Extract category from URI: api://spec/category
    match = re.match(r"api://spec/(\w+)", uri)
    if not match:
        raise ValueError(f"Invalid API URI format: {uri}")

    category = match.group(1)

    if category not in API_ENDPOINTS:
        raise ValueError(f"Unknown API category: {category}")

    endpoints = API_ENDPOINTS[category]

    # Format API spec as readable text
    formatted_spec = format_api_spec(category, endpoints)

    return ResourceContents(
        contents=[
            TextResourceContents(
                uri=uri,
                mimeType="application/json",
                text=json.dumps(endpoints, indent=2)
            ),
            TextResourceContents(
                uri=f"{uri}#formatted",
                mimeType="text/markdown",
                text=formatted_spec
            )
        ]
    )

def format_api_spec(category: str, endpoints: dict) -> str:
    """Format API specification as markdown"""
    lines = [f"# API Specification: {category}", ""]

    for endpoint, spec in endpoints.items():
        lines.append(f"## {endpoint}")
        lines.append(f"\n{spec['description']}\n")

        if 'parameters' in spec:
            lines.append("**Parameters:**")
            for param, details in spec['parameters'].items():
                required = " (required)" if details.get('required') else ""
                default = f" (default: {details['default']})" if 'default' in details else ""
                lines.append(f"- `{param}`: {details['type']}{required}{default}")
            lines.append("")

        if 'body' in spec:
            lines.append("**Request Body:**")
            for field, details in spec['body'].items():
                required = " (required)" if details.get('required') else ""
                lines.append(f"- `{field}`: {details['type']}{required}")
            lines.append("")

        if 'response' in spec:
            lines.append("**Response:**")
            lines.append(f"```json\n{json.dumps(spec['response'], indent=2)}\n```")
            lines.append("")

    return "\n".join(lines)

async def read_log_resource(uri: str) -> ResourceContents:
    """Read log file"""
    # Extract filename from URI: logs://filename.log
    filename = uri[7:]
    filepath = os.path.join(LOGS_PATH, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Log file not found: {filename}")

    # Read last 1000 lines (to avoid huge logs)
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # Get last 1000 lines
        content = "".join(lines[-1000:])

    logger.debug(f"Read log file: {filename} ({len(lines)} total lines, returning last 1000)")

    return ResourceContents(
        contents=[
            TextResourceContents(
                uri=uri,
                mimeType="text/plain",
                text=content
            )
        ]
    )

async def read_config_resource(uri: str) -> ResourceContents:
    """Read configuration data"""
    if uri == "config://server":
        config = {
            "server_name": app.name,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "docs_path": DOCS_PATH,
            "logs_path": LOGS_PATH,
            "config_path": CONFIG_PATH,
            "timestamp": datetime.now().isoformat()
        }
    elif uri == "config://database":
        config = {
            "available_schemas": list(DATABASE_SCHEMAS.keys()),
            "total_tables": len(DATABASE_SCHEMAS),
            "connection": "sqlite://example.db"
        }
    else:
        raise ValueError(f"Unknown config resource: {uri}")

    return ResourceContents(
        contents=[
            TextResourceContents(
                uri=uri,
                mimeType="application/json",
                text=json.dumps(config, indent=2)
            )
        ]
    )

async def read_dynamic_resource(uri: str) -> ResourceContents:
    """Read dynamically generated content"""
    if uri == "dynamic://system/status":
        status = {
            "timestamp": datetime.now().isoformat(),
            "server_name": app.name,
            "uptime": "N/A (stdio transport)",
            "available_resources": await count_available_resources(),
            "environment": {
                "DOCS_PATH": DOCS_PATH,
                "LOGS_PATH": LOGS_PATH,
                "CONFIG_PATH": CONFIG_PATH
            }
        }
        content = json.dumps(status, indent=2)

    elif uri == "dynamic://stats/requests":
        stats = {
            "timestamp": datetime.now().isoformat(),
            "note": "Request tracking not implemented in this example",
            "total_requests": 0
        }
        content = json.dumps(stats, indent=2)

    else:
        raise ValueError(f"Unknown dynamic resource: {uri}")

    return ResourceContents(
        contents=[
            TextResourceContents(
                uri=uri,
                mimeType="application/json",
                text=content
            )
        ]
    )

async def read_file_resource(uri: str) -> ResourceContents:
    """Read file directly (with security checks)"""
    # Remove file:// prefix
    filepath = uri[7:]

    # Security: Prevent directory traversal
    filepath = os.path.abspath(filepath)

    # Security: Only allow reading from certain directories
    allowed_paths = [
        os.path.abspath(DOCS_PATH),
        os.path.abspath(LOGS_PATH),
        os.path.abspath(CONFIG_PATH)
    ]

    if not any(filepath.startswith(allowed) for allowed in allowed_paths):
        raise PermissionError(f"Access denied: {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    # Determine mime type based on extension
    ext = os.path.splitext(filepath)[1].lower()
    mime_types = {
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".json": "application/json",
        ".log": "text/plain"
    }
    mime_type = mime_types.get(ext, "text/plain")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    return ResourceContents(
        contents=[
            TextResourceContents(
                uri=uri,
                mimeType=mime_type,
                text=content
            )
        ]
    )

async def count_available_resources() -> int:
    """Count total available resources"""
    resources = await list_resources()
    return len(resources)

# Optional: Provide tools to complement resources

@app.list_tools()
async def list_tools():
    """
    Provide tools for resource discovery and management.
    """
    return [
        Tool(
            name="list_resource_types",
            description="List all available resource types and their descriptions",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="search_resources",
            description="Search for resources by keyword in name or description",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Search keyword"
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="get_schema_info",
            description="Get information about available database schemas",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls"""
    logger.info(f"Tool called: {name}")

    if name == "list_resource_types":
        types = {
            "docs://": "Documentation files (markdown)",
            "schema://": "Database schemas (JSON)",
            "api://": "API specifications (JSON/Markdown)",
            "logs://": "System log files (text)",
            "config://": "Configuration data (JSON)",
            "dynamic://": "Dynamically generated content (JSON)",
            "file://": "Direct file access (various types)"
        }
        result = "Available Resource Types:\n\n"
        for prefix, desc in types.items():
            result += f"- {prefix}: {desc}\n"

        return [TextContent(type="text", text=result)]

    elif name == "search_resources":
        keyword = arguments["keyword"].lower()
        resources = await list_resources()

        matches = [
            r for r in resources
            if keyword in r.name.lower() or keyword in r.description.lower()
        ]

        if not matches:
            result = f"No resources found matching '{keyword}'"
        else:
            result = f"Found {len(matches)} resources matching '{keyword}':\n\n"
            for r in matches:
                result += f"- {r.name}\n  URI: {r.uri}\n  {r.description}\n\n"

        return [TextContent(type="text", text=result)]

    elif name == "get_schema_info":
        info = "Available Database Schemas:\n\n"
        for table_name, schema in DATABASE_SCHEMAS.items():
            info += f"Table: {table_name}\n"
            info += f"  Columns: {len(schema['columns'])}\n"
            info += f"  URI: schema://database/{table_name}\n\n"

        return [TextContent(type="text", text=info)]

    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}",
            isError=True
        )]

async def main():
    """Main entry point"""
    logger.info("Starting Resource Server")
    logger.info(f"Documentation path: {DOCS_PATH}")
    logger.info(f"Logs path: {LOGS_PATH}")
    logger.info(f"Config path: {CONFIG_PATH}")

    # Create example directories if they don't exist
    for path in [DOCS_PATH, LOGS_PATH, CONFIG_PATH]:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Ensured directory exists: {path}")

    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("STDIO transport initialized")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.exception("Server error")
        raise

if __name__ == "__main__":
    asyncio.run(main())
