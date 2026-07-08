#!/usr/bin/env python3
"""
MCP Skill Executor (Multi-transport)
====================================
Supports stdio, SSE, and HTTP transports for MCP with stats tracking.
"""

import json
import sys
import asyncio
import argparse
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import os

# Import stats manager
try:
    from stats_manager import MCPStatsManager, init_stats_manager, get_stats_manager
    HAS_STATS = True
except ImportError:
    HAS_STATS = False


# API Key 轮询管理
class APIKeyRotator:
    """多 API Key 轮询管理器"""
    
    def __init__(self):
        self.keys = []
        self.index = 0
        self._load_keys()
    
    def _load_keys(self):
        """从环境变量加载 API Keys"""
        load_dotenv(Path(__file__).parent / '.env')
        keys_str = os.getenv('TAVILY_API_KEY', '')
        if keys_str:
            self.keys = [k.strip() for k in keys_str.split(',') if k.strip()]
    
    def get_key(self) -> str:
        """获取下一个 API Key（轮询）"""
        if not self.keys:
            raise ValueError("No API keys configured")
        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        return key
    
    def get_key_count(self) -> int:
        """获取可用 Key 数量"""
        return len(self.keys)


# 全局轮询器实例
_api_rotator = APIKeyRotator()


async def list_tools(config):
    """List tools from MCP server."""
    transport = config.get("transport", "stdio")

    if transport == "stdio":
        return await list_tools_stdio(config)
    elif transport == "sse":
        return await list_tools_sse(config)
    elif transport == "http":
        return await list_tools_http(config)
    else:
        raise ValueError(f"Unsupported transport: {transport}")


async def list_tools_stdio(config):
    """List tools from stdio MCP server."""
    server_params = StdioServerParameters(
        command=config["command"],
        args=config.get("args", []),
        env=config.get("env")
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.list_tools()

            tools = [
                {"name": tool.name, "description": tool.description}
                for tool in response.tools
            ]
            return tools


async def list_tools_sse(config):
    """List tools from SSE/HTTP MCP server (Tavily-style)."""
    result = await http_sse_request(config, "tools/list")
    if "result" in result and "tools" in result["result"]:
        return [
            {"name": t["name"], "description": t.get("description", "")}
            for t in result["result"]["tools"]
        ]
    return []


async def list_tools_http(config):
    """List tools from HTTP MCP server."""
    import httpx

    endpoint = config.get("endpoint")
    if not endpoint:
        raise ValueError("HTTP transport requires 'endpoint' in config")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json={
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/list"
            },
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        if "result" in result and "tools" in result["result"]:
            return [
                {"name": t["name"], "description": t.get("description", "")}
                for t in result["result"]["tools"]
            ]
        return []


async def http_sse_request(config, method, params=None):
    """Send a JSON-RPC request to HTTP MCP server with SSE response handling."""
    import httpx
    import re

    endpoint = config.get("endpoint")
    if not endpoint:
        raise ValueError("SSE transport requires 'endpoint' in config")

    # 获取轮询的 API Key 并替换 endpoint 中的 key
    current_key = _api_rotator.get_key()
    endpoint = re.sub(r'tavilyApiKey=[^&]+', f'tavilyApiKey={current_key}', endpoint)

    request_id = str(uuid.uuid4())

    # Build JSON-RPC request
    request_body = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method
    }
    if params:
        request_body["params"] = params

    # Send request with proper Accept header for SSE response
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            endpoint,
            json=request_body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        )

        # Check if response is SSE format
        content_type = response.headers.get("content-type", "")
        if "text/event-stream" in content_type:
            # Parse SSE response
            result = parse_sse_response(response.text)
            return result
        else:
            # Regular JSON response
            return response.json()


def parse_sse_response(text: str) -> dict:
    """Parse SSE formatted response."""
    result = {}
    for line in text.strip().split('\n'):
        line = line.strip()
        if line.startswith('event:'):
            event_type = line[6:].strip()
        elif line.startswith('data:'):
            data = line[5:].strip()
            try:
                result = json.loads(data)
            except json.JSONDecodeError:
                pass
    return result


