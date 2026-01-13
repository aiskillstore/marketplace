# MCP Protocol Specification Reference

## Protocol Basics

MCP uses JSON-RPC 2.0 for message exchange. All messages follow a standardized format for reliable client-server communication.

## Message Format and Structure

### Tool Call Request
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_database",
    "arguments": {
      "query": "SELECT * FROM users",
      "limit": 10
    }
  }
}
```

### Tool Call Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 10 users: Alice, Bob, ..."
      }
    ]
  }
}
```

### Error Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "details": "query parameter is required"
    }
  }
}
```

## Message Types

**Request**: Client → Server (expects response)
- Must include `id` field for response matching
- Contains `method` and `params`

**Response**: Server → Client (answers request)
- Matches request `id`
- Contains either `result` or `error`

**Notification**: One-way message (no response expected)
- No `id` field
- Used for logging and status updates

## Transport Mechanisms

### STDIO (Standard Input/Output)
**Best for**: Local tools, command-line applications

**Pros**:
- Simple setup
- Secure (no network exposure)
- No firewall configuration needed

**Cons**:
- Limited to single machine
- No remote access

**Usage**:
```python
# Server runs as subprocess, communicates via stdin/stdout
# Claude Desktop launches: python server.py
```

### HTTP with Server-Sent Events (SSE)
**Best for**: Web services, remote servers, cloud deployments

**Pros**:
- Network accessible
- Scalable to multiple clients
- Firewall-friendly (standard HTTP/HTTPS)

**Cons**:
- More complex setup
- Requires hosting infrastructure

**Usage**:
```python
# Server exposes HTTP endpoint
# Client connects to: http://localhost:8000/mcp
```

### WebSocket (Future)
**Status**: Planned for future MCP versions

**Best for**: Real-time bidirectional communication

## Error Codes

Standard JSON-RPC error codes:
- `-32700`: Parse error (invalid JSON)
- `-32600`: Invalid request (malformed)
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
- `-32000` to `-32099`: Server-defined errors

## Capability Declaration

During initialization, servers declare their capabilities:

```python
{
    "capabilities": {
        "tools": {},           # Server provides tools
        "resources": {},       # Server provides resources
        "prompts": {},         # Server provides prompts
        "logging": {}          # Server supports logging
    },
    "serverInfo": {
        "name": "my-server",
        "version": "1.0.0"
    }
}
```

## Best Practices

1. **Always validate message structure** before processing
2. **Use appropriate error codes** for different failure types
3. **Include detailed error messages** to aid debugging
4. **Log all requests/responses** in development
5. **Implement timeouts** for long-running operations
