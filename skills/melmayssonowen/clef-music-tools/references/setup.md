# Connect Clef MCP

Public no-auth MCP endpoint: `https://clefdrills.com/mcp`.

## Claude Code

```sh
claude mcp add --transport http clef https://clefdrills.com/mcp
```

## Cursor

```json
{"mcpServers":{"clef":{"url":"https://clefdrills.com/mcp"}}}
```

## Codex

```toml
[mcp_servers.clef]
url = "https://clefdrills.com/mcp"
```

## VS Code / Copilot

```json
{"servers":{"clef":{"type":"http","url":"https://clefdrills.com/mcp"}}}
```
