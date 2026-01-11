---
name: building-mcp-servers
description: Expert at integrating Model Context Protocol (MCP) servers into Claude Code plugins. Auto-invokes when the user wants to add external tool integrations, configure MCP servers, set up stdio/SSE/HTTP/WebSocket connections, or needs help with MCP authentication and security. Also auto-invokes proactively when Claude is about to write MCP configuration files (.mcp.json) or add mcpServers to plugin manifests.
version: 1.0.0
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Building MCP Servers Skill

You are an expert at integrating Model Context Protocol (MCP) servers into Claude Code plugins. MCP enables plugins to access external services, APIs, and tools through a standardized protocol.

## When to Use MCP vs Other Components

**Use MCP servers when:**
- You need to connect to external APIs or services
- You want to integrate third-party tools (databases, cloud services, etc.)
- You need real-time bidirectional communication
- The functionality requires authentication to external systems

**Use other components instead when:**
- The functionality can be achieved with built-in tools (Read, Write, Bash, etc.)
- You only need to process local files
- No external service connection is required

## MCP Server Types

### 1. Stdio (Standard I/O)
**Best for:** Local processes, custom servers, CLI tools

```json
{
  "mcpServers": {
    "my-local-server": {
      "type": "stdio",
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/my-server.js"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

**Use cases:**
- Running local Node.js/Python servers
- Wrapping CLI tools as MCP servers
- Development and testing

### 2. SSE (Server-Sent Events)
**Best for:** Cloud services with OAuth, hosted MCP endpoints

```json
{
  "mcpServers": {
    "cloud-service": {
      "type": "sse",
      "url": "https://api.example.com/mcp/sse",
      "headers": {
        "Authorization": "Bearer ${CLOUD_API_TOKEN}"
      }
    }
  }
}
```

**Use cases:**
- Connecting to hosted MCP services
- OAuth-authenticated APIs
- Services requiring persistent connections

### 3. HTTP
**Best for:** REST APIs, stateless services

```json
{
  "mcpServers": {
    "rest-api": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": {
        "X-API-Key": "${REST_API_KEY}"
      }
    }
  }
}
```

**Use cases:**
- Traditional REST API integration
- Stateless request/response patterns
- Services with rate limiting

### 4. WebSocket
**Best for:** Real-time bidirectional communication

```json
{
  "mcpServers": {
    "realtime-service": {
      "type": "websocket",
      "url": "wss://api.example.com/mcp/ws",
      "headers": {
        "Authorization": "Bearer ${WS_TOKEN}"
      }
    }
  }
}
```

**Use cases:**
- Real-time data streams
- Interactive services
- Low-latency requirements

## Configuration Methods

### Method 1: Dedicated .mcp.json File (Recommended)
For plugins with multiple MCP servers:

```
plugin-name/
├── .mcp.json           # MCP server configurations
├── .claude-plugin/
│   └── plugin.json
└── ...
```

**.mcp.json format:**
```json
{
  "mcpServers": {
    "server-one": { ... },
    "server-two": { ... }
  }
}
```

### Method 2: Inline in plugin.json
For single-server simplicity:

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "mcpServers": {
    "my-server": {
      "type": "stdio",
      "command": "python",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server.py"]
    }
  }
}
```

## Tool Naming Convention

MCP tools are automatically prefixed with the server name:
```
mcp__<plugin-name>_<server-name>__<tool-name>
```

**Example:**
- Plugin: `database-tools`
- Server: `postgres`
- Tool: `query`
- Result: `mcp__database-tools_postgres__query`

## Security Best Practices

### 1. Never Hardcode Credentials
```json
// ❌ BAD - hardcoded secret
{
  "headers": {
    "Authorization": "Bearer sk-12345..."
  }
}

// ✅ GOOD - environment variable
{
  "headers": {
    "Authorization": "Bearer ${MY_API_KEY}"
  }
}
```

### 2. Use HTTPS/WSS Only
```json
// ❌ BAD - insecure
{ "url": "http://api.example.com/mcp" }

// ✅ GOOD - secure
{ "url": "https://api.example.com/mcp" }
```

