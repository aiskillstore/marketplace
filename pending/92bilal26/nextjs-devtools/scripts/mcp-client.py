#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal MCP Client - Bundle with any skill that needs MCP access.

Supports both HTTP and stdio transports for connecting to MCP servers.

Usage:
    # List available tools from an HTTP MCP server
    python mcp-client.py list --url http://localhost:8080

    # List tools from a stdio MCP server
    python mcp-client.py list --stdio "npx -y @modelcontextprotocol/server-github"

    # Call a tool
    python mcp-client.py call --url http://localhost:8080 --tool create_issue \
        --params '{"title": "Bug report", "body": "Details..."}'

    # Emit tool schemas as markdown (for caching in references/)
    python mcp-client.py emit --url http://localhost:8080

    # Emit as JSON (for programmatic use)
    python mcp-client.py emit --url http://localhost:8080 --format json
"""

import argparse
import json
import subprocess
import sys
import threading
import queue
from typing import Optional, Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


class MCPClientError(Exception):
    """Base exception for MCP client errors."""
    pass


class HTTPTransport:
    """MCP client using HTTP transport (streamable HTTP with session support)."""

    def __init__(self, url: str, headers: Optional[dict] = None):
        url = url.rstrip('/')
        # Playwright MCP and other streamable HTTP servers use /mcp endpoint
        if not url.endswith('/mcp'):
            url = url + '/mcp'
        self.url = url
        self.headers = headers or {}
        self._request_id = 0
        self._session_id: Optional[str] = None
        self._initialized = False

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _ensure_initialized(self):
        """Initialize the session if not already done."""
        if self._initialized:
            return

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-client", "version": "1.0.0"}
            }
        }

        data = json.dumps(payload).encode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            **self.headers
        }

        req = Request(self.url, data=data, headers=headers, method='POST')

        try:
            with urlopen(req, timeout=30) as resp:
                # Check for session ID in response headers
                self._session_id = resp.headers.get('Mcp-Session-Id')
                response = self._parse_response(resp.read().decode('utf-8'))
        except HTTPError as e:
            body = e.read().decode('utf-8') if e.fp else str(e)
            raise MCPClientError(f"HTTP {e.code}: {body}")
        except URLError as e:
            raise MCPClientError(f"Connection failed: {e.reason}")

        if "error" in response:
            err = response["error"]
            raise MCPClientError(f"Initialize failed: {err.get('message')}")

        self._initialized = True

        # Send initialized notification
        self._send_notification("notifications/initialized")

    def _parse_response(self, body: str) -> dict:
        """Parse response body, handling SSE format if needed."""
        body = body.strip()

        # Handle SSE format (event stream)
        if body.startswith('event:') or body.startswith('data:'):
            for line in body.split('\n'):
                if line.startswith('data:'):
                    json_data = line[5:].strip()
                    if json_data:
                        return json.loads(json_data)
            raise MCPClientError("No data in SSE response")

        # Regular JSON response
        return json.loads(body)

    def _send_notification(self, method: str, params: Optional[dict] = None):
        """Send a notification (no response expected)."""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
        }
        if params:
            payload["params"] = params

        data = json.dumps(payload).encode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            **self.headers
        }
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id

        req = Request(self.url, data=data, headers=headers, method='POST')
        try:
            with urlopen(req, timeout=30) as resp:
                pass  # Notifications don't return data
        except (HTTPError, URLError):
            pass  # Ignore notification errors

    def request(self, method: str, params: Optional[dict] = None) -> dict:
        """Send a JSON-RPC request to the MCP server."""
        self._ensure_initialized()

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
        }
        if params:
            payload["params"] = params

        data = json.dumps(payload).encode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            **self.headers
        }
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id

        req = Request(self.url, data=data, headers=headers, method='POST')

        try:
            with urlopen(req, timeout=30) as resp:
                response = self._parse_response(resp.read().decode('utf-8'))
        except HTTPError as e:
            body = e.read().decode('utf-8') if e.fp else str(e)
            raise MCPClientError(f"HTTP {e.code}: {body}")
        except URLError as e:
            raise MCPClientError(f"Connection failed: {e.reason}")

        if "error" in response:
            err = response["error"]
            raise MCPClientError(f"MCP error {err.get('code')}: {err.get('message')}")

        return response.get("result", {})


class StdioTransport:
    """MCP client using stdio transport (for local MCP servers)."""

    def __init__(self, command: str):
        self.command = command
        self._request_id = 0
        self._process: Optional[subprocess.Popen] = None
        self._response_queue: queue.Queue = queue.Queue()
        self._reader_thread: Optional[threading.Thread] = None

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _start(self):
        """Start the MCP server process."""
        if self._process is not None:
            return

        self._process = subprocess.Popen(
            self.command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # Start reader thread
        self._reader_thread = threading.Thread(target=self._read_responses, daemon=True)
        self._reader_thread.start()

        # Send initialize request
        self._send({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-client", "version": "1.0.0"}
            }
        })

        # Wait for initialize response
        try:
            resp = self._response_queue.get(timeout=10)
            if "error" in resp:
                raise MCPClientError(f"Initialize failed: {resp['error']}")
        except queue.Empty:
            raise MCPClientError("Timeout waiting for server initialization")

        # Send initialized notification
        self._send({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })

    def _read_responses(self):
        """Background thread to read responses from the server."""
        while self._process and self._process.poll() is None:
            try:
                line = self._process.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    try:
                        msg = json.loads(line)
                        # Only queue responses (messages with id), not notifications
                        if "id" in msg:
                            self._response_queue.put(msg)
                    except json.JSONDecodeError:
                        pass  # Ignore non-JSON output
            except Exception:
                break

    def _send(self, message: dict):
        """Send a message to the server."""
        if self._process is None:
            raise MCPClientError("Process not started")
        line = json.dumps(message) + "\n"
        self._process.stdin.write(line)
        self._process.stdin.flush()

    def request(self, method: str, params: Optional[dict] = None) -> dict:
        """Send a JSON-RPC request and wait for response."""
        self._start()

        req_id = self._next_id()
        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
        }
        if params:
            payload["params"] = params

        self._send(payload)

        # Wait for response with matching id
        try:
            while True:
                resp = self._response_queue.get(timeout=30)
                if resp.get("id") == req_id:
                    if "error" in resp:
                        err = resp["error"]
                        raise MCPClientError(f"MCP error {err.get('code')}: {err.get('message')}")
                    return resp.get("result", {})
        except queue.Empty:
            raise MCPClientError(f"Timeout waiting for response to {method}")

    def close(self):
        """Shutdown the server process."""
        if self._process:
            self._process.terminate()
            self._process.wait(timeout=5)
            self._process = None


class MCPClient:
    """High-level MCP client that works with any transport."""

    def __init__(self, transport):
        self.transport = transport

    def list_tools(self) -> list[dict]:
        """Get list of available tools from the server."""
        result = self.transport.request("tools/list")
        return result.get("tools", [])

    def call_tool(self, name: str, arguments: Optional[dict] = None) -> Any:
        """Call a tool and return the result."""
        params = {"name": name}
        if arguments:
            params["arguments"] = arguments

        result = self.transport.request("tools/call", params)
        return result

    def list_resources(self) -> list[dict]:
        """Get list of available resources."""
        result = self.transport.request("resources/list")
        return result.get("resources", [])

    def list_prompts(self) -> list[dict]:
        """Get list of available prompts."""
        result = self.transport.request("prompts/list")
        return result.get("prompts", [])


def emit_markdown(tools: list[dict]) -> str:
    """Generate markdown documentation for tools."""
    lines = ["# MCP Server Tools\n"]
    lines.append(f"*{len(tools)} tools available*\n")

    for tool in tools:
        name = tool.get("name", "unnamed")
        desc = tool.get("description", "No description")
        schema = tool.get("inputSchema", {})
        annotations = tool.get("annotations", {})

        lines.append(f"## `{name}`\n")
        lines.append(f"{desc}\n")

        # Add annotations if present
        if annotations:
            flags = []
            if annotations.get("readOnlyHint"):
                flags.append("read-only")
            if annotations.get("destructiveHint"):
                flags.append("destructive")
            if annotations.get("idempotentHint"):
                flags.append("idempotent")
            if flags:
                lines.append(f"*Flags: {', '.join(flags)}*\n")

        # Add input schema
        if schema.get("properties"):
            lines.append("### Parameters\n")
            required = set(schema.get("required", []))
            for prop_name, prop_def in schema["properties"].items():
                req_marker = " *(required)*" if prop_name in required else ""
                prop_type = prop_def.get("type", "any")
                prop_desc = prop_def.get("description", "")
                lines.append(f"- **`{prop_name}`** (`{prop_type}`){req_marker}: {prop_desc}")
            lines.append("")

        # Add full schema as collapsible
        lines.append("<details>")
        lines.append("<summary>Full Schema</summary>\n")
        lines.append("```json")
        lines.append(json.dumps(schema, indent=2))
        lines.append("```")
        lines.append("</details>\n")

    return "\n".join(lines)


def emit_json(tools: list[dict]) -> str:
    """Generate JSON output for tools."""
    return json.dumps({"tools": tools}, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Universal MCP Client - connect to any MCP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Commands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    list_parser = subparsers.add_parser("list", help="List available tools")
    list_parser.add_argument("--verbose", "-v", action="store_true", help="Show full tool details")

    # call command
    call_parser = subparsers.add_parser("call", help="Call a tool")
    call_parser.add_argument("--tool", "-t", required=True, help="Tool name")
    call_parser.add_argument("--params", "-p", default="{}", help="JSON parameters")

    # emit command
    emit_parser = subparsers.add_parser("emit", help="Emit tool schemas as documentation")
    emit_parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")

    # resources command
    subparsers.add_parser("resources", help="List available resources")

    # prompts command
    subparsers.add_parser("prompts", help="List available prompts")

    # Transport options (added to all subparsers)
    for sub in [list_parser, call_parser, emit_parser]:
        transport_group = sub.add_mutually_exclusive_group(required=True)
        transport_group.add_argument("--url", "-u", help="HTTP URL of MCP server")
        transport_group.add_argument("--stdio", "-s", help="Command to start stdio MCP server")
        sub.add_argument("--header", "-H", action="append", default=[],
                        help="HTTP header (format: 'Name: Value')")

    args = parser.parse_args()

    # Create transport
    transport = None
    try:
        if hasattr(args, 'url') and args.url:
            headers = {}
            for h in args.header:
                if ':' in h:
                    key, value = h.split(':', 1)
                    headers[key.strip()] = value.strip()
            transport = HTTPTransport(args.url, headers)
        elif hasattr(args, 'stdio') and args.stdio:
            transport = StdioTransport(args.stdio)
        else:
            parser.error("Must specify --url or --stdio")

        client = MCPClient(transport)

        # Execute command
        if args.command == "list":
            tools = client.list_tools()
            if args.verbose:
                print(json.dumps(tools, indent=2))
            else:
                for tool in tools:
                    desc = tool.get("description", "")[:60]
                    print(f"  {tool['name']}: {desc}...")

        elif args.command == "call":
            params = json.loads(args.params)
            result = client.call_tool(args.tool, params)
            print(json.dumps(result, indent=2))

        elif args.command == "emit":
            tools = client.list_tools()
            if args.format == "markdown":
                print(emit_markdown(tools))
            else:
                print(emit_json(tools))

        elif args.command == "resources":
            resources = client.list_resources()
            print(json.dumps(resources, indent=2))

        elif args.command == "prompts":
            prompts = client.list_prompts()
            print(json.dumps(prompts, indent=2))

    except MCPClientError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
    finally:
        if transport and hasattr(transport, 'close'):
            transport.close()


if __name__ == "__main__":
    main()
