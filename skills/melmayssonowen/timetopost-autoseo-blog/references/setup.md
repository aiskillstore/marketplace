# Connect the TimeToPost MCP

Hosted MCP endpoint: `https://api.timetopost.co/mcp` with OAuth. For a client with remote Streamable HTTP support, add this URL and complete OAuth.

## Claude Code

```sh
claude mcp add --transport http timetopost https://api.timetopost.co/mcp
```

## Cursor

```json
{"mcpServers":{"timetopost":{"url":"https://api.timetopost.co/mcp"}}}
```

## Codex

```toml
[mcp_servers.timetopost]
url = "https://api.timetopost.co/mcp"
```

## VS Code / Copilot

```json
{"servers":{"timetopost":{"type":"http","url":"https://api.timetopost.co/mcp"}}}
```

The stdio option uses the official TimeToPost npm package and the user's API token from Settings → API, supplied through a local environment variable. Never paste a real token into chat or commit one to config. Confirm package and argument names against current official instructions before using stdio.
