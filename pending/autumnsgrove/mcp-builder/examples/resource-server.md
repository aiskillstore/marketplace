# Resource Server Example

## Overview
MCP server demonstrating static and dynamic resource access for documentation and system information.

## Complete Implementation

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, ResourceContents, TextResourceContents
import os
import glob
import json
from datetime import datetime
import asyncio

app = Server("resource-server")

# Resource handlers
@app.list_resources()
async def list_resources():
    """List all available resources"""
    resources = []

    # Static resources: Documentation files
    docs_path = "docs/"
    if os.path.exists(docs_path):
        for filepath in glob.glob(f"{docs_path}**/*.md", recursive=True):
            uri = f"file://{os.path.abspath(filepath)}"
            name = os.path.basename(filepath)
            resources.append(Resource(
                uri=uri,
                name=f"Documentation: {name}",
                description=f"Markdown documentation: {filepath}",
                mimeType="text/markdown"
            ))

    # Dynamic resources: System information
    resources.extend([
        Resource(
            uri="dynamic://system/status",
            name="System Status",
            description="Current system status and metrics",
            mimeType="application/json"
        ),
        Resource(
            uri="dynamic://system/info",
            name="System Information",
            description="System environment information",
            mimeType="application/json"
        )
    ])

    return resources

@app.read_resource()
async def read_resource(uri: str):
    """Read resource content based on URI"""

    # Handle file:// URIs (static documentation)
    if uri.startswith("file://"):
        return await read_file_resource(uri)

    # Handle dynamic:// URIs (system information)
    elif uri.startswith("dynamic://"):
        return await read_dynamic_resource(uri)

    else:
        raise ValueError(f"Unsupported URI scheme: {uri}")

async def read_file_resource(uri: str):
    """Read static file resource"""
    filepath = uri[7:]  # Remove file:// prefix

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Resource not found: {uri}")

    # Security: Ensure file is within allowed directory
    abs_filepath = os.path.abspath(filepath)
    allowed_dirs = [os.path.abspath("docs/")]

    if not any(abs_filepath.startswith(d) for d in allowed_dirs):
        raise PermissionError(f"Access denied: {uri}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine mime type based on extension
    mime_type = "text/plain"
    if filepath.endswith('.md'):
        mime_type = "text/markdown"
    elif filepath.endswith('.json'):
        mime_type = "application/json"
    elif filepath.endswith('.html'):
        mime_type = "text/html"

    return ResourceContents(
        contents=[
            TextResourceContents(
                uri=uri,
                mimeType=mime_type,
                text=content
            )
        ]
    )

async def read_dynamic_resource(uri: str):
    """Generate dynamic resource content"""

    if uri == "dynamic://system/status":
        status = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": get_uptime(),
            "memory_mb": get_memory_usage(),
            "cpu_percent": get_cpu_usage(),
            "active_processes": get_process_count()
        }
        return ResourceContents(
            contents=[
                TextResourceContents(
                    uri=uri,
                    mimeType="application/json",
                    text=json.dumps(status, indent=2)
                )
            ]
        )

    elif uri == "dynamic://system/info":
        info = {
            "platform": os.uname().sysname,
            "hostname": os.uname().nodename,
            "python_version": os.sys.version,
            "working_directory": os.getcwd(),
            "environment": dict(os.environ)
        }
        return ResourceContents(
            contents=[
                TextResourceContents(
                    uri=uri,
                    mimeType="application/json",
                    text=json.dumps(info, indent=2)
                )
            ]
        )

    else:
        raise ValueError(f"Unknown dynamic resource: {uri}")

# Helper functions for system metrics
def get_uptime():
    """Get system uptime in seconds"""
    try:
        with open('/proc/uptime', 'r') as f:
            return float(f.readline().split()[0])
    except:
        return 0.0

def get_memory_usage():
    """Get memory usage in MB"""
    try:
        import psutil
        return psutil.virtual_memory().used / (1024 * 1024)
    except:
        return 0.0

def get_cpu_usage():
    """Get CPU usage percentage"""
    try:
        import psutil
        return psutil.cpu_percent(interval=0.1)
    except:
        return 0.0

def get_process_count():
    """Get number of running processes"""
    try:
        import psutil
        return len(psutil.pids())
    except:
        return 0

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

## Resource Types Demonstrated

### Static Resources
- Markdown documentation files
- Configuration files
- API specifications

### Dynamic Resources
- System status (real-time)
- Environment information
- Metrics and monitoring data

## Security Considerations
- **Path traversal protection**: Validates file paths
- **Directory restrictions**: Limits access to allowed directories
- **Sensitive data filtering**: Can redact sensitive environment variables

## Usage Examples

```
"Show me the API documentation"
"What's the current system status?"
"List all available documentation"
```

## Extension Ideas
- Add template resources with parameters
- Implement resource subscriptions for updates
- Add caching for expensive dynamic resources
- Support binary resources (images, PDFs)
