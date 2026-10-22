# Connect the TimeToPost MCP

Hosted endpoint: `https://api.timetopost.co/mcp` with OAuth. Select this endpoint in an MCP client that supports remote Streamable HTTP and complete its OAuth flow.

For stdio clients, install the published TimeToPost MCP package using its current official setup instructions. Set the user's own API token in the process environment from TimeToPost Settings → API. Never ask anyone to paste a token into chat or place a real token in a config file committed to a project.

Client configuration shapes (replace `<package>` with the current package name from the official TimeToPost setup page):

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

For clients that require stdio, follow the official npm instructions and inject the token through a local environment variable. Hosted OAuth is preferred when supported.