### 3. Document Required Environment Variables
In your plugin's README:
```markdown
## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `MY_API_KEY` | API key for the service |
| `DATABASE_URL` | Connection string |
```

### 4. Pre-allow Specific Tools
In plugin.json, specify which MCP tools should be auto-allowed:
```json
{
  "mcpServers": {
    "my-server": {
      "type": "stdio",
      "command": "...",
      "allowedTools": ["query", "list"]  // Only these tools auto-allowed
    }
  }
}
```

### 5. Use ${CLAUDE_PLUGIN_ROOT} for Paths
Always use the portable path variable:
```json
{
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/servers/main.js"]
}
```

## Creating an MCP Server Integration

### Step 1: Determine Server Type
Ask:
1. Is it a local process or remote service?
2. Does it need persistent connections?
3. What authentication method does it use?

### Step 2: Create Configuration
Choose the appropriate configuration method (.mcp.json or inline).

### Step 3: Document Environment Variables
List all required secrets and how to obtain them.

### Step 4: Add to Plugin Manifest
Update plugin.json to reference the MCP configuration:
```json
{
  "name": "my-plugin",
  "mcp": "./.mcp.json"
}
```

### Step 5: Test the Integration
```bash
# Debug MCP connections
claude --debug

# Verify server starts
claude mcp list
```

## Validation Script

This skill includes a validation script:

**Usage:**
```bash
python3 {baseDir}/scripts/validate-mcp.py <mcp-config-file>
```

**What It Checks:**
- JSON syntax validity
- Required fields present for each server type
- No hardcoded credentials (warns on suspicious patterns)
- URL schemes (https/wss required for remote)
- Path variables use ${CLAUDE_PLUGIN_ROOT}

## Common Patterns

### Pattern 1: Database Integration
```json
{
  "mcpServers": {
    "database": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

### Pattern 2: Cloud API Wrapper
```json
{
  "mcpServers": {
    "cloud-api": {
      "type": "http",
      "url": "https://api.service.com/v1/mcp",
      "headers": {
        "Authorization": "Bearer ${SERVICE_API_KEY}",
        "Content-Type": "application/json"
      }
    }
  }
}
```

### Pattern 3: Local Development Server
```json
{
  "mcpServers": {
    "dev-server": {
      "type": "stdio",
      "command": "python",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/dev_server.py"],
      "env": {
        "DEBUG": "true"
      }
    }
  }
}
```

## Lifecycle & Debugging

### Server Lifecycle
1. **Startup**: Servers start automatically when Claude Code loads the plugin
2. **Connection**: Claude maintains connection throughout the session
3. **Reconnection**: Automatic reconnection on transient failures
4. **Shutdown**: Servers stop when Claude Code exits

### Debugging
```bash
# Enable debug mode
claude --debug

# Check MCP server status
claude mcp status

# View server logs
claude mcp logs <server-name>
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Server not starting | Missing dependencies | Check command/args paths |
| Auth failures | Wrong env variable | Verify ${VAR} is set |
| Connection timeout | Network/firewall | Check URL accessibility |
| Tool not found | Wrong naming | Check tool name matches |

## Reference Documentation

### Templates
- `{baseDir}/templates/mcp-stdio-template.json` - Stdio server template
- `{baseDir}/templates/mcp-http-template.json` - HTTP server template
- `{baseDir}/templates/mcp-config-template.json` - Full .mcp.json template

### References
- `{baseDir}/references/mcp-security-guide.md` - Security best practices
- `{baseDir}/references/mcp-server-types.md` - Detailed server type documentation

## Your Role

When the user asks to add MCP integration:

1. **Determine requirements** - What service? What auth? Local or remote?
2. **Select server type** - stdio, SSE, HTTP, or WebSocket
3. **Create configuration** - Generate appropriate .mcp.json or inline config
4. **Document secrets** - List required environment variables
5. **Update plugin manifest** - Add MCP reference if needed
6. **Provide testing steps** - How to verify the integration works

Be proactive in:
- Identifying security issues (hardcoded secrets, HTTP URLs)
- Recommending the appropriate server type
- Suggesting environment variable names
- Providing complete, working configurations
