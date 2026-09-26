# MCP Client Setup

Connect your AI assistant to Aident via the Model Context Protocol.

## Server URL

Use the Aident Loadout MCP URL:

```text
https://loadout.aident.ai/mcp
```

For non-production deployments, replace the full server URL with that deployment's MCP URL.

For interactive, always-current setup instructions with videos for each client, visit https://loadout.aident.ai/dashboard and open the card for your client.

## Client Configuration

### Claude Code

Run in your terminal:

```bash
claude mcp add --transport http aident https://loadout.aident.ai/mcp
```

Or add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "aident": {
      "type": "http",
      "url": "https://loadout.aident.ai/mcp"
    }
  }
}
```

### Claude Desktop

Add to your config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS, `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "aident": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://loadout.aident.ai/mcp"]
    }
  }
}
```

### Claude on the web (claude.ai), Claude Desktop connectors, and Claude Cowork

On **Pro/Max/Team/Enterprise** plans, add Aident as an account-level connector so it is available across claude.ai, Claude Desktop, and Claude Cowork:

1. Open **Settings → Connectors** (on claude.ai or in the desktop app).
2. Click **Add custom connector**.
3. Enter the name `Aident Loadout` and the server URL `https://loadout.aident.ai/mcp`, then save.
4. Complete the OAuth sign-in when prompted and enable the connector in your chat's tools menu.

### Cursor IDE

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "aident": {
      "url": "https://loadout.aident.ai/mcp"
    }
  }
}
```

### VS Code (Copilot)

Add to `.vscode/mcp.json` in your project root:

```json
{
  "servers": {
    "aident": {
      "type": "http",
      "url": "https://loadout.aident.ai/mcp"
    }
  }
}
```

### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "aident": {
      "serverUrl": "https://loadout.aident.ai/mcp"
    }
  }
}
```

### ChatGPT (web and desktop)

ChatGPT connects to Aident as a Developer Mode plugin (a custom MCP connection). Requires a Pro, Plus, Business, Enterprise, or Edu plan; on Business/Enterprise/Edu workspaces an admin may need to allow custom connections.

1. In ChatGPT, open **Settings → Security and login** and enable **Developer mode**.
2. Go to **chatgpt.com/plugins** and click the add (**+**) button.
3. Enter the name `Aident Loadout`, an optional description, and the server URL `https://loadout.aident.ai/mcp`, then create the connection.
4. Sign in through the OAuth window and click **Approve**.
5. In a new chat, mention `@Aident Loadout` or simply ask for Aident tools.

After Aident ships tool updates, open chatgpt.com/plugins and click **Refresh** on the connection; new conversations then use the updated tools.

### Gemini CLI

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "aident": {
      "httpUrl": "https://loadout.aident.ai/mcp"
    }
  }
}
```

### Other MCP Clients

Any MCP-compatible client (Codex, Goose, Kiro, OpenCode, Antigravity, Factory, etc.) can connect using the server URL `https://loadout.aident.ai/mcp`. Refer to your client's documentation for where to add MCP server configurations.

## Authentication

On first connection, your MCP client opens a browser window for OAuth sign-in. After authorizing, you're connected automatically. No manual token management needed.

After MCP setup, ask your AI assistant to guide you to https://loadout.aident.ai/dashboard/apps to connect the services it should use.

To log out or switch accounts, use the `auth` tool with `{ "action": "logout" }`, then reconnect to sign in with a different account.

## Verify Connection

Ask your AI assistant to use an Aident tool. You should see the focused Aident Loadout tools available. Try:

```
Use Aident to list my available capabilities
```

See [SKILL.md](../SKILL.md) for the full tool list.
