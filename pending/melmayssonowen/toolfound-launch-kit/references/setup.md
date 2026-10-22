# Connect Toolfound MCP

Endpoint: `https://toolfound.com/api/mcp` (Streamable HTTP, no authentication for discovery). Use a client that supports remote MCP.

## Claude Code

```sh
claude mcp add --transport http toolfound https://toolfound.com/api/mcp
```

## Cursor

```json
{"mcpServers":{"toolfound":{"url":"https://toolfound.com/api/mcp"}}}
```

## Codex

```toml
[mcp_servers.toolfound]
url = "https://toolfound.com/api/mcp"
```

## VS Code / Copilot

```json
{"servers":{"toolfound":{"type":"http","url":"https://toolfound.com/api/mcp"}}}
```