async def describe_tool(config, tool_name):
    """Describe a specific tool."""
    transport = config.get("transport", "stdio")

    if transport == "stdio":
        return await describe_tool_stdio(config, tool_name)
    elif transport == "sse":
        return await describe_tool_sse(config, tool_name)
    elif transport == "http":
        return await describe_tool_http(config, tool_name)
    else:
        raise ValueError(f"Unsupported transport: {transport}")


async def describe_tool_stdio(config, tool_name):
    """Describe a tool from stdio MCP server."""
    server_params = StdioServerParameters(
        command=config["command"],
        args=config.get("args", []),
        env=config.get("env")
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.list_tools()

            for tool in response.tools:
                if tool.name == tool_name:
                    return {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
            return None


async def describe_tool_sse(config, tool_name):
    """Describe a tool from SSE MCP server."""
    # Get full tool list with schemas
    result = await http_sse_request(config, "tools/list")
    if "result" in result and "tools" in result["result"]:
        for t in result["result"]["tools"]:
            if t["name"] == tool_name:
                return {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "inputSchema": t.get("inputSchema", {"type": "object", "properties": {}})
                }
    return None


async def describe_tool_http(config, tool_name):
    """Describe a tool from HTTP MCP server."""
    import httpx

    endpoint = config.get("endpoint")
    if not endpoint:
        raise ValueError("HTTP transport requires 'endpoint' in config")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json={
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/list"
            },
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        if "result" in result and "tools" in result["result"]:
            for t in result["result"]["tools"]:
                if t["name"] == tool_name:
                    return {
                        "name": t["name"],
                        "description": t.get("description", ""),
                        "inputSchema": t.get("inputSchema", {"type": "object", "properties": {}})
                    }
    return None


async def call_tool(config, tool_name, arguments):
    """Call a specific tool."""
    transport = config.get("transport", "stdio")

    if transport == "stdio":
        return await call_tool_stdio(config, tool_name, arguments)
    elif transport == "sse":
        return await call_tool_sse(config, tool_name, arguments)
    elif transport == "http":
        return await call_tool_http(config, tool_name, arguments)
    else:
        raise ValueError(f"Unsupported transport: {transport}")


async def call_tool_with_stats(config, tool_name, arguments):
    """Call a tool with statistics tracking."""
    start_time = time.time()
    success = False
    error = None
    result = None

    try:
        result = await call_tool(config, tool_name, arguments)
        success = True
    except Exception as e:
        error = str(e)
        raise
    finally:
        duration = time.time() - start_time

        # Record stats if available
        if HAS_STATS:
            stats_manager = get_stats_manager()
            if stats_manager:
                stats_manager.record_call(tool_name, arguments, success, duration, error)

    return result


async def call_tool_stdio(config, tool_name, arguments):
    """Call a tool from stdio MCP server."""
    server_params = StdioServerParameters(
        command=config["command"],
        args=config.get("args", []),
        env=config.get("env")
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.call_tool(tool_name, arguments)
            return response.content


async def call_tool_sse(config, tool_name, arguments):
    """Call a tool from SSE MCP server."""
    result = await http_sse_request(config, "tools/call", {
        "name": tool_name,
        "arguments": arguments
    })

    if "result" in result:
        content = result["result"].get("content", [])
        return content
    elif "error" in result:
        raise RuntimeError(f"MCP error: {result['error']}")
    else:
        return [{"text": json.dumps(result)}]


async def call_tool_http(config, tool_name, arguments):
    """Call a tool from HTTP MCP server."""
    import httpx

    endpoint = config.get("endpoint")
    if not endpoint:
        raise ValueError("HTTP transport requires 'endpoint' in config")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json={
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            },
            headers={"Content-Type": "application/json"}
        )
        result = response.json()

        if "result" in result:
            content = result["result"].get("content", [])
            return content
        elif "error" in result:
            raise RuntimeError(f"MCP error: {result['error']}")
        else:
            return [{"text": json.dumps(result)}]


async def main():
    parser = argparse.ArgumentParser(
        description="MCP Skill Executor - Multi-transport support (stdio/SSE/HTTP)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                          List all available tools
  %(prog)s --describe tool_name           Get tool schema and parameters
  %(prog)s --call '{"tool": "..."}'        Execute a tool call
  %(prog)s --status                        Show status and statistics
  %(prog)s --stats                         Show detailed statistics
  %(prog)s --logs [limit]                  Show recent logs

Supported transports:
  stdio (default) - Standard input/output
  sse - Server-Sent Events (HTTP with SSE response)
  http - HTTP polling
        """
    )
    parser.add_argument("--call", help="JSON tool call to execute")
    parser.add_argument("--describe", help="Get tool schema")
    parser.add_argument("--list", action="store_true", help="List all tools")
    parser.add_argument("--status", action="store_true", help="Show status and statistics")
    parser.add_argument("--stats", action="store_true", help="Show detailed statistics")
    parser.add_argument("--logs", nargs='?', const=100, type=int, help="Show recent logs (default: 100)")
    parser.add_argument("--tool", help="Filter logs by tool name")
    parser.add_argument("--reset-stats", action="store_true", help="Reset all statistics")
    parser.add_argument("--key-status", action="store_true", help="Show API key rotation status")
    parser.add_argument("--session", help="Set session name for stats tracking")
    parser.add_argument("--version", action="version", version="%(prog)s 5.0.0")

    args = parser.parse_args()

    # Load server config
    config_path = Path(__file__).parent / "mcp-config.json"
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    # Initialize stats manager
    if HAS_STATS:
        init_stats_manager(Path(__file__).parent)

    # Detect transport
    transport = config.get("transport", "stdio")

    try:
        if args.list:
            tools = await list_tools(config)
            print(json.dumps(tools, indent=2, ensure_ascii=False))

        elif args.describe:
            schema = await describe_tool(config, args.describe)
            if schema:
                print(json.dumps(schema, indent=2, ensure_ascii=False))
            else:
                print(f"Tool not found: {args.describe}", file=sys.stderr)
                sys.exit(1)

        elif args.call:
            call_data = json.loads(args.call)
            result = await call_tool_with_stats(
                config,
                call_data["tool"],
                call_data.get("arguments", {})
            )

            # Format result
            if isinstance(result, list):
                for item in result:
                    if hasattr(item, 'text'):
                        print(item.text)
                    elif isinstance(item, dict) and 'text' in item:
                        print(item['text'])
                    else:
                        print(json.dumps(item, indent=2) if isinstance(item, dict) else str(item))
            else:
                print(json.dumps(result, indent=2) if isinstance(result, dict) else str(result))

        elif args.status:
            if HAS_STATS:
                stats_manager = get_stats_manager()
                status = stats_manager.get_status()
                print(json.dumps(status, indent=2, ensure_ascii=False))
            else:
                print("Stats tracking not available", file=sys.stderr)

        elif args.stats:
            if HAS_STATS:
                stats_manager = get_stats_manager()
                stats = stats_manager.get_stats()
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            else:
                print("Stats tracking not available", file=sys.stderr)

        elif args.logs is not None:
            if HAS_STATS:
                stats_manager = get_stats_manager()
                logs = stats_manager.get_logs(limit=args.logs, tool_name=args.tool)
                print(json.dumps(logs, indent=2, ensure_ascii=False))
            else:
                print("Stats tracking not available", file=sys.stderr)

        elif args.reset_stats:
            if HAS_STATS:
                stats_manager = get_stats_manager()
                stats_manager.reset_stats()
                print("Statistics reset successfully")
            else:
                print("Stats tracking not available", file=sys.stderr)

        elif args.key_status:
            key_info = {
                "total_keys": _api_rotator.get_key_count(),
                "current_index": _api_rotator.index,
                "keys_preview": [f"{k[:15]}...{k[-4:]}" for k in _api_rotator.keys]
            }
            print(json.dumps(key_info, indent=2, ensure_ascii=False))

        elif args.session:
            # 设置会话名称
            if HAS_STATS:
                stats_manager = get_stats_manager()
                stats_manager.set_session_name(args.session)
                print(f"Session name set to: {args.session}")
            else:
                print("Stats tracking not available", file=sys.stderr)

        else:
            parser.print_help()

        # Explicitly flush
        sys.stdout.flush()
        sys.stderr.flush()

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in --call argument: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
